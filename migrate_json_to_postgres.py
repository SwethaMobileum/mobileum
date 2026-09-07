import os
import sys
import json
import psycopg2
from psycopg2.extras import Json

def load_env_local():
    """Load DATABASE_URL from .env.local or src/.env.local if present."""
    env_paths = ['.env.local', 'src/.env.local']
    for path in env_paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        if k.strip() in ['DATABASE_URL', 'POSTGRES_URL']:
                            os.environ[k.strip()] = v.strip().strip('"').strip("'")

def main():
    load_env_local()
    db_url = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')
    
    if len(sys.argv) > 1:
        db_url = sys.argv[1]

    if not db_url or 'your-postgres-connection-string' in db_url:
        print("Error: DATABASE_URL is not set or contains placeholder value.")
        print("Usage: python migrate_json_to_postgres.py [DATABASE_URL]")
        print("Example: python migrate_json_to_postgres.py postgresql://postgres:password@localhost:5432/postgres")
        sys.exit(1)

    print(f"Connecting to PostgreSQL database...")
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        print("Connected successfully.")
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)

    # 1. Create tables
    print("Creating tables if they do not exist...")
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS country_overrides (
        country_id TEXT NOT NULL,
        operator_id TEXT NOT NULL DEFAULT 'Global',
        section TEXT NOT NULL,
        field_name TEXT NOT NULL,
        value JSONB,
        updated_by TEXT DEFAULT 'Anonymous',
        updated_at TIMESTAMPTZ DEFAULT NOW(),
        PRIMARY KEY (country_id, operator_id, section, field_name)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS change_history (
        id SERIAL PRIMARY KEY,
        country_id TEXT NOT NULL,
        operator_id TEXT NOT NULL DEFAULT 'Global',
        section TEXT NOT NULL,
        field_name TEXT NOT NULL,
        old_value JSONB,
        new_value JSONB,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS countries (
        country_id TEXT PRIMARY KEY,
        country_name TEXT NOT NULL,
        region TEXT,
        gdp_per_capita NUMERIC
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS operators (
        operator_id SERIAL PRIMARY KEY,
        country_id TEXT REFERENCES countries(country_id) ON DELETE CASCADE,
        operator_name TEXT NOT NULL,
        subscriber_count NUMERIC,
        five_g_penetration_pct NUMERIC,
        impact_analysis JSONB
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS operator_financials_5y (
        id SERIAL PRIMARY KEY,
        operator_id INT REFERENCES operators(operator_id) ON DELETE CASCADE,
        year INT,
        revenue_usd_b NUMERIC,
        ebitda_usd_b NUMERIC,
        capex_usd_b NUMERIC
    );
    """)

    conn.commit()
    print("Tables created / verified successfully.")

    # 2. Populate countries & operators from master_telecom.json
    telecom_path = os.path.join('src', 'data', 'master_telecom.json')
    fin_path = os.path.join('src', 'data', 'operator_financials.json')

    if os.path.exists(telecom_path):
        print(f"Reading {telecom_path}...")
        with open(telecom_path, 'r', encoding='utf-8') as f:
            telecom_data = json.load(f)
        
        countries_dict = telecom_data.get('countries', {})
        print(f"Found {len(countries_dict)} countries to migrate.")

        op_name_to_id = {}

        for country_key, c_data in countries_dict.items():
            country_id = c_data.get('country', country_key)
            country_name = c_data.get('country', country_key)
            region = c_data.get('region')
            gdp_per_capita = c_data.get('gdp_per_capita_usd')

            cur.execute("""
                INSERT INTO countries (country_id, country_name, region, gdp_per_capita)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (country_id) DO UPDATE 
                SET country_name = EXCLUDED.country_name,
                    region = EXCLUDED.region,
                    gdp_per_capita = EXCLUDED.gdp_per_capita;
            """, (country_id, country_name, region, gdp_per_capita))

            for op in c_data.get('operators', []):
                op_name = op.get('operator')
                sub_count = op.get('sub_base_mln')
                five_g = op.get('fiveG_pct')
                impact_analysis = Json(op)

                cur.execute("""
                    INSERT INTO operators (country_id, operator_name, subscriber_count, five_g_penetration_pct, impact_analysis)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING operator_id;
                """, (country_id, op_name, sub_count, five_g, impact_analysis))
                
                op_id = cur.fetchone()[0]
                op_name_to_id[op_name] = op_id

        conn.commit()
        print(f"Migrated {len(op_name_to_id)} operators.")

        # 3. Populate financials from operator_financials.json
        if os.path.exists(fin_path):
            print(f"Reading {fin_path}...")
            with open(fin_path, 'r', encoding='utf-8') as f:
                fin_data = json.load(f)
            
            groups = fin_data.get('groups', {})
            op_to_grp = fin_data.get('operator_to_group', {})

            fin_count = 0
            for op_name, grp_name in op_to_grp.items():
                if op_name in op_name_to_id and grp_name in groups:
                    grp = groups[grp_name]
                    op_id = op_name_to_id[op_name]
                    
                    # 3-year performance history if available
                    perf = grp.get('performance_trend_3yr', {})
                    if perf and isinstance(perf, dict) and 'history' in perf:
                        for entry in perf['history']:
                            yr_str = entry.get('year', '')
                            # Extract numeric year
                            yr_num = None
                            for word in yr_str.split():
                                if word.isdigit() and len(word) == 4:
                                    yr_num = int(word)
                                    break
                            
                            rev = grp.get('revenue_usd_bn')
                            ebitda = None
                            capex = None

                            cur.execute("""
                                INSERT INTO operator_financials_5y (operator_id, year, revenue_usd_b, ebitda_usd_b, capex_usd_b)
                                VALUES (%s, %s, %s, %s, %s);
                            """, (op_id, yr_num or 2024, rev, ebitda, capex))
                            fin_count += 1
                    else:
                        rev = grp.get('revenue_usd_bn')
                        cur.execute("""
                            INSERT INTO operator_financials_5y (operator_id, year, revenue_usd_b, ebitda_usd_b, capex_usd_b)
                            VALUES (%s, %s, %s, %s, %s);
                        """, (op_id, 2024, rev, None, None))
                        fin_count += 1

            conn.commit()
            print(f"Migrated {fin_count} financial records.")

    print("\nDatabase migration completed successfully!")
    cur.close()
    conn.close()

if __name__ == '__main__':
    main()

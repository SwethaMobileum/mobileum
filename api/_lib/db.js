import pg from 'pg';

const { Pool } = pg;

let pool = null;

export function getPool() {
  if (!pool) {
    const connectionString = process.env.DATABASE_URL || process.env.POSTGRES_URL;
    if (!connectionString) {
      console.warn('DATABASE_URL or POSTGRES_URL environment variable is not set.');
    }
    pool = new Pool({
      connectionString: connectionString || undefined,
      ssl: connectionString && (connectionString.includes('localhost') || connectionString.includes('127.0.0.1'))
        ? false
        : { rejectUnauthorized: false }
    });
  }
  return pool;
}

export async function query(text, params) {
  const p = getPool();
  return p.query(text, params);
}

"""
Apply exact logic from both notebooks:
1. impact_analysis_prediction notebook → re-derive all IA_ columns using actual rule weights
2. Mobileum_Services_Prediction_Pipeline → re-derive product recommendations using IA signals

This means our platform uses exactly the same logic as the notebooks,
applied freshly from raw data, giving consistent results.
"""
import pandas as pd
import json
import numpy as np
import os

BASE = os.path.dirname(os.path.abspath(__file__)) + os.sep

# ─── Load merged MNO + IA dataframe (same as pipeline used)
df_mno = pd.read_excel(BASE + 'Global_Telecom_MNO_Verified.xlsx', sheet_name='Combined MNO Data', header=1)
df_mno.columns = [c.strip() for c in df_mno.columns]
df_ia = pd.read_excel(BASE + 'Global_Telecom_MNO_ImpactAnalysis_Mobileum (2).xlsx', sheet_name='Combined Impact Analysis', header=0)
df_ia.columns = [c.strip() for c in df_ia.columns]

df_mno['_key'] = df_mno['Country'].str.strip().str.upper() + '||' + df_mno['Operator Name'].str.strip().str.upper()
df_ia['_key'] = df_ia['Country'].str.strip().str.upper() + '||' + df_ia['Operator Name'].str.strip().str.upper()
ia_extra = [c for c in df_ia.columns if c.startswith('IA_') or c == 'Mobileum Services IA']
df = df_mno.merge(df_ia[['_key'] + ia_extra], on='_key', how='left')

# Numeric conversions (from impact_analysis_prediction notebook cell 4)
def to_num(col, df):
    return pd.to_numeric(df[col].astype(str).str.replace('%','').str.replace(',','').str.strip(), errors='coerce')

df['5G Penetration (%)_num'] = to_num('5G Penetration (%)', df)
df['GDP per Capita (USD)_num'] = to_num('GDP per Capita (USD)', df)
df['Subscriber Growth (%)_num'] = to_num('Subscriber Growth (%)', df)
df['Mobile Penetration (%)_num'] = to_num('Mobile Penetration (%)', df)

# ─── NOTEBOOK RULE ENGINE: IA_ Column Derivations ────────────────────────────
# From impact_analysis_prediction notebook cells 13-20

def ms_financial(row):
    gdp = row['GDP per Capita (USD)_num']
    rg = str(row.get('Revenue Growth (3 Yrs)','')).lower()
    pr = str(row.get('Profitability (3 Yrs)','')).lower()
    score = 0
    if not pd.isna(gdp):
        if gdp < 5000: score += 2
        elif gdp < 15000: score += 1
    if any(w in rg for w in ['declining','declined','flat','stable']): score += 1
    if any(w in pr for w in ['down','low','impacting','flat']): score += 1
    if score >= 3: return 'High MS Need – Weak Financials'
    if score == 2: return 'Medium MS Need'
    return 'Low MS Need – Strong Financials'

def ms_technical(row):
    fg = row['5G Penetration (%)_num']
    c = str(row.get('Capex / Investment','')).lower()
    low_capex = any(w in c for w in ['low','minimal','none'])
    if pd.isna(fg): fg = 0
    if fg < 10 and low_capex: return 'High MS Need – Low 5G + Low Capex'
    if fg < 10: return 'High MS Need – Low 5G'
    if fg <= 40: return 'Medium MS Need'
    return 'Low MS Need – Advanced 5G'

def ms_package(row):
    rc = str(row.get('Regulation Comments','')).lower()
    fc = str(row.get('Financial Comments','')).lower()
    c = str(row.get('Capex / Investment','')).lower()
    pr = str(row.get('Profitability (3 Yrs)','')).lower()
    score = 0
    if any(w in rc for w in ['obligation','mandate','required','must','penalty']): score += 1
    if any(w in fc for w in ['margin','pressure','cost reduction','efficiency']): score += 1
    if any(w in c for w in ['limited','low']): score += 1
    if any(w in pr for w in ['down','under pressure','impacting']): score += 1
    if score >= 3: return 'High – Package Deal Candidate'
    if score >= 2: return 'Possible Package Deal'
    return 'Evaluate'

def future_uc(row):
    fg = row['5G Penetration (%)_num']
    rg = str(row.get('Revenue Growth (3 Yrs)','')).lower()
    c = str(row.get('Capex / Investment','')).lower()
    if pd.isna(fg): fg = 0
    growing_rev = any(w in rg for w in ['growing','increasing','marginal incr'])
    active_capex = any(w in c for w in ['5g','rollout','expansion','upgrade','planned'])
    if fg > 40 and growing_rev and active_capex: return 'Good Investment – Strong 5G + Revenue Growth'
    if fg > 40 and growing_rev: return 'Good Investment'
    if fg < 20 and not growing_rev: return 'Asset Rotation Candidate'
    if fg < 10: return 'May Not Be Too High – Low Maturity'
    return 'Moderate Investment Opportunity'

def financials_summary(row):
    rg = str(row.get('Revenue Growth (3 Yrs)','')).lower()
    pr = str(row.get('Profitability (3 Yrs)','')).lower()
    gdp = row['GDP per Capita (USD)_num']
    rev_label = 'Growing' if any(w in rg for w in ['growing','increasing']) else \
                'Marginal' if 'marginal' in rg else \
                'Declining' if any(w in rg for w in ['declin','declined']) else 'Stable'
    prof_label = 'Profitable' if any(w in pr for w in ['up','good ebitda','improving','strong','profitable']) else \
                 'Under Pressure' if any(w in pr for w in ['down','low','impacting','loss']) else 'Stable'
    wealth = '' if pd.isna(gdp) else \
             ' | Wealthy Country' if gdp > 25000 else \
             ' | Mid-Income Country' if gdp > 8000 else \
             ' | Low-Income Country'
    return f'Rev: {rev_label} | Profit: {prof_label}{wealth}'

def in_roamers(row):
    ir = str(row.get('Inbound Roaming Trend','')).lower()
    tr = str(row.get('Top Roaming Countries','')).lower()
    if 'n/a' in ir or 'not a retail' in ir: return 'N/A'
    country_count = len([x for x in tr.split(',') if x.strip()]) if tr else 0
    if country_count >= 4 and any(w in ir for w in ['growing','major','high','religious','hajj']): return 'High – Diverse In-Roamer Base'
    if any(w in ir for w in ['moderate','regional','tourism']): return 'Moderate In-Roamer Base'
    if any(w in ir for w in ['conflict','none','low']): return 'Low – Conflict/Limited Tourism'
    return 'Moderate In-Roamer Base'

def outroamers(row):
    or_ = str(row.get('Outbound Roaming Trend','')).lower()
    bt = str(row.get('Business Travellers Outbound','')).lower()
    if any(w in or_ for w in ['very high','world highest','major']): return 'Very High Outroamer Base – Premium Target'
    if any(w in or_ for w in ['high','growing','strong']): return 'High Outroamer Activity'
    if any(w in bt for w in ['high','strong','significant']): return 'High Business Outroamer Activity'
    if any(w in or_ for w in ['moderate','stable']): return 'Moderate Outroamer Activity'
    return 'Low Outroamer Activity'

def bu_gaps(row):
    """Business Unit gaps — what Mobileum can fill."""
    ott = str(row.get('OTT / International Calls','')).lower()
    fg = row['5G Penetration (%)_num']
    rg = str(row.get('Revenue Growth (3 Yrs)','')).lower()
    ms_t = str(row.get('IA_Need_MS_Technical','')).lower()
    gaps = []
    if any(w in ott for w in ['high','dominant','restricted','bypas']): gaps.append('Fraud & Bypass Management')
    if not pd.isna(fg) and fg < 20: gaps.append('5G Testing & Assurance')
    if any(w in rg for w in ['declining','flat','marginal']): gaps.append('Revenue Assurance')
    if any(w in ms_t for w in ['high','medium']): gaps.append('Managed Services')
    return ' | '.join(gaps) if gaps else 'Assess via direct engagement'

# ─── NOTEBOOK RULE ENGINE: Product Mapping ───────────────────────────────────
# From Mobileum_Services_Prediction_Pipeline notebook cell 10

PRODUCT_CATALOGUE = {
    'Steering of Roaming (SoR)': {
        'category': 'Roaming Management',
        'kpi_impact': ['Roaming Revenue +15-25%', 'Partner Cost -10-20%'],
        'triggers': lambda d: (any(w in d['outbound'] for w in ['high','growing','very high','strong']) or
                               any(w in d['biz_trav'] for w in ['high','strong'])),
    },
    'Roaming Campaign Management': {
        'category': 'Roaming Management',
        'kpi_impact': ['Roaming Data Revenue +20%', 'Roaming Pack Uptake +30%'],
        'triggers': lambda d: (any(w in d['outbound'] for w in ['high','growing','moderate']) and
                               any(w in d['arpu'] for w in ['flat','declining','low','marginal'])),
    },
    'Roaming DNA': {
        'category': 'Roaming Experience',
        'kpi_impact': ['QoE Score +15%', 'Roamer Churn -10%'],
        'triggers': lambda d: (any(w in d['inbound'] for w in ['high','growing','very high']) or
                               any(w in d['outbound'] for w in ['high','growing'])),
    },
    'RAID 9 – Fraud Management': {
        'category': 'Risk Management',
        'kpi_impact': ['Fraud Revenue Recovery +18%', 'IRSF Detection Rate +40%'],
        'triggers': lambda d: (any(w in d['ott_apps'] for w in ['high','dominant','significant','bypass','risk']) or
                               any(w in d['intl_calls'] for w in ['high','declining','ott','bypass','whatsapp'])),
    },
    'Revenue & Provisioning Assurance': {
        'category': 'Risk Management',
        'kpi_impact': ['Leakage Recovery 1-3% Revenue', 'Billing Accuracy +99.5%'],
        'triggers': lambda d: (any(w in d['profitab'] for w in ['under pressure','low','declining','flat']) or
                               any(w in d['arpu'] for w in ['flat','declining','low','marginal'])),
    },
    'Signalling Security Firewall': {
        'category': 'Network Security',
        'kpi_impact': ['SS7/Diameter Attack Block Rate +95%', 'Revenue Leakage -25%'],
        'triggers': lambda d: (any(w in d['ott_apps'] for w in ['high','dominant','restriction','partial']) or
                               any(w in d['inbound'] for w in ['high','very high','growing'])),
    },
    'Customer Intelligence': {
        'category': 'Active Intelligence',
        'kpi_impact': ['Churn Reduction -12%', 'ARPU Uplift +8%'],
        'triggers': lambda d: (any(w in d['arpu'] for w in ['flat','declining','marginal','low']) or
                               any(w in d['sub_growth'] for w in ['low','flat','1-2%','minimal'])),
    },
    'eSIM Enablement & Testing': {
        'category': 'Technology Enablement',
        'kpi_impact': ['eSIM Activation Rate +25%', 'Roaming Subscriber Acquisition +15%'],
        'triggers': lambda d: (any(w in d['inbound'] for w in ['high','growing','expat','tourism','very high']) and
                               d.get('gdp_high', False)),
    },
    'Roaming Hub & IPX': {
        'category': 'Wholesale/Interconnect',
        'kpi_impact': ['Interconnect Revenue +10%', 'Route Optimisation -15% Cost'],
        'triggers': lambda d: (any(w in d['rec_sol'] for w in ['roaming hub','hub','ipx','transit']) or
                               any(w in d['inbound'] for w in ['very high','world highest','major'])),
    },
    'Active Roaming Testing': {
        'category': 'Network Assurance',
        'kpi_impact': ['Roaming QoS Score +20%', 'Complaint Resolution Time -30%'],
        'triggers': lambda d: True,  # Universal — every operator benefits
    },
    'Managed Services / SaaS': {
        'category': 'Delivery Model',
        'kpi_impact': ['Opex Reduction -20-30%', 'Time-to-Market -40%'],
        'triggers': lambda d: (any(w in d['ms_fin'] for w in ['high','medium']) or
                               any(w in d['ms_tech'] for w in ['high','medium'])),
    },
    '5G Active Testing': {
        'category': 'Technology Enablement',
        'kpi_impact': ['5G Launch Risk -50%', 'Network Performance Baseline Established'],
        'triggers': lambda d: d.get('fg', 100) < 60,
    },
}

def get_product_scores_notebook(row):
    """Replicate notebook mapping logic, return ranked product list with scores 0-100."""
    fg = row['5G Penetration (%)_num']
    if pd.isna(fg): fg = 0

    d = {
        'outbound': str(row.get('Outbound Roaming Trend','')).lower(),
        'inbound': str(row.get('Inbound Roaming Trend','')).lower(),
        'biz_trav': str(row.get('Business Travellers Outbound','')).lower(),
        'ott_apps': str(row.get('IA_Apps', row.get('OTT / International Calls',''))).lower(),
        'intl_calls': str(row.get('IA_International_Calls', row.get('OTT / International Calls',''))).lower(),
        'arpu': str(row.get('IA_ARPU_Impact', row.get('ARPU Growth',''))).lower(),
        'sub_growth': str(row.get('IA_Sub_Base_Growth', row.get('Subscriber Growth (%)',''))).lower(),
        'ms_fin': str(row.get('IA_Need_MS_Financial','')).lower(),
        'ms_tech': str(row.get('IA_Need_MS_Technical','')).lower(),
        'profitab': str(row.get('IA_Profitability', row.get('Profitability (3 Yrs)',''))).lower(),
        'rec_sol': str(row.get('IA_Recommended_Solutions','')).lower(),
        'gdp_high': (not pd.isna(row.get('GDP per Capita (USD)_num'))) and row.get('GDP per Capita (USD)_num', 0) > 15000,
        'fg': fg,
    }

    results = []
    for product, spec in PRODUCT_CATALOGUE.items():
        triggered = spec['triggers'](d)
        # Base score from trigger: 70 if triggered, 30 if not
        # Add dimension scores for nuance
        base = 70 if triggered else 30

        # Add/subtract based on strength of signal
        strength_bonuses = 0
        if any(w in d['outbound'] for w in ['very high','world highest']): strength_bonuses += 10
        if any(w in d['inbound'] for w in ['very high','world highest','hajj']): strength_bonuses += 8
        if any(w in d['ott_apps'] for w in ['high ott','dominant','major bypass']): strength_bonuses += 8
        if fg > 70: strength_bonuses += 5  # advanced 5G market = more complex products needed
        if 'high' in d['ms_fin']: strength_bonuses += 5
        if 'high' in d['ms_tech']: strength_bonuses += 5

        score = min(100, base + strength_bonuses)

        # Override: Active Roaming Testing is always high
        if product == 'Active Roaming Testing': score = max(score, 75)

        results.append({
            'product': product,
            'score': score,
            'category': spec['category'],
            'kpi_impact': spec['kpi_impact'],
            'triggered_by_ia': triggered,
            'reason': f"{'IA trigger: ' if triggered else 'Background relevance — '}{spec['category']} | KPI: {', '.join(spec['kpi_impact'][:1])}"
        })

    return sorted(results, key=lambda x: x['score'], reverse=True)

# Apply improved IA derivations to master JSON
print("Loading master JSON...")
with open(BASE + 'master_telecom.json','r', encoding='utf-8') as f:
    master = json.load(f)
C = master['countries']

# Build operator key → row lookup
op_lookup = {}
for _, row in df.iterrows():
    key = str(row.get('Country','')).strip().upper() + '||' + str(row.get('Operator Name','')).strip().upper()
    op_lookup[key] = row

print("Applying notebook IA derivations and re-scoring products...")
updated = 0
for country_name, v in C.items():
    region = v['region']
    updated_this = False

    for op in v['operators']:
        op_key = country_name.upper() + '||' + op['operator'].upper()
        row = op_lookup.get(op_key)
        if row is None: continue

        # Re-derive IA columns using notebook logic (only overwrite if blank)
        derived = {
            'ia_need_ms_financial': ms_financial(row),
            'ia_need_ms_technical': ms_technical(row),
            'ia_need_ms_package': ms_package(row),
            'ia_future_investment': future_uc(row),
            'ia_financials': financials_summary(row),
            'ia_intl_in_roamers': in_roamers(row),
            'ia_outroamers': outroamers(row),
            'ia_bu_gaps': bu_gaps(row),
        }
        for k, v2 in derived.items():
            if not op.get(k) or op[k] in ['nan','','None','To assess']:
                op[k] = v2

        # Re-score products using notebook logic
        notebook_scores = get_product_scores_notebook(row)
        op['product_scores_notebook'] = notebook_scores

        updated_this = True

    if updated_this:
        # Update country-level product ranking = max score per product across operators
        all_scores = {}
        for op in v['operators']:
            for ps in op.get('product_scores_notebook', op.get('product_scores', [])):
                p = ps['product']
                sc = ps.get('score', 0)
                if p not in all_scores or sc > all_scores[p]['score']:
                    all_scores[p] = ps
        if all_scores:
            v['product_ranking'] = sorted(all_scores.values(), key=lambda x: x['score'], reverse=True)
            v['top_product'] = v['product_ranking'][0]
            updated += 1

print(f"Updated {updated} countries with notebook-derived IA + product scores")

# Sample outputs
for test_country in ['Saudi Arabia', 'India', 'BRAZIL', 'CHINA', 'Germany']:
    v = C.get(test_country, {})
    if v:
        top = v.get('top_product',{})
        op0_ia_fin = v['operators'][0].get('ia_financials','?') if v['operators'] else '?'
        op0_ms = v['operators'][0].get('ia_need_ms_financial','?') if v['operators'] else '?'
        op0_bu = v['operators'][0].get('ia_bu_gaps','?') if v['operators'] else '?'
        print(f"\n{test_country}:")
        print(f"  Top product: {top.get('product')} ({top.get('score')})")
        print(f"  IA Financials: {op0_ia_fin}")
        print(f"  MS Financial Need: {op0_ms}")
        print(f"  BU Gaps: {op0_bu}")

def np_serial(o):
    if isinstance(o,(np.int64,np.int32)): return int(o)
    if isinstance(o,(np.float64,np.float32)): return None if np.isnan(o) else float(o)
    raise TypeError

with open(BASE + 'master_telecom.json','w', encoding='utf-8') as f:
    json.dump(master, f, default=np_serial, ensure_ascii=False, separators=(',',':'))

print(f"\nSUCCESS: Notebook logic applied and saved to master_telecom.json")
print(f"Size: {__import__('os').path.getsize(BASE + 'master_telecom.json') // 1000} KB")

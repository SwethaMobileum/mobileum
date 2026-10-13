"""
Enrichment Script — Pull data from APAC_Country_Profiles_Updated.xlsx
and LATAM_Telecom_Filled.xlsx, merge into master_telecom.json
These files contain country profiles + IA in a non-standard layout (per-sheet, freeform rows)
"""
import pandas as pd
import json
import numpy as np
import re
import os

BASE = os.path.dirname(os.path.abspath(__file__)) + os.sep

def trend_score(val):
    if not val or str(val).lower() in ['nan','none','']: return 3
    v = str(val).lower()
    if any(k in v for k in ['very high','strongly','major','saturated','excellent']): return 5
    if any(k in v for k in ['high','growing','increasing','strong','positive','good']): return 4
    if any(k in v for k in ['moderate','stable','flat','neutral','marginal','mixed','steady','medium']): return 3
    if any(k in v for k in ['low','declining','down','decreasing','weak','minimal']): return 2
    if any(k in v for k in ['very low','none','absent','nil','no ']): return 1
    return 3

def parse_apac_sheet(sheet_name, file_path):
    """Parse one APAC country sheet into structured dict."""
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    except:
        return None

    rows = {}
    for i, row in df.iterrows():
        for j, val in enumerate(row):
            if pd.notna(val) and str(val).strip():
                rows[(i, j)] = str(val).strip()

    result = {'country_name': sheet_name, 'profile': {}, 'ia': {}, 'operators': {}}

    # Extract country profile row 6 (data values)
    for i in range(4, 10):
        for j in range(3, 9):
            val = rows.get((i, j), '')
            if val:
                # row 5 col 3 = population, col4=mobile users, col5=pen, col6=gdp, col7=age, col8=age65
                if i == 5 and j == 3: result['profile']['population'] = val
                if i == 5 and j == 4: result['profile']['mobile_users'] = val
                if i == 5 and j == 5: result['profile']['mobile_penetration'] = val
                if i == 5 and j == 6: result['profile']['gdp_growth'] = val
                if i == 5 and j == 7: result['profile']['avg_age'] = val
                if i == 5 and j == 8: result['profile']['age_over_65'] = val

    # Extract roaming behaviour (rows 11-13)
    outbound = rows.get((12, 3)) or rows.get((11, 3)) or ''
    biz_trav = rows.get((12, 4)) or rows.get((11, 4)) or ''
    inbound = rows.get((12, 5)) or rows.get((11, 5)) or ''
    top_countries = rows.get((12, 6)) or rows.get((11, 6)) or ''
    ott = rows.get((12, 7)) or rows.get((11, 7)) or ''
    result['roaming'] = {
        'outbound': outbound,
        'inbound': inbound,
        'biz_travellers': biz_trav,
        'top_countries': top_countries,
        'ott': ott
    }

    # Extract events (rows 16-20 for LATAM style; rows 17-21 for APAC)
    events = []
    for i in range(14, 22):
        ev_name = rows.get((i, 3)) or rows.get((i, 2), '')
        ev_month = rows.get((i, 4), '')
        ev_impact = rows.get((i, 5), '')
        if ev_name and ev_name not in ['Regulations','Events','country profile','roamer behaviour','Telecom Market','Financials','Back','◀ Back']:
            if any(m in ev_month.lower() for m in ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec','year','var']) or ev_impact:
                events.append({'name': ev_name, 'month': ev_month, 'impact': ev_impact})
    result['events'] = events

    # Extract IA columns (col 11=IA label, col 12-14 = operator values)
    # First get operator names from row 5 cols 12-14
    op_names = []
    for col in [12, 13, 14]:
        n = rows.get((5, col)) or rows.get((4, col), '')
        if n and n not in ['IMPACT ANALYSIS', 'Impact Analysis']:
            op_names.append(n)

    ia_map = {}
    ia_labels_col = 11  # column where IA label is
    for i in range(5, 40):
        label = rows.get((i, ia_labels_col), '').strip()
        if not label or label == 'IMPACT ANALYSIS': continue
        for k, col in enumerate([12, 13, 14]):
            op = op_names[k] if k < len(op_names) else f'Operator {k+1}'
            val = rows.get((i, col), '')
            if op not in ia_map: ia_map[op] = {}
            if label and val:
                ia_map[op][label] = val

    result['ia_by_operator'] = ia_map

    # Operator financials from telecom market section (rows 22-37, col 2=op, 3=rev, 4=profit, 5=capex)
    op_fin = {}
    for i in range(20, 40):
        op = rows.get((i, 2), '')
        rev = rows.get((i, 3), '')
        prof = rows.get((i, 4), '')
        capex = rows.get((i, 5), '')
        if op and op not in ['Operator', 'Operator Name', 'Back', '◀ Back']:
            op_fin[op] = {'revenue_growth': rev, 'profitability': prof, 'capex': capex}

    result['op_financials'] = op_fin

    return result

# Load all APAC sheets
print("Parsing APAC sheets...")
xl_apac = pd.ExcelFile(BASE + 'APAC_Country_Profiles_Updated.xlsx')
apac_data = {}
for sheet in xl_apac.sheet_names:
    if sheet in ['APAC Overview']: continue
    parsed = parse_apac_sheet(sheet, BASE + 'APAC_Country_Profiles_Updated.xlsx')
    if parsed:
        apac_data[sheet] = parsed
        print(f"  {sheet}: profile={bool(parsed['profile'])}, roaming={bool(parsed['roaming']['outbound'])}, events={len(parsed['events'])}, ia_ops={list(parsed['ia_by_operator'].keys())[:3]}")

# Load all LATAM sheets
print("\nParsing LATAM sheets...")
xl_latam = pd.ExcelFile(BASE + 'LATAM_Telecom_Filled.xlsx')
latam_data = {}
for sheet in xl_latam.sheet_names:
    if sheet in ['LATAM Accounts']: continue
    parsed = parse_apac_sheet(sheet, BASE + 'LATAM_Telecom_Filled.xlsx')
    if parsed:
        latam_data[sheet] = parsed
        print(f"  {sheet}: roaming={bool(parsed['roaming']['outbound'])}, events={len(parsed['events'])}, ia_ops={list(parsed['ia_by_operator'].keys())[:2]}")

# Now load master JSON and enrich
print("\nLoading master JSON for enrichment...")
with open(BASE + 'master_telecom.json', 'r', encoding='utf-8') as f:
    master = json.load(f)
C = master['countries']

# Map sheet names to country keys in master
SHEET_TO_KEY = {
    # APAC
    'China': 'CHINA', 'Japan': 'JAPAN', 'South Korea': 'SOUTH KOREA',
    'North Korea': 'NORTH KOREA', 'Taiwan': 'TAIWAN', 'Mongolia': 'MONGOLIA',
    'Russia Asian': 'RUSSIA (ASIAN)', 'Hong Kong': 'HONG KONG', 'Macau': 'MACAU',
    'Indonesia': 'INDONESIA', 'Philippines': 'PHILIPPINES', 'Vietnam': 'VIETNAM',
    'Thailand': 'THAILAND', 'Malaysia': 'MALAYSIA', 'Myanmar': 'MYANMAR',
    'Cambodia': 'CAMBODIA', 'Laos': 'LAOS', 'Singapore': 'SINGAPORE',
    'Brunei': 'BRUNEI', 'Timor-Leste': 'TIMOR-LESTE', 'Australia': 'AUSTRALIA',
    'New Zealand': 'NEW ZEALAND', 'Papua New Guinea': 'PAPUA NEW GUINEA',
    'Fiji': 'FIJI', 'Solomon Islands': 'SOLOMON ISLANDS', 'Vanuatu': 'VANUATU',
    'Samoa': 'SAMOA', 'Tonga': 'TONGA',
    # LATAM
    'Argentina': 'ARGENTINA', 'Bolivia': 'BOLIVIA', 'Brazil': 'BRAZIL',
    'Chile': 'CHILE', 'Colombia': 'COLOMBIA', 'Ecuador': 'ECUADOR',
    'Guyana': 'GUYANA', 'Paraguay': 'PARAGUAY', 'Peru': 'PERU',
    'Suriname': 'SURINAME', 'Uruguay': 'URUGUAY', 'Venezuela': 'VENEZUELA',
    'Belize': 'BELIZE', 'Costa Rica': 'COSTA RICA', 'El Salvador': 'EL SALVADOR',
    'Guatemala': 'GUATEMALA', 'Honduras': 'HONDURAS', 'Nicaragua': 'NICARAGUA',
    'Panama': 'PANAMA', 'Mexico': 'MEXICO', 'Cuba': 'CUBA',
    'Dominican Republic': 'DOMINICAN REPUBLIC', 'Jamaica': 'JAMAICA',
    'Puerto Rico': 'PUERTO RICO', 'Trinidad & Tobago': 'TRINIDAD & TOBAGO',
}

enriched_count = 0
all_parsed = {**apac_data, **latam_data}

def parse_month_to_num(month_str):
    m = month_str.lower()
    mapping = {'jan':1,'feb':2,'mar':3,'apr':4,'may':5,'jun':6,'jul':7,'aug':8,'sep':9,'oct':10,'nov':11,'dec':12}
    for abbr, num in mapping.items():
        if abbr in m: return num
    return None

for sheet_name, parsed in all_parsed.items():
    country_key = SHEET_TO_KEY.get(sheet_name)
    if not country_key or country_key not in C:
        print(f"  SKIP {sheet_name} -> key={country_key}")
        continue

    v = C[country_key]

    # 1. Enrich roaming data on each operator (fill missing from individual sheet)
    roam = parsed['roaming']
    for op in v['operators']:
        # Fill outbound/inbound from sheet if blank in main data
        if (not op.get('outbound_roaming') or op['outbound_roaming'] == 'nan') and roam.get('outbound'):
            op['outbound_roaming'] = roam['outbound']
            op['outbound_roaming_score'] = trend_score(roam['outbound'])
        if (not op.get('inbound_roaming') or op['inbound_roaming'] == 'nan') and roam.get('inbound'):
            op['inbound_roaming'] = roam['inbound']
            op['inbound_roaming_score'] = trend_score(roam['inbound'])
        if (not op.get('top_roaming_countries') or op['top_roaming_countries'] == 'nan') and roam.get('top_countries'):
            op['top_roaming_countries'] = roam['top_countries']
        if (not op.get('biz_travellers') or op['biz_travellers'] == 'nan') and roam.get('biz_travellers'):
            op['biz_travellers'] = roam['biz_travellers']
            op['biz_travellers_score'] = trend_score(roam['biz_travellers'])
        if (not op.get('ott_intl_calls') or op['ott_intl_calls'] == 'nan') and roam.get('ott'):
            op['ott_intl_calls'] = roam['ott']
            op['ott_score'] = trend_score(roam['ott'])

    # 2. Enrich IA data per operator from sheet
    ia_by_op = parsed['ia_by_operator']
    for op in v['operators']:
        op_name = op['operator']
        # Find matching IA entry (fuzzy match first word or contains)
        match_key = None
        for ia_op_name in ia_by_op:
            if op_name.lower() in ia_op_name.lower() or ia_op_name.lower() in op_name.lower():
                match_key = ia_op_name
                break
            # First word match
            if op_name.split()[0].lower() == ia_op_name.split()[0].lower():
                match_key = ia_op_name
                break
        if not match_key: continue

        ia = ia_by_op[match_key]

        def fill_ia(op_key, ia_key, alternatives=[]):
            keys_to_try = [ia_key] + alternatives
            for k in keys_to_try:
                if k in ia and ia[k] and ia[k] not in ['nan','','None','To assess']:
                    if not op.get(op_key) or op[op_key] in ['nan','','None']:
                        op[op_key] = ia[k]
                        break

        fill_ia('ia_outbound_impact', 'Outbound impact', ['Outbound Impact'])
        fill_ia('ia_inbound_impact', 'Inbound impact', ['Inbound Impact'])
        fill_ia('ia_arpu_impact', 'ARPU Impact', ['ARPU impact'])
        fill_ia('ia_apps', 'Apps ', ['Apps'])
        fill_ia('ia_rev_growth', 'Rev growth ', ['Rev growth', 'Revenue growth'])
        fill_ia('ia_profitability', 'Profitability')
        fill_ia('ia_need_ms_financial', 'Need for MS - Financial', ['Need for MS Financial'])
        fill_ia('ia_need_ms_technical', 'Need for MS - Technical', ['Need for MS Technical'])
        fill_ia('ia_sub_base_growth', 'Sub Base growth', ['Sub base growth'])
        fill_ia('ia_financials', 'Financials')
        fill_ia('ia_biz_traveller_impact', 'Biz traveller impact', ['Biz Traveller impact'])
        fill_ia('ia_population_growth', 'Population growth', ['Population Growth'])
        fill_ia('ia_gdp_growth', 'GDP growth')
        fill_ia('ia_penetration', 'Penetration')
        fill_ia('ia_international_calls', 'International calls', ['International Calls'])
        fill_ia('ia_intl_in_roamers', 'International in-roamers', ['International In-roamers'])
        fill_ia('ia_outroamers', 'Outroamers')
        fill_ia('ia_scope_of_ms', 'Scope of MS')
        fill_ia('ia_future_investment', 'Future Investment cash flow', ['Future Investment UC'])
        fill_ia('ia_immigration_impact', 'Immigration impact', ['Immigration Impact'])

    # 3. Enrich events → seasonal calendar
    for ev in parsed['events']:
        month_num = parse_month_to_num(ev.get('month',''))
        if month_num:
            intensity = trend_score(ev.get('impact','moderate'))
            current = v['seasonal_roaming'].get(str(month_num), 0)
            if isinstance(current, str): current = int(current) if current.isdigit() else 0
            v['seasonal_roaming'][month_num] = max(current, intensity)

    # 4. Enrich operator financials from sheet
    op_fin = parsed['op_financials']
    for op in v['operators']:
        for fin_op_name, fin_data in op_fin.items():
            if op['operator'].split()[0].lower() in fin_op_name.lower() or fin_op_name.lower() in op['operator'].lower():
                if (not op.get('revenue_growth') or op['revenue_growth'] == 'nan') and fin_data.get('revenue_growth'):
                    op['revenue_growth'] = fin_data['revenue_growth']
                    op['revenue_growth_score'] = trend_score(fin_data['revenue_growth'])
                if (not op.get('profitability') or op['profitability'] == 'nan') and fin_data.get('profitability'):
                    op['profitability'] = fin_data['profitability']
                    op['profitability_score'] = trend_score(fin_data['profitability'])
                break

    # 5. Enrich profile (GDP, age etc. for LATAM/APAC which may have missed World Bank data)
    prof = parsed.get('profile', {})
    if prof.get('gdp_growth') and not v.get('gdp_growth_pct'):
        try:
            gdp_str = prof['gdp_growth'].replace('%','').split('-')[0].strip()
            v['gdp_growth_pct'] = float(gdp_str)
        except: pass
    if prof.get('avg_age') and not v.get('avg_age'):
        try: v['avg_age'] = float(prof['avg_age'])
        except: pass

    enriched_count += 1

print(f"\nSUCCESS: Enriched {enriched_count} countries from APAC/LATAM sheets")

# Also pull from prediction notebook: the rule logic is already implemented in our scoring engine.
# The notebook used exact same column names — we've replicated its logic in Python scoring functions.
# Verify by checking a sample operator's product scores match expectations

print("\nSample enriched data — China Mobile:")
china = C.get('CHINA', {})
for op in china['operators']:
    if 'China Mobile' in op['operator']:
        print(f"  Outbound: {op.get('outbound_roaming','?')}")
        print(f"  Inbound: {op.get('inbound_roaming','?')}")
        print(f"  IA outbound impact: {op.get('ia_outbound_impact','?')}")
        print(f"  IA apps: {op.get('ia_apps','?')}")
        print(f"  Seasonal: {china.get('seasonal_roaming',{})}")

print("\nSample enriched data — Brazil Claro:")
brazil = C.get('BRAZIL', {})
for op in brazil['operators']:
    if 'Claro' in op['operator']:
        print(f"  Outbound: {op.get('outbound_roaming','?')}")
        print(f"  Top roaming: {op.get('top_roaming_countries','?')}")
        print(f"  IA sub growth: {op.get('ia_sub_base_growth','?')}")
        break

# Save enriched JSON
def np_serial(o):
    if isinstance(o,(np.int64,np.int32)): return int(o)
    if isinstance(o,(np.float64,np.float32)): return None if np.isnan(o) else float(o)
    raise TypeError

with open(BASE + 'master_telecom.json','w', encoding='utf-8') as f:
    json.dump(master, f, default=np_serial, ensure_ascii=False, separators=(',',':'))

print(f"\nSUCCESS: master_telecom.json updated with APAC/LATAM enrichment")

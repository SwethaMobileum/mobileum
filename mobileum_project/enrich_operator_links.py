"""
Enrichment Script — Populate global operator links across master_telecom.json,
operator_financials.json, and operator_performance_tracker.js
Only populates verified direct URLs. Never generates Google Search links.
"""
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MASTER_JSON_PATH = os.path.join(BASE_DIR, 'master_telecom.json')
REACT_DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'mobileum_react', 'src', 'data'))
FINANCIALS_JSON_PATH = os.path.join(REACT_DATA_DIR, 'operator_financials.json')

# Comprehensive Known Global Telecom Groups & Operators Direct Links Mapping
KNOWN_OPERATOR_LINKS = {
    # APAC / Global Flagships
    "AIRTEL": {
        "corporate_url": "https://www.airtel.in",
        "investor_url": "https://www.airtel.in/about-bharti/reports?path=quarterly-results",
        "annual_reports_url": "https://www.airtel.in/about-bharti/reports?path=annual-reports",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Bharti_Airtel"
    },
    "JIO": {
        "corporate_url": "https://www.jio.com",
        "investor_url": "https://www.jio.com/en-in/investor-relations",
        "annual_reports_url": "https://www.ril.com/investors/financial-reporting",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Jio"
    },
    "VODAFONE IDEA": {
        "corporate_url": "https://www.myvi.in",
        "investor_url": "https://www.myvi.in/investor-relations",
        "annual_reports_url": "https://www.myvi.in/investor-relations/reports",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Vodafone_Idea"
    },
    "VI (VODAFONE IDEA)": {
        "corporate_url": "https://www.myvi.in",
        "investor_url": "https://www.myvi.in/investor-relations",
        "annual_reports_url": "https://www.myvi.in/investor-relations/reports",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Vodafone_Idea"
    },
    "CHINA MOBILE": {
        "corporate_url": "https://www.chinamobileltd.com",
        "investor_url": "https://www.chinamobileltd.com/en/ir/reports.php",
        "annual_reports_url": "https://www.chinamobileltd.com/en/ir/reports/ar2024.pdf",
        "wikipedia_url": "https://en.wikipedia.org/wiki/China_Mobile"
    },
    "CHINA TELECOM": {
        "corporate_url": "http://www.chinatelecom-h.com",
        "investor_url": "http://www.chinatelecom-h.com/en/ir/reports.php",
        "annual_reports_url": "http://www.chinatelecom-h.com/en/ir/reports.php",
        "wikipedia_url": "https://en.wikipedia.org/wiki/China_Telecom"
    },
    "CHINA UNICOM": {
        "corporate_url": "https://www.chinaunicom.com.hk",
        "investor_url": "https://www.chinaunicom.com.hk/en/ir/reports.php",
        "annual_reports_url": "https://www.chinaunicom.com.hk/en/ir/reports.php",
        "wikipedia_url": "https://en.wikipedia.org/wiki/China_Unicom"
    },
    "SINGTEL": {
        "corporate_url": "https://www.singtel.com",
        "investor_url": "https://www.singtel.com/about-us/investor-relations",
        "annual_reports_url": "https://www.singtel.com/about-us/investor-relations/financial-results",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Singtel"
    },
    "TELSTRA": {
        "corporate_url": "https://www.telstra.com.au",
        "investor_url": "https://www.telstra.com.au/aboutus/investors",
        "annual_reports_url": "https://www.telstra.com.au/aboutus/investors/financial-information/reports",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Telstra"
    },
    "OPTUS": {
        "corporate_url": "https://www.optus.com.au",
        "investor_url": "https://www.singtel.com/about-us/investor-relations",
        "annual_reports_url": "https://www.singtel.com/about-us/investor-relations/financial-results",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Optus"
    },
    "NTT DATA": {
        "corporate_url": "https://www.nttdata.com",
        "investor_url": "https://www.nttdata.com/global/en/investors/",
        "annual_reports_url": "https://www.nttdata.com/global/en/investors/financial-information/",
        "wikipedia_url": "https://en.wikipedia.org/wiki/NTT_Data"
    },
    "NTT DOCOMO": {
        "corporate_url": "https://www.docomo.ne.jp/english/",
        "investor_url": "https://www.ntt.co.jp/ir/index_e.html",
        "annual_reports_url": "https://www.ntt.co.jp/ir/library_e/annual/",
        "wikipedia_url": "https://en.wikipedia.org/wiki/NTT_Docomo"
    },
    "KDDI": {
        "corporate_url": "https://www.kddi.com/english/",
        "investor_url": "https://www.kddi.com/english/corporate/ir/",
        "annual_reports_url": "https://www.kddi.com/english/corporate/ir/ir-library/annual-report/",
        "wikipedia_url": "https://en.wikipedia.org/wiki/KDDI"
    },
    "SOFTBANK": {
        "corporate_url": "https://www.softbank.jp/en/",
        "investor_url": "https://www.softbank.jp/en/corp/ir/",
        "annual_reports_url": "https://www.softbank.jp/en/corp/ir/documents/reports/",
        "wikipedia_url": "https://en.wikipedia.org/wiki/SoftBank_Group"
    },
    "RAKUTEN": {
        "corporate_url": "https://mobile.rakuten.co.jp",
        "investor_url": "https://global.rakuten.com/corp/investors/",
        "annual_reports_url": "https://global.rakuten.com/corp/investors/documents/",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Rakuten_Mobile"
    },
    "SK TELECOM": {
        "corporate_url": "https://www.sktelecom.com/index_en.html",
        "investor_url": "https://www.sktelecom.com/en/investor/main.do",
        "annual_reports_url": "https://www.sktelecom.com/en/investor/report/annual.do",
        "wikipedia_url": "https://en.wikipedia.org/wiki/SK_Telecom"
    },
    "KT": {
        "corporate_url": "https://corp.kt.com/eng/",
        "investor_url": "https://corp.kt.com/eng/investors/",
        "annual_reports_url": "https://corp.kt.com/eng/investors/financial-information/",
        "wikipedia_url": "https://en.wikipedia.org/wiki/KT_Corporation"
    },
    "TELKOMSEL": {
        "corporate_url": "https://www.telkomsel.com",
        "investor_url": "https://www.telkom.co.id/sites/enterprise/en/investor-relations",
        "annual_reports_url": "https://www.telkom.co.id/sites/enterprise/en/investor-relations/reports",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Telkomsel"
    },
    "AXIATA": {
        "corporate_url": "https://www.axiata.com",
        "investor_url": "https://www.axiata.com/investors",
        "annual_reports_url": "https://www.axiata.com/investors/reports",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Axiata"
    },
    "MAXIS": {
        "corporate_url": "https://www.maxis.com.my",
        "investor_url": "https://maxis.listedcompany.com",
        "annual_reports_url": "https://maxis.listedcompany.com/ar.html",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Maxis_Communications"
    },
    "AIS": {
        "corporate_url": "https://www.ais.th",
        "investor_url": "https://investor.ais.co.th",
        "annual_reports_url": "https://investor.ais.co.th/annual_reports.html",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Advanced_Info_Service"
    },
    "TRUE": {
        "corporate_url": "https://true.th",
        "investor_url": "https://www.true.th/ir",
        "annual_reports_url": "https://www.true.th/ir/reports",
        "wikipedia_url": "https://en.wikipedia.org/wiki/True_Corporation"
    },
    "VIETTEL": {
        "corporate_url": "https://viettel.com.vn",
        "investor_url": "https://viettel.com.vn/en/about-us",
        "annual_reports_url": "https://viettel.com.vn/en/news",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Viettel"
    },
    "GLOBE": {
        "corporate_url": "https://www.globe.com.ph",
        "investor_url": "https://www.globe.com.ph/about-us/investor-relations.html",
        "annual_reports_url": "https://www.globe.com.ph/about-us/investor-relations/financial-reports.html",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Globe_Telecom"
    },
    "PLDT": {
        "corporate_url": "https://main.pldt.com",
        "investor_url": "https://main.pldt.com/investor-relations",
        "annual_reports_url": "https://main.pldt.com/investor-relations/annual-reports",
        "wikipedia_url": "https://en.wikipedia.org/wiki/PLDT"
    },
    "SMART": {
        "corporate_url": "https://smart.com.ph",
        "investor_url": "https://main.pldt.com/investor-relations",
        "annual_reports_url": "https://main.pldt.com/investor-relations/annual-reports",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Smart_Communications"
    },

    # EMEA / MECA / Africa
    "MTN": {
        "corporate_url": "https://www.mtn.com",
        "investor_url": "https://www.mtn.com/investors/",
        "annual_reports_url": "https://www.mtn.com/investors/financial-results/",
        "wikipedia_url": "https://en.wikipedia.org/wiki/MTN_Group"
    },
    "ORANGE": {
        "corporate_url": "https://www.orange.com",
        "investor_url": "https://www.orange.com/en/investors",
        "annual_reports_url": "https://www.orange.com/en/investors/results-and-presentation",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Orange_S.A."
    },
    "VODAFONE": {
        "corporate_url": "https://www.vodafone.com",
        "investor_url": "https://www.vodafone.com/investors",
        "annual_reports_url": "https://www.vodafone.com/investors/results-reports-and-presentations",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Vodafone"
    },
    "STC": {
        "corporate_url": "https://www.stc.com.sa",
        "investor_url": "https://www.stc.com.sa/wps/wcm/connect/english/stc/investors",
        "annual_reports_url": "https://www.stc.com.sa/wps/wcm/connect/english/stc/investors/financialReports",
        "wikipedia_url": "https://en.wikipedia.org/wiki/STC_Group"
    },
    "E&": {
        "corporate_url": "https://eand.com",
        "investor_url": "https://eand.com/en/investor-relations.jsp",
        "annual_reports_url": "https://eand.com/en/investor-relations/financial-reports.jsp",
        "wikipedia_url": "https://en.wikipedia.org/wiki/E%26_(company)"
    },
    "ETISALAT": {
        "corporate_url": "https://eand.com",
        "investor_url": "https://eand.com/en/investor-relations.jsp",
        "annual_reports_url": "https://eand.com/en/investor-relations/financial-reports.jsp",
        "wikipedia_url": "https://en.wikipedia.org/wiki/E%26_(company)"
    },
    "MOBILY": {
        "corporate_url": "https://www.mobily.com.sa",
        "investor_url": "https://www.mobily.com.sa/wps/portal/Personal/AboutMobily/InvestorRelations",
        "annual_reports_url": "https://www.mobily.com.sa/wps/portal/Personal/AboutMobily/InvestorRelations/FinancialResults",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Mobily"
    },
    "ZAIN": {
        "corporate_url": "https://www.zain.com",
        "investor_url": "https://www.zain.com/en/investor-relations/",
        "annual_reports_url": "https://www.zain.com/en/investor-relations/financial-reports/",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Zain_Group"
    },
    "OOREDOO": {
        "corporate_url": "https://www.ooredoo.com",
        "investor_url": "https://www.ooredoo.com/en/investors/",
        "annual_reports_url": "https://www.ooredoo.com/en/investors/financial-information/financial-results/",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Ooredoo"
    },
    "VODACOM": {
        "corporate_url": "https://www.vodacom.com",
        "investor_url": "https://www.vodacom.com/investor-relations.php",
        "annual_reports_url": "https://www.vodacom.com/financial-results.php",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Vodacom"
    },
    "SAFARICOM": {
        "corporate_url": "https://www.safaricom.co.ke",
        "investor_url": "https://www.safaricom.co.ke/investor-relation",
        "annual_reports_url": "https://www.safaricom.co.ke/investor-relation/reports/financial-reports",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Safaricom"
    },

    # EUROPE & NORTH AMERICA / LATAM
    "TELEFONICA": {
        "corporate_url": "https://www.telefonica.com",
        "investor_url": "https://www.telefonica.com/en/shareholders-investors/",
        "annual_reports_url": "https://www.telefonica.com/en/shareholders-investors/financial-reports/",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Telef%C3%B3nica"
    },
    "AMERICA MOVIL": {
        "corporate_url": "https://www.americamovil.com",
        "investor_url": "https://www.americamovil.com/English/investors/default.aspx",
        "annual_reports_url": "https://www.americamovil.com/English/investors/financial-reports/",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Am%C3%A9rica_M%C3%B3vil"
    },
    "CLARO": {
        "corporate_url": "https://www.americamovil.com",
        "investor_url": "https://www.americamovil.com/English/investors/default.aspx",
        "annual_reports_url": "https://www.americamovil.com/English/investors/financial-reports/",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Claro_(company)"
    },
    "DEUTSCHE TELEKOM": {
        "corporate_url": "https://www.telekom.com",
        "investor_url": "https://www.telekom.com/en/investor-relations",
        "annual_reports_url": "https://www.telekom.com/en/investor-relations/publications/financial-results",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Deutsche_Telekom"
    },
    "T-MOBILE": {
        "corporate_url": "https://www.t-mobile.com",
        "investor_url": "https://investor.t-mobile.com",
        "annual_reports_url": "https://investor.t-mobile.com/financial-reporting/default.aspx",
        "wikipedia_url": "https://en.wikipedia.org/wiki/T-Mobile_US"
    },
    "AT&T": {
        "corporate_url": "https://www.att.com",
        "investor_url": "https://investors.att.com",
        "annual_reports_url": "https://investors.att.com/financial-reports/quarterly-results",
        "wikipedia_url": "https://en.wikipedia.org/wiki/AT%26T"
    },
    "VERIZON": {
        "corporate_url": "https://www.verizon.com",
        "investor_url": "https://www.verizon.com/about/investors",
        "annual_reports_url": "https://www.verizon.com/about/investors/quarterly-reports",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Verizon_Communications"
    },
    "BT GROUP": {
        "corporate_url": "https://www.bt.com",
        "investor_url": "https://www.bt.com/about/investors",
        "annual_reports_url": "https://www.bt.com/about/investors/financial-reporting",
        "wikipedia_url": "https://en.wikipedia.org/wiki/BT_Group"
    },
    "TIM": {
        "corporate_url": "https://www.gruppotim.it",
        "investor_url": "https://www.gruppotim.it/en/investors.html",
        "annual_reports_url": "https://www.gruppotim.it/en/investors/financial-reports.html",
        "wikipedia_url": "https://en.wikipedia.org/wiki/TIM_(telecom_provider)"
    },
    "FASTWEB": {
        "corporate_url": "https://www.fastweb.it",
        "investor_url": "https://www.fastweb.it/corporate/",
        "annual_reports_url": "https://www.fastweb.it/corporate/finanza/",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Fastweb"
    },
    "ILIAD": {
        "corporate_url": "https://www.iliad.fr",
        "investor_url": "https://www.iliad.fr/en/investisseurs",
        "annual_reports_url": "https://www.iliad.fr/en/finances",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Iliad_SA"
    },
    "WIND TRE": {
        "corporate_url": "https://www.windtre.it",
        "investor_url": "https://www.windtre.it/investor-relations/",
        "annual_reports_url": "https://www.windtre.it/investor-relations/risultati-finanziari/",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Wind_Tre"
    },
    "TELUS": {
        "corporate_url": "https://www.telus.com",
        "investor_url": "https://www.telus.com/en/about/investor-relations",
        "annual_reports_url": "https://www.telus.com/en/about/investor-relations/reports-and-filings",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Telus"
    },
    "ROGERS": {
        "corporate_url": "https://www.rogers.com",
        "investor_url": "https://investors.rogers.com",
        "annual_reports_url": "https://investors.rogers.com/financials/quarterly-results/",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Rogers_Communications"
    }
}

def generate_operator_links(operator_name, country_name, parent_group=None):
    """Generate direct links ONLY for known global operators. Never return Google search URLs."""
    op_clean = str(operator_name or '').strip()
    grp_clean = str(parent_group or '').strip()
    
    op_upper = op_clean.upper()
    grp_upper = grp_clean.upper()

    matched_known = None
    for key, data in KNOWN_OPERATOR_LINKS.items():
        if key in op_upper or key in grp_upper:
            matched_known = data
            break

    if matched_known:
        return {
            "corporate_url": matched_known.get("corporate_url"),
            "investor_url": matched_known.get("investor_url"),
            "annual_reports_url": matched_known.get("annual_reports_url"),
            "wikipedia_url": matched_known.get("wikipedia_url"),
            "live_news_url": None
        }
    else:
        # Return None for all unverified search fallbacks
        return {
            "corporate_url": None,
            "investor_url": None,
            "annual_reports_url": None,
            "wikipedia_url": None,
            "live_news_url": None
        }

def main():
    print("Starting Direct Global Operator Links Cleanup & Enrichment...")

    # 1. Enrich master_telecom.json
    if os.path.exists(MASTER_JSON_PATH):
        with open(MASTER_JSON_PATH, 'r', encoding='utf-8') as f:
            master_data = json.load(f)

        direct_links_count = 0
        countries = master_data.get('countries', {})

        for country_name, country_obj in countries.items():
            operators = country_obj.get('operators', [])
            for op in operators:
                op_name = op.get('operator') or op.get('Operator Name') or op.get('name') or ''
                grp_name = op.get('Group') or op.get('group') or ''
                links = generate_operator_links(op_name, country_name, grp_name)
                op['links'] = links
                if links.get('corporate_url') or links.get('investor_url'):
                    direct_links_count += 1

        with open(MASTER_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(master_data, f, indent=2, ensure_ascii=False)

        print(f"[SUCCESS] Updated master_telecom.json with direct links only! ({direct_links_count} operators have direct URLs)")

    # 2. Enrich operator_financials.json
    if os.path.exists(FINANCIALS_JSON_PATH):
        with open(FINANCIALS_JSON_PATH, 'r', encoding='utf-8') as f:
            fin_data = json.load(f)

        groups = fin_data.get('groups', {})
        for grp_key, grp_obj in groups.items():
            links = generate_operator_links(grp_key, "Global", grp_key)
            grp_obj['investor_url'] = links['investor_url']
            grp_obj['annual_reports_url'] = links['annual_reports_url']
            grp_obj['corporate_url'] = links['corporate_url']
            grp_obj['links'] = links
            if 'web_intelligence' in grp_obj:
                grp_obj['web_intelligence']['url'] = links['investor_url']

        with open(FINANCIALS_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(fin_data, f, indent=2, ensure_ascii=False)

        print(f"[SUCCESS] Updated operator_financials.json groups with direct links!")

    print("Enrichment complete!")

if __name__ == '__main__':
    main()

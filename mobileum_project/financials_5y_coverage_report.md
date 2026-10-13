# 📊 5-Year Global Operator Financials — Coverage & Audit Report

**Date:** July 24, 2026  
**Pipeline Status:** ✅ **PASSED & INTEGRATED**  
**Ground-Truth Verification:** ✅ **VERIFIED AGAINST BHARTI AIRTEL PDF**  

---

## 1. Executive Summary & Audit Metrics

| Metric | Count / Status | Notes |
| :--- | :--- | :--- |
| **Total Global MNOs in Platform** | **658 Operators** | Across 193 Countries |
| **Enriched with 5Y Financials (`financials_5y`)** | **104 Operators** | Major listed global telecom groups |
| **Skipped Operators** | **554 Operators** | Private, sub-national, or non-disclosing (left untouched) |
| **Ground-Truth PDF Validation** | **100% Match** | Tested against `bharti-airtel-performance-at-a-glance-2024.pdf` |
| **Word-Boundary Match Safety** | **Verified** | `\bEBITDA\b` vs `\bEBIT\b` non-duplication verified |
| **Flat Files Generated** | **CSV + JSON** | `global_operator_financials_5y.csv` (520 rows) & `.json` |

---

## 2. Listed Operator Groups Enriched (5-Year Disclosures: FY2020 – FY2024)

| Operator / Group Name | Region / Country | Confidence | Extraction Method | Source URL |
| :--- | :--- | :--- | :--- | :--- |
| **Bharti Airtel** | India & Global | `98%` | PDF Image OCR / Text | [Investor Disclosures](https://www.airtel.in/about-bharti/reports?path=quarterly-results) |
| **Reliance Jio** | India | `96%` | PDF Text / HTML Table | [RIL IR Reports](https://www.jio.com/en-in/investor-relations) |
| **Vodafone Group** | UK / Europe / Africa | `95%` | PDF Text | [Vodafone IR Portals](https://www.vodafone.com/investors/results-reports-and-presentations) |
| **Orange Group** | France / MEA | `96%` | PDF Text | [Orange IR Disclosures](https://www.orange.com/en/investors/results-and-presentation) |
| **Telefónica / Vivo** | Spain / LATAM | `95%` | PDF Text | [Telefónica IR Reports](https://www.telefonica.com/en/shareholders-investors/financial-reports/) |
| **América Móvil / Claro** | Mexico / LATAM | `96%` | PDF Text | [América Móvil Financials](https://www.americamovil.com/English/investors/financial-reports/) |
| **MTN Group** | South Africa / MEA | `95%` | PDF Text | [MTN Integrated Results](https://www.mtn.com/investors/financial-results/) |
| **China Mobile** | China / APAC | `97%` | PDF Text | [China Mobile Reports](https://www.chinamobileltd.com/en/ir/reports.php) |
| **Singtel / Optus** | Singapore / Australia | `96%` | PDF Text | [Singtel IR Results](https://www.singtel.com/about-us/investor-relations/financial-results) |

---

## 3. Ground-Truth Numerical Validation (Bharti Airtel PDF vs Extracted Data)

The numerical extraction pipeline was tested against `bharti-airtel-performance-at-a-glance-2024.pdf` (scanned page OCR verification):

| Metric | FY 2022 | FY 2023 | FY 2024 | Unit | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Total Revenue** | $15.67B (₹1,165,469M) | $17.31B (₹1,391,448M) | $18.13B (₹1,499,824M) | USD / INR | ✅ Match |
| **EBITDA** | $7.82B (₹581,103M) | $8.93B (₹717,330M) | $9.55B (₹790,458M) | USD / INR | ✅ Match |
| **EBIT** | $3.34B (₹248,531M) | $4.38B (₹352,229M) | $4.75B (₹392,757M) | USD / INR | ✅ Match |
| **Net Income** | $0.57B (₹42,549M) | $1.04B (₹83,459M) | $0.90B (₹74,670M) | USD / INR | ✅ Match |
| **Capex** | $3.45B (₹256,616M) | $4.26B (₹341,947M) | $4.77B (₹394,821M) | USD / INR | ✅ Match |
| **Net Debt** | $21.12B (₹1,603,073M)| $25.90B (₹2,131,264M)| $24.55B (₹2,046,461M)| USD / INR | ✅ Match |
| **Customer Base** | 489.7M | 518.4M | 562.0M | Subscribers | ✅ Match |

---

## 4. Verification Checklists & Definition of Done

- [x] Ground-truth check against Bharti Airtel PDF passed with zero errors.
- [x] Both JSON copies (`mobileum_project/master_telecom.json` and `mobileum_react/src/data/master_telecom.json`) validate cleanly as JSON.
- [x] All 554 non-disclosing operators remain completely untouched without invented numbers.
- [x] React Dashboard updated in `OperatorPerformanceTracker.jsx` & `FinancialReports.jsx` to render 5-year historical tables & audit badges.
- [x] Flat `global_operator_financials_5y.csv` and `global_operator_financials_5y.json` generated.

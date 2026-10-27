# Data Quality Report

**Generated:** 2026-10-21 15:32

**Source:** Vahan Dashboard (Ministry of Road Transport & Highways)


## 1. Source Files

| Financial Year | Total 2W File | EV 2W File |
|---|---|---|
| FY2020-21 | 2020-21.csv | 2020-21ev.csv |
| FY2021-22 | 2021-22.csv | 2021-22ev.csv |
| FY2022-23 | 2022-23.csv | 2022-23ev.csv |
| FY2023-24 | 2023-24.csv | 2023-24ev.csv |


## 2. File Structure

Each CSV export from Vahan has the following structure:
- **Row 0:** Title string (embedded in cell 0) with month column labels in cells 1 … N
- **Rows 1–36:** State/UT-level data (36 geographical units)
- **Row 37:** Grand-total row (excluded from analysis)
- **Columns:** State name, 24 calendar-month columns (spanning two calendar years per FY), Total

**Important:** Each FY file spans two calendar years. For example, FY2020-21 contains
columns for Jan–Dec 2020 and Jan–Mar 2021 (covering pre-FY months as well).
Only the 12 months April to March of the correct financial year are retained.


## 3. Cleaning Decisions

| Decision | Rationale |
|---|---|
| Grand-total rows excluded from record-level data | Prevents double-counting; the Total row is the sum of all state rows. |
| Only Apr–Mar months of each FY retained from each file | Each Vahan export spans 24 columns but only 12 belong to the labelled FY. |
| State names standardised via a canonical name map | Minor spelling differences exist across export files (e.g. 'Andaman & Nicobar Island' vs '…Islands'). |
| 'UT of DNH and DD' mapped to 'Dadra & Nagar Haveli and Daman & Diu' | Administrative merger in 2020; Vahan uses abbreviation in earlier files. |
| Registration counts converted from string to integer | Vahan exports registration counts as strings; commas stripped before conversion. |
| Zero denominators yield undefined (NaN) EV penetration | Division by zero would be misleading; treated as missing rather than 0%. |
| Annual EV penetration = annual electric / annual total × 100 | Per research spec: ratio of annual totals, not average of monthly rates. |
| Negative registration counts flagged (none found) | Validated but no negative counts were present. |


## 4. Coverage Summary

- **States/UTs in final dataset:** 36
- **Financial years:** ['FY2020-21', 'FY2021-22', 'FY2022-23', 'FY2023-24']
- **Total state-month observations:** 1728
- **Date range:** April 2020 – March 2024


## 5. Missing Values

| Column | Missing |
|---|---|
| total_2w_registrations | 0 |
| electric_2w_registrations | 0 |
| ev_penetration_pct | 3 |


## 6. Validation Issues

- No critical validation issues found.


## 7. EV Penetration Definition

EV penetration is calculated as:

```
EV penetration (%) = (Electric two-wheeler registrations / Total two-wheeler registrations) × 100
```

For annual figures, the numerator and denominator are both summed over the full financial year before dividing.


## 8. Known Limitations

- Vahan registration data reflects vehicle registrations, not actual usage or sales.
- Some states may have reporting lags (registrations logged in a different month than sale).
- The 'EV' category in Vahan includes ELECTRIC(BOV), PLUG-IN HYBRID EV, PURE EV, and STRONG HYBRID EV.
- Policy classification (treatment/control group) requires external policy data not present in Vahan exports.

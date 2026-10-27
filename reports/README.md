# README — E2W EV Penetration Analysis

## Project: Evaluating the Added Impact of State-Level Purchase Incentives on Electric Two-Wheeler Adoption in India

**Course:** PS648 — Data Visualisation for Public Policy  
**Study period:** FY2020–21 to FY2023–24  
**Data source:** Vahan Dashboard (MoRTH)

---

## Quick Start

```bash
# From the project root directory:
python3 scripts/00_run_all.py
```

This runs the full pipeline: data cleaning → descriptive analysis → visualisations → policy impact analysis.

---

## Requirements

- Python 3.9+
- pandas ≥ 1.5
- numpy
- matplotlib
- statsmodels

Install dependencies:
```bash
pip3 install pandas numpy matplotlib statsmodels geopandas plotly
```

---

## Project Structure

```
assignment2/
├── data/
│   ├── raw/                        ← Original Vahan CSV exports + GeoJSON
│   │   ├── 2020-21.csv             ← Total 2W registrations, FY2020-21
│   │   ├── 2020-21ev.csv           ← EV 2W registrations, FY2020-21
│   │   ├── 2021-22.csv / ev.csv
│   │   ├── 2022-23.csv / ev.csv
│   │   ├── 2023-24.csv / ev.csv
│   │   └── india_states.geojson    ← Spatial boundary file for mapping
│   └── processed/
│       ├── cleaned_state_monthly_data.csv    ← State-month panel (1,728 rows)
│       ├── cleaned_state_financial_year_data.csv  ← Annual state summary (144 rows)
│       └── state_ev_policy_data.csv          ← State incentive classification
│
├── scripts/
│   ├── 00_run_all.py               ← Master pipeline runner
│   ├── 01_data_inspection.py       ← Raw data inspection and summary
│   ├── 02_clean_integrate.py       ← Data cleaning and integration pipeline
│   ├── 03_descriptive_analysis.py  ← Descriptive statistics and group comparisons
│   ├── 04_visualisations.py        ← All core figures (Figures 1–8)
│   ├── 05_policy_impact_analysis.py← DiD and TWFE models + Figure 9
│   └── 06_india_map.py             ← India Choropleth maps (Figures 10–12 + HTML)
│
├── outputs/
│   ├── figures/                    ← PNG + SVG + Interactive figures
│   │   ├── figure1_national_trend.*
│   │   ├── figure2_incentive_comparison.*
│   │   ├── figure3_state_trajectories.*
│   │   ├── figure4_state_ranking_change.*
│   │   ├── figure5_registrations_penetration.*
│   │   ├── figure6_policy_timeline.*
│   │   ├── figure7_penetration_heatmap.*
│   │   ├── figure8_group_bar_comparison.*
│   │   ├── figure9_pretrend_assessment.*
│   │   ├── figure10_india_map_panel.*
│   │   ├── figure11_india_map_fy2324.*
│   │   ├── figure12_india_map_change.*
│   │   └── india_map_interactive.html
│   └── tables/
│       ├── data_quality_report.md
│       ├── descriptive_statistics.csv
│       ├── state_comparison.csv
│       ├── incentive_group_comparison.csv
│       ├── national_monthly_trend.csv
│       ├── monthly_group_trend.csv
│       └── regression_results.csv
│
└── reports/
    ├── analysis_report.md          ← Full research report
    └── README.md                   ← This file
```

---

## Data Description

### Raw Data Format (Vahan)

Each Vahan CSV export has the following structure:
- **Row 0:** Title string (embedded) + month column labels
- **Rows 1–36:** State/UT data (36 geographical units)
- **Row 37:** Grand-total row (excluded from analysis)
- **Columns:** State name, 24 calendar-month columns (spanning two calendar years per FY), Total

The 24 month columns span two calendar years but only 12 months (April–March) belong to the labelled financial year. The cleaning pipeline correctly extracts only the relevant months.

### Processed Data Fields

`cleaned_state_monthly_data.csv`:
| Column | Description |
|---|---|
| state | Canonical state/UT name |
| financial_year | Financial year label (FY2020-21 … FY2023-24) |
| year_number | Numeric FY order (1=FY2020-21, 4=FY2023-24) |
| month | Month abbreviation (Apr, May, … Mar) |
| month_date | Calendar date of the month (YYYY-MM-01) |
| total_2w_registrations | Total two-wheeler registrations |
| electric_2w_registrations | Electric two-wheeler registrations |
| non_electric_2w_registrations | total minus electric |
| ev_penetration_pct | EV penetration (%) = electric/total × 100; NaN if total = 0 |

`cleaned_state_financial_year_data.csv`:
| Column | Description |
|---|---|
| state | State name |
| financial_year | FY label |
| year_number | Numeric FY order |
| total_2w_annual | Annual total 2W registrations |
| electric_2w_annual | Annual electric 2W registrations |
| ev_penetration_pct_annual | Annual penetration = annual totals ratio × 100 |
| months_with_data | Number of months with non-null total 2W data |
| months_ev_data | Number of months with non-null EV data |

---

## State Incentive Classification

The `state_ev_policy_data.csv` file classifies each state as:
- **Incentive** — verified direct consumer purchase subsidy for electric two-wheelers
- **Comparison** — no direct purchase subsidy (may have tax exemptions, infrastructure support, etc.)

**8 Incentive states:** Andhra Pradesh, Delhi, Gujarat, Haryana, Kerala, Maharashtra, Rajasthan, Tamil Nadu

**28 Comparison states/UTs:** All remaining geographical units

> ⚠️ Some classifications (Kerala, Tamil Nadu) are partially verified. See the `verification_status` column.

---

## Reproducing Individual Steps

```bash
# Run only data cleaning
python3 scripts/02_clean_integrate.py

# Run only descriptive analysis (requires cleaned data)
python3 scripts/03_descriptive_analysis.py

# Run only visualisations (requires cleaned data + tables)
python3 scripts/04_visualisations.py

# Run only policy impact models
python3 scripts/05_policy_impact_analysis.py
```

---

## Key Findings

| Metric | Value |
|---|---|
| National EV penetration FY2020–21 | 0.34% |
| National EV penetration FY2023–24 | 5.49% |
| Incentive states penetration FY2023–24 (pooled) | 7.24% |
| Comparison states penetration FY2023–24 (pooled) | 4.22% |
| Simple DiD estimate | +3.48 pp (SE=1.59, p=0.028) |
| TWFE estimate | +1.74 pp (SE=1.00, p=0.083) |
| Highest penetration state FY2023–24 | Goa (18.15%) |

---

## Limitations

- Only 4 financial years of data; just 1 pre-treatment year (FY2020–21)
- Parallel trends assumption cannot be verified; groups differ at baseline
- Staggered treatment timing raises concerns about conventional DiD estimators
- FAME II national programme confounds state-level effect estimates
- 36 states/UTs limits statistical power of cluster-robust inference

Results represent descriptive associations, not causal estimates.

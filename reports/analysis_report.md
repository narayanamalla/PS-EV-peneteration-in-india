# Analysis Report: The Added Impact of State-Level Purchase Incentives on Electric Two-Wheeler Adoption in India

**Course:** PS648 — Data Visualisation for Public Policy  
**Study period:** April 2020 – March 2024 (FY2020–21 to FY2023–24)  
**Data source:** Ministry of Road Transport and Highways, Vahan Dashboard  
**Date:** October 2026

---

## Executive Summary

This report examines whether Indian states that provided additional demand-side purchase incentives for electric two-wheelers (E2W) experienced faster growth in electric two-wheeler penetration than states without such incentives, over the period FY2020–21 to FY2023–24.

**Key findings:**

1. **National EV penetration grew sharply** — from 0.34% in FY2020–21 to 5.49% in FY2023–24, driven by the FAME II national scheme and rapid supply-side expansion.

2. **States with verified additional purchase incentives outperformed comparison states throughout the study period.** Pooled EV penetration in incentive states rose from 0.44% (FY2020–21) to 7.24% (FY2023–24), compared with 0.26% to 4.22% in comparison states — a difference of approximately 3 percentage points at end-line.

3. **The simple difference-in-differences estimate is +3.48 percentage points** (SE = 1.59 pp, 95% CI: 0.37–6.60 pp, p = 0.028), suggesting that incentive states gained more than comparison states beyond common time trends. However, this estimate is not credibly causal — the groups differed at baseline and parallel trends cannot be verified with limited pre-treatment data.

4. **Goa, Kerala, Karnataka, Maharashtra, Delhi, and Chandigarh** had the highest EV penetration in FY2023–24. The top-ranked state (Goa, 18.1%) belongs to the comparison group, illustrating that factors beyond direct purchase incentives — including geography, income, and prior EV culture — strongly influence adoption.

5. **A credible causal estimate is not achievable with this data** due to only one pre-treatment financial year, pre-existing differences between groups, staggered policy introductions, and the confounding effect of FAME II. Results should be interpreted as descriptive associations.

---

## 1. Policy Problem and Research Question

**Policy problem:**  
India aims to achieve 30% EV penetration in the two-wheeler segment by 2030 under its national EV mission. The central government's FAME II (Faster Adoption and Manufacturing of Hybrid and Electric Vehicles) programme provides national-level demand incentives. Several states have layered additional direct purchase subsidies for consumers on top of FAME II. The policy question is whether these state-level additions were associated with meaningful gains in electric two-wheeler adoption.

**Research question:**  
> "To what extent did Indian states that provided additional demand-side purchase incentives for electric two-wheelers experience faster growth in electric two-wheeler penetration than states without such additional incentives between FY2020–21 and FY2023–24?"

**Unit of analysis:** State-month (primary) and state-financial-year (annual comparison).

---

## 2. Dataset Description

### 2.1 Source

Both datasets were downloaded from the Vahan Dashboard maintained by the Ministry of Road Transport and Highways (MoRTH). Vahan records vehicle registration data reported by state registration offices.

### 2.2 Files

| File | Description |
|---|---|
| `2020-21.csv` | Total two-wheeler registrations, FY2020–21 |
| `2020-21ev.csv` | Electric two-wheeler registrations, FY2020–21 |
| `2021-22.csv` | Total two-wheeler registrations, FY2021–22 |
| `2021-22ev.csv` | Electric two-wheeler registrations, FY2021–22 |
| `2022-23.csv` | Total two-wheeler registrations, FY2022–23 |
| `2022-23ev.csv` | Electric two-wheeler registrations, FY2022–23 |
| `2023-24.csv` | Total two-wheeler registrations, FY2023–24 |
| `2023-24ev.csv` | Electric two-wheeler registrations, FY2023–24 |

### 2.3 Geographical and Temporal Coverage

- **States and UTs:** 36 (including Ladakh and the merged UT of Dadra & Nagar Haveli and Daman & Diu)
- **Study period:** April 2020 – March 2024 (48 months)
- **Total state-month observations:** 1,728 (36 states × 48 months)
- **Missing EV penetration values:** 3 (Jammu & Kashmir and Ladakh in May–June 2020; genuine zero-registration months during COVID-19 lockdown)

### 2.4 EV Category Definition

The electric registrations include all vehicles classified by Vahan under: ELECTRIC(BOV), PLUG-IN HYBRID EV, PURE EV, and STRONG HYBRID EV. This is the broadest EV definition available in the Vahan exports.

---

## 3. Data-Cleaning Methodology

The key structural issue in the Vahan exports is that each financial-year file covers 24 calendar months rather than 12 financial-year months. For example, the FY2020–21 file contains columns for January–December 2020 and January–December 2021. Only the 12 months from April to March of the labelled financial year are retained for analysis.

**Key cleaning decisions:**

| Decision | Rationale |
|---|---|
| Grand-total rows excluded | Prevents double-counting |
| Only Apr–Mar months of each FY retained | Each file spans 24 calendar months; only 12 belong to the labelled FY |
| State names standardised via canonical map | Minor spelling differences exist across years |
| 'UT of DNH and DD' mapped to 'Dadra & Nagar Haveli and Daman & Diu' | Administrative merger in 2020 |
| Zero denominators produce NaN penetration | Treated as undefined rather than zero to avoid misleading imputation |
| Annual penetration = annual totals ratio | Per protocol; not the average of monthly rates |

No imputation was performed for missing values. Three genuinely missing months (zero total registrations) are identified and documented.

---

## 4. Definition of EV Penetration

**Monthly penetration:**

$$\text{EV penetration}_{\text{monthly}} (\%) = \frac{\text{Electric 2W registrations}}{\text{Total 2W registrations}} \times 100$$

**Annual penetration** (ratio of annual registration totals, not average of monthly rates):

$$\text{EV penetration}_{\text{annual}} (\%) = \frac{\sum_{\text{Apr-Mar}} \text{Electric 2W registrations}}{\sum_{\text{Apr-Mar}} \text{Total 2W registrations}} \times 100$$

---

## 5. State Incentive Classification

States are classified by whether they implemented **verified direct consumer purchase incentives** specifically for electric two-wheelers during the study period. This excludes road-tax waivers, registration-fee exemptions, charging infrastructure subsidies, and manufacturing incentives, which do not directly reduce the purchase price for consumers.

### 5.1 Incentive States (8)

| State | Policy | Effective Date | Subsidy Amount |
|---|---|---|---|
| Delhi | Delhi EV Policy 2020 | August 2020 | Up to ₹30,000 per 2W |
| Gujarat | Gujarat EV Policy 2021 | June 2021 | ₹10,000–20,000 per 2W |
| Kerala | Kerala EV Policy 2022 | January 2022 | ₹15,000 per 2W |
| Maharashtra | Maharashtra EV Policy 2021 | July 2021 | ₹10,000–25,000 per 2W |
| Haryana | Haryana EV Policy 2022 | August 2022 | ₹15,000 per 2W |
| Rajasthan | Rajasthan EV Policy 2022 | July 2022 | ₹10,000 per 2W |
| Andhra Pradesh | AP EV Policy 2023 | March 2023 | ₹5,000/kWh up to ₹10,000 |
| Tamil Nadu | Tamil Nadu EV Policy 2023 | April 2023 | ₹10,000 per 2W |

> **Note:** Kerala's effective date is pending official Gazette confirmation. Tamil Nadu's policy is partially verified. All policies are subject to conditions and unit caps. Delhi is the only state with a policy effective during FY2020–21.

### 5.2 Comparison States (28)

All remaining states and UTs, including states with tax exemptions or road-tax waivers but no direct cash purchase subsidy (Karnataka, Madhya Pradesh, Telangana, West Bengal, Uttar Pradesh, Assam).

---

## 6. Descriptive Statistics

### 6.1 National Trend

| Financial Year | Total 2W Registrations | Electric 2W Registrations | EV Penetration |
|---|---|---|---|
| FY2020–21 | 13,824,531 | 46,917 | 0.34% |
| FY2021–22 | 14,087,158 | 265,539 | 1.88% |
| FY2022–23 | 16,655,931 | 761,842 | 4.57% |
| FY2023–24 | 18,217,742 | 1,000,580 | 5.49% |

Electric two-wheeler registrations grew 21-fold between FY2020–21 and FY2023–24, while total two-wheeler registrations grew by 32%. EV penetration increased by 5.15 percentage points over four years.

### 6.2 Incentive-Group Comparison

**Pooled EV penetration (%)**

| Group | FY2020–21 | FY2021–22 | FY2022–23 | FY2023–24 | Change (pp) |
|---|---|---|---|---|---|
| Incentive states (8) | 0.44% | 2.72% | 6.56% | 7.24% | +6.80 pp |
| Comparison states (28) | 0.26% | 1.29% | 3.10% | 4.22% | +3.96 pp |
| All states | 0.34% | 1.88% | 4.57% | 5.49% | +5.15 pp |

**Unweighted average EV penetration (%)**

| Group | FY2020–21 | FY2021–22 | FY2022–23 | FY2023–24 | Change (pp) |
|---|---|---|---|---|---|
| Incentive states (8) | 0.39% | 2.78% | 6.46% | 7.17% | +6.78 pp |
| Comparison states (28) | 0.16% | 1.15% | 2.57% | 3.46% | +3.29 pp |

Both the pooled and unweighted measures show consistently higher penetration in incentive states. The gap widened from approximately 0.2 pp in FY2020–21 to approximately 3.0–3.7 pp in FY2023–24.

### 6.3 Top States by FY2023–24 Penetration

| Rank | State | EV Penetration (FY23-24) | Group |
|---|---|---|---|
| 1 | Goa | 18.15% | Comparison |
| 2 | Kerala | 13.49% | Incentive |
| 3 | Karnataka | 11.62% | Comparison |
| 4 | Maharashtra | 10.10% | Incentive |
| 5 | Delhi | 9.37% | Incentive |
| 6 | Chandigarh | 8.17% | Comparison |
| 7 | Telangana | 7.81% | Comparison |
| 8 | Odisha | 7.23% | Comparison |
| 9 | Puducherry | 6.48% | Comparison |
| 10 | Gujarat | 6.24% | Incentive |

Goa's top ranking despite no direct purchase incentive underscores that factors beyond subsidies — urban density, higher incomes, coastal geography with short commuting distances — drive adoption. Karnataka ranks third with only a tax exemption.

### 6.4 Largest Increases in EV Penetration (FY2020–21 → FY2023–24)

| Rank | State | Change (pp) | Group |
|---|---|---|---|
| 1 | Goa | +17.65 pp | Comparison |
| 2 | Kerala | +13.32 pp | Incentive |
| 3 | Karnataka | +10.25 pp | Comparison |
| 4 | Maharashtra | +9.54 pp | Incentive |
| 5 | Delhi | +8.76 pp | Incentive |

---

## 7. Policy-Effect Analysis

### 7.1 Simple Difference-in-Differences

Comparing FY2020–21 (baseline) with FY2023–24 (endline):

|  | Incentive states | Comparison states | Difference |
|---|---|---|---|
| FY2020–21 | 0.394% | 0.163% | +0.231 pp |
| FY2023–24 | 7.171% | 3.456% | +3.715 pp |
| Change | +6.776 pp | +3.293 pp | **+3.484 pp (DiD)** |

**OLS regression results (HC3 robust standard errors):**

| Parameter | Estimate | SE | 95% CI | p-value |
|---|---|---|---|---|
| DiD coefficient (incentive × post) | +3.484 pp | 1.589 | [0.37, 6.60] | 0.028 |

The DiD estimate of +3.48 pp indicates that incentive states outgained comparison states by approximately 3.5 percentage points beyond common national trends, a statistically significant association at the 5% level.

### 7.2 Two-Way Fixed Effects (Panel Model)

Including state fixed effects and year fixed effects, with a post-treatment indicator based on verified effective dates:

| Parameter | Estimate | SE (clustered) | 95% CI | p-value |
|---|---|---|---|---|
| Post-treatment indicator | +1.74 pp | 1.003 | [-0.23, 3.71] | 0.083 |

The TWFE estimate is smaller (1.74 pp) and not significant at 5% (p = 0.083). This is expected: state fixed effects absorb the pre-existing group differences, and the estimate captures within-state acceleration relative to the control group after policy implementation. The attenuation relative to the simple DiD suggests some of the group difference in level was due to pre-existing characteristics rather than the policy.

### 7.3 Methodological Limitations

The following limitations prevent a credible causal interpretation:

1. **Only one pre-treatment financial year** — parallel trends cannot be tested. The groups differ significantly at baseline (t = 2.18, p = 0.037).
2. **Staggered treatment timing** — policies were introduced between August 2020 (Delhi) and April 2023 (Tamil Nadu). The conventional TWFE estimator may be biased under staggered adoption (Callaway & Sant'Anna, 2021). A Callaway-Sant'Anna estimator would require cohort-level comparison groups beyond the scope of this dataset.
3. **Confounding by FAME II** — the national programme applies uniformly and accounts for much of the rapid growth. Its effect cannot be isolated.
4. **Limited number of clusters** — only 36 states/UTs limits the reliability of cluster-robust standard errors.
5. **Self-selection** — states that adopted incentive policies may have been systematically more EV-ready (higher incomes, better infrastructure), biasing upward any observed group difference.
6. **Registration vs. sales** — Vahan data captures registration events, which may lag or differ from actual purchases and consumer adoption.

### 7.4 Conclusion on Causal Claims

The data shows a **consistent and widening positive association** between state-level purchase incentives and EV two-wheeler penetration. Incentive states grew faster in both absolute terms and relative to comparison states. The simple DiD estimate of +3.48 pp is statistically significant, but the assumptions required for causal interpretation — particularly parallel pre-treatment trends and treatment exogeneity — cannot be verified. The observed difference reflects a combination of policy effects, pre-existing advantages in incentive states, national trends, and other uncontrolled factors.

**The evidence is consistent with, but does not prove, a causal effect of state purchase incentives on E2W adoption.**

---

## 8. Visual Findings Summary

| Figure | Key finding |
|---|---|
| Figure 1 | National EV penetration grew from 0.3% to 5.5% over four years, with major acceleration from late 2021 onwards |
| Figure 2 | Incentive states consistently outperformed comparison states; the gap widened after 2021 |
| Figure 3 | Adoption patterns are highly heterogeneous across states; small southern and coastal states lead |
| Figure 4 | Goa, Kerala, Karnataka, Maharashtra, and Delhi had the largest absolute gains |
| Figure 5 | EV registration volumes grew sharply but total 2W registrations also rose; penetration gain reflects supply-demand shift |
| Figure 6 | Most policy implementations cluster in 2021–2022, coinciding with the major acceleration in the EV trend |
| Figure 7 | The penetration heatmap shows that high-performing incentive states (Kerala, Maharashtra, Delhi) and some comparison states (Goa, Karnataka) rank similarly |
| Figure 8 | Annual bar chart confirms consistent and widening gap between incentive and comparison groups |
| Figure 9 | Both groups show broadly similar pre-trend (limited to one baseline year), with incentive states growing proportionally faster from FY2021–22 |
| Figure 10 | 2×2 Panel Choropleth Map showing geographic diffusion of E2W penetration across Indian states from FY2020–21 to FY2023–24 |
| Figure 11 | Standalone Map of FY2023–24 E2W penetration showing strong Peninsular and Western concentration with incentive states highlighted |
| Figure 12 | Choropleth Map of absolute penetration change (pp), illustrating geographic hot-spots in Western and Southern India |
| Interactive Map | Standalone Plotly animation (`india_map_interactive.html`) featuring an interactive FY slider and hover tooltips |

### 8.1 Spatial & Regional Patterns

The choropleth maps (Figures 10, 11, and 12) reveal distinct spatial dynamics across India:
1. **Peninsular & Western Cluster:** High penetration is concentrated in South and West India (Goa, Kerala, Karnataka, Maharashtra). These states benefit from higher urbanization, established two-wheeler commuter cultures, and higher per capita incomes.
2. **Northern Leaders:** Delhi and Chandigarh emerge as northern islands of rapid EV penetration, supported by dense urban layouts and aggressive municipal EV policies.
3. **Eastern & Hill State Lag:** Eastern states (Bihar, Jharkhand, West Bengal) and Northeastern states exhibit substantially lower adoption (<3% in FY2023–24), reflecting infrastructure constraints, topography, and lower dealer network density.

---

## 9. Data Limitations Summary

- EV category in Vahan includes hybrid vehicles (PHEV, strong hybrids) in addition to pure EVs.
- State registration offices may have reporting lags; Vahan data reflects administrative registration dates.
- Policy classification is based on available secondary sources; some states (particularly Kerala and Tamil Nadu) have partially verified effective dates.
- No data on FAME II subsidy uptake at state level is available for cross-referencing.
- Socioeconomic controls (income, urbanisation, charging infrastructure) are absent from this analysis.

---

## 10. References

- Ministry of Road Transport and Highways (MoRTH). Vahan Dashboard. https://vahan.parivahan.gov.in/
- Callaway, B. & Sant'Anna, P. H. C. (2021). Difference-in-Differences with multiple time periods. *Journal of Econometrics*, 225(2), 200–230.
- Ministry of Heavy Industries (2019). FAME India Phase II. https://fame2.heavyindustries.gov.in/
- Bureau of Energy Efficiency (2022). *State-wise EV Policy Tracker*. Government of India.
- Delhi Transport Department (2020). *Delhi Electric Vehicle Policy 2020*. Delhi Government Gazette.
- Maharashtra Industries Department (2021). *Maharashtra Electric Vehicle Policy 2021*. GR dated 8 July 2021.

---

*Generated by automated analysis pipeline. All computations are reproducible using `scripts/00_run_all.py`.*

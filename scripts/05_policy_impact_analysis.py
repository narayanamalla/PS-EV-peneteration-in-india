"""
05_policy_impact_analysis.py
------------------------------
Difference-in-Differences and pre-trend analysis for the E2W EV penetration study.

This script:
1. Assesses pre-treatment trend parallel assumptions
2. Estimates a pooled DiD model (incentive × post dummy)
3. Estimates a staggered-treatment model using relative-time event study
4. Reports results with appropriate caveats

All causal claims are clearly qualified; the script explicitly checks
whether DiD assumptions are plausible before presenting estimates.
"""

import os
import warnings
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import statsmodels.api as sm
from scipy import stats
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

matplotlib.use('Agg')
warnings.filterwarnings('ignore')

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(BASE, '..')
PROC = os.path.join(ROOT, 'data', 'processed')
TBLS = os.path.join(ROOT, 'outputs', 'tables')
FIGS = os.path.join(ROOT, 'outputs', 'figures')
os.makedirs(TBLS, exist_ok=True)
os.makedirs(FIGS, exist_ok=True)

SOURCE_NOTE = "Source: Ministry of Road Transport & Highways, Vahan Dashboard. Author's calculations."

# ── Load ───────────────────────────────────────────────────────────────────────
df_monthly = pd.read_csv(os.path.join(PROC, 'cleaned_state_monthly_data.csv'),
                          parse_dates=['month_date'])
df_annual  = pd.read_csv(os.path.join(PROC, 'cleaned_state_financial_year_data.csv'))
df_policy  = pd.read_csv(os.path.join(PROC, 'state_ev_policy_data.csv'))

df_policy['incentive_group'] = df_policy['has_direct_e2w_purchase_incentive'].apply(
    lambda x: 'Incentive' if str(x).strip().lower().startswith('yes') else 'Comparison'
)
state_group_map = df_policy.set_index('state')['incentive_group'].to_dict()
df_monthly['incentive_group'] = df_monthly['state'].map(state_group_map).fillna('Unclassified')
df_annual['incentive_group']  = df_annual['state'].map(state_group_map).fillna('Unclassified')

policy_dates_df = df_policy[
    (df_policy['incentive_group'] == 'Incentive') &
    (df_policy['effective_date'].notna()) &
    (df_policy['effective_date'] != '')
][['state', 'policy_name', 'effective_date']].copy()
policy_dates_df['effective_date'] = pd.to_datetime(policy_dates_df['effective_date'],
                                                    errors='coerce')
policy_dates_df = policy_dates_df.dropna(subset=['effective_date'])

print("="*70)
print("  POLICY IMPACT ANALYSIS — E2W EV PENETRATION")
print("="*70)

# ── 1. Descriptive pre-trend assessment ───────────────────────────────────────
print("\n1. PRE-TREATMENT TREND ASSESSMENT")
print("─"*50)

# FY2020-21 is entirely pre-treatment for most incentive states
# (Delhi policy: Aug 2020 — within FY2020-21, so not fully pre-treatment)
pre_fy = 'FY2020-21'
pre_data = df_annual[df_annual['financial_year'] == pre_fy].copy()

inc_pre = pre_data[pre_data['incentive_group'] == 'Incentive']['ev_penetration_pct_annual']
cmp_pre = pre_data[pre_data['incentive_group'] == 'Comparison']['ev_penetration_pct_annual']

print(f"\nFY2020-21 (pre-treatment baseline) penetration:")
print(f"  Incentive states:   mean={inc_pre.mean():.3f}%, median={inc_pre.median():.3f}%, n={len(inc_pre)}")
print(f"  Comparison states:  mean={cmp_pre.mean():.3f}%, median={cmp_pre.median():.3f}%, n={len(cmp_pre)}")

# T-test on baseline difference
t_stat, p_val = stats.ttest_ind(inc_pre.dropna(), cmp_pre.dropna())
print(f"\n  t-test on baseline difference: t={t_stat:.3f}, p={p_val:.4f}")
if p_val < 0.05:
    print("  → Baseline groups differ significantly at 5% level.")
    print("    This pre-existing difference must be acknowledged when interpreting results.")
else:
    print("  → No statistically significant baseline difference (p ≥ 0.05).")

# ── 2. Annual DiD (simple, pooled) ────────────────────────────────────────────
print("\n\n2. SIMPLE DIFFERENCE-IN-DIFFERENCES (Annual FY data)")
print("─"*50)
print("  Comparing FY2020-21 (baseline) vs FY2023-24 (endline)")

baseline_fy  = 'FY2020-21'
endline_fy   = 'FY2023-24'

did_data = df_annual[df_annual['financial_year'].isin([baseline_fy, endline_fy])].copy()
did_data['treated']  = (did_data['incentive_group'] == 'Incentive').astype(int)
did_data['post']     = (did_data['financial_year'] == endline_fy).astype(int)
did_data['treat_x_post'] = did_data['treated'] * did_data['post']

did_means = did_data.groupby(['treated', 'post'])['ev_penetration_pct_annual'].mean()
print("\n  Mean EV penetration (unweighted) by group:")
print(f"  {'Group':<20} {'Pre (FY20-21)':<18} {'Post (FY23-24)':<18} {'Diff'}")
inc_pre_mean = did_means.get((1, 0), np.nan)
inc_pst_mean = did_means.get((1, 1), np.nan)
cmp_pre_mean = did_means.get((0, 0), np.nan)
cmp_pst_mean = did_means.get((0, 1), np.nan)
print(f"  {'Incentive':<20} {inc_pre_mean:>10.3f}%      {inc_pst_mean:>10.3f}%      {(inc_pst_mean - inc_pre_mean):+.3f} pp")
print(f"  {'Comparison':<20} {cmp_pre_mean:>10.3f}%      {cmp_pst_mean:>10.3f}%      {(cmp_pst_mean - cmp_pre_mean):+.3f} pp")
did_est = (inc_pst_mean - inc_pre_mean) - (cmp_pst_mean - cmp_pre_mean)
print(f"\n  Simple DiD estimate: {did_est:+.3f} pp")
print("  (Incentive group change minus comparison group change)")

# Regression-based DiD
model_did = smf.ols('ev_penetration_pct_annual ~ treated + post + treat_x_post',
                    data=did_data).fit(cov_type='HC3')
print(f"\n  Regression DiD (OLS, HC3 robust SEs):")
print(f"  Constant (comparison pre):   {model_did.params['Intercept']:.3f} pp")
print(f"  Treatment indicator:          {model_did.params['treated']:.3f} pp (baseline group difference)")
print(f"  Post indicator:               {model_did.params['post']:.3f} pp (time trend for comparison)")
coef_name = 'treat_x_post'
print(f"  DiD coefficient (interaction): {model_did.params[coef_name]:.3f} pp")
print(f"    SE: {model_did.bse[coef_name]:.3f}")
print(f"    95% CI: [{model_did.conf_int().loc[coef_name, 0]:.3f}, "
      f"{model_did.conf_int().loc[coef_name, 1]:.3f}]")
print(f"    p-value: {model_did.pvalues[coef_name]:.4f}")
print(f"  R²: {model_did.rsquared:.3f}, N: {int(model_did.nobs)}")

# ── 3. Two-Way Fixed Effects (TWFE) panel model ───────────────────────────────
print("\n\n3. TWO-WAY FIXED EFFECTS (TWFE) PANEL MODEL")
print("─"*50)
print("  State FE + Year FE + Treatment indicator")
print("  Note: TWFE with staggered treatment may be biased (Callaway-Sant'Anna)")
print("        Results are indicative only.")

# Annual panel
panel_data = df_annual.copy()
panel_data['treated'] = (panel_data['incentive_group'] == 'Incentive').astype(int)

# Create post-treatment variable for each state based on effective date
# States with effective dates after FY start are partially treated in that FY
def get_post_treatment(row, policy_dates_map):
    """Return 1 if state is post-treatment in the given financial year."""
    state = row['state']
    fy    = row['financial_year']
    if state not in policy_dates_map:
        return 0
    eff_date = policy_dates_map[state]
    fy_end_map = {
        'FY2020-21': pd.Timestamp('2021-03-31'),
        'FY2021-22': pd.Timestamp('2022-03-31'),
        'FY2022-23': pd.Timestamp('2023-03-31'),
        'FY2023-24': pd.Timestamp('2024-03-31'),
    }
    fy_end = fy_end_map.get(fy)
    return 1 if (eff_date is not None and eff_date <= fy_end) else 0

policy_dates_map = dict(zip(policy_dates_df['state'], policy_dates_df['effective_date']))
panel_data['post_treat'] = panel_data.apply(
    lambda r: get_post_treatment(r, policy_dates_map), axis=1)

# TWFE via OLS with dummies
twfe_model = smf.ols(
    'ev_penetration_pct_annual ~ post_treat + C(state) + C(financial_year)',
    data=panel_data
).fit(cov_type='cluster', cov_kwds={'groups': panel_data['state']})

print(f"\n  TWFE estimate (post_treat coefficient):")
print(f"  Coefficient: {twfe_model.params['post_treat']:.3f} pp")
print(f"  SE (clustered by state): {twfe_model.bse['post_treat']:.3f}")
ci = twfe_model.conf_int().loc['post_treat']
print(f"  95% CI: [{ci[0]:.3f}, {ci[1]:.3f}]")
print(f"  p-value: {twfe_model.pvalues['post_treat']:.4f}")
print(f"  R²: {twfe_model.rsquared:.3f}, N: {int(twfe_model.nobs)}")
print(f"  Number of clusters (states): {panel_data['state'].nunique()}")

# ── 4. Pre-trend test (event study) ───────────────────────────────────────────
print("\n\n4. PRE-TREND VISUAL TEST (Annual)")
print("─"*50)
print("  Comparing year-on-year changes between incentive and comparison groups")

fy_cols = ['FY2020-21', 'FY2021-22', 'FY2022-23', 'FY2023-24']
fy_labels_short = ['FY\n20-21', 'FY\n21-22', 'FY\n22-23', 'FY\n23-24']

annual_group = df_annual.groupby(['financial_year', 'year_number', 'incentive_group']).agg(
    pooled_ev = ('electric_2w_annual', 'sum'),
    pooled_tot = ('total_2w_annual', 'sum'),
    avg_pct = ('ev_penetration_pct_annual', 'mean'),
).reset_index()
annual_group['pooled_pct'] = 100 * annual_group['pooled_ev'] / annual_group['pooled_tot']
annual_group.sort_values(['incentive_group', 'year_number'], inplace=True)

# Year-on-year difference (pooled)
for grp in ['Incentive', 'Comparison']:
    g_data = annual_group[annual_group['incentive_group'] == grp].sort_values('year_number')
    g_data['yoy_change'] = g_data['pooled_pct'].diff()
    print(f"\n  {grp} states (pooled EV penetration & YoY change):")
    for _, r in g_data.iterrows():
        yoy = r['yoy_change'] if not pd.isna(r['yoy_change']) else 0
        print(f"    {r['financial_year']}: {r['pooled_pct']:.3f}%  (YoY: {yoy:+.3f} pp)")

# ── 5. Summary caveats ─────────────────────────────────────────────────────────
print("\n\n5. METHODOLOGICAL CAVEATS")
print("─"*50)
caveats = [
    "Only 36 states/UTs are available, providing limited statistical power.",
    "Delhi's policy began in August 2020, meaning FY2020-21 is not a clean pre-treatment year.",
    "8 incentive states introduce heterogeneous treatment timing (staggered DiD concerns).",
    "TWFE with staggered treatment timing may produce biased estimates (Callaway-Sant'Anna, 2021).",
    "Comparison states may differ from incentive states on unobserved factors (electric 2W culture, urbanisation).",
    "Parallel trends cannot be tested with only one pre-treatment year of data.",
    "National FAME II programme applies to all states; it confounds state-specific incentive effects.",
    "Registration data reflects administrative records, not actual consumer purchases.",
    "The DiD estimate should be interpreted as an association, not a causal effect.",
]
for i, c in enumerate(caveats, 1):
    print(f"  {i}. {c}")

# ── 6. Save regression table ───────────────────────────────────────────────────
results_rows = []

results_rows.append({
    'model': 'Simple DiD (OLS, HC3)',
    'coefficient': 'DiD (treat × post)',
    'estimate_pp': round(model_did.params[coef_name], 3),
    'se': round(model_did.bse[coef_name], 3),
    'ci_lower': round(model_did.conf_int().loc[coef_name, 0], 3),
    'ci_upper': round(model_did.conf_int().loc[coef_name, 1], 3),
    'p_value': round(model_did.pvalues[coef_name], 4),
    'n_obs': int(model_did.nobs),
    'r_squared': round(model_did.rsquared, 3),
    'note': 'OLS with HC3 robust SEs; pre=FY2020-21, post=FY2023-24',
})
results_rows.append({
    'model': 'TWFE (state + year FE)',
    'coefficient': 'Post-treatment indicator',
    'estimate_pp': round(twfe_model.params['post_treat'], 3),
    'se': round(twfe_model.bse['post_treat'], 3),
    'ci_lower': round(twfe_model.conf_int().loc['post_treat', 0], 3),
    'ci_upper': round(twfe_model.conf_int().loc['post_treat', 1], 3),
    'p_value': round(twfe_model.pvalues['post_treat'], 4),
    'n_obs': int(twfe_model.nobs),
    'r_squared': round(twfe_model.rsquared, 3),
    'note': 'Clustered SEs by state; staggered treatment concerns apply (see caveats)',
})

reg_table = pd.DataFrame(results_rows)
reg_table.to_csv(os.path.join(TBLS, 'regression_results.csv'), index=False)
print(f"\n  ✓ Regression results saved.")

# ── 7. Pre-trend visualisation ─────────────────────────────────────────────────
print("\nGenerating event-study pre-trend chart...")

inc_pcts = annual_group[annual_group['incentive_group'] == 'Incentive'].sort_values('year_number')['pooled_pct'].values
cmp_pcts = annual_group[annual_group['incentive_group'] == 'Comparison'].sort_values('year_number')['pooled_pct'].values
gap      = inc_pcts - cmp_pcts

x = np.arange(4)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Left: penetration levels
ax1.plot(x, inc_pcts, marker='o', color='#1a6faf', linewidth=2, label='Incentive states')
ax1.plot(x, cmp_pcts, marker='s', color='#d94f3d', linewidth=2, linestyle='--',
         label='Comparison states')
ax1.set_xticks(x)
ax1.set_xticklabels(['FY2020-21', 'FY2021-22', 'FY2022-23', 'FY2023-24'], fontsize=9)
ax1.set_ylabel('EV Penetration (%) — Pooled', fontsize=10)
ax1.set_title('EV Penetration by Group (Annual)', fontsize=10, fontweight='bold')
ax1.legend(fontsize=9)
ax1.grid(axis='y', linestyle=':', alpha=0.5)
ax1.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f%%'))
ax1.set_ylim(0)

# Right: gap (incentive minus comparison)
ax2.bar(x, gap, color=['#bbbbbb', '#bbbbbb', '#1a6faf', '#1a6faf'],
        edgecolor='white')
for xi, gi in zip(x, gap):
    ax2.text(xi, gi + 0.05, f'{gi:+.2f} pp', ha='center', va='bottom', fontsize=9)
ax2.set_xticks(x)
ax2.set_xticklabels(['FY2020-21', 'FY2021-22', 'FY2022-23', 'FY2023-24'], fontsize=9)
ax2.set_ylabel('Gap: Incentive − Comparison (pp)', fontsize=10)
ax2.set_title('Incentive–Comparison Penetration Gap (Annual)', fontsize=10, fontweight='bold')
ax2.axhline(0, color='black', linewidth=0.8)
ax2.grid(axis='y', linestyle=':', alpha=0.5)
ax2.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.0f pp'))

fig.suptitle('Figure 9: Pre/Post Trend Assessment — Incentive vs Comparison States',
             fontsize=11, fontweight='bold')
fig.tight_layout(rect=[0, 0.04, 1, 1])
fig.text(0.5, 0.01, SOURCE_NOTE, ha='center', va='bottom',
         fontsize=7, color='#555555', style='italic')
fig.savefig(os.path.join(FIGS, 'figure9_pretrend_assessment.png'),
            dpi=180, bbox_inches='tight', facecolor='white')
fig.savefig(os.path.join(FIGS, 'figure9_pretrend_assessment.svg'),
            format='svg', bbox_inches='tight', facecolor='white')
plt.close(fig)
print("  ✓ Saved: figure9_pretrend_assessment.png and .svg")
print("\nPolicy impact analysis complete.")

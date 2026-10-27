"""
03_descriptive_analysis.py
---------------------------
Descriptive statistics, state comparisons, and incentive-group analysis.

Inputs:
  data/processed/cleaned_state_monthly_data.csv
  data/processed/cleaned_state_financial_year_data.csv
  data/processed/state_ev_policy_data.csv

Outputs:
  outputs/tables/descriptive_statistics.csv
  outputs/tables/state_comparison.csv
  outputs/tables/incentive_group_comparison.csv
"""

import os
import warnings
import pandas as pd
import numpy as np

warnings.filterwarnings('ignore')

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(BASE, '..')
PROC = os.path.join(ROOT, 'data', 'processed')
TBLS = os.path.join(ROOT, 'outputs', 'tables')
os.makedirs(TBLS, exist_ok=True)

# ── Load data ─────────────────────────────────────────────────────────────────
df_monthly = pd.read_csv(os.path.join(PROC, 'cleaned_state_monthly_data.csv'),
                          parse_dates=['month_date'])
df_annual  = pd.read_csv(os.path.join(PROC, 'cleaned_state_financial_year_data.csv'))
df_policy  = pd.read_csv(os.path.join(PROC, 'state_ev_policy_data.csv'))

print("Monthly dataset:", df_monthly.shape)
print("Annual dataset:", df_annual.shape)
print("Policy dataset:", df_policy.shape)

# ── Incentive classification ──────────────────────────────────────────────────
# Only 'Yes' = verified direct purchase incentive; everything else = comparison
df_policy['incentive_group'] = df_policy['has_direct_e2w_purchase_incentive'].apply(
    lambda x: 'Incentive' if str(x).strip().lower().startswith('yes') else 'Comparison'
)
incentive_states = df_policy[df_policy['incentive_group'] == 'Incentive']['state'].tolist()
comparison_states = df_policy[df_policy['incentive_group'] == 'Comparison']['state'].tolist()

print(f"\nIncentive states ({len(incentive_states)}): {incentive_states}")
print(f"Comparison states ({len(comparison_states)}): {comparison_states}")

# Also capture effective dates for incentive states
policy_dates = df_policy[df_policy['incentive_group'] == 'Incentive'][
    ['state', 'effective_date', 'policy_name']
].copy()
policy_dates['effective_date'] = pd.to_datetime(
    policy_dates['effective_date'], errors='coerce')

# Merge incentive group into datasets
state_group_map = df_policy.set_index('state')['incentive_group'].to_dict()

df_annual['incentive_group']  = df_annual['state'].map(state_group_map).fillna('Unclassified')
df_monthly['incentive_group'] = df_monthly['state'].map(state_group_map).fillna('Unclassified')

# ── 1. National totals by FY ──────────────────────────────────────────────────
national_fy = df_annual.groupby('financial_year').agg(
    total_2w          = ('total_2w_annual', 'sum'),
    electric_2w       = ('electric_2w_annual', 'sum'),
    year_number       = ('year_number', 'first'),
).reset_index()
national_fy['ev_penetration_pct'] = (
    100 * national_fy['electric_2w'] / national_fy['total_2w'])

print("\n== National EV Penetration by FY ==")
print(national_fy.to_string(index=False))

# ── 2. State-level by FY ──────────────────────────────────────────────────────
state_fy_pivot = df_annual.pivot_table(
    index='state',
    columns='financial_year',
    values='ev_penetration_pct_annual',
    aggfunc='first'
).reset_index()

# Change in penetration
fy_cols = ['FY2020-21', 'FY2021-22', 'FY2022-23', 'FY2023-24']
for col in fy_cols:
    if col not in state_fy_pivot.columns:
        state_fy_pivot[col] = np.nan

state_fy_pivot['change_fy2021_to_fy2024_pp'] = (
    state_fy_pivot['FY2023-24'] - state_fy_pivot['FY2020-21'])
state_fy_pivot['rank_fy2024'] = state_fy_pivot['FY2023-24'].rank(
    ascending=False, na_option='bottom').astype(int)
state_fy_pivot['rank_change'] = state_fy_pivot['change_fy2021_to_fy2024_pp'].rank(
    ascending=False, na_option='bottom').astype(int)
state_fy_pivot['incentive_group'] = state_fy_pivot['state'].map(state_group_map)

# ── 3. Registration volumes ────────────────────────────────────────────────────
state_regs = df_annual.pivot_table(
    index='state',
    columns='financial_year',
    values=['total_2w_annual', 'electric_2w_annual'],
    aggfunc='first'
).reset_index()

# ── 4. State comparison table (comprehensive) ─────────────────────────────────
state_comparison = state_fy_pivot.copy()
# Add registration data
for fy in fy_cols:
    sub = df_annual[df_annual['financial_year'] == fy][
        ['state', 'total_2w_annual', 'electric_2w_annual']].copy()
    sub.columns = ['state', f'total_2w_{fy}', f'electric_2w_{fy}']
    state_comparison = state_comparison.merge(sub, on='state', how='left')

# Relative growth in EV registrations (FY2020-21 as baseline)
ev_baseline = df_annual[df_annual['financial_year'] == 'FY2020-21'][
    ['state', 'electric_2w_annual']].rename(
    columns={'electric_2w_annual': 'ev_baseline'})
ev_end = df_annual[df_annual['financial_year'] == 'FY2023-24'][
    ['state', 'electric_2w_annual']].rename(
    columns={'electric_2w_annual': 'ev_end'})
ev_growth = ev_baseline.merge(ev_end, on='state', how='inner')
ev_growth['ev_relative_growth_pct'] = np.where(
    ev_growth['ev_baseline'] > 0,
    100 * (ev_growth['ev_end'] - ev_growth['ev_baseline']) / ev_growth['ev_baseline'],
    np.nan
)
state_comparison = state_comparison.merge(
    ev_growth[['state', 'ev_baseline', 'ev_end', 'ev_relative_growth_pct']],
    on='state', how='left')

state_comparison.sort_values('rank_fy2024', inplace=True)
state_comparison.reset_index(drop=True, inplace=True)

print("\n== State Comparison (top 15 by FY2023-24 penetration) ==")
print(state_comparison[['state', 'FY2020-21', 'FY2021-22', 'FY2022-23', 'FY2023-24',
                          'change_fy2021_to_fy2024_pp', 'incentive_group']].head(15).to_string())

# ── 5. Incentive-group descriptive comparison ──────────────────────────────────
def group_stats(group_df, label):
    """Compute weighted and unweighted group penetration."""
    row = {'incentive_group': label}
    for fy in fy_cols:
        sub = group_df[group_df['financial_year'] == fy]
        # Pooled (weighted) penetration
        pool_ev = sub['electric_2w_annual'].sum()
        pool_tot = sub['total_2w_annual'].sum()
        row[f'pooled_pct_{fy}'] = (100 * pool_ev / pool_tot) if pool_tot > 0 else np.nan
        # Unweighted average (equal-state-weight)
        row[f'avg_pct_{fy}'] = sub['ev_penetration_pct_annual'].mean()
        row[f'n_states_{fy}'] = sub['state'].nunique()
    return row

incentive_df = df_annual[df_annual['incentive_group'] == 'Incentive']
comparison_df = df_annual[df_annual['incentive_group'] == 'Comparison']

group_rows = [
    group_stats(incentive_df, 'Incentive states'),
    group_stats(comparison_df, 'Comparison states'),
    group_stats(df_annual, 'All states'),
]
incentive_group_stats = pd.DataFrame(group_rows)
print("\n== Incentive Group Comparison (Pooled Penetration %) ==")
pooled_cols = ['incentive_group'] + [f'pooled_pct_{fy}' for fy in fy_cols]
print(incentive_group_stats[pooled_cols].to_string(index=False))
print("\n== Incentive Group Comparison (Unweighted Average Penetration %) ==")
avg_cols = ['incentive_group'] + [f'avg_pct_{fy}' for fy in fy_cols]
print(incentive_group_stats[avg_cols].to_string(index=False))

# ── 6. Monthly national trend ─────────────────────────────────────────────────
national_monthly = df_monthly.groupby('month_date').agg(
    total_2w    = ('total_2w_registrations', 'sum'),
    electric_2w = ('electric_2w_registrations', 'sum'),
).reset_index()
national_monthly['ev_penetration_pct'] = (
    100 * national_monthly['electric_2w'] / national_monthly['total_2w'])

# ── 7. Monthly group trends ────────────────────────────────────────────────────
monthly_group = df_monthly.groupby(['month_date', 'incentive_group']).agg(
    total_2w    = ('total_2w_registrations', 'sum'),
    electric_2w = ('electric_2w_registrations', 'sum'),
    n_states    = ('state', 'nunique'),
).reset_index()
monthly_group['ev_penetration_pct'] = (
    100 * monthly_group['electric_2w'] / monthly_group['total_2w'])

# ── 8. Descriptive statistics summary ─────────────────────────────────────────
desc_rows = []

# National FY stats
for _, row in national_fy.iterrows():
    desc_rows.append({
        'category': 'National',
        'state': 'All India',
        'financial_year': row['financial_year'],
        'total_2w_registrations': row['total_2w'],
        'electric_2w_registrations': row['electric_2w'],
        'ev_penetration_pct': row['ev_penetration_pct'],
        'metric': 'Pooled national penetration',
    })

# Group stats
for _, g_row in incentive_group_stats.iterrows():
    grp = g_row['incentive_group']
    for fy in fy_cols:
        desc_rows.append({
            'category': grp,
            'state': grp,
            'financial_year': fy,
            'total_2w_registrations': np.nan,
            'electric_2w_registrations': np.nan,
            'ev_penetration_pct': g_row[f'pooled_pct_{fy}'],
            'metric': 'Pooled group penetration',
        })

desc_stats = pd.DataFrame(desc_rows)

# Save all tables
state_comparison.to_csv(os.path.join(TBLS, 'state_comparison.csv'), index=False)
incentive_group_stats.to_csv(os.path.join(TBLS, 'incentive_group_comparison.csv'), index=False)
desc_stats.to_csv(os.path.join(TBLS, 'descriptive_statistics.csv'), index=False)
national_monthly.to_csv(os.path.join(TBLS, 'national_monthly_trend.csv'), index=False)
monthly_group.to_csv(os.path.join(TBLS, 'monthly_group_trend.csv'), index=False)

print("\n✓ All descriptive tables saved.")

# Export objects for use by visualisation script
if __name__ == '__main__':
    print("\nDescriptive analysis complete.")

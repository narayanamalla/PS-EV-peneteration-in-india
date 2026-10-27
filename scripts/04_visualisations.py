"""
04_visualisations.py
---------------------
Publication-quality figures for the E2W EV penetration analysis.

Figures produced:
  Figure 1 — National adoption trend (monthly)
  Figure 2 — Incentive vs comparison group monthly trends
  Figure 3 — State-level penetration trajectories (small multiples)
  Figure 4 — State ranking by change in EV penetration
  Figure 5 — Registrations and penetration over time (national)
  Figure 6 — Policy timeline annotated on group trends
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
from matplotlib.lines import Line2D

matplotlib.use('Agg')
warnings.filterwarnings('ignore')

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE  = os.path.dirname(os.path.abspath(__file__))
ROOT  = os.path.join(BASE, '..')
PROC  = os.path.join(ROOT, 'data', 'processed')
FIGS  = os.path.join(ROOT, 'outputs', 'figures')
TBLS  = os.path.join(ROOT, 'outputs', 'tables')
os.makedirs(FIGS, exist_ok=True)

# ── Load data ──────────────────────────────────────────────────────────────────
df_monthly = pd.read_csv(os.path.join(PROC, 'cleaned_state_monthly_data.csv'),
                          parse_dates=['month_date'])
df_annual  = pd.read_csv(os.path.join(PROC, 'cleaned_state_financial_year_data.csv'))
df_policy  = pd.read_csv(os.path.join(PROC, 'state_ev_policy_data.csv'))
national_monthly = pd.read_csv(os.path.join(TBLS, 'national_monthly_trend.csv'),
                                 parse_dates=['month_date'])
monthly_group = pd.read_csv(os.path.join(TBLS, 'monthly_group_trend.csv'),
                              parse_dates=['month_date'])
state_comparison = pd.read_csv(os.path.join(TBLS, 'state_comparison.csv'))

# Policy classification
df_policy['incentive_group'] = df_policy['has_direct_e2w_purchase_incentive'].apply(
    lambda x: 'Incentive' if str(x).strip().lower().startswith('yes') else 'Comparison'
)
state_group_map = df_policy.set_index('state')['incentive_group'].to_dict()
df_annual['incentive_group']  = df_annual['state'].map(state_group_map).fillna('Unclassified')
df_monthly['incentive_group'] = df_monthly['state'].map(state_group_map).fillna('Unclassified')

# Verified policy dates
policy_dates_df = df_policy[
    (df_policy['incentive_group'] == 'Incentive') &
    (df_policy['effective_date'].notna()) &
    (df_policy['effective_date'] != '')
][['state', 'policy_name', 'effective_date']].copy()
policy_dates_df['effective_date'] = pd.to_datetime(
    policy_dates_df['effective_date'], errors='coerce')
policy_dates_df = policy_dates_df.dropna(subset=['effective_date'])

# Study period bounds
STUDY_START = pd.Timestamp('2020-04-01')
STUDY_END   = pd.Timestamp('2024-03-31')

# ── Style ──────────────────────────────────────────────────────────────────────
INCENTIVE_COLOR  = '#1a6faf'   # Blue
COMPARISON_COLOR = '#d94f3d'   # Red
NATIONAL_COLOR   = '#2d7a4f'   # Green

FY_BOUNDARIES = [
    pd.Timestamp('2021-04-01'),
    pd.Timestamp('2022-04-01'),
    pd.Timestamp('2023-04-01'),
]
FY_LABELS = ['FY2021-22', 'FY2022-23', 'FY2023-24']

SOURCE_NOTE = 'Source: Ministry of Road Transport & Highways, Vahan Dashboard. Author\'s calculations.'

def add_fy_bands(ax, alpha=0.04):
    """Shade alternating financial-year bands."""
    bands = [
        (pd.Timestamp('2020-04-01'), pd.Timestamp('2021-04-01')),
        (pd.Timestamp('2021-04-01'), pd.Timestamp('2022-04-01')),
        (pd.Timestamp('2022-04-01'), pd.Timestamp('2023-04-01')),
        (pd.Timestamp('2023-04-01'), pd.Timestamp('2024-04-01')),
    ]
    for i, (s, e) in enumerate(bands):
        ax.axvspan(s, e, color='grey' if i % 2 == 0 else 'white', alpha=alpha, zorder=0)

def add_source(fig, note=SOURCE_NOTE, y=0.01):
    fig.text(0.5, y, note, ha='center', va='bottom',
             fontsize=7, color='#555555', style='italic',
             wrap=True)

def save_fig(fig, name):
    png_path = os.path.join(FIGS, f'{name}.png')
    svg_path = os.path.join(FIGS, f'{name}.svg')
    fig.savefig(png_path, dpi=180, bbox_inches='tight', facecolor='white')
    fig.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'  ✓ Saved: {os.path.basename(png_path)} and {os.path.basename(svg_path)}')


# ═══════════════════════════════════════════════════════════════════════════════
# Figure 1 — National monthly EV penetration trend
# ═══════════════════════════════════════════════════════════════════════════════
print('\nGenerating Figure 1 — National adoption trend...')

fig, ax = plt.subplots(figsize=(11, 5))
add_fy_bands(ax)

ax.plot(national_monthly['month_date'], national_monthly['ev_penetration_pct'],
        color=NATIONAL_COLOR, linewidth=2.2, label='Pooled EV penetration', zorder=3)
ax.fill_between(national_monthly['month_date'],
                national_monthly['ev_penetration_pct'],
                alpha=0.12, color=NATIONAL_COLOR)

# FY boundary lines
for bd in FY_BOUNDARIES:
    ax.axvline(bd, color='grey', linewidth=0.8, linestyle='--', alpha=0.6, zorder=2)

# FY labels at top
ylim_top = national_monthly['ev_penetration_pct'].max() * 1.15
fy_spans = [
    (pd.Timestamp('2020-04-01'), pd.Timestamp('2021-04-01'), 'FY2020–21'),
    (pd.Timestamp('2021-04-01'), pd.Timestamp('2022-04-01'), 'FY2021–22'),
    (pd.Timestamp('2022-04-01'), pd.Timestamp('2023-04-01'), 'FY2022–23'),
    (pd.Timestamp('2023-04-01'), pd.Timestamp('2024-04-01'), 'FY2023–24'),
]
for s, e, label in fy_spans:
    mid = s + (e - s) / 2
    ax.text(mid, ylim_top * 0.97, label, ha='center', va='top',
            fontsize=8, color='#444444', fontweight='bold')

ax.set_xlim(STUDY_START, STUDY_END)
ax.set_ylim(0, ylim_top)
ax.set_xlabel('Month', fontsize=10)
ax.set_ylabel('EV Penetration (%)', fontsize=10)
ax.set_title('Figure 1: National Electric Two-Wheeler Penetration Trend\n'
             '(Pooled: all 36 states/UTs, April 2020 – March 2024)',
             fontsize=11, fontweight='bold', pad=10)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[4, 7, 10, 1]))
ax.tick_params(axis='both', labelsize=8)
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f%%'))
ax.grid(axis='y', linestyle=':', alpha=0.5, zorder=0)
ax.legend(fontsize=9, loc='upper left')
fig.tight_layout(rect=[0, 0.04, 1, 1])
add_source(fig)
save_fig(fig, 'figure1_national_trend')


# ═══════════════════════════════════════════════════════════════════════════════
# Figure 2 — Incentive vs comparison group monthly trends
# ═══════════════════════════════════════════════════════════════════════════════
print('Generating Figure 2 — Incentive vs comparison group trends...')

inc_monthly = monthly_group[monthly_group['incentive_group'] == 'Incentive']
cmp_monthly = monthly_group[monthly_group['incentive_group'] == 'Comparison']

fig, ax = plt.subplots(figsize=(11, 5))
add_fy_bands(ax)

ax.plot(inc_monthly['month_date'], inc_monthly['ev_penetration_pct'],
        color=INCENTIVE_COLOR, linewidth=2.2,
        label='Incentive states (8)', zorder=3)
ax.plot(cmp_monthly['month_date'], cmp_monthly['ev_penetration_pct'],
        color=COMPARISON_COLOR, linewidth=2.2,
        label='Comparison states (28)', zorder=3, linestyle='--')
ax.fill_between(inc_monthly['month_date'], inc_monthly['ev_penetration_pct'],
                alpha=0.10, color=INCENTIVE_COLOR)
ax.fill_between(cmp_monthly['month_date'], cmp_monthly['ev_penetration_pct'],
                alpha=0.10, color=COMPARISON_COLOR)

for bd in FY_BOUNDARIES:
    ax.axvline(bd, color='grey', linewidth=0.8, linestyle='--', alpha=0.6)

ymax = max(inc_monthly['ev_penetration_pct'].max(),
           cmp_monthly['ev_penetration_pct'].max()) * 1.2

for s, e, label in fy_spans:
    mid = s + (e - s) / 2
    ax.text(mid, ymax * 0.97, label, ha='center', va='top',
            fontsize=8, color='#444444', fontweight='bold')

ax.set_xlim(STUDY_START, STUDY_END)
ax.set_ylim(0, ymax)
ax.set_xlabel('Month', fontsize=10)
ax.set_ylabel('EV Penetration (%) — Pooled', fontsize=10)
ax.set_title('Figure 2: EV Penetration — States with Additional Purchase Incentives\n'
             'vs Comparison States (Pooled registrations, 2020–2024)',
             fontsize=11, fontweight='bold', pad=10)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[4, 7, 10, 1]))
ax.tick_params(axis='both', labelsize=8)
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f%%'))
ax.grid(axis='y', linestyle=':', alpha=0.5)
ax.legend(fontsize=9, loc='upper left')
# Note on group definition
ax.text(0.01, 0.35,
        'Incentive states: AP, Delhi, Gujarat,\nHaryana, Kerala, Maharashtra,\nRajasthan, Tamil Nadu\n(verified direct purchase subsidy)',
        transform=ax.transAxes, fontsize=7.5,
        bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.8),
        color='#333333')
fig.tight_layout(rect=[0, 0.04, 1, 1])
add_source(fig)
save_fig(fig, 'figure2_incentive_comparison')


# ═══════════════════════════════════════════════════════════════════════════════
# Figure 3 — State-level trajectories (small multiples)
# ═══════════════════════════════════════════════════════════════════════════════
print('Generating Figure 3 — State-level trajectories...')

states_sorted = sorted(df_annual['state'].unique())
n_states = len(states_sorted)
ncols = 6
nrows = int(np.ceil(n_states / ncols))

fig, axes = plt.subplots(nrows, ncols, figsize=(16, nrows * 2.4),
                          sharex=False, sharey=False)
axes_flat = axes.flatten()

fy_cols_short = ['FY2020-21', 'FY2021-22', 'FY2022-23', 'FY2023-24']
fy_x = [1, 2, 3, 4]

for i, state in enumerate(states_sorted):
    ax = axes_flat[i]
    s_data = df_annual[df_annual['state'] == state].sort_values('year_number')
    grp = state_group_map.get(state, 'Unclassified')
    color = INCENTIVE_COLOR if grp == 'Incentive' else COMPARISON_COLOR

    pcts = [s_data[s_data['financial_year'] == fy]['ev_penetration_pct_annual'].values
            for fy in fy_cols_short]
    pcts = [p[0] if len(p) > 0 else np.nan for p in pcts]

    ax.plot(fy_x, pcts, color=color, linewidth=1.8, marker='o', markersize=3.5)
    ax.fill_between(fy_x, pcts, alpha=0.12, color=color)
    ax.set_title(state, fontsize=6.5, fontweight='bold', pad=3, wrap=True)
    ax.set_xticks(fy_x)
    ax.set_xticklabels(['20-21', '21-22', '22-23', '23-24'], fontsize=5.5, rotation=30)
    ax.tick_params(axis='y', labelsize=5.5)
    ax.set_ylim(bottom=0)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.0f%%'))
    ax.grid(axis='y', linestyle=':', alpha=0.4)

# Hide unused subplots
for j in range(n_states, len(axes_flat)):
    axes_flat[j].set_visible(False)

# Legend
legend_handles = [
    mpatches.Patch(color=INCENTIVE_COLOR, label='Incentive state'),
    mpatches.Patch(color=COMPARISON_COLOR, label='Comparison state'),
]
fig.legend(handles=legend_handles, loc='lower right', fontsize=9,
           bbox_to_anchor=(0.98, 0.01))

fig.suptitle('Figure 3: EV Two-Wheeler Penetration Trajectories by State\n'
             '(FY2020–21 to FY2023–24)',
             fontsize=12, fontweight='bold', y=1.01)
fig.tight_layout(rect=[0, 0.03, 1, 1])
add_source(fig, y=0.005)
save_fig(fig, 'figure3_state_trajectories')


# ═══════════════════════════════════════════════════════════════════════════════
# Figure 4 — State ranking by change in EV penetration
# ═══════════════════════════════════════════════════════════════════════════════
print('Generating Figure 4 — State ranking by change in penetration...')

sc = state_comparison[['state', 'change_fy2021_to_fy2024_pp', 'incentive_group',
                         'FY2020-21', 'FY2023-24']].dropna(
    subset=['change_fy2021_to_fy2024_pp']).copy()
sc.sort_values('change_fy2021_to_fy2024_pp', ascending=True, inplace=True)
sc.reset_index(drop=True, inplace=True)

colors = [INCENTIVE_COLOR if g == 'Incentive' else COMPARISON_COLOR
          for g in sc['incentive_group']]

fig, ax = plt.subplots(figsize=(9, 11))
bars = ax.barh(sc['state'], sc['change_fy2021_to_fy2024_pp'],
               color=colors, edgecolor='white', linewidth=0.4)

# Annotate values
for bar, val in zip(bars, sc['change_fy2021_to_fy2024_pp']):
    ax.text(val + 0.05, bar.get_y() + bar.get_height() / 2,
            f'{val:+.2f} pp', va='center', ha='left', fontsize=6.5, color='#333333')

ax.axvline(0, color='black', linewidth=0.8)
ax.set_xlabel('Change in EV Penetration (percentage points, FY2020–21 → FY2023–24)',
              fontsize=9)
ax.set_title('Figure 4: State Rankings — Change in Electric Two-Wheeler Penetration\n'
             'FY2020–21 to FY2023–24',
             fontsize=11, fontweight='bold', pad=10)
ax.tick_params(axis='both', labelsize=8)
ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('%.0f pp'))
ax.grid(axis='x', linestyle=':', alpha=0.5)

legend_handles = [
    mpatches.Patch(color=INCENTIVE_COLOR, label='Incentive state'),
    mpatches.Patch(color=COMPARISON_COLOR, label='Comparison state'),
]
ax.legend(handles=legend_handles, fontsize=8, loc='lower right')
fig.tight_layout(rect=[0, 0.04, 1, 1])
add_source(fig)
save_fig(fig, 'figure4_state_ranking_change')


# ═══════════════════════════════════════════════════════════════════════════════
# Figure 5 — Registrations and penetration (national)
# ═══════════════════════════════════════════════════════════════════════════════
print('Generating Figure 5 — Registrations and penetration...')

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8), sharex=True,
                                 gridspec_kw={'hspace': 0.35})
add_fy_bands(ax1)
add_fy_bands(ax2)

# Top panel: registration volumes
ax1.fill_between(national_monthly['month_date'],
                  national_monthly['total_2w'] / 1e6,
                  color='#aaaaaa', alpha=0.5, label='Non-electric 2W', zorder=2)
ax1.fill_between(national_monthly['month_date'],
                  national_monthly['electric_2w'] / 1e6,
                  color=INCENTIVE_COLOR, alpha=0.8, label='Electric 2W', zorder=3)
ax1.set_ylabel('Registrations (millions)', fontsize=10)
ax1.set_title('Figure 5: National Two-Wheeler Registrations and EV Penetration\n'
              '(Monthly, April 2020 – March 2024)',
              fontsize=11, fontweight='bold', pad=10)
ax1.legend(fontsize=9, loc='upper left')
ax1.grid(axis='y', linestyle=':', alpha=0.5)
ax1.tick_params(axis='y', labelsize=8)

# Bottom panel: EV penetration
ax2.plot(national_monthly['month_date'],
         national_monthly['ev_penetration_pct'],
         color=NATIONAL_COLOR, linewidth=2, zorder=3)
ax2.fill_between(national_monthly['month_date'],
                  national_monthly['ev_penetration_pct'],
                  alpha=0.15, color=NATIONAL_COLOR)
ax2.set_ylabel('EV Penetration (%)', fontsize=10)
ax2.set_xlabel('Month', fontsize=10)
ax2.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f%%'))
ax2.grid(axis='y', linestyle=':', alpha=0.5)
ax2.tick_params(axis='both', labelsize=8)

for ax in [ax1, ax2]:
    for bd in FY_BOUNDARIES:
        ax.axvline(bd, color='grey', linewidth=0.8, linestyle='--', alpha=0.6)
    ax.set_xlim(STUDY_START, STUDY_END)

for s, e, label in fy_spans:
    mid = s + (e - s) / 2
    ax1.text(mid, ax1.get_ylim()[1] * 0.97 if ax1.get_ylim()[1] > 0 else 1,
             label, ha='center', va='top', fontsize=8, color='#444444', fontweight='bold')

ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
ax2.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[4, 7, 10, 1]))
fig.tight_layout(rect=[0, 0.04, 1, 1])
add_source(fig)
save_fig(fig, 'figure5_registrations_penetration')


# ═══════════════════════════════════════════════════════════════════════════════
# Figure 6 — Policy timeline annotated on group trends
# ═══════════════════════════════════════════════════════════════════════════════
print('Generating Figure 6 — Policy timeline...')

fig, ax = plt.subplots(figsize=(13, 6.5))
add_fy_bands(ax)

ax.plot(inc_monthly['month_date'], inc_monthly['ev_penetration_pct'],
        color=INCENTIVE_COLOR, linewidth=2.2,
        label='Incentive states (pooled)', zorder=3)
ax.plot(cmp_monthly['month_date'], cmp_monthly['ev_penetration_pct'],
        color=COMPARISON_COLOR, linewidth=2.2, linestyle='--',
        label='Comparison states (pooled)', zorder=3)

ax.fill_between(inc_monthly['month_date'], inc_monthly['ev_penetration_pct'],
                alpha=0.10, color=INCENTIVE_COLOR)
ax.fill_between(cmp_monthly['month_date'], cmp_monthly['ev_penetration_pct'],
                alpha=0.10, color=COMPARISON_COLOR)

# Policy annotation
y_max_val = inc_monthly['ev_penetration_pct'].max() * 1.35
policy_label_map = {
    'Delhi':        'DL EV\nPolicy',
    'Maharashtra':  'MH EV\nPolicy',
    'Gujarat':      'GJ EV\nPolicy',
    'Kerala':       'KL EV\nPolicy',
    'Rajasthan':    'RJ EV\nPolicy',
    'Haryana':      'HR EV\nPolicy',
    'Andhra Pradesh': 'AP EV\nPolicy',
    'Tamil Nadu':   'TN EV\nPolicy',
}

# Stagger vertical positions to avoid overlap
y_positions = np.linspace(0.55, 0.90, len(policy_dates_df))
policy_dates_sorted = policy_dates_df.sort_values('effective_date').reset_index(drop=True)

for idx, (_, row) in enumerate(policy_dates_sorted.iterrows()):
    dt = row['effective_date']
    if STUDY_START <= dt <= STUDY_END:
        lbl = policy_label_map.get(row['state'], row['state'][:4] + ' EV\nPolicy')
        ax.axvline(dt, color=INCENTIVE_COLOR, linewidth=1.0,
                   linestyle=':', alpha=0.7, zorder=2)
        ax.annotate(lbl,
                    xy=(dt, y_positions[idx] * y_max_val),
                    xytext=(dt + pd.Timedelta(days=12),
                            y_positions[idx] * y_max_val),
                    fontsize=6.0, color=INCENTIVE_COLOR,
                    arrowprops=dict(arrowstyle='->', color=INCENTIVE_COLOR,
                                   lw=0.7),
                    ha='left', va='center')

for bd in FY_BOUNDARIES:
    ax.axvline(bd, color='grey', linewidth=0.8, linestyle='--', alpha=0.5)

for s, e, label in fy_spans:
    mid = s + (e - s) / 2
    ax.text(mid, y_max_val * 0.98, label, ha='center', va='top',
            fontsize=8, color='#444444', fontweight='bold')

ax.set_xlim(STUDY_START, STUDY_END)
ax.set_ylim(0, y_max_val)
ax.set_xlabel('Month', fontsize=10)
ax.set_ylabel('EV Penetration (%) — Pooled', fontsize=10)
ax.set_title('Figure 6: EV Penetration with State Policy Implementation Dates\n'
             '(Incentive vs Comparison States, April 2020 – March 2024)',
             fontsize=11, fontweight='bold', pad=10)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[4, 7, 10, 1]))
ax.tick_params(axis='both', labelsize=8)
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f%%'))
ax.grid(axis='y', linestyle=':', alpha=0.5)
ax.legend(fontsize=9, loc='upper left')
ax.text(0.01, 0.05,
        'Vertical dotted lines show verified effective dates\nof state direct purchase incentive policies.',
        transform=ax.transAxes, fontsize=7.5,
        bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.85),
        color='#333333')
fig.tight_layout(rect=[0, 0.04, 1, 1])
add_source(fig)
save_fig(fig, 'figure6_policy_timeline')


# ═══════════════════════════════════════════════════════════════════════════════
# Bonus Figure 7 — Annual EV penetration heatmap (state × FY)
# ═══════════════════════════════════════════════════════════════════════════════
print('Generating Figure 7 — State × FY penetration heatmap...')

heatmap_df = df_annual.pivot_table(
    index='state', columns='financial_year',
    values='ev_penetration_pct_annual', aggfunc='first'
)[['FY2020-21', 'FY2021-22', 'FY2022-23', 'FY2023-24']]
heatmap_df.sort_values('FY2023-24', ascending=False, inplace=True)

incentive_marker = ['★ ' if state_group_map.get(s, '') == 'Incentive' else '  '
                    for s in heatmap_df.index]
row_labels = [f'{m}{s}' for m, s in zip(incentive_marker, heatmap_df.index)]

fig, ax = plt.subplots(figsize=(8, 12))
cmap = matplotlib.colormaps['YlOrRd']
im = ax.imshow(heatmap_df.values, aspect='auto', cmap=cmap,
               vmin=0, vmax=float(heatmap_df.values[~np.isnan(heatmap_df.values)].max()))

ax.set_xticks(range(4))
ax.set_xticklabels(['FY2020-21', 'FY2021-22', 'FY2022-23', 'FY2023-24'],
                   fontsize=9, fontweight='bold')
ax.set_yticks(range(len(heatmap_df)))
ax.set_yticklabels(row_labels, fontsize=7.5)

# Annotate cells
for row in range(len(heatmap_df)):
    for col in range(4):
        val = heatmap_df.values[row, col]
        if not np.isnan(val):
            txt_color = 'white' if val > heatmap_df.values[~np.isnan(heatmap_df.values)].max() * 0.6 else 'black'
            ax.text(col, row, f'{val:.1f}%', ha='center', va='center',
                    fontsize=6.5, color=txt_color, fontweight='bold')

cb = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
cb.set_label('EV Penetration (%)', fontsize=8)
cb.ax.tick_params(labelsize=7)

ax.set_title('Figure 7: EV Two-Wheeler Penetration by State and Financial Year\n'
             '(★ = State with verified direct purchase incentive)',
             fontsize=10, fontweight='bold', pad=12)
fig.tight_layout(rect=[0, 0.03, 1, 1])
add_source(fig)
save_fig(fig, 'figure7_penetration_heatmap')


# ═══════════════════════════════════════════════════════════════════════════════
# Bonus Figure 8 — Incentive group: FY-level bar comparison
# ═══════════════════════════════════════════════════════════════════════════════
print('Generating Figure 8 — Group bar chart...')

fy_labels_plot = ['FY2020-21', 'FY2021-22', 'FY2022-23', 'FY2023-24']
x = np.arange(len(fy_labels_plot))
width = 0.35

inc_pooled = []
cmp_pooled = []
for fy in fy_labels_plot:
    inc_sub = df_annual[(df_annual['financial_year'] == fy) &
                         (df_annual['incentive_group'] == 'Incentive')]
    cmp_sub = df_annual[(df_annual['financial_year'] == fy) &
                         (df_annual['incentive_group'] == 'Comparison')]
    inc_pooled.append(100 * inc_sub['electric_2w_annual'].sum() /
                      inc_sub['total_2w_annual'].sum() if inc_sub['total_2w_annual'].sum() > 0 else 0)
    cmp_pooled.append(100 * cmp_sub['electric_2w_annual'].sum() /
                      cmp_sub['total_2w_annual'].sum() if cmp_sub['total_2w_annual'].sum() > 0 else 0)

fig, ax = plt.subplots(figsize=(8, 5))
bars1 = ax.bar(x - width/2, inc_pooled, width, label='Incentive states',
               color=INCENTIVE_COLOR, alpha=0.85, edgecolor='white')
bars2 = ax.bar(x + width/2, cmp_pooled, width, label='Comparison states',
               color=COMPARISON_COLOR, alpha=0.85, edgecolor='white')

for bars in [bars1, bars2]:
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 0.06,
                f'{h:.2f}%', ha='center', va='bottom', fontsize=8)

ax.set_xticks(x)
ax.set_xticklabels(fy_labels_plot, fontsize=10)
ax.set_ylabel('EV Penetration (%) — Pooled', fontsize=10)
ax.set_title('Figure 8: EV Two-Wheeler Penetration — Incentive vs Comparison States\n'
             '(Annual, pooled registrations)',
             fontsize=11, fontweight='bold', pad=10)
ax.legend(fontsize=9)
ax.grid(axis='y', linestyle=':', alpha=0.5)
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.0f%%'))
ax.set_ylim(0, max(max(inc_pooled), max(cmp_pooled)) * 1.25)
fig.tight_layout(rect=[0, 0.04, 1, 1])
add_source(fig)
save_fig(fig, 'figure8_group_bar_comparison')

print('\n✓ All figures generated.')

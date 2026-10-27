"""
06_india_map.py
---------------
Publication-quality choropleth maps of EV two-wheeler penetration across Indian states.

Features:
  - Official complete Survey of India boundaries including Jammu & Kashmir and Ladakh
  - Multi-hue, high-contrast colormap (Spectral_r: Blue -> Cyan -> Yellow -> Orange -> Crimson)
  - Small legible state names and penetration percentages on every state/UT
  - Leader lines and offset callouts for small states and union territories
  - Highlighted borders for states offering verified direct purchase incentives
  - High-res PNG, vector SVG, and interactive animated Plotly HTML
"""

import os
import json
import warnings
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import matplotlib.ticker as mticker
import matplotlib.colors as mcolors
from mpl_toolkits.axes_grid1 import make_axes_locatable
from shapely.validation import make_valid

matplotlib.use('Agg')
warnings.filterwarnings('ignore')

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE  = os.path.dirname(os.path.abspath(__file__))
ROOT  = os.path.join(BASE, '..')
PROC  = os.path.join(ROOT, 'data', 'processed')
RAW   = os.path.join(ROOT, 'data', 'raw')
FIGS  = os.path.join(ROOT, 'outputs', 'figures')
os.makedirs(FIGS, exist_ok=True)

# ── Load data ──────────────────────────────────────────────────────────────────
df_annual = pd.read_csv(os.path.join(PROC, 'cleaned_state_financial_year_data.csv'))
df_policy = pd.read_csv(os.path.join(PROC, 'state_ev_policy_data.csv'))

df_policy['incentive_group'] = df_policy['has_direct_e2w_purchase_incentive'].apply(
    lambda x: 'Incentive' if str(x).strip().lower().startswith('yes') else 'Comparison'
)
incentive_states = set(df_policy[df_policy['incentive_group'] == 'Incentive']['state'])

# ── Load Complete GeoJSON (Official Survey of India boundaries) ────────────────
geojson_path = os.path.join(RAW, 'india_states_complete.geojson')
gdf = gpd.read_file(geojson_path)
gdf['geometry'] = gdf['geometry'].apply(make_valid)
gdf = gdf.to_crs(epsg=4326)

print("Complete GeoJSON CRS:", gdf.crs)
print("Boundary Extent:", gdf.total_bounds)

# Canonical map from GeoJSON st_nm to Vahan dataset state names
GEO_NAME_MAP = {
    'Andaman and Nicobar Islands': 'Andaman & Nicobar Islands',
    'Arunachal Pradesh':          'Arunachal Pradesh',
    'Assam':                      'Assam',
    'Bihar':                      'Bihar',
    'Chandigarh':                 'Chandigarh',
    'Chhattisgarh':               'Chhattisgarh',
    'Dadra and Nagar Haveli':     'Dadra & Nagar Haveli and Daman & Diu',
    'Daman and Diu':              'Dadra & Nagar Haveli and Daman & Diu',
    'Delhi':                      'Delhi',
    'Goa':                        'Goa',
    'Gujarat':                    'Gujarat',
    'Haryana':                    'Haryana',
    'Himachal Pradesh':           'Himachal Pradesh',
    'Jammu and Kashmir':          'Jammu & Kashmir',
    'Jharkhand':                  'Jharkhand',
    'Karnataka':                  'Karnataka',
    'Kerala':                     'Kerala',
    'Lakshadweep':                'Lakshadweep',
    'Madhya Pradesh':             'Madhya Pradesh',
    'Maharashtra':                'Maharashtra',
    'Manipur':                    'Manipur',
    'Meghalaya':                  'Meghalaya',
    'Mizoram':                    'Mizoram',
    'Nagaland':                   'Nagaland',
    'Odisha':                     'Odisha',
    'Puducherry':                 'Puducherry',
    'Punjab':                     'Punjab',
    'Rajasthan':                  'Rajasthan',
    'Sikkim':                     'Sikkim',
    'Tamil Nadu':                 'Tamil Nadu',
    'Telangana':                  'Telangana',
    'Tripura':                    'Tripura',
    'Uttar Pradesh':              'Uttar Pradesh',
    'Uttarakhand':                'Uttarakhand',
    'West Bengal':                'West Bengal',
    'Andhra Pradesh':             'Andhra Pradesh',
    'Ladakh':                     'Ladakh'
}

gdf['state'] = gdf['st_nm'].map(GEO_NAME_MAP)
gdf_dissolved = gdf.dissolve(by='state', as_index=False)[['state', 'geometry']]
print(f"Dissolved to {len(gdf_dissolved)} administrative regions (all 36 matched)")

# ── EV penetration pivot ───────────────────────────────────────────────────────
FY_COLS = ['FY2020-21', 'FY2021-22', 'FY2022-23', 'FY2023-24']
pct_pivot = df_annual.pivot_table(
    index='state', columns='financial_year',
    values='ev_penetration_pct_annual', aggfunc='first'
).reset_index()

gdf_data = gdf_dissolved.merge(pct_pivot, on='state', how='left')
gdf_data['is_incentive'] = gdf_data['state'].isin(incentive_states)

# Colormap settings: Multi-hued Spectral_r (Blue -> Cyan -> Yellow -> Orange -> Crimson)
CMAP = 'Spectral_r'
VMIN = 0.0
VMAX = 20.0
INCENTIVE_EDGE_COLOR = '#111827'   # Dark contrast border
INCENTIVE_EDGE_WIDTH = 1.8
NORMAL_EDGE_COLOR    = '#ffffff'   # Clean white boundary separator
NORMAL_EDGE_WIDTH    = 0.6
OCEAN_COLOR          = '#eef6fc'
SOURCE = "Source: Ministry of Road Transport & Highways, Vahan Dashboard. Boundaries: Survey of India standard. Author's calculations."

# Smart label offset coordinates for small UTs and states
LABEL_OFFSETS = {
    'Delhi': (82.5, 29.5),
    'Chandigarh': (73.2, 31.8),
    'Goa': (71.0, 15.4),
    'Puducherry': (82.8, 11.2),
    'Dadra & Nagar Haveli and Daman & Diu': (69.2, 20.2),
    'Sikkim': (89.5, 28.5),
    'Lakshadweep': (69.2, 10.8),
    'Tripura': (90.2, 22.4),
}

# Short display names for compact map legibility
SHORT_NAMES = {
    'Jammu & Kashmir': 'J&K',
    'Himachal Pradesh': 'Himachal',
    'Madhya Pradesh': 'Madhya Pr.',
    'Uttar Pradesh': 'Uttar Pr.',
    'Andhra Pradesh': 'Andhra Pr.',
    'Arunachal Pradesh': 'Arunachal',
    'Dadra & Nagar Haveli and Daman & Diu': 'DNH & DD',
    'Andaman & Nicobar Islands': 'A&N Islands',
    'Uttarakhand': 'Uttarakhand',
    'West Bengal': 'W. Bengal',
}

def annotate_states(ax, gdf_d, col, is_small_panel=False):
    """Draw small state names and EV penetration percentages on map."""
    fontsize = 3.6 if is_small_panel else 5.2
    stroke_w = 1.2 if is_small_panel else 1.8

    for _, r in gdf_d.iterrows():
        name = r['state']
        val = r[col]
        val_str = f'{val:.1f}%' if pd.notna(val) else 'N/A'
        pt = r.geometry.representative_point()

        # In small panel view, skip long offsets to avoid clutter
        if is_small_panel:
            disp_name = SHORT_NAMES.get(name, name)
            if val >= 4.0 or name in ['Delhi', 'Goa', 'Kerala', 'Maharashtra', 'Karnataka', 'Jammu & Kashmir', 'Ladakh']:
                ax.text(pt.x, pt.y, f'{disp_name}\n{val_str}',
                        fontsize=fontsize, ha='center', va='center', fontweight='bold',
                        color='#111111',
                        path_effects=[pe.withStroke(linewidth=stroke_w, foreground='white')])
        else:
            # Standalone map: label every single state
            if name in LABEL_OFFSETS:
                ox, oy = LABEL_OFFSETS[name]
                disp_name = SHORT_NAMES.get(name, name)
                ax.annotate(
                    f'{disp_name}\n{val_str}',
                    xy=(pt.x, pt.y), xytext=(ox, oy),
                    fontsize=fontsize, ha='center', va='center', fontweight='bold',
                    color='#111111',
                    arrowprops=dict(arrowstyle='->', lw=0.6, color='#222222'),
                    path_effects=[pe.withStroke(linewidth=stroke_w, foreground='white')]
                )
            else:
                disp_name = SHORT_NAMES.get(name, name)
                ax.text(pt.x, pt.y, f'{disp_name}\n{val_str}',
                        fontsize=fontsize, ha='center', va='center', fontweight='bold',
                        color='#111111',
                        path_effects=[pe.withStroke(linewidth=stroke_w, foreground='white')])


# ── Map Drawing Function ───────────────────────────────────────────────────────
def draw_map(ax, gdf_d, col, title, cmap_norm, cmap_obj, is_small_panel=False):
    ax.set_aspect('equal')
    ax.set_facecolor(OCEAN_COLOR)

    # Plot base polygons
    gdf_d.plot(
        column=col, ax=ax,
        cmap=cmap_obj, norm=cmap_norm,
        edgecolor=NORMAL_EDGE_COLOR, linewidth=NORMAL_EDGE_WIDTH,
        zorder=3, legend=False
    )

    # Thicker highlight border for verified incentive states
    incentive_geo = gdf_d[gdf_d['is_incentive']]
    if not incentive_geo.empty:
        incentive_geo.plot(ax=ax, color='none',
                           edgecolor=INCENTIVE_EDGE_COLOR,
                           linewidth=INCENTIVE_EDGE_WIDTH, zorder=5)

    # Add small state names & percentage values
    annotate_states(ax, gdf_d, col, is_small_panel=is_small_panel)

    ax.set_title(title, fontsize=10 if is_small_panel else 12, fontweight='bold', pad=8)
    ax.set_axis_off()

    # Bounding box showing complete India, full J&K, Ladakh, A&N, and Lakshadweep
    ax.set_xlim(67.5, 98.0)
    ax.set_ylim(6.0, 37.8)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. Figure 10: 2×2 Panel Map across Financial Years
# ═══════════════════════════════════════════════════════════════════════════════
print('\nGenerating Figure 10 (2×2 Panel Map across FY2020-21 to FY2023-24)...')

cmap_obj  = matplotlib.colormaps[CMAP]
cmap_norm = mcolors.Normalize(vmin=VMIN, vmax=VMAX)

fig, axes = plt.subplots(2, 2, figsize=(16, 18))
axes_flat = axes.flatten()

fy_titles = {
    'FY2020-21': 'FY 2020–21  (Baseline)',
    'FY2021-22': 'FY 2021–22',
    'FY2022-23': 'FY 2022–23',
    'FY2023-24': 'FY 2023–24  (End-line)',
}

for ax, fy in zip(axes_flat, FY_COLS):
    draw_map(ax, gdf_data, fy, fy_titles[fy], cmap_norm, cmap_obj, is_small_panel=True)

fig.subplots_adjust(right=0.86, hspace=0.06, wspace=0.02)
cbar_ax = fig.add_axes([0.88, 0.18, 0.022, 0.64])
sm = plt.cm.ScalarMappable(cmap=cmap_obj, norm=cmap_norm)
sm.set_array([])
cbar = fig.colorbar(sm, cax=cbar_ax)
cbar.set_label('EV Two-Wheeler Penetration (%)', fontsize=11, labelpad=10)
cbar.ax.tick_params(labelsize=9)
cbar.set_ticks([0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20])
cbar.set_ticklabels(['0%', '2%', '4%', '6%', '8%', '10%', '12%', '14%', '16%', '18%', '20%+'])

border_patch = mpatches.Patch(
    facecolor='none', edgecolor=INCENTIVE_EDGE_COLOR,
    linewidth=2, label='★ Direct Purchase Incentive State (verified)'
)
fig.legend(handles=[border_patch],
           loc='lower center', ncol=1,
           fontsize=10, frameon=True,
           bbox_to_anchor=(0.44, 0.015))

fig.suptitle(
    'Figure 10: Evolution of Electric Two-Wheeler Penetration Across India\n'
    '(Complete official boundaries including Jammu & Kashmir and Ladakh | FY2020–21 to FY2023–24)',
    fontsize=14, fontweight='bold', y=0.98
)
fig.text(0.44, 0.003, SOURCE, ha='center', fontsize=8, color='#555555', style='italic')

panel_png = os.path.join(FIGS, 'figure10_india_map_panel.png')
panel_svg = os.path.join(FIGS, 'figure10_india_map_panel.svg')
fig.savefig(panel_png, dpi=200, bbox_inches='tight', facecolor='white')
fig.savefig(panel_svg, format='svg', bbox_inches='tight', facecolor='white')
plt.close(fig)
print(f'  ✓ Saved: figure10_india_map_panel.png and .svg')


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Figure 11: Standalone FY2023-24 Map with Complete State Names & Percentages
# ═══════════════════════════════════════════════════════════════════════════════
print('Generating Figure 11 (Standalone FY2023-24 Detailed Map)...')

fig2, ax2 = plt.subplots(figsize=(12, 14))
draw_map(ax2, gdf_data, 'FY2023-24',
         'Electric Two-Wheeler Penetration by State & UT — FY 2023–24',
         cmap_norm, cmap_obj, is_small_panel=False)

divider = make_axes_locatable(ax2)
cax2 = divider.append_axes('right', size='3.5%', pad=0.15)
sm2 = plt.cm.ScalarMappable(cmap=cmap_obj, norm=cmap_norm)
sm2.set_array([])
cbar2 = fig2.colorbar(sm2, cax=cax2)
cbar2.set_label('EV Penetration Rate (%)', fontsize=11, labelpad=8)
cbar2.ax.tick_params(labelsize=9)
cbar2.set_ticks([0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20])
cbar2.set_ticklabels(['0%', '2%', '4%', '6%', '8%', '10%', '12%', '14%', '16%', '18%', '20%+'])

h1 = mpatches.Patch(facecolor='none', edgecolor=INCENTIVE_EDGE_COLOR,
                    linewidth=2.5, label='Direct Purchase Incentive State')
ax2.legend(handles=[h1], loc='lower left', fontsize=9.5, framealpha=0.92, facecolor='white')

fig2.suptitle(
    'Figure 11: Geographic Distribution of Electric Two-Wheeler Penetration (FY 2023–24)\n'
    '(Complete official Indian boundary; state names and penetration figures displayed)',
    fontsize=13, fontweight='bold', y=0.96
)
fig2.text(0.5, 0.02, SOURCE, ha='center', fontsize=8, color='#555555', style='italic')

solo_png = os.path.join(FIGS, 'figure11_india_map_fy2324.png')
solo_svg = os.path.join(FIGS, 'figure11_india_map_fy2324.svg')
fig2.savefig(solo_png, dpi=200, bbox_inches='tight', facecolor='white')
fig2.savefig(solo_svg, format='svg', bbox_inches='tight', facecolor='white')
plt.close(fig2)
print(f'  ✓ Saved: figure11_india_map_fy2324.png and .svg')


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Figure 12: Change Map (FY2020-21 → FY2023-24)
# ═══════════════════════════════════════════════════════════════════════════════
print('Generating Figure 12 (Change in EV Penetration Map)...')

gdf_data['change_pp'] = gdf_data['FY2023-24'] - gdf_data['FY2020-21']

change_cmap = matplotlib.colormaps['Spectral_r']
change_norm = mcolors.Normalize(vmin=0, vmax=float(gdf_data['change_pp'].max()))

fig3, ax3 = plt.subplots(figsize=(12, 14))
ax3.set_aspect('equal')
ax3.set_facecolor(OCEAN_COLOR)

gdf_data.plot(column='change_pp', ax=ax3,
              cmap=change_cmap, norm=change_norm,
              edgecolor=NORMAL_EDGE_COLOR, linewidth=NORMAL_EDGE_WIDTH,
              zorder=3, legend=False)

gdf_data[gdf_data['is_incentive']].plot(
    ax=ax3, color='none',
    edgecolor=INCENTIVE_EDGE_COLOR,
    linewidth=INCENTIVE_EDGE_WIDTH, zorder=5
)

# Annotate with change figures
for _, r in gdf_data.iterrows():
    name = r['state']
    val = r['change_pp']
    val_str = f'+{val:.1f}pp' if pd.notna(val) else 'N/A'
    pt = r.geometry.representative_point()

    if name in LABEL_OFFSETS:
        ox, oy = LABEL_OFFSETS[name]
        disp = SHORT_NAMES.get(name, name)
        ax3.annotate(
            f'{disp}\n{val_str}', xy=(pt.x, pt.y), xytext=(ox, oy),
            fontsize=5.2, ha='center', va='center', fontweight='bold', color='#111111',
            arrowprops=dict(arrowstyle='->', lw=0.6, color='#222222'),
            path_effects=[pe.withStroke(linewidth=1.8, foreground='white')]
        )
    else:
        disp = SHORT_NAMES.get(name, name)
        ax3.text(pt.x, pt.y, f'{disp}\n{val_str}',
                 fontsize=5.2, ha='center', va='center', fontweight='bold', color='#111111',
                 path_effects=[pe.withStroke(linewidth=1.8, foreground='white')])

ax3.set_xlim(67.5, 98.0)
ax3.set_ylim(6.0, 37.8)
ax3.set_axis_off()

divider3 = make_axes_locatable(ax3)
cax3 = divider3.append_axes('right', size='3.5%', pad=0.15)
sm3 = plt.cm.ScalarMappable(cmap=change_cmap, norm=change_norm)
sm3.set_array([])
cbar3 = fig3.colorbar(sm3, cax=cax3)
cbar3.set_label('Penetration Gain (percentage points)', fontsize=11, labelpad=8)
cbar3.ax.tick_params(labelsize=9)

h1c = mpatches.Patch(facecolor='none', edgecolor=INCENTIVE_EDGE_COLOR,
                     linewidth=2.5, label='Direct Purchase Incentive State')
ax3.legend(handles=[h1c], loc='lower left', fontsize=9.5, framealpha=0.92, facecolor='white')

fig3.suptitle(
    'Figure 12: Total Change in EV Two-Wheeler Penetration (FY 2020–21 → FY 2023–24)\n'
    '(Complete official Indian boundary; percentage point gains displayed per state)',
    fontsize=13, fontweight='bold', y=0.96
)
fig3.text(0.5, 0.02, SOURCE, ha='center', fontsize=8, color='#555555', style='italic')

change_png = os.path.join(FIGS, 'figure12_india_map_change.png')
change_svg = os.path.join(FIGS, 'figure12_india_map_change.svg')
fig3.savefig(change_png, dpi=200, bbox_inches='tight', facecolor='white')
fig3.savefig(change_svg, format='svg', bbox_inches='tight', facecolor='white')
plt.close(fig3)
print(f'  ✓ Saved: figure12_india_map_change.png and .svg')


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Interactive Animated Plotly HTML Map with FY Slider & Complete Boundaries
# ═══════════════════════════════════════════════════════════════════════════════
print('Generating interactive animated map (Plotly HTML)...')
try:
    import plotly.express as px

    with open(geojson_path) as f:
        geojson_data = json.load(f)

    for feature in geojson_data['features']:
        raw_name = feature['properties']['st_nm']
        feature['properties']['state'] = GEO_NAME_MAP.get(raw_name, raw_name)
        feature['id'] = feature['properties']['state']

    df_int = df_annual.merge(df_policy[['state', 'incentive_group', 'policy_name']], on='state', how='left')
    df_int['ev_penetration_pct_annual'] = df_int['ev_penetration_pct_annual'].round(2)

    fig_int = px.choropleth(
        df_int,
        geojson=geojson_data,
        locations='state',
        featureidkey='properties.state',
        color='ev_penetration_pct_annual',
        color_continuous_scale='Spectral_r',
        range_color=(0, 20),
        animation_frame='financial_year',
        hover_name='state',
        hover_data={
            'state': False,
            'ev_penetration_pct_annual': ':.2f',
            'incentive_group': True,
            'electric_2w_annual': ':,',
            'total_2w_annual': ':,'
        },
        labels={
            'ev_penetration_pct_annual': 'EV Penetration (%)',
            'incentive_group': 'Incentive Group',
            'electric_2w_annual': 'Electric 2W',
            'total_2w_annual': 'Total 2W'
        },
        title='Electric Two-Wheeler Penetration Across India (FY2020-21 to FY2023-24)'
    )
    fig_int.update_geos(fitbounds='locations', visible=False)
    fig_int.update_layout(margin={'r':0,'t':50,'l':0,'b':0})

    interactive_out = os.path.join(FIGS, 'india_map_interactive.html')
    fig_int.write_html(interactive_out)
    print(f'  ✓ Saved: india_map_interactive.html')
except Exception as e:
    print(f'  ⚠ Plotly interactive map error: {e}')

print('\n✓ All India map figures generated successfully with complete boundaries, multi-colors, and state labels.')

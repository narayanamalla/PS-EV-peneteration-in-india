import json
import os
import pandas as pd
import geopandas as gpd
from shapely.validation import make_valid

# 1. GeoJSON with complete official boundaries
gdf = gpd.read_file('data/raw/india_states_complete.geojson')
gdf['geometry'] = gdf['geometry'].apply(make_valid)

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
gdf_d = gdf.dissolve(by='state', as_index=False)[['state', 'geometry']]
gdf_d['geometry'] = gdf_d['geometry'].simplify(tolerance=0.012, preserve_topology=True)
geo_json = json.loads(gdf_d.to_json())

# 2. State FY data & Policy
df_fy = pd.read_csv('data/processed/cleaned_state_financial_year_data.csv')
df_pol = pd.read_csv('data/processed/state_ev_policy_data.csv')
df_pol['group'] = df_pol['has_direct_e2w_purchase_incentive'].apply(
    lambda x: 'Incentive' if str(x).strip().lower().startswith('yes') else 'Comparison'
)

pol_dict = df_pol.set_index('state').to_dict(orient='index')

states_dict = {}
for st in sorted(df_fy['state'].unique()):
    st_rows = df_fy[df_fy['state'] == st].sort_values('year_number')
    pol_info = pol_dict.get(st, {})
    
    years_data = {}
    for _, r in st_rows.iterrows():
        years_data[r['financial_year']] = {
            'total_2w': int(r['total_2w_annual']),
            'electric_2w': int(r['electric_2w_annual']),
            'penetration_pct': round(float(r['ev_penetration_pct_annual']), 2) if pd.notna(r['ev_penetration_pct_annual']) else 0.0
        }
    
    pen_21 = years_data.get('FY2020-21', {}).get('penetration_pct', 0)
    pen_24 = years_data.get('FY2023-24', {}).get('penetration_pct', 0)
    change_pp = round(pen_24 - pen_21, 2)
    
    states_dict[st] = {
        'name': st,
        'group': pol_info.get('group', 'Comparison'),
        'has_direct_incentive': pol_info.get('group') == 'Incentive',
        'policy_name': pol_info.get('policy_name', 'None identified'),
        'effective_date': pol_info.get('effective_date', 'N/A') if pd.notna(pol_info.get('effective_date')) else 'N/A',
        'incentive_amount': pol_info.get('incentive_amount_or_formula', 'No direct purchase incentive identified'),
        'notes': pol_info.get('notes', ''),
        'verification_status': pol_info.get('verification_status', ''),
        'source_url': pol_info.get('source_url', ''),
        'years': years_data,
        'change_pp': change_pp
    }

# Compute ranks
fy24_sorted = sorted(states_dict.values(), key=lambda s: s['years']['FY2023-24']['penetration_pct'], reverse=True)
for rank, s in enumerate(fy24_sorted, 1):
    states_dict[s['name']]['rank_fy24'] = rank

change_sorted = sorted(states_dict.values(), key=lambda s: s['change_pp'], reverse=True)
for rank, s in enumerate(change_sorted, 1):
    states_dict[s['name']]['rank_change'] = rank

# 3. National Annual
nat_annual = []
for fy in ['FY2020-21', 'FY2021-22', 'FY2022-23', 'FY2023-24']:
    sub = df_fy[df_fy['financial_year'] == fy]
    tot = int(sub['total_2w_annual'].sum())
    ev = int(sub['electric_2w_annual'].sum())
    pen = round(100.0 * ev / tot, 2)
    
    inc_sub = sub[sub['state'].isin([s for s, d in states_dict.items() if d['has_direct_incentive']])]
    cmp_sub = sub[~sub['state'].isin([s for s, d in states_dict.items() if d['has_direct_incentive']])]
    
    inc_pen = round(100.0 * inc_sub['electric_2w_annual'].sum() / inc_sub['total_2w_annual'].sum(), 2)
    cmp_pen = round(100.0 * cmp_sub['electric_2w_annual'].sum() / cmp_sub['total_2w_annual'].sum(), 2)
    
    nat_annual.append({
        'financial_year': fy,
        'total_2w': tot,
        'electric_2w': ev,
        'penetration_pct': pen,
        'incentive_pooled': inc_pen,
        'comparison_pooled': cmp_pen
    })

# 4. Monthly Trend (48 months)
df_m = pd.read_csv('data/processed/cleaned_state_monthly_data.csv')
inc_states_list = [s for s, d in states_dict.items() if d['has_direct_incentive']]
df_m['is_inc'] = df_m['state'].isin(inc_states_list)

m_trend = []
for dt, grp in df_m.groupby('month_date'):
    tot_all = grp['total_2w_registrations'].sum()
    ev_all = grp['electric_2w_registrations'].sum()
    pen_all = round(100.0 * ev_all / tot_all, 2) if tot_all > 0 else 0
    
    inc_g = grp[grp['is_inc']]
    tot_inc = inc_g['total_2w_registrations'].sum()
    ev_inc = inc_g['electric_2w_registrations'].sum()
    pen_inc = round(100.0 * ev_inc / tot_inc, 2) if tot_inc > 0 else 0
    
    cmp_g = grp[~grp['is_inc']]
    tot_cmp = cmp_g['total_2w_registrations'].sum()
    ev_cmp = cmp_g['electric_2w_registrations'].sum()
    pen_cmp = round(100.0 * ev_cmp / tot_cmp, 2) if tot_cmp > 0 else 0
    
    # Format label like 'Apr 2020'
    date_obj = pd.to_datetime(dt)
    label_str = date_obj.strftime('%b %Y')
    
    m_trend.append({
        'date': str(dt)[:7],
        'label': label_str,
        'total_2w': int(tot_all),
        'electric_2w': int(ev_all),
        'penetration_all': pen_all,
        'penetration_incentive': pen_inc,
        'penetration_comparison': pen_cmp
    })

payload = {
    'geo_json': geo_json,
    'states': states_dict,
    'national_annual': nat_annual,
    'monthly_trend': m_trend,
    'econometrics': {
        'did_estimate': 3.484,
        'did_se': 1.589,
        'did_pvalue': 0.0283,
        'did_ci': [0.369, 6.598],
        'twfe_estimate': 1.739,
        'twfe_se': 1.003,
        'twfe_pvalue': 0.0829,
        'incentive_states_count': 8,
        'comparison_states_count': 28
    }
}

with open('data.json', 'w') as f:
    json.dump(payload, f)

print('data.json created successfully in root!')

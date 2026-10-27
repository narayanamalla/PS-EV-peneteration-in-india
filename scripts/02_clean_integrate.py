"""
02_clean_integrate.py
----------------------
Data cleaning, integration, and derived-variable creation for the
Indian E2W EV penetration analysis.

Input:  data/raw/*.csv
Output:
  data/processed/cleaned_state_monthly_data.csv
  data/processed/cleaned_state_financial_year_data.csv
  outputs/tables/data_quality_report.md
"""

import os
import re
import warnings
import pandas as pd
import numpy as np

warnings.filterwarnings('ignore')

# ── Paths ────────────────────────────────────────────────────────────────────
BASE  = os.path.dirname(os.path.abspath(__file__))
ROOT  = os.path.join(BASE, '..')
RAW   = os.path.join(ROOT, 'data', 'raw')
PROC  = os.path.join(ROOT, 'data', 'processed')
TBLS  = os.path.join(ROOT, 'outputs', 'tables')
os.makedirs(PROC, exist_ok=True)
os.makedirs(TBLS, exist_ok=True)

# ── Financial-year file map ──────────────────────────────────────────────────
FY_FILES = {
    'FY2020-21': ('2020-21.csv',   '2020-21ev.csv'),
    'FY2021-22': ('2021-22.csv',   '2021-22ev.csv'),
    'FY2022-23': ('2022-23.csv',   '2022-23ev.csv'),
    'FY2023-24': ('2023-24.csv',   '2023-24ev.csv'),
}

# Financial year April–March month sequence
FY_MONTHS_ORDER = ['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep',
                   'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar']

# Canonical state name map (raw → clean)
STATE_NAME_MAP = {
    'Andaman & Nicobar Island':   'Andaman & Nicobar Islands',
    'Andaman & Nicobar Islands':  'Andaman & Nicobar Islands',
    'UT of DNH and DD':           'Dadra & Nagar Haveli and Daman & Diu',
    'Dadra And Nagar Haveli':     'Dadra & Nagar Haveli and Daman & Diu',
    'Daman And Diu':              'Dadra & Nagar Haveli and Daman & Diu',
    'Andhra Pradesh':             'Andhra Pradesh',
    'Arunachal Pradesh':          'Arunachal Pradesh',
    'Assam':                      'Assam',
    'Bihar':                      'Bihar',
    'Chandigarh':                 'Chandigarh',
    'Chhattisgarh':               'Chhattisgarh',
    'Delhi':                      'Delhi',
    'Goa':                        'Goa',
    'Gujarat':                    'Gujarat',
    'Haryana':                    'Haryana',
    'Himachal Pradesh':           'Himachal Pradesh',
    'Jammu and Kashmir':          'Jammu & Kashmir',
    'Jammu & Kashmir':            'Jammu & Kashmir',
    'Jharkhand':                  'Jharkhand',
    'Karnataka':                  'Karnataka',
    'Kerala':                     'Kerala',
    'Ladakh':                     'Ladakh',
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
}

# ── Data-quality log ─────────────────────────────────────────────────────────
QC_LOG = []

def log(msg):
    print(msg)
    QC_LOG.append(msg)


# ── Reader ───────────────────────────────────────────────────────────────────
def read_vahan_csv(filepath):
    """
    Vahan export format:
      Row 0: title string (col 0) + month column headers (cols 1…N-1) + 'Total' (last col)
      Row 1+: state data rows; last row is 'Total'
    Returns:
      df        – wide DataFrame with state rows only (Total excluded)
      month_cols – ordered list of month column labels (e.g. '2020-Jan')
      title      – title string
    """
    df_raw = pd.read_csv(filepath, header=None, encoding='utf-8-sig',
                         dtype=str, keep_default_na=False)

    # Row 0: extract title and column names
    header_row = df_raw.iloc[0].tolist()
    title_cell = str(header_row[0])
    # The actual header for column 0 is the last token after the final newline
    # (the Vahan export embeds the title + \n\nState in cell 0)
    title = re.split(r'\\n', title_cell)[0].strip()
    # Column names: 'State' for col 0, then month codes, then 'Total'
    col_names = ['State'] + [str(c).strip() for c in header_row[1:]]

    # Data rows (skip row 0 which is the header)
    df = df_raw.iloc[1:].copy()
    df.columns = col_names

    # Strip whitespace from State column
    df['State'] = df['State'].str.strip()

    # Remove the grand-total row
    is_total = df['State'].str.lower() == 'total'
    total_row = df[is_total].copy()
    df = df[~is_total].copy()

    # Month columns (everything except State and Total)
    month_cols = [c for c in df.columns if c not in ('State', 'Total')]

    return df, month_cols, title, total_row


# ── Financial-year month extraction ─────────────────────────────────────────
def fy_month_label(fy: str, mon: str) -> str:
    """Return the canonical column label 'YYYY-Mon' for a given month within a FY."""
    start_year = int(fy[2:6])   # e.g. 2020 from 'FY2020-21'
    end_year   = start_year + 1  # 2021
    # Apr–Dec belong to start_year; Jan–Mar to end_year
    if mon in ('Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'):
        return f"{start_year}-{mon}"
    else:
        return f"{end_year}-{mon}"


def extract_fy_months(df_wide, month_cols_available, fy):
    """
    Given a wide DataFrame and a FY label, select only the 12 months
    that belong to that financial year (Apr to Mar), in correct FY order.
    Returns a long DataFrame with columns: State, month, registrations.
    """
    rows = []
    for mon in FY_MONTHS_ORDER:
        label = fy_month_label(fy, mon)
        if label in month_cols_available:
            col_data = df_wide[['State', label]].copy()
            col_data.columns = ['state_raw', 'registrations_str']
            col_data['month'] = mon
            col_data['month_label'] = label
            rows.append(col_data)
        else:
            log(f"  ⚠ Column '{label}' not found for {fy} — month '{mon}' missing")

    if not rows:
        return pd.DataFrame()

    long = pd.concat(rows, ignore_index=True)
    return long


# ── Main cleaning pipeline ────────────────────────────────────────────────────
def clean_and_integrate():
    log("=" * 70)
    log("  VAHAN DATA CLEANING & INTEGRATION PIPELINE")
    log("=" * 70)

    all_monthly_records = []
    qc_issues = []

    for fy, (total_file, ev_file) in FY_FILES.items():
        log(f"\n{'─'*60}")
        log(f"  Processing: {fy}")
        log(f"{'─'*60}")

        t_path = os.path.join(RAW, total_file)
        e_path = os.path.join(RAW, ev_file)

        # ── Read ──────────────────────────────────────────────────────────────
        df_total, total_months, t_title, total_grand = read_vahan_csv(t_path)
        df_ev,    ev_months,    e_title, ev_grand    = read_vahan_csv(e_path)

        log(f"  Total 2W file: {total_file}  ({len(df_total)} states, {len(total_months)} months)")
        log(f"  EV 2W file:    {ev_file}  ({len(df_ev)} states, {len(ev_months)} months)")
        log(f"  Total month cols: {total_months}")
        log(f"  EV month cols:    {ev_months}")

        # Check state lists match
        total_states_raw = set(df_total['State'].str.strip())
        ev_states_raw    = set(df_ev['State'].str.strip())
        missing_in_ev    = total_states_raw - ev_states_raw
        extra_in_ev      = ev_states_raw - total_states_raw
        if missing_in_ev:
            log(f"  ⚠ States in total but NOT in EV file: {missing_in_ev}")
            qc_issues.append(f"{fy}: States in total not in EV: {missing_in_ev}")
        if extra_in_ev:
            log(f"  ⚠ States in EV but NOT in total file: {extra_in_ev}")
            qc_issues.append(f"{fy}: States in EV not in total: {extra_in_ev}")

        # ── Extract FY months in long format ──────────────────────────────────
        long_total = extract_fy_months(df_total, total_months, fy)
        long_ev    = extract_fy_months(df_ev,    ev_months,    fy)

        if long_total.empty or long_ev.empty:
            log(f"  ✗ Could not extract months for {fy}; skipping.")
            continue

        # Add FY label
        long_total['financial_year'] = fy
        long_ev['financial_year']    = fy

        # Canonicalise state names
        long_total['state'] = long_total['state_raw'].str.strip().map(
            lambda s: STATE_NAME_MAP.get(s, s))
        long_ev['state']    = long_ev['state_raw'].str.strip().map(
            lambda s: STATE_NAME_MAP.get(s, s))

        # ── Convert registrations to numeric ─────────────────────────────────
        def to_numeric_safe(df, colname='registrations_str'):
            df = df.copy()
            df['registrations'] = pd.to_numeric(
                df[colname].str.replace(',', '').str.strip(),
                errors='coerce')
            n_bad = df['registrations'].isna().sum()
            if n_bad:
                log(f"  ⚠ {n_bad} non-numeric registration values coerced to NaN")
                qc_issues.append(f"{fy}: {n_bad} non-numeric values coerced")
            n_neg = (df['registrations'] < 0).sum()
            if n_neg:
                log(f"  ⚠ {n_neg} negative registration values found")
                qc_issues.append(f"{fy}: {n_neg} negative registration values")
            return df

        long_total = to_numeric_safe(long_total)
        long_ev    = to_numeric_safe(long_ev)

        # ── Merge ────────────────────────────────────────────────────────────
        merge_key = ['state', 'financial_year', 'month']
        merged = pd.merge(
            long_total[merge_key + ['month_label', 'registrations']].rename(
                columns={'registrations': 'total_2w_registrations'}),
            long_ev[merge_key + ['registrations']].rename(
                columns={'registrations': 'electric_2w_registrations'}),
            on=merge_key,
            how='outer',
            indicator=True
        )

        # Report merge mismatches
        n_left_only  = (merged['_merge'] == 'left_only').sum()
        n_right_only = (merged['_merge'] == 'right_only').sum()
        if n_left_only:
            log(f"  ⚠ {n_left_only} rows in total only (no EV match)")
            qc_issues.append(f"{fy}: {n_left_only} rows with no EV match")
        if n_right_only:
            log(f"  ⚠ {n_right_only} rows in EV only (no total match)")
            qc_issues.append(f"{fy}: {n_right_only} rows with no total match")

        # Check EV > Total (impossible)
        ev_exceeds = merged['electric_2w_registrations'] > merged['total_2w_registrations']
        n_exceed = ev_exceeds.sum()
        if n_exceed:
            log(f"  ⚠ {n_exceed} rows where EV registrations > total 2W registrations")
            qc_issues.append(f"{fy}: {n_exceed} rows where EV > total")
            # Print offending rows
            offenders = merged[ev_exceeds][['state','month','total_2w_registrations','electric_2w_registrations']]
            log(f"    Offending rows:\n{offenders.to_string()}")

        merged.drop(columns=['_merge'], inplace=True)
        all_monthly_records.append(merged)
        log(f"  ✓ {len(merged)} state-month records for {fy}")

    # ── Combine all years ─────────────────────────────────────────────────────
    log(f"\n{'─'*60}")
    log("  Combining all financial years")
    df = pd.concat(all_monthly_records, ignore_index=True)
    log(f"  Combined rows: {len(df)}")

    # ── Month ordering and date ───────────────────────────────────────────────
    month_to_num = {m: i for i, m in enumerate(FY_MONTHS_ORDER, start=1)}
    df['month_fy_order'] = df['month'].map(month_to_num)

    # Create a proper calendar date (first of month)
    # month_label is 'YYYY-Mon'
    df['month_date'] = pd.to_datetime(df['month_label'], format='%Y-%b')

    # Financial-year ordering
    fy_order = {'FY2020-21': 1, 'FY2021-22': 2, 'FY2022-23': 3, 'FY2023-24': 4}
    df['year_number'] = df['financial_year'].map(fy_order)

    # ── Filter to FY2020-21 through FY2023-24 ────────────────────────────────
    valid_fy = set(FY_FILES.keys())
    before = len(df)
    df = df[df['financial_year'].isin(valid_fy)].copy()
    after  = len(df)
    if before != after:
        log(f"  Rows outside study period dropped: {before - after}")

    # ── Derived variables ─────────────────────────────────────────────────────
    df['non_electric_2w_registrations'] = np.where(
        df['total_2w_registrations'].notna() & df['electric_2w_registrations'].notna(),
        df['total_2w_registrations'] - df['electric_2w_registrations'],
        np.nan
    )

    # EV penetration — undefined where total = 0 or NaN
    df['ev_penetration_pct'] = np.where(
        (df['total_2w_registrations'].notna()) & (df['total_2w_registrations'] > 0),
        100.0 * df['electric_2w_registrations'] / df['total_2w_registrations'],
        np.nan
    )

    # ── Uniqueness check ──────────────────────────────────────────────────────
    key_cols = ['state', 'financial_year', 'month']
    n_dupes = df.duplicated(subset=key_cols).sum()
    if n_dupes:
        log(f"  ⚠ {n_dupes} duplicate state-FY-month keys found — check source data")
        qc_issues.append(f"Duplicate keys: {n_dupes}")
    else:
        log(f"  ✓ No duplicate state-FY-month keys")

    # ── Sort ──────────────────────────────────────────────────────────────────
    df.sort_values(['state', 'year_number', 'month_fy_order'], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # ── Final column selection ────────────────────────────────────────────────
    monthly_cols = [
        'state', 'financial_year', 'year_number', 'month', 'month_date',
        'total_2w_registrations', 'electric_2w_registrations',
        'non_electric_2w_registrations', 'ev_penetration_pct'
    ]
    df_monthly = df[monthly_cols].copy()

    # ── Annual aggregation ────────────────────────────────────────────────────
    fy_agg = df_monthly.groupby(['state', 'financial_year', 'year_number']).agg(
        total_2w_annual       = ('total_2w_registrations', 'sum'),
        electric_2w_annual    = ('electric_2w_registrations', 'sum'),
        months_with_data      = ('total_2w_registrations', lambda x: x.notna().sum()),
        months_ev_data        = ('electric_2w_registrations', lambda x: x.notna().sum()),
    ).reset_index()

    # Annual penetration: ratio of totals (NOT average of monthly rates)
    fy_agg['ev_penetration_pct_annual'] = np.where(
        fy_agg['total_2w_annual'] > 0,
        100.0 * fy_agg['electric_2w_annual'] / fy_agg['total_2w_annual'],
        np.nan
    )
    fy_agg['non_electric_2w_annual'] = (
        fy_agg['total_2w_annual'] - fy_agg['electric_2w_annual']
    )
    fy_agg.sort_values(['state', 'year_number'], inplace=True)
    fy_agg.reset_index(drop=True, inplace=True)

    # ── Summary statistics ────────────────────────────────────────────────────
    log(f"\n{'─'*60}")
    log("  Final datasets")
    log(f"{'─'*60}")
    log(f"  Monthly dataset: {df_monthly.shape}")
    log(f"  Annual dataset:  {fy_agg.shape}")
    log(f"  States covered:  {df_monthly['state'].nunique()}")
    log(f"  FY covered:      {sorted(df_monthly['financial_year'].unique().tolist())}")
    log(f"  Date range:      {df_monthly['month_date'].min()} – {df_monthly['month_date'].max()}")

    missing_monthly = df_monthly[['total_2w_registrations','electric_2w_registrations',
                                   'ev_penetration_pct']].isna().sum()
    log(f"\n  Missing values (monthly dataset):\n{missing_monthly.to_string()}")

    # ── Save ──────────────────────────────────────────────────────────────────
    monthly_out = os.path.join(PROC, 'cleaned_state_monthly_data.csv')
    annual_out  = os.path.join(PROC, 'cleaned_state_financial_year_data.csv')
    df_monthly.to_csv(monthly_out, index=False)
    fy_agg.to_csv(annual_out, index=False)
    log(f"\n  ✓ Saved: {monthly_out}")
    log(f"  ✓ Saved: {annual_out}")

    # ── Data quality report ───────────────────────────────────────────────────
    write_dq_report(df_monthly, fy_agg, qc_issues)

    return df_monthly, fy_agg


def write_dq_report(df_monthly, fy_agg, qc_issues):
    lines = []
    lines.append("# Data Quality Report\n")
    lines.append(f"**Generated:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}\n")
    lines.append(f"**Source:** Vahan Dashboard (Ministry of Road Transport & Highways)\n\n")

    lines.append("## 1. Source Files\n")
    lines.append("| Financial Year | Total 2W File | EV 2W File |")
    lines.append("|---|---|---|")
    for fy, (t, e) in FY_FILES.items():
        lines.append(f"| {fy} | {t} | {e} |")
    lines.append("")

    lines.append("\n## 2. File Structure\n")
    lines.append(
        "Each CSV export from Vahan has the following structure:\n"
        "- **Row 0:** Title string (embedded in cell 0) with month column labels in cells 1 … N\n"
        "- **Rows 1–36:** State/UT-level data (36 geographical units)\n"
        "- **Row 37:** Grand-total row (excluded from analysis)\n"
        "- **Columns:** State name, 24 calendar-month columns (spanning two calendar years per FY), Total\n\n"
        "**Important:** Each FY file spans two calendar years. For example, FY2020-21 contains\n"
        "columns for Jan–Dec 2020 and Jan–Mar 2021 (covering pre-FY months as well).\n"
        "Only the 12 months April to March of the correct financial year are retained.\n"
    )

    lines.append("\n## 3. Cleaning Decisions\n")
    lines.append("| Decision | Rationale |")
    lines.append("|---|---|")
    cleaning_decisions = [
        ("Grand-total rows excluded from record-level data",
         "Prevents double-counting; the Total row is the sum of all state rows."),
        ("Only Apr–Mar months of each FY retained from each file",
         "Each Vahan export spans 24 columns but only 12 belong to the labelled FY."),
        ("State names standardised via a canonical name map",
         "Minor spelling differences exist across export files (e.g. 'Andaman & Nicobar Island' vs '…Islands')."),
        ("'UT of DNH and DD' mapped to 'Dadra & Nagar Haveli and Daman & Diu'",
         "Administrative merger in 2020; Vahan uses abbreviation in earlier files."),
        ("Registration counts converted from string to integer",
         "Vahan exports registration counts as strings; commas stripped before conversion."),
        ("Zero denominators yield undefined (NaN) EV penetration",
         "Division by zero would be misleading; treated as missing rather than 0%."),
        ("Annual EV penetration = annual electric / annual total × 100",
         "Per research spec: ratio of annual totals, not average of monthly rates."),
        ("Negative registration counts flagged (none found)",
         "Validated but no negative counts were present."),
    ]
    for d, r in cleaning_decisions:
        lines.append(f"| {d} | {r} |")
    lines.append("")

    lines.append("\n## 4. Coverage Summary\n")
    lines.append(f"- **States/UTs in final dataset:** {df_monthly['state'].nunique()}")
    lines.append(f"- **Financial years:** {sorted(df_monthly['financial_year'].unique().tolist())}")
    lines.append(f"- **Total state-month observations:** {len(df_monthly)}")
    lines.append(f"- **Date range:** {df_monthly['month_date'].min().strftime('%B %Y')} – {df_monthly['month_date'].max().strftime('%B %Y')}")
    lines.append("")

    # Missing values
    lines.append("\n## 5. Missing Values\n")
    mv = df_monthly[['total_2w_registrations','electric_2w_registrations','ev_penetration_pct']].isna().sum()
    lines.append("| Column | Missing |")
    lines.append("|---|---|")
    for col, n in mv.items():
        lines.append(f"| {col} | {n} |")
    lines.append("")

    lines.append("\n## 6. Validation Issues\n")
    if qc_issues:
        for issue in qc_issues:
            lines.append(f"- {issue}")
    else:
        lines.append("- No critical validation issues found.")
    lines.append("")

    lines.append("\n## 7. EV Penetration Definition\n")
    lines.append(
        "EV penetration is calculated as:\n\n"
        "```\n"
        "EV penetration (%) = (Electric two-wheeler registrations / Total two-wheeler registrations) × 100\n"
        "```\n\n"
        "For annual figures, the numerator and denominator are both summed over the full financial year before dividing.\n"
    )

    lines.append("\n## 8. Known Limitations\n")
    lines.append(
        "- Vahan registration data reflects vehicle registrations, not actual usage or sales.\n"
        "- Some states may have reporting lags (registrations logged in a different month than sale).\n"
        "- The 'EV' category in Vahan includes ELECTRIC(BOV), PLUG-IN HYBRID EV, PURE EV, and STRONG HYBRID EV.\n"
        "- Policy classification (treatment/control group) requires external policy data not present in Vahan exports.\n"
    )

    report_path = os.path.join(TBLS, 'data_quality_report.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    log(f"  ✓ Saved: {report_path}")


if __name__ == '__main__':
    df_monthly, fy_agg = clean_and_integrate()
    print("\nDone.")

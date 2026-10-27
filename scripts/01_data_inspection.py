"""
01_data_inspection.py
---------------------
Inspect and summarise the raw Vahan CSV files without modifying them.
Prints a detailed summary of each file's dimensions, columns, data types,
sample rows, date range, unique states, missing values and structure.
"""

import pandas as pd
import os
import sys

RAW_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')

FILES = {
    'total_2w': ['2020-21.csv', '2021-22.csv', '2022-23.csv', '2023-24.csv'],
    'ev_2w':    ['2020-21ev.csv', '2021-22ev.csv', '2022-23ev.csv', '2023-24ev.csv'],
}


def read_vahan_csv(filepath):
    """
    Vahan exports have:
      Row 0: Title string (single cell)
      Row 1: Empty
      Row 2: Header row (State, month columns, Total)
      Row 3+: Data rows
    """
    with open(filepath, encoding='utf-8-sig') as f:
        lines = f.readlines()

    title = lines[0].strip().strip('"')

    # Find the actual header row (contains 'State')
    header_row = None
    for i, line in enumerate(lines):
        if line.strip().startswith('State,') or line.strip().startswith('"State,'):
            header_row = i
            break

    if header_row is None:
        raise ValueError(f"Could not find header row in {filepath}")

    df = pd.read_csv(filepath, skiprows=header_row, encoding='utf-8-sig')
    return df, title


def inspect_file(label, filepath):
    print(f"\n{'='*70}")
    print(f"  FILE: {os.path.basename(filepath)}  [{label}]")
    print(f"{'='*70}")

    df, title = read_vahan_csv(filepath)
    print(f"\nTitle:\n  {title}")
    print(f"\nDimensions: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"\nColumns ({len(df.columns)}):")
    for c in df.columns:
        print(f"  {c!r}")

    print(f"\nFirst 3 data rows:")
    print(df.head(3).to_string())

    print(f"\nLast 3 data rows:")
    print(df.tail(3).to_string())

    # Identify state vs total rows
    state_col = df.columns[0]
    is_total = df[state_col].str.strip().str.lower() == 'total'
    n_total_rows = is_total.sum()
    n_state_rows = (~is_total).sum()
    states = df.loc[~is_total, state_col].unique().tolist()
    print(f"\nRows labelled 'Total': {n_total_rows}")
    print(f"Rows labelled as states/UTs: {n_state_rows}")
    print(f"Unique states/UTs ({len(states)}): {states}")

    # Month columns (everything except State and Total)
    month_cols = [c for c in df.columns if c not in [state_col, 'Total']]
    print(f"\nMonth columns ({len(month_cols)}): {month_cols}")

    # Check numeric validity of registration columns
    data_cols = month_cols + (['Total'] if 'Total' in df.columns else [])
    num_df = df.loc[~is_total, data_cols].apply(pd.to_numeric, errors='coerce')
    n_missing = num_df.isna().sum().sum()
    n_negative = (num_df < 0).sum().sum()
    print(f"\nMissing values in registration columns: {n_missing}")
    print(f"Negative values in registration columns: {n_negative}")

    return df, states, month_cols


def main():
    print("\n" + "#"*70)
    print("  VAHAN DATA INSPECTION REPORT")
    print("#"*70)

    all_states = {}
    for group, filenames in FILES.items():
        for fname in filenames:
            fpath = os.path.join(RAW_DIR, fname)
            df, states, months = inspect_file(group, fpath)
            all_states[fname] = set(states)

    # Cross-file state coverage comparison
    print(f"\n\n{'='*70}")
    print("  CROSS-FILE STATE COVERAGE")
    print(f"{'='*70}")
    all_keys = sorted(all_states.keys())
    union_states = set().union(*all_states.values())
    print(f"\nUnion of all states across files ({len(union_states)}):")
    for s in sorted(union_states):
        present_in = [k for k in all_keys if s in all_states[k]]
        print(f"  {s:<40} present in {len(present_in)}/{len(all_keys)} files")

    print(f"\nInspection complete.")


if __name__ == '__main__':
    main()

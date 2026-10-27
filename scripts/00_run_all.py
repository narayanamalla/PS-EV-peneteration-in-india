"""
00_run_all.py
--------------
Master script: runs the complete E2W EV penetration analysis pipeline
from raw Vahan data to final outputs.

Usage:
    python3 scripts/00_run_all.py

All paths are relative to the project root. Run from the project root directory.
"""

import subprocess
import sys
import os
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = [
    ('Data inspection',      'scripts/02_clean_integrate.py'),
    ('Descriptive analysis', 'scripts/03_descriptive_analysis.py'),
    ('Visualisations',       'scripts/04_visualisations.py'),
    ('Policy impact',        'scripts/05_policy_impact_analysis.py'),
    ('Geographic maps',      'scripts/06_india_map.py'),
]

print("=" * 70)
print("  E2W EV PENETRATION ANALYSIS — FULL PIPELINE")
print("=" * 70)
print()

errors = []
for label, script in SCRIPTS:
    print(f"  ▶ {label}: {script}")
    t0 = time.time()
    result = subprocess.run(
        [sys.executable, os.path.join(ROOT, '..', script)],
        capture_output=True, text=True
    )
    elapsed = time.time() - t0
    if result.returncode == 0:
        print(f"    ✓ Done ({elapsed:.1f}s)")
    else:
        print(f"    ✗ Error ({elapsed:.1f}s):")
        print(result.stderr[-500:] if result.stderr else result.stdout[-500:])
        errors.append(label)
    print()

print("=" * 70)
if errors:
    print(f"  Completed with errors in: {', '.join(errors)}")
else:
    print("  ✓ All steps completed successfully.")
print("=" * 70)
print()
print("  Outputs:")
print("  data/processed/   → cleaned CSVs and policy data")
print("  outputs/figures/  → PNG and SVG visualisations")
print("  outputs/tables/   → analytical tables and reports")
print("  reports/          → analysis_report.md and README.md")

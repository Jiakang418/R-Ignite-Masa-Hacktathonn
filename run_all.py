#!/usr/bin/env python3
"""
run_all.py — Single-command pipeline execution for R-Ignite MASA Hackathon 2026.

Usage:
    python run_all.py

Executes all six analysis notebooks in dependency order using the project
virtual environment. Total runtime: ~5–8 minutes (GEV bootstrap and ARIMA
grid search dominate).

Each notebook is executed in-place (outputs are written back to the .ipynb
file). All figures and CSV outputs land in outputs/.
"""

import subprocess
import sys
import time
from pathlib import Path

VENV_JUPYTER = Path(".venv/bin/jupyter")
KERNEL       = "rignite_venv"
TIMEOUT      = 600  # 10 minutes per notebook (generous for bootstrap)

NOTEBOOKS = [
    ("01_data_ingestion.ipynb",        "Load & validate all raw data sources"),
    ("02_indicator_analysis.ipynb",    "16-indicator EDA + sector GHG decomposition"),
    ("03_arima_ghg_forecast.ipynb",    "ARIMA GHG forecast 2024–2030 (MYS + PHL)"),
    ("04_chirps_gev_enso.ipynb",       "GEV extreme value + PELT regime break + ENSO"),
    ("05_exhibit2_visualization.ipynb","Transition cost (NGFS NZ2050) + stress matrix"),
    ("06_executive_summary.ipynb",     "Three Gaps dashboard + interactive HTML"),
    ("07_recommendations.ipynb",        "R1–R5 treaty recommendations + procurement roadmap"),
    ("08_gev_copula.ipynb",            "GEV-Copula joint model — MYS-PHL tail dependence"),
]

def run_notebook(notebook_file: str, description: str) -> bool:
    path = Path("notebooks") / notebook_file
    print(f"\n{'='*70}")
    print(f"  {notebook_file}")
    print(f"  {description}")
    print(f"{'='*70}")
    t0 = time.time()

    result = subprocess.run(
        [
            str(VENV_JUPYTER), "nbconvert",
            "--to", "notebook",
            "--execute", "--inplace",
            f"--ExecutePreprocessor.timeout={TIMEOUT}",
            f"--ExecutePreprocessor.kernel_name={KERNEL}",
            str(path),
        ],
        capture_output=True,
        text=True,
    )

    elapsed = time.time() - t0
    if result.returncode == 0:
        print(f"  ✅  OK  ({elapsed:.0f}s)")
        return True
    else:
        print(f"  ❌  FAILED  ({elapsed:.0f}s)")
        print(result.stderr[-2000:])
        return False


def main():
    print("R-Ignite MASA Hackathon 2026 — Full Pipeline")
    print("============================================")
    print(f"Kernel: {KERNEL}  |  Timeout per notebook: {TIMEOUT}s")

    if not VENV_JUPYTER.exists():
        print("ERROR: .venv/bin/jupyter not found.")
        print("Run:  python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt")
        sys.exit(1)

    failures = []
    t_total = time.time()

    for nb_file, desc in NOTEBOOKS:
        success = run_notebook(nb_file, desc)
        if not success:
            failures.append(nb_file)
            print("Pipeline halted — fix the error above before continuing.")
            sys.exit(1)

    elapsed_total = time.time() - t_total
    print(f"\n{'='*70}")
    if failures:
        print(f"❌  {len(failures)} notebook(s) failed: {failures}")
        sys.exit(1)
    else:
        print(f"✅  All {len(NOTEBOOKS)} notebooks completed in {elapsed_total:.0f}s")
        print()
        print("Key outputs:")
        key_files = [
            ("outputs/executive_summary.png",       "Three Gaps framework (main figure)"),
            ("outputs/executive_summary_onepage.pdf","One-page executive summary (PDF)"),
            ("outputs/interactive_stress_test.html", "Interactive Plotly dashboard"),
            ("outputs/r3_gev_and_regime_break.png",  "GEV return levels + PELT break"),
            ("outputs/exhibit_2_chart_final.png",    "Transition cost exhibit"),
        ]
        for fpath, label in key_files:
            exists = "✅" if Path(fpath).exists() else "⬜"
            print(f"  {exists}  {fpath}  —  {label}")


if __name__ == "__main__":
    main()

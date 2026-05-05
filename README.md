# R-Ignite — MASA Hackathon 2026: SEA Climate Risk Assessment for Hannover Re

## Problem Statement
Quantify two additive sources of reserve inadequacy in Hannover Re's SEA treaty book: (1) physical risk mispricing via GEV extreme precipitation analysis, and (2) transition risk exposure under NGFS Net Zero 2050 carbon pricing scenarios.

## Data Sources
| Dataset | Source | Coverage |
|---|---|---|
| CHIRPS v2.0 RX5day | UCSB Climate Hazards Group | MYS+PHL, 1990–2023 |
| EM-DAT | CRED/UCLouvain | MYS+PHL, 1905–2025 |
| NOAA ONI | NOAA CPC | Global, 1950–2026 |
| WDI (CAIT) | World Bank | MYS+PHL, 1990–2023 |
| NGFS GCAM 6.0 | NGFS Scenario Portal | MYS+PHL, 2020–2100 |
| Climate Watch | WRI | MYS+PHL sector GHG |

## Environment Setup & Replication

**Requirements:** Python 3.12+ (tested on 3.12.3). All package version pins are in `requirements.txt`.

**Estimated total run time:** ~5–8 minutes on a standard laptop (GEV bootstrap n=500 and ARIMA grid search dominate).

### Quickstart — Single Command

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m ipykernel install --user --name rignite_venv --display-name "R-Ignite Venv"
python run_all.py
```

`run_all.py` executes all six notebooks in dependency order, writes outputs back to the `.ipynb` files, and prints a summary of all key output files on completion.

### Manual Step-by-Step

1. Create a virtual environment: `python -m venv .venv && source .venv/bin/activate`
2. Install dependencies: `pip install -r requirements.txt`
3. Register the kernel: `python -m ipykernel install --user --name rignite_venv`
4. Execute notebooks `01` through `06` **sequentially** — each notebook depends on outputs from the prior step.

| Notebook | Purpose | Key Output |
|---|---|---|
| `01_data_ingestion.ipynb` | Load & validate all raw sources | `data/processed/*.csv` |
| `02_indicator_analysis.ipynb` | 16-indicator EDA, sector GHG decomposition | `outputs/r1_*.csv/png` |
| `03_arima_ghg_forecast.ipynb` | ARIMA GHG forecast 2024–2026 (MYS + PHL) | `outputs/r2_*.csv/png` |
| `04_chirps_gev_enso.ipynb` | GEV extreme value + PELT + ENSO | `outputs/r3_*.csv/png` |
| `05_exhibit2_visualization.ipynb` | Transition cost (NGFS NZ2050) + stress matrix | `outputs/r4_*.csv/png` |
| `06_executive_summary.ipynb` | Combined dashboard + winning paragraph | `outputs/executive_summary.png`, `interactive_stress_test.html` |
| `08_gev_copula.ipynb` | GEV-Copula joint model — MYS-PHL tail dependence | `outputs/r8_copula_*.png`, `r8_copula_results.csv` |

**Optional — NGFS pre-processing:** `process_ngfs.py` converts the raw `data/raw/Downscaled_GCAM 6.0 NGFS_data.csv` (62 MB) into `data/processed/ngfs_carbon_price_mys_phl.csv`. Run it once if the processed file is missing:
```
python process_ngfs.py
```
If the raw NGFS file is absent, notebooks gracefully degrade to pre-computed outputs in `outputs/`.

### Interactive Dashboard

**Live deployed app:** *(deploy via Streamlit Community Cloud — see steps below)*

```bash
streamlit run app.py
```

Opens a live browser app with three panels:
- **Panel 1 — GEV Return Level Curves:** MYS and PHL 100-yr return levels with 95% bootstrap CI bands
- **Panel 2 — Transition Cost Explorer:** Carbon price × pass-through rate sliders (IMF/OECD calibrated range)
- **Panel 3 — HRe Reserve Gap Waterfall:** Combined physical + transition exposure with SEA allocation sensitivity

All data loaded from `outputs/` — no re-running notebooks required.

**Static fallback:** `outputs/interactive_stress_test.html` — open in any browser, no install needed.

### Deploy to Streamlit Community Cloud (Bonus Points)

This project is fully configured for one-click Streamlit deployment (`app.py` entrypoint, `requirements.txt`, `runtime.txt`).

1. Push this repo to GitHub: `git push origin main`
2. Open [share.streamlit.io](https://share.streamlit.io/) → **New app**
3. Select repository + branch (`main`), set **Main file path:** `app.py`
4. Click **Deploy** — app goes live at `https://<repo-name>.streamlit.app`
5. **Add the live URL to this README and to `outputs/r5_recommendations.txt`**

If a redeploy is needed after changes, use **Reboot app** from the Streamlit app settings menu.

## Key Outputs — Start Here

The `outputs/` directory contains 29 files. Judges: read these five in order.

| File | What it shows | Notebook |
|---|---|---|
| `executive_summary_onepage.pdf` | **One-page brief** — Three Gaps framework, three actions, dollar amounts | `06` |
| `interactive_stress_test.html` | **Interactive dashboard** — open in any browser, no install needed | `06` |
| `r3_gev_and_regime_break.png` | GEV return levels (MYS 216mm / PHL 521mm) + PELT 2007 break | `04` |
| `exhibit_2_chart_final.png` | Transition cost (NGFS NZ2050): MYS $22.4bn vs PHL $14.8bn | `05` |
| `r3_eal_decomposition_waterfall.png` | EAL assumption chain: total loss → insurance penetration → treaty attachment → HRe share | `04` |

Supporting analytical outputs:

| File | Content |
|---|---|
| `r3_results_table.csv` | GEV parameters, bootstrap CIs, PELT break, ENSO correlations, EAL gap |
| `r4_stress_scenario_table.csv` | Three carbon price scenarios (CP / NZ2050 / 2× stress) with GDP % |
| `r4_pass_through_sensitivity_matrix.csv` | 3×3 pass-through × carbon price sensitivity (anchored to IMF/EIOPA) |
| `r6_hre_impact_estimate.csv` | HRe reserve gap with assumption chain and source citations |
| `r8_copula_results.csv` | GEV-Copula: Kendall τ, AIC table, conditional La Niña copula, portfolio loss gap |
| `r8_copula_analysis.png` | Copula AIC comparison · ENSO-conditional τ · portfolio loss CDF |
| `regulatory_context.pdf` | BNM CCPT / BSP Circ.1085 / UNFCCC Art.6 treaty implication table |

## Generative AI Usage
See [AI_Usage.md](AI_Usage.md) for full disclosure of AI tooling used in this repository.
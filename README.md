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

1. Create a virtual environment: `python -m venv .venv && source .venv/bin/activate`
2. Install dependencies: `pip install -r requirements.txt`
3. Execute notebooks `01` through `06` **sequentially** — each notebook depends on outputs from the prior step.

| Notebook | Purpose | Key Output |
|---|---|---|
| `01_data_ingestion.ipynb` | Load & validate all raw sources | `data/processed/*.csv` |
| `02_indicator_analysis.ipynb` | 16-indicator EDA, sector GHG decomposition | `outputs/r1_*.csv/png` |
| `03_arima_ghg_forecast.ipynb` | ARIMA GHG forecast 2024–2026 (MYS + PHL) | `outputs/r2_*.csv/png` |
| `04_chirps_gev_enso.ipynb` | GEV extreme value + PELT + ENSO | `outputs/r3_*.csv/png` |
| `05_exhibit2_visualization.ipynb` | Transition cost (NGFS NZ2050) + stress matrix | `outputs/r4_*.csv/png` |
| `06_executive_summary.ipynb` | Combined dashboard + winning paragraph | `outputs/executive_summary.png`, `interactive_stress_test.html` |

**Optional — NGFS pre-processing:** `process_ngfs.py` converts the raw `data/raw/Downscaled_GCAM 6.0 NGFS_data.csv` (62 MB) into `data/processed/ngfs_carbon_price_mys_phl.csv`. Run it once if the processed file is missing:
```
python process_ngfs.py
```
If the raw NGFS file is absent, notebooks gracefully degrade to pre-computed outputs in `outputs/`.

## Generative AI Usage
See [AI_Usage.md](AI_Usage.md) for full disclosure of AI tooling used in this repository.
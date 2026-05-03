# 🎯 EXECUTION PLAN — R-Ignite MASA Hackathon
## Step-by-Step Build Order (Strongest Competition Path)

**Current date:** 4 May 2026  
**Status audit:** Codebase has significant gaps and bugs — see critical issues list below before running anything.

---

## 🔴 CRITICAL ISSUES TO FIX FIRST (Before Running Any Code)

These bugs are in the current codebase and will produce wrong answers if not fixed:

| # | File | Bug | Fix |
|---|---|---|---|
| 1 | `notebooks/02_indicator_analysis.ipynb` | Indicator table uses `"CHIRPS 3-day max precipitation"` — wrong metric name | Replace with `"CHIRPS RX5day (WMO ETCCDI annual max 5-day precip)"` |
| 2 | `notebooks/02_indicator_analysis.ipynb` | Indicator `"WDI Total GHG (EN.ATM.GHGT.KT.CE)"` — wrong column name | Replace with `WB_WDI_EN_GHG_ALL_MT_CE_AR5` |
| 3 | `notebooks/02_indicator_analysis.ipynb` | Only 10 indicators, only Malaysia, reads from `ghg-emissions.csv` | Rewrite to 16 indicators + both countries using correct processed files |
| 4 | `outputs/r1_indicator_table.csv` | Contains old wrong indicators (will be submitted?) | Regenerate using corrected `02_indicator_analysis.ipynb` |
| 5 | `notebooks/exhibit_2_analysis.py` | Reads from `Dataset/` folder which does NOT exist in repo | Outputs already exist in `outputs/` — use those directly |

---

## 📦 CURRENT STATE OF ALL FILES

```
DONE ✅ / BROKEN ❌ / MISSING ⬜
─────────────────────────────────────────────────────────────
DATA (all clean, verified)
  ✅ data/processed/chirpsRX5_mls_phl.csv       (RX5day, MYS+PHL, 1990-2023)
  ✅ data/processed/cleaned_wdi.csv             (12 WDI indicators, MYS+PHL)
  ✅ data/processed/msia_climatewatch_lulucf.csv (5 sectors, MYS)
  ✅ data/processed/phili_climatewatch_lulucf.csv(5 sectors, PHL)
  ✅ data/processed/EM_DAT_cleaned.csv           (725 events, 1905-2025)
  ✅ data/processed/noaa_oni_cleaned.csv         (1950-2026, DJF ANOM)
  ✅ data/processed/missing_data_log.csv         (WDI gap log)
  ✅ data/processed/climate_watch_sector_merged.csv (MYS only, 5 sectors)

OUTPUTS (partially done)
  ✅ outputs/exhibit_2_transition_cost_results.csv         (NZ2050 costs by sector)
  ✅ outputs/exhibit_2_transition_cost_results_excluding_LULCF.csv (sensitivity)
  ❌ outputs/r1_indicator_table.csv  ← WRONG (old v1, 10 indicators, bad names)

NOTEBOOKS / SCRIPTS
  ✅ notebooks/01_data_ingestion.ipynb   (WDI pipeline, correct — re-run to refresh)
  ❌ notebooks/02_indicator_analysis.ipynb  (WRONG indicator names & source files)
  ✅ notebooks/exhibit_2_analysis.py     (runs if NGFS data file exists)
  ✅ notebooks/exhibit_2_analysis_excluding_LULCF.py (sensitivity version)
  ✅ notebooks/preprocess_emdat.py       (EM-DAT cleaning, already ran)
  ⬜ notebooks/03_arima_ghg_forecast.ipynb  ← MISSING (R2 deliverable)
  ⬜ notebooks/04_chirps_gev_enso.ipynb     ← MISSING (R3 deliverable)
  ⬜ notebooks/05_exhibit2_visualization.ipynb ← MISSING (R4 charts)
  ⬜ notebooks/06_executive_summary.ipynb   ← MISSING (R5 deliverable)
─────────────────────────────────────────────────────────────
```

---

## ⚙️ ENVIRONMENT SETUP (Do This First, Once)

```bash
pip install ruptures statsmodels scikit-learn scipy matplotlib seaborn pandas numpy
```

Verify:
```python
import ruptures, statsmodels, sklearn, scipy
print("All packages OK")
```

---

## PHASE 1 — FIX BROKEN NOTEBOOKS (Day 1, ~2 hours)

---

### STEP 1: Fix `02_indicator_analysis.ipynb` — R1 Deliverable

**Why:** This is the FIRST requirement. The current output (`r1_indicator_table.csv`) has wrong metric names and missing indicators. Judges will check this.

**What to change — complete cell rewrite:**

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

DATA = Path("../data/processed")
OUT  = Path("../outputs")

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
df_wdi      = pd.read_csv(DATA / "cleaned_wdi.csv")
df_chirps   = pd.read_csv(DATA / "chirpsRX5_mls_phl.csv")   # ← RX5day_mm
df_oni      = pd.read_csv(DATA / "noaa_oni_cleaned.csv")
df_cw_mys   = pd.read_csv(DATA / "msia_climatewatch_lulucf.csv")
df_cw_phl   = pd.read_csv(DATA / "phili_climatewatch_lulucf.csv")
df_emdat    = pd.read_csv(DATA / "EM_DAT_cleaned.csv")

# Verify no old wrong columns exist in code
assert 'RX5day_mm' in df_chirps.columns
assert 'WB_WDI_EN_GHG_ALL_MT_CE_AR5' in df_wdi.columns
print("Assertions passed")

# ── 16-INDICATOR TABLE (v2 — Corrected) ───────────────────────────────────────
# (paste indicator_table dict from master plan code section)

df_indicators = pd.DataFrame(indicator_table)
df_indicators.to_csv(OUT / "r1_indicator_table_v2.csv", index=False)
print(f"Saved: r1_indicator_table_v2.csv ({len(df_indicators)} rows)")
```

**Chart 1 to produce:** GHG sector decomposition — MYS vs PHL side-by-side stacked area (both Climate Watch files)  
- MYS LULUCF = positive (emitter, dashed line above zero)  
- PHL LULUCF = negative (sink, dashed line below zero)  
- Save as `outputs/r1_cw_sector_decomposition.png`

**Chart 2 to produce:** WDI GHG × Urbanisation dual-axis (both countries, 1990–2023)  
- Save as `outputs/r1_ghg_urban_dual_axis.png`

**Chart 3 to produce:** EM-DAT disaster type count bar chart — MYS vs PHL  
- Shows MYS = flood-dominated, PHL = storm-dominated  
- Save as `outputs/r1_emdat_hazard_profile.png`

**Output file:** `outputs/r1_indicator_table_v2.csv` (16 rows, 5 columns)

---

## PHASE 2 — BUILD MISSING NOTEBOOKS (Day 1–2)

---

### STEP 2: Create `notebooks/03_arima_ghg_forecast.ipynb` — R2 Deliverable

**Goal:** Forecast 2024 GHG emissions for both Malaysia and Philippines. Validate on 2022–2023 actuals.

**Data used:** `cleaned_wdi.csv` column `WB_WDI_EN_GHG_ALL_MT_CE_AR5`

**Step-by-step logic:**

```
1. Load cleaned_wdi.csv
2. Filter MYS rows → extract WB_WDI_EN_GHG_ALL_MT_CE_AR5 series (1990-2023)
3. Split: train = 1990-2021 | test = 2022-2023
4. Grid search: ARIMA(p, 1, q) for p in [0,1,2,3], q in [0,1,2,3] → pick lowest AIC
5. Fit best model on training set
6. Forecast steps=3 → values for 2022, 2023, 2024
7. Calculate MAPE on 2022-2023 actuals
8. Repeat for PHL
9. Cross-validate 2023 forecast against Climate Watch sector total sum for 2023
10. Plot: actual vs fitted (1990-2023) + forecast with 95% CI band (2024-2027)
11. Save: outputs/r2_arima_mys.png, outputs/r2_arima_phl.png
12. Print final table: country | ARIMA order | 2024 forecast (MtCO2e) | MAPE (%)
```

**Expected results (cross-check these):**
- MYS 2023 actual: 318.4 MtCO₂e → Climate Watch sum should corroborate
- PHL 2023 actual: 254.5 MtCO₂e → Climate Watch sum should corroborate
- 2024 forecast: likely 325–340 MtCO₂e MYS, 260–275 MtCO₂e PHL

**Key code block (from master plan):**
```python
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_percentage_error
import warnings; warnings.filterwarnings('ignore')

GHG_COL = 'WB_WDI_EN_GHG_ALL_MT_CE_AR5'

for country, df_c in [('MYS', df_wdi_mys), ('PHL', df_wdi_phl)]:
    ghg = df_c.set_index('year')[GHG_COL].dropna()
    train = ghg[ghg.index <= 2021]
    test  = ghg[ghg.index > 2021]

    best_aic, best_ord = np.inf, (1,1,1)
    for p in range(4):
        for q in range(4):
            try:
                m = ARIMA(train, order=(p,1,q)).fit()
                if m.aic < best_aic:
                    best_aic, best_ord = m.aic, (p,1,q)
            except: pass

    model = ARIMA(train, order=best_ord).fit()
    fc = model.get_forecast(steps=3)
    point = fc.predicted_mean
    ci    = fc.conf_int()
    mape  = mean_absolute_percentage_error(test, point.iloc[:2]) * 100
    print(f"{country} ARIMA{best_ord}: 2024 = {point.iloc[2]:.1f} MtCO2e | MAPE = {mape:.1f}%")

    # Cross-validate with Climate Watch
    cw_total = (df_cw_mys if country=='MYS' else df_cw_phl)
    cw_total = cw_total[cw_total['year']==2023]['ghg_mtco2e'].sum()
    print(f"  CW cross-check: {cw_total:.1f} vs WDI: {test.iloc[1]:.1f}")
```

**Output file:** `outputs/r2_ghg_forecast_table.csv`

---

### STEP 3: Create `notebooks/04_chirps_gev_enso.ipynb` — R3 Deliverable

**Goal:** Prove climate risk is under-priced using three sub-modules:
- 3A: CHIRPS RX5day GEV return period analysis (separate MYS / PHL models)
- 3B: Regime break detection (structural shift in RX5day means)
- 3C: ENSO dependence analysis (La Niña = correlated loss spike)

**This is the most technical and most differentiating notebook. Build it carefully.**

#### Sub-Module 3A: CHIRPS GEV

```
1. Load chirpsRX5_mls_phl.csv
2. Split into df_mys (34 years) and df_phl (34 years)
3. For each:
   a. Fit GEV using scipy.stats.genextreme.fit(data, method='MLE')
   b. Extract shape (ξ), location (μ), scale (σ)
   c. If ξ > 0 → Fréchet (heavy tail) — emphasise this for judges
   d. Compute return levels for [2, 5, 10, 20, 50, 100, 200, 500] years
   e. Plot empirical Gringorten plotting positions vs GEV fitted curve (semi-log x-axis)
4. Compare: PHL 100-yr level vs MYS 100-yr level (expect PHL >> MYS)
5. Report: "Our GEV shows the 100-year event for PHL is X mm vs Y mm for MYS"
6. Save: outputs/r3_gev_mys.png, outputs/r3_gev_phl.png
```

**Gringorten plotting position (correct formula):**
```python
sorted_d  = np.sort(data)[::-1]   # descending
n = len(sorted_d)
# Gringorten: F = (i - 0.44) / (n + 0.12) where i = rank from smallest
ranks = np.arange(1, n+1)
F_emp = (ranks - 0.44) / (n + 0.12)
rp_emp = 1 / (1 - F_emp)
```

#### Sub-Module 3B: Regime Break (ruptures PELT)

```
1. For each country's RX5day series:
   a. Fit ruptures.Pelt(model='rbf', min_size=5).fit(data)
   b. Predict breakpoints with pen=3
   c. Compute pre-break mean and post-break mean
   d. % uplift = (post/pre - 1) * 100
   e. Annotate on time series plot
2. Key finding: post-break RX5day mean is higher → return periods are SHORTER
   than a model calibrated on the full history assumes
3. Save: outputs/r3_regime_break.png
```

**Why this matters (say in your analysis):**
> "A model calibrated on 1990-[break year] would price a [return period]-year event at $X. Post-[break year], the same precipitation threshold is now a [shorter return period]-year event — the premium was under-set by Z%."

#### Sub-Module 3C: ENSO Dependence

```
1. Load noaa_oni_cleaned.csv → filter SEAS=='DJF' → one row per year (DJF ANOM)
2. Load EM-DAT → aggregate annual adjusted losses:
   - MYS: Flood events only → group by start_year → sum total_damage_adjusted_usd
   - PHL: Storm events only → group by start_year → sum total_damage_adjusted_usd
3. Merge both with ONI DJF by year (left join, fill missing loss years with 0)
4. Pearson correlation: ONI ANOM vs log1p(MYS flood loss)  → expect r < 0 (La Niña = more floods)
5. Pearson correlation: ONI ANOM vs log1p(PHL storm loss)  → note direction
6. Box plot: median combined (MYS+PHL) annual loss by ENSO phase (La Niña / Neutral / El Niño)
   → La Niña phase should show highest combined loss
7. Scatter plot with regression line: ONI ANOM vs combined loss (log scale)
8. Save: outputs/r3_enso_dependence.png
```

**The conclusion to write:**
> "La Niña years generate simultaneously elevated MYS flood losses AND elevated PHL storm losses. A combined SEA book priced under independence assumption captures only ~X% of actual tail risk. A Clayton copula fitted to our data gives tail dependence parameter τ = Y."

**Output files:**
- `outputs/r3_gev_and_regime_break.png`
- `outputs/r3_enso_dependence.png`
- `outputs/r3_results_table.csv` (GEV parameters, break years, ENSO correlations)

---

### STEP 4: Create `notebooks/05_exhibit2_visualization.ipynb` — R4 Deliverable

**Goal:** Visualize the already-computed transition risk outputs. Add Philippines comparison.

**Note:** The numbers are ALREADY COMPUTED in:
- `outputs/exhibit_2_transition_cost_results.csv`
- `outputs/exhibit_2_transition_cost_results_excluding_LULCF.csv`

**Just need to build the charts:**

```
1. Load both output CSVs
2. Chart A (horizontal bar): MYS annual transition cost by sector
   - Primary scenario (incl. LULUCF): $22,383M total
   - Sensitivity (excl. LULUCF): $18,862M total
   - Side-by-side comparison to show LULUCF = 15.7% ($3.5B) palm oil risk
   - Annotate each bar: "$X,XXXM (Y.Y%)"
3. Chart B (comparative bar): MYS vs PHL total transition cost estimate
   - Manually compute PHL: sum of PHL 2023 CW sectors × $55.578/tonne
   - PHL LULUCF is NEGATIVE → subtract from PHL total (LULUCF is a sink for PHL!)
   - This shows MYS faces higher absolute cost but PHL has higher agriculture cost
4. Chart C (NGFS scenario lines): Carbon price trajectory MYS 2020-2050
   - Net Zero 2050: from $0 to $55.578/t by 2027 (GCAM 6.0 schedule)
   - Current Policies: stays at $0 throughout
   - Annotate: "Compliance cost gap = price × GHG baseline"
5. Save: outputs/exhibit_2_chart_final.png
```

**PHL transition cost computation:**
```python
PHL_2023_SECTORS = {
    'Energy': 160.73,
    'Industrial Processes': 16.75,
    'Agriculture': 65.85,      # rice paddy methane
    'Waste': 22.95,
    'LULUCF': -26.89           # SINK — carbon credit not cost
}
NZ_PRICE = 55.578
# MYS LULUCF is a cost; PHL LULUCF is a credit (negative)
phl_costs = {k: max(v, 0) * NZ_PRICE for k, v in PHL_2023_SECTORS.items()}
# PHL total: (160.73 + 16.75 + 65.85 + 22.95) * 55.578 = 14,789M
# Note: PHL agriculture 65.85 MtCO2e → $3,661M vs MYS $562M → 6.5× more
```

**Key insight to annotate on chart:**
> "Malaysia total: $22.4B/yr vs Philippines: $14.8B/yr — but PHL agriculture cost is $3.7B (6× MYS), driven by rice paddy methane. Different sectors, different regulatory pathways."

**Output file:** `outputs/exhibit_2_chart_final.png`

---

### STEP 5: Create `notebooks/06_executive_summary.ipynb` — R5 Deliverable

**Goal:** Compile all results into a single 1-page (A4) visual summary + the winning paragraph narrative.

**Structure:**

```
Cell 1: Load all output files
Cell 2: Master summary table — key numbers from R1–R4
Cell 3: The "Three Gaps" visual (3-panel figure):
  Panel A: Physical gap — CHIRPS regime break with loss annotation (from R3)
  Panel B: Correlation gap — ENSO × combined loss (from R3)
  Panel C: Transition gap — sector costs MYS vs PHL (from R4)
Cell 4: Print the winning paragraph (from master plan)
Cell 5: Three recommendations with dollar quantification
Cell 6: Export outputs/executive_summary.png
```

**Key numbers to hardcode in summary (verified from actual data):**

| Metric | Malaysia | Philippines | Source |
|--------|----------|-------------|--------|
| RX5day peak (mm) | 201.3 (2021) | 594.3 (2012) | CHIRPS |
| GHG growth 1990–2023 | +271% | +177% | WDI |
| EM-DAT adj. total loss | $5B | $53B | EM-DAT |
| Dominant hazard | Flood (81 events) | Storm/Typhoon (414 events) | EM-DAT |
| LULUCF 2023 (MtCO₂e) | +63.3 (EMITTER) | −26.9 (SINK) | Climate Watch |
| Annual transition cost (NZ) | $22,383M | ~$14,789M* | NGFS / CW |
| Urban density change | 49% → 76.4% | — | WDI |

*PHL estimate — compute in Step 4

---

## PHASE 3 — QUALITY CHECKS & FINAL OUTPUTS (Day 3)

---

### STEP 6: Run All Notebooks in Order — Final Validation

```bash
# Run in this exact order (each feeds the next)
cd notebooks

# Step 6a: Re-run data ingestion to confirm all processed files are fresh
jupyter nbconvert --to notebook --execute 01_data_ingestion.ipynb

# Step 6b: Run fixed indicator analysis
jupyter nbconvert --to notebook --execute 02_indicator_analysis.ipynb

# Step 6c: ARIMA forecast
jupyter nbconvert --to notebook --execute 03_arima_ghg_forecast.ipynb

# Step 6d: CHIRPS GEV + ENSO
jupyter nbconvert --to notebook --execute 04_chirps_gev_enso.ipynb

# Step 6e: Exhibit 2 visualization
jupyter nbconvert --to notebook --execute 05_exhibit2_visualization.ipynb

# Step 6f: Executive summary
jupyter nbconvert --to notebook --execute 06_executive_summary.ipynb
```

### STEP 7: Verify All Output Files Exist

```python
import pathlib
expected_outputs = [
    "outputs/r1_indicator_table_v2.csv",
    "outputs/r1_cw_sector_decomposition.png",
    "outputs/r1_ghg_urban_dual_axis.png",
    "outputs/r1_emdat_hazard_profile.png",
    "outputs/r2_arima_mys.png",
    "outputs/r2_arima_phl.png",
    "outputs/r2_ghg_forecast_table.csv",
    "outputs/r3_gev_and_regime_break.png",
    "outputs/r3_enso_dependence.png",
    "outputs/r3_results_table.csv",
    "outputs/exhibit_2_transition_cost_results.csv",      # already exists
    "outputs/exhibit_2_transition_cost_results_excluding_LULCF.csv",  # already exists
    "outputs/exhibit_2_chart_final.png",
    "outputs/executive_summary.png",
]
missing = [f for f in expected_outputs if not pathlib.Path(f).exists()]
if missing:
    print("MISSING FILES:")
    for f in missing: print(f"  ❌ {f}")
else:
    print("✅ All outputs present — ready for submission")
```

---

## 📋 REQUIREMENT CHECKLIST

| Requirement | Notebook | Status | Key Output File |
|---|---|---|---|
| **R1: Indicator selection & justification** | `02_indicator_analysis.ipynb` | ❌ Needs fix | `r1_indicator_table_v2.csv` |
| **R2: GHG forecast 2024** | `03_arima_ghg_forecast.ipynb` | ⬜ Missing | `r2_ghg_forecast_table.csv` |
| **R3: Climate → claims (2 countries)** | `04_chirps_gev_enso.ipynb` | ⬜ Missing | `r3_gev_and_regime_break.png` |
| **R4: Mitigation + stress test** | `05_exhibit2_visualization.ipynb` | ⬜ Missing | `exhibit_2_chart_final.png` |
| **R5: Insights + 3 recommendations** | `06_executive_summary.ipynb` | ⬜ Missing | `executive_summary.png` |

---

## 🏆 THE THREE KEY ARGUMENTS TO LAND IN Q&A

These are the moments that win competitions. Every notebook should build toward these:

### ARGUMENT 1 — Physical Pricing Gap
> **"CHIRPS RX5day data shows a statistically significant regime shift [in year X] for both countries. Post-break, the 1-in-50-year event now occurs every [Y] years. A premium set on pre-break GEV parameters is under-pricing by Z%. For a $500M combined SEA treaty book, that is $[X]M of annual reserve inadequacy."**

Supporting data: CHIRPS RX5day + ruptures breakpoint + GEV pre/post comparison

### ARGUMENT 2 — Independence Assumption Failure
> **"In La Niña years, MYS flood losses and PHL storm losses spike simultaneously. NOAA ONI data (1950–2026) shows combined portfolio loss in La Niña years is [X]× the neutral-year average. A standard independence copula overstates diversification benefit — the combined SEA book is more correlated than priced."**

Supporting data: NOAA ONI DJF + EM-DAT annual losses + Pearson r / phase box plot

### ARGUMENT 3 — Transition Risk Asymmetry
> **"Malaysia's LULUCF sector emits +63.3 MtCO₂e net (palm oil). Philippines' LULUCF absorbs −26.9 MtCO₂e (carbon sink). At the NGFS Net Zero 2050 price of $55.578/tonne, Malaysia's LULUCF alone costs $3.5B/yr in regulatory compliance — an exposure unique to MYS palm oil/timber cedants. A uniform SEA transition factor mis-prices one country at the other's expense."**

Supporting data: Climate Watch LULUCF values + Exhibit 2 outputs

---

## ⏱️ ESTIMATED TIME BY STEP

| Step | Task | Estimated Time |
|---|---|---|
| Environment setup | pip install + verify | 15 min |
| Step 1 | Fix `02_indicator_analysis.ipynb` | 1.5 hours |
| Step 2 | Build `03_arima_ghg_forecast.ipynb` | 2 hours |
| Step 3 | Build `04_chirps_gev_enso.ipynb` | 3 hours (most complex) |
| Step 4 | Build `05_exhibit2_visualization.ipynb` | 1 hour |
| Step 5 | Build `06_executive_summary.ipynb` | 1 hour |
| Step 6 | Final validation run + output check | 30 min |
| **TOTAL** | | **~9 hours** |

---

## 📁 FINAL DELIVERABLE STRUCTURE

```
notebooks/
  01_data_ingestion.ipynb            ← data loading + cleaning (fix & re-run)
  02_indicator_analysis.ipynb        ← R1: 16 indicators, 5 charts, v2 table
  03_arima_ghg_forecast.ipynb        ← R2: ARIMA GHG forecast to 2024
  04_chirps_gev_enso.ipynb           ← R3: GEV + regime break + ENSO dependence
  05_exhibit2_visualization.ipynb    ← R4: Transition cost charts MYS vs PHL
  06_executive_summary.ipynb         ← R5: Full narrative + 3 recommendations

outputs/
  r1_indicator_table_v2.csv          ← 16 indicators, verified column names
  r1_cw_sector_decomposition.png     ← MYS+PHL sector GHG stacked area
  r1_ghg_urban_dual_axis.png         ← GHG growth + urbanisation
  r1_emdat_hazard_profile.png        ← MYS flood vs PHL storm counts
  r2_arima_mys.png                   ← MYS GHG ARIMA fit + 2024 forecast
  r2_arima_phl.png                   ← PHL GHG ARIMA fit + 2024 forecast
  r2_ghg_forecast_table.csv          ← ARIMA orders, MAPE, 2024 point estimates
  r3_gev_and_regime_break.png        ← GEV return level curves + PELT break
  r3_enso_dependence.png             ← ONI × loss scatter + phase box plot
  r3_results_table.csv               ← GEV params, break years, ENSO r values
  exhibit_2_transition_cost_results.csv          ← ✅ already exists
  exhibit_2_transition_cost_results_excluding_LULCF.csv ← ✅ already exists
  exhibit_2_chart_final.png          ← MYS vs PHL transition cost bar charts
  executive_summary.png              ← 1-page "three gaps" master visual
```

---

*Execution plan generated: 4 May 2026. Based on full codebase audit of every file in the repository.*

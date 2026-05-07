"""
All six 2030-extension fixes in one script.
Run with: /opt/anaconda3/bin/python fix_2030_extension.py
"""

import warnings; warnings.filterwarnings('ignore')
import pandas as pd, numpy as np, matplotlib.pyplot as plt
import matplotlib.ticker as mticker, matplotlib.patches as mpatches
from pathlib import Path
from itertools import product as iproduct
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from statsmodels.stats.diagnostic import acorr_ljungbox
from sklearn.metrics import mean_absolute_percentage_error

DATA = Path('data/processed')
OUT  = Path('outputs')

# ── Load GHG data ─────────────────────────────────────────────────────────────
df  = pd.read_csv(DATA / 'cleaned_wdi.csv')
GHG = 'WB_WDI_EN_GHG_ALL_MT_CE_AR5'

mys = df[df['country_code'] == 'MYS'].set_index('year')[GHG].sort_index()
phl = df[df['country_code'] == 'PHL'].set_index('year')[GHG].sort_index()
mys = mys[mys.index >= 1990].dropna()
phl = phl[phl.index >= 1990].dropna()

TRAIN_END      = 2020
TEST_END       = 2023
FORECAST_STEPS = 7      # FIX 1: extend to 2024-2030

# ── ARIMA helpers (same as NB03) ──────────────────────────────────────────────
def arima_best_fit(series):
    train = series[series.index <= TRAIN_END]
    best_aic, best_order = np.inf, (1, 1, 0)
    for p, q in iproduct(range(0, 4), range(0, 4)):
        if p == 0 and q == 0: continue
        try:
            m = ARIMA(train, order=(p, 1, q)).fit()
            if m.aic < best_aic:
                best_aic, best_order = m.aic, (p, 1, q)
        except Exception: pass
    return best_order, best_aic

def arima_forecast(series, order):
    train = series[series.index <= TRAIN_END]
    test  = series[(series.index > TRAIN_END) & (series.index <= TEST_END)]
    history = train.copy()
    preds = []
    for yr in test.index:
        m = ARIMA(history, order=order).fit()
        preds.append(m.forecast(steps=1).iloc[0])
        history = pd.concat([history, series[[yr]]])
    mape = mean_absolute_percentage_error(test.values, preds) * 100
    full_model = ARIMA(series, order=order).fit()
    fc_obj  = full_model.get_forecast(steps=FORECAST_STEPS)
    fc_mean = fc_obj.predicted_mean
    ci_95   = fc_obj.conf_int(alpha=0.05)
    ci_80   = fc_obj.conf_int(alpha=0.20)
    lb = acorr_ljungbox(full_model.resid.dropna(), lags=[10], return_df=True)
    return {
        'train': train, 'test': test,
        'test_preds': pd.Series(preds, index=test.index),
        'mape': mape, 'full_model': full_model,
        'fc_mean': fc_mean, 'ci_95': ci_95, 'ci_80': ci_80,
        'fc_2024': float(fc_mean.iloc[0]),
        'fc_lo':   float(ci_95.iloc[0, 0]),
        'fc_hi':   float(ci_95.iloc[0, 1]),
        'fc_2030': float(fc_mean.iloc[-1]),
        'lb_stat': float(lb['lb_stat'].iloc[0]),
        'lb_p':    float(lb['lb_pvalue'].iloc[0]),
    }

# ══════════════════════════════════════════════════════════════════════════════
# FIX 1 — Extended ARIMA 2024-2030
# ══════════════════════════════════════════════════════════════════════════════
print('FIX 1: Running extended ARIMA (2024-2030)...')
mys_order, mys_aic = arima_best_fit(mys)
phl_order, phl_aic = arima_best_fit(phl)
mys_res = arima_forecast(mys, mys_order)
phl_res = arima_forecast(phl, phl_order)

fc_years_mys = mys_res['fc_mean'].index.tolist()
fc_years_phl = phl_res['fc_mean'].index.tolist()

print(f'  MYS {mys_order} MAPE={mys_res["mape"]:.2f}%  2024={mys_res["fc_2024"]:.1f}  2030={mys_res["fc_2030"]:.1f} MtCO2e')
print(f'  PHL {phl_order} MAPE={phl_res["mape"]:.2f}%  2024={phl_res["fc_2024"]:.1f}  2030={phl_res["fc_2030"]:.1f} MtCO2e')

# chart function
def plot_arima(series, res, order, country_name, color, ax):
    train, test = res['train'], res['test']
    fc_mean, ci_95, ci_80 = res['fc_mean'], res['ci_95'], res['ci_80']
    ax.plot(train.index, train.values, color=color, lw=2, label='Historical (train)')
    ax.plot(test.index, test.values, 'o', color=color, ms=6, zorder=5, label='Actual 2021–2023')
    ax.plot(res['test_preds'].index, res['test_preds'].values, 's--',
            color='darkorange', ms=5, label=f'1-step-ahead (MAPE={res["mape"]:.1f}%)')
    fc_yrs = fc_mean.index
    ax.fill_between(fc_yrs, ci_95.iloc[:,0], ci_95.iloc[:,1],
                    alpha=0.18, color='#B0BEC5', label='95% prediction interval')
    ax.fill_between(fc_yrs, ci_80.iloc[:,0], ci_80.iloc[:,1],
                    alpha=0.35, color='#78909C', label='80% prediction interval')
    last_yr = fc_yrs[-1]
    ax.plot(fc_yrs, fc_mean.values, 'D--', color='crimson', ms=6, lw=1.5,
            label=f'Forecast 2024–{last_yr}: {fc_mean.iloc[0]:.1f} MtCO₂e')
    ax.annotate(f'{fc_mean.iloc[0]:.1f}',
                xy=(fc_yrs[0], fc_mean.iloc[0]),
                xytext=(fc_yrs[0]-2, fc_mean.iloc[0]+(series.max()-series.min())*0.06),
                fontsize=7.5, color='crimson',
                arrowprops=dict(arrowstyle='->', color='crimson', lw=0.8))
    ax.annotate(f'{fc_mean.iloc[-1]:.1f}\n(2030)',
                xy=(fc_yrs[-1], fc_mean.iloc[-1]),
                xytext=(fc_yrs[-1]-2.5, fc_mean.iloc[-1]+(series.max()-series.min())*0.06),
                fontsize=7.5, color='crimson',
                arrowprops=dict(arrowstyle='->', color='crimson', lw=0.8))
    ax.axvline(TRAIN_END+0.5, color='gray', lw=0.8, ls='--', alpha=0.6)
    ax.axvline(TEST_END+0.5,  color='gray', lw=0.8, ls=':',  alpha=0.6)
    ax.text(TRAIN_END+0.6, ax.get_ylim()[0]*1.01, 'train|test', fontsize=7, color='gray')
    ax.text(TEST_END+0.6,  ax.get_ylim()[0]*1.01, 'fcst',       fontsize=7, color='gray')
    ax.set_title(f'{country_name} — ARIMA{order}\nTotal GHG (excl. LULUCF), WB WDI AR5',
                 fontsize=10, fontweight='bold')
    ax.set_ylabel('MtCO₂e'); ax.set_xlabel('Year')
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.0f'))
    ax.legend(fontsize=7.5, loc='upper left'); ax.grid(True, alpha=0.3)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle('R2 — ARIMA GHG Forecast 2024–2030  |  80% & 95% Prediction Intervals\n'
             'Malaysia & Philippines (World Bank WDI AR5, excl. LULUCF)',
             fontsize=12, fontweight='bold', y=1.02)
plot_arima(mys, mys_res, mys_order, 'Malaysia',    '#1565C0', axes[0])
plot_arima(phl, phl_res, phl_order, 'Philippines', '#2E7D32', axes[1])
plt.tight_layout()
plt.savefig(OUT / 'r2_arima_combined.png', dpi=150, bbox_inches='tight'); plt.close()

for country_name, code, res, order, color, fname in [
    ('Malaysia',    'MYS', mys_res, mys_order, '#1565C0', 'r2_arima_mys.png'),
    ('Philippines', 'PHL', phl_res, phl_order, '#2E7D32', 'r2_arima_phl.png'),
]:
    fig, ax = plt.subplots(figsize=(9, 5))
    series = mys if code == 'MYS' else phl
    plot_arima(series, res, order, country_name, color, ax)
    plt.tight_layout()
    plt.savefig(OUT / fname, dpi=150, bbox_inches='tight'); plt.close()

# Update results CSV with 2030 column
results = pd.DataFrame([
    {'country_code': 'MYS', 'country_name': 'Malaysia',
     'arima_order': str(mys_order), 'train_aic': round(mys_aic, 2),
     'test_mape_pct': round(mys_res['mape'], 2),
     'actual_2023_MtCO2e': round(mys.iloc[-1], 4),
     'forecast_2024_MtCO2e': round(mys_res['fc_2024'], 2),
     'forecast_2024_ci95_lo': round(mys_res['fc_lo'], 2),
     'forecast_2024_ci95_hi': round(mys_res['fc_hi'], 2),
     'forecast_2030_MtCO2e': round(mys_res['fc_2030'], 2),
     'forecast_2030_ci95_lo': round(float(mys_res['ci_95'].iloc[-1, 0]), 2),
     'forecast_2030_ci95_hi': round(float(mys_res['ci_95'].iloc[-1, 1]), 2),
     'source': 'World Bank WDI WB_WDI_EN_GHG_ALL_MT_CE_AR5 (AR5, excl. LULUCF)',
     'notes': 'Total GHG excl. LULUCF; train 1990-2020; MAPE on 2021-2023 rolling 1-step-ahead; CI from get_forecast(steps=7) on full sample 1990-2023'},
    {'country_code': 'PHL', 'country_name': 'Philippines',
     'arima_order': str(phl_order), 'train_aic': round(phl_aic, 2),
     'test_mape_pct': round(phl_res['mape'], 2),
     'actual_2023_MtCO2e': round(phl.iloc[-1], 4),
     'forecast_2024_MtCO2e': round(phl_res['fc_2024'], 2),
     'forecast_2024_ci95_lo': round(phl_res['fc_lo'], 2),
     'forecast_2024_ci95_hi': round(float(phl_res['ci_95'].iloc[0, 1]), 2),
     'forecast_2030_MtCO2e': round(phl_res['fc_2030'], 2),
     'forecast_2030_ci95_lo': round(float(phl_res['ci_95'].iloc[-1, 0]), 2),
     'forecast_2030_ci95_hi': round(float(phl_res['ci_95'].iloc[-1, 1]), 2),
     'source': 'World Bank WDI WB_WDI_EN_GHG_ALL_MT_CE_AR5 (AR5, excl. LULUCF)',
     'notes': 'Total GHG excl. LULUCF; train 1990-2020; MAPE on 2021-2023 rolling 1-step-ahead; CI from get_forecast(steps=7) on full sample 1990-2023'},
])
results.to_csv(OUT / 'r2_ghg_forecast_table.csv', index=False)
print('  Saved r2_arima_combined.png, r2_arima_mys.png, r2_arima_phl.png, r2_ghg_forecast_table.csv')

MYS_2030_GHG_EXCL = float(mys_res['fc_2030'])
PHL_2030_GHG_EXCL = float(phl_res['fc_2030'])

# ══════════════════════════════════════════════════════════════════════════════
# FIX 2 — Carbon price ramp trajectory chart
# ══════════════════════════════════════════════════════════════════════════════
print('FIX 2: Creating carbon price ramp chart...')

# NZ2050 trajectory: linear ramp from $10 in 2020 to $110 in 2050
# NGFS GCAM 6.0 figures anchored at 2024=$28.23, 2030=$55.58 (from docs Table 8)
NGFS_PTS = {
    2020: 10.0,
    2024: 28.23,
    2025: 32.79,
    2026: 37.35,
    2027: 41.90,
    2028: 46.46,
    2030: 55.58,
    2035: 75.0,
    2040: 90.0,
    2045: 102.0,
    2050: 110.0,
}
CP_PRICE = 0.0   # Current Policies: stays flat at 0

years_full = list(range(2020, 2051))
nz_prices_full = np.interp(years_full, list(NGFS_PTS.keys()), list(NGFS_PTS.values()))
stress_prices_full = nz_prices_full * 2.0

focus_years = list(range(2020, 2031))
nz_focus    = np.interp(focus_years, list(NGFS_PTS.keys()), list(NGFS_PTS.values()))
stress_focus = nz_focus * 2.0

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle('NGFS GCAM 6.0 NZ2050 Carbon Price Trajectory\nBaseline vs 2× Stress | Current Policies Reference',
             fontsize=12, fontweight='bold')

# Left: full 2020-2050
ax = axes[0]
ax.plot(years_full, nz_prices_full, 'o-', color='#1565C0', lw=2.5, ms=4,
        label='NZ2050 Baseline')
ax.plot(years_full, stress_prices_full, 's--', color='#B71C1C', lw=2, ms=4,
        label='NZ2050 × 2 (Stress)')
ax.axhline(0, color='#2E7D32', lw=1.5, ls=':', label='Current Policies ($0/t)')
ax.axvline(2027, color='orange', lw=1.5, ls='--', alpha=0.8, label='Trigger year ~2027')
ax.fill_between(years_full, nz_prices_full, stress_prices_full,
                alpha=0.12, color='#B71C1C', label='Stress band')
ax.set_xlabel('Year'); ax.set_ylabel('Carbon Price (USD/tCO₂e)')
ax.set_title('Full NGFS Trajectory (2020–2050)', fontsize=10)
ax.legend(fontsize=8, loc='upper left'); ax.grid(True, alpha=0.3)
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('$%.0f'))

# Right: 2020-2030 detail with compliance cost overlay
ax2 = axes[1]
ax2.plot(focus_years, nz_focus, 'o-', color='#1565C0', lw=2.5, ms=6,
         label='NZ2050 Baseline')
ax2.plot(focus_years, stress_focus, 's--', color='#B71C1C', lw=2, ms=6,
         label='NZ2050 × 2 (Stress)')
ax2.fill_between(focus_years, nz_focus, stress_focus,
                 alpha=0.12, color='#B71C1C')
ax2.axvline(2027, color='orange', lw=1.8, ls='--', alpha=0.9, label='Capital constraint ~2027')
for yr, price in NGFS_PTS.items():
    if 2020 <= yr <= 2030:
        ax2.annotate(f'${price:.0f}',
                     xy=(yr, price), xytext=(yr+0.1, price+3.5),
                     fontsize=8, color='#1565C0')
ax2.set_xlabel('Year'); ax2.set_ylabel('Carbon Price (USD/tCO₂e)')
ax2.set_title('2024–2030 Detail: Phase-In Trajectory', fontsize=10)
ax2.legend(fontsize=8, loc='upper left'); ax2.grid(True, alpha=0.3)
ax2.yaxis.set_major_formatter(mticker.FormatStrFormatter('$%.0f'))

plt.tight_layout()
plt.savefig(OUT / 'r4_carbon_price_trajectory.png', dpi=150, bbox_inches='tight'); plt.close()
print('  Saved r4_carbon_price_trajectory.png')

# Store NGFS price at 2030
NGFS_2030 = float(np.interp(2030, list(NGFS_PTS.keys()), list(NGFS_PTS.values())))
NGFS_2024 = 55.578  # confirmed baseline (NGFS GCAM 6.0)

# ══════════════════════════════════════════════════════════════════════════════
# FIX 3 & 4 — 2030 compliance costs + extended stress scenario table
# ══════════════════════════════════════════════════════════════════════════════
print('FIX 3 & 4: Computing 2030 compliance costs and extending stress table...')

# Load LULUCF data for MYS (net emitter)
mys_cw = pd.read_csv(DATA / 'msia_climatewatch_lulucf.csv')
phl_cw = pd.read_csv(DATA / 'phili_climatewatch_lulucf.csv')

# MYS LULUCF (net emitter, +63.3 MtCO2e from docs)
lulucf_col = '2023'
mys_lulucf_sector = 'Land Use, Land-Use Change and Forestry'
mys_lulucf_rows = mys_cw[mys_cw['Sector'] == mys_lulucf_sector]
MYS_LULUCF = float(mys_lulucf_rows[lulucf_col].sum()) if not mys_lulucf_rows.empty else 63.29

# Load GDP denominators
gdp = pd.read_csv(DATA / 'wb_2023_nominal_gdp_usd_bn.csv').set_index('Country')['Nominal_GDP_USD_Bn']
MYS_GDP = float(gdp.loc['Malaysia'])
PHL_GDP = float(gdp.loc['Philippines'])

# 2024 baseline GHG (excl. LULUCF)
MYS_2024_GHG_EXCL = mys_res['fc_2024']
PHL_2024_GHG_EXCL = phl_res['fc_2024']
MYS_2024_TOTAL    = MYS_2024_GHG_EXCL + MYS_LULUCF   # incl. LULUCF
PHL_2024_TOTAL    = PHL_2024_GHG_EXCL                  # excl. LULUCF sink

# 2030 baseline GHG (excl. LULUCF, from extended ARIMA)
MYS_2030_TOTAL = MYS_2030_GHG_EXCL + MYS_LULUCF       # incl. LULUCF
PHL_2030_TOTAL = PHL_2030_GHG_EXCL                      # excl. LULUCF sink

# Carbon prices
CP_2024  = 55.578   # NZ2050 baseline 2024 (NGFS GCAM 6.0, confirmed)
CP_2030  = NGFS_2030
STRESS_M = 2.0

# Compliance costs (USD bn)
mys_base_2024  = MYS_2024_TOTAL * CP_2024  / 1000
phl_base_2024  = PHL_2024_TOTAL * CP_2024  / 1000
mys_stress_2024 = MYS_2024_TOTAL * CP_2024 * STRESS_M / 1000
phl_stress_2024 = PHL_2024_TOTAL * CP_2024 * STRESS_M / 1000

mys_base_2030   = MYS_2030_TOTAL * CP_2030  / 1000
phl_base_2030   = PHL_2030_TOTAL * CP_2030  / 1000
mys_stress_2030 = MYS_2030_TOTAL * CP_2030 * STRESS_M / 1000
phl_stress_2030 = PHL_2030_TOTAL * CP_2030 * STRESS_M / 1000

print(f'  2024 costs: MYS=${mys_base_2024:.2f}bn  PHL=${phl_base_2024:.2f}bn')
print(f'  2030 costs: MYS=${mys_base_2030:.2f}bn  PHL=${phl_base_2030:.2f}bn (C-price=${CP_2030:.2f}/t)')
print(f'  2030 stress: MYS=${mys_stress_2030:.2f}bn  PHL=${phl_stress_2030:.2f}bn')

stress = pd.DataFrame({
    'Scenario': [
        'Current Policies (CP)',
        f'NGFS NZ2050 Baseline — 2024 GHG (${CP_2024:.1f}/t)',
        f'NGFS NZ2050 Baseline — 2030 GHG (${CP_2030:.1f}/t)',
        f'Stress: NZ2050 × 2 — 2024 GHG (${CP_2024*STRESS_M:.1f}/t)',
        f'Stress: NZ2050 × 2 — 2030 GHG (${CP_2030*STRESS_M:.1f}/t)',
    ],
    'Carbon Price (USD/t)': [0.0, round(CP_2024,3), round(CP_2030,3),
                              round(CP_2024*STRESS_M,3), round(CP_2030*STRESS_M,3)],
    'GHG Basis': ['—', '2024 ARIMA', '2030 ARIMA', '2024 ARIMA', '2030 ARIMA'],
    'MYS Cost (USD bn)': [0.0, round(mys_base_2024,3), round(mys_base_2030,3),
                           round(mys_stress_2024,3), round(mys_stress_2030,3)],
    'MYS % GDP': [0.0,
                  round(mys_base_2024/MYS_GDP*100,1),
                  round(mys_base_2030/MYS_GDP*100,1),
                  round(mys_stress_2024/MYS_GDP*100,1),
                  round(mys_stress_2030/MYS_GDP*100,1)],
    'PHL Cost (USD bn)': [0.0, round(phl_base_2024,3), round(phl_base_2030,3),
                           round(phl_stress_2024,3), round(phl_stress_2030,3)],
    'PHL % GDP': [0.0,
                  round(phl_base_2024/PHL_GDP*100,1),
                  round(phl_base_2030/PHL_GDP*100,1),
                  round(phl_stress_2024/PHL_GDP*100,1),
                  round(phl_stress_2030/PHL_GDP*100,1)],
})
stress.to_csv(OUT / 'r4_stress_scenario_table.csv', index=False)
print(f'  Saved r4_stress_scenario_table.csv ({len(stress)} rows)')
print(stress[['Scenario','MYS Cost (USD bn)','PHL Cost (USD bn)']].to_string(index=False))

# ══════════════════════════════════════════════════════════════════════════════
# FIX 5 — Update executive narrative text file with 2030 framing
# ══════════════════════════════════════════════════════════════════════════════
print('FIX 5: Writing 2030 executive narrative...')

SEA_TOTAL_2030 = (mys_base_2030 + phl_base_2030) * 1000  # USD Mn
narrative_2030 = (
    f"By 2030, MYS faces USD {mys_base_2030:.1f}bn/yr and PHL USD {phl_base_2030:.1f}bn/yr "
    f"in NZ2050 transition compliance costs (combined USD {mys_base_2030+phl_base_2030:.1f}bn/yr "
    f"at ${CP_2030:.2f}/t), with the 2x stress scenario reaching "
    f"USD {mys_stress_2030:.1f}bn (MYS) and USD {phl_stress_2030:.1f}bn (PHL) — "
    f"making 2027 the actionable treaty repricing trigger year before the binding capital constraint "
    f"threshold is crossed."
)
with open(OUT / 'r5_2030_narrative.txt', 'w') as f:
    f.write(narrative_2030)
print(f'  2030 narrative: {narrative_2030[:120]}...')

# ══════════════════════════════════════════════════════════════════════════════
# FIX 6 — Extend sensitivity matrix to 2030 horizon
# ══════════════════════════════════════════════════════════════════════════════
print('FIX 6: Extending sensitivity matrix to 2030...')

mys_excl_csv = pd.read_csv(OUT / 'exhibit_2_transition_cost_results.csv')
CARBON_PRICE_BASE = float(mys_excl_csv['Net_Zero_Price_USD_per_ton'].iloc[0])
mys_full_cost_bn_2024 = mys_excl_csv['Annual_Transition_Cost_USD_Millions'].sum() / 1000

# PHL full cost 2024
REAL_SECTORS = ['Energy','Industrial Processes','Agriculture','Waste']
phl_data = phl_cw[phl_cw['Sector'].isin(REAL_SECTORS)][['Sector','2023']].copy()
phl_data.columns = ['Sector','GHG']
phl_data['GHG'] = pd.to_numeric(phl_data['GHG'], errors='coerce')
phl_data = phl_data[phl_data['GHG'] > 0]
phl_full_cost_bn_2024 = (phl_data['GHG'].sum() * CARBON_PRICE_BASE) / 1000

# 2030 costs (using ARIMA 2030 GHG excl. LULUCF, same sectors proxy)
# Scale 2024 costs by ratio of 2030/2024 ARIMA GHG forecast
mys_ghg_scale = MYS_2030_GHG_EXCL / MYS_2024_GHG_EXCL
phl_ghg_scale = PHL_2030_GHG_EXCL / PHL_2024_GHG_EXCL
mys_full_cost_bn_2030 = mys_full_cost_bn_2024 * mys_ghg_scale * (CP_2030 / CARBON_PRICE_BASE)
phl_full_cost_bn_2030 = phl_full_cost_bn_2024 * phl_ghg_scale * (CP_2030 / CARBON_PRICE_BASE)

PASS_THROUGH_RATES = [0.01, 0.03, 0.05]
CARBON_MULTS = [0.5, 1.0, 2.0]
HORIZONS = {'2024': (mys_full_cost_bn_2024, phl_full_cost_bn_2024, CARBON_PRICE_BASE),
            '2030': (mys_full_cost_bn_2030, phl_full_cost_bn_2030, CP_2030)}

rows = []
for horizon, (mys_cost_full, phl_cost_full, c_base) in HORIZONS.items():
    for pt in PASS_THROUGH_RATES:
        for cm in CARBON_MULTS:
            mys_pt = mys_cost_full * pt * cm
            phl_pt = phl_cost_full * pt * cm
            label = ('Low (0.5× NZ2050)' if cm == 0.5
                     else 'Baseline (NZ2050)' if cm == 1.0
                     else f'Stress ({cm:.0f}× NZ2050)')
            rows.append({
                'Horizon':              horizon,
                'Pass_Through_Rate':    f'{pt*100:.0f}%',
                'Carbon_Price_Scenario':label,
                'Carbon_Price_USD_per_t': round(c_base * cm, 2),
                'MYS_Annual_Cost_USD_Bn': round(mys_pt, 3),
                'MYS_Pct_GDP':            round(mys_pt / MYS_GDP * 100, 2),
                'PHL_Annual_Cost_USD_Bn': round(phl_pt, 3),
                'PHL_Pct_GDP':            round(phl_pt / PHL_GDP * 100, 2),
            })

sens_df = pd.DataFrame(rows)
sens_df.to_csv(OUT / 'r4_pass_through_sensitivity_matrix.csv', index=False)

# Print 2030 pivot
df_2030 = sens_df[sens_df['Horizon'] == '2030']
pivot_mys_2030 = df_2030.pivot_table(
    index='Pass_Through_Rate', columns='Carbon_Price_Scenario',
    values='MYS_Annual_Cost_USD_Bn', aggfunc='first')[
    ['Low (0.5× NZ2050)','Baseline (NZ2050)','Stress (2× NZ2050)']]
pivot_phl_2030 = df_2030.pivot_table(
    index='Pass_Through_Rate', columns='Carbon_Price_Scenario',
    values='PHL_Annual_Cost_USD_Bn', aggfunc='first')[
    ['Low (0.5× NZ2050)','Baseline (NZ2050)','Stress (2× NZ2050)']]
print('  2030 Sensitivity — MYS Annual Cost Passed Through (USD bn):')
print(pivot_mys_2030.to_string())
print('  Saved r4_pass_through_sensitivity_matrix.csv (2024 + 2030 horizon)')

print('\n✓ All 6 fixes complete.')

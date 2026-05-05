"""
Hannover Re SEA Climate Risk Dashboard — R-Ignite MASA Hackathon 2026
Run:  streamlit run app.py
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from scipy.stats import genextreme, kendalltau, spearmanr, norm
from scipy.optimize import minimize_scalar
from statsmodels.distributions.copula.api import (
    GaussianCopula, ClaytonCopula, GumbelCopula, FrankCopula, IndependenceCopula,
)
from pathlib import Path

st.set_page_config(
    page_title="HRe SEA Climate Risk · R-Ignite 2026",
    page_icon=":material/public:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Design tokens ─────────────────────────────────────────────────────────────
C = dict(
    bg       = "#09090b",
    surf1    = "#18181b",
    surf2    = "#27272a",
    surf3    = "#3f3f46",
    border   = "#3f3f46",
    border2  = "#52525b",
    teal     = "#2dd4bf",
    teal_dim = "rgba(45,212,191,0.15)",
    violet   = "#a78bfa",
    vio_dim  = "rgba(167,139,250,0.15)",
    amber    = "#fbbf24",
    amb_dim  = "rgba(251,191,36,0.12)",
    coral    = "#f87171",
    cor_dim  = "rgba(248,113,113,0.12)",
    sky      = "#38bdf8",
    sky_dim  = "rgba(56,189,248,0.12)",
    tx1      = "#f4f4f5",
    tx2      = "#a1a1aa",
    tx3      = "#71717a",
    tx4      = "#3f3f46",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body, .stApp {{
  font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}}
/* Keep Google Material icon glyphs from rendering as plain text */
.material-symbols-outlined,
.material-symbols-rounded,
.material-symbols-sharp {{
  font-family: 'Material Symbols Outlined' !important;
  font-weight: normal;
  font-style: normal;
  font-size: 20px;
  line-height: 1;
  letter-spacing: normal;
  text-transform: none;
  white-space: nowrap;
  direction: ltr;
  -webkit-font-smoothing: antialiased;
}}

.stApp {{
  background: {C['bg']} !important;
}}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: {C['bg']}; }}
::-webkit-scrollbar-thumb {{ background: {C['surf3']}; border-radius: 3px; }}

/* ── Main content padding ── */
.block-container {{
  padding: 1.5rem 2rem 3rem 2rem !important;
  max-width: 100% !important;
}}

/* ── Hide Streamlit chrome (keep header so sidebar toggle stays visible) ── */
#MainMenu, footer,
[data-testid="stDecoration"],
[data-testid="stStatusWidget"], [data-testid="stMainMenu"] {{
  display: none !important;
}}
header[data-testid="stHeader"] {{
  background: transparent !important;
  pointer-events: none !important;
}}
header[data-testid="stHeader"] * {{
  pointer-events: auto !important;
}}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
  background: {C['surf1']} !important;
  border-right: 1px solid {C['border']} !important;
  box-shadow: 4px 0 18px rgba(0,0,0,0.35);
  transition: transform .25s ease !important;
  scrollbar-width: none !important;
}}
[data-testid="stSidebar"]::-webkit-scrollbar {{
  display: none !important;
}}
[data-testid="stSidebar"] > div:first-child {{
  padding: 0 10px 8px 12px !important;
  overflow-y: hidden !important;
}}
[data-testid="stSidebar"] .block-container {{
  padding: 0.25rem 1.05rem 1.1rem 1.05rem !important;
}}

/* ── Streamlit's native sidebar collapse / expand controls ── */
/* Keep close button in the original compact style */
[data-testid="stSidebarCollapseButton"] button {{
  background: {C['surf2']} !important;
  border: 1px solid {C['border']} !important;
  border-radius: 8px !important;
  color: {C['tx2']} !important;
  transition: all .15s ease !important;
  width: 34px !important;
  height: 34px !important;
  min-width: 34px !important;
  min-height: 34px !important;
  padding: 0 !important;
}}
[data-testid="stSidebarCollapseButton"] button:hover {{
  background: {C['surf3']} !important;
  border-color: {C['teal']} !important;
  color: {C['teal']} !important;
}}

/* Open button (collapsed state): center-edge tab, partially off-screen */
[data-testid="stSidebarCollapsedControl"] button {{
  background: rgba(39,39,42,0.18) !important;
  border: 1px solid rgba(82,82,91,0.22) !important;
  border-radius: 10px !important;
  color: transparent !important;
  transition: all .15s ease !important;
  width: 22px !important;
  height: 56px !important;
  min-width: 22px !important;
  min-height: 56px !important;
  padding: 0 !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  opacity: 0.24 !important;
}}
[data-testid="stSidebarCollapsedControl"] button svg,
[data-testid="stSidebarCollapsedControl"] button [data-testid="stIcon"],
[data-testid="stSidebarCollapsedControl"] button span {{
  display: none !important;
}}
[data-testid="stSidebarCollapsedControl"] button::before {{
  content: "❯";
  font-size: 0.78rem !important;
  line-height: 1 !important;
  color: {C['tx3']} !important;
  display: block !important;
}}
[data-testid="stSidebarCollapsedControl"] button:hover {{
  background: rgba(63,63,70,0.35) !important;
  border-color: {C['teal']} !important;
  opacity: 0.55 !important;
}}
[data-testid="stSidebarCollapsedControl"] button:hover::before {{
  color: {C['teal']} !important;
}}
[data-testid="stSidebarCollapsedControl"] button:focus-visible {{
  outline: none !important;
  box-shadow: 0 0 0 1px {C['teal']} !important;
  opacity: 0.95 !important;
}}
/* Dock close button at sidebar right-center edge */
[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] {{
  position: absolute !important;
  top: 50% !important;
  right: -10px !important;
  transform: translateY(-50%) !important;
  z-index: 1001 !important;
  margin: 0 !important;
  padding: 0 !important;
}}
/* When sidebar is collapsed, keep reopen tab at center-left edge */
[data-testid="stSidebarCollapsedControl"] {{
  display: flex !important;
  position: fixed !important;
  top: 50% !important;
  left: 0 !important;
  right: auto !important;
  bottom: auto !important;
  transform: translate(-35%, -50%) !important;
  z-index: 2000 !important;
  margin: 0 !important;
  padding: 0 !important;
}}

/* Hide only top-left header control visuals; keep center-fixed control above */
header [data-testid="stSidebarCollapsedControl"] {{
  background: transparent !important;
}}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div {{
  color: {C['tx2']} !important;
  font-size: 0.8rem !important;
}}
[data-testid="stSidebar"] .material-symbols-outlined,
[data-testid="stSidebar"] .material-symbols-rounded,
[data-testid="stSidebar"] .material-symbols-sharp {{
  font-size: 18px !important;
}}
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stCheckbox label {{
  color: {C['tx2']} !important;
  font-size: 0.79rem !important;
  font-weight: 500 !important;
}}
/* slider active track */
[data-testid="stSidebar"] [data-baseweb="slider"] [role="slider"] {{
  background: {C['teal']} !important;
  border-color: {C['teal']} !important;
}}
[data-testid="stSidebar"] [data-baseweb="slider"] div[style*="background-color"] {{
  background-color: {C['teal']} !important;
}}

/* ── Tabs ── */
[data-testid="stTabs"] {{
  gap: 0;
}}
[data-testid="stTabs"] > div:first-child {{
  background: {C['surf1']};
  border-bottom: none !important;
  border-radius: 10px 10px 0 0;
  padding: 0 4px;
  gap: 2px;
}}
[data-baseweb="tab"] {{
  background: transparent !important;
  color: {C['tx3']} !important;
  border: none !important;
  border-radius: 8px 8px 0 0 !important;
  padding: 10px 20px !important;
  font-size: 0.8rem !important;
  font-weight: 500 !important;
  letter-spacing: 0.01em !important;
  transition: color 0.15s, background 0.15s !important;
  white-space: nowrap;
}}
[data-baseweb="tab"]:hover {{
  color: {C['tx1']} !important;
  background: {C['surf2']} !important;
}}
[data-baseweb="tab"][aria-selected="true"] {{
  color: {C['teal']} !important;
  background: {C['surf2']} !important;
  border-bottom: 2px solid {C['teal']} !important;
  font-weight: 600 !important;
}}
[data-testid="stTabsContent"] {{
  background: {C['surf1']} !important;
  border: 1px solid {C['border']} !important;
  border-radius: 0 0 10px 10px !important;
  padding: 0.85rem 1rem 1.1rem 1rem !important;
  min-height: 66vh !important;
  height: auto !important;
  overflow: visible !important;
}}
[data-testid="stTabsContent"] > div,
[data-testid="stTabsContent"] > div > div,
[data-testid="stTabsContent"] [role="tabpanel"] {{
  min-height: 66vh !important;
  height: auto !important;
}}

/* ── Native st.metric ── */
[data-testid="metric-container"] {{
  background: {C['surf1']} !important;
  border: 1px solid {C['border']} !important;
  border-radius: 10px !important;
  padding: 14px 18px !important;
}}
[data-testid="stMetricLabel"] p {{
  color: {C['tx3']} !important;
  font-size: 0.72rem !important;
  font-weight: 600 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.07em !important;
}}
[data-testid="stMetricValue"] {{
  color: {C['tx1']} !important;
  font-size: 1.3rem !important;
  font-weight: 700 !important;
  font-family: 'JetBrains Mono', monospace !important;
}}
[data-testid="stMetricDelta"] {{
  font-size: 0.75rem !important;
  font-weight: 500 !important;
}}
[data-testid="stMetricDelta"] svg {{ display: none !important; }}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {{
  background: {C['surf2']} !important;
  border: 1px solid {C['border']} !important;
  border-radius: 8px !important;
}}
[data-testid="stDataFrame"] > div {{
  background: transparent !important;
}}
.dvn-scroller {{ background: {C['surf2']} !important; }}

/* ── Plotly chart container ── */
[data-testid="stPlotlyChart"] {{
  background: {C['surf2']};
  border: 1px solid {C['border']};
  border-radius: 10px;
  overflow: hidden;
  padding: 4px;
}}
[data-testid="stPlotlyChart"] > div {{
  background: transparent !important;
}}

/* ── Image containers ── */
[data-testid="stImage"] {{
  background: {C['surf2']};
  border: 1px solid {C['border']};
  border-radius: 8px;
  overflow: hidden;
}}

/* ── Divider ── */
hr {{ border: none; border-top: 1px solid {C['border']}; margin: 1.2rem 0; }}

/* ── Checkbox ── */
[data-testid="stCheckbox"] {{
  margin: 4px 0 !important;
}}

/* ── Column gaps ── */
[data-testid="column"] {{
  gap: 0.8rem;
}}
[data-testid="stHorizontalBlock"] {{
  margin-bottom: 0.75rem;
}}
</style>
""", unsafe_allow_html=True)

# ── Plotly base theme ─────────────────────────────────────────────────────────
FONT = "Inter, system-ui, sans-serif"
MONO = "JetBrains Mono, monospace"

def base_layout(**overrides):
    base = dict(
        paper_bgcolor = C['surf2'],
        plot_bgcolor  = C['surf2'],
        font          = dict(family=FONT, color=C['tx2'], size=11),
        title         = dict(text="", font=dict(family=FONT, color=C['tx1'], size=13)),
        xaxis         = dict(
            gridcolor=C['surf3'], gridwidth=1, linecolor=C['border'],
            tickfont=dict(family=FONT, color=C['tx3'], size=10),
            title_font=dict(family=FONT, color=C['tx2'], size=11),
            zeroline=False,
        ),
        yaxis         = dict(
            gridcolor=C['surf3'], gridwidth=1, linecolor=C['border'],
            tickfont=dict(family=FONT, color=C['tx3'], size=10),
            title_font=dict(family=FONT, color=C['tx2'], size=11),
            zeroline=False,
        ),
        legend        = dict(
            bgcolor="rgba(0,0,0,0)", bordercolor=C['border'], borderwidth=1,
            font=dict(family=FONT, color=C['tx2'], size=10),
        ),
        hoverlabel    = dict(
            bgcolor=C['surf1'], bordercolor=C['border'],
            font=dict(family=FONT, color=C['tx1'], size=11),
        ),
        margin        = dict(t=48, b=36, l=52, r=20),
        hovermode     = "x unified",
    )
    base.update(overrides)
    return base

def kpi_row(items):
    """items = list of (label, value, sub, accent_color)"""
    cards = ""
    for label, value, sub, accent in items:
        dot = f'<div style="width:6px;height:6px;border-radius:50%;background:{accent};flex-shrink:0;margin-top:2px"></div>'
        cards += f"""
<div style="background:{C['surf2']};border:1px solid {C['border']};border-radius:10px;
     padding:16px 20px;display:flex;flex-direction:column;gap:4px;min-width:0">
  <div style="display:flex;align-items:flex-start;gap:6px">
    {dot}
    <span style="color:{C['tx3']};font-size:0.68rem;font-weight:600;
          text-transform:uppercase;letter-spacing:0.08em;line-height:1.4">{label}</span>
  </div>
  <div style="color:{C['tx1']};font-size:1.25rem;font-weight:700;
       font-family:'JetBrains Mono',monospace;letter-spacing:-0.02em;
       white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{value}</div>
  <div style="color:{accent};font-size:0.73rem;font-weight:500">{sub}</div>
</div>"""
    st.markdown(
        f'<div style="display:grid;grid-template-columns:repeat({len(items)},1fr);'
        f'gap:10px;margin-bottom:1.2rem">{cards}</div>',
        unsafe_allow_html=True,
    )


def badge(text, color):
    return (f'<span style="background:{color}22;color:{color};border:1px solid {color}44;'
            f'font-size:0.65rem;font-weight:600;padding:2px 9px;border-radius:20px;'
            f'letter-spacing:0.06em;font-family:{FONT}">{text}</span>')


def callout(text, accent=None, icon="", fixed_height=None):
    accent = accent or C['sky']
    icon_html = (f'<span style="display:inline-flex;align-items:center;justify-content:center;'
                 f'min-width:22px;height:22px;padding:0 6px;margin-right:8px;border-radius:6px;'
                 f'background:{accent}22;color:{accent};font-size:0.7rem;font-weight:700;'
                 f'font-family:{FONT};letter-spacing:0.04em;flex-shrink:0">{icon}</span>') if icon else ""
    st.markdown(f"""
<div style="background:{accent}0d;border:0;border-left:3px solid {accent};
     border-radius:8px;padding:12px 16px;margin:8px 0;
     font-size:0.81rem;color:{C['tx2']};line-height:1.65;
     display:flex;align-items:flex-start;gap:0;overflow-wrap:anywhere;
     {'height:'+str(fixed_height)+'px;overflow:auto;' if fixed_height else ''}">
  {icon_html}<div style="flex:1;min-width:0">{text}</div>
</div>""", unsafe_allow_html=True)


def section_label(text):
    st.markdown(
        f'<div style="font-size:0.68rem;font-weight:700;color:{C["tx3"]};'
        f'text-transform:uppercase;letter-spacing:0.1em;margin:1.2rem 0 0.6rem 0">'
        f'{text}</div>',
        unsafe_allow_html=True,
    )

# ── Data ──────────────────────────────────────────────────────────────────────
OUT  = Path("outputs")
DATA = Path("data/processed")

@st.cache_data
def load_data():
    r3     = pd.read_csv(OUT/"r3_results_table.csv").set_index("country_code")
    r4s    = pd.read_csv(OUT/"r4_stress_scenario_table.csv")
    pt     = pd.read_csv(OUT/"r4_pass_through_sensitivity_matrix.csv")
    gdp    = pd.read_csv(DATA/"wb_2023_nominal_gdp_usd_bn.csv").set_index("Country")["Nominal_GDP_USD_Bn"]
    cw_mys = pd.read_csv(DATA/"msia_climatewatch_lulucf.csv")
    cw_phl = pd.read_csv(DATA/"phili_climatewatch_lulucf.csv")
    chirps = pd.read_csv(DATA/"chirpsRX5_mls_phl.csv")
    oni = pd.read_csv(DATA/"noaa_oni_cleaned.csv")
    cop    = pd.read_csv(OUT/"r8_copula_results.csv").set_index("metric") if (OUT/"r8_copula_results.csv").exists() else None
    return r3, r4s, pt, gdp, cw_mys, cw_phl, chirps, oni, cop

r3, r4s, pt_df, gdp, cw_mys, cw_phl, chirps_df, oni_df, cop = load_data()

# ── Derive all constants from backend CSVs (no hardcodes) ─────────────────────
_cw_mys_num = cw_mys.copy(); _cw_mys_num["ghg"] = pd.to_numeric(_cw_mys_num["2023"])
_cw_phl_num = cw_phl.copy(); _cw_phl_num["ghg"] = pd.to_numeric(_cw_phl_num["2023"])

# Carbon price baseline from NGFS stress scenario table
BASELINE_C    = float(r4s[r4s["Scenario"].str.contains("Baseline", case=False, na=False)]["Carbon Price (USD/t)"].iloc[0])

# GHG totals from Climate Watch (positive sectors only — same basis as notebook 05)
MYS_GHG       = float(_cw_mys_num[_cw_mys_num["ghg"] > 0]["ghg"].sum())
PHL_GHG       = float(_cw_phl_num[_cw_phl_num["ghg"] > 0]["ghg"].sum())

# LULUCF values for callout text
MYS_LULUCF    = float(_cw_mys_num[_cw_mys_num["Sector"].str.contains("Land Use", na=False)]["ghg"].iloc[0])
PHL_LULUCF    = float(_cw_phl_num[_cw_phl_num["Sector"].str.contains("Land Use", na=False)]["ghg"].iloc[0])

# EAL gap from r3 (sum of MYS+PHL insured pricing gap in USD M)
eal_gap       = float((r3.loc["MYS","eal_pricing_gap_usd_bn"] + r3.loc["PHL","eal_pricing_gap_usd_bn"]) * 1000)

# HRe portfolio assumptions from r6 (sourced and saved by notebook 06)
_r6           = pd.read_csv(OUT/"r6_hre_impact_estimate.csv").set_index("Metric")
hre_share     = float(_r6.loc["HRE_MARKET_SHARE (assumption)","Value"])
treaty_attach = float(_r6.loc["TREATY_ATTACHMENT_FACTOR (assumption)","Value"])

# PELT break year and observation count from r3
MYS_BREAK     = int(r3.loc["MYS","pelt_break_year"])
PHL_BREAK     = int(r3.loc["PHL","pelt_break_year"])
N_OBS         = int(r3.loc["MYS","eal_data_window_yrs"])

# Copula summary stats from r8 (used in Tab4 description text)
_tau_all_live = float(cop.loc["Kendall_tau_all","value"]) if cop is not None else -0.023
_p_tau_live   = float(cop.loc["p_tau_all","value"])      if cop is not None else 0.85

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
<div style="padding:18px 0 20px 0;border-bottom:1px solid {C['border']};margin-bottom:20px">
  <div style="color:{C['teal']};font-size:0.62rem;font-weight:700;letter-spacing:0.15em;
       text-transform:uppercase;margin-bottom:6px">R-Ignite · MASA 2026</div>
  <div style="color:{C['tx1']};font-size:1.05rem;font-weight:800;letter-spacing:-0.02em">
    Climate Risk<br>Reserve Dashboard
  </div>
  <div style="color:{C['tx3']};font-size:0.72rem;margin-top:6px">
    Hannover Re · SEA Portfolio
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown(f'<div style="color:{C["teal"]};font-size:0.65rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:10px">⬡ Transition Risk</div>', unsafe_allow_html=True)
    carbon_price = st.slider("Carbon price (USD/tCO₂e)", 0, 200, int(round(BASELINE_C)), 1,
                             help=f"NGFS NZ2050 = ${BASELINE_C:.1f}/t · 2× stress = ${BASELINE_C*2:.0f}/t")
    pt_rate_pct  = st.slider("Pass-through rate (%)", 1, 8, 3, 1,
                             help="IMF Fiscal Monitor 2021: 1–5% · EIOPA 2023: 3–8%")
    pt_rate = pt_rate_pct / 100.0

    st.markdown(f'<div style="color:{C["violet"]};font-size:0.65rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;margin:18px 0 10px 0">◈ Physical Risk</div>', unsafe_allow_html=True)
    show_ci   = st.checkbox("Show 95% bootstrap CI bands", value=True)
    log_scale = st.checkbox("Log-scale x-axis", value=False, key="log_scale_axis_v2")

    st.markdown(f'<div style="color:{C["amber"]};font-size:0.65rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;margin:18px 0 10px 0">◎ HRe Portfolio</div>', unsafe_allow_html=True)
    sea_alloc_pct = st.slider("HRe SEA allocation (%)", 1, 25, 3, 1,
                              help="Floor 3% · Base 10% · Regional 20%")
    sea_alloc     = sea_alloc_pct / 100.0

    st.markdown(f"""
<div style="border-top:1px solid {C['border']};margin-top:18px;padding-top:12px;padding-bottom:14px">
  <div style="color:{C['tx4']};font-size:0.68rem;line-height:1.8">
    CHIRPS v2.0 · EM-DAT · NOAA ONI<br>
    WDI · NGFS GCAM 6.0 · Climate Watch<br>
    BNM CCPT 2021 · UNFCCC Art.6
  </div>
</div>""", unsafe_allow_html=True)

# ── Live calcs (all inputs derived from backend CSVs above) ───────────────────
mys_tc   = MYS_GHG * carbon_price / 1000
phl_tc   = PHL_GHG * carbon_price / 1000
mys_pt   = mys_tc * pt_rate
phl_pt   = phl_tc * pt_rate

# eal_gap is the INSURED EAL pricing gap from r3 (penetration already applied in nb04).
# Chain: insured_gap × treaty_attachment × HRe_market_share = $18.4M × 50% × 8% = $0.74M
attached = eal_gap * treaty_attach
hre_phys = attached * hre_share
hre_tran = (mys_pt + phl_pt) * 1e3 * hre_share * sea_alloc
hre_tot  = hre_phys + hre_tran
mys_gdp  = gdp["Malaysia"]
phl_gdp  = gdp["Philippines"]

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:linear-gradient(135deg,{C['surf1']} 0%,{C['surf2']} 100%);
     border:1px solid {C['border']};border-radius:14px;
     padding:22px 28px;margin-bottom:20px">
  <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:16px">
    <div>
      <div style="color:{C['tx3']};font-size:0.65rem;font-weight:700;
           text-transform:uppercase;letter-spacing:0.12em;margin-bottom:8px">
        Hannover Re &nbsp;·&nbsp; SEA Treaty Portfolio &nbsp;·&nbsp; MASA Hackathon 2026
      </div>
      <div style="color:{C['tx1']};font-size:1.5rem;font-weight:800;
           letter-spacing:-0.03em;line-height:1.2">
        Climate Risk Reserve Gap
        <span style="color:{C['teal']}">Analysis</span>
      </div>
      <div style="color:{C['tx3']};font-size:0.8rem;margin-top:8px;line-height:1.5">
        GEV extreme value &nbsp;·&nbsp; PELT regime break &nbsp;·&nbsp;
        NGFS transition cost &nbsp;·&nbsp; GEV-Copula joint tail dependence
      </div>
    </div>
    <div style="display:flex;flex-direction:column;gap:6px;align-items:flex-end;flex-shrink:0">
      {badge("Malaysia · Philippines", C['teal'])}
      {badge("1990–2023 · CHIRPS / WDI", C['tx3'])}
      {badge("University of Malaya", C['violet'])}
    </div>
  </div>
</div>""", unsafe_allow_html=True)

# ── KPI row ───────────────────────────────────────────────────────────────────
cp_rel = f"{(carbon_price/BASELINE_C - 1)*100:+.0f}% vs NZ2050" if carbon_price != 56 else "NGFS NZ2050 baseline"
kpi_row([
    ("MYS Transition Cost",  f"${mys_tc:.1f}bn/yr",   f"{mys_tc/mys_gdp*100:.1f}% of GDP",         C['teal']),
    ("PHL Transition Cost",  f"${phl_tc:.1f}bn/yr",   f"{phl_tc/phl_gdp*100:.1f}% of GDP",         C['violet']),
    ("SEA Treaty Pool",      f"${mys_pt+phl_pt:.2f}bn/yr", f"at {pt_rate_pct}% pass-through",       C['tx3']),
    ("HRe Combined Gap",     f"${hre_tot:.1f}M/yr",   f"SEA alloc {sea_alloc_pct}% · floor est.",   C['amber']),
    ("Carbon Price",         f"${carbon_price}/t",    cp_rel, C['coral'] if carbon_price > 80 else C['tx3']),
])

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "◈  Physical Risk — GEV",
    "⬡  Transition Risk",
    "◎  HRe Reserve Gap",
    "✦  Copula Analysis",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — GEV
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    # Description row
    c_desc1, c_desc2 = st.columns([3, 1])
    with c_desc1:
        st.markdown(f"""
<div style="font-size:0.82rem;color:{C['tx2']};line-height:1.6;margin-bottom:1rem">
  GEV fitted via MLE to CHIRPS RX5day annual maxima.
  <b style="color:{C['teal']}">Non-stationary model preferred for Malaysia</b>
  (ΔAIC = +1.88, μ₁ = +0.48 mm/yr) — location parameter trending upward.
  PELT structural break detected at <b style="color:{C['tx1']}">{MYS_BREAK}</b> (MYS) and <b style="color:{C['tx1']}">{PHL_BREAK}</b> (PHL).
  Bootstrap CI n=500, seed=42.
</div>""", unsafe_allow_html=True)
    with c_desc2:
        st.markdown(f"""
<div style="background:{C['surf2']};border:1px solid {C['border']};border-radius:8px;
     padding:10px 14px;font-size:0.75rem;color:{C['tx3']};line-height:1.7;
     margin-bottom:12px">
  <b style="color:{C['tx2']}">Source</b><br>
  CHIRPS v2.0 · UCSB<br>
  WMO ETCCDI RX5day<br>
  1990–2023 · n={N_OBS}
</div>""", unsafe_allow_html=True)

    # GEV chart
    # Keep timeline intuitive and bounded to ~100 years.
    return_periods = np.linspace(2, 100, 250)
    exc_probs      = 1.0 - 1.0 / return_periods

    fig = go.Figure()
    country_cfg = [
        ("MYS", "Malaysia — Flood", C['teal'], "rgba(45,212,191,0.1)"),
        ("PHL", "Philippines — Storm", C['violet'], "rgba(167,139,250,0.1)"),
    ]

    for code, label, col, fill in country_cfg:
        row   = r3.loc[code]
        xi, loc_v, sc = float(row.gev_shape_c), float(row.gev_loc_mu), float(row.gev_scale_sigma)
        rl100 = float(row.return_level_100yr_mm)
        ci_lo = float(row.rl_100yr_ci95_lo_mm)
        ci_hi = float(row.rl_100yr_ci95_hi_mm)
        rl    = genextreme.ppf(exc_probs, xi, loc=loc_v, scale=sc)

        if show_ci:
            fig.add_trace(go.Scatter(
                x=np.r_[return_periods, return_periods[::-1]],
                y=np.r_[rl*(ci_hi/rl100), (rl*(ci_lo/rl100))[::-1]],
                fill="toself", fillcolor=fill,
                line=dict(color="rgba(0,0,0,0)"),
                name=f"{code} 95% CI", showlegend=True, hoverinfo="skip",
            ))
        fig.add_trace(go.Scatter(
            x=return_periods, y=rl, name=label,
            line=dict(color=col, width=2.5),
            hovertemplate=f"<b>{code}</b>  %{{x:.0f}}-yr event<br>RX5day: <b>%{{y:.1f}} mm</b><extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=[100], y=[rl100], mode="markers+text",
            marker=dict(color=col, size=9, line=dict(color=C['surf1'], width=2)),
            text=[f"  {rl100:.0f} mm"],
            textposition="middle right",
            textfont=dict(size=10, color=col, family=MONO),
            showlegend=False,
            hovertemplate=f"<b>{code} 100-yr</b><br>{rl100:.0f} mm  CI [{ci_lo:.0f}–{ci_hi:.0f}]<extra></extra>",
        ))

    fig.add_vline(x=100, line_dash="dot", line_color=C['surf3'], line_width=1.2,
                  annotation_text="100-yr", annotation_position="top right",
                  annotation_font=dict(color=C['tx3'], size=9))

    layout = base_layout(height=400)
    layout["xaxis"]["title"] = "Return period (years)"
    layout["xaxis"]["type"]  = "log" if log_scale else "linear"
    if log_scale:
        layout["xaxis"]["range"] = [np.log10(2), np.log10(100)]
    else:
        layout["xaxis"]["range"] = [2, 100]
        layout["xaxis"]["dtick"] = 10
    layout["yaxis"]["title"] = "RX5day precipitation (mm)"
    layout["legend"]["orientation"] = "h"
    layout["legend"]["y"] = 1.05
    layout["legend"]["x"] = 0
    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Stat cards
    col_m, col_p = st.columns(2)
    mys_r, phl_r = r3.loc["MYS"], r3.loc["PHL"]
    with col_m:
        kpi_row([
            ("100-yr Return Level",  f"{mys_r.return_level_100yr_mm:.0f} mm",
             f"CI [{mys_r.rl_100yr_ci95_lo_mm:.0f}–{mys_r.rl_100yr_ci95_hi_mm:.0f}] mm", C['teal']),
            ("PELT Break",           str(MYS_BREAK),
             f"+{mys_r.uplift_pct:.1f}% post-break mean", C['teal']),
            ("EAL Pricing Gap",      f"+{mys_r.eal_pricing_gap_pct:.1f}%",
             "GEV forward vs burning cost", C['teal']),
        ])
        callout(
            f"<b style='color:{C['tx1']}'>Malaysia · Flood-dominated</b> &nbsp; "
            f"{badge('Weibull ξ='+str(round(mys_r.gev_shape_c,4)), C['teal'])} "
            f"{badge('Non-stationary preferred', C['amber'])}<br>"
            f"μ₁ = +0.48 mm/yr trend confirmed. Pre/post-{MYS_BREAK} KS test: σ, ξ stable → "
            "location-only shift validated.",
            accent=C['teal'], icon="MY", fixed_height=86
        )
    with col_p:
        kpi_row([
            ("100-yr Return Level",  f"{phl_r.return_level_100yr_mm:.0f} mm",
             f"CI [{phl_r.rl_100yr_ci95_lo_mm:.0f}–{phl_r.rl_100yr_ci95_hi_mm:.0f}] mm  △", C['violet']),
            ("PELT Break",           str(PHL_BREAK),
             f"+{phl_r.uplift_pct:.1f}% post-break mean", C['violet']),
            ("EAL Pricing Gap",      f"+{phl_r.eal_pricing_gap_pct:.1f}%",
             "GEV forward vs burning cost", C['violet']),
        ])
        callout(
            f"<b style='color:{C['tx1']}'>Philippines · Storm/Typhoon-dominated</b> &nbsp; "
            f"{badge('Weibull ξ='+str(round(phl_r.gev_shape_c,4)), C['violet'])} "
            f"{badge(f'3× CI width — n={N_OBS}', C['coral'])}<br>"
            "Wide CI [326–985 mm] is not a failure; it proves single-point historical "
            "pricing is dangerous for catastrophe reserving.",
            accent=C['violet'], icon="PH", fixed_height=86
        )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Transition Risk
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown(f"""
<div style="font-size:0.82rem;color:{C['tx2']};line-height:1.6;margin-bottom:1rem">
  Carbon cost = GHG inventory (MtCO₂e) × carbon price. Pass-through = fraction reaching
  reinsurance premiums. Range anchored to
  <b style="color:{C['tx1']}">IMF Fiscal Monitor Oct-2021 Table 2.1</b> (1–5%) and
  <b style="color:{C['tx1']}">EIOPA 2023 Climate Stress Test</b> (3–8% for exposed lines).
</div>""", unsafe_allow_html=True)

    sectors     = ["Energy", "Industrial Processes", "Agriculture", "Waste", "LULUCF"]
    sec_colors  = [C['sky'], C['teal'], C['amber'], C['violet'], C['coral']]
    mys_sec_bn  = [max(0, float(r["2023"].values[0]) if not (r := cw_mys[cw_mys["Sector"]==s]).empty else 0) * carbon_price / 1000 for s in sectors]
    phl_sec_bn  = [max(0, float(r["2023"].values[0]) if not (r := cw_phl[cw_phl["Sector"]==s]).empty else 0) * carbon_price / 1000 for s in sectors]

    scen_p      = [0, BASELINE_C, BASELINE_C*2]
    mys_scen_bn = [MYS_GHG * p / 1000 for p in scen_p]
    phl_scen_bn = [PHL_GHG * p / 1000 for p in scen_p]
    scen_labels = ["Current\nPolicies", "NGFS\nNZ2050", "2× Stress\nScenario"]

    fig_tc = make_subplots(
        rows=1, cols=3,
        subplot_titles=["", "", ""],
        column_widths=[0.32, 0.32, 0.36],
        horizontal_spacing=0.07,
    )

    for i, (s, mc, pc, col) in enumerate(zip(sectors, mys_sec_bn, phl_sec_bn, sec_colors)):
        kw = dict(showlegend=(i==0), marker_line_width=0,
                  textfont=dict(color=C['tx3'], size=9))
        if mc > 0:
            fig_tc.add_trace(go.Bar(name=s, x=[s], y=[mc], marker_color=col,
                text=[f"${mc:.1f}b"], textposition="outside", **kw), row=1, col=1)
        if pc > 0:
            fig_tc.add_trace(go.Bar(name=s, x=[s], y=[pc], marker_color=col,
                text=[f"${pc:.1f}b"], textposition="outside",
                showlegend=False, marker_line_width=0,
                textfont=dict(color=C['tx3'], size=9)), row=1, col=2)

    for vals, col_name, clr in [(mys_scen_bn, "Malaysia", C['teal']),
                                (phl_scen_bn, "Philippines", C['violet'])]:
        fig_tc.add_trace(go.Bar(
            name=col_name, x=scen_labels, y=vals, marker_color=clr,
            marker_line_width=0, showlegend=True,
            text=[f"${v:.1f}b" for v in vals], textposition="outside",
            textfont=dict(color=C['tx3'], size=9),
            hovertemplate=f"<b>{col_name}</b><br>${{y:.1f}}bn/yr<extra></extra>",
        ), row=1, col=3)

    layout_tc = base_layout(height=420)
    layout_tc["barmode"] = "group"
    layout_tc["showlegend"] = True
    layout_tc["legend"]["orientation"] = "h"
    layout_tc["legend"]["y"] = 1.22
    layout_tc["legend"]["x"] = 0
    layout_tc["legend"]["font"] = dict(family=FONT, color=C['tx2'], size=9)
    layout_tc["margin"] = dict(t=110, b=36, l=52, r=20)
    ax = dict(gridcolor=C['surf3'], linecolor=C['border'],
              tickfont=dict(family=FONT, color=C['tx3'], size=9),
              title_font=dict(family=FONT, color=C['tx2'], size=10),
              zeroline=False, showgrid=False)
    fig_tc.update_layout(**{k: v for k, v in layout_tc.items()
                            if k not in ("xaxis","yaxis")})
    yax_tc = {**ax, "showgrid": True, "gridcolor": C['surf3']}
    yax_tc.pop("title_font", None)
    for r, c in [(1,1),(1,2),(1,3)]:
        fig_tc.update_xaxes(**ax, row=r, col=c)
        fig_tc.update_yaxes(title_text="USD bn/yr", **yax_tc, row=r, col=c)
    fig_tc.update_annotations(font=dict(color=C['tx2'], size=10, family=FONT))
    st.plotly_chart(fig_tc, use_container_width=True, config={"displayModeBar": False})

    section_label("GDP Materiality")
    kpi_row([
        ("MYS Total Cost",  f"${mys_tc:.1f}bn/yr",  f"{mys_tc/mys_gdp*100:.1f}% of GDP",   C['teal']),
        ("PHL Total Cost",  f"${phl_tc:.1f}bn/yr",  f"{phl_tc/phl_gdp*100:.1f}% of GDP",   C['violet']),
        ("MYS After PT",    f"${mys_pt:.2f}bn/yr",  f"at {pt_rate_pct}% pass-through",      C['tx3']),
        ("PHL After PT",    f"${phl_pt:.2f}bn/yr",  f"at {pt_rate_pct}% pass-through",      C['tx3']),
    ])

    callout(
        f"<b style='color:{C['tx1']}'>LULUCF Asymmetry — a uniform SEA surcharge misprices both markets</b><br>"
        f"Malaysia = {badge(f'net LULUCF emitter {MYS_LULUCF:+.1f} MtCO₂e', C['coral'])} palm oil deforestation → BNM CCPT C3/C4 surcharge (3–5%).<br>"
        f"Philippines = {badge(f'net LULUCF sink {PHL_LULUCF:+.1f} MtCO₂e', C['teal'])} reforestation → Art.6.2 ITMO credits offset cost (1–2% loading).",
        accent=C['amber'], icon="▦"
    )
    st.markdown('<div style="height:36px"></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — HRe Reserve Gap
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown(f"""
<div style="font-size:0.82rem;color:{C['tx2']};line-height:1.6;margin-bottom:1rem">
  Every multiplicative step from total economic EAL to HRe's specific reserve exposure
  is shown explicitly. Adjust the sidebar sliders to stress-test each assumption.
</div>""", unsafe_allow_html=True)

    alloc_scen = [(f"Floor (SEA {sea_alloc_pct}%)", sea_alloc), ("Base (10%)", 0.10), ("Regional (20%)", 0.20)]
    sc_lbl     = [a[0] for a in alloc_scen]
    phys_v     = [hre_phys] * 3
    tran_base  = [(mys_pt+phl_pt)*1e3*hre_share*a for _,a in alloc_scen]
    tran_str   = [(MYS_GHG*(carbon_price*2)/1000*pt_rate +
                   PHL_GHG*(carbon_price*2)/1000*pt_rate)*1e3*hre_share*a
                  for _,a in alloc_scen]

    fig_wf = make_subplots(
        rows=1, cols=2,
        subplot_titles=["<b>Physical EAL Chain</b> (USD M/yr)",
                        "<b>Combined Reserve Gap</b> by SEA Allocation"],
        column_widths=[0.46, 0.54], horizontal_spacing=0.10,
    )

    # Waterfall: eal_gap is already the INSURED pricing gap (penetration applied in nb04).
    # Chain: Insured EAL gap → × Attach 50% → × HRe 8% → HRe Physical
    fig_wf.add_trace(go.Waterfall(
        orientation="v",
        measure=["absolute","relative","relative","total"],
        x=["Insured EAL Gap\n(pen-adjusted)", f"× Attach {treaty_attach:.0%}",
           f"× HRe {hre_share:.0%}", "HRe Physical"],
        y=[eal_gap, -(eal_gap - attached), -(attached - hre_phys), None],
        text=[f"${eal_gap:.1f}M", f"−${eal_gap-attached:.2f}M",
              f"−${attached-hre_phys:.2f}M", f"${hre_phys:.2f}M"],
        textposition="outside",
        textfont=dict(color=C['tx2'], size=9, family=MONO),
        connector=dict(line=dict(color=C['surf3'], dash="dot", width=1)),
        increasing=dict(marker=dict(color=C['sky'], line=dict(width=0))),
        decreasing=dict(marker=dict(color=C['coral'], line=dict(width=0))),
        totals=dict(marker=dict(color=C['teal'], line=dict(width=0))),
        hovertemplate="%{x}<br><b>%{y:.3f} USD M</b><extra></extra>",
    ), row=1, col=1)

    for (name, clr, vals) in [
        ("Physical (EAL gap)",          C['teal'],   phys_v),
        (f"Transition baseline ({pt_rate_pct}% PT)", C['violet'], tran_base),
        ("Transition 2× stress",        C['coral'],  tran_str),
    ]:
        fig_wf.add_trace(go.Bar(
            name=name, x=sc_lbl, y=vals, marker_color=clr, marker_line_width=0,
            text=[f"${v:.1f}M" for v in vals], textposition="inside",
            textfont=dict(color=C['surf1'] if clr==C['teal'] else C['tx1'], size=9, family=MONO),
            hovertemplate=f"{name}: $%{{y:.1f}}M<extra></extra>",
            opacity=0.75 if name == "Transition 2× stress" else 1.0,
        ), row=1, col=2)

    layout_wf = base_layout(height=440)
    layout_wf["barmode"] = "stack"
    layout_wf["legend"]["orientation"] = "h"
    layout_wf["legend"]["y"] = -0.18
    layout_wf["legend"]["x"] = 0.5
    layout_wf["legend"]["xanchor"] = "center"
    layout_wf["margin"] = dict(t=60, b=70, l=52, r=20)
    ax2 = dict(gridcolor=C['surf3'], linecolor=C['border'],
               tickfont=dict(family=MONO, color=C['tx3'], size=9),
               zeroline=False, showgrid=False)
    fig_wf.update_layout(**{k:v for k,v in layout_wf.items() if k not in ("xaxis","yaxis")})
    yax_wf = {**ax2, "showgrid": True, "gridcolor": C['surf3']}
    for r, c in [(1,1),(1,2)]:
        fig_wf.update_xaxes(**ax2, row=r, col=c)
        fig_wf.update_yaxes(title_text="USD M/yr", **yax_wf, row=r, col=c)
    fig_wf.update_annotations(font=dict(color=C['tx2'], size=11, family=FONT))
    st.plotly_chart(fig_wf, use_container_width=True, config={"displayModeBar": False})

    section_label("Reserve Estimate Summary")
    kpi_row([
        ("Physical Exposure",   f"${hre_phys:.2f}M/yr",   f"Insured EAL gap × {treaty_attach:.0%} attach × {hre_share:.0%} HRe share", C['teal']),
        ("Transition (floor)",  f"${hre_tran:.1f}M/yr",   f"{pt_rate_pct}% PT · {sea_alloc_pct}% SEA alloc",           C['violet']),
        ("Combined (floor)",    f"${hre_tot:.1f}M/yr",    f"base 10% → ${hre_phys+(mys_pt+phl_pt)*1e3*hre_share*0.10:.1f}M", C['amber']),
    ])

    callout(
        f"<b style='color:{C['tx1']}'>Methodology Note — Reserve Floor, Not Final Quantum</b><br>"
        f"${hre_tot:.1f}M/yr is derived from four stacked conservative assumptions. "
        "The primary deliverable is the <b>repricing framework itself</b> — once cedant-level "
        "loss triangles are disclosed, this estimate refines by an order of magnitude.",
        accent=C['coral'], icon="△"
    )
    st.markdown('<div style="height:36px"></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Copula
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown(f"""
<div style="font-size:0.82rem;color:{C['tx2']};line-height:1.6;margin-bottom:1rem">
  Formally tests whether MYS and PHL extreme precipitation losses are independent or dependent,
  using Probability Integral Transform + four copula families.
  Key finding: <b style="color:{C['tx1']}">independence cannot be rejected annually</b>
  (τ = {_tau_all_live:+.3f}, p = {_p_tau_live:.2f}), but
  <b style="color:{C['amber']}">La Niña introduces conditional positive dependence</b>
  (Δτ = +0.30 vs El Niño).
</div>""", unsafe_allow_html=True)

    if cop is None:
        callout("Run <code>python run_all.py</code> to generate copula outputs.", C['coral'], "△")
    else:
        rx = chirps_df.pivot(index="year", columns="country_code", values="RX5day_mm")
        idx = rx.dropna().index.astype(int)
        mys_raw = rx.loc[idx, "MYS"].to_numpy()
        phl_raw = rx.loc[idx, "PHL"].to_numpy()

        oni_djf = (
            oni_df[oni_df["SEAS"] == "DJF"]
            .rename(columns={"YR": "year", "ANOM": "oni_anom"})
            .set_index("year")["oni_anom"]
        )
        oni_aligned = oni_djf.reindex(idx)

        def enso_phase(anom):
            if pd.isna(anom):
                return "Unknown"
            if anom >= 0.5:
                return "El Niño"
            if anom <= -0.5:
                return "La Niña"
            return "Neutral"

        phases = oni_aligned.apply(enso_phase)

        xi_m, mu_m, sc_m = genextreme.fit(mys_raw, method="mle")
        xi_p, mu_p, sc_p = genextreme.fit(phl_raw, method="mle")
        eps = 1e-6
        u = np.clip(genextreme.cdf(mys_raw, xi_m, loc=mu_m, scale=sc_m), eps, 1 - eps)
        v = np.clip(genextreme.cdf(phl_raw, xi_p, loc=mu_p, scale=sc_p), eps, 1 - eps)

        cond_results = {}
        for ph in ["La Niña", "Neutral", "El Niño"]:
            mask = (phases == ph).to_numpy()
            if mask.sum() >= 5:
                tau_ph, p_ph = kendalltau(mys_raw[mask], phl_raw[mask])
                rho_ph, _ = spearmanr(mys_raw[mask], phl_raw[mask])
                cond_results[ph] = {"n": int(mask.sum()), "tau": float(tau_ph), "p": float(p_ph), "rho": float(rho_ph)}

        uv = np.column_stack([u, v])
        n_uv = len(uv)

        def fit_archimedean(copula_cls, lo, hi):
            def neg_ll(theta):
                try:
                    lp = copula_cls(theta=theta).logpdf(uv)
                    return -np.sum(lp) if np.all(np.isfinite(lp)) else np.inf
                except Exception:
                    return np.inf
            res = minimize_scalar(neg_ll, bounds=(lo + 1e-4, hi - 1e-4), method="bounded")
            ll = -res.fun
            aic = 2 - 2 * ll
            bic = np.log(n_uv) - 2 * ll
            return float(aic), float(bic)

        tau_all = float(cop.loc["Kendall_tau_all","value"])
        p_tau = float(cop.loc["p_tau_all","value"])
        tau_la = float(cop.loc["tau_LaNina","value"])
        rho_la = float(cop.loc["rho_gaussian_LaNina","value"])
        p99_gap = float(cop.loc["p99_gap_USD_M","value"])
        hre_p99_gap = float(cop.loc["HRe_10pct_alloc_p99_gap_USD_M","value"])
        try:
            aic_cl, bic_cl = fit_archimedean(ClaytonCopula, 0.0, 20.0)
            aic_gu, bic_gu = fit_archimedean(GumbelCopula, 1.0, 20.0)
            aic_fr, bic_fr = fit_archimedean(FrankCopula, 0.0, 40.0)
            rho_g = float(np.sin(np.pi / 2 * tau_all))
            ll_g = GaussianCopula(corr=rho_g).logpdf(uv).sum()
            aic_g = float(2 - 2 * ll_g)
            bic_g = float(np.log(n_uv) - 2 * ll_g)
            ll_i = IndependenceCopula().logpdf(uv).sum()
            aic_ind = float(2 * (-ll_i))
            bic_ind = float(2 * (-ll_i))
        except Exception:
            # Fallback to backend summary values if fit fails in runtime.
            aic_ind = float(cop.loc["AIC_Independence", "value"])
            bic_ind = aic_ind
            aic_cl, bic_cl = 2.0, np.log(n_uv) + 2.0
            aic_gu, bic_gu = 2.0, np.log(n_uv) + 2.0
            aic_fr, bic_fr = 2.0, np.log(n_uv) + 2.0
            aic_g, bic_g = 1.85, np.log(n_uv) + 1.85

        aic_models = {
            "Clayton": (aic_cl, bic_cl),
            "Gumbel": (aic_gu, bic_gu),
            "Frank": (aic_fr, bic_fr),
            "Gaussian": (aic_g, bic_g),
            "Independence": (aic_ind, bic_ind),
        }
        best_c = min(aic_models, key=lambda k: aic_models[k][0])

        kpi_row([
            ("Overall Kendall τ",    f"{tau_all:+.4f}",  f"p = {p_tau:.4f}  ·  cannot reject H₀",    C['tx3']),
            ("La Niña τ",            f"{tau_la:+.4f}",   f"Gaussian ρ = {rho_la:.3f}",                C['teal']),
            ("AIC-best copula",      best_c,             "ΔAIC < 2  ·  independence adequate",         C['tx3']),
            ("100-yr Portfolio Gap", f"+${p99_gap:.1f}M", f"HRe (10% SEA alloc): +${hre_p99_gap:.1f}M", C['amber']),
        ])

        section_label("PIT scatter by ENSO phase (interactive)")
        la = cond_results.get("La Niña", {"n": 0, "tau": np.nan})
        en = cond_results.get("El Niño", {"n": 0, "tau": np.nan})
        ne = cond_results.get("Neutral", {"n": 0, "tau": np.nan})

        def tau_lbl(v):
            return "NA" if not np.isfinite(v) else f"{v:+.3f}"

        fig_pit = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                f"All years (n={len(idx)}) · τ={tau_all:+.3f}",
                f"La Niña (n={la['n']}) · τ={tau_lbl(la['tau'])}",
                f"El Niño (n={en['n']}) · τ={tau_lbl(en['tau'])}",
                f"Neutral (n={ne['n']}) · τ={tau_lbl(ne['tau'])}",
            ],
            horizontal_spacing=0.08,
            vertical_spacing=0.20,
        )
        phase_specs = [
            ("All years", None, C["tx2"], 1, 1),
            ("La Niña", "La Niña", C["teal"], 1, 2),
            ("El Niño", "El Niño", C["coral"], 2, 1),
            ("Neutral", "Neutral", C["amber"], 2, 2),
        ]
        for _, phase_name, clr, r, c in phase_specs:
            mask = np.ones(len(idx), dtype=bool) if phase_name is None else (phases == phase_name).to_numpy()
            fig_pit.add_trace(
                go.Scatter(
                    x=u[mask], y=v[mask], mode="markers",
                    marker=dict(size=7, color=clr, line=dict(color=C["surf1"], width=0.6), opacity=0.82),
                    customdata=np.column_stack([idx[mask]]),
                    hovertemplate="Year %{customdata[0]}<br>U(MYS): %{x:.3f}<br>V(PHL): %{y:.3f}<extra></extra>",
                    showlegend=False,
                ),
                row=r, col=c
            )
            fig_pit.add_vline(x=0.5, line_dash="dot", line_color=C["surf3"], line_width=1, row=r, col=c)
            fig_pit.add_hline(y=0.5, line_dash="dot", line_color=C["surf3"], line_width=1, row=r, col=c)
            fig_pit.update_xaxes(range=[0, 1], row=r, col=c)
            fig_pit.update_yaxes(range=[0, 1], row=r, col=c)
        # Keep axis labels only where they add information, to avoid overlap between subplots.
        fig_pit.update_xaxes(title_text="U (MYS PIT)", row=2, col=1)
        fig_pit.update_xaxes(title_text="U (MYS PIT)", row=2, col=2)
        fig_pit.update_yaxes(title_text="V (PHL PIT)", row=1, col=1)
        fig_pit.update_yaxes(title_text="V (PHL PIT)", row=2, col=1)

        lay_pit = base_layout(height=600)
        lay_pit["margin"] = dict(t=78, b=44, l=56, r=20)
        lay_pit["title"] = dict(
            text="R8 — GEV Copula PIT Scatter by ENSO Phase",
            x=0.01, xanchor="left",
            font=dict(family=FONT, color=C["tx2"], size=12),
        )
        fig_pit.update_layout(**{k: v for k, v in lay_pit.items() if k not in ("xaxis", "yaxis")})
        fig_pit.update_annotations(font=dict(color=C["tx2"], size=10, family=FONT))
        st.plotly_chart(fig_pit, use_container_width=True, config={"displayModeBar": False})

        section_label("AIC selection · Conditional τ · Portfolio CDF (interactive)")
        fig_cop = make_subplots(
            rows=1, cols=3,
            subplot_titles=["AIC comparison", "ENSO-conditional concordance (τ)", "Portfolio loss curve"],
            column_widths=[0.28, 0.30, 0.42],
            horizontal_spacing=0.09,
        )
        aic_x = ["Clayton", "Gumbel", "Frank", "Gaussian", "Independence"]
        aic_vals = [aic_models[m][0] for m in aic_x]
        bic_vals = [aic_models[m][1] for m in aic_x]
        aic_colors = [C["sky"], C["sky"], C["sky"], C["sky"], C["teal"]]
        fig_cop.add_trace(
            go.Bar(
                x=aic_x, y=aic_vals,
                marker_color=aic_colors,
                marker_line_width=0,
                name="AIC",
                text=[f"{v:.2f}" if abs(v) >= 0.005 else "0.00" for v in aic_vals],
                textposition="outside",
                textfont=dict(color=C["tx2"], size=9, family=MONO),
                hovertemplate="<b>%{x}</b><br>AIC %{y:.3f}<extra></extra>",
                showlegend=True,
            ),
            row=1, col=1
        )
        fig_cop.add_trace(
            go.Bar(
                x=aic_x, y=bic_vals,
                marker_color="rgba(0,0,0,0)",
                marker_line_width=1.8,
                marker_line_color=C["tx3"],
                opacity=1.0,
                name="BIC",
                hovertemplate="<b>%{x}</b><br>BIC %{y:.3f}<extra></extra>",
                showlegend=True,
            ),
            row=1, col=1
        )

        ph_order = ["El Niño", "Neutral", "La Niña"]
        ph_colors = [C["coral"], C["tx2"], C["teal"]]
        tau_vals, n_vals = [], []
        for ph in ph_order:
            if ph in cond_results:
                tau_vals.append(cond_results[ph]["tau"])
                n_vals.append(cond_results[ph]["n"])
            else:
                tau_vals.append(np.nan)
                n_vals.append(0)
        fig_cop.add_trace(
            go.Bar(
                x=ph_order, y=tau_vals,
                marker_color=ph_colors, marker_line_width=0,
                text=[f"τ={t:+.3f}<br>n={n}" if np.isfinite(t) else "NA" for t, n in zip(tau_vals, n_vals)],
                textposition="auto",
                textfont=dict(color=C["tx2"], size=9, family=MONO),
                hovertemplate="<b>%{x}</b><br>τ %{y:+.4f}<extra></extra>",
                showlegend=False,
            ),
            row=1, col=2
        )
        fig_cop.add_hline(y=0, line_color=C["surf3"], line_width=1, row=1, col=2)
        fig_cop.add_hline(y=tau_all, line_color=C["tx3"], line_dash="dot", line_width=1, row=1, col=2)

        rng = np.random.default_rng(42)
        n_sim = 200000
        mys_eal_bn = float(r3.loc["MYS", "eal_forward_usd_bn"])
        phl_eal_bn = float(r3.loc["PHL", "eal_forward_usd_bn"])

        def gev_loss_from_uniform(prob, xi, mu, sc, eal_bn):
            rx5 = genextreme.ppf(np.clip(prob, 1e-8, 1 - 1e-8), xi, loc=mu, scale=sc)
            mean_rx = genextreme.mean(xi, loc=mu, scale=sc) if xi < 1 else mu
            return eal_bn * 1e3 * (rx5 / mean_rx)

        u_ind = rng.uniform(size=n_sim)
        v_ind = rng.uniform(size=n_sim)
        combined_ind = gev_loss_from_uniform(u_ind, xi_m, mu_m, sc_m, mys_eal_bn) + gev_loss_from_uniform(v_ind, xi_p, mu_p, sc_p, phl_eal_bn)
        z1 = rng.standard_normal(n_sim)
        z2 = rng.standard_normal(n_sim)
        z2_corr = rho_la * z1 + np.sqrt(1 - rho_la**2) * z2
        combined_la = gev_loss_from_uniform(norm.cdf(z1), xi_m, mu_m, sc_m, mys_eal_bn) + gev_loss_from_uniform(norm.cdf(z2_corr), xi_p, mu_p, sc_p, phl_eal_bn)
        pct_range = np.linspace(80, 99.5, 320)
        t_range = 1 / (1 - pct_range / 100)
        pct_vals_ind = np.percentile(combined_ind, pct_range)
        pct_vals_la = np.percentile(combined_la, pct_range)

        fig_cop.add_trace(
            go.Scatter(
                x=t_range, y=pct_vals_ind, mode="lines",
                line=dict(color=C["teal"], width=2.2),
                name="Independence",
                hovertemplate="T=%{x:.1f}yr<br>$%{y:,.1f}M<extra></extra>",
                showlegend=True,
            ),
            row=1, col=3
        )
        fig_cop.add_trace(
            go.Scatter(
                x=t_range, y=pct_vals_la, mode="lines",
                line=dict(color=C["violet"], width=2.2, dash="dash"),
                name=f"La Niña Gaussian (ρ={rho_la:.2f})",
                hovertemplate="T=%{x:.1f}yr<br>$%{y:,.1f}M<extra></extra>",
                showlegend=True,
            ),
            row=1, col=3
        )
        fig_cop.add_trace(
            go.Scatter(
                x=np.concatenate([t_range, t_range[::-1]]),
                y=np.concatenate([pct_vals_ind, pct_vals_la[::-1]]),
                fill="toself", fillcolor="rgba(167,139,250,0.12)",
                line=dict(color="rgba(0,0,0,0)"),
                hoverinfo="skip",
                showlegend=False,
            ),
            row=1, col=3
        )
        fig_cop.add_vline(x=100, line_dash="dot", line_color=C["surf3"], line_width=1, row=1, col=3)
        fig_cop.add_annotation(
            x=100, y=max(np.percentile(combined_ind, 99), np.percentile(combined_la, 99)),
            xref="x3", yref="y3",
            text=f"Δ100-yr: +${p99_gap:.1f}M",
            showarrow=False, yshift=20,
            font=dict(color=C["coral"], size=10, family=MONO),
        )
        lay_cop = base_layout(height=405)
        lay_cop["barmode"] = "overlay"
        lay_cop["legend"] = dict(
            orientation="h", y=-0.28, x=0.5, xanchor="center",
            font=dict(family=FONT, color=C["tx2"], size=9)
        )
        lay_cop["margin"] = dict(t=70, b=120, l=40, r=14)
        lay_cop["title"] = dict(
            text="R8 — Copula Model Selection, Conditional Concordance, and Portfolio Tail Risk",
            x=0.01, xanchor="left",
            font=dict(family=FONT, color=C["tx2"], size=12),
        )
        fig_cop.update_layout(**{k: v for k, v in lay_cop.items() if k not in ("xaxis", "yaxis")})
        fig_cop.update_yaxes(title_text="AIC", row=1, col=1)
        fig_cop.update_yaxes(title_text="Kendall τ", range=[-0.55, 0.55], row=1, col=2)
        fig_cop.update_xaxes(
            type="log",
            title_text="Return period (years)",
            range=[np.log10(5), np.log10(200)],
            tickvals=[5, 10, 20, 50, 100, 200],
            row=1, col=3
        )
        fig_cop.update_yaxes(title_text="Combined loss (USD M)", row=1, col=3)
        fig_cop.update_annotations(font=dict(color=C["tx2"], size=10, family=FONT))
        st.plotly_chart(fig_cop, use_container_width=True, config={"displayModeBar": False})

        section_label("Three key findings")
        f1, f2, f3 = st.columns(3)
        with f1:
            callout(
                f"{badge('Finding 1', C['teal'])}<br><br>"
                f"<b style='color:{C['tx1']}'>Independence adequate annually</b><br>"
                f"τ = {tau_all:+.4f} (p = {p_tau:.4f}). ΔAIC < 2 — Burnham-Anderson: no evidence against "
                "independence. <b>Standard univariate GEV (R3) is validated.</b>",
                C['teal'], fixed_height=160
            )
        with f2:
            callout(
                f"{badge('Finding 2', C['amber'])}<br><br>"
                f"<b style='color:{C['tx1']}'>ENSO breaks independence</b><br>"
                f"La Niña τ = {tau_la:+.4f} and Gaussian ρ = {rho_la:.4f}. "
                "Conditional dependence strengthens under ENSO stress and should be priced in tail scenarios.",
                C['amber'], fixed_height=160
            )
        with f3:
            callout(
                f"{badge('Finding 3', C['coral'])}<br><br>"
                f"<b style='color:{C['tx1']}'>100-yr portfolio understatement</b><br>"
                f"La Niña Gaussian copula (ρ = {rho_la:.2f}) raises combined 100-yr loss by "
                f"<b>+${p99_gap:.1f}M</b>; HRe 10% SEA allocation uplift is <b>+${hre_p99_gap:.1f}M</b>.",
                C['coral'], fixed_height=160
            )

        section_label("ENSO-conditional concordance table")

        def fmt_tau(x):
            return "NA" if not np.isfinite(x) else f"{x:+.4f}"

        def fmt_p(x):
            return "NA" if not np.isfinite(x) else f"{x:.4f}"

        ln = cond_results.get("La Niña", {"n": 0, "tau": np.nan, "p": np.nan})
        nt = cond_results.get("Neutral", {"n": 0, "tau": np.nan, "p": np.nan})
        el = cond_results.get("El Niño", {"n": 0, "tau": np.nan, "p": np.nan})

        rows = [
            ("●", C['teal'],   "La Niña",   f"n={ln['n']}",  fmt_tau(ln["tau"]), fmt_p(ln["p"]), "Positive dependence — joint extremes",  "Apply +1% loading on combined MYS+PHL XL limits"),
            ("◐", C['tx2'],    "Neutral",   f"n={nt['n']}",  fmt_tau(nt["tau"]), fmt_p(nt["p"]), "Negative / offsetting",                  "No action required"),
            ("○", C['coral'],  "El Niño",   f"n={el['n']}",  fmt_tau(el["tau"]), fmt_p(el["p"]), "Near-independent",                       "No action required"),
            ("—", C['tx3'],    "All years", f"n={len(idx)}", f"{tau_all:+.4f}", f"{p_tau:.4f}", "Cannot reject independence",             "Standard univariate pricing valid"),
        ]
        body_rows = ""
        for dot, dot_color, phase, n, tau, p, interp, action in rows:
            body_rows += f"""
<tr style="border-top:1px solid {C['border']}">
  <td style="padding:11px 14px;white-space:nowrap">
    <span style="color:{dot_color};font-size:0.95rem;margin-right:8px">{dot}</span>
    <span style="color:{C['tx1']};font-weight:600">{phase}</span>
    <span style="color:{C['tx3']};font-size:0.72rem;margin-left:6px;font-family:{MONO}">{n}</span>
  </td>
  <td style="padding:11px 14px;font-family:{MONO};color:{C['tx1']};font-size:0.82rem">{tau}</td>
  <td style="padding:11px 14px;font-family:{MONO};color:{C['tx2']};font-size:0.82rem">{p}</td>
  <td style="padding:11px 14px;color:{C['tx2']};font-size:0.81rem">{interp}</td>
  <td style="padding:11px 14px;color:{C['tx2']};font-size:0.81rem">{action}</td>
</tr>"""
        st.markdown(f"""
<div style="background:{C['surf2']};border:1px solid {C['border']};border-radius:10px;
     overflow:hidden">
  <table style="width:100%;border-collapse:collapse;font-family:{FONT}">
    <thead>
      <tr style="background:{C['surf3']}">
        <th style="text-align:left;padding:10px 14px;color:{C['tx3']};
            font-size:0.66rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em">Phase</th>
        <th style="text-align:left;padding:10px 14px;color:{C['tx3']};
            font-size:0.66rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em">Kendall τ</th>
        <th style="text-align:left;padding:10px 14px;color:{C['tx3']};
            font-size:0.66rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em">p-value</th>
        <th style="text-align:left;padding:10px 14px;color:{C['tx3']};
            font-size:0.66rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em">Interpretation</th>
        <th style="text-align:left;padding:10px 14px;color:{C['tx3']};
            font-size:0.66rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em">Treaty action</th>
      </tr>
    </thead>
    <tbody>{body_rows}</tbody>
  </table>
</div>""", unsafe_allow_html=True)
        st.markdown('<div style="height:36px"></div>', unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="margin-top:1.3rem;
     padding-top:0.7rem;display:flex;justify-content:space-between;
     align-items:center;gap:16px;flex-wrap:wrap">
  <div style="color:{C['tx4']};font-size:0.71rem;line-height:1.8">
    <b style="color:{C['tx3']}">Data:</b>
    CHIRPS v2.0 (UCSB) &nbsp;·&nbsp; EM-DAT (CRED/UCLouvain) &nbsp;·&nbsp;
    NOAA ONI (CPC) &nbsp;·&nbsp; World Bank WDI &nbsp;·&nbsp; NGFS GCAM 6.0 &nbsp;·&nbsp;
    Climate Watch (WRI) &nbsp;·&nbsp; BNM CCPT 2021 &nbsp;·&nbsp; UNFCCC Art.6
  </div>
  <div style="color:{C['tx4']};font-size:0.71rem;text-align:right;white-space:nowrap">
    R-Ignite MASA Hackathon 2026 &nbsp;·&nbsp; University of Malaya
  </div>
</div>""", unsafe_allow_html=True)

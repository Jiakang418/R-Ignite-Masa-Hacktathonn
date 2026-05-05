"""
Hannover Re SEA Climate Risk Dashboard — R-Ignite MASA Hackathon 2026
Run:  streamlit run app.py
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from scipy.stats import genextreme
from pathlib import Path

st.set_page_config(
    page_title="HRe SEA Climate Risk · R-Ignite 2026",
    page_icon="🌏",
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

html, body, .stApp, [class*="st-"], [data-testid] {{
  font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
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

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header, [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"] {{
  display: none !important;
}}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
  background: {C['surf1']} !important;
  border-right: 1px solid {C['border']} !important;
}}
[data-testid="stSidebar"] > div:first-child {{
  padding: 0 !important;
}}
[data-testid="stSidebar"] .block-container {{
  padding: 1.2rem 1.2rem 2rem 1.2rem !important;
}}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div {{
  color: {C['tx2']} !important;
  font-size: 0.8rem !important;
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
  border-bottom: 1px solid {C['border']};
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
  background: {C['surf1']};
  border: 1px solid {C['border']};
  border-top: none;
  border-radius: 0 0 10px 10px;
  padding: 1.5rem 1.5rem 2rem 1.5rem !important;
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
[data-testid="stDataFrame"] > div {{
  background: {C['surf2']} !important;
  border: 1px solid {C['border']} !important;
  border-radius: 8px !important;
  overflow: hidden !important;
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
        title_font    = dict(family=FONT, color=C['tx1'], size=13, weight=600),
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

# ── HTML / Layout helpers ─────────────────────────────────────────────────────
def card(content_fn, title="", badge="", badge_color=""):
    """Wraps a content function in a styled card."""
    hdr = ""
    if title:
        bdg = (f'<span style="background:{badge_color}22;color:{badge_color};'
               f'font-size:0.65rem;font-weight:600;padding:2px 8px;border-radius:20px;'
               f'border:1px solid {badge_color}44;margin-left:8px;letter-spacing:0.06em">'
               f'{badge}</span>') if badge else ""
        hdr = (f'<div style="font-size:0.78rem;font-weight:700;color:{C["tx2"]};'
               f'text-transform:uppercase;letter-spacing:0.09em;margin-bottom:1rem">'
               f'{title}{bdg}</div>')
    st.markdown(f'<div style="background:{C["surf2"]};border:1px solid {C["border"]};'
                f'border-radius:12px;padding:1.2rem 1.4rem;margin-bottom:1rem">'
                f'{hdr}</div>', unsafe_allow_html=True)
    content_fn()


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


def callout(text, accent=None, icon=""):
    accent = accent or C['sky']
    st.markdown(f"""
<div style="background:{accent}0d;border:1px solid {accent}33;border-left:3px solid {accent};
     border-radius:8px;padding:12px 16px;margin:8px 0;
     font-size:0.81rem;color:{C['tx2']};line-height:1.65">
  {'<span style="font-size:0.85rem;margin-right:6px">'+icon+'</span>' if icon else ''}{text}
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
    cop    = pd.read_csv(OUT/"r8_copula_results.csv").set_index("metric") if (OUT/"r8_copula_results.csv").exists() else None
    return r3, r4s, pt, gdp, cw_mys, cw_phl, cop

r3, r4s, pt_df, gdp, cw_mys, cw_phl, cop = load_data()

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
    carbon_price = st.slider("Carbon price (USD/tCO₂e)", 0, 200, 56, 1,
                             help="NGFS NZ2050 ≈ $55.6/t · 2× stress = $111/t")
    pt_rate_pct  = st.slider("Pass-through rate (%)", 1, 8, 3, 1,
                             help="IMF Fiscal Monitor 2021: 1–5% · EIOPA 2023: 3–8%")
    pt_rate = pt_rate_pct / 100.0

    st.markdown(f'<div style="color:{C["violet"]};font-size:0.65rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;margin:18px 0 10px 0">◈ Physical Risk</div>', unsafe_allow_html=True)
    show_ci   = st.checkbox("Show 95% bootstrap CI bands", value=True)
    log_scale = st.checkbox("Log-scale x-axis", value=True)

    st.markdown(f'<div style="color:{C["amber"]};font-size:0.65rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;margin:18px 0 10px 0">◎ HRe Portfolio</div>', unsafe_allow_html=True)
    sea_alloc_pct = st.slider("HRe SEA allocation (%)", 1, 25, 3, 1,
                              help="Floor 3% · Base 10% · Regional 20%")
    sea_alloc     = sea_alloc_pct / 100.0
    hre_share     = 0.08
    treaty_attach = 0.50

    st.markdown(f"""
<div style="border-top:1px solid {C['border']};margin-top:24px;padding-top:16px">
  <div style="color:{C['tx4']};font-size:0.68rem;line-height:1.8">
    CHIRPS v2.0 · EM-DAT · NOAA ONI<br>
    WDI · NGFS GCAM 6.0 · Climate Watch<br>
    BNM CCPT 2021 · UNFCCC Art.6
  </div>
</div>""", unsafe_allow_html=True)

# ── Live calcs ────────────────────────────────────────────────────────────────
BASELINE_C = 55.578
MYS_GHG    = 388.4   # 325.1 (ARIMA 2024) + 63.3 (LULUCF)
PHL_GHG    = 260.8

mys_tc   = MYS_GHG * carbon_price / 1000
phl_tc   = PHL_GHG * carbon_price / 1000
mys_pt   = mys_tc * pt_rate
phl_pt   = phl_tc * pt_rate
eal_gap  = 18.4  # USD M, MYS+PHL
pen      = 0.175
insured  = eal_gap * pen
attached = insured * treaty_attach
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
    "📈  Physical Risk — GEV",
    "🏭  Transition Risk",
    "🏦  HRe Reserve Gap",
    "🔗  Copula Analysis",
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
  PELT structural break detected at <b style="color:{C['tx1']}">2007</b> in both markets.
  Bootstrap CI n=500, seed=42.
</div>""", unsafe_allow_html=True)
    with c_desc2:
        st.markdown(f"""
<div style="background:{C['surf2']};border:1px solid {C['border']};border-radius:8px;
     padding:10px 14px;font-size:0.75rem;color:{C['tx3']};line-height:1.7">
  <b style="color:{C['tx2']}">Source</b><br>
  CHIRPS v2.0 · UCSB<br>
  WMO ETCCDI RX5day<br>
  1990–2023 · n=34
</div>""", unsafe_allow_html=True)

    # GEV chart
    return_periods = np.logspace(np.log10(2), np.log10(200), 300)
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
            ("PELT Break",           "2007",
             f"+{mys_r.uplift_pct:.1f}% post-break mean", C['teal']),
            ("EAL Pricing Gap",      f"+{mys_r.eal_pricing_gap_pct:.1f}%",
             "GEV forward vs burning cost", C['teal']),
        ])
        callout(
            f"<b style='color:{C['tx1']}'>Malaysia · Flood-dominated</b> &nbsp; "
            f"{badge('Weibull ξ='+str(round(mys_r.gev_shape_c,4)), C['teal'])} "
            f"{badge('Non-stationary preferred', C['amber'])}<br>"
            f"μ₁ = +0.48 mm/yr trend confirmed. Pre/post-2007 KS test: σ, ξ stable → "
            "location-only shift validated.",
            accent=C['teal'], icon="🇲🇾"
        )
    with col_p:
        kpi_row([
            ("100-yr Return Level",  f"{phl_r.return_level_100yr_mm:.0f} mm",
             f"CI [{phl_r.rl_100yr_ci95_lo_mm:.0f}–{phl_r.rl_100yr_ci95_hi_mm:.0f}] mm  ⚠", C['violet']),
            ("PELT Break",           "2007",
             f"+{phl_r.uplift_pct:.1f}% post-break mean", C['violet']),
            ("EAL Pricing Gap",      f"+{phl_r.eal_pricing_gap_pct:.1f}%",
             "GEV forward vs burning cost", C['violet']),
        ])
        callout(
            f"<b style='color:{C['tx1']}'>Philippines · Storm/Typhoon-dominated</b> &nbsp; "
            f"{badge('Weibull ξ='+str(round(phl_r.gev_shape_c,4)), C['violet'])} "
            f"{badge('3× CI width — n=34', C['coral'])}<br>"
            "Wide CI [326–985 mm] is not a failure; it proves single-point historical "
            "pricing is dangerous for catastrophe reserving.",
            accent=C['violet'], icon="🇵🇭"
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
        subplot_titles=[
            f"<b>Malaysia</b> — Sectors @ ${carbon_price}/t",
            f"<b>Philippines</b> — Sectors @ ${carbon_price}/t",
            "<b>Scenario</b> — MYS vs PHL Total",
        ],
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
    layout_tc["legend"]["y"] = 1.08
    layout_tc["legend"]["x"] = 0
    layout_tc["margin"] = dict(t=60, b=36, l=52, r=20)
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
    fig_tc.update_annotations(font=dict(color=C['tx2'], size=11, family=FONT))
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
        f"Malaysia = {badge('net LULUCF emitter +63.3 MtCO₂e', C['coral'])} palm oil deforestation → BNM CCPT C3/C4 surcharge (3–5%).<br>"
        f"Philippines = {badge('net LULUCF sink −26.9 MtCO₂e', C['teal'])} reforestation → Art.6.2 ITMO credits offset cost (1–2% loading).",
        accent=C['amber'], icon="📊"
    )


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

    fig_wf.add_trace(go.Waterfall(
        orientation="v",
        measure=["absolute","relative","relative","relative","total"],
        x=["Total EAL", f"× Pen {pen:.0%}", f"× Attach {treaty_attach:.0%}",
           f"× HRe {hre_share:.0%}", "HRe Physical"],
        y=[eal_gap, -(eal_gap-insured), -(insured-attached), -(attached-hre_phys), None],
        text=[f"${eal_gap:.1f}M", f"−${eal_gap-insured:.1f}M",
              f"−${insured-attached:.2f}M", f"−${attached-hre_phys:.2f}M",
              f"${hre_phys:.2f}M"],
        textposition="outside",
        textfont=dict(color=C['tx2'], size=9, family=MONO),
        connector=dict(line=dict(color=C['surf3'], dash="dot", width=1)),
        increasing=dict(marker=dict(color=C['sky'], line=dict(width=0))),
        decreasing=dict(marker=dict(color=C['coral'], opacity=0.85, line=dict(width=0))),
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
        ("Physical Exposure",   f"${hre_phys:.2f}M/yr",   f"EAL × {pen:.0%} × {treaty_attach:.0%} × {hre_share:.0%}", C['teal']),
        ("Transition (floor)",  f"${hre_tran:.1f}M/yr",   f"{pt_rate_pct}% PT · {sea_alloc_pct}% SEA alloc",           C['violet']),
        ("Combined (floor)",    f"${hre_tot:.1f}M/yr",    f"base 10% → ${hre_phys+(mys_pt+phl_pt)*1e3*hre_share*0.10:.1f}M", C['amber']),
    ])

    callout(
        f"<b style='color:{C['tx1']}'>Methodology Note — Reserve Floor, Not Final Quantum</b><br>"
        f"${hre_tot:.1f}M/yr is derived from four stacked conservative assumptions. "
        "The primary deliverable is the <b>repricing framework itself</b> — once cedant-level "
        "loss triangles are disclosed, this estimate refines by an order of magnitude.",
        accent=C['coral'], icon="⚠"
    )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Copula
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown(f"""
<div style="font-size:0.82rem;color:{C['tx2']};line-height:1.6;margin-bottom:1rem">
  Formally tests whether MYS and PHL extreme precipitation losses are independent or dependent,
  using Probability Integral Transform + four copula families.
  Key finding: <b style="color:{C['tx1']}">independence cannot be rejected annually</b>
  (τ = −0.023, p = 0.85), but
  <b style="color:{C['amber']}">La Niña introduces conditional positive dependence</b>
  (Δτ = +0.30 vs El Niño).
</div>""", unsafe_allow_html=True)

    if cop is None:
        callout("Run <code>python run_all.py</code> to generate copula outputs.", C['coral'], "⚠")
    else:
        tau_all = float(cop.loc["Kendall_tau_all","value"])
        p_tau   = float(cop.loc["p_tau_all","value"])
        tau_la  = float(cop.loc["tau_LaNina","value"])
        rho_la  = float(cop.loc["rho_gaussian_LaNina","value"])
        p99_gap = float(cop.loc["p99_gap_USD_M","value"])
        best_c  = str(cop.loc["best_copula","value"])

        kpi_row([
            ("Overall Kendall τ",    f"{tau_all:+.4f}",  f"p = {p_tau:.4f}  ·  cannot reject H₀",    C['tx3']),
            ("La Niña τ",            f"{tau_la:+.4f}",   f"vs El Niño −0.091  ·  Δτ = +0.30",         C['teal']),
            ("AIC-best copula",      best_c,             "ΔAIC < 2  ·  independence adequate",         C['tx3']),
            ("100-yr Portfolio Gap", f"+${p99_gap:.1f}M", f"La Niña ρ={rho_la:.2f} vs independence",  C['amber']),
        ])

        col_l, col_r = st.columns(2)
        with col_l:
            section_label("PIT scatter by ENSO phase")
            pit = OUT / "r8_copula_pit_scatter.png"
            if pit.exists():
                st.image(str(pit), use_container_width=True)
        with col_r:
            section_label("AIC selection · Conditional τ · Portfolio CDF")
            ca = OUT / "r8_copula_analysis.png"
            if ca.exists():
                st.image(str(ca), use_container_width=True)

        section_label("Three key findings")
        f1, f2, f3 = st.columns(3)
        with f1:
            callout(
                f"{badge('Finding 1', C['teal'])}<br><br>"
                f"<b style='color:{C['tx1']}'>Independence adequate annually</b><br>"
                f"τ = {tau_all:+.4f} (p = {p_tau:.4f}). ΔAIC < 2 — Burnham-Anderson: no evidence against "
                "independence. <b>Standard univariate GEV (R3) is validated.</b>",
                C['teal']
            )
        with f2:
            callout(
                f"{badge('Finding 2', C['amber'])}<br><br>"
                f"<b style='color:{C['tx1']}'>ENSO breaks independence</b><br>"
                f"La Niña τ = {tau_la:+.4f} vs El Niño τ = −0.09. Δτ = +0.30. "
                "Mechanism: La Niña → western Pacific warm pool → simultaneous MYS floods "
                "+ PHL typhoons (IPCC AR6 WG1 §3.3.3).",
                C['amber']
            )
        with f3:
            callout(
                f"{badge('Finding 3', C['coral'])}<br><br>"
                f"<b style='color:{C['tx1']}'>100-yr portfolio understatement</b><br>"
                f"La Niña Gaussian copula (ρ = {rho_la:.2f}) raises combined 100-yr loss by "
                f"<b>+${p99_gap:.1f}M (+1.2%)</b>. Supplements Rec.3 with a "
                "mathematically grounded reserve loading.",
                C['coral']
            )

        section_label("ENSO-conditional concordance table")
        cond_df = pd.DataFrame({
            "Phase":  ["🔵  La Niña (n=14)", "⚫  Neutral (n=9)", "🔴  El Niño (n=11)", "—  All years (n=34)"],
            "Kendall τ":  [f"{tau_la:+.4f}", "−0.3333", "−0.0909", f"{tau_all:+.4f}"],
            "p-value": ["0.3308", "0.2595", "0.7612", f"{p_tau:.4f}"],
            "Interpretation": ["Positive dependence — joint extremes", "Negative — offsetting", "Near-independent", "Cannot reject independence"],
            "Treaty action": ["Apply +1% loading on combined MYS+PHL XL limits", "No action required", "No action required", "Standard univariate pricing valid"],
        })
        st.dataframe(cond_df, hide_index=True, use_container_width=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="border-top:1px solid {C['border']};margin-top:2.5rem;
     padding-top:1.2rem;display:flex;justify-content:space-between;
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

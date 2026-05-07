"""
MASA Hackathon 2026: R-Ignite — 10-page body report (cover + 10 body pages).
Margins 1 inch, 12pt Times-Roman body font, A4.
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, HRFlowable,
)

BASE  = "/Users/a1357/Documents/GitHub/R-Ignite-Masa-Hacktathonn"
OUT_D = os.path.join(BASE, "outputs")
PDF   = os.path.join(OUT_D, "MASA_R_Ignite_Report_2026.pdf")

# ── colours ──────────────────────────────────────────────────────────────────
DARK   = colors.HexColor("#1a1a2e")
MID    = colors.HexColor("#6b2737")
ACCENT = colors.HexColor("#c0392b")
LGREY  = colors.HexColor("#f5f5f5")
LBLUE  = colors.HexColor("#eaf3f8")

PW, PH = A4
M   = 1.0 * inch
TW  = PW - 2 * M

# ── styles ────────────────────────────────────────────────────────────────────
def S(name, **kw): return ParagraphStyle(name, **kw)

BD  = S("bd",  fontName="Times-Roman",  fontSize=12, leading=14.5, alignment=TA_JUSTIFY, spaceAfter=3)
BSM = S("bsm", fontName="Times-Roman",  fontSize=10, leading=12,   alignment=TA_JUSTIFY, spaceAfter=2)
H1  = S("h1",  fontName="Times-Bold",   fontSize=15, leading=18,   spaceBefore=6, spaceAfter=4, textColor=DARK)
H2  = S("h2",  fontName="Times-Bold",   fontSize=12, leading=15,   spaceBefore=5, spaceAfter=3, textColor=MID)
BL  = S("bl",  fontName="Times-Roman",  fontSize=11, leading=13,   leftIndent=12, spaceAfter=2)
CAP = S("cap", fontName="Times-Italic", fontSize=9,  leading=11,   alignment=TA_CENTER,
        textColor=colors.HexColor("#555"), spaceAfter=3)
EXS = S("exs", fontName="Times-Roman",  fontSize=12, leading=15,   alignment=TA_JUSTIFY,
        backColor=LBLUE, borderPad=5, spaceAfter=5)
FND = S("fnd", fontName="Times-BoldItalic", fontSize=11, leading=13, textColor=MID,
        leftIndent=8, spaceAfter=4)
TH  = S("th",  fontName="Times-Bold",   fontSize=9,  leading=11,   textColor=colors.white, alignment=TA_CENTER)
TC  = S("tc",  fontName="Times-Roman",  fontSize=9,  leading=11,   alignment=TA_LEFT)
TN  = S("tn",  fontName="Times-Roman",  fontSize=9,  leading=11,   alignment=TA_CENTER)

def hr(): return HRFlowable(width=TW, thickness=0.7, color=MID, spaceAfter=4, spaceBefore=1)
def sp(h=0.06): return Spacer(1, h*inch)

def img(name, w=None, h=None):
    """Return a ReportLab Image at specified width or height, preserving aspect ratio.
    Passes explicit dimensions to the Image constructor so Table cells cannot override them."""
    p = os.path.join(OUT_D, name)
    if not os.path.exists(p):
        return Spacer(1, 0.05 * inch)
    # Read native pixel dimensions first using PIL to get the aspect ratio.
    from PIL import Image as PILImage
    with PILImage.open(p) as pil:
        px_w, px_h = pil.size
    ratio = px_w / px_h
    if w and h:
        return Image(p, width=w, height=h)
    elif w:
        return Image(p, width=w, height=w / ratio)
    elif h:
        return Image(p, width=h * ratio, height=h)
    else:
        # Natural size scaled to fit TW at most
        scale = min(1.0, TW / px_w)
        return Image(p, width=px_w * scale, height=px_h * scale)

def tbl(hdrs, rows, cws, nc=None):
    """Build a styled Table. nc = set of column indices to centre."""
    nc = nc or set()
    data = [[Paragraph(h, TH) for h in hdrs]]
    for r in rows:
        data.append([Paragraph(str(c), TN if i in nc else TC) for i, c in enumerate(r)])
    t = Table(data, colWidths=cws, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1, 0), MID),
        ("TEXTCOLOR",     (0,0), (-1, 0), colors.white),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.white, LGREY]),
        ("GRID",          (0,0), (-1,-1), 0.35, colors.HexColor("#cccccc")),
        ("TOPPADDING",    (0,0), (-1,-1), 2), ("BOTTOMPADDING",(0,0),(-1,-1),2),
        ("LEFTPADDING",   (0,0), (-1,-1), 3), ("VALIGN",       (0,0),(-1,-1),"TOP"),
    ]))
    return t

def side(a, b, wa=0.50):
    """Two-column layout."""
    wb = 1.0 - wa
    t = Table([[a, b]], colWidths=[TW*wa, TW*wb])
    t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),
                            ("LEFTPADDING",(0,0),(-1,-1),0),
                            ("RIGHTPADDING",(0,0),(-1,-1),3)]))
    return t

def bhead(text):
    t = Table([[Paragraph(text, S("bh", fontName="Times-Bold", fontSize=11,
                                  textColor=colors.white, leading=14))]],
              colWidths=[TW])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),MID),
                            ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
                            ("LEFTPADDING",(0,0),(-1,-1),5)]))
    return t

# ── Cover canvas ──────────────────────────────────────────────────────────────
class Cover:
    def __call__(self, cv, doc):
        cv.saveState()
        cv.setFillColor(DARK); cv.rect(0, 0, PW, PH, fill=1, stroke=0)
        cv.setFillColor(MID);  cv.rect(0, PH*0.52, PW, PH*0.48, fill=1, stroke=0)
        cv.setFillColor(ACCENT); cv.rect(0, PH*0.50, PW, PH*0.025, fill=1, stroke=0)

        cv.setFillColor(colors.white)
        cv.setFont("Times-Bold", 30); cv.drawCentredString(PW/2, PH*0.79, "CLIMATE RISK ASSESSMENT")
        cv.setFont("Times-Bold", 18); cv.drawCentredString(PW/2, PH*0.73,
            "Quantifying Physical & Transition Gaps")
        cv.drawCentredString(PW/2, PH*0.69, "in Hannover Re's SEA Treaty Book")

        cv.setFillColor(colors.HexColor("#f0d0d4"))
        cv.setFont("Times-Roman", 13); cv.drawCentredString(PW/2, PH*0.62,
            "MASA Hackathon 2026: R-Ignite")

        cv.setFillColor(colors.white)
        cv.setFont("Times-Bold", 12); cv.drawCentredString(PW/2, PH*0.44, "Team: UM Actuarial Consultants")
        cv.setFont("Times-Roman", 11)
        names = ["Felicia Sia Xin Rou", "Team Member 2", "Team Member 3", "Team Member 4"]
        for i, nm in enumerate(names):
            cv.drawCentredString(PW/2, PH*0.39 - i*0.17*inch, nm)
        cv.setFont("Times-Roman", 11); cv.drawCentredString(PW/2, PH*0.22, "University of Malaya")
        cv.setFont("Times-Italic", 10); cv.drawCentredString(PW/2, PH*0.18, "Submitted: 7 May 2026")
        cv.drawCentredString(PW/2, PH*0.13,
            "Data: World Bank WDI Wide Format · CHIRPS v2.0 · EM-DAT · NOAA ONI · NGFS GCAM 6.0")

        cv.setFillColor(ACCENT); cv.rect(0, 0, PW, 0.32*inch, fill=1, stroke=0)
        cv.setFillColor(colors.white); cv.setFont("Times-Roman", 8.5)
        cv.drawCentredString(PW/2, 0.10*inch,
            "Malaysian Actuarial Student Association (MASA)  ·  Strategic Partner: Hannover Re")
        cv.restoreState()

class Footer:
    def __call__(self, cv, doc):
        cv.saveState()
        cv.setStrokeColor(MID); cv.setLineWidth(1.0)
        cv.line(M, PH-M+0.15*inch, PW-M, PH-M+0.15*inch)
        cv.setFont("Times-Italic", 8.5); cv.setFillColor(colors.HexColor("#555"))
        cv.drawString(M, PH-M+0.03*inch, "MASA Hackathon 2026: R-Ignite  |  Climate Risk Assessment")
        cv.drawRightString(PW-M, PH-M+0.03*inch, "University of Malaya")
        cv.setLineWidth(0.5); cv.line(M, M-0.12*inch, PW-M, M-0.12*inch)
        pg = doc.page - 1
        cv.setFont("Times-Roman", 8.5)
        cv.drawCentredString(PW/2, M-0.25*inch, f"— {pg} —")
        cv.drawString(M, M-0.25*inch, "Confidential — For Judging Purposes Only")
        cv.drawRightString(PW-M, M-0.25*inch, "WDI · CHIRPS · EM-DAT · NOAA ONI · NGFS GCAM 6.0")
        cv.restoreState()

# ── Story ──────────────────────────────────────────────────────────────────────
def build():
    doc = SimpleDocTemplate(PDF, pagesize=A4,
        leftMargin=M, rightMargin=M,
        topMargin=M+0.22*inch, bottomMargin=M+0.18*inch,
        title="MASA R-Ignite 2026 — Climate Risk Assessment",
        author="UM Actuarial Consultants")

    cov = Cover(); ftr = Footer()

    def on_page(cv, doc):
        if doc.page == 1: cov(cv, doc)
        else:             ftr(cv, doc)

    story = [Spacer(1, 0.01*inch)]  # cover (drawn by callback)

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 1 — EXECUTIVE SUMMARY (full dedicated page, per handbook §7.3.2)
    # Handbook: "Page 1 of the report must include a one-paragraph summary."
    # ══════════════════════════════════════════════════════════════════════════
    story += [PageBreak(), Paragraph("1. Executive Summary", H1), hr()]

    # Required one-paragraph summary (handbook §7.3.2)
    story.append(Paragraph(
        "As actuarial consultants to Hannover Re, we identify <b>two additive pricing gaps</b> "
        "in the firm's SEA treaty book: a <b>physical gap</b> (USD 18.4M/yr combined EAL "
        "shortfall) from a 2007 PELT hazard regime shift in CHIRPS RX5day precipitation records "
        "undetected by burning-cost methods (+6.9% MYS flood hazard uplift; +6.1% PHL); and a "
        "<b>transition gap</b> (USD 1.1bn/yr SEA treaty pool at 3% pass-through) from NGFS "
        "GCAM 6.0 NZ2050 carbon pricing (USD 55.58/t), with a critical LULUCF asymmetry "
        "(MYS net emitter +63 MtCO2e vs PHL net sink -27 MtCO2e) requiring country-specific "
        "loadings. Five recommendations close the USD 3.4–19M/yr HRe annual under-reserve.",
        EXS))

    # Compact quantitative results table (5 rows — fits within page budget)
    story.append(Paragraph("Key Quantitative Results", H2))
    story.append(tbl(
        ["Metric", "Malaysia (MYS)", "Philippines (PHL)"],
        [["ARIMA 2024 GHG forecast (MtCO2e, MAPE)", "325.1 (1.71%)", "260.8 (3.56%)"],
         ["GEV 100-yr RX5day / PELT break / uplift", "216mm / 2007 / +6.9%", "521mm / 2007 / +6.1%"],
         ["Forward EAL gap vs. burning cost",         "+6.5M/yr (+5.87%)",   "+11.9M/yr (+1.28%)"],
         ["Transition cost (NGFS NZ2050, % GDP)",     "22.4bn/yr (5.5%)",    "14.8bn/yr (3.3%)"],
         ["HRe reserve gap — base / 2x stress",       "9.66M / 18.58M/yr",   "SEA pool: 1.115bn/yr"]],
        [TW*0.38, TW*0.31, TW*0.31], nc={1,2}))

    # Methodology (4 lines)
    story.append(Paragraph("Methodology", H2))
    story.append(Paragraph(
        "Four analytical modules are deployed: (1) <b>ARIMA GHG Forecasting</b> — AIC-selected "
        "ARIMA(p,1,q) with 3-step rolling MAPE validation on WDI WB_WDI_EN_GHG_ALL_MT_CE_AR5; "
        "(2) <b>GEV + EAL Repricing</b> — MLE-GEV on 34yr CHIRPS RX5day with 500-iteration "
        "bootstrap CI, PELT regime detection, and EM-DAT loss integration; (3) <b>ENSO "
        "Copula</b> — NOAA ONI DJF correlation tests (Pearson/Spearman/Kendall), AIC copula "
        "selection (Independence; La Nina sub-sample Gaussian rho=0.32 -> audit trigger only); "
        "and (4) <b>Transition Risk</b> — NGFS GCAM 6.0 cost gap applied to Climate Watch "
        "2023 sector GHG with 3%/yr IEA abatement trajectory, stressed 2x to 2030.", BD))

    # 5 recommendations — compact 3-column table
    story.append(Paragraph("Five Strategic Recommendations", H2))
    story.append(tbl(
        ["#", "Recommendation", "Trigger / Loading"],
        [["R1", "GEV EAL flood loading",       "+35-36% on MYS treaties >USD 50M; +1-2% floor PHL"],
         ["R2", "Country transition surcharges", "3-5% MYS (BNM CCPT C3/C4); 1-2% PHL (BSP 1085)"],
         ["R3", "ENSO audit trigger",           "ONI <= -0.5°C -> facultative audit (NOT pricing)"],
         ["R4", "Climate Warranty Clause",      "MYS LULUCF: 10% co-participation on non-disclosure"],
         ["R5", "Data procurement (0-12 mo.)",  "Loss triangles + sub-national CHIRPS -> CI +/-12pp"]],
        [TW*0.05, TW*0.30, TW*0.65]))

    # Limitations (3 lines)
    story.append(Paragraph("Key Limitations", H2))
    story.append(Paragraph(
        "The 34-year CHIRPS sample yields wide GEV bootstrap CI (PHL +/-44.5pp, addressed by R5). "
        "WDI gaps (MYS fossil fuel share and renewable share 2021–23) are excluded from models. "
        "The 3% carbon pass-through carries +/-2pp uncertainty, driving a 5x HRe reserve variance "
        "(USD 3.0–14.9M/yr). LULUCF measurement error (+/-20–30%, FAO FRA 2020) affects MYS net "
        "emitter classification. All five recommendations remain valid across these uncertainty "
        "ranges and become more precise as cedant-level data are incorporated via R5.", BD))

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 2 — Problem Framing + Data Landscape + GHG Trends
    # ══════════════════════════════════════════════════════════════════════════
    story += [PageBreak(), Paragraph("2. Problem Framing & Data Landscape", H1), hr()]
    story.append(Paragraph(
        "Hannover Re faces two structural under-pricing risks in SEA: burning-cost treaty "
        "methods pre-date the post-2007 hazard regime shift, and no current loading captures "
        "emerging carbon compliance pass-through from BNM CCPT and BSP Circular 1085. "
        "The assessment focuses on MYS (flood-dominant: 81 EM-DAT events, 1990–2023) and "
        "PHL (typhoon-dominant: 414 events) across four independent risk channels:", BD))

    story.append(tbl(["Risk Channel","Data / Model","Pricing Instrument"],
        [["Physical — Hazard",        "CHIRPS RX5day GEV + PELT",        "Treaty flood EAL loading"],
         ["Physical — Vulnerability", "WDI Urbanisation x GDP/capita",   "EAL structural trend factor"],
         ["Transition — Regulatory",  "NGFS GCAM 6.0 x Climate Watch",  "Country surcharge (3-5%)"],
         ["Transition — LULUCF",      "MYS emitter +63 vs PHL sink -27 MtCO2e","Asymmetric warranty clause"]],
        [TW*0.27, TW*0.40, TW*0.33]))

    story.append(Paragraph("2.1  Indicator Selection", H2))
    story.append(tbl(["Indicator","Type","Layer","Key Fact"],
        [["CHIRPS RX5day annual max",    "Physical",   "Hazard",       "MYS 133.9mm; PHL 244.4mm mean"],
         ["WDI Total GHG AR5 (MtCO2e)", "Phys+Trans", "ARIMA target", "MYS +271%; PHL +177% (1990-2023)"],
         ["NOAA ONI DJF anomaly",        "Physical",   "Dependence",   "ENSO inter-annual loss driver"],
         ["WDI Urban pop %",             "Physical",   "Vulnerability","MYS 49% to 76.4%; asset density"],
         ["Climate Watch Energy GHG",    "Transition", "Exposure",     "MYS 279.9 MtCO2e = 69.5% total"],
         ["Climate Watch LULUCF net",    "Transition", "Asymmetry",    "MYS +63.3 emitter; PHL -26.9 sink"],
         ["NGFS GCAM 6.0 NZ2050 price",  "Transition", "Cost scalar",  "USD 55.578/t (NZ2050 - CP gap)"],
         ["WDI GDP/capita + Forest %",   "Phys+Trans", "Loss/LULUCF",  "Penetration & carbon stock proxy"]],
        [TW*0.30, TW*0.12, TW*0.14, TW*0.44]))
    story.append(Paragraph("Table 1 — Key indicators (WDI · CHIRPS · EM-DAT · NOAA · NGFS GCAM 6.0).", CAP))

    story.append(Paragraph("2.2  GHG Trends & Sector Decomposition", H2))
    story.append(side(
        img("r1_ghg_urban_dual_axis.png",    w=TW*0.51),
        img("r1_cw_sector_decomposition.png", w=TW*0.47), wa=0.52))
    story.append(Paragraph(
        "Figure 1a — GHG vs. urbanisation MYS & PHL 1990-2023 [left]; MYS urban share +56%, "
        "compounding insured asset exposure within the same flood footprint. "
        "Figure 1b — Climate Watch 2023 sector decomposition [right]; Energy = 69.5% of MYS "
        "total; LULUCF adds +15.7% net emitter premium absent in PHL.", CAP))

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 3 — ARIMA GHG Forecasting
    # ══════════════════════════════════════════════════════════════════════════
    story += [PageBreak(), Paragraph("4. GHG Forecasting — ARIMA Model", H1), hr()]
    story.append(Paragraph(
        "Country-level ARIMA models forecast 2024 total GHG (excl. LULUCF) from WDI indicator "
        "<i>WB_WDI_EN_GHG_ALL_MT_CE_AR5</i>. Training window 1990–2020; held-out validation "
        "2021–2023 using 3-step rolling 1-step-ahead MAPE. Model selected by AIC (grid search "
        "p,q in {0,1,2}); first-difference applied after ADF stationarity test.", BD))

    story.append(tbl(
        ["Country","Model","Train AIC","MAPE","Actual 2023","Forecast 2024","95% CI (MtCO2e)"],
        [["Malaysia",    "ARIMA(1,1,1)","224.08","1.71%","318.4","325.1","[307.9, 342.3]"],
         ["Philippines", "ARIMA(2,1,0)","196.08","3.56%","254.5","260.8","[249.1, 272.4]"]],
        [TW*0.14,TW*0.15,TW*0.12,TW*0.09,TW*0.13,TW*0.13,TW*0.24], nc={2,3,4,5}))
    story.append(Paragraph("Table 2 — ARIMA forecast summary (MtCO2e excl. LULUCF).", CAP))

    story.append(side(
        img("r2_arima_mys.png", w=TW*0.49),
        img("r2_arima_phl.png", w=TW*0.49)))
    story.append(Paragraph(
        "Figure 3 — ARIMA(1,1,1) MYS [left] and ARIMA(2,1,0) PHL [right]. "
        "Shaded = 95% CI; dashed = 2024 forecast. MYS MAPE 1.71%; PHL 3.56%.", CAP))

    story.append(Paragraph("Key Improvements & Implications", H2))
    for b in [
        "<b>Improvement 1:</b> Column disambiguation — switched from deprecated EN.ATM.GHGT.KT.CE "
        "to WB_WDI_EN_GHG_ALL_MT_CE_AR5 (AR5 GWP100), correcting a 12% overcount.",
        "<b>Improvement 2:</b> Rolling validation — replaced static split with 3-step rolling "
        "1-step-ahead MAPE to prevent data leakage.",
        "<b>Improvement 3:</b> LULUCF excluded from ARIMA target; handled separately under "
        "transition risk to avoid double-counting.",
        "<b>Implication:</b> Under NGFS NZ2050 (3%/yr abatement), GHG baselines fall to "
        "317 MtCO2e (MYS) and 162 MtCO2e (PHL) by 2030 — but <i>compliance cost</i> rises "
        "as carbon prices escalate, creating peak transition exposure in 2026–2028.",
    ]:
        story.append(Paragraph(f"• {b}", BL))

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 4 — Physical Hazard: GEV & EAL
    # ══════════════════════════════════════════════════════════════════════════
    story += [PageBreak(), Paragraph("5. Physical Hazard — GEV & EAL Repricing", H1), hr()]
    story.append(Paragraph(
        "GEV distributions are fitted to 34-year CHIRPS RX5day annual maxima by MLE with "
        "500-iteration bootstrap CI (seed 42). Regime detection uses PELT (BIC penalty). "
        "EAL is integrated from the GEV survival function against EM-DAT insured loss data, "
        "with the forward EAL incorporating the post-2007 hazard uplift.", BD))

    story.append(tbl(
        ["Country","Shape xi","GEV Family","RL100 (mm)","95% CI (mm)","Break","Uplift"],
        [["Malaysia",    "-0.032","Weibull (xi<0)","216.4","[170.8, 343.6]","2007","+6.9%"],
         ["Philippines", "-0.122","Weibull (xi<0)","520.7","[326.1, 984.8]","2007","+6.1%"]],
        [TW*0.14,TW*0.10,TW*0.17,TW*0.12,TW*0.22,TW*0.10,TW*0.15], nc={3,6}))
    story.append(Paragraph("Table 3 — GEV parameters; 100-yr return levels with bootstrap 95% CI.", CAP))

    story.append(side(
        img("r3_gev_and_regime_break.png",       w=TW*0.51),
        img("r3_qq_distributional_comparison.png", w=TW*0.47), wa=0.52))
    story.append(Paragraph(
        "Figure 4a — PELT regime break 2007: +6.9% MYS, +6.1% PHL post-break mean shift [left]. "
        "Figure 4b — GEV Q-Q plots confirming Weibull family fit [right].", CAP))

    story.append(Paragraph("5.1  EAL Repricing Results", H2))
    story.append(tbl(
        ["Country","Burning Cost","Obs. Mean RX5","GEV Mean RX5","Forward EAL","Gap","Gap %"],
        [["Malaysia",    "USD 110.8M","133.9mm","132.6mm","USD 117.3M","USD 6.5M", "+5.87%"],
         ["Philippines", "USD 926.5M","244.4mm","233.3mm","USD 938.4M","USD 11.9M","+1.28%"]],
        [TW*0.14,TW*0.15,TW*0.13,TW*0.13,TW*0.15,TW*0.15,TW*0.15], nc={5,6}))
    story.append(Paragraph("Table 4 — Forward EAL vs. EM-DAT burning cost (GEV PELT-adjusted).", CAP))

    story.append(side(
        img("r3_sensitivity_tornado.png",       w=TW*0.50),
        img("r3_eal_decomposition_waterfall.png", w=TW*0.48), wa=0.51))
    story.append(Paragraph(
        "Figure 5 — Sensitivity tornado [left]: regime break uplift dominates EAL uncertainty. "
        "EAL waterfall decomposition [right]: hazard regime shift is the primary EAL driver.", CAP))

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 5 — Insurance Claims Comparison & ENSO/Copula
    # ══════════════════════════════════════════════════════════════════════════
    story += [PageBreak(), Paragraph("6. SEA Insurance Claims & ENSO Dependence", H1), hr()]
    story.append(tbl(
        ["Metric","Malaysia","Philippines"],
        [["Total EM-DAT events 1990–2023",     "89 (81 flood, 8 storm)",      "579 (414 storm, 165 flood)"],
         ["Mean annual insured EAL",           "USD 110.8M",                  "USD 926.5M"],
         ["Insurance penetration (Swiss Re)",  "~15% of economic loss",       "~8% of economic loss"],
         ["Penetration gap (insured gap/yr)",  "USD 6.5M",                    "USD 11.9M"],
         ["Primary peril",                     "Monsoonal flooding (Oct–Jan)","Typhoons (Jun–Dec)"],
         ["LULUCF status",                     "Net EMITTER +63.3 MtCO2e",   "Net SINK -26.9 MtCO2e"],
         ["Regulatory driver",                 "BNM CCPT C3/C4",             "BSP Circular 1085"],
         ["2024 ARIMA forecast (MtCO2e)",     "325.1 [307.9–342.3]",        "260.8 [249.1–272.4]"]],
        [TW*0.38, TW*0.31, TW*0.31]))
    story.append(Paragraph(
        "Table 5 — MYS vs PHL: fundamentally different peril profiles, penetration gaps, and "
        "regulatory frameworks. A uniform SEA treaty loading is actuarially incorrect.", CAP))

    story.append(Paragraph("6.1  ENSO Dependence & Copula Analysis", H2))
    # Height-constrain to 128pt so the nearly-square copula PIT scatter (ratio 1.16)
    # and the ENSO chart (ratio 1.52) share the same row height without distortion.
    story.append(side(
        img("r3_enso_dependence.png",    h=128),
        img("r8_copula_pit_scatter.png", h=128), wa=0.55))
    story.append(Paragraph(
        "Figure 6a — ENSO (ONI DJF) vs annual insured loss: r = -0.016, p = 0.93 "
        "(no significant annual correlation) [left]. "
        "Figure 6b — Copula PIT scatter (MYS vs PHL): AIC selects Independence; "
        "La Nina sub-sample (n=14) yields Gaussian rho = 0.32 [right].", CAP))

    story.append(tbl(
        ["Test","Statistic","Interpretation"],
        [["Pearson r (MYS annual)",  "r = -0.016, p = 0.93",   "Not significant"],
         ["Spearman rho (MYS)",       "rho = -0.071, p = 0.69",   "Not significant"],
         ["Pearson r (PHL annual)", "r = -0.026, p = 0.83",   "Not significant"],
         ["Copula — full sample",   "Independence (AIC=0)",   "deltaAIC = 0 vs Clayton/Gumbel"],
         ["Kendall tau — La Niña",   "tau = +0.209, n=14",       "Weak positive sub-sample dependence"],
         ["Gaussian rho — La Niña",  "rho = +0.322",             "p99 combined gap +USD 25.9M"]],
        [TW*0.30, TW*0.35, TW*0.35]))
    story.append(Paragraph("Table 6 — ENSO dependence tests and copula analysis results.", CAP))

    story.append(Paragraph(
        "<b>Finding:</b> At annual aggregation, ENSO does not price into either market's losses "
        "(p >> 0.05). However, during La Niña years (n=14), weak positive dependence emerges "
        "(rho = 0.32), creating a p99 combined-book gap of USD 25.9M. NOAA's OND La Niña outlook "
        "should be used as a TCFD facultative <i>audit trigger</i>, not a pricing variable.", FND))

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 6 — Transition Risk Assessment
    # ══════════════════════════════════════════════════════════════════════════
    story += [PageBreak(), Paragraph("7. Transition Risk — NGFS GCAM 6.0", H1), hr()]
    story.append(Paragraph(
        "Transition costs use the NGFS GCAM 6.0 Phase 4 NZ2050 vs Current Policies gap: "
        "USD 55.578/t (2024). Applied to Climate Watch 2023 sector GHG baselines to derive "
        "annual regulatory compliance costs. <b>KEY ASYMMETRY:</b> MYS is a net LULUCF "
        "emitter (+63.3 MtCO2e; palm oil deforestation) — subject to EU Deforestation Regulation "
        "and BNM CCPT Pillar 2. PHL is a net LULUCF sink (-26.9 MtCO2e; REDD+) — earns "
        "Article 6.2 ITMO credits. Applying a uniform SEA LULUCF factor overstates PHL cost ~18%.", BD))

    story.append(tbl(
        ["Sector","MYS GHG (MtCO2e)","MYS Cost (USD M)","% Total","PHL Cost (USD M)"],
        [["Energy",           "279.85","15,554","69.5%","8,935"],
         ["LULUCF",           " 63.29"," 3,518","15.7%","N/A — net sink"],
         ["Industrial Proc.", " 29.87"," 1,660"," 7.4%","  931"],
         ["Waste",            " 19.49"," 1,083"," 4.8%","  632"],
         ["Agriculture",      " 10.11","   562"," 2.5%","3,661 (rice methane)"],
         ["<b>TOTAL</b>","<b>402.6</b>","<b>22,376</b>","<b>100%</b>","<b>14,799</b>"]],
        [TW*0.22,TW*0.18,TW*0.20,TW*0.12,TW*0.28], nc={1,2,3,4}))
    story.append(Paragraph(
        "Table 7 — MYS sector GHG and NZ2050 compliance cost (USD 55.578/t). "
        "MYS total incl. LULUCF: USD 22.4bn/yr (5.5% GDP). PHL excl. sink: USD 14.8bn/yr (3.3% GDP).", CAP))

    # Wide-aspect charts (ratio ~2.45): use 65% page width for readable bar labels.
    story.append(side(
        img("r4_exhibit2a_mys_sectors.png", w=TW*0.54),
        img("r4_exhibit2b_mys_vs_phl.png",  w=TW*0.43), wa=0.55))
    story.append(Paragraph(
        "Figure 7a — MYS sector decomposition at NGFS NZ2050 price [left, 63% width]. "
        "Figure 7b — Country comparison: MYS incl. LULUCF vs PHL excl. sink [right].", CAP))

    story.append(Paragraph("7.1  Pass-Through to Treaty Pool", H2))
    story.append(tbl(
        ["Scenario","Carbon Price","MYS Pool","PHL Pool","SEA Total"],
        [["Current Policies",    "USD 0/t",      "USD 0",     "USD 0",     "USD 0"],
         ["NGFS NZ2050 Baseline","USD 55.578/t","USD 672M", "USD 444M", "USD 1,115M"],
         ["Stress: NZ2050 x 2", "USD 111/t",   "USD 1,295M","USD 888M", "USD 2,230M"]],
        [TW*0.30,TW*0.16,TW*0.18,TW*0.18,TW*0.18], nc={1,2,3,4}))
    story.append(Paragraph("Table 8 — Annual transition pass-through to SEA treaty pool (3% rate, 50% attachment).", CAP))

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 7 — Stress Testing & 2030 Projections
    # ══════════════════════════════════════════════════════════════════════════
    story += [PageBreak(), Paragraph("8. Stress Testing & 2030 Projections", H1), hr()]
    story.append(Paragraph(
        "Using ARIMA 2024 as GHG baseline, we project NZ2050 costs to 2030 under 3%/yr linear "
        "IEA abatement. Carbon prices escalate from USD 28.2/t (2024) to USD 55.6/t (2030).", BD))
    story.append(img("r4_transition_cost_trajectory.png", w=TW * 0.90))
    story.append(Paragraph(
        "Figure 8 — Annual transition compliance cost 2024–2030 (NGFS NZ2050): "
        "combined MYS+PHL reaches USD 26.6bn/yr by 2030.", CAP))

    story.append(tbl(
        ["Year","C-Price ($/t)","MYS (USDbn)","PHL (USDbn)","Combined (USDbn)","HRe Floor","HRe Base"],
        [["2024","28.23","10.75","5.49","16.24","USD 0.49bn","USD 1.30bn"],
         ["2026","37.35","13.38","6.83","20.21","USD 0.60bn","USD 1.62bn"],
         ["2028","46.46","15.66","8.00","23.66","USD 0.71bn","USD 1.89bn"],
         ["2030","55.58","17.63","9.00","26.63","USD 0.81bn","USD 2.13bn"]],
        [TW*0.09,TW*0.13,TW*0.13,TW*0.13,TW*0.18,TW*0.17,TW*0.17], nc={1,2,3,4}))
    story.append(Paragraph(
        "Table 9 — 2024–2030 trajectory. HRe cols: 8% APAC share x 50% attachment x 3%/10% SEA alloc.", CAP))

    story.append(Paragraph("8.1  Stress Scenario Design", H2))
    story.append(tbl(["Scenario","Assumption","HRe 2030 Impact"],
        [["Baseline NZ2050",         "USD 55.578/t x GHG 2023",                    "USD 2.13bn/yr (base)"],
         ["Carbon 2x Stress",        "USD 111/t (doubled NZ2050)",                 "USD 4.25bn/yr"],
         ["PELT Uplift",             "+6.9%/+6.1% hazard to forward EAL",          "+USD 1.3M/yr physical"],
         ["Combined Stress",         "2x carbon + full PELT + La Niña rho=0.32",     "Binding capital constraint"],
         ["La Niña Correlation",     "Gaussian copula rho=0.32 activated (p99)",     "+USD 2.59M (10% alloc.)"]],
        [TW*0.25,TW*0.43,TW*0.32]))
    story.append(Paragraph("Table 10 — Stress scenarios and Hannover Re impacts.", CAP))

    for b in [
        "By 2030, combined compliance cost reaches <b>USD 26.6bn/yr</b> even under conservative "
        "3%/yr abatement — driven by carbon price escalation, not emission growth.",
        "HRe base-case reserve gap (10% SEA alloc.) reaches <b>USD 2.13bn/yr by 2030</b> "
        "vs. USD 9.66M today — a 22x amplification in 6 years under unchanged treaty pricing.",
        "The 2x carbon stress at 2030 represents the binding capital constraint for SEA "
        "underwriting capacity and triggers mandatory Climate Warranty Clause activation.",
    ]:
        story.append(Paragraph(f"• {b}", BL))

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 8 — Financial Impact (HRe Numbers)
    # ══════════════════════════════════════════════════════════════════════════
    story += [PageBreak(), Paragraph("9. Financial Impact — HRe Reserve Implications", H1), hr()]
    story.append(Paragraph(
        "Top-down reserve estimates are calibrated from Hannover Re 2023 Annual Report (8% APAC "
        "non-life market share), Swiss Re Sigma 1/2024 (50% treaty attachment for SEA), and "
        "BNM/BSP data (3–10% SEA sub-book allocation). These produce a conservative floor and "
        "a base-case estimate of the annual under-reserving position.", BD))

    story.append(tbl(["Metric","Value","Basis"],
        [["Physical EAL Gap (MYS+PHL)",        "USD 18.4M/yr",  "GEV forward EAL - EM-DAT burning cost"],
         ["HRe Physical Exposure",             "USD 0.74M/yr",  "18.4M x 8% share x 50% attach."],
         ["SEA Transition Pool (3% PT)",       "USD 1,115M/yr", "Baseline NZ2050 pass-through"],
         ["HRe Transition Floor (3% alloc.)",  "USD 2.68M/yr",  "1,115M x 8% x 50% x 3% SEA"],
         ["HRe Combined — FLOOR",              "USD 3.41M/yr",  "Conservative: 3% alloc., baseline C"],
         ["HRe Combined — BASE CASE",          "USD 9.66M/yr",  "10% alloc., 3% PT, baseline carbon"],
         ["HRe Combined — STRESS (2xC)",       "USD 18.58M/yr", "10% alloc., 3% PT, 2x carbon"],
         ["p99 La Niña Correlated Gap",        "USD 2.59M/yr",  "10% alloc., Gaussian copula rho=0.32"]],
        [TW*0.42,TW*0.18,TW*0.40], nc={1}))
    story.append(Paragraph(
        "Table 11 — HRe annual reserve gap. Floor is conservative lower bound; "
        "refined by cedant-level loss triangles under Recommendation 5.", CAP))

    story.append(Paragraph(
        "<b>Methodology note:</b> The floor estimate of USD 3.41M/yr derives from four stacked "
        "macro assumptions (each independently sourced). The primary deliverable is the repricing "
        "<i>methodology</i> — not the initial dollar quantum. Cedant-level triangles will "
        "refine this by an order of magnitude.", FND))

    story.append(Paragraph("9.1  Insurance Penetration Gap", H2))
    story.append(tbl(["Country","Penetration","Economic Gap/yr","Insured Gap Range","Treaty Implication"],
        [["Malaysia",    "15%","USD 6.5M","USD 0.65–1.30M","EAL understated +5.87%"],
         ["Philippines", " 8%","USD 11.9M","USD 0.59–1.78M","EAL understated +1.28%"]],
        [TW*0.13,TW*0.13,TW*0.18,TW*0.20,TW*0.36], nc={1}))
    story.append(Paragraph("Table 12 — Insurance penetration gap (Swiss Re Sigma 2023 SEA benchmarks).", CAP))

    story.append(Paragraph("9.2  CI-Derived Loading from Bootstrap Uncertainty", H2))
    story.append(Paragraph(
        "The 34-year CHIRPS sample (n=34) produces wide bootstrap CI on GEV return levels, "
        "particularly for PHL (CI range = 985-326 = 659mm for the 100yr return level). "
        "Following Hosking-Wallis (1997), we derive an additional CI-loading to compensate "
        "for estimation uncertainty: MYS +29.5pp and PHL +44.5pp of base loading. "
        "These are reduced to approximately +/-12pp when sample size reaches n=43 "
        "(Recommendation 5 procurement target).", BD))
    story.append(img("r4_rec4_ci_loading.png", w=TW * 0.88))
    story.append(Paragraph(
        "Figure 9 — CI-derived loading by country: MYS +29.5pp; PHL +44.5pp (n=34 sample).", CAP))

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 9 — Strategic Recommendations
    # ══════════════════════════════════════════════════════════════════════════
    story += [PageBreak(), Paragraph("10. Strategic Risk Management Recommendations", H1), hr()]
    story.append(Paragraph(
        "Five interconnected recommendations address both pricing gaps with explicit triggers, "
        "loadings, and governance protocols derived directly from the quantitative analysis.", BD))

    recs_data = [
        ["R1","EAL-Calibrated Flood Loading",
         "Trigger: MYS treaties > USD 50M. Replace EM-DAT burning cost with GEV forward EAL. "
         "Apply +35–36% flood loading (MYS property cat treaties). Apply +1–2% floor (PHL). "
         "Basis: GEV PELT uplift + bootstrap CI mid-point."],
        ["R2","Country-Specific Transition Surcharges",
         "MYS 3–5% surcharge (BNM CCPT C3/C4 cedants; LULUCF emitter status warrants Climate "
         "Warranty Clause at renewal). PHL 1–2% surcharge (lower GHG intensity; LULUCF sink "
         "credits partially offset). Re-evaluate at each NGFS Phase update."],
        ["R3","ENSO Conditional Audit Protocol",
         "Trigger: NOAA OND ONI <= -0.5°C (La Niña onset). Activate facultative audit of "
         "combined MYS+PHL book. If audit shows >15% exposure increase, apply PELT uplift "
         "(+6.9% flood treaties). ENSO is an AUDIT TRIGGER only — not a pricing variable."],
        ["R4","Climate Warranty Clause",
         "Apply to MYS cedants with LULUCF-exposed operations (palm oil, plantation forestry). "
         "Terms: 10% co-participation on non-disclosure of LULUCF emission change >10% vs prior "
         "year. Aligned with Lloyd's ESG Guidance 2023 and BNM CCPT Pillar 2."],
        ["R5","Cedant Data Procurement Roadmap",
         "0–12 month horizon: procure cedant-level 10+ year loss triangles and sub-national "
         "CHIRPS 0.05° grids. Increases effective sample n=34 -> n>=43 (Hosking-Wallis), "
         "reducing CI loading from +44.5pp (PHL) to approximately +/-12pp."],
    ]
    for code, title, detail in recs_data:
        story.append(bhead(f"{code} — {title}"))
        story.append(Paragraph(detail, BD))
        story.append(sp(0.03))

    story.append(img("r4_rec1_treaty_threshold.png", w=TW * 0.92))
    story.append(Paragraph(
        "Figure 10 — R1 treaty threshold calibration: GEV EAL-based loading vs. EM-DAT burning cost.", CAP))

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE 10 — Limitations, Scalability & Conclusion
    # ══════════════════════════════════════════════════════════════════════════
    story += [PageBreak(), Paragraph("11. Limitations, Scalability & Conclusion", H1), hr()]

    story.append(Paragraph("11.1  Key Limitations & Uncertainties", H2))
    for lim in [
        "<b>Sample size (n=34):</b> PHL GEV bootstrap CI spans [326, 985mm] — a 3x range "
        "demanding floor-loading only, not point-estimate pricing. Resolved by R5.",
        "<b>WDI data gaps:</b> MYS fossil fuel share (2021–23 gap, flagged as 0.0 not true zero); "
        "MYS renewable share (2022–23 missing). Excluded from quantitative models.",
        "<b>ARIMA post-2023 structure:</b> Assumes no structural policy break; Malaysia's NETR "
        "2023 could accelerate decarbonisation, making our transition cost estimate conservative.",
        "<b>Pass-through uncertainty:</b> 3% rate carries +/-2pp uncertainty (Swiss Re Sigma), "
        "driving a 5x range in HRe reserve variance (USD 3.0M to USD 14.9M/yr at 10% alloc.).",
        "<b>LULUCF measurement:</b> Climate Watch LULUCF estimates carry +/-20–30% uncertainty "
        "(FAO FRA 2020). MYS net emitter status could narrow with next FRA cycle (2025).",
        "<b>Copula power:</b> n=34 annual observations limit copula tail dependence estimation; "
        "La Niña sub-sample (n=14) insufficient for robust block-maxima GEV.",
    ]:
        story.append(Paragraph(f"• {lim}", BL))

    story.append(Paragraph("11.2  Scalability & Industry Implementation", H2))
    story.append(tbl(["Initiative","Implementation Path"],
        [["ASEAN expansion",     "Apply GEV+ARIMA to Thailand, Indonesia, Vietnam via same CHIRPS/WDI pipeline"],
         ["Sub-national grids",  "Replace country-averaged CHIRPS with 0.05°x0.05° cedant-coordinate EAL"],
         ["NGFS auto-refresh",   "Rebuild cost trajectory in <2 hours on each NGFS Phase release"],
         ["Cedant integration",  "Embed CI loading as treaty pricing rule: countryin{MYS,PHL} + CCPT -> surcharge"],
         ["TCFD alignment",      "Map all 5 recommendations to TCFD Strategy, Risk Mgmt, Metrics & Targets"]],
        [TW*0.22,TW*0.78]))
    story.append(Paragraph("Table 13 — Scalability roadmap for broader portfolio adoption.", CAP))

    story.append(Paragraph("11.3  Conclusion", H2))
    story.append(Paragraph(
        "This analysis establishes two independently quantified, additive pricing gaps in "
        "Hannover Re's SEA treaty book. The physical gap (USD 18.4M/yr EAL shortfall) stems "
        "from a 2007 hazard regime shift undetected by standard burning-cost methods. The "
        "transition gap (USD 1.1bn/yr SEA pool at current pass-through) reflects carbon price "
        "escalation under NGFS NZ2050, with a critical MYS/PHL LULUCF asymmetry that uniform "
        "SEA factors cannot capture. Both gaps compound to a USD 9.66M/yr base-case HRe under-"
        "reserve, rising to USD 2.13bn/yr by 2030. The five recommendations — implemented in "
        "sequence from immediate treaty repricing to 12-month data procurement — translate these "
        "modelling outputs directly into contract-specific pricing actions. The accompanying "
        "Streamlit interactive dashboard (outputs/interactive_stress_test.html) provides live "
        "decision support aligned with BNM CCPT and TCFD disclosure requirements.", BD))

    story.append(sp(0.06))
    story.append(hr())
    story.append(Paragraph(
        "<b>AI Usage Declaration:</b> Claude Sonnet 4.6 (Anthropic) assisted with code "
        "structuring, output interpretation, and report drafting. All quantitative outputs, "
        "model parameters, and financial calculations were independently verified by the team "
        "against primary source data. All AI-generated content has been reviewed and validated.", BSM))

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f"✅  Report -> {PDF}")

if __name__ == "__main__":
    build()

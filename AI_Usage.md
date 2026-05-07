# AI Usage Disclosure — MASA Hackathon 2026

**Team:** Numbers
**Submission:** Quantifying Climate Risk & Pricing Adequacy in SEA — Hannover Re

---

## Summary

AI tools were used **strictly for assistance** — code optimization, documentation drafting, and brainstorming only. All core actuarial logic, methodology design, data sourcing, model selection, and interpretation were developed independently by our team.

---

## Tools Used

| Tool | Version | Purpose |
|------|---------|---------|
| Claude Sonnet 4.6 (Anthropic) | May 2026 | Code optimization, documentation drafting, script structuring |
| Cursor (cursor.com) | May 2026 | In-editor debugging assistance, error diagnosis, code navigation |
| GitHub Copilot | — | In-editor code completion suggestions |

---

## What AI Did

- Helped restructure Python functions for readability 
- Suggested docstring and comment phrasing
- Assisted in formatting table layouts in `python-docx`
- Cursor used for in-editor debugging: tracing runtime errors, stack traces, and import issues in notebooks and scripts

---

## What AI Did Not Do

- AI did not design, select, or tune any statistical model (ARIMA, GEV, PELT, copula families)
- AI did not choose which datasets to use or how to interpret results
- AI did not derive the pass-through rate, BNM CCPT regulatory anchors, or NGFS carbon price path
- AI did not write the actuarial logic in notebooks 01–08
- All numbers in the submission are sourced directly from public datasets (CHIRPS, EM-DAT, NOAA ONI, World Bank WDI, NGFS GCAM 6.0, Climate Watch) and verified by team members independently of any AI output

---

## Verification Statement

Every quantitative claim in this submission — return levels, EAL gaps, carbon compliance costs, HRe reserve estimates, and pass-through rates — is traceable to a specific row in `outputs/*.csv`, which is itself reproducible by running `python run_all.py` from the repository root.

We confirm that no AI tool was used to fabricate, hallucinate, or generate data values. All outputs are reproducible without AI assistance.

---

*Signed by all team members: Khe Jia Kang, Lean Wen Jie, Lee Jing Xuan, Lau Hiap Meng, Felicia Sia Xin Rou*

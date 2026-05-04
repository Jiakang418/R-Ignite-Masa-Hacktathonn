"""
EXHIBIT 2: THE TRANSITION RISK COST (SENSITIVITY ANALYSIS - EXCLUDING LULCF)
Transition Risk Quantification for Malaysian Cedant Industries

This script calculates the annual transition cost each sector faces under
Net Zero 2050 vs. Current Policies climate scenarios, EXCLUDING the Land Use,
Land-Use Change and Forestry (LULCF) sector.

This is a SENSITIVITY ANALYSIS to show impact of sector exclusions.

Inputs:
- NGFS: Malaysia carbon price projections (Current Policies vs. Net Zero 2050)
- Climate Watch: Malaysia sector-level GHG emissions baseline (2023), excluding LULCF

Output:
- Sector-by-sector transition cost exposure (ranked by cost), 4 sectors (vs 5 in primary)
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

# NOTE: Outputs already in outputs/exhibit_2_transition_cost_results_excluding_LULCF.csv
# Place NGFS file in data/raw/ to re-run.
DATA_DIR = Path("../data/raw")
NGFS_CSV_FILE = Path("../data/processed") / "ngfs_carbon_price_mys_phl.csv"
NGFS_XLSX_FILE = DATA_DIR / "Downscaled_GCAM 6.0 NGFS_data.xlsx"
GHG_FILE = DATA_DIR / "ghg-emissions excluding LULCF.csv"  # SENSITIVITY: EXCLUDING LULCF

CARBON_PRICE_YEAR = 2027  # Mid-range year for analysis
REGION = "MYS"
CARBON_PRICE_VAR = "Price|Carbon"

# ============================================================================
# STEP 1: LOAD NGFS DATA
# ============================================================================

print("=" * 80)
print("EXHIBIT 2: TRANSITION RISK COST ANALYSIS (SENSITIVITY: EXCLUDING LULCF)")
print("=" * 80)

# ── Graceful degradation: skip if NGFS absent but pre-computed outputs exist ──
_ngfs_present = NGFS_CSV_FILE.exists() or NGFS_XLSX_FILE.exists()
if not _ngfs_present:
    _pre = Path("../outputs/exhibit_2_transition_cost_results_excluding_LULCF.csv")
    if _pre.exists():
        print(f"\n⚠  NGFS raw file not found in: {DATA_DIR}")
        print(f"   Pre-computed output already exists: {_pre}")
        print("   Skipping analysis. Place NGFS data in data/raw/ to regenerate.")
        exit(0)
    else:
        print(f"\n❌  NGFS raw file not found AND no pre-computed output exists.")
        print(f"   Required: '{NGFS_CSV_FILE.name}' or '{NGFS_XLSX_FILE.name}' in {DATA_DIR}")
        exit(1)

print("\n[Step 1] Loading NGFS data...")

# Try CSV first, then XLSX
try:
    print(f"  Attempting to load CSV: {NGFS_CSV_FILE}")
    # Try different encodings for CSV
    for encoding in ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']:
        try:
            ngfs_df = pd.read_csv(NGFS_CSV_FILE, low_memory=False, encoding=encoding)
            print(f"  ✓ CSV loaded (encoding: {encoding}): {ngfs_df.shape[0]} rows, {ngfs_df.shape[1]} columns")
            break
        except (UnicodeDecodeError, pd.errors.ParserError):
            continue
    else:
        raise ValueError("Could not load CSV with any encoding, trying XLSX...")
except (FileNotFoundError, ValueError):
    print(f"  CSV not found or unreadable, trying XLSX: {NGFS_XLSX_FILE}")
    ngfs_df = pd.read_excel(NGFS_XLSX_FILE)
    print(f"  ✓ XLSX loaded: {ngfs_df.shape[0]} rows, {ngfs_df.shape[1]} columns")
except Exception as e:
    print(f"  ❌ Error loading NGFS: {e}")
    exit(1)

# ============================================================================
# STEP 2: EXTRACT MALAYSIA CARBON PRICES
# ============================================================================

print("\n[Step 2] Extracting Malaysia carbon prices...")

# Filter for Malaysia carbon price data
carbon_price_data = ngfs_df[
    (ngfs_df["Region"] == REGION) &
    (ngfs_df["Variable"] == CARBON_PRICE_VAR)
].copy()

print(f"  ✓ Found {carbon_price_data.shape[0]} scenario rows for Malaysia carbon price")

if carbon_price_data.shape[0] == 0:
    print(f"\n  ❌ ERROR: No data found for Region={REGION}, Variable={CARBON_PRICE_VAR}")
    print(f"\n  Debug Info:")
    print(f"    Unique regions: {ngfs_df['Region'].unique()[:10]}")
    print(f"    Unique variables: {ngfs_df['Variable'].unique()[:10]}")
    exit(1)

# Get unique scenarios
mys_scenarios = carbon_price_data["Scenario"].unique()
print(f"\n  Scenarios found for Malaysia carbon price:")
for i, scenario in enumerate(mys_scenarios, 1):
    print(f"    {i}. {scenario}")

# ============================================================================
# STEP 3: EXTRACT CARBON PRICES FOR BOTH SCENARIOS
# ============================================================================

print(f"\n[Step 3] Extracting carbon prices for year {CARBON_PRICE_YEAR}...")

current_pol_price = None
net_zero_price = None
current_pol_scenario = None
net_zero_scenario = None

# Detect scenarios by price profile:
# Current Policies = $0 at CARBON_PRICE_YEAR (scenario with zero or near-zero price)
# Net Zero 2050    = highest positive price at CARBON_PRICE_YEAR (scenario 4 = $55.578)
scenario_prices = {}
for scenario in mys_scenarios:
    scenario_data = carbon_price_data[carbon_price_data["Scenario"] == scenario]
    if len(scenario_data) > 0 and str(CARBON_PRICE_YEAR) in scenario_data.columns:
        price = float(scenario_data.iloc[0][str(CARBON_PRICE_YEAR)])
        scenario_prices[scenario] = price
        print(f"  Scenario {scenario}: ${price:.3f}/ton at {CARBON_PRICE_YEAR}")

if not scenario_prices:
    print(f"\n  ❌ ERROR: No scenario price data found for year {CARBON_PRICE_YEAR}")
    exit(1)

# Current Policies = scenario whose 2027 price is 0 (or closest to 0)
current_pol_scenario = min(scenario_prices, key=lambda s: abs(scenario_prices[s]))
current_pol_price    = scenario_prices[current_pol_scenario]

# Net Zero 2050 = scenario with price matching expected $55.578 range
nz_candidates = {s: p for s, p in scenario_prices.items() if p > 50 and p < 70}
if nz_candidates:
    net_zero_scenario = max(nz_candidates, key=lambda s: nz_candidates[s])
else:
    net_zero_scenario = max(scenario_prices, key=lambda s: scenario_prices[s])
net_zero_price = scenario_prices[net_zero_scenario]

print(f"  ✓ Current Policies scenario: {current_pol_scenario} — ${current_pol_price:.3f}/ton at {CARBON_PRICE_YEAR}")
print(f"  ✓ Net Zero 2050 scenario:   {net_zero_scenario} — ${net_zero_price:.3f}/ton at {CARBON_PRICE_YEAR}")

if current_pol_price is None or net_zero_price is None:
    print(f"\n  ❌ ERROR: Could not extract prices for both scenarios")
    exit(1)

# ============================================================================
# STEP 4: LOAD CLIMATE WATCH GHG (EXCLUDING LULCF)
# ============================================================================

print(f"\n[Step 4] Loading Climate Watch sector GHG emissions (EXCLUDING LULCF)...")

try:
    ghg_df = pd.read_csv(GHG_FILE)
    print(f"  ✓ Climate Watch (excluding LULCF) loaded: {ghg_df.shape[0]} sectors")
except FileNotFoundError:
    print(f"  ❌ ERROR: Climate Watch file not found: {GHG_FILE}")
    exit(1)

# Get most recent year
available_years = sorted([col for col in ghg_df.columns if col.isdigit()], reverse=True)
latest_year = int(available_years[0])
print(f"  ✓ Most recent year available: {latest_year}")

# Extract sector emissions
sector_emissions = {}
print(f"\n  Sector emissions ({latest_year}):")
for idx, row in ghg_df.iterrows():
    sector = row["Sector"]
    emissions = row[str(latest_year)]
    if pd.notna(emissions):
        sector_emissions[sector] = float(emissions)
        print(f"    {sector:45s}: {emissions:>10.2f} MtCO2e")

# ============================================================================
# STEP 5: CALCULATE TRANSITION COSTS
# ============================================================================

print(f"\n[Step 5] Calculating transition costs with Dynamic Stress Scenarios & Pass-Through...")

carbon_price_diff = net_zero_price - current_pol_price
print(f"\n  Carbon price differential (Net Zero - Current Policies):")
print(f"    {net_zero_price:.2f} - {current_pol_price:.2f} = ${carbon_price_diff:.2f}/ton CO2e")

STRESS_MULTIPLIER = 2.0
PASS_THROUGH_RATES = [0.01, 0.03, 0.05]
DEFAULT_PT_RATE = 0.03

transition_costs = {}
all_scenario_results = []
for sector, emissions_mtco2e in sector_emissions.items():
    # Match the primary R4 methodology so the LULUCF exclusion is a like-for-like sensitivity.
    base_cost_usd = emissions_mtco2e * carbon_price_diff * 1_000_000
    transition_costs[sector] = base_cost_usd / 1_000_000

    for pt_rate in PASS_THROUGH_RATES:
        baseline_cost_usd = emissions_mtco2e * carbon_price_diff * pt_rate * 1_000_000
        stress_cost_usd = emissions_mtco2e * (carbon_price_diff * STRESS_MULTIPLIER) * pt_rate * 1_000_000
        all_scenario_results.append({
            "Sector": sector,
            "Pass_Through_Rate": f"{pt_rate * 100:.0f}%",
            "Baseline_Cost_USD_Millions": baseline_cost_usd / 1_000_000,
            "Stress_Cost_USD_Millions": stress_cost_usd / 1_000_000,
        })

# Sort by cost (descending)
sorted_costs = sorted(transition_costs.items(), key=lambda x: x[1], reverse=True)

stress_output_file = Path("../outputs/r4_stress_scenario_table_excluding_LULCF.csv")
pd.DataFrame(all_scenario_results).to_csv(stress_output_file, index=False)
print(f"  ✓ Stress scenarios exported to: {stress_output_file}")

# ============================================================================
# STEP 6: CREATE RESULTS TABLE
# ============================================================================

print(f"\n[Step 6] Creating results table...")

results = []
for rank, (sector, cost) in enumerate(sorted_costs, 1):
    results.append({
        "Rank": rank,
        "Sector": sector,
        "GHG_Baseline_MtCO2e": sector_emissions[sector],
        "Current_Pol_Price_USD_per_ton": current_pol_price,
        "Net_Zero_Price_USD_per_ton": net_zero_price,
        "Price_Diff_USD_per_ton": carbon_price_diff,
        "Annual_Transition_Cost_USD_Millions": cost
    })

results_df = pd.DataFrame(results)

# ============================================================================
# STEP 7: DISPLAY RESULTS
# ============================================================================

print("\n" + "=" * 80)
print("EXHIBIT 2: TRANSITION RISK COST RANKING (EXCLUDING LULCF)")
print("=" * 80)

print(f"\nAnalysis Parameters:")
print(f"  Region: Malaysia (MYS)")
print(f"  GHG Baseline Year: {latest_year}")
print(f"  Carbon Price Year: {CARBON_PRICE_YEAR}")
print(f"  Current Policies Scenario: {current_pol_scenario}")
print(f"  Net Zero Scenario: {net_zero_scenario}")
print(f"  Current Policies Carbon Price: ${current_pol_price:.2f}/ton CO2e")
print(f"  Net Zero 2050 Carbon Price: ${net_zero_price:.2f}/ton CO2e")
print(f"  Price Differential: ${carbon_price_diff:.2f}/ton CO2e")
print(f"  Sectors Included: 4 (excluding LULCF)")

print("\n" + "=" * 80)
print("SECTOR-BY-SECTOR TRANSITION COST EXPOSURE")
print("=" * 80 + "\n")

# Format for display
display_df = results_df.copy()
display_df["GHG_Baseline_MtCO2e"] = display_df["GHG_Baseline_MtCO2e"].apply(lambda x: f"{x:.2f}")
display_df["Current_Pol_Price_USD_per_ton"] = display_df["Current_Pol_Price_USD_per_ton"].apply(lambda x: f"${x:.2f}")
display_df["Net_Zero_Price_USD_per_ton"] = display_df["Net_Zero_Price_USD_per_ton"].apply(lambda x: f"${x:.2f}")
display_df["Price_Diff_USD_per_ton"] = display_df["Price_Diff_USD_per_ton"].apply(lambda x: f"${x:.2f}")
display_df["Annual_Transition_Cost_USD_Millions"] = display_df["Annual_Transition_Cost_USD_Millions"].apply(lambda x: f"${x:,.0f}M")

print(display_df.to_string(index=False))

# Calculate totals
total_cost = results_df["Annual_Transition_Cost_USD_Millions"].sum()
print("\n" + "-" * 80)
print(f"TOTAL ANNUAL TRANSITION COST (Excluding LULCF): ${total_cost:,.0f}M")
print("-" * 80)

# Add percentages
print("\nSector % of Total Cost:")
for rank, (sector, cost) in enumerate(sorted_costs, 1):
    pct = (cost / total_cost) * 100
    print(f"  {rank}. {sector:45s}: {pct:>6.1f}%")

# ============================================================================
# STEP 8: EXPORT RESULTS
# ============================================================================

print(f"\n[Step 8] Exporting results...")

# Create clean export dataframe
export_df = results_df.copy()
export_df["% of Total"] = (export_df["Annual_Transition_Cost_USD_Millions"] / total_cost * 100).round(1)

output_file = Path("../outputs/exhibit_2_transition_cost_results_excluding_LULCF.csv")
export_df.to_csv(output_file, index=False)
print(f"  ✓ Results saved to: {output_file}")

# ============================================================================
# STEP 9: SENSITIVITY COMPARISON
# ============================================================================

print("\n" + "=" * 80)
print("SENSITIVITY ANALYSIS: LULCF IMPACT")
print("=" * 80)

primary_output_file = Path("../outputs/exhibit_2_transition_cost_results.csv")
primary_df = pd.read_csv(primary_output_file)
primary_total = primary_df["Annual_Transition_Cost_USD_Millions"].sum()
lulucf_impact = primary_total - total_cost
lulucf_pct = (lulucf_impact / primary_total * 100) if primary_total else float("nan")

print(f"\nComparison with PRIMARY ANALYSIS (including LULCF):")
print(f"  Primary Total (5 sectors):        ${primary_total:>10,.2f}M")
print(f"  Sensitivity Total (4 sectors):    ${total_cost:>10,.2f}M")
print(f"  LULCF Sector Impact:              ${lulucf_impact:>10,.2f}M ({lulucf_pct:.1f}%)")

# Dynamic energy-sector burden percentages
_energy_primary = primary_df[primary_df["Sector"] == "Energy"]["Annual_Transition_Cost_USD_Millions"].sum()
_energy_sensit  = results_df[results_df["Sector"] == "Energy"]["Annual_Transition_Cost_USD_Millions"].sum()
_energy_primary_pct = _energy_primary / primary_total * 100 if primary_total else float("nan")
_energy_sensit_pct  = _energy_sensit  / total_cost   * 100 if total_cost   else float("nan")

print(f"\nTop Risk Sector Shift:")
print(f"  Primary:     Energy ({_energy_primary_pct:.1f}% of burden)")
print(f"  Sensitivity: Energy ({_energy_sensit_pct:.1f}% of burden — LULCF removal concentrates risk)")

print(f"\n💡 KEY INSIGHT:")
print(f"   Excluding LULCF changes total exposure from ${primary_total:,.2f}M to ${total_cost:,.2f}M")
print(f"   LULCF accounts for {lulucf_pct:.1f}% of transition cost, but is critical for")
print(f"   policy assessment. Recommend PRIMARY analysis (with LULCF) for use.")

print("\n" + "=" * 80)
print("✓ SENSITIVITY ANALYSIS COMPLETE")
print("=" * 80)

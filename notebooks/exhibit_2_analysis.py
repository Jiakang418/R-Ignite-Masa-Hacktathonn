"""
EXHIBIT 2: THE TRANSITION RISK COST
Transition Risk Quantification for Malaysian Cedant Industries

This script calculates the annual transition cost each sector faces under
Net Zero 2050 vs. Current Policies climate scenarios.

Inputs:
- NGFS: Malaysia carbon price projections (Current Policies vs. Net Zero 2050)
- Climate Watch: Malaysia sector-level GHG emissions baseline (2023)

Output:
- Sector-by-sector transition cost exposure (ranked by cost)
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

DATA_DIR = Path("Dataset")
NGFS_CSV_FILE = DATA_DIR / "Downscaled_GCAM 6.0 NGFS_data.csv"
NGFS_XLSX_FILE = DATA_DIR / "Downscaled_GCAM 6.0 NGFS_data.xlsx"
GHG_FILE = DATA_DIR / "ghg-emissions.csv"

CARBON_PRICE_YEAR = 2027  # Mid-range year for analysis
REGION = "MYS"
CARBON_PRICE_VAR = "Price|Carbon"

# ============================================================================
# STEP 1: LOAD NGFS DATA
# ============================================================================

print("=" * 80)
print("EXHIBIT 2: TRANSITION RISK COST ANALYSIS")
print("=" * 80)
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

# Find Current Policies scenario
for scenario in mys_scenarios:
    if any(keyword in scenario for keyword in ["Current", "current", "CP"]):
        scenario_data = carbon_price_data[carbon_price_data["Scenario"] == scenario]
        if len(scenario_data) > 0 and str(CARBON_PRICE_YEAR) in scenario_data.columns:
            current_pol_price = float(scenario_data.iloc[0][str(CARBON_PRICE_YEAR)])
            current_pol_scenario = scenario
            print(f"  ✓ Current Policies scenario: '{scenario}'")
            print(f"    Carbon price ({CARBON_PRICE_YEAR}): ${current_pol_price:.2f}/ton CO2e")

# Find Net Zero scenario
for scenario in mys_scenarios:
    if any(keyword in scenario.lower() for keyword in ["net zero", "nz", "zero"]):
        scenario_data = carbon_price_data[carbon_price_data["Scenario"] == scenario]
        if len(scenario_data) > 0 and str(CARBON_PRICE_YEAR) in scenario_data.columns:
            net_zero_price = float(scenario_data.iloc[0][str(CARBON_PRICE_YEAR)])
            net_zero_scenario = scenario
            print(f"  ✓ Net Zero scenario: '{scenario}'")
            print(f"    Carbon price ({CARBON_PRICE_YEAR}): ${net_zero_price:.2f}/ton CO2e")

# Validation
if current_pol_price is None or net_zero_price is None:
    print(f"\n  ⚠️  Warning: Could not auto-detect both scenarios.")
    print(f"  Current Policies found: {current_pol_price is not None}")
    print(f"  Net Zero found: {net_zero_price is not None}")
    print(f"\n  Attempting manual extraction of first two scenarios...")
    
    if len(mys_scenarios) >= 2:
        scenario_data_1 = carbon_price_data[carbon_price_data["Scenario"] == mys_scenarios[0]]
        scenario_data_2 = carbon_price_data[carbon_price_data["Scenario"] == mys_scenarios[1]]
        
        if str(CARBON_PRICE_YEAR) in scenario_data_1.columns:
            current_pol_price = float(scenario_data_1.iloc[0][str(CARBON_PRICE_YEAR)])
            current_pol_scenario = mys_scenarios[0]
            print(f"  ✓ Using first scenario as Current Policies: {current_pol_scenario}")
            print(f"    Price: ${current_pol_price:.2f}/ton")
        
        if str(CARBON_PRICE_YEAR) in scenario_data_2.columns:
            net_zero_price = float(scenario_data_2.iloc[0][str(CARBON_PRICE_YEAR)])
            net_zero_scenario = mys_scenarios[1]
            print(f"  ✓ Using second scenario as Net Zero: {net_zero_scenario}")
            print(f"    Price: ${net_zero_price:.2f}/ton")

if current_pol_price is None or net_zero_price is None:
    print(f"\n  ❌ ERROR: Could not extract prices for both scenarios")
    exit(1)

# ============================================================================
# STEP 4: LOAD CLIMATE WATCH GHG
# ============================================================================

print(f"\n[Step 4] Loading Climate Watch sector GHG emissions...")

try:
    ghg_df = pd.read_csv(GHG_FILE)
    print(f"  ✓ Climate Watch loaded: {ghg_df.shape[0]} sectors")
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

print(f"\n[Step 5] Calculating transition costs...")

carbon_price_diff = net_zero_price - current_pol_price
print(f"\n  Carbon price differential (Net Zero - Current Policies):")
print(f"    {net_zero_price:.2f} - {current_pol_price:.2f} = ${carbon_price_diff:.2f}/ton CO2e")

transition_costs = {}
for sector, emissions_mtco2e in sector_emissions.items():
    # Emissions are in MtCO2e (million metric tons)
    # Cost = Emissions (MtCO2e) × Price Differential ($/ton) / 1,000,000 (to get to $M)
    cost_usd = emissions_mtco2e * carbon_price_diff * 1_000_000  # MtCO2e to tCO2e × $/t
    cost_millions = cost_usd / 1_000_000  # Convert to millions
    transition_costs[sector] = cost_millions

# Sort by cost (descending)
sorted_costs = sorted(transition_costs.items(), key=lambda x: x[1], reverse=True)

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
print("EXHIBIT 2: TRANSITION RISK COST RANKING")
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
print(f"TOTAL ANNUAL TRANSITION COST (All Sectors): ${total_cost:,.0f}M")
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

output_file = Path("exhibit_2_transition_cost_results.csv")
export_df.to_csv(output_file, index=False)
print(f"  ✓ Results saved to: {output_file}")

# ============================================================================
# STEP 9: INTERPRETATION
# ============================================================================

print("\n" + "=" * 80)
print("INTERPRETATION & IMPLICATIONS")
print("=" * 80)

top_sector, top_cost = sorted_costs[0]
print(f"\n🎯 HIGHEST RISK SECTOR: {top_sector}")
print(f"   Annual transition cost under Net Zero: ${top_cost:,.0f}M")
print(f"   This is {top_cost/total_cost*100:.1f}% of total Malaysian transition cost")

print(f"\n⚠️  POLICY INTERPRETATION:")
print(f"   If Malaysia transitions from Current Policies to Net Zero 2050:")
print(f"   - Total regulatory cost impact: ${total_cost:,.0f}M per year")
print(f"   - Carbon price increases by ${carbon_price_diff:.2f}/ton CO2e")
print(f"   - Top 3 sectors account for {sum([c for s, c in sorted_costs[:3]]) / total_cost * 100:.1f}% of total burden")

print(f"\n💡 CEDANT PORTFOLIO RISK:")
print(f"   Your cedant insureds face maximum exposure in:")
for rank, (sector, cost) in enumerate(sorted_costs[:3], 1):
    print(f"   {rank}. {sector}: ${cost:,.0f}M/year exposure")
print(f"\n   If currently priced assuming Current Policies carbon costs,")
print(f"   but Net Zero emerges → ${total_cost:,.0f}M reserve gap")

print("\n" + "=" * 80)
print("END OF EXHIBIT 2 ANALYSIS")
print("=" * 80)

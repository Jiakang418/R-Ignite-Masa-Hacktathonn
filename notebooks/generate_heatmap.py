"""
generate_heatmap.py
-------------------
Generates outputs/r_heatmap_reserve_gap.png — the 2D sensitivity heatmap of
Hannover Re's annual reserve gap as a function of:
  X-axis: NZ2050 carbon price (USD 0–200 / tonne CO2)
  Y-axis: Treaty pass-through rate (0–8 %)
  Color : Annual HRe reserve gap (USD millions)

Formula (from Tier 1 / Exhibit 2 sensitivity derivation):
  GAP = 0.74 + 5.796 × carbon_price × (pass_through_rate / 100)

where:
  0.74  = physical EAL gap base (USD M/yr, from MYS PELT uplift)
  5.796 = scale factor from NGFS NZ2050 × SEA GHG × HRe share chain

Contour lines:  $3.4M (floor)  |  $9.7M (central)  |  $18.6M (stress)
Trigger marker: NGFS NZ2050 trajectory crosses USD 56/t at ~2027 renewal cycle.

Run from project root:
    python notebooks/generate_heatmap.py

Saves: outputs/r_heatmap_reserve_gap.png
"""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

OUT = Path(__file__).parent.parent / 'outputs'
OUT.mkdir(exist_ok=True)

# ── Grid ──────────────────────────────────────────────────────────────────────
carbon_prices   = np.linspace(0, 200, 300)        # USD/t
pass_through    = np.linspace(0, 8, 300)           # %
CP, PT          = np.meshgrid(carbon_prices, pass_through)

GAP = 0.74 + 5.796 * CP * (PT / 100)              # USD M/yr

# ── Figure ────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 7))
fig.patch.set_facecolor('#FAFAFA')
ax.set_facecolor('#FAFAFA')

# Filled heatmap
cmap = plt.colormaps.get_cmap('RdYlGn_r').resampled(256)
cf   = ax.contourf(CP, PT, GAP, levels=100, cmap=cmap, alpha=0.92)
cb   = fig.colorbar(cf, ax=ax, pad=0.02, fraction=0.04)
cb.set_label('Annual HRe Reserve Gap (USD M)', fontsize=11)
cb.ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('$%.0fM'))

# Contour lines: floor / central / stress
CONTOURS = [3.4, 9.7, 18.6]
CLABELS  = ['$3.4M (floor)', '$9.7M (central)', '$18.6M (stress)']
CCOLORS  = ['#1565C0', '#E65100', '#B71C1C']
CSTYLES  = ['--', '-', ':']

cs = ax.contour(CP, PT, GAP, levels=CONTOURS, colors=CCOLORS, linewidths=[1.6, 2.2, 1.6],
                linestyles=CSTYLES)
for i, (lvl, lbl, col) in enumerate(zip(CONTOURS, CLABELS, CCOLORS)):
    ax.clabel(cs, [lvl], fmt={lvl: lbl}, fontsize=9, colors=[col], inline=True)

# Trigger point: NGFS NZ2050 hits ~$56/t at 2027 renewal at 3% pass-through
TRIGGER_CP = 56.0
TRIGGER_PT = 3.0
ax.scatter([TRIGGER_CP], [TRIGGER_PT], s=120, color='black', zorder=6, marker='*')
ax.annotate(
    'NGFS NZ2050\n~2027 trigger\n($56/t, 3% PT)',
    xy=(TRIGGER_CP, TRIGGER_PT),
    xytext=(TRIGGER_CP + 18, TRIGGER_PT + 1.5),
    fontsize=8.5, color='black',
    arrowprops=dict(arrowstyle='->', color='black', lw=1.1),
    bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='grey', alpha=0.85),
)

# NGFS Current Policies reference line (approx. $12/t blended SEA average)
ax.axvline(12, color='grey', lw=1.0, ls=':', alpha=0.7)
ax.text(13, 7.5, 'Current\nPolicies\n($12/t)', fontsize=7.5, color='grey', va='top')

# Axis labels
ax.set_xlabel('Carbon Price (USD / tonne CO$_{2}$)', fontsize=12)
ax.set_ylabel('Treaty Pass-Through Rate (%)', fontsize=12)
ax.set_title(
    'Hannover Re — Annual Physical + Transition Reserve Gap Sensitivity\n'
    'Malaysia & Philippines Reinsurance Sub-Book  |  NGFS GCAM 6.0 NZ2050 Scenario',
    fontsize=11, fontweight='bold', pad=12,
)

# Source note
fig.text(
    0.01, 0.01,
    'Formula: GAP = 0.74 + 5.796 x carbon_price x (pass_through/100)  USD M/yr\n'
    'Sources: NGFS GCAM 6.0 NZ2050; Swiss Re Sigma 1/2024; CHIRPS PELT analysis; EM-DAT 1991-2024',
    fontsize=7, color='grey', va='bottom',
)

plt.tight_layout(rect=[0, 0.06, 1, 1])
out_path = OUT / 'r_heatmap_reserve_gap.png'
plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
plt.close()
print(f'Saved: {out_path}')
print(f'  Floor  ($3.4M contour): carbon_price ~{(3.4 - 0.74) / (5.796 * 0.03):.0f} USD/t at 3% PT')
print(f'  Central($9.7M contour): carbon_price ~{(9.7 - 0.74) / (5.796 * 0.03):.0f} USD/t at 3% PT')
print(f'  Stress($18.6M contour): carbon_price ~{(18.6- 0.74) / (5.796 * 0.03):.0f} USD/t at 3% PT')

if __name__ == '__main__':
    pass  # script already runs on import; explicit main guard for import safety

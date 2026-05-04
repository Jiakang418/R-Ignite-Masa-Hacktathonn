# phase1_implementation.py

"""
Phase 1 Implementation

This script implements the comprehensive testing for insurance penetration and its impact on the HRe market.

Sections:
1. Insurance Penetration Assumptions
2. Treaty Attachment Factor
3. Sensitivity Analysis 
4. Tornado Chart Visualization
"""

import matplotlib.pyplot as plt
import numpy as np

# 1. Insurance Penetration Assumptions
class InsurancePenetration:
    def __init__(self):
        # Country-specific benchmarks
        self.malaysia_penetration = (0.10, 0.20)  # 10-20%
        self.philippines_penetration = (0.05, 0.10)  # 5-10%
        self.mid_malaysia = sum(self.malaysia_penetration) / 2
        self.mid_philippines = sum(self.philippines_penetration) / 2
        
    def empirical_derivation(self):
        # Example logic to derive empirical data from EM-DAT
        malaysia_empirical = self.mid_malaysia  # Mid-point example
        philippines_empirical = self.mid_philippines
        return malaysia_empirical, philippines_empirical

# 2. Treaty Attachment Factor and HRe Market Share
TREATY_ATTACHMENT_FACTOR = 0.50  # 50%
HRE_MARKET_SHARE = 0.03  # 3%

# 3. Sensitivity Analysis
def sensitivity_analysis(penetration_range, attachment_range, market_share_range):
    results = []
    for p in np.linspace(*penetration_range, num=5):
        for t in np.linspace(*attachment_range, num=5):
            for m in np.linspace(*market_share_range, num=5):
                # Example logic to calculate HRe Exposure
                exposure = p * t * m  # Simplistic exposure formula
                results.append((p, t, m, exposure))
    return results

# 4. Tornado Chart Visualization
def plot_tornado_chart(exposure_results):
    # Example tornado chart data preparation
    influences = [result[3] for result in exposure_results]
    assumptions = ['Ins Penetration', 'Treaty Attachment', 'HRe Market Share'] * (len(influences) // 3)
    plt.figure(figsize=(10, 6))
    plt.barh(assumptions, influences)
    plt.xlabel('Impact on HRe Exposure')
    plt.title('Tornado Chart of Assumptions')
    plt.show()

if __name__ == '__main__':
    insurance = InsurancePenetration()
    malaysia_empirical, philippines_empirical = insurance.empirical_derivation()
    print(f'Malaysia Empirical Penetration: {malaysia_empirical}\nPhilippines Empirical Penetration: {philippines_empirical}')
    analysis_results = sensitivity_analysis((0.05, 0.25), (0.30, 0.70), (0.01, 0.05))
    plot_tornado_chart(analysis_results)
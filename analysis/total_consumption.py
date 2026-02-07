import pandas as pd
import os

def calculate_2025_consumption():
    # 1. Constants based on OSU FY2025 reporting and documentation
    # Reported Energy Use Intensity (EUI) for Columbus Campus
    # Source: OSU Sustainability Institute FY2025
    eui_kbtu_per_sqft = 176.65 
    
    # Total Campus Gross Square Footage (approximate for Columbus campus)
    # Source: OSU Enterprise for Research, Innovation and Knowledge
    total_sqft = 25_000_000 
    
    # Conversion Factors
    # 1 kWh = 3.412 kBTU
    # 1 MWh = 1,000 kWh
    kbtu_to_mwh = 1 / (3.412 * 1000)
    
    # 2. Calculation
    total_kbtu = total_sqft * eui_kbtu_per_sqft
    total_mwh = total_kbtu * kbtu_to_mwh
    
    # 3. Cost Analysis (FY25 Rate)
    # Source: OSU Business and Finance Utility Rates FY25
    elec_rate_per_mwh = 151.50 # $0.1515 per kWh
    total_cost = total_mwh * elec_rate_per_mwh

    # 4. Output Results
    print(f"--- OSU COLUMBUS CAMPUS 2025 ESTIMATES ---")
    print(f"Total Building Area:     {total_sqft:,} sq. ft.")
    print(f"Energy Intensity:        {eui_kbtu_per_sqft} kBTU/sq. ft.")
    print(f"Total Consumption:       {total_mwh:,.2f} MWh")
    print(f"Estimated Annual Cost:   ${total_cost:,.2f}")
    print("-" * 42)
    print("Note: Calculation excludes McCracken/CHP generation as ")
    print("on-site electrical production is not active for 2025.")

if __name__ == "__main__":
    calculate_2025_consumption()
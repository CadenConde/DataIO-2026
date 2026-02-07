import pandas as pd
import glob
import os

def analyze_efficiency_refined():
    data_dir = 'cleanedData'
    metadata_path = os.path.join(data_dir, 'building_metadata.csv')
    readings_pattern = os.path.join(data_dir, 'meter-readings-*.csv')

    # Load Metadata
    df_meta = pd.read_csv(metadata_path)
    df_meta['buildingnumber'] = df_meta['buildingnumber'].astype(str).str.zfill(3)
    
    # Load and Filter Meter Readings
    reading_files = glob.glob(readings_pattern)
    all_readings = []
    
    for f in reading_files:
        # Important: Documentation states 'utility' must be 'ELECTRICITY' for kWh [cite: 117]
        temp_df = pd.read_csv(f, dtype={'simscode': str})
        
        # Filter for ONLY Electricity (Energy), excluding POWER (Demand) [cite: 125, 132]
        elec_df = temp_df[temp_df['utility'] == 'ELECTRICITY'].copy()
        all_readings.append(elec_df)
    
    if not all_readings:
        return

    df_energy = pd.concat(all_readings)

    # DATA CORRECTION: 
    # Check if 'readingvalue' is the hourly interval or a window sum.
    # If the total is still too high, the dataset might be providing 
    # cumulative meter readings rather than delta (hourly usage).
    
    # We aggregate by building and month (assuming files are monthly)
    # to check for outliers or duplicated timestamps.
    df_energy = df_energy.drop_duplicates(subset=['simscode', 'readingtime'])

    total_kwh = df_energy['readingvalue'].sum()
    total_mwh = total_kwh / 1000

    # Efficiency Calculations
    energy_totals = df_energy.groupby('simscode')['readingvalue'].sum().reset_index()
    df_merged = pd.merge(
        energy_totals, 
        df_meta[['buildingnumber', 'buildingname', 'grossarea']], 
        left_on='simscode', 
        right_on='buildingnumber'
    )

    df_merged['kwh_per_sqft'] = df_merged['readingvalue'] / df_merged['grossarea']
    total_sqft = df_merged['grossarea'].sum()
    
    df_merged['pct_total_usage'] = (df_merged['readingvalue'] / total_kwh) * 100
    df_merged['pct_total_sqft'] = (df_merged['grossarea'] / total_sqft) * 100

    print(f"--- REFINED ANNUAL SUMMARY ---")
    print(f"Total Electricity Usage: {total_mwh:,.2f} MWh")
    print(f"Calculated Carbon Impact: {(total_mwh * 911.4 / 2204.62):,.2f} Tonnes CO2") 
    print("-" * 85)

    # 6. Sort by Least Efficient (Highest kWh/sqft) to Most Efficient (Lowest)
    df_final = df_merged.sort_values(by='kwh_per_sqft', ascending=False)

    # Output formatting
    print(f"{'Building Name':<35} | {'kWh/sqft':<10} | {'% Total Usage':<15} | {'% Total Sqft':<15}")
    print("-" * 85)
    for _, row in df_final.iterrows():
        print(f"{row['buildingname'][:34]:<35} | "
              f"{row['kwh_per_sqft']:>10.2f} | "
              f"{row['pct_total_usage']:>14.2f}% | "
              f"{row['pct_total_sqft']:>14.2f}%")

if __name__ == "__main__":
    analyze_efficiency_refined()
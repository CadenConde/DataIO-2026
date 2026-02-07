import pandas as pd
import glob
import os
import numpy as np

def check_for_outliers():
    input_dir = 'cleanedData'
    readings_pattern = os.path.join(input_dir, 'meter-readings-*.csv')
    files = glob.glob(readings_pattern)
    
    if not files:
        print("No files found in cleanedData/.")
        return

    all_outliers = []

    print(f"Scanning {len(files)} files for energy anomalies...")

    for f in files:
        df = pd.read_csv(f, dtype={'simscode': str})
        df.columns = [c.lower() for c in df.columns]
        
        # We only care about Electricity for this check
        elec = df[df['utility'] == 'ELECTRICITY'].copy()
        
        if elec.empty:
            continue

        # 1. PHYSICAL LIMIT CHECK
        # An average large building rarely exceeds 2,000 - 5,000 kWh in a single hour.
        # If we see 100,000+ in one hour, it's almost certainly a unit error or duplicate sum.
        physical_limit = 50000 
        phys_outliers = elec[elec['readingvalue'] > physical_limit]

        # 2. STATISTICAL CHECK (Z-Score)
        # Finds values that are extreme relative to THAT specific building's normal behavior
        elec['z_score'] = elec.groupby('simscode')['readingvalue'].transform(
            lambda x: (x - x.mean()) / x.std() if x.std() > 0 else 0
        )
        stat_outliers = elec[elec['z_score'].abs() > 5] # 5 standard deviations is very extreme

        combined = pd.concat([phys_outliers, stat_outliers]).drop_duplicates()
        if not combined.empty:
            combined['file_source'] = os.path.basename(f)
            all_outliers.append(combined)

    if all_outliers:
        outlier_df = pd.concat(all_outliers)
        
        # Save results for inspection
        outlier_df.to_csv('analysis/detected_outliers.csv', index=False)
        
        print(f"\nALERT: Detected {len(outlier_df)} suspicious rows.")
        print("-" * 50)
        print(outlier_df[['simscode', 'readingtime', 'readingvalue', 'file_source']].head(10))
        print("\nFull list saved to analysis/detected_outliers.csv")
        
        # Summary of the "Crazy" values
        print(f"\nMax value found: {outlier_df['readingvalue'].max():,.2f} kWh")
        print(f"Average value of outliers: {outlier_df['readingvalue'].mean():,.2f} kWh")
    else:
        print("No extreme outliers detected.")

if __name__ == "__main__":
    check_for_outliers()
import pandas as pd
import glob
import os

def clean_energy_data():
    input_dir = 'data'
    output_dir = 'cleanedData'
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. Process SIMS Building Metadata
    metadata_path = os.path.join(input_dir, 'building_metadata.csv')
    try:
        df_meta = pd.read_csv(metadata_path)
        
        # Filter for Columbus campus as per documentation [cite: 83]
        df_meta_cleaned = df_meta[df_meta['campusname'] == 'Columbus']
        
        # Save cleaned metadata
        df_meta_cleaned.to_csv(os.path.join(output_dir, 'building_metadata.csv'), index=False)
        
        # FORMATTING FIX: Convert integer buildingNumber to a 3-digit padded string
        # This ensures it matches the 'simsCode' format (e.g., 5 -> "005") 
        valid_bldg_numbers = set(
            df_meta_cleaned['buildingnumber'].astype(str).str.zfill(3)
        )
        
        print(f"Filtered to {len(valid_bldg_numbers)} buildings on the Columbus campus.")
        
    except FileNotFoundError:
        print(f"Error: {metadata_path} not found.")
        return

    # 2. Process Smart Meter Readings
    readings_pattern = os.path.join(input_dir, 'meter-readings-*.csv')
    reading_files = glob.glob(readings_pattern)

    for file_path in reading_files:
        file_name = os.path.basename(file_path)
        # Force simsCode to string during load to preserve leading zeros
        df_readings = pd.read_csv(file_path, dtype={'simscode': str})
        
        # Filter: keep only if the simsCode is in our padded Columbus building list
        df_readings_cleaned = df_readings[df_readings['simscode'].isin(valid_bldg_numbers)]
        
        # Save the filtered monthly file
        df_readings_cleaned.to_csv(os.path.join(output_dir, file_name), index=False)
        print(f"Processed {file_name}: Saved {len(df_readings_cleaned)} rows.")

if __name__ == "__main__":
    clean_energy_data()
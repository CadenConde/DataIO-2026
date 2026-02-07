import pandas as pd
import glob
import os
import matplotlib.pyplot as plt

def analyze_building_efficiency():
    # Setup paths
    input_dir = 'cleanedData'
    output_dir = 'analysis'
    metadata_path = os.path.join(input_dir, 'building_metadata.csv')
    readings_pattern = os.path.join(input_dir, 'meter-readings-*.csv')

    # 1. Load Data
    df_meta = pd.read_csv(metadata_path)
    # Ensure columns are lowercase as noted
    df_meta.columns = [c.lower() for c in df_meta.columns]
    df_meta['buildingnumber'] = df_meta['buildingnumber'].astype(str).str.zfill(3)
    
    reading_files = glob.glob(readings_pattern)
    all_readings = []
    for f in reading_files:
        df = pd.read_csv(f, dtype={'simscode': str})
        df.columns = [c.lower() for c in df.columns]
        # Only use Electricity to ensure kWh units
        all_readings.append(df[df['utility'] == 'ELECTRICITY'])
    
    df_energy = pd.concat(all_readings)

    # 2. Data Cleaning: Prevent Overcounting
    # We drop duplicates based on the unique combination of building, time, and meter ID
    df_energy = df_energy.drop_duplicates(subset=['simscode', 'readingtime', 'meterid'])
    
    # Aggregate yearly total usage per building
    building_usage = df_energy.groupby('simscode')['readingvalue'].sum().reset_index()

    # 3. Enhanced Categorization Logic
    dorms = [
        "archer", "barrett", "blackburn", "bowen", "busch", "drackett", "halloran", 
        "haverfield", "houck", "houston", "jones", "lawrence", "mendoza", "norton", 
        "nosker", "raney", "scott", "taylor", "torres", "lincoln", "morrill", 
        "baker", "bradley", "canfield", "fechko", "german", "hanley", "mack", 
        "morrison", "neil", "park-stradley", "paterson", "pennsylvania", 
        "pomerene", "tenth", "scholars", "siebert", "smith-steeb", "worthington", "residence"
    ]

    def get_category(name):
        name = str(name).lower()
        if "union" in name: return "Union"
        if "libra" in name: return "Library"
        if "recreat" in name: return "Gym"
        if "lab" in name: return "Lab"
        if any(d in name for d in dorms): return "Dorm"
        if "hall" in name: return "Classroom"
        return "Other"

    # 4. Merge and Calculate
    df_merged = pd.merge(building_usage, df_meta, left_on='simscode', right_on='buildingnumber')
    df_merged['category'] = df_merged['buildingname'].apply(get_category)
    
    # Filter out "Other" as requested
    df_filtered = df_merged[df_merged['category'] != "Other"].copy()
    
    # Calculate kWh per sqft
    df_filtered['kwh_per_sqft'] = df_filtered['readingvalue'] / df_filtered['grossarea']

    # 5. Aggregate by Category
    category_summary = df_filtered.groupby('category').agg({
        'kwh_per_sqft': 'mean',
        'readingvalue': 'sum',
        'grossarea': 'sum'
    }).sort_values('kwh_per_sqft', ascending=False)

    # Calculate percentages for the final table
    total_usage = df_filtered['readingvalue'].sum()
    total_area = df_filtered['grossarea'].sum()
    category_summary['% Total Usage'] = (category_summary['readingvalue'] / total_usage) * 100
    category_summary['% Total Sqft'] = (category_summary['grossarea'] / total_area) * 100

    # 6. Prettier Visualization
    plt.style.use('ggplot')
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # OSU Scarlet and Gray palette
    colors = ['#BB0000', '#666666', '#999999', '#CCCCCC', '#333333', '#777777']
    
    bars = ax.bar(category_summary.index, category_summary['kwh_per_sqft'], 
                  color=colors[:len(category_summary)], edgecolor='black', alpha=0.8)

    # Formatting
    ax.set_title('Building Efficiency by Category (Columbus Campus)', fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel('Avg annual $kWh / ft^2$', fontsize=12)
    ax.set_xlabel('Building Type', fontsize=12)
    plt.xticks(rotation=0, fontweight='bold')
    
    # Add data labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), 
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'efficiency_by_category.png'), dpi=300)
    
    # Save the raw data
    category_summary.to_csv(os.path.join(output_dir, 'category_efficiency_results.csv'))
    
    print("Analysis Complete.")
    print(f"Annual Campus Usage (Filtered): {total_usage/1000:,.2f} MWh")
    print(category_summary[['kwh_per_sqft', '% Total Usage', '% Total Sqft']])

if __name__ == "__main__":
    analyze_building_efficiency()
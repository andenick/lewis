"""
IMF Bulk CSV Import Script
===========================

Import bulk-downloaded IMF data (CSV files from data.imf.org) into platform format.

Since the IMF SDMX API is unreliable, this script processes bulk CSV downloads.

Usage:
1. Download data from https://data.imf.org/
2. Select: Balance of Payments (BOP) or Direction of Trade (DOTS)
3. Choose countries, indicators, time period
4. Download as CSV
5. Place CSV files in: Technical/src/data/imf_downloads/
6. Run this script

Author: Claude
Date: 2025-10-06
"""

import os
import pandas as pd
from pathlib import Path
import sys
DATA_ROOT = Path(os.environ.get("DATA_ROOT", "data"))

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.append(str(PROJECT_ROOT / "Technical" / "src"))

# Paths
IMF_DOWNLOADS = PROJECT_ROOT / "Technical" / "src" / "data" / "imf_downloads"
IMF_DOWNLOADS.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = DATA_ROOT / "IMF"
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)


def process_imf_csv(csv_file: Path) -> pd.DataFrame:
    """
    Process IMF bulk CSV download.
    
    IMF CSV format typically has:
    - Country columns
    - Indicator rows
    - Time periods as columns or rows (varies)
    """
    print(f"\n[PROCESSING] {csv_file.name}")
    
    # Read CSV
    df = pd.read_csv(csv_file)
    
    print(f"  Dimensions: {df.shape}")
    print(f"  Columns: {list(df.columns[:5])}...")
    
    # IMF CSVs vary in format - attempt common structure
    # Usually: Country, Indicator, Attribute, Year columns, Value
    
    # Try to standardize
    standardized = []
    
    # Check if this is a wide format (years as columns)
    year_cols = [col for col in df.columns if col.isdigit() and len(col) == 4]
    
    if year_cols:
        # Wide format: melt years into rows
        print(f"  Format: Wide (found {len(year_cols)} year columns)")
        
        # Identify ID columns (non-year columns)
        id_cols = [col for col in df.columns if col not in year_cols]
        
        # Melt
        df_long = df.melt(
            id_vars=id_cols,
            value_vars=year_cols,
            var_name='year',
            value_name='value'
        )
        
        # Convert year to int
        df_long['year'] = df_long['year'].astype(int)
        
        # Remove NaN values
        df_long = df_long.dropna(subset=['value'])
        
        standardized = df_long
        
    else:
        # Already in long format
        print(f"  Format: Long")
        standardized = df
    
    print(f"  Output rows: {len(standardized):,}")
    
    return standardized


def import_all_imf_files():
    """Import all CSV files from downloads folder."""
    csv_files = list(IMF_DOWNLOADS.glob("*.csv"))
    
    if not csv_files:
        print("\n[ERROR] No CSV files found in:")
        print(f"  {IMF_DOWNLOADS}")
        print("\nInstructions:")
        print("1. Go to: https://data.imf.org/")
        print("2. Navigate to: Data > Balance of Payments")
        print("3. Select countries and indicators")
        print("4. Download as CSV")
        print(f"5. Place CSV files in: {IMF_DOWNLOADS}")
        return
    
    print(f"\n[FOUND] {len(csv_files)} CSV files")
    
    all_data = []
    
    for csv_file in csv_files:
        try:
            df = process_imf_csv(csv_file)
            if len(df) > 0:
                # Add source metadata
                df['source_file'] = csv_file.name
                all_data.append(df)
        except Exception as e:
            print(f"  [ERROR] {str(e)}")
    
    if all_data:
        # Combine all
        combined = pd.concat(all_data, ignore_index=True)
        
        # Save
        output_file = OUTPUT_PATH / "imf_bulk_import.csv"
        combined.to_csv(output_file, index=False, encoding='utf-8')
        
        print(f"\n[SUCCESS] Combined data saved")
        print(f"  File: {output_file}")
        print(f"  Total observations: {len(combined):,}")
        
        if 'Country' in combined.columns or 'country' in combined.columns:
            country_col = 'Country' if 'Country' in combined.columns else 'country'
            print(f"  Countries: {combined[country_col].nunique()}")
        
        if 'Indicator' in combined.columns or 'indicator' in combined.columns:
            ind_col = 'Indicator' if 'Indicator' in combined.columns else 'indicator'
            print(f"  Indicators: {combined[ind_col].nunique()}")
        
    else:
        print("\n[WARNING] No data imported")


def main():
    """Main execution."""
    print("="*80)
    print("IMF BULK CSV IMPORT")
    print("="*80)
    
    import_all_imf_files()


if __name__ == "__main__":
    main()

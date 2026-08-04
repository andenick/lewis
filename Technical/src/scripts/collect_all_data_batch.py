"""
Comprehensive Batch Data Collection
====================================

Systematically collect data from all available APIs in small batches.
Saves incrementally to avoid timeouts and data loss.
"""

import os
import sys
from pathlib import Path
import pandas as pd
import requests
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
OUTPUT_ROOT = Path(os.environ.get("OUTPUT_ROOT", "outputs"))

print("\n" + "="*80)
print("COMPREHENSIVE BATCH DATA COLLECTION")
print("="*80)
print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ============================================================================
# CONFIGURATION
# ============================================================================

# Priority countries in batches
BATCH_1_G7 = ['USA', 'GBR', 'DEU', 'FRA', 'ITA', 'JPN', 'CAN']
BATCH_2_MAJOR = ['CHN', 'KOR', 'AUS', 'ESP', 'NLD', 'BEL', 'SWE']
BATCH_3_EMERGING = ['MEX', 'BRA', 'IND', 'ZAF', 'IDN', 'TUR', 'POL']
BATCH_4_OTHER = ['CHE', 'NOR', 'DNK', 'FIN', 'IRL', 'NZL', 'AUT']

ALL_BATCHES = [BATCH_1_G7, BATCH_2_MAJOR, BATCH_3_EMERGING, BATCH_4_OTHER]
BATCH_NAMES = ['G7', 'Major_Advanced', 'Emerging', 'Other_Advanced']

# Key World Bank indicators
WB_INDICATORS = {
    'BN.CAB.XOKA.CD': 'Current_Account_USD',
    'BN.CAB.XOKA.GD.ZS': 'Current_Account_pct_GDP',
    'NE.EXP.GNFS.CD': 'Exports_Goods_Services_USD',
    'NE.IMP.GNFS.CD': 'Imports_Goods_Services_USD',
    'NY.GDP.MKTP.CD': 'GDP_Current_USD',
}

# ============================================================================
# WORLD BANK BATCH COLLECTION
# ============================================================================

def collect_worldbank_batch(countries, batch_name, start_year=2000, end_year=2024):
    """Collect World Bank data for a batch of countries."""

    print(f"\n{'='*80}")
    print(f"WORLD BANK - {batch_name}")
    print(f"{'='*80}")
    print(f"Countries: {', '.join(countries)}")
    print(f"Period: {start_year}-{end_year}")

    WB_BATCH_PATH = OUTPUT_ROOT / "World_Bank" / f"Batch_{batch_name}"
    WB_BATCH_PATH.mkdir(parents=True, exist_ok=True)

    all_data = []
    collected_count = 0
    error_count = 0

    for i, country in enumerate(countries, 1):
        print(f"\n[{i}/{len(countries)}] {country}:")

        for indicator_code, indicator_name in WB_INDICATORS.items():
            try:
                print(f"  {indicator_name[:35]:35s} ", end='', flush=True)

                url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator_code}"
                params = {
                    'date': f'{start_year}:{end_year}',
                    'format': 'json',
                    'per_page': 100
                }

                response = requests.get(url, params=params, timeout=30)

                if response.status_code == 200:
                    data = response.json()

                    if len(data) > 1 and data[1]:
                        count = 0
                        for obs in data[1]:
                            year = obs.get('date')
                            value = obs.get('value')

                            if value is not None:
                                all_data.append({
                                    'country': country,
                                    'country_name': obs.get('country', {}).get('value', ''),
                                    'year': int(year),
                                    'indicator_code': indicator_code,
                                    'indicator_name': indicator_name,
                                    'value': float(value)
                                })
                                count += 1
                        print(f"[OK {count:3d}]")
                        collected_count += count
                    else:
                        print("[No data]")
                else:
                    print(f"[Err {response.status_code}]")
                    error_count += 1

                time.sleep(0.05)

            except Exception as e:
                print(f"[ERROR]")
                error_count += 1
                continue

    # Save batch data
    if all_data:
        df = pd.DataFrame(all_data)

        # Save full batch dataset
        batch_file = WB_BATCH_PATH / f"worldbank_{batch_name}_{start_year}_{end_year}.csv"
        df.to_csv(batch_file, index=False)

        print(f"\n{'-'*80}")
        print(f"BATCH {batch_name} SUMMARY:")
        print(f"{'-'*80}")
        print(f"Observations collected: {len(df):,}")
        print(f"Countries: {df['country'].nunique()}")
        print(f"Indicators: {df['indicator_name'].nunique()}")
        print(f"Years: {df['year'].min()}-{df['year'].max()}")
        print(f"Errors: {error_count}")
        print(f"Saved to: {batch_file.relative_to(PROJECT_ROOT)}")

        return df
    else:
        print(f"\n[WARNING] No data collected for {batch_name}")
        return pd.DataFrame()

# ============================================================================
# COLLECT ALL BATCHES
# ============================================================================

all_collected = []
total_obs = 0

for batch_countries, batch_name in zip(ALL_BATCHES, BATCH_NAMES):
    try:
        batch_df = collect_worldbank_batch(batch_countries, batch_name)
        if not batch_df.empty:
            all_collected.append(batch_df)
            total_obs += len(batch_df)

        # Pause between batches
        print(f"\nPausing 10 seconds before next batch...")
        time.sleep(10)

    except Exception as e:
        print(f"\n[ERROR] Batch {batch_name} failed: {e}")
        continue

# ============================================================================
# COMBINE ALL BATCHES
# ============================================================================

if all_collected:
    print("\n" + "="*80)
    print("COMBINING ALL BATCHES")
    print("="*80)

    combined = pd.concat(all_collected, ignore_index=True)

    # Save combined dataset
    WB_COMBINED_PATH = OUTPUT_ROOT / "World_Bank"
    combined_file = WB_COMBINED_PATH / "worldbank_all_countries_2000_2024.csv"
    combined.to_csv(combined_file, index=False)

    print(f"\nCombined dataset saved to: {combined_file.relative_to(PROJECT_ROOT)}")
    print(f"\nTotal observations: {len(combined):,}")
    print(f"Countries: {combined['country'].nunique()}")
    print(f"Indicators: {combined['indicator_name'].nunique()}")

    # Create pivot tables
    print(f"\nCreating pivot tables...")
    for indicator_name in combined['indicator_name'].unique():
        indicator_df = combined[combined['indicator_name'] == indicator_name].copy()
        pivot = indicator_df.pivot(index='year', columns='country', values='value')

        filename = indicator_name.replace('_', '_').lower() + ".csv"
        pivot_file = WB_COMBINED_PATH / filename
        pivot.to_csv(pivot_file)
        print(f"  -> {filename}")

    # Country coverage report
    print("\n" + "="*80)
    print("COUNTRY COVERAGE REPORT")
    print("="*80)
    coverage = combined.groupby('country').agg({
        'year': ['min', 'max', 'count'],
        'indicator_name': 'nunique'
    }).round(0)
    coverage.columns = ['First_Year', 'Last_Year', 'Total_Obs', 'Indicators']
    print(coverage.to_string())

    # Save coverage report
    coverage_file = WB_COMBINED_PATH / "country_coverage_report.csv"
    coverage.to_csv(coverage_file)

print("\n" + "="*80)
print("BATCH COLLECTION COMPLETE")
print("="*80)
print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Total observations collected: {total_obs:,}")

"""
Priority Data Collection Script
================================

Quickly collect data from available APIs for priority countries.
Focus: G7 + major emerging markets
"""

import os
import sys
from pathlib import Path
import pandas as pd
import requests
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
OUTPUT_ROOT = Path(os.environ.get("OUTPUT_ROOT", "outputs"))

# Priority countries
G7 = ['USA', 'GBR', 'DEU', 'FRA', 'ITA', 'JPN', 'CAN']
BRICS = ['BRA', 'RUS', 'IND', 'CHN', 'ZAF']
OTHER_KEY = ['MEX', 'KOR', 'AUS', 'ESP', 'NLD']

ALL_PRIORITY = G7 + BRICS + OTHER_KEY

print("\n" + "="*80)
print("PRIORITY COUNTRIES DATA COLLECTION")
print("="*80)
print(f"\nCountries to collect: {len(ALL_PRIORITY)}")
print(f"G7: {', '.join(G7)}")
print(f"BRICS: {', '.join(BRICS)}")
print(f"Other: {', '.join(OTHER_KEY)}")

# ============================================================================
# WORLD BANK DATA COLLECTION
# ============================================================================

print("\n" + "="*80)
print("WORLD BANK API - Balance of Payments")
print("="*80)

WB_PATH = OUTPUT_ROOT / "World_Bank_Quick"
WB_PATH.mkdir(parents=True, exist_ok=True)

# Key BoP indicators
INDICATORS = {
    'BN.CAB.XOKA.CD': 'Current_Account_USD',
    'BN.CAB.XOKA.GD.ZS': 'Current_Account_pct_GDP',
    'NE.EXP.GNFS.CD': 'Exports_Goods_Services_USD',
    'NE.IMP.GNFS.CD': 'Imports_Goods_Services_USD',
    'NY.GDP.MKTP.CD': 'GDP_Current_USD',
}

all_data = []
errors = []

for i, country in enumerate(ALL_PRIORITY, 1):
    print(f"\n[{i}/{len(ALL_PRIORITY)}] {country}:")

    for indicator_code, indicator_name in INDICATORS.items():
        try:
            print(f"  {indicator_name[:30]:30s} ", end='')

            url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator_code}"
            params = {
                'date': '2000:2024',
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
                    print(f"[OK {count:3d} obs]")
                else:
                    print("[No data]")
            else:
                print(f"[Error {response.status_code}]")
                errors.append(f"{country}-{indicator_code}")

            time.sleep(0.05)  # Minimal rate limiting

        except Exception as e:
            print(f"[ERROR: {str(e)[:30]}]")
            errors.append(f"{country}-{indicator_code}")
            continue

# Save collected data
if all_data:
    df = pd.DataFrame(all_data)

    print("\n" + "="*80)
    print("COLLECTION SUMMARY")
    print("="*80)
    print(f"\nTotal observations: {len(df):,}")
    print(f"Countries: {df['country'].nunique()}")
    print(f"Indicators: {df['indicator_name'].nunique()}")
    print(f"Years: {df['year'].min()}-{df['year'].max()}")

    # Save full dataset
    output_file = WB_PATH / "worldbank_priority_countries_2000_2024.csv"
    df.to_csv(output_file, index=False)
    print(f"\n[SAVED] {output_file.relative_to(PROJECT_ROOT)}")

    # Create pivot tables for easier analysis
    for indicator_name in df['indicator_name'].unique():
        indicator_df = df[df['indicator_name'] == indicator_name].copy()
        pivot = indicator_df.pivot(index='year', columns='country', values='value')

        filename = indicator_name.replace('_', '_').lower() + ".csv"
        pivot_file = WB_PATH / filename
        pivot.to_csv(pivot_file)
        print(f"  -> {filename}")

    # Country coverage report
    print("\n" + "-"*80)
    print("COUNTRY COVERAGE:")
    print("-"*80)
    coverage = df.groupby('country').agg({
        'year': ['min', 'max', 'count'],
        'indicator_name': 'nunique'
    }).round(0)
    coverage.columns = ['First_Year', 'Last_Year', 'Total_Obs', 'Indicators']
    print(coverage.to_string())

else:
    print("\n[WARNING] No data collected!")

if errors:
    print(f"\n[WARNING] {len(errors)} errors occurred")

print("\n" + "="*80)
print("PRIORITY DATA COLLECTION COMPLETE")
print("="*80)

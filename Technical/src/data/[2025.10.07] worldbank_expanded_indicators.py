"""
World Bank Expanded Indicators Collector
=========================================

Add 20 more high-value indicators to the existing 60 countries.

This expands from 34 to 54 indicators, adding:
- Government finance indicators
- Poverty and inequality metrics
- Energy and environment data
- Financial sector indicators
- Infrastructure metrics

Author: Claude
Date: 2025-10-06
"""

import os
import pandas as pd
import requests
import time
from pathlib import Path
from typing import List, Dict
import sys

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.append(str(PROJECT_ROOT / "Technical" / "src"))

from data.collection_tracker import CollectionTracker

# Paths
OUTPUT_ROOT = Path(os.environ.get("OUTPUT_ROOT", "outputs"))
WB_EXPANDED_PATH = OUTPUT_ROOT / "World_Bank_Expanded_Indicators"
WB_EXPANDED_PATH.mkdir(parents=True, exist_ok=True)


class WorldBankExpandedIndicators:
    """
    Collect 20 additional World Bank indicators for existing 60 countries.
    """

    def __init__(self):
        """Initialize collector."""
        self.base_url = "https://api.worldbank.org/v2"
        self.session = requests.Session()
        self.tracker = CollectionTracker()

        # All 60 countries from Phase 1
        self.countries = [
            # G7
            'USA', 'GBR', 'DEU', 'FRA', 'ITA', 'JPN', 'CAN',
            # Major Emerging
            'CHN', 'IND', 'BRA', 'ZAF', 'TUR', 'MEX', 'IDN', 'POL', 'KOR',
            # Advanced Economies
            'AUS', 'ESP', 'NLD', 'BEL', 'SWE', 'CHE', 'NOR', 'DNK',
            'FIN', 'IRL', 'NZL', 'AUT',
            # Europe expansion
            'PRT', 'GRC', 'CZE', 'HUN', 'ROU', 'BGR', 'HRV', 'SVK', 'SVN', 'LUX', 'ISL',
            # Middle East
            'SAU', 'ARE', 'ISR', 'EGY', 'QAT', 'KWT',
            # Asia expansion
            'THA', 'MYS', 'SGP', 'PHL', 'VNM', 'PAK', 'BGD', 'LKA',
            # Latin America expansion
            'ARG', 'CHL', 'COL', 'PER', 'VEN',
            # Africa expansion
            'NGA', 'KEN',
        ]

        # 20 NEW indicators (high-value additions)
        self.new_indicators = {
            # Government Finance (4)
            'GC.TAX.TOTL.GD.ZS': 'Tax_Revenue_Pct_GDP',
            'GC.REV.XGRT.GD.ZS': 'Revenue_Excluding_Grants_Pct_GDP',
            'GC.XPN.TOTL.GD.ZS': 'Expense_Pct_GDP',
            'GC.DOD.TOTL.GD.ZS': 'Central_Govt_Debt_Pct_GDP',

            # Poverty & Inequality (3)
            'SI.POV.NAHC': 'Poverty_Headcount_Ratio_National',
            'SI.POV.GINI': 'GINI_Index',
            'SI.DST.10TH.10': 'Income_Share_Top_10_Pct',

            # Financial Sector (4)
            'FR.INR.LEND': 'Lending_Interest_Rate',
            'FR.INR.DPST': 'Deposit_Interest_Rate',
            'FB.AST.NPER.ZS': 'Bank_Nonperforming_Loans_Pct',
            'FD.RES.LIQU.AS.ZS': 'Bank_Liquid_Reserves_Pct_Assets',

            # Energy & Environment (4)
            'EG.USE.PCAP.KG.OE': 'Energy_Use_Per_Capita',
            'EN.ATM.CO2E.PC': 'CO2_Emissions_Per_Capita',
            'EG.ELC.ACCS.ZS': 'Access_to_Electricity_Pct',
            'EG.USE.ELEC.KH.PC': 'Electric_Power_Consumption_Per_Capita',

            # Infrastructure (3)
            'IS.ROD.PAVE.ZS': 'Roads_Paved_Pct',
            'IT.NET.USER.ZS': 'Internet_Users_Pct',
            'IT.CEL.SETS.P2': 'Mobile_Subscriptions_Per_100',

            # Trade Policy (2)
            'TM.TAX.MRCH.WM.AR.ZS': 'Tariff_Rate_Applied_Weighted_Mean',
            'TM.TAX.TCOM.SM.AR.ZS': 'Tariff_Rate_Simple_Mean',
        }

        print("="*80)
        print("WORLD BANK EXPANDED INDICATORS COLLECTOR")
        print("="*80)
        print(f"Countries: {len(self.countries)}")
        print(f"NEW Indicators: {len(self.new_indicators)}")
        print(f"Potential Observations: {len(self.countries) * len(self.new_indicators) * 25:,}")
        print(f"Output: {WB_EXPANDED_PATH}")
        print()

    def get_country_data(self, country: str, start_year: int = 2000,
                        end_year: int = 2024) -> pd.DataFrame:
        """Get new indicators for a country."""
        print(f"\n[{country}] Collecting expanded indicators...")

        all_data = []
        success_count = 0
        skip_count = 0
        error_count = 0

        for indicator_code, indicator_name in self.new_indicators.items():
            # Check if already collected
            if self.tracker.is_collected('World_Bank_Expanded', country,
                                        indicator_code, start_year, end_year):
                skip_count += 1
                continue

            # Build URL
            url = f"{self.base_url}/country/{country}/indicator/{indicator_code}"
            params = {
                'date': f'{start_year}:{end_year}',
                'format': 'json',
                'per_page': 500
            }

            try:
                response = self.session.get(url, params=params, timeout=30)

                if response.status_code == 200:
                    data = response.json()

                    if len(data) > 1 and data[1]:
                        records = []
                        for obs in data[1]:
                            if obs['value'] is not None:
                                records.append({
                                    'country': country,
                                    'country_name': obs.get('country', {}).get('value', country),
                                    'indicator_code': indicator_code,
                                    'indicator_name': indicator_name,
                                    'year': int(obs['date']),
                                    'value': float(obs['value'])
                                })

                        if records:
                            df = pd.DataFrame(records)
                            all_data.append(df)
                            success_count += 1
                            print(f"  [OK] {indicator_code}: {len(records)} obs")

                            self.tracker.record_collection(
                                source='World_Bank_Expanded',
                                country=country,
                                indicator=indicator_code,
                                start_year=start_year,
                                end_year=end_year,
                                observations=len(records),
                                file_path=str(WB_EXPANDED_PATH / f"wb_exp_{country}_{indicator_code}.csv"),
                                success=True
                            )
                        else:
                            error_count += 1
                            self.tracker.record_collection(
                                source='World_Bank_Expanded',
                                country=country,
                                indicator=indicator_code,
                                start_year=start_year,
                                end_year=end_year,
                                observations=0,
                                file_path="",
                                success=False,
                                error="No data available"
                            )
                else:
                    error_count += 1

                time.sleep(0.1)

            except Exception as e:
                error_count += 1
                time.sleep(0.5)

        print(f"  Summary: {success_count} success, {skip_count} skipped, {error_count} failed")

        if all_data:
            return pd.concat(all_data, ignore_index=True)
        else:
            return pd.DataFrame()

    def collect_all_countries(self, batch_size: int = 10):
        """Collect expanded indicators for all 60 countries."""
        print("\n" + "="*80)
        print(f"COLLECTING EXPANDED INDICATORS: {len(self.countries)} COUNTRIES")
        print("="*80)

        total_obs = 0

        for i in range(0, len(self.countries), batch_size):
            batch = self.countries[i:i+batch_size]
            batch_num = i//batch_size + 1

            print(f"\n{'='*80}")
            print(f"BATCH {batch_num}: {', '.join(batch)}")
            print(f"{'='*80}")

            batch_data = []

            for country in batch:
                df = self.get_country_data(country)
                if len(df) > 0:
                    batch_data.append(df)
                    total_obs += len(df)

            # Save batch
            if batch_data:
                batch_df = pd.concat(batch_data, ignore_index=True)
                batch_file = WB_EXPANDED_PATH / f"Batch_{batch_num}.csv"
                batch_df.to_csv(batch_file, index=False, encoding='utf-8')
                print(f"\n  [SAVED] {batch_file.name} ({len(batch_df):,} obs)")

            # Pause between batches
            if i + batch_size < len(self.countries):
                print("\n  [PAUSE] 10 seconds...")
                time.sleep(10)

        print("\n" + "="*80)
        print("EXPANDED INDICATORS COLLECTION COMPLETE")
        print("="*80)
        print(f"Total observations: {total_obs:,}")

        return total_obs

    def combine_all_batches(self):
        """Combine all batch files."""
        print("\n[COMBINE] Combining batches...")

        all_files = list(WB_EXPANDED_PATH.glob("Batch_*.csv"))

        if not all_files:
            print("  No batch files found.")
            return

        all_data = [pd.read_csv(f) for f in all_files]
        combined = pd.concat(all_data, ignore_index=True)

        # Save combined
        combined_file = WB_EXPANDED_PATH / "worldbank_expanded_indicators.csv"
        combined.to_csv(combined_file, index=False, encoding='utf-8')

        print(f"  Saved: {combined_file.name}")
        print(f"  Total observations: {len(combined):,}")
        print(f"  Countries: {combined['country'].nunique()}")
        print(f"  Indicators: {combined['indicator_code'].nunique()}")


def main():
    """Main execution."""
    collector = WorldBankExpandedIndicators()

    auto = '--auto' in sys.argv or not sys.stdin.isatty()

    if auto:
        collector.collect_all_countries(batch_size=10)
        collector.combine_all_batches()
    else:
        response = input("\nStart expanded indicators collection? (y/n): ")
        if response.lower() == 'y':
            collector.collect_all_countries(batch_size=10)
            collector.combine_all_batches()


if __name__ == "__main__":
    main()

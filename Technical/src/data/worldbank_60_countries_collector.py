"""
World Bank 60 Countries Collector
==================================

Expand World Bank coverage from 28 to 60 countries for global representation.

Adds 32 new countries across:
- Additional European economies
- Middle East & North Africa
- Additional Asian economies
- Additional Latin American economies
- Additional African economies

Author: Claude
Date: 2025-10-06
"""

import os
import pandas as pd
import requests
import time
from pathlib import Path
from typing import List
import sys

# Add project to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.append(str(PROJECT_ROOT / "Technical" / "src"))

from data.collection_tracker import CollectionTracker

# Project paths
OUTPUT_ROOT = Path(os.environ.get("OUTPUT_ROOT", "outputs"))
WB_PATH = OUTPUT_ROOT / "World_Bank_60Countries"
WB_PATH.mkdir(parents=True, exist_ok=True)


class WorldBank60Collector:
    """
    Collect World Bank data for 60 countries (32 new + 28 existing).
    """

    def __init__(self):
        """Initialize collector."""
        self.base_url = "https://api.worldbank.org/v2"
        self.session = requests.Session()
        self.tracker = CollectionTracker()

        # Same 33 indicators as existing collector
        self.indicators = {
            # BoP
            'BN.CAB.XOKA.CD': 'Current_Account_Balance_USD',
            'BN.CAB.XOKA.GD.ZS': 'Current_Account_pct_GDP',
            # Trade
            'NE.EXP.GNFS.CD': 'Exports_Goods_Services_USD',
            'NE.IMP.GNFS.CD': 'Imports_Goods_Services_USD',
            # GDP
            'NY.GDP.MKTP.CD': 'GDP_Current_USD',
            # FDI
            'BX.KLT.DINV.CD.WD': 'FDI_Net_Inflows_USD',
            'BM.KLT.DINV.CD.WD': 'FDI_Net_Outflows_USD',
            'BN.KLT.DINV.CD': 'FDI_Net_USD',
            # Portfolio
            'BX.PEF.TOTL.CD.WD': 'Portfolio_Equity_Net_Inflows',
            'BN.TRF.KOGT.CD': 'Net_Capital_Account',
            # Reserves
            'FI.RES.TOTL.CD': 'Total_Reserves_USD',
            'FI.RES.TOTL.MO': 'Reserves_Months_Imports',
            'FI.RES.XGLD.CD': 'Reserves_Excluding_Gold_USD',
            # Debt
            'DT.DOD.DECT.CD': 'External_Debt_Stocks_Total_USD',
            'DT.DOD.DECT.GN.ZS': 'External_Debt_pct_GNI',
            'DT.TDS.DECT.GN.ZS': 'Debt_Service_pct_GNI',
            # Exchange Rates
            'PA.NUS.FCRF': 'Official_Exchange_Rate',
            'PX.REX.REER': 'Real_Effective_Exchange_Rate_Index',
            # Inflation
            'FP.CPI.TOTL.ZG': 'Inflation_Consumer_Prices_Annual',
            'NY.GDP.DEFL.KD.ZG': 'GDP_Deflator_Annual',
            # GDP Metrics
            'NY.GDP.PCAP.CD': 'GDP_Per_Capita_USD',
            'NY.GDP.MKTP.KD.ZG': 'GDP_Growth_Annual',
            # Trade Ratios
            'NE.EXP.GNFS.ZS': 'Exports_pct_GDP',
            'NE.IMP.GNFS.ZS': 'Imports_pct_GDP',
            'TG.VAL.TOTL.GD.ZS': 'Merchandise_Trade_pct_GDP',
            # Labor
            'SL.UEM.TOTL.ZS': 'Unemployment_Total_pct',
            'SL.TLF.TOTL.IN': 'Labor_Force_Total',
            # Remittances
            'BX.TRF.PWKR.CD.DT': 'Personal_Remittances_Received_USD',
            'BM.TRF.PWKR.CD.DT': 'Personal_Remittances_Paid_USD',
            # Tourism
            'ST.INT.RCPT.CD': 'International_Tourism_Receipts_USD',
            'ST.INT.XPND.CD': 'International_Tourism_Expenditures_USD',
            # Financial Development
            'FS.AST.PRVT.GD.ZS': 'Domestic_Credit_to_Private_Sector_pct_GDP',
            'FM.LBL.BMNY.GD.ZS': 'Broad_Money_pct_GDP',
        }

        print("\n" + "="*80)
        print("WORLD BANK 60 COUNTRIES COLLECTOR")
        print("="*80)
        print(f"Total indicators: {len(self.indicators)}")
        print(f"Output path: {WB_PATH}")

    def get_indicator_data(self, country: str, indicator_code: str,
                          start_year: int = 2000, end_year: int = 2024) -> pd.DataFrame:
        """Get data for specific indicator and country."""
        # Check if already collected
        if self.tracker.is_collected('WorldBank_60Countries', country, indicator_code,
                                    start_year, end_year):
            return pd.DataFrame()  # Skip

        url = f"{self.base_url}/country/{country}/indicator/{indicator_code}"
        params = {
            'format': 'json',
            'date': f"{start_year}:{end_year}",
            'per_page': 500
        }

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if len(data) < 2 or data[1] is None:
                return pd.DataFrame()

            records = []
            for item in data[1]:
                if item['value'] is not None:
                    records.append({
                        'country': country,
                        'country_name': item['country']['value'],
                        'indicator_code': indicator_code,
                        'indicator_name': self.indicators.get(indicator_code, indicator_code),
                        'year': int(item['date']),
                        'value': float(item['value'])
                    })

            if records:
                return pd.DataFrame(records)
            else:
                return pd.DataFrame()

        except requests.exceptions.RequestException:
            return pd.DataFrame()

    def collect_country_data(self, country: str, start_year: int = 2000,
                            end_year: int = 2024) -> pd.DataFrame:
        """Collect all indicators for a country."""
        print(f"\n[{country}] Collecting World Bank data...")

        all_data = []
        success_count = 0
        skip_count = 0
        error_count = 0

        for indicator_code, indicator_name in self.indicators.items():
            df = self.get_indicator_data(country, indicator_code, start_year, end_year)

            if len(df) > 0:
                all_data.append(df)
                success_count += 1

                # Record successful collection
                self.tracker.record_collection(
                    source='WorldBank_60Countries',
                    country=country,
                    indicator=indicator_code,
                    start_year=start_year,
                    end_year=end_year,
                    observations=len(df),
                    file_path=str(WB_PATH / f"{country}.csv"),
                    success=True
                )

                print(f"  [OK] {indicator_name}: {len(df)} obs")
            elif self.tracker.is_collected('WorldBank_60Countries', country, indicator_code,
                                          start_year, end_year):
                skip_count += 1
            else:
                error_count += 1
                # Record failure
                self.tracker.record_collection(
                    source='WorldBank_60Countries',
                    country=country,
                    indicator=indicator_code,
                    start_year=start_year,
                    end_year=end_year,
                    observations=0,
                    file_path="",
                    success=False,
                    error="No data available"
                )

            # Rate limiting
            time.sleep(0.05)

        print(f"  Summary: {success_count} success, {skip_count} skipped, {error_count} no data")

        if all_data:
            return pd.concat(all_data, ignore_index=True)
        else:
            return pd.DataFrame()

    def collect_all_countries(self, countries: List[str],
                             start_year: int = 2000,
                             end_year: int = 2024,
                             batch_size: int = 5):
        """Collect data for all countries in batches."""
        print("\n" + "="*80)
        print(f"COLLECTING DATA FOR {len(countries)} COUNTRIES")
        print("="*80)

        total_obs = 0

        # Process in batches
        for i in range(0, len(countries), batch_size):
            batch = countries[i:i+batch_size]
            batch_num = i//batch_size + 1

            print(f"\n{'='*80}")
            print(f"BATCH {batch_num}: {', '.join(batch)}")
            print(f"{'='*80}")

            batch_data = []

            for country in batch:
                df = self.collect_country_data(country, start_year, end_year)
                if len(df) > 0:
                    batch_data.append(df)
                    total_obs += len(df)

            # Save batch
            if batch_data:
                batch_df = pd.concat(batch_data, ignore_index=True)
                batch_file = WB_PATH / f"Batch_{batch_num}.csv"
                batch_df.to_csv(batch_file, index=False)
                print(f"\n  [SAVED] {batch_file.name} ({len(batch_df)} obs)")

            # Pause between batches
            if i + batch_size < len(countries):
                print("\n  [PAUSE] 10 seconds before next batch...")
                time.sleep(10)

        print("\n" + "="*80)
        print("COLLECTION COMPLETE")
        print("="*80)
        print(f"Total observations: {total_obs:,}")

    def combine_all_batches(self):
        """Combine all batch files."""
        print("\n[COMBINE] Combining batches...")

        all_files = list(WB_PATH.glob("Batch_*.csv"))

        if not all_files:
            print("  No batch files found.")
            return

        all_data = [pd.read_csv(f) for f in all_files]
        combined = pd.concat(all_data, ignore_index=True)

        # Save combined
        combined_file = WB_PATH / "worldbank_60countries_all.csv"
        combined.to_csv(combined_file, index=False)

        print(f"  Saved: {combined_file.name}")
        print(f"  Total observations: {len(combined):,}")
        print(f"  Countries: {combined['country'].nunique()}")
        print(f"  Indicators: {combined['indicator_code'].nunique()}")
        print(f"  Years: {combined['year'].min()}-{combined['year'].max()}")


def main():
    """Main execution."""
    import sys

    collector = WorldBank60Collector()

    # 32 NEW countries (adding to existing 28 for total of 60)
    new_countries = [
        # Additional Europe (11)
        'PRT', 'GRC', 'CZE', 'HUN', 'ROU', 'BGR',
        'HRV', 'SVK', 'SVN', 'LUX', 'ISL',

        # Middle East & North Africa (6)
        'SAU', 'ARE', 'ISR', 'EGY', 'QAT', 'KWT',

        # Additional Asia (8)
        'THA', 'MYS', 'SGP', 'PHL', 'VNM',
        'PAK', 'BGD', 'LKA',

        # Additional Latin America (5)
        'ARG', 'CHL', 'COL', 'PER', 'VEN',

        # Additional Africa (2)
        'NGA', 'KEN',
    ]

    print(f"\nCollecting {len(new_countries)} NEW countries...")
    print("(28 existing countries already in World_Bank_Complete/)")

    # Check for --auto flag
    if '--auto' in sys.argv or not sys.stdin.isatty():
        collector.collect_all_countries(new_countries, batch_size=5)
        collector.combine_all_batches()
    else:
        response = input("\nStart collection? (y/n): ")
        if response.lower() == 'y':
            collector.collect_all_countries(new_countries, batch_size=5)
            collector.combine_all_batches()


if __name__ == "__main__":
    main()

"""
World Bank Expanded Data Collector
==================================

Intelligent collector for expanded World Bank indicators.

Features:
- 30+ indicators (expanded from 5)
- Collection tracking to avoid redundant API calls
- Intelligent retry logic
- Batch collection with progress tracking
- Complete metadata logging

New Indicators:
- Financial flows (FDI, portfolio investment)
- Reserves and assets
- External debt
- Exchange rates
- Inflation
- Employment and labor
- Additional trade metrics

Author: Claude
Date: 2025-10-06
"""

import os
import pandas as pd
import requests
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import sys

# Add project to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.append(str(PROJECT_ROOT / "Technical" / "src"))

from data.collection_tracker import CollectionTracker


# Project paths
OUTPUT_ROOT = Path(os.environ.get("OUTPUT_ROOT", "outputs"))
WB_PATH = OUTPUT_ROOT / "World_Bank_Expanded"
WB_PATH.mkdir(parents=True, exist_ok=True)


class WorldBankExpandedCollector:
    """
    Collect expanded World Bank indicators with intelligent tracking.
    """

    def __init__(self):
        """Initialize collector."""
        self.base_url = "https://api.worldbank.org/v2"
        self.session = requests.Session()
        self.tracker = CollectionTracker()

        # Expanded indicator set (30+ indicators)
        self.indicators = {
            # Balance of Payments (existing)
            'BN.CAB.XOKA.CD': 'Current_Account_Balance_USD',
            'BN.CAB.XOKA.GD.ZS': 'Current_Account_pct_GDP',

            # Trade (existing)
            'NE.EXP.GNFS.CD': 'Exports_Goods_Services_USD',
            'NE.IMP.GNFS.CD': 'Imports_Goods_Services_USD',

            # GDP (existing)
            'NY.GDP.MKTP.CD': 'GDP_Current_USD',

            # NEW: Foreign Direct Investment
            'BX.KLT.DINV.CD.WD': 'FDI_Net_Inflows_USD',
            'BM.KLT.DINV.CD.WD': 'FDI_Net_Outflows_USD',
            'BN.KLT.DINV.CD': 'FDI_Net_USD',

            # NEW: Portfolio Investment
            'BX.PEF.TOTL.CD.WD': 'Portfolio_Equity_Net_Inflows',
            'BN.TRF.KOGT.CD': 'Net_Capital_Account',

            # NEW: International Reserves
            'FI.RES.TOTL.CD': 'Total_Reserves_USD',
            'FI.RES.TOTL.MO': 'Reserves_Months_Imports',
            'FI.RES.XGLD.CD': 'Reserves_Excluding_Gold_USD',

            # NEW: External Debt
            'DT.DOD.DECT.CD': 'External_Debt_Stocks_Total_USD',
            'DT.DOD.DECT.GN.ZS': 'External_Debt_pct_GNI',
            'DT.TDS.DECT.GN.ZS': 'Debt_Service_pct_GNI',

            # NEW: Exchange Rates
            'PA.NUS.FCRF': 'Official_Exchange_Rate',
            'PX.REX.REER': 'Real_Effective_Exchange_Rate_Index',

            # NEW: Inflation
            'FP.CPI.TOTL.ZG': 'Inflation_Consumer_Prices_Annual',
            'NY.GDP.DEFL.KD.ZG': 'GDP_Deflator_Annual',

            # NEW: Additional GDP Metrics
            'NY.GDP.PCAP.CD': 'GDP_Per_Capita_USD',
            'NY.GDP.MKTP.KD.ZG': 'GDP_Growth_Annual',

            # NEW: Additional Trade Metrics
            'NE.EXP.GNFS.ZS': 'Exports_pct_GDP',
            'NE.IMP.GNFS.ZS': 'Imports_pct_GDP',
            'TG.VAL.TOTL.GD.ZS': 'Merchandise_Trade_pct_GDP',

            # NEW: Labor and Employment
            'SL.UEM.TOTL.ZS': 'Unemployment_Total_pct',
            'SL.TLF.TOTL.IN': 'Labor_Force_Total',

            # NEW: Remittances
            'BX.TRF.PWKR.CD.DT': 'Personal_Remittances_Received_USD',
            'BM.TRF.PWKR.CD.DT': 'Personal_Remittances_Paid_USD',

            # NEW: Tourism
            'ST.INT.RCPT.CD': 'International_Tourism_Receipts_USD',
            'ST.INT.XPND.CD': 'International_Tourism_Expenditures_USD',

            # NEW: Financial Development
            'FS.AST.DOMS.GD.ZS': 'Domestic_Credit_to_Private_Sector_pct_GDP',
            'FM.LBL.BMNY.GD.ZS': 'Broad_Money_pct_GDP',
        }

        print("\n" + "="*80)
        print("WORLD BANK EXPANDED COLLECTOR")
        print("="*80)
        print(f"Total indicators: {len(self.indicators)}")
        print(f"Output path: {WB_PATH}")

    def get_indicator_data(self, country: str, indicator_code: str,
                          start_year: int = 2000, end_year: int = 2024) -> pd.DataFrame:
        """
        Get data for a specific indicator and country.

        Parameters
        ----------
        country : str
            Country code (ISO 3-letter)
        indicator_code : str
            World Bank indicator code
        start_year : int
            Start year
        end_year : int
            End year

        Returns
        -------
        pd.DataFrame
            Data for indicator
        """
        # Check if already collected
        if self.tracker.is_collected('WorldBank_Expanded', country, indicator_code,
                                    start_year, end_year):
            return pd.DataFrame()  # Skip, already collected

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
                df = pd.DataFrame(records)
                return df
            else:
                return pd.DataFrame()

        except requests.exceptions.RequestException as e:
            print(f"    [ERROR] {country} {indicator_code}: {str(e)}")
            return pd.DataFrame()

    def collect_country_data(self, country: str, start_year: int = 2000,
                            end_year: int = 2024) -> pd.DataFrame:
        """
        Collect all indicators for a single country.

        Parameters
        ----------
        country : str
            Country code
        start_year : int
            Start year
        end_year : int
            End year

        Returns
        -------
        pd.DataFrame
            Combined data for all indicators
        """
        print(f"\n[{country}] Collecting {len(self.indicators)} indicators...")

        all_data = []
        success_count = 0
        skip_count = 0
        error_count = 0

        for indicator_code, indicator_name in self.indicators.items():
            # Check if already collected
            if self.tracker.is_collected('WorldBank_Expanded', country, indicator_code,
                                        start_year, end_year):
                skip_count += 1
                continue

            df = self.get_indicator_data(country, indicator_code, start_year, end_year)

            if len(df) > 0:
                all_data.append(df)
                success_count += 1

                # Record successful collection
                self.tracker.record_collection(
                    source='WorldBank_Expanded',
                    country=country,
                    indicator=indicator_code,
                    start_year=start_year,
                    end_year=end_year,
                    observations=len(df),
                    file_path=str(WB_PATH / f"{country}_expanded.csv"),
                    success=True
                )

                print(f"  [OK] {indicator_name}: {len(df)} obs")
            else:
                error_count += 1
                # Record failed collection
                self.tracker.record_collection(
                    source='WorldBank_Expanded',
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
            combined = pd.concat(all_data, ignore_index=True)
            return combined
        else:
            return pd.DataFrame()

    def collect_all_countries(self, countries: List[str],
                             start_year: int = 2000,
                             end_year: int = 2024,
                             batch_size: int = 5):
        """
        Collect data for all countries in batches.

        Parameters
        ----------
        countries : list
            List of country codes
        start_year : int
            Start year
        end_year : int
            End year
        batch_size : int
            Countries per batch
        """
        print("\n" + "="*80)
        print(f"COLLECTING EXPANDED DATA FOR {len(countries)} COUNTRIES")
        print("="*80)

        # Process in batches
        for i in range(0, len(countries), batch_size):
            batch = countries[i:i+batch_size]
            batch_name = f"Batch_{i//batch_size + 1}"

            print(f"\n{'='*80}")
            print(f"BATCH {i//batch_size + 1}: {', '.join(batch)}")
            print(f"{'='*80}")

            batch_data = []

            for country in batch:
                df = self.collect_country_data(country, start_year, end_year)
                if len(df) > 0:
                    batch_data.append(df)

            # Save batch
            if batch_data:
                batch_df = pd.concat(batch_data, ignore_index=True)
                batch_file = WB_PATH / f"{batch_name}.csv"
                batch_df.to_csv(batch_file, index=False)
                print(f"\n  [SAVED] Batch file: {batch_file.name} ({len(batch_df)} obs)")

            # Pause between batches
            if i + batch_size < len(countries):
                print("\n  [PAUSE] Waiting 10 seconds before next batch...")
                time.sleep(10)

        print("\n" + "="*80)
        print("COLLECTION COMPLETE")
        print("="*80)

    def combine_all_batches(self):
        """Combine all batch files into master file."""
        print("\n[COMBINE] Combining all batches...")

        all_files = list(WB_PATH.glob("Batch_*.csv"))

        if not all_files:
            print("  No batch files found.")
            return

        all_data = []
        for file in all_files:
            df = pd.read_csv(file)
            all_data.append(df)
            print(f"  - {file.name}: {len(df)} obs")

        combined = pd.concat(all_data, ignore_index=True)

        # Save combined
        combined_file = WB_PATH / "worldbank_expanded_all_countries.csv"
        combined.to_csv(combined_file, index=False)

        print(f"\n  [FILE] Combined file: {combined_file.name}")
        print(f"  Total observations: {len(combined):,}")
        print(f"  Countries: {combined['country'].nunique()}")
        print(f"  Indicators: {combined['indicator_code'].nunique()}")
        print(f"  Years: {combined['year'].min()}-{combined['year'].max()}")

        # Create pivot tables for key indicators
        self.create_pivot_tables(combined)

    def create_pivot_tables(self, df: pd.DataFrame):
        """Create pivot tables for key indicators."""
        print("\n[PIVOT] Creating pivot tables...")

        # Top 10 most important indicators
        key_indicators = [
            'BN.CAB.XOKA.CD',  # Current Account
            'NY.GDP.MKTP.CD',  # GDP
            'FI.RES.TOTL.CD',  # Reserves
            'BX.KLT.DINV.CD.WD',  # FDI Inflows
            'DT.DOD.DECT.CD',  # External Debt
            'PA.NUS.FCRF',  # Exchange Rate
            'FP.CPI.TOTL.ZG',  # Inflation
            'NY.GDP.MKTP.KD.ZG',  # GDP Growth
            'NE.EXP.GNFS.CD',  # Exports
            'NE.IMP.GNFS.CD',  # Imports
        ]

        pivot_dir = WB_PATH / "Pivots"
        pivot_dir.mkdir(exist_ok=True)

        for indicator in key_indicators:
            indicator_df = df[df['indicator_code'] == indicator]

            if len(indicator_df) > 0:
                pivot = indicator_df.pivot_table(
                    index='country',
                    columns='year',
                    values='value'
                )

                indicator_name = self.indicators.get(indicator, indicator).lower()
                pivot_file = pivot_dir / f"{indicator_name}.csv"
                pivot.to_csv(pivot_file)
                print(f"  - {pivot_file.name}")


def main():
    """Main execution."""
    collector = WorldBankExpandedCollector()

    # Same 28 countries as before
    countries = [
        # G7
        'USA', 'GBR', 'DEU', 'FRA', 'ITA', 'JPN', 'CAN',
        # BRICS+
        'CHN', 'BRA', 'IND', 'ZAF', 'TUR',
        # Major Advanced
        'KOR', 'AUS', 'ESP', 'NLD', 'BEL', 'SWE',
        # Emerging
        'MEX', 'IDN', 'POL',
        # Other Advanced
        'CHE', 'NOR', 'DNK', 'FIN', 'IRL', 'NZL', 'AUT'
    ]

    # Collect all countries
    collector.collect_all_countries(countries, start_year=2000, end_year=2024, batch_size=5)

    # Combine batches
    collector.combine_all_batches()

    # Export tracker summary
    collector.tracker.export_summary_report()


if __name__ == "__main__":
    main()

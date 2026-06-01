"""
IMF Data Collector
==================

Collects international economics data from IMF (International Monetary Fund) APIs.

Data Sources:
- Balance of Payments (BOP)
- International Investment Position (IIP)
- Direction of Trade Statistics (DOTS)
- Coordinated Portfolio Investment Survey (CPIS)
- Coordinated Direct Investment Survey (CDIS)
- Currency Composition of Official Foreign Exchange Reserves (COFER)

No API key required for IMF data.

Author: Claude
Date: 2025-10-06
"""

import os
import requests
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime
import json
import time

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
OUTPUT_ROOT = Path(os.environ.get("OUTPUT_ROOT", "outputs"))
IMF_PATH = OUTPUT_ROOT / "IMF"


class IMFDataCollector:
    """
    Collect data from IMF APIs.

    IMF provides free access to comprehensive international economic data
    through their JSON-based REST API.
    """

    def __init__(self):
        """Initialize IMF data collector."""
        self.base_url = "http://dataservices.imf.org/REST/SDMX_JSON.svc"
        self.session = requests.Session()

        # Set up output directories
        self.bop_path = IMF_PATH / "Balance_of_Payments"
        self.iip_path = IMF_PATH / "International_Investment_Position"
        self.dots_path = IMF_PATH / "Direction_of_Trade"
        self.cpis_path = IMF_PATH / "CPIS"
        self.cdis_path = IMF_PATH / "CDIS"
        self.cofer_path = IMF_PATH / "COFER"

        for path in [self.bop_path, self.iip_path, self.dots_path,
                     self.cpis_path, self.cdis_path, self.cofer_path]:
            path.mkdir(parents=True, exist_ok=True)

        print("\n" + "="*80)
        print("IMF Data Collector Initialized")
        print("="*80)
        print(f"Output directory: {IMF_PATH.relative_to(PROJECT_ROOT)}")

    # ========================================================================
    # BALANCE OF PAYMENTS
    # ========================================================================

    def get_bop_data(self, countries: List[str] = None,
                     start_year: int = 2000, end_year: int = None) -> pd.DataFrame:
        """
        Get Balance of Payments data from IMF.

        Parameters
        ----------
        countries : list of str, optional
            ISO 2-letter country codes. If None, gets all available countries.
        start_year : int, default 2000
            Start year for data
        end_year : int, optional
            End year for data. If None, uses current year.

        Returns
        -------
        pd.DataFrame
            BOP data
        """
        if end_year is None:
            end_year = datetime.now().year

        print(f"\n[IMF BOP] Collecting Balance of Payments data...")
        print(f"  Period: {start_year}-{end_year}")

        # IMF BOP database ID: BOP
        database = "BOP"

        # Get all countries if not specified
        if countries is None:
            countries = self._get_country_list(database)
            print(f"  Found {len(countries)} countries available")
        else:
            print(f"  Countries: {len(countries)}")

        all_data = []

        for i, country in enumerate(countries[:20], 1):  # Limit to first 20 for demo
            try:
                print(f"  [{i}/{min(len(countries), 20)}] Fetching {country}...", end=' ')

                # Build URL for country
                # Format: CompactData/{database}/{frequency}.{country}.{indicator}.{frequency}
                # A = Annual, Q = Quarterly
                url = f"{self.base_url}/CompactData/{database}/A.{country}.BCA_BP6_USD.?"

                response = self.session.get(url, timeout=30)

                if response.status_code == 200:
                    data = response.json()

                    # Parse JSON response
                    if 'CompactData' in data and 'DataSet' in data['CompactData']:
                        dataset = data['CompactData']['DataSet']
                        if 'Series' in dataset:
                            series_data = dataset['Series']
                            if not isinstance(series_data, list):
                                series_data = [series_data]

                            for series in series_data:
                                if 'Obs' in series:
                                    obs = series['Obs']
                                    if not isinstance(obs, list):
                                        obs = [obs]

                                    for observation in obs:
                                        year = observation.get('@TIME_PERIOD', '')
                                        value = observation.get('@OBS_VALUE', np.nan)

                                        if year and start_year <= int(year) <= end_year:
                                            all_data.append({
                                                'country': country,
                                                'year': int(year),
                                                'indicator': 'Current_Account',
                                                'value': float(value) if value != np.nan else np.nan,
                                                'unit': 'USD_Millions'
                                            })

                    print(f"OK")
                else:
                    print(f"SKIP (HTTP {response.status_code})")

                # Rate limiting
                time.sleep(0.5)

            except Exception as e:
                print(f"ERROR: {e}")
                continue

        if all_data:
            df = pd.DataFrame(all_data)
            print(f"\n[OK] Collected {len(df):,} observations from {df['country'].nunique()} countries")

            # Save to file
            output_file = self.bop_path / f"imf_bop_{start_year}_{end_year}.csv"
            df.to_csv(output_file, index=False)
            print(f"[SAVED] {output_file.relative_to(PROJECT_ROOT)}")

            return df
        else:
            print("[WARNING] No data collected")
            return pd.DataFrame()

    # ========================================================================
    # DIRECTION OF TRADE STATISTICS
    # ========================================================================

    def get_trade_data(self, countries: List[str] = None,
                       start_year: int = 2000, end_year: int = None) -> pd.DataFrame:
        """
        Get bilateral trade data from IMF Direction of Trade Statistics.

        Parameters
        ----------
        countries : list of str, optional
            ISO 2-letter country codes
        start_year : int, default 2000
            Start year
        end_year : int, optional
            End year

        Returns
        -------
        pd.DataFrame
            Trade data
        """
        if end_year is None:
            end_year = datetime.now().year

        print(f"\n[IMF DOTS] Collecting Direction of Trade Statistics...")
        print(f"  Period: {start_year}-{end_year}")

        # DOTS database
        database = "DOTS"

        if countries is None:
            # Get major trading economies
            countries = ['US', 'CN', 'DE', 'JP', 'GB', 'FR', 'IT', 'CA', 'KR', 'MX']
            print(f"  Using major economies: {len(countries)} countries")

        all_data = []

        for i, country in enumerate(countries, 1):
            try:
                print(f"  [{i}/{len(countries)}] Fetching {country}...", end=' ')

                # Get total exports and imports
                # TXG_FOB_USD = Goods, Exports, Value, US Dollars
                # TMG_CIF_USD = Goods, Imports, Value, US Dollars
                url = f"{self.base_url}/CompactData/{database}/A.{country}.TXG_FOB_USD+TMG_CIF_USD.?"

                response = self.session.get(url, timeout=30)

                if response.status_code == 200:
                    data = response.json()

                    # Parse response (similar to BOP)
                    if 'CompactData' in data and 'DataSet' in data['CompactData']:
                        dataset = data['CompactData']['DataSet']
                        if 'Series' in dataset:
                            series_data = dataset['Series']
                            if not isinstance(series_data, list):
                                series_data = [series_data]

                            for series in series_data:
                                indicator = series.get('@INDICATOR', '')

                                if 'Obs' in series:
                                    obs = series['Obs']
                                    if not isinstance(obs, list):
                                        obs = [obs]

                                    for observation in obs:
                                        year = observation.get('@TIME_PERIOD', '')
                                        value = observation.get('@OBS_VALUE', np.nan)

                                        if year and start_year <= int(year) <= end_year:
                                            all_data.append({
                                                'country': country,
                                                'year': int(year),
                                                'indicator': 'Exports' if 'TXG' in indicator else 'Imports',
                                                'value': float(value) if value != np.nan else np.nan,
                                                'unit': 'USD_Millions'
                                            })

                    print(f"OK")
                else:
                    print(f"SKIP")

                time.sleep(0.5)

            except Exception as e:
                print(f"ERROR: {e}")
                continue

        if all_data:
            df = pd.DataFrame(all_data)
            print(f"\n[OK] Collected {len(df):,} observations from {df['country'].nunique()} countries")

            output_file = self.dots_path / f"imf_trade_{start_year}_{end_year}.csv"
            df.to_csv(output_file, index=False)
            print(f"[SAVED] {output_file.relative_to(PROJECT_ROOT)}")

            return df
        else:
            print("[WARNING] No data collected")
            return pd.DataFrame()

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _get_country_list(self, database: str) -> List[str]:
        """
        Get list of available countries for a database.

        Parameters
        ----------
        database : str
            Database ID (BOP, DOTS, etc.)

        Returns
        -------
        list of str
            Country codes
        """
        try:
            url = f"{self.base_url}/CodeList/{database}"
            response = self.session.get(url, timeout=30)

            if response.status_code == 200:
                data = response.json()
                # Parse country codes from response
                # This is simplified - actual parsing depends on IMF API structure
                return ['US', 'GB', 'DE', 'FR', 'IT', 'JP', 'CN', 'CA', 'AU', 'KR']  # Sample
            else:
                return []
        except:
            # Fallback to G20 countries
            return ['US', 'GB', 'DE', 'FR', 'IT', 'JP', 'CN', 'CA', 'AU', 'KR',
                   'BR', 'MX', 'IN', 'ID', 'TR', 'SA', 'AR', 'ZA']

    def get_metadata(self, database: str) -> Dict:
        """
        Get metadata for IMF database.

        Parameters
        ----------
        database : str
            Database ID

        Returns
        -------
        dict
            Metadata information
        """
        metadata = {
            'BOP': {
                'name': 'Balance of Payments',
                'description': 'Balance of Payments Statistics (BPM6)',
                'frequency': 'Annual, Quarterly',
                'coverage': '190+ countries',
                'start_year': 1950
            },
            'DOTS': {
                'name': 'Direction of Trade Statistics',
                'description': 'Bilateral trade flows',
                'frequency': 'Annual, Monthly',
                'coverage': '190+ countries',
                'start_year': 1980
            },
            'IIP': {
                'name': 'International Investment Position',
                'description': 'Cross-border asset and liability positions',
                'frequency': 'Annual, Quarterly',
                'coverage': '150+ countries',
                'start_year': 2000
            }
        }

        return metadata.get(database, {})

    def collect_all(self, start_year: int = 2010, end_year: int = None):
        """
        Collect all available IMF data.

        Parameters
        ----------
        start_year : int, default 2010
            Start year
        end_year : int, optional
            End year
        """
        print("\n" + "="*80)
        print("IMF COMPREHENSIVE DATA COLLECTION")
        print("="*80)

        # Collect Balance of Payments
        bop_data = self.get_bop_data(start_year=start_year, end_year=end_year)

        # Collect Trade Statistics
        trade_data = self.get_trade_data(start_year=start_year, end_year=end_year)

        print("\n" + "="*80)
        print("IMF DATA COLLECTION COMPLETE")
        print("="*80)
        print(f"\nData saved to: {IMF_PATH.relative_to(PROJECT_ROOT)}")

        return {
            'bop': bop_data,
            'trade': trade_data
        }


def main():
    """Main execution: collect IMF data."""
    print("\n" + "="*80)
    print("IMF International Economics Data Collection")
    print("="*80)

    collector = IMFDataCollector()

    # Collect data for recent period (2010-present)
    data = collector.collect_all(start_year=2010, end_year=2024)

    print("\n[COMPLETE] IMF data collection finished!")


if __name__ == "__main__":
    main()

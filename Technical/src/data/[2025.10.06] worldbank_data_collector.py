"""
World Bank Data Collector
==========================

Collects international economics data from World Bank API.

Data Sources:
- Balance of Payments indicators
- Trade statistics
- GDP and normalization data
- Development indicators

No API key required.

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
WB_PATH = OUTPUT_ROOT / "World_Bank"


class WorldBankDataCollector:
    """
    Collect data from World Bank API.

    World Bank provides free access to 16,000+ indicators for 190+ countries.
    """

    def __init__(self):
        """Initialize World Bank data collector."""
        self.base_url = "https://api.worldbank.org/v2"
        self.session = requests.Session()

        # Set up output directories
        self.bop_path = WB_PATH / "Balance_of_Payments"
        self.trade_path = WB_PATH / "Trade"
        self.gdp_path = WB_PATH / "GDP"
        self.indicators_path = WB_PATH / "Indicators"

        for path in [self.bop_path, self.trade_path, self.gdp_path, self.indicators_path]:
            path.mkdir(parents=True, exist_ok=True)

        print("\n" + "="*80)
        print("World Bank Data Collector Initialized")
        print("="*80)
        print(f"Output directory: {WB_PATH.relative_to(PROJECT_ROOT)}")

        # Key indicators for balance of payments
        self.bop_indicators = {
            'BN.CAB.XOKA.CD': 'Current_Account_Balance_USD',
            'BN.CAB.XOKA.GD.ZS': 'Current_Account_pct_GDP',
            'BN.KLT.DINV.CD': 'Foreign_Direct_Investment_Net_USD',
            'BN.KLT.PTXL.CD': 'Portfolio_Investment_Net_USD',
            'BN.FIN.TOTL.CD': 'Financial_Account_Net_USD',
            'BN.GSR.FCTY.CD': 'Primary_Income_Net_USD',
            'BN.TRF.CURR.CD': 'Secondary_Income_Net_USD',
        }

        # Trade indicators
        self.trade_indicators = {
            'NE.EXP.GNFS.CD': 'Exports_Goods_Services_USD',
            'NE.IMP.GNFS.CD': 'Imports_Goods_Services_USD',
            'NE.RSB.GNFS.CD': 'Trade_Balance_USD',
            'NE.EXP.GNFS.ZS': 'Exports_pct_GDP',
            'NE.IMP.GNFS.ZS': 'Imports_pct_GDP',
            'TG.VAL.TOTL.GD.ZS': 'Merchandise_Trade_pct_GDP',
        }

        # GDP indicators
        self.gdp_indicators = {
            'NY.GDP.MKTP.CD': 'GDP_Current_USD',
            'NY.GDP.MKTP.KD': 'GDP_Constant_2015_USD',
            'NY.GDP.MKTP.KD.ZG': 'GDP_Growth_Annual',
            'NY.GDP.PCAP.CD': 'GDP_Per_Capita_USD',
        }

        # Priority countries to collect
        self.priority_countries = [
            'USA', 'GBR', 'DEU', 'FRA', 'ITA', 'JPN', 'CAN',  # G7
            'CHN', 'KOR', 'MEX', 'AUS', 'BRA', 'IND',  # Major emerging
            'ESP', 'NLD', 'BEL', 'SWE', 'POL', 'AUT',  # EU
            'CHE', 'NOR', 'DNK', 'FIN', 'IRL', 'NZL',  # Other advanced
        ]

    # ========================================================================
    # BALANCE OF PAYMENTS DATA
    # ========================================================================

    def get_bop_data(self, countries: List[str] = None,
                     start_year: int = 2000, end_year: int = None) -> pd.DataFrame:
        """
        Get Balance of Payments indicators from World Bank.

        Parameters
        ----------
        countries : list of str, optional
            ISO 3-letter country codes. If None, uses priority countries.
        start_year : int, default 2000
            Start year for data
        end_year : int, optional
            End year for data. If None, uses current year.

        Returns
        -------
        pd.DataFrame
            BOP data with columns: country, year, indicator, value
        """
        if end_year is None:
            end_year = datetime.now().year

        if countries is None:
            countries = self.priority_countries

        print(f"\n[World Bank BOP] Collecting Balance of Payments indicators...")
        print(f"  Period: {start_year}-{end_year}")
        print(f"  Countries: {len(countries)}")
        print(f"  Indicators: {len(self.bop_indicators)}")

        all_data = []

        for i, country in enumerate(countries, 1):
            print(f"\n  [{i}/{len(countries)}] {country}")

            for indicator_code, indicator_name in self.bop_indicators.items():
                try:
                    print(f"    - {indicator_name}...", end=' ')

                    # Build URL
                    url = f"{self.base_url}/country/{country}/indicator/{indicator_code}"
                    params = {
                        'date': f'{start_year}:{end_year}',
                        'format': 'json',
                        'per_page': 1000
                    }

                    response = self.session.get(url, params=params, timeout=30)

                    if response.status_code == 200:
                        data = response.json()

                        # World Bank returns [metadata, data]
                        if len(data) > 1 and data[1]:
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
                            print(f"OK ({len(data[1])} obs)")
                        else:
                            print("No data")
                    else:
                        print(f"Error {response.status_code}")

                    # Rate limiting - be polite
                    time.sleep(0.1)

                except Exception as e:
                    print(f"ERROR: {str(e)[:50]}")
                    continue

        if all_data:
            df = pd.DataFrame(all_data)
            print(f"\n[OK] Collected {len(df):,} observations")
            print(f"  Countries: {df['country'].nunique()}")
            print(f"  Indicators: {df['indicator_name'].nunique()}")
            print(f"  Years: {df['year'].min()}-{df['year'].max()}")

            # Save to file
            output_file = self.bop_path / f"worldbank_bop_{start_year}_{end_year}.csv"
            df.to_csv(output_file, index=False)
            print(f"[SAVED] {output_file.relative_to(PROJECT_ROOT)}")

            return df
        else:
            print("[WARNING] No data collected")
            return pd.DataFrame()

    # ========================================================================
    # TRADE DATA
    # ========================================================================

    def get_trade_data(self, countries: List[str] = None,
                       start_year: int = 2000, end_year: int = None) -> pd.DataFrame:
        """
        Get trade indicators from World Bank.

        Parameters
        ----------
        countries : list of str, optional
            ISO 3-letter country codes
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

        if countries is None:
            countries = self.priority_countries

        print(f"\n[World Bank Trade] Collecting trade indicators...")
        print(f"  Period: {start_year}-{end_year}")
        print(f"  Countries: {len(countries)}")
        print(f"  Indicators: {len(self.trade_indicators)}")

        all_data = []

        for i, country in enumerate(countries, 1):
            print(f"\n  [{i}/{len(countries)}] {country}")

            for indicator_code, indicator_name in self.trade_indicators.items():
                try:
                    print(f"    - {indicator_name}...", end=' ')

                    url = f"{self.base_url}/country/{country}/indicator/{indicator_code}"
                    params = {
                        'date': f'{start_year}:{end_year}',
                        'format': 'json',
                        'per_page': 1000
                    }

                    response = self.session.get(url, params=params, timeout=30)

                    if response.status_code == 200:
                        data = response.json()

                        if len(data) > 1 and data[1]:
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
                            print(f"OK ({len(data[1])} obs)")
                        else:
                            print("No data")
                    else:
                        print(f"Error {response.status_code}")

                    time.sleep(0.1)

                except Exception as e:
                    print(f"ERROR: {str(e)[:50]}")
                    continue

        if all_data:
            df = pd.DataFrame(all_data)
            print(f"\n[OK] Collected {len(df):,} observations")

            output_file = self.trade_path / f"worldbank_trade_{start_year}_{end_year}.csv"
            df.to_csv(output_file, index=False)
            print(f"[SAVED] {output_file.relative_to(PROJECT_ROOT)}")

            return df
        else:
            print("[WARNING] No data collected")
            return pd.DataFrame()

    # ========================================================================
    # GDP DATA
    # ========================================================================

    def get_gdp_data(self, countries: List[str] = None,
                     start_year: int = 1960, end_year: int = None) -> pd.DataFrame:
        """
        Get GDP indicators from World Bank.

        Parameters
        ----------
        countries : list of str, optional
            ISO 3-letter country codes
        start_year : int, default 1960
            Start year
        end_year : int, optional
            End year

        Returns
        -------
        pd.DataFrame
            GDP data
        """
        if end_year is None:
            end_year = datetime.now().year

        if countries is None:
            countries = self.priority_countries

        print(f"\n[World Bank GDP] Collecting GDP indicators...")
        print(f"  Period: {start_year}-{end_year}")
        print(f"  Countries: {len(countries)}")
        print(f"  Indicators: {len(self.gdp_indicators)}")

        all_data = []

        for i, country in enumerate(countries, 1):
            print(f"\n  [{i}/{len(countries)}] {country}")

            for indicator_code, indicator_name in self.gdp_indicators.items():
                try:
                    print(f"    - {indicator_name}...", end=' ')

                    url = f"{self.base_url}/country/{country}/indicator/{indicator_code}"
                    params = {
                        'date': f'{start_year}:{end_year}',
                        'format': 'json',
                        'per_page': 2000  # Longer time series
                    }

                    response = self.session.get(url, params=params, timeout=30)

                    if response.status_code == 200:
                        data = response.json()

                        if len(data) > 1 and data[1]:
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
                            print(f"OK ({len(data[1])} obs)")
                        else:
                            print("No data")
                    else:
                        print(f"Error {response.status_code}")

                    time.sleep(0.1)

                except Exception as e:
                    print(f"ERROR: {str(e)[:50]}")
                    continue

        if all_data:
            df = pd.DataFrame(all_data)
            print(f"\n[OK] Collected {len(df):,} observations")

            output_file = self.gdp_path / f"worldbank_gdp_{start_year}_{end_year}.csv"
            df.to_csv(output_file, index=False)
            print(f"[SAVED] {output_file.relative_to(PROJECT_ROOT)}")

            return df
        else:
            print("[WARNING] No data collected")
            return pd.DataFrame()

    # ========================================================================
    # COMPREHENSIVE COLLECTION
    # ========================================================================

    def collect_all(self, countries: List[str] = None,
                    start_year: int = 2000, end_year: int = None):
        """
        Collect all available World Bank data.

        Parameters
        ----------
        countries : list of str, optional
            ISO 3-letter country codes. If None, uses priority countries.
        start_year : int, default 2000
            Start year
        end_year : int, optional
            End year
        """
        print("\n" + "="*80)
        print("WORLD BANK COMPREHENSIVE DATA COLLECTION")
        print("="*80)

        # Collect Balance of Payments
        bop_data = self.get_bop_data(countries=countries,
                                     start_year=start_year,
                                     end_year=end_year)

        # Collect Trade Statistics
        trade_data = self.get_trade_data(countries=countries,
                                         start_year=start_year,
                                         end_year=end_year)

        # Collect GDP (longer time series)
        gdp_data = self.get_gdp_data(countries=countries,
                                     start_year=1960,
                                     end_year=end_year)

        print("\n" + "="*80)
        print("WORLD BANK DATA COLLECTION COMPLETE")
        print("="*80)
        print(f"\nData saved to: {WB_PATH.relative_to(PROJECT_ROOT)}")
        print(f"\nSummary:")
        print(f"  BOP observations: {len(bop_data):,}")
        print(f"  Trade observations: {len(trade_data):,}")
        print(f"  GDP observations: {len(gdp_data):,}")
        print(f"  Total: {len(bop_data) + len(trade_data) + len(gdp_data):,}")

        return {
            'bop': bop_data,
            'trade': trade_data,
            'gdp': gdp_data
        }

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def get_country_list(self) -> pd.DataFrame:
        """
        Get list of all countries from World Bank API.

        Returns
        -------
        pd.DataFrame
            Country codes and names
        """
        try:
            url = f"{self.base_url}/country"
            params = {'format': 'json', 'per_page': 500}

            response = self.session.get(url, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()

                if len(data) > 1 and data[1]:
                    countries = []
                    for country in data[1]:
                        if country.get('capitalCity'):  # Filter to actual countries
                            countries.append({
                                'code': country.get('id'),
                                'name': country.get('name'),
                                'region': country.get('region', {}).get('value', ''),
                                'income_level': country.get('incomeLevel', {}).get('value', '')
                            })

                    df = pd.DataFrame(countries)
                    print(f"Found {len(df)} countries")
                    return df
        except Exception as e:
            print(f"Error getting country list: {e}")

        return pd.DataFrame()


def main():
    """Main execution: collect World Bank data."""
    print("\n" + "="*80)
    print("World Bank International Economics Data Collection")
    print("="*80)

    collector = WorldBankDataCollector()

    # Collect data for recent period (2000-present) for priority countries
    data = collector.collect_all(start_year=2000, end_year=2024)

    print("\n[COMPLETE] World Bank data collection finished!")


if __name__ == "__main__":
    main()

"""
UN Comtrade Data Collector
===========================

Collects bilateral trade data from UN Comtrade API.

Data Sources:
- Bilateral merchandise trade flows
- Product-level trade data (HS codes)
- Trade by partner country

Requires API key (free registration).

Author: Claude
Date: 2025-10-06
"""

import os
import requests
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import json
import time

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
OUTPUT_ROOT = Path(os.environ.get("OUTPUT_ROOT", "outputs"))
COMTRADE_PATH = OUTPUT_ROOT / "UN_Comtrade"


class ComtradeDataCollector:
    """
    Collect data from UN Comtrade API.

    UN Comtrade provides bilateral trade flows for 200+ countries.
    """

    def __init__(self, api_key: str):
        """
        Initialize UN Comtrade data collector.

        Parameters
        ----------
        api_key : str
            UN Comtrade API key
        """
        self.api_key = api_key
        self.base_url = "https://comtradeapi.un.org/data/v1"
        self.session = requests.Session()

        # Set up output directories
        self.bilateral_path = COMTRADE_PATH / "Bilateral_Trade"
        self.product_path = COMTRADE_PATH / "Product_Level"

        for path in [self.bilateral_path, self.product_path]:
            path.mkdir(parents=True, exist_ok=True)

        print("\n" + "="*80)
        print("UN Comtrade Data Collector Initialized")
        print("="*80)
        print(f"Output directory: {COMTRADE_PATH.relative_to(PROJECT_ROOT)}")

    def get_bilateral_trade(self, reporter: str, partner: str,
                           flow_code: str = 'M',
                           start_year: int = 2010,
                           end_year: int = 2023) -> pd.DataFrame:
        """
        Get bilateral trade between two countries.

        Parameters
        ----------
        reporter : str
            Reporter country code (e.g., 'USA', 'CHN')
        partner : str
            Partner country code (e.g., 'USA', 'CHN')
        flow_code : str, default 'M'
            Trade flow: 'M' = imports, 'X' = exports
        start_year : int, default 2010
            Start year
        end_year : int, default 2023
            End year

        Returns
        -------
        pd.DataFrame
            Bilateral trade data
        """
        print(f"\n  Fetching {reporter} {'imports from' if flow_code == 'M' else 'exports to'} {partner}...")
        print(f"    Period: {start_year}-{end_year}", end=' ')

        all_data = []

        for year in range(start_year, end_year + 1):
            try:
                # Build URL for Comtrade API v1
                url = f"{self.base_url}/get/C/A/{year}/{reporter}/{flow_code}/0"

                params = {
                    'subscription-key': self.api_key,
                    'partner': partner,
                    'format': 'json'
                }

                response = self.session.get(url, params=params, timeout=60)

                if response.status_code == 200:
                    data = response.json()

                    # Parse response
                    if 'data' in data and data['data']:
                        for record in data['data']:
                            all_data.append({
                                'reporter': reporter,
                                'partner': partner,
                                'flow': 'Import' if flow_code == 'M' else 'Export',
                                'year': year,
                                'trade_value_usd': record.get('primaryValue', 0),
                                'commodity_code': record.get('cmdCode', 'TOTAL'),
                                'commodity_desc': record.get('cmdDesc', 'All Commodities'),
                                'quantity': record.get('qty', None),
                                'quantity_unit': record.get('qtyUnit', None)
                            })
                        print(".", end='')
                    else:
                        print("x", end='')

                else:
                    print(f"E{response.status_code}", end='')

                # Rate limiting - respect API limits (100 requests/hour)
                time.sleep(2)

            except Exception as e:
                print(f"ERROR: {e}", end='')
                continue

        print(f" Done ({len(all_data)} records)")

        if all_data:
            df = pd.DataFrame(all_data)
            return df
        else:
            return pd.DataFrame()

    def get_bilateral_aggregate(self, reporter: str, partner: str,
                               start_year: int = 2010,
                               end_year: int = 2023) -> pd.DataFrame:
        """
        Get aggregate bilateral trade (total commodities only).

        Parameters
        ----------
        reporter : str
            Reporter country code
        partner : str
            Partner country code
        start_year : int, default 2010
            Start year
        end_year : int, default 2023
            End year

        Returns
        -------
        pd.DataFrame
            Bilateral trade aggregates
        """
        print(f"\n[Comtrade Bilateral] {reporter} <-> {partner}")

        # Get both imports and exports
        imports = self.get_bilateral_trade(reporter, partner, 'M', start_year, end_year)
        exports = self.get_bilateral_trade(reporter, partner, 'X', start_year, end_year)

        # Combine
        all_data = []
        if not imports.empty:
            all_data.append(imports)
        if not exports.empty:
            all_data.append(exports)

        if all_data:
            df = pd.concat(all_data, ignore_index=True)

            # Filter to TOTAL only
            df = df[df['commodity_code'] == 'TOTAL'].copy()

            # Save
            filename = f"bilateral_{reporter}_{partner}_{start_year}_{end_year}.csv"
            output_file = self.bilateral_path / filename
            df.to_csv(output_file, index=False)
            print(f"  [SAVED] {len(df)} observations")

            return df
        else:
            print("  [WARNING] No data")
            return pd.DataFrame()

    def get_us_major_partners(self, start_year: int = 2015,
                             end_year: int = 2023) -> pd.DataFrame:
        """
        Get US bilateral trade with major trading partners.

        Parameters
        ----------
        start_year : int, default 2015
            Start year
        end_year : int, default 2023
            End year

        Returns
        -------
        pd.DataFrame
            US bilateral trade data
        """
        print(f"\n[Comtrade US Partners] Collecting US bilateral trade...")
        print(f"  Period: {start_year}-{end_year}")

        # Major US trading partners
        partners = ['CHN', 'CAN', 'MEX', 'JPN', 'DEU', 'GBR', 'KOR']

        all_data = []

        for partner in partners:
            df = self.get_bilateral_aggregate('USA', partner, start_year, end_year)
            if not df.empty:
                all_data.append(df)

            # Rate limiting between partners
            time.sleep(5)

        if all_data:
            combined = pd.concat(all_data, ignore_index=True)

            # Save combined
            output_file = self.bilateral_path / f"us_major_partners_{start_year}_{end_year}.csv"
            combined.to_csv(output_file, index=False)
            print(f"\n[SAVED] Combined: {len(combined):,} observations")
            print(f"  {output_file.relative_to(PROJECT_ROOT)}")

            # Summary
            print(f"\nSummary:")
            print(f"  Partners: {combined['partner'].nunique()}")
            print(f"  Years: {combined['year'].min()}-{combined['year'].max()}")

            return combined
        else:
            print("[WARNING] No data collected")
            return pd.DataFrame()

    def collect_all(self, start_year: int = 2015, end_year: int = 2023):
        """
        Collect key bilateral trade data.

        Parameters
        ----------
        start_year : int, default 2015
            Start year
        end_year : int, default 2023
            End year
        """
        print("\n" + "="*80)
        print("UN COMTRADE COMPREHENSIVE DATA COLLECTION")
        print("="*80)

        # Collect US major partners
        us_data = self.get_us_major_partners(start_year, end_year)

        print("\n" + "="*80)
        print("COMTRADE DATA COLLECTION COMPLETE")
        print("="*80)
        print(f"\nData saved to: {COMTRADE_PATH.relative_to(PROJECT_ROOT)}")

        return {
            'us_bilateral': us_data
        }


def main():
    """Main execution: collect UN Comtrade data."""

    # UN Comtrade API key. Get a free key at https://comtradeplus.un.org/
    # and set COMTRADE_API_KEY.
    API_KEY = os.environ.get("COMTRADE_API_KEY")
    if not API_KEY:
        raise SystemExit("COMTRADE_API_KEY not set. See README (Setup) for a free key.")

    print("\n" + "="*80)
    print("UN Comtrade Bilateral Trade Data Collection")
    print("="*80)

    collector = ComtradeDataCollector(api_key=API_KEY)

    # Collect data for recent years (2015-2023)
    # Limited scope to avoid hitting rate limits
    data = collector.collect_all(start_year=2019, end_year=2023)

    print("\n[COMPLETE] Comtrade data collection finished!")


if __name__ == "__main__":
    main()

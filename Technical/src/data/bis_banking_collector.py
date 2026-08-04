"""
BIS International Banking Statistics Collector
==============================================

Collect international banking statistics from Bank for International Settlements.

BIS provides unique data on:
- Cross-border banking flows
- International banking positions
- Global liquidity indicators
- Banking network structures

This data complements IMF Balance of Payments with banking sector detail.

Data Source: BIS Data Portal (stats.bis.org)
API: SDMX RESTful API v1
Coverage: 40+ reporting countries, 200+ counterparty countries
Frequency: Quarterly

Author: Claude (Lewis Platform)
Date: 2025-10-11
"""

import os
import pandas as pd
import requests
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import sys
import json
import xml.etree.ElementTree as ET

# Add project to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.append(str(PROJECT_ROOT / "Technical" / "src"))

# Try to import CollectionTracker, but make it optional
try:
    from data.collection_tracker import CollectionTracker
    HAS_TRACKER = True
except ImportError:
    CollectionTracker = None
    HAS_TRACKER = False
    print("[WARN] CollectionTracker not available - running without tracking")

# Project paths
OUTPUT_ROOT = Path(os.environ.get("OUTPUT_ROOT", "outputs"))
BIS_PATH = OUTPUT_ROOT / "BIS"
BIS_PATH.mkdir(parents=True, exist_ok=True)


class BISBankingCollector:
    """
    Collect BIS international banking statistics.

    BIS compiles banking statistics in cooperation with central banks worldwide,
    providing unique insights into cross-border banking flows and positions.
    """

    def __init__(self):
        """Initialize BIS collector."""
        # BIS SDMX API base
        self.base_url = "https://stats.bis.org/api/v1"
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/vnd.sdmx.data+csv;version=1.0.0",
            "User-Agent": "Mozilla/5.0 (Lewis Economics Platform)"
        })
        self.tracker = CollectionTracker() if HAS_TRACKER else None

        # BIS key dataflows for international banking
        self.dataflows = {
            # Locational Banking Statistics (LBS)
            'LBS_D_PUB': 'Locational Banking Statistics (by residence)',

            # Consolidated Banking Statistics (CBS)
            'CBS_PUB': 'Consolidated Banking Statistics (by nationality)',

            # Debt Service Ratios
            'TOTAL_CREDIT': 'Total Credit to Non-Financial Sector',
        }

        print("\n" + "="*80)
        print("BIS INTERNATIONAL BANKING STATISTICS COLLECTOR")
        print("="*80)
        print(f"Data source: Bank for International Settlements")
        print(f"API: {self.base_url}")
        print(f"Output: {BIS_PATH}")
        print(f"\nDatasets:")
        for code, name in self.dataflows.items():
            print(f"  - {code}: {name}")

    def test_api_access(self) -> bool:
        """Test BIS API connectivity."""
        print("\n[TEST] Testing BIS API access...")

        try:
            # Test with data availability endpoint
            test_url = f"{self.base_url}/dataflow"

            response = self.session.get(test_url, timeout=30)

            if response.status_code == 200:
                print("  [OK] BIS API accessible")
                print(f"  Response size: {len(response.content)} bytes")
                return True
            else:
                print(f"  [ERROR] HTTP {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"  [ERROR] {str(e)[:100]}")
            return False

    def get_locational_banking_stats(self, start_period: str = "2010-Q1",
                                     end_period: str = "2024-Q4") -> pd.DataFrame:
        """
        Get Locational Banking Statistics (LBS).

        LBS captures banks' on-balance-sheet financial claims and liabilities
        by residence (where the banking office is located).

        Parameters
        ----------
        start_period : str
            Start period (format: YYYY-QN)
        end_period : str
            End period (format: YYYY-QN)

        Returns
        -------
        pd.DataFrame
            Locational banking statistics
        """
        print(f"\n[LBS] Collecting Locational Banking Statistics...")
        print(f"  Period: {start_period} to {end_period}")

        try:
            # BIS LBS dataflow: LBS_D_PUB
            # Query structure: dataflow_id/key?parameters
            # Using simplified query for aggregate data
            url = f"{self.base_url}/data/LBS_D_PUB/Q...A..."
            url += f"?startPeriod={start_period}&endPeriod={end_period}"
            url += "&format=csv"

            print(f"  Query URL: {url[:100]}...")

            response = self.session.get(url, timeout=120)

            if response.status_code == 200:
                # Parse CSV response
                from io import StringIO
                df = pd.read_csv(StringIO(response.text))

                if not df.empty:
                    print(f"  [OK] Collected {len(df):,} observations")
                    print(f"  Columns: {list(df.columns)[:5]}...")

                    # Save raw data
                    output_file = BIS_PATH / f"bis_lbs_{start_period}_{end_period}.csv"
                    df.to_csv(output_file, index=False)
                    print(f"  [SAVED] {output_file.relative_to(PROJECT_ROOT)}")

                    return df
                else:
                    print("  [WARN] Empty response")
                    return pd.DataFrame()

            elif response.status_code == 404:
                print("  [WARN] Dataset not found - may need different query structure")
                return pd.DataFrame()

            elif response.status_code == 413:
                print("  [WARN] Response too large - need to narrow query")
                return pd.DataFrame()

            else:
                print(f"  [ERROR] HTTP {response.status_code}")
                if response.text:
                    print(f"  Response: {response.text[:200]}")
                return pd.DataFrame()

        except Exception as e:
            print(f"  [ERROR] {str(e)[:100]}")
            return pd.DataFrame()

    def get_consolidated_banking_stats(self, start_period: str = "2010-Q1",
                                       end_period: str = "2024-Q4") -> pd.DataFrame:
        """
        Get Consolidated Banking Statistics (CBS).

        CBS captures banks' on-balance-sheet financial claims on an immediate
        borrower basis, consolidated worldwide by nationality of reporting banks.

        Parameters
        ----------
        start_period : str
            Start period (format: YYYY-QN)
        end_period : str
            End period (format: YYYY-QN)

        Returns
        -------
        pd.DataFrame
            Consolidated banking statistics
        """
        print(f"\n[CBS] Collecting Consolidated Banking Statistics...")
        print(f"  Period: {start_period} to {end_period}")

        try:
            # BIS CBS dataflow: CBS_PUB
            url = f"{self.base_url}/data/CBS_PUB/Q......."
            url += f"?startPeriod={start_period}&endPeriod={end_period}"
            url += "&format=csv"

            print(f"  Query URL: {url[:100]}...")

            response = self.session.get(url, timeout=120)

            if response.status_code == 200:
                from io import StringIO
                df = pd.read_csv(StringIO(response.text))

                if not df.empty:
                    print(f"  [OK] Collected {len(df):,} observations")

                    output_file = BIS_PATH / f"bis_cbs_{start_period}_{end_period}.csv"
                    df.to_csv(output_file, index=False)
                    print(f"  [SAVED] {output_file.relative_to(PROJECT_ROOT)}")

                    return df
                else:
                    print("  [WARN] Empty response")
                    return pd.DataFrame()

            else:
                print(f"  [ERROR] HTTP {response.status_code}")
                return pd.DataFrame()

        except Exception as e:
            print(f"  [ERROR] {str(e)[:100]}")
            return pd.DataFrame()

    def get_total_credit_stats(self, start_period: str = "2010-Q1",
                               end_period: str = "2024-Q4") -> pd.DataFrame:
        """
        Get Total Credit to Non-Financial Sector statistics.

        Measures total credit from all sources (domestic banks, foreign banks,
        other domestic financial corps, non-financial corps) to the non-financial
        private sector and governments.

        Parameters
        ----------
        start_period : str
            Start period (format: YYYY-QN)
        end_period : str
            End period (format: YYYY-QN)

        Returns
        -------
        pd.DataFrame
            Total credit statistics
        """
        print(f"\n[CREDIT] Collecting Total Credit Statistics...")
        print(f"  Period: {start_period} to {end_period}")

        try:
            # BIS Total Credit dataflow
            url = f"{self.base_url}/data/TOTAL_CREDIT/Q........"
            url += f"?startPeriod={start_period}&endPeriod={end_period}"
            url += "&format=csv"

            print(f"  Query URL: {url[:100]}...")

            response = self.session.get(url, timeout=120)

            if response.status_code == 200:
                from io import StringIO
                df = pd.read_csv(StringIO(response.text))

                if not df.empty:
                    print(f"  [OK] Collected {len(df):,} observations")

                    output_file = BIS_PATH / f"bis_total_credit_{start_period}_{end_period}.csv"
                    df.to_csv(output_file, index=False)
                    print(f"  [SAVED] {output_file.relative_to(PROJECT_ROOT)}")

                    return df
                else:
                    print("  [WARN] Empty response")
                    return pd.DataFrame()

            else:
                print(f"  [ERROR] HTTP {response.status_code}")
                return pd.DataFrame()

        except Exception as e:
            print(f"  [ERROR] {str(e)[:100]}")
            return pd.DataFrame()

    def get_available_dataflows(self) -> List[Dict]:
        """
        Get list of all available BIS dataflows.

        Returns
        -------
        List[Dict]
            Available dataflows with IDs and descriptions
        """
        print("\n[INFO] Fetching available BIS dataflows...")

        try:
            url = f"{self.base_url}/dataflow"
            response = self.session.get(url, timeout=30)

            if response.status_code == 200:
                # BIS returns SDMX-ML format
                # Parse to extract dataflow IDs
                root = ET.fromstring(response.content)

                dataflows = []
                for dataflow in root.findall('.//{*}Dataflow'):
                    df_id = dataflow.get('id', '')
                    name_elem = dataflow.find('{*}Name')
                    name = name_elem.text if name_elem is not None else ''

                    if df_id:
                        dataflows.append({'id': df_id, 'name': name})

                print(f"  [OK] Found {len(dataflows)} dataflows")

                # Print first 10
                print("\n  Top 10 dataflows:")
                for df in dataflows[:10]:
                    print(f"    {df['id']}: {df['name'][:60]}")

                return dataflows

            else:
                print(f"  [ERROR] HTTP {response.status_code}")
                return []

        except Exception as e:
            print(f"  [ERROR] {str(e)[:100]}")
            return []


def main():
    """Main execution."""
    print("\n" + "="*80)
    print("BIS INTERNATIONAL BANKING STATISTICS DATA COLLECTION")
    print("="*80)

    collector = BISBankingCollector()

    # Test API
    if collector.test_api_access():
        print("\n[INFO] API test successful.")

        # Get available dataflows first
        dataflows = collector.get_available_dataflows()

        if dataflows:
            print(f"\n[INFO] Found {len(dataflows)} available datasets")

        # Try collecting some key statistics
        print("\n[INFO] Attempting to collect banking statistics...")

        # Locational Banking Statistics
        lbs_data = collector.get_locational_banking_stats("2015-Q1", "2024-Q4")

        # Consolidated Banking Statistics
        cbs_data = collector.get_consolidated_banking_stats("2015-Q1", "2024-Q4")

        # Total Credit
        credit_data = collector.get_total_credit_stats("2015-Q1", "2024-Q4")

        print("\n" + "="*80)
        print("BIS DATA COLLECTION COMPLETE")
        print("="*80)

        total_obs = 0
        datasets_collected = 0

        if not lbs_data.empty:
            total_obs += len(lbs_data)
            datasets_collected += 1
            print(f"\n  LBS observations: {len(lbs_data):,}")

        if not cbs_data.empty:
            total_obs += len(cbs_data)
            datasets_collected += 1
            print(f"  CBS observations: {len(cbs_data):,}")

        if not credit_data.empty:
            total_obs += len(credit_data)
            datasets_collected += 1
            print(f"  Credit observations: {len(credit_data):,}")

        print(f"\n  Total observations: {total_obs:,}")
        print(f"  Datasets collected: {datasets_collected}/3")

        if datasets_collected == 0:
            print("\n[WARN] No data collected - BIS API may require different query structure")
            print("[INFO] Run with --explore flag to see available dataflows")

    else:
        print("\n[ERROR] API test failed. Cannot proceed with collection.")


if __name__ == "__main__":
    main()

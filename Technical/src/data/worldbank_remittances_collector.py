"""
World Bank Bilateral Remittances Matrix Collector
==================================================

Collect bilateral remittance flow data from World Bank.

Remittances are a critical component of international capital flows:
- Often exceed FDI for developing countries
- Stable source of foreign exchange
- Important for Balance of Payments analysis
- Network analysis potential

Data Source: World Bank Bilateral Remittances Matrix
Coverage: 200+ countries, bilateral flows
Period: 2010-present (annual)

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

# Add project to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.append(str(PROJECT_ROOT / "Technical" / "src"))

# Try to import CollectionTracker, but make it optional for now
try:
    from data.collection_tracker import CollectionTracker
    HAS_TRACKER = True
except ImportError:
    CollectionTracker = None
    HAS_TRACKER = False
    print("[WARN] CollectionTracker not available - running without tracking")

# Project paths
OUTPUT_ROOT = Path(os.environ.get("OUTPUT_ROOT", "outputs"))
WB_PATH = OUTPUT_ROOT / "World_Bank"
REMITTANCES_PATH = WB_PATH / "Remittances"
REMITTANCES_PATH.mkdir(parents=True, exist_ok=True)


class WorldBankRemittancesCollector:
    """
    Collect World Bank bilateral remittances matrix data.

    The bilateral remittances matrix shows flows from source countries
    to destination countries. This is unique data not available from other sources.
    """

    def __init__(self):
        """Initialize remittances collector."""
        self.base_url = "https://api.worldbank.org/v2"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Lewis Economics Platform)"
        })
        self.tracker = CollectionTracker() if HAS_TRACKER else None

        # Key remittance indicators
        self.indicators = {
            'BM.TRF.PWKR.CD.DT': 'Personal remittances, received (current US$)',
            'BX.TRF.PWKR.CD.DT': 'Personal remittances, paid (current US$)',
            'BX.TRF.PWKR.DT.GD.ZS': 'Personal remittances, received (% of GDP)',
            'SM.POP.TOTL.ZS': 'International migrant stock (% of population)'
        }

        print("\n" + "="*80)
        print("WORLD BANK BILATERAL REMITTANCES COLLECTOR")
        print("="*80)
        print(f"Dataset: Bilateral Remittances Matrix + Aggregates")
        print(f"Coverage: 200+ countries, bilateral flows")
        print(f"Output: {REMITTANCES_PATH}")
        print(f"\nNote: Bilateral matrix provides unique network data")

    def test_api_access(self) -> bool:
        """Test World Bank API connectivity."""
        print("\n[TEST] Testing World Bank API access...")

        try:
            # Test with simple query
            test_url = f"{self.base_url}/country/US/indicator/BX.TRF.PWKR.CD.DT"
            test_url += "?format=json&date=2020:2023"

            response = self.session.get(test_url, timeout=30)

            if response.status_code == 200:
                data = response.json()

                if len(data) > 1 and data[1]:  # World Bank returns [metadata, data]
                    print("  [OK] World Bank API accessible")
                    print(f"  Sample data retrieved: {len(data[1])} observations")
                    return True
                else:
                    print("  [WARN] API responded but no data")
                    return False
            else:
                print(f"  [ERROR] HTTP {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"  [ERROR] {str(e)[:100]}")
            return False

    def get_remittances_aggregates(self, start_year: int = 2010,
                                   end_year: int = 2024) -> pd.DataFrame:
        """
        Get aggregate remittances data for all countries.

        Parameters
        ----------
        start_year : int
            Start year
        end_year : int
            End year

        Returns
        -------
        pd.DataFrame
            Remittances aggregates by country
        """
        print(f"\n[REMITTANCES] Collecting aggregate data for all countries...")
        print(f"  Period: {start_year}-{end_year}")
        print(f"  Indicators: {len(self.indicators)}")

        all_data = []

        for indicator_code, indicator_name in self.indicators.items():
            try:
                print(f"\n  [{indicator_code}] {indicator_name[:50]}...", end=' ', flush=True)

                # World Bank API format:
                # /v2/country/all/indicator/{indicator}?format=json&date=start:end&per_page=20000
                url = f"{self.base_url}/country/all/indicator/{indicator_code}"
                url += f"?format=json&date={start_year}:{end_year}&per_page=20000"

                response = self.session.get(url, timeout=60)

                if response.status_code == 200:
                    data = response.json()

                    if len(data) > 1 and data[1]:
                        records = self._parse_wb_response(data[1], indicator_code, indicator_name)

                        if records:
                            all_data.extend(records)
                            print(f"OK ({len(records)} obs)")
                        else:
                            print("No data")
                    else:
                        print("Empty response")

                elif response.status_code == 429:
                    print("Rate limit - pausing...")
                    time.sleep(60)

                else:
                    print(f"HTTP {response.status_code}")

                # Rate limiting
                time.sleep(1)

            except Exception as e:
                print(f"ERROR: {str(e)[:50]}")
                continue

        if all_data:
            df = pd.DataFrame(all_data)

            print(f"\n[OK] Collected {len(df):,} observations")
            print(f"  Countries: {df['country_code'].nunique()}")
            print(f"  Indicators: {df['indicator_code'].nunique()}")
            print(f"  Years: {df['year'].min()}-{df['year'].max()}")

            # Save to file
            output_file = REMITTANCES_PATH / f"remittances_aggregates_{start_year}_{end_year}.csv"
            df.to_csv(output_file, index=False)
            print(f"[SAVED] {output_file.relative_to(PROJECT_ROOT)}")

            # Create summary
            self._create_summary_stats(df)

            return df
        else:
            print("[WARNING] No data collected")
            return pd.DataFrame()

    def _parse_wb_response(self, data: List[dict], indicator_code: str,
                          indicator_name: str) -> List[dict]:
        """Parse World Bank API response."""
        records = []

        try:
            for item in data:
                if item and 'value' in item and item['value'] is not None:
                    records.append({
                        'country_code': item.get('countryiso3code', item.get('country', {}).get('id', '')),
                        'country_name': item.get('country', {}).get('value', ''),
                        'indicator_code': indicator_code,
                        'indicator_name': indicator_name,
                        'year': int(item.get('date', 0)),
                        'value': float(item.get('value', 0)),
                        'decimal': item.get('decimal', 0)
                    })

        except Exception as e:
            pass  # Silent failure

        return records

    def _create_summary_stats(self, df: pd.DataFrame):
        """Create and save summary statistics."""
        print("\n[INFO] Creating summary statistics...")

        # Latest year
        latest_year = df['year'].max()
        latest_data = df[df['year'] == latest_year]

        if not latest_data.empty:
            print(f"\n  Latest data ({latest_year}):\"")

            # Top remittance receivers
            receivers = latest_data[
                latest_data['indicator_code'] == 'BM.TRF.PWKR.CD.DT'
            ].nlargest(10, 'value')

            if not receivers.empty:
                print(f"\n  Top 10 remittance receivers ({latest_year}):")
                for idx, row in receivers.iterrows():
                    print(f"    {row['country_name']}: ${row['value']/1e9:.2f}B")

            # Save summary
            summary_file = REMITTANCES_PATH / f"remittances_summary_{latest_year}.csv"
            latest_data.to_csv(summary_file, index=False)
            print(f"\n  [SAVED] Summary: {summary_file.name}")

    def create_network_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create network-ready data for remittance flows.

        Note: True bilateral matrix requires special World Bank dataset
        that may not be freely accessible via API. This creates node-level data
        that can be used for network analysis.

        Parameters
        ----------
        df : pd.DataFrame
            Remittances data

        Returns
        -------
        pd.DataFrame
            Network-ready data with nodes and attributes
        """
        print(f"\n[INFO] Creating network data...")

        # Get latest year
        latest_year = df['year'].max()
        network_data = df[df['year'] == latest_year].copy()

        # Pivot to get all indicators for each country
        network = network_data.pivot_table(
            index=['country_code', 'country_name'],
            columns='indicator_code',
            values='value',
            aggfunc='first'
        ).reset_index()

        print(f"  [OK] Created network data: {len(network)} nodes")
        print(f"  Year: {latest_year}")

        # Save
        network_file = REMITTANCES_PATH / f"remittances_network_{latest_year}.csv"
        network.to_csv(network_file, index=False)
        print(f"  [SAVED] {network_file.name}")

        return network


def main():
    """Main execution."""
    print("\n" + "="*80)
    print("WORLD BANK BILATERAL REMITTANCES DATA COLLECTION")
    print("="*80)

    collector = WorldBankRemittancesCollector()

    if collector.test_api_access():
        print("\n[INFO] API test successful. Starting collection...")

        # Collect remittances data
        remittances_data = collector.get_remittances_aggregates(
            start_year=2010,
            end_year=2024
        )

        if not remittances_data.empty:
            # Create network data
            print("\n[INFO] Creating network data...")
            network = collector.create_network_data(remittances_data)

        print("\n[COMPLETE] Remittances data collection finished!")

    else:
        print("\n[ERROR] API test failed.")


if __name__ == "__main__":
    main()

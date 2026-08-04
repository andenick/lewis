"""
Eurostat Balance of Payments Collector
=======================================

Collect quarterly Balance of Payments data for EU27 countries from Eurostat.

Eurostat provides comprehensive, standardized BoP data for all EU member states:
- 27 EU countries (post-Brexit)
- Quarterly frequency (1999-present)
- Full BPM6 compliance
- No API rate limits (more lenient than OECD)

Coverage: All EU27 member states
Period: 1999-present (quarterly)
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
EUROSTAT_PATH = OUTPUT_ROOT / "Eurostat"
EUROSTAT_PATH.mkdir(parents=True, exist_ok=True)


class EurostatBoPCollector:
    """
    Collect Eurostat Balance of Payments data for EU27.

    Eurostat provides high-quality, harmonized BoP data for all EU member states
    using the BPM6 standard. Data is freely available via REST API.
    """

    def __init__(self):
        """Initialize Eurostat collector."""
        # Eurostat REST API base (JSON format)
        self.base_url = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data"
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Lewis Economics Platform)"
        })
        self.tracker = CollectionTracker() if HAS_TRACKER else None

        # EU27 member states (post-Brexit, as of 2025)
        self.countries = {
            # Founding members
            'BE': 'Belgium', 'FR': 'France', 'DE': 'Germany',
            'IT': 'Italy', 'LU': 'Luxembourg', 'NL': 'Netherlands',

            # Early joiners
            'DK': 'Denmark', 'IE': 'Ireland', 'GR': 'Greece',
            'PT': 'Portugal', 'ES': 'Spain', 'AT': 'Austria',
            'FI': 'Finland', 'SE': 'Sweden',

            # 2004 expansion
            'CY': 'Cyprus', 'CZ': 'Czech Republic', 'EE': 'Estonia',
            'HU': 'Hungary', 'LV': 'Latvia', 'LT': 'Lithuania',
            'MT': 'Malta', 'PL': 'Poland', 'SK': 'Slovakia', 'SI': 'Slovenia',

            # Later joiners
            'BG': 'Bulgaria', 'RO': 'Romania', 'HR': 'Croatia'
        }

        # Eurostat BOP dataset codes
        # Using bop_eu6_q (EU Balance of Payments - Quarterly)
        self.dataset = "bop_eu6_q"

        # Key BOP indicators (BPM6)
        self.bop_items = [
            'CA',      # Current Account
            'G',       # Goods
            'S',       # Services
            'IP',      # Primary Income
            'IS',      # Secondary Income
            'KA',      # Capital Account
            'FA',      # Financial Account
            'NFI',     # Net Financial Investment
            'DI',      # Direct Investment
            'PI',      # Portfolio Investment
            'FI',      # Financial Derivatives
            'OI',      # Other Investment
            'RA'       # Reserve Assets
        ]

        print("\n" + "="*80)
        print("EUROSTAT BALANCE OF PAYMENTS COLLECTOR")
        print("="*80)
        print(f"Countries: {len(self.countries)} EU27 member states")
        print(f"Dataset: {self.dataset} (Balance of Payments - Quarterly)")
        print(f"Frequency: Quarterly")
        print(f"Output: {EUROSTAT_PATH}")
        print(f"\nNote: Eurostat APIs are generally more permissive than OECD")

    def test_api_access(self) -> bool:
        """Test Eurostat API with a simple query."""
        print("\n[TEST] Testing Eurostat API access...")

        try:
            # Test with Germany current account, recent quarters
            # Format: dataset/freq.bop_item.unit.geo/query?parameters
            test_url = f"{self.base_url}/{self.dataset}/Q.CA.MIO_EUR.DE"
            test_url += "?startPeriod=2023-Q1&endPeriod=2024-Q4"

            response = self.session.get(test_url, timeout=30)

            if response.status_code == 200:
                data = response.json()

                # Eurostat SDMX-JSON has different structure
                if 'data' in data or 'dataSets' in data or 'value' in data:
                    print("  [OK] Eurostat API accessible")
                    print(f"  Response type: SDMX-JSON")
                    return True
                else:
                    print("  [WARN] API responded but unexpected format")
                    print(f"  Keys in response: {list(data.keys())[:5]}")
                    return False

            else:
                print(f"  [ERROR] HTTP {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"  [ERROR] {str(e)[:100]}")
            return False

    def get_country_data(self, country: str, start_year: int = 2010,
                        end_year: int = 2024) -> pd.DataFrame:
        """
        Get BoP data for a specific EU country.

        Parameters
        ----------
        country : str
            ISO 2-letter country code
        start_year : int
            Start year
        end_year : int
            End year

        Returns
        -------
        pd.DataFrame
            BoP data for country
        """
        print(f"\n[{country}] Collecting Eurostat BoP data...")

        # Check if already collected
        if self.tracker and self.tracker.is_collected('Eurostat', country, 'ALL_BOP',
                                    start_year, end_year):
            print(f"  [SKIP] Already collected")
            return pd.DataFrame()

        all_records = []

        try:
            # Collect each BOP item separately
            for bop_item in self.bop_items:
                try:
                    # Build Eurostat BoP query
                    # Format: dataset/freq.bop_item.unit.geo
                    url = f"{self.base_url}/{self.dataset}/Q.{bop_item}.MIO_EUR.{country}"
                    url += f"?startPeriod={start_year}-Q1&endPeriod={end_year}-Q4"

                    response = self.session.get(url, timeout=60)

                    if response.status_code == 200:
                        data = response.json()
                        records = self._parse_eurostat_json(data, country, bop_item, start_year, end_year)

                        if records:
                            all_records.extend(records)

                    elif response.status_code == 429:
                        print(f"  [WARN] Rate limit on {bop_item} - pausing...")
                        time.sleep(30)
                        # Retry once
                        response = self.session.get(url, timeout=60)
                        if response.status_code == 200:
                            data = response.json()
                            records = self._parse_eurostat_json(data, country, bop_item, start_year, end_year)
                            if records:
                                all_records.extend(records)

                    # Small delay to be respectful
                    time.sleep(0.5)

                except Exception as e:
                    print(f"  [WARN] Error on {bop_item}: {str(e)[:50]}")
                    continue

            if all_records:
                df = pd.DataFrame(all_records)
                print(f"  [OK] Collected {len(df):,} observations")
                print(f"      BOP items: {df['bop_item'].nunique()}")
                print(f"      Time span: {df['period'].min()} to {df['period'].max()}")

                # Record successful collection
                if self.tracker:
                    self.tracker.record_collection(
                        source='Eurostat',
                        country=country,
                        indicator='ALL_BOP',
                        start_year=start_year,
                        end_year=end_year,
                        observations=len(df),
                        file_path=str(EUROSTAT_PATH / f"eurostat_{country.lower()}.csv"),
                        success=True
                    )

                return df
            else:
                print(f"  [WARN] No data collected")

                if self.tracker:
                    self.tracker.record_collection(
                        source='Eurostat',
                        country=country,
                        indicator='ALL_BOP',
                        start_year=start_year,
                        end_year=end_year,
                        observations=0,
                        file_path="",
                        success=False,
                        error="No data in response"
                    )

                return pd.DataFrame()

        except Exception as e:
            print(f"  [ERROR] {str(e)[:100]}")

            if self.tracker:
                self.tracker.record_collection(
                    source='Eurostat',
                    country=country,
                    indicator='ALL_BOP',
                    start_year=start_year,
                    end_year=end_year,
                    observations=0,
                    file_path="",
                    success=False,
                    error=str(e)
                )

            return pd.DataFrame()

    def _parse_eurostat_json(self, data: dict, country: str, bop_item: str,
                            start_year: int, end_year: int) -> List[dict]:
        """
        Parse Eurostat SDMX-JSON response into records.

        Eurostat uses SDMX-JSON format which has structure:
        - value: dict of index -> value
        - dimension: dimension info including time periods
        """
        records = []

        try:
            # Eurostat SDMX-JSON structure
            # Check for different response formats
            if 'value' in data:
                # Format 1: Compact JSON with value dict
                values = data.get('value', {})

                # Get time dimension
                dimensions = data.get('dimension', {})
                time_dim = None

                # Find time dimension
                for dim_key, dim_data in dimensions.items():
                    if isinstance(dim_data, dict) and 'category' in dim_data:
                        if 'TIME_PERIOD' in str(dim_data) or 'time' in dim_key.lower():
                            time_dim = dim_data.get('category', {}).get('index', {})
                            break

                if time_dim:
                    # Map indices to time periods
                    time_periods = {idx: period for period, idx in time_dim.items()}

                    for idx_str, value in values.items():
                        idx = int(idx_str)
                        period = time_periods.get(idx, '')

                        if period and '-Q' in period:
                            year = int(period.split('-')[0])
                            quarter = int(period.split('-Q')[1])

                            if start_year <= year <= end_year:
                                records.append({
                                    'country': country,
                                    'country_name': self.countries.get(country, country),
                                    'bop_item': bop_item,
                                    'bop_item_name': self._get_bop_item_name(bop_item),
                                    'year': year,
                                    'quarter': quarter,
                                    'period': period,
                                    'value': float(value) if value is not None else None,
                                    'unit': 'Million EUR',
                                    'frequency': 'Quarterly'
                                })

            elif 'dataSets' in data:
                # Format 2: Full SDMX-JSON with dataSets
                datasets = data.get('dataSets', [])
                if datasets:
                    observations = datasets[0].get('observations', {})

                    # Get structure for time periods
                    structure = data.get('structure', {})
                    dimensions = structure.get('dimensions', {})

                    # Find time dimension
                    time_values = []
                    if 'observation' in dimensions:
                        for dim in dimensions['observation']:
                            if dim.get('id') == 'TIME_PERIOD':
                                time_values = [v.get('id') for v in dim.get('values', [])]
                                break

                    for obs_key, obs_value in observations.items():
                        time_idx = int(obs_key.split(':')[0])

                        if time_idx < len(time_values):
                            period = time_values[time_idx]

                            if '-Q' in period:
                                year = int(period.split('-')[0])
                                quarter = int(period.split('-Q')[1])

                                if start_year <= year <= end_year:
                                    value = obs_value[0] if isinstance(obs_value, list) else obs_value

                                    records.append({
                                        'country': country,
                                        'country_name': self.countries.get(country, country),
                                        'bop_item': bop_item,
                                        'bop_item_name': self._get_bop_item_name(bop_item),
                                        'year': year,
                                        'quarter': quarter,
                                        'period': period,
                                        'value': float(value) if value is not None else None,
                                        'unit': 'Million EUR',
                                        'frequency': 'Quarterly'
                                    })

        except Exception as e:
            pass  # Silent failure for individual parsing

        return records

    def _get_bop_item_name(self, code: str) -> str:
        """Get human-readable name for BOP item code."""
        names = {
            'CA': 'Current Account',
            'G': 'Goods',
            'S': 'Services',
            'IP': 'Primary Income',
            'IS': 'Secondary Income',
            'KA': 'Capital Account',
            'FA': 'Financial Account',
            'NFI': 'Net Financial Investment',
            'DI': 'Direct Investment',
            'PI': 'Portfolio Investment',
            'FI': 'Financial Derivatives',
            'OI': 'Other Investment',
            'RA': 'Reserve Assets'
        }
        return names.get(code, code)

    def run_batch_collection(self, batch_size: int = 5, pause_seconds: int = 10):
        """
        Run batch collection across all EU27 countries.

        Parameters
        ----------
        batch_size : int
            Number of countries per batch
        pause_seconds : int
            Seconds to pause between batches
        """
        print("\n" + "="*80)
        print("STARTING EUROSTAT EU27 BATCH COLLECTION")
        print("="*80)

        countries_list = list(self.countries.keys())
        total_countries = len(countries_list)
        total_observations = 0
        batch_num = 0

        # Process in batches
        for i in range(0, total_countries, batch_size):
            batch_num += 1
            batch_countries = countries_list[i:i+batch_size]

            print(f"\n{'='*80}")
            print(f"BATCH {batch_num}: {', '.join(batch_countries)}")
            print(f"{'='*80}")

            batch_data = []

            for country in batch_countries:
                df = self.get_country_data(country, 2010, 2024)
                if not df.empty:
                    batch_data.append(df)
                    total_observations += len(df)

            # Save batch
            if batch_data:
                batch_df = pd.concat(batch_data, ignore_index=True)
                batch_file = EUROSTAT_PATH / f"Batch_{batch_num}.csv"
                batch_df.to_csv(batch_file, index=False)
                print(f"\n  [SAVED] Batch {batch_num}: {len(batch_df):,} observations -> {batch_file.name}")

            # Pause between batches (except last)
            if i + batch_size < total_countries:
                print(f"\n  [PAUSE] Waiting {pause_seconds} seconds before next batch...")
                time.sleep(pause_seconds)

        # Combine all batches
        print(f"\n{'='*80}")
        print("COMBINING BATCHES")
        print(f"{'='*80}")

        all_files = list(EUROSTAT_PATH.glob("Batch_*.csv"))
        if all_files:
            all_data = [pd.read_csv(f) for f in all_files]
            combined = pd.concat(all_data, ignore_index=True)

            # Save combined
            combined_file = EUROSTAT_PATH / "eurostat_eu27_all_countries.csv"
            combined.to_csv(combined_file, index=False)

            print(f"\n  [COMPLETE] Total observations: {len(combined):,}")
            print(f"  [SAVED] {combined_file.name}")

            # Summary stats
            print(f"\n  Countries: {combined['country'].nunique()}")
            print(f"  BOP Items: {combined['bop_item'].nunique()}")
            print(f"  Years: {combined['year'].min()}-{combined['year'].max()}")

        print("\n" + "="*80)
        print("EUROSTAT COLLECTION COMPLETE")
        print("="*80)
        print(f"\nTotal observations collected: {total_observations:,}")


def main():
    """Main execution."""
    import sys

    collector = EurostatBoPCollector()

    # Test API
    if collector.test_api_access():
        print("\n[INFO] API test successful. Ready to collect.")

        # Check if running with --auto flag
        if '--auto' in sys.argv or not sys.stdin.isatty():
            print("\n[AUTO] Starting batch collection...")
            collector.run_batch_collection(batch_size=5, pause_seconds=15)
        else:
            # Interactive mode
            response = input("\nStart EU27 batch collection? (y/n): ")
            if response.lower() == 'y':
                collector.run_batch_collection(batch_size=5, pause_seconds=15)
    else:
        print("\n[ERROR] API test failed. Cannot proceed with collection.")


if __name__ == "__main__":
    main()

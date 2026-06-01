"""
OECD Balance of Payments Collector
===================================

Collect quarterly/monthly Balance of Payments data from OECD.

Features:
- OECD SDMX-JSON API (easier than XML)
- Balance of Payments indicators
- 38 OECD member countries
- Quarterly frequency (2000-2024)
- Intelligent collection tracking

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
OECD_PATH = OUTPUT_ROOT / "OECD"
OECD_PATH.mkdir(parents=True, exist_ok=True)


class OECDBoPCollector:
    """
    Collect OECD Balance of Payments data using SDMX-JSON API.
    """

    def __init__(self):
        """Initialize collector."""
        # OECD SDMX API base (JSON format)
        self.base_url = "https://sdmx.oecd.org/public/rest/data"
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        self.tracker = CollectionTracker() if HAS_TRACKER else None

        # OECD member countries (38)
        self.countries = {
            # G7
            'USA': 'United States', 'GBR': 'United Kingdom', 'DEU': 'Germany',
            'FRA': 'France', 'ITA': 'Italy', 'JPN': 'Japan', 'CAN': 'Canada',

            # Other advanced economies
            'AUT': 'Austria', 'BEL': 'Belgium', 'DNK': 'Denmark', 'FIN': 'Finland',
            'GRC': 'Greece', 'ISL': 'Iceland', 'IRL': 'Ireland', 'LUX': 'Luxembourg',
            'NLD': 'Netherlands', 'NOR': 'Norway', 'PRT': 'Portugal', 'ESP': 'Spain',
            'SWE': 'Sweden', 'CHE': 'Switzerland', 'AUS': 'Australia', 'NZL': 'New Zealand',

            # Emerging OECD members
            'MEX': 'Mexico', 'TUR': 'Turkey', 'POL': 'Poland', 'CZE': 'Czech Republic',
            'HUN': 'Hungary', 'KOR': 'South Korea', 'SVK': 'Slovakia', 'CHL': 'Chile',
            'SVN': 'Slovenia', 'ISR': 'Israel', 'EST': 'Estonia', 'LVA': 'Latvia',
            'LTU': 'Lithuania', 'COL': 'Colombia', 'CRI': 'Costa Rica'
        }

        # OECD Balance of Payments dataset structure
        # Using DSD_BOP@DF_BOP dataset
        # Filter: COUNTRY.MEASURE.ACCOUNTING_ENTRY.COUNTERPART.ITEM.FREQ.CURRENCY.TRANSFORMATION
        # We'll collect ALL BoP items by using empty dimensions (dots)
        self.bop_filter_template = "{country}.....Q.XDC.Y"  # Quarterly, National Currency, Level values

        print("\n" + "="*80)
        print("OECD BALANCE OF PAYMENTS COLLECTOR")
        print("="*80)
        print(f"Countries: {len(self.countries)}")
        print(f"Dataset: DSD_BOP@DF_BOP (Balance of Payments)")
        print(f"Frequency: Quarterly")
        print(f"Output: {OECD_PATH}")

    def test_api_access(self):
        """Test OECD API with a simple query."""
        print("\n[TEST] Testing OECD API access...")

        # Test with USA BoP current account quarterly
        # Structure: COUNTRY.MEASURE.ACCOUNTING_ENTRY.COUNTERPART.ITEM.FREQ.CURRENCY.TRANSFORMATION
        test_url = f"{self.base_url}/OECD.SDD.TPS,DSD_BOP@DF_BOP,1.0/USA.....Q.XDC.Y"
        test_url += "?startPeriod=2020-Q1&endPeriod=2024-Q4"

        try:
            response = self.session.get(test_url, timeout=15)

            if response.status_code == 200:
                data = response.json()

                # Check if we got data
                if 'dataSets' in data:
                    print("  [OK] OECD API accessible")
                    print(f"  Response type: SDMX-JSON")

                    # Try to parse a sample
                    dataSets = data.get('dataSets', [])
                    if dataSets and 'series' in dataSets[0]:
                        series_count = len(dataSets[0].get('series', {}))
                        print(f"  Sample data: {series_count} series found")

                    return True
                else:
                    print("  [WARN] API responded but no data structure found")
                    print(f"  Keys in response: {list(data.keys())}")
                    return False

            else:
                print(f"  [ERROR] HTTP {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"  [ERROR] {str(e)}")
            return False

    def get_country_data(self, country: str, start_year: int = 2000,
                        end_year: int = 2024) -> pd.DataFrame:
        """
        Get BoP data for a specific country.

        Parameters
        ----------
        country : str
            ISO 3-letter country code
        start_year : int
            Start year
        end_year : int
            End year

        Returns
        -------
        pd.DataFrame
            BoP data for country
        """
        print(f"\n[{country}] Collecting OECD BoP data...")

        # Check if already collected
        if self.tracker and self.tracker.is_collected('OECD', country, 'ALL_BOP',
                                    start_year, end_year):
            print(f"  [SKIP] Already collected")
            return pd.DataFrame()

        try:
            # Build OECD BoP query
            # Structure: COUNTRY.MEASURE.ACCOUNTING_ENTRY.COUNTERPART.ITEM.FREQ.CURRENCY.TRANSFORMATION
            bop_filter = self.bop_filter_template.format(country=country)
            url = f"{self.base_url}/OECD.SDD.TPS,DSD_BOP@DF_BOP,1.0/{bop_filter}"
            url += f"?startPeriod={start_year}-Q1&endPeriod={end_year}-Q4"

            print(f"  Querying: {bop_filter}")

            response = self.session.get(url, timeout=60)

            if response.status_code == 200:
                data = response.json()

                # Parse SDMX-JSON
                records = self._parse_bop_json(data, country, start_year, end_year)

                if records:
                    df = pd.DataFrame(records)
                    print(f"  [OK] Collected {len(df):,} observations")
                    print(f"      Series: {df['series_key'].nunique()}")
                    print(f"      Time span: {df['period'].min()} to {df['period'].max()}")

                    # Record successful collection
                    if self.tracker:
                        self.tracker.record_collection(
                            source='OECD',
                            country=country,
                            indicator='ALL_BOP',
                            start_year=start_year,
                            end_year=end_year,
                            observations=len(df),
                            file_path=str(OECD_PATH / f"oecd_{country.lower()}.csv"),
                            success=True
                        )

                    return df
                else:
                    print(f"  [WARN] No data in response")

                    if self.tracker:
                        self.tracker.record_collection(
                            source='OECD',
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

            else:
                print(f"  [ERROR] HTTP {response.status_code}")
                if response.text:
                    print(f"      {response.text[:150]}")

                if self.tracker:
                    self.tracker.record_collection(
                        source='OECD',
                        country=country,
                        indicator='ALL_BOP',
                        start_year=start_year,
                        end_year=end_year,
                        observations=0,
                        file_path="",
                        success=False,
                        error=f"HTTP {response.status_code}"
                    )

                return pd.DataFrame()

        except requests.exceptions.RequestException as e:
            print(f"  [ERROR] {str(e)}")

            if self.tracker:
                self.tracker.record_collection(
                    source='OECD',
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

    def _parse_bop_json(self, data: dict, country: str,
                       start_year: int, end_year: int) -> List[dict]:
        """
        Parse OECD BoP SDMX-JSON response into records.

        Parameters
        ----------
        data : dict
            JSON response from OECD API
        country : str
            Country code
        start_year : int
            Filter start year
        end_year : int
            Filter end year

        Returns
        -------
        list
            List of data records
        """
        records = []

        try:
            # SDMX-JSON structure
            dataSets = data.get('dataSets', [])

            if not dataSets:
                return records

            # Get series data
            series = dataSets[0].get('series', {})

            # Get structure for dimensions
            structure = data.get('structure', {})

            # Get dimension values for series (not observations)
            series_dimensions = structure.get('dimensions', {}).get('series', [])

            # Build dimension mappings
            dim_mappings = {}
            for dim in series_dimensions:
                dim_id = dim.get('id')
                dim_values = {i: v.get('id') for i, v in enumerate(dim.get('values', []))}
                dim_mappings[dim_id] = dim_values

            # Get observation dimensions (time)
            obs_dimensions = structure.get('dimensions', {}).get('observation', [])
            time_values = []
            for dim in obs_dimensions:
                if dim.get('id') == 'TIME_PERIOD':
                    time_values = [v.get('id') for v in dim.get('values', [])]
                    break

            # Parse each series
            for series_key, series_data in series.items():
                # Parse series key (e.g., "0:0:0:0:0:0:0:0")
                key_parts = series_key.split(':')

                # Map series dimensions
                series_info = {}
                for i, dim in enumerate(series_dimensions):
                    if i < len(key_parts):
                        dim_id = dim.get('id')
                        val_idx = int(key_parts[i])
                        if dim_id in dim_mappings and val_idx in dim_mappings[dim_id]:
                            series_info[dim_id] = dim_mappings[dim_id][val_idx]

                # Get observations
                observations = series_data.get('observations', {})

                for obs_idx, obs_value in observations.items():
                    # Get time period
                    time_idx = int(obs_idx)
                    if time_idx < len(time_values):
                        time_period = time_values[time_idx]

                        # Parse quarter (format: YYYY-Q#)
                        if '-Q' in time_period:
                            year = int(time_period.split('-')[0])
                            quarter = int(time_period.split('-Q')[1])

                            # Filter by year
                            if start_year <= year <= end_year:
                                # Get value (first element if list)
                                value = obs_value[0] if isinstance(obs_value, list) else obs_value

                                records.append({
                                    'country': country,
                                    'country_name': self.countries.get(country, country),
                                    'series_key': series_key,
                                    'measure': series_info.get('MEASURE', ''),
                                    'accounting_entry': series_info.get('ACCOUNTING_ENTRY', ''),
                                    'counterpart_area': series_info.get('COUNTERPART_AREA', ''),
                                    'bop_item': series_info.get('BOP_ITEM', ''),
                                    'year': year,
                                    'quarter': quarter,
                                    'period': time_period,
                                    'value': value,
                                    'frequency': 'Quarterly'
                                })

        except Exception as e:
            print(f"    [WARN] Parse error: {str(e)}")
            import traceback
            traceback.print_exc()

        return records

    def run_batch_collection(self, batch_size: int = 5, pause_seconds: int = 10):
        """
        Run batch collection across all countries.

        Parameters
        ----------
        batch_size : int
            Number of countries per batch
        pause_seconds : int
            Seconds to pause between batches
        """
        print("\n" + "="*80)
        print("STARTING BATCH COLLECTION")
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
                df = self.get_country_data(country, 2000, 2024)
                if not df.empty:
                    batch_data.append(df)
                    total_observations += len(df)

            # Save batch
            if batch_data:
                batch_df = pd.concat(batch_data, ignore_index=True)
                batch_file = OECD_PATH / f"Batch_{batch_num}.csv"
                batch_df.to_csv(batch_file, index=False)
                print(f"\n  [SAVED] Batch {batch_num}: {len(batch_df)} observations -> {batch_file.name}")

            # Pause between batches (except last)
            if i + batch_size < total_countries:
                print(f"\n  [PAUSE] Waiting {pause_seconds} seconds before next batch...")
                time.sleep(pause_seconds)

        # Combine all batches
        print(f"\n{'='*80}")
        print("COMBINING BATCHES")
        print(f"{'='*80}")

        all_files = list(OECD_PATH.glob("Batch_*.csv"))
        if all_files:
            all_data = [pd.read_csv(f) for f in all_files]
            combined = pd.concat(all_data, ignore_index=True)

            # Save combined
            combined_file = OECD_PATH / "oecd_all_countries.csv"
            combined.to_csv(combined_file, index=False)

            print(f"\n  [COMPLETE] Total observations: {len(combined):,}")
            print(f"  [SAVED] {combined_file.name}")

            # Summary stats
            print(f"\n  Countries: {combined['country'].nunique()}")
            print(f"  Series: {combined['series_key'].nunique()}")
            print(f"  Years: {combined['year'].min()}-{combined['year'].max()}")

        print("\n" + "="*80)
        print("COLLECTION COMPLETE")
        print("="*80)
        print(f"\nTotal observations collected: {total_observations:,}")


def main():
    """Main execution."""
    import sys

    collector = OECDBoPCollector()

    # Test API
    if collector.test_api_access():
        print("\n[INFO] API test successful. Ready to collect.")

        # Check if running with --auto flag
        if '--auto' in sys.argv or not sys.stdin.isatty():
            print("\n[AUTO] Starting batch collection...")
            collector.run_batch_collection(batch_size=5, pause_seconds=10)
        else:
            # Interactive mode
            response = input("\nStart batch collection? (y/n): ")
            if response.lower() == 'y':
                collector.run_batch_collection(batch_size=5, pause_seconds=10)
    else:
        print("\n[ERROR] API test failed. Cannot proceed with collection.")


if __name__ == "__main__":
    main()

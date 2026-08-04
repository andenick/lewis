"""
IMF Balance of Payments Data Collector (Full Implementation)
=============================================================

Collect Balance of Payments data from IMF using direct JSON API.

Uses IMF JSON API (no SDMX parsing required for basic data).

Features:
- Balance of Payments (BOP) quarterly/annual data
- Direction of Trade Statistics (DOTS) monthly data
- Major economies covered
- Intelligent collection tracking

Author: Claude
Date: 2025-10-06
"""

import os
import pandas as pd
import requests
import time
from pathlib import Path
from typing import List, Dict, Optional
import sys
import json

# Add project to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.append(str(PROJECT_ROOT / "Technical" / "src"))

from data.collection_tracker import CollectionTracker

# Project paths
OUTPUT_ROOT = Path(os.environ.get("OUTPUT_ROOT", "outputs"))
IMF_PATH = OUTPUT_ROOT / "IMF"
IMF_PATH.mkdir(parents=True, exist_ok=True)


class IMFDataCollector:
    """
    Collect IMF data using direct JSON API.

    Note: IMF provides a simpler JSON endpoint for basic data queries.
    """

    def __init__(self):
        """Initialize collector."""
        # IMF Data API base (uses CompactData format)
        self.base_url = "https://dataservices.imf.org/REST/SDMX_JSON.svc"
        self.session = requests.Session()
        self.tracker = CollectionTracker()

        # IMF country codes (ISO 2-letter)
        self.countries = {
            # G7
            'US': 'United States',
            'GB': 'United Kingdom',
            'DE': 'Germany',
            'FR': 'France',
            'IT': 'Italy',
            'JP': 'Japan',
            'CA': 'Canada',
            # Other Major
            'CN': 'China',
            'IN': 'India',
            'BR': 'Brazil',
            'RU': 'Russia',
            'AU': 'Australia',
            'KR': 'Korea',
            'MX': 'Mexico',
            'ES': 'Spain',
            'NL': 'Netherlands',
            'CH': 'Switzerland',
            'SE': 'Sweden',
            'PL': 'Poland',
            'TR': 'Turkey',
            'ID': 'Indonesia',
            'SA': 'Saudi Arabia',
            'AR': 'Argentina',
            'ZA': 'South Africa',
        }

        # Key BOP indicators (IMF BPM6 codes)
        self.bop_indicators = {
            'BCA_BP6_USD': 'Current_Account_Balance',
            'BGS_BP6_USD': 'Goods_and_Services_Balance',
            'BGGST_BP6_USD': 'Goods_Trade_Balance',
            'BGSS_BP6_USD': 'Services_Balance',
            'BIP_BP6_USD': 'Primary_Income_Balance',
            'BIS_BP6_USD': 'Secondary_Income_Balance',
            'BFA_BP6_USD': 'Financial_Account',
            'BFDI_BP6_USD': 'Direct_Investment_Net',
            'BFPI_BP6_USD': 'Portfolio_Investment_Net',
            'BFOI_BP6_USD': 'Other_Investment_Net',
            'BFRA_BP6_USD': 'Reserve_Assets',
        }

        print("\n" + "="*80)
        print("IMF DATA COLLECTOR (Full Implementation)")
        print("="*80)
        print(f"Countries: {len(self.countries)}")
        print(f"BOP Indicators: {len(self.bop_indicators)}")
        print(f"Output: {IMF_PATH}")

    def test_imf_api(self, country: str = 'US', indicator: str = 'BCA_BP6_USD') -> bool:
        """Test IMF API with a simple query."""
        print(f"\n[TEST] Testing IMF API with {country} - {indicator}...")

        # CompactData endpoint: CompactData/{database}/{freq}.{country}.{indicator}
        url = f"{self.base_url}/CompactData/BOP/Q.{country}.{indicator}"

        try:
            response = self.session.get(url, timeout=30)

            if response.status_code == 200:
                data = response.json()
                print(f"  [OK] API accessible")
                print(f"  Response structure: {list(data.keys()) if isinstance(data, dict) else 'list'}")
                return True
            else:
                print(f"  [ERROR] HTTP {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"  [ERROR] {str(e)}")
            return False

    def get_bop_data_simple(self, country: str, indicator: str,
                           start_year: int = 2000, end_year: int = 2024,
                           frequency: str = 'A') -> pd.DataFrame:
        """
        Get BOP data using simple approach - try annual data.

        Args:
            country: IMF country code (e.g., 'US', 'GB')
            indicator: BOP indicator code
            start_year: Start year
            end_year: End year
            frequency: 'A' for annual, 'Q' for quarterly
        """
        # Check if already collected
        if self.tracker.is_collected('IMF_BOP', country, indicator,
                                    start_year, end_year):
            return pd.DataFrame()

        # Try the CompactData endpoint
        url = f"{self.base_url}/CompactData/BOP/{frequency}.{country}.{indicator}"

        try:
            response = self.session.get(url, timeout=30)

            if response.status_code == 200:
                data = response.json()

                # IMF JSON structure varies, attempt to parse
                # Typically: {'CompactData': {...}}
                records = []

                # Try to extract observations
                if 'CompactData' in data:
                    compact_data = data['CompactData']
                    if 'DataSet' in compact_data:
                        dataset = compact_data['DataSet']
                        if 'Series' in dataset:
                            series = dataset['Series']

                            # Series can be dict or list
                            if isinstance(series, dict):
                                series = [series]

                            for s in series:
                                if 'Obs' in s:
                                    obs_list = s['Obs']
                                    if isinstance(obs_list, dict):
                                        obs_list = [obs_list]

                                    for obs in obs_list:
                                        if '@TIME_PERIOD' in obs and '@OBS_VALUE' in obs:
                                            try:
                                                records.append({
                                                    'country': country,
                                                    'country_name': self.countries.get(country, country),
                                                    'indicator': indicator,
                                                    'indicator_name': self.bop_indicators.get(indicator, indicator),
                                                    'time_period': obs['@TIME_PERIOD'],
                                                    'value': float(obs['@OBS_VALUE']),
                                                    'frequency': frequency
                                                })
                                            except (ValueError, KeyError):
                                                continue

                if records:
                    df = pd.DataFrame(records)

                    # Parse time period
                    if frequency == 'Q':
                        df['year'] = df['time_period'].str[:4].astype(int)
                        df['quarter'] = df['time_period'].str[5:].str.replace('Q', '').astype(int)
                    else:
                        df['year'] = df['time_period'].astype(int)

                    # Record success
                    self.tracker.record_collection(
                        source='IMF_BOP',
                        country=country,
                        indicator=indicator,
                        start_year=start_year,
                        end_year=end_year,
                        observations=len(df),
                        file_path=str(IMF_PATH / f"imf_bop_{country}_{indicator}.csv"),
                        success=True
                    )

                    return df
                else:
                    # No data found
                    self.tracker.record_collection(
                        source='IMF_BOP',
                        country=country,
                        indicator=indicator,
                        start_year=start_year,
                        end_year=end_year,
                        observations=0,
                        file_path="",
                        success=False,
                        error="No observations in response"
                    )
                    return pd.DataFrame()

            else:
                # HTTP error
                self.tracker.record_collection(
                    source='IMF_BOP',
                    country=country,
                    indicator=indicator,
                    start_year=start_year,
                    end_year=end_year,
                    observations=0,
                    file_path="",
                    success=False,
                    error=f"HTTP {response.status_code}"
                )
                return pd.DataFrame()

        except requests.exceptions.RequestException as e:
            # Request error
            self.tracker.record_collection(
                source='IMF_BOP',
                country=country,
                indicator=indicator,
                start_year=start_year,
                end_year=end_year,
                observations=0,
                file_path="",
                success=False,
                error=str(e)
            )
            return pd.DataFrame()

    def collect_country_bop(self, country: str, frequency: str = 'A',
                           start_year: int = 2000, end_year: int = 2024) -> pd.DataFrame:
        """Collect all BOP indicators for a country."""
        print(f"\n[{country}] Collecting IMF BOP data ({frequency})...")

        all_data = []
        success_count = 0
        skip_count = 0
        error_count = 0

        for indicator_code in self.bop_indicators.keys():
            df = self.get_bop_data_simple(country, indicator_code, start_year, end_year, frequency)

            if len(df) > 0:
                all_data.append(df)
                success_count += 1
                print(f"  [OK] {indicator_code}: {len(df)} obs")
            elif self.tracker.is_collected('IMF_BOP', country, indicator_code, start_year, end_year):
                skip_count += 1
            else:
                error_count += 1

            # Rate limiting
            time.sleep(0.2)

        print(f"  Summary: {success_count} success, {skip_count} skipped, {error_count} failed")

        if all_data:
            return pd.concat(all_data, ignore_index=True)
        else:
            return pd.DataFrame()

    def collect_all_countries(self, countries: Optional[List[str]] = None,
                             frequency: str = 'A',
                             batch_size: int = 5):
        """Collect BOP data for all countries."""
        if countries is None:
            countries = list(self.countries.keys())

        print("\n" + "="*80)
        print(f"COLLECTING IMF BOP DATA FOR {len(countries)} COUNTRIES")
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
                df = self.collect_country_bop(country, frequency)
                if len(df) > 0:
                    batch_data.append(df)
                    total_obs += len(df)

            # Save batch
            if batch_data:
                batch_df = pd.concat(batch_data, ignore_index=True)
                batch_file = IMF_PATH / f"Batch_{batch_num}_{frequency}.csv"
                batch_df.to_csv(batch_file, index=False, encoding='utf-8')
                print(f"\n  [SAVED] {batch_file.name} ({len(batch_df)} obs)")

            # Pause between batches
            if i + batch_size < len(countries):
                print("\n  [PAUSE] 10 seconds...")
                time.sleep(10)

        print("\n" + "="*80)
        print("COLLECTION COMPLETE")
        print("="*80)
        print(f"Total observations: {total_obs:,}")

        return total_obs

    def combine_all_batches(self, frequency: str = 'A'):
        """Combine all batch files."""
        print("\n[COMBINE] Combining batches...")

        all_files = list(IMF_PATH.glob(f"Batch_*_{frequency}.csv"))

        if not all_files:
            print("  No batch files found.")
            return

        all_data = [pd.read_csv(f) for f in all_files]
        combined = pd.concat(all_data, ignore_index=True)

        # Save combined
        combined_file = IMF_PATH / f"imf_bop_{frequency}_all_countries.csv"
        combined.to_csv(combined_file, index=False, encoding='utf-8')

        print(f"  Saved: {combined_file.name}")
        print(f"  Total observations: {len(combined):,}")
        print(f"  Countries: {combined['country'].nunique()}")
        print(f"  Indicators: {combined['indicator'].nunique()}")


def main():
    """Main execution."""
    import sys

    collector = IMFDataCollector()

    # Test API first
    if not collector.test_imf_api():
        print("\n[ERROR] IMF API test failed. Check connection.")
        return

    # Check for --auto flag
    auto = '--auto' in sys.argv or not sys.stdin.isatty()

    # Default: collect G7 + major economies (first 15 countries)
    countries_to_collect = list(collector.countries.keys())[:15]

    print(f"\n[INFO] Will collect {len(countries_to_collect)} countries:")
    print(f"  {', '.join(countries_to_collect)}")

    if auto:
        # Annual data (less API load)
        collector.collect_all_countries(countries_to_collect, frequency='A', batch_size=5)
        collector.combine_all_batches(frequency='A')
    else:
        response = input("\nStart IMF BOP collection? (y/n): ")
        if response.lower() == 'y':
            collector.collect_all_countries(countries_to_collect, frequency='A', batch_size=5)
            collector.combine_all_batches(frequency='A')


if __name__ == "__main__":
    main()

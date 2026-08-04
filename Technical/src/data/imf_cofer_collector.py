"""
IMF COFER (Currency Composition of Official Foreign Exchange Reserves) Collector
================================================================================

Collect global foreign exchange reserves composition by currency.

COFER shows how central banks allocate their FX reserves across currencies:
- USD, EUR, JPY, GBP, CNY, CAD, AUD, CHF
- Advanced economies vs Emerging markets
- World total

Note: Individual country breakdowns are CONFIDENTIAL.
Only aggregates by country group are published.

Coverage: Global aggregates
Period: 1995-present
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
IMF_PATH = OUTPUT_ROOT / "IMF"
COFER_PATH = IMF_PATH / "COFER"
COFER_PATH.mkdir(parents=True, exist_ok=True)


class IMFCOFERCollector:
    """
    Collect IMF COFER (Currency Composition of Official FX Reserves) data.

    COFER provides aggregate data on how global FX reserves are allocated
    across major currencies. Individual country data is confidential.
    """

    def __init__(self):
        """Initialize COFER collector."""
        self.base_url = "https://dataservices.imf.org/REST/SDMX_JSON.svc"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Lewis Economics Platform)',
            'Accept': 'application/json'
        })
        self.tracker = CollectionTracker() if HAS_TRACKER else None

        # Currency codes in COFER
        self.currencies = {
            'USD': 'US Dollar',
            'EUR': 'Euro',
            'JPY': 'Japanese Yen',
            'GBP': 'British Pound',
            'CNY': 'Chinese Renminbi',
            'CAD': 'Canadian Dollar',
            'AUD': 'Australian Dollar',
            'CHF': 'Swiss Franc',
            'OTHER': 'Other currencies',
            'TOTAL': 'Total allocated reserves'
        }

        # Country groups
        self.country_groups = {
            'WORLD': 'World Total',
            'ADV': 'Advanced Economies',
            'EMG': 'Emerging Markets and Developing Economies'
        }

        print("\n" + "="*80)
        print("IMF COFER DATA COLLECTOR")
        print("="*80)
        print(f"Dataset: Currency Composition of Official FX Reserves")
        print(f"Coverage: Global aggregates by currency")
        print(f"Output: {COFER_PATH}")
        print(f"\nNote: Individual country data is CONFIDENTIAL")
        print(f"      Only aggregates available (World, Advanced, Emerging)")

    def test_api_access(self) -> bool:
        """Test IMF API connectivity."""
        print("\n[TEST] Testing IMF COFER API access...")

        try:
            test_url = f"{self.base_url}/Dataflow"
            response = self.session.get(test_url, timeout=30)

            if response.status_code == 200:
                print("  [OK] IMF API accessible")
                return True
            else:
                print(f"  [ERROR] HTTP {response.status_code}")

                # Try HTTP fallback
                print("  [RETRY] Trying HTTP...")
                self.base_url = "http://dataservices.imf.org/REST/SDMX_JSON.svc"
                response = self.session.get(self.base_url + "/Dataflow", timeout=30)

                if response.status_code == 200:
                    print("  [OK] HTTP fallback successful")
                    return True
                else:
                    return False

        except requests.exceptions.RequestException as e:
            print(f"  [ERROR] {str(e)[:100]}")
            return False

    def get_cofer_data(self, start_year: int = 2010, end_year: int = None) -> pd.DataFrame:
        """
        Get COFER currency composition data.

        Parameters
        ----------
        start_year : int
            Start year (COFER available from 1995)
        end_year : int, optional
            End year

        Returns
        -------
        pd.DataFrame
            COFER data showing FX reserves by currency and country group
        """
        if end_year is None:
            end_year = datetime.now().year

        print(f"\n[COFER] Collecting FX reserves currency composition...")
        print(f"  Period: {start_year}-{end_year}")
        print(f"  Frequency: Quarterly")

        all_data = []

        # Collect for each country group
        for group_code, group_name in self.country_groups.items():
            try:
                print(f"\n  [{group_code}] {group_name}...", end=' ', flush=True)

                # Build COFER query
                # Format: CompactData/COFER/{frequency}.{country_group}.{currency}
                # Q = Quarterly
                url = f"{self.base_url}/CompactData/COFER/Q.{group_code}"

                response = self.session.get(url, timeout=60)

                if response.status_code == 200:
                    data = response.json()
                    records = self._parse_cofer_response(data, group_code, group_name, start_year, end_year)

                    if records:
                        all_data.extend(records)
                        print(f"OK ({len(records)} obs)")
                    else:
                        print("No data")

                elif response.status_code == 429:
                    print("Rate limit - pausing...")
                    time.sleep(60)

                else:
                    print(f"HTTP {response.status_code}")

                time.sleep(2)  # Rate limiting

            except Exception as e:
                print(f"ERROR: {str(e)[:50]}")
                continue

        if all_data:
            df = pd.DataFrame(all_data)

            print(f"\n[OK] Collected {len(df):,} observations")
            print(f"  Country Groups: {df['country_group'].nunique()}")
            print(f"  Currencies: {df['currency'].nunique()}")
            print(f"  Period: {df['period'].min()} to {df['period'].max()}")

            # Save to file
            output_file = COFER_PATH / f"cofer_reserves_{start_year}_{end_year}.csv"
            df.to_csv(output_file, index=False)
            print(f"[SAVED] {output_file.relative_to(PROJECT_ROOT)}")

            # Create summary stats
            self._create_summary_stats(df)

            return df
        else:
            print("[WARNING] No data collected")
            return pd.DataFrame()

    def _parse_cofer_response(self, data: dict, group_code: str, group_name: str,
                             start_year: int, end_year: int) -> List[dict]:
        """Parse IMF COFER JSON response."""
        records = []

        try:
            compact_data = data.get('CompactData', {})
            dataset = compact_data.get('DataSet', {})

            if 'Series' in dataset:
                series = dataset['Series']
                if not isinstance(series, list):
                    series = [series]

                for series_item in series:
                    # Get currency dimension
                    currency = series_item.get('@CURRENCY', 'UNKNOWN')
                    indicator = series_item.get('@INDICATOR', '')

                    # Get observations
                    obs = series_item.get('Obs', [])
                    if not isinstance(obs, list):
                        obs = [obs]

                    for observation in obs:
                        period = observation.get('@TIME_PERIOD', '')
                        value_str = observation.get('@OBS_VALUE', '')

                        if period and value_str:
                            # Parse quarter (format: 2024-Q3)
                            if '-Q' in period:
                                year = int(period.split('-')[0])
                                quarter = int(period.split('-Q')[1])

                                if start_year <= year <= end_year:
                                    try:
                                        value = float(value_str)
                                    except (ValueError, TypeError):
                                        value = None

                                    records.append({
                                        'country_group': group_code,
                                        'country_group_name': group_name,
                                        'currency': currency,
                                        'currency_name': self.currencies.get(currency, currency),
                                        'indicator': indicator,
                                        'year': year,
                                        'quarter': quarter,
                                        'period': period,
                                        'value': value,
                                        'unit': 'USD_Millions'
                                    })

        except Exception as e:
            pass  # Silent failure

        return records

    def _create_summary_stats(self, df: pd.DataFrame):
        """Create and save summary statistics."""
        print("\n[INFO] Creating summary statistics...")

        # Latest quarter
        latest_period = df['period'].max()
        latest_data = df[df['period'] == latest_period]

        if not latest_data.empty:
            print(f"\n  Latest data ({latest_period}):")

            # Show currency shares for world total
            world_latest = latest_data[latest_data['country_group'] == 'WORLD']

            if not world_latest.empty:
                # Calculate shares
                total_reserves = world_latest[world_latest['currency'] == 'TOTAL']['value'].sum()

                if total_reserves > 0:
                    print(f"  Total allocated reserves: ${total_reserves:,.0f}M")
                    print(f"\n  Currency shares:")

                    for currency in ['USD', 'EUR', 'JPY', 'GBP', 'CNY', 'CAD', 'AUD', 'CHF']:
                        currency_data = world_latest[world_latest['currency'] == currency]
                        if not currency_data.empty:
                            amount = currency_data['value'].sum()
                            share = (amount / total_reserves) * 100
                            print(f"    {currency}: {share:5.2f}% (${amount:,.0f}M)")

            # Save summary
            summary_file = COFER_PATH / f"cofer_summary_{latest_period.replace('-', '_')}.csv"
            latest_data.to_csv(summary_file, index=False)
            print(f"\n  [SAVED] Summary: {summary_file.name}")

    def analyze_currency_trends(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze currency share trends over time.

        Parameters
        ----------
        df : pd.DataFrame
            COFER data

        Returns
        -------
        pd.DataFrame
            Time series of currency shares
        """
        # Focus on world total
        world_data = df[df['country_group'] == 'WORLD'].copy()

        if world_data.empty:
            return pd.DataFrame()

        # Pivot to get shares over time
        shares = []

        for period in sorted(world_data['period'].unique()):
            period_data = world_data[world_data['period'] == period]

            total = period_data[period_data['currency'] == 'TOTAL']['value'].sum()

            if total > 0:
                record = {'period': period}

                for currency in ['USD', 'EUR', 'JPY', 'GBP', 'CNY']:
                    currency_val = period_data[period_data['currency'] == currency]['value'].sum()
                    record[f'{currency}_share'] = (currency_val / total) * 100

                shares.append(record)

        if shares:
            shares_df = pd.DataFrame(shares)
            print(f"\n[OK] Calculated currency shares over {len(shares)} periods")

            # Save
            shares_file = COFER_PATH / "cofer_currency_shares_timeseries.csv"
            shares_df.to_csv(shares_file, index=False)
            print(f"[SAVED] {shares_file.relative_to(PROJECT_ROOT)}")

            return shares_df
        else:
            return pd.DataFrame()


def main():
    """Main execution."""
    print("\n" + "="*80)
    print("IMF COFER FX RESERVES CURRENCY COMPOSITION DATA COLLECTION")
    print("="*80)

    collector = IMFCOFERCollector()

    if collector.test_api_access():
        print("\n[INFO] API test successful. Starting collection...")

        # Collect COFER data (2010-2024)
        cofer_data = collector.get_cofer_data(
            start_year=2010,
            end_year=2024
        )

        if not cofer_data.empty:
            # Analyze trends
            print("\n[INFO] Analyzing currency trends...")
            shares = collector.analyze_currency_trends(cofer_data)

        print("\n[COMPLETE] COFER data collection finished!")

    else:
        print("\n[ERROR] API test failed.")


if __name__ == "__main__":
    main()

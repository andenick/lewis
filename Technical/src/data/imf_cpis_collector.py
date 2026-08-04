"""
IMF CPIS (Coordinated Portfolio Investment Survey) Data Collector
=================================================================

Collect bilateral portfolio investment position data from IMF.

The CPIS provides bilateral portfolio holdings by country pair:
- Portfolio equity holdings by issuer country
- Debt securities holdings by issuer country
- Breakdown by sector (banks, non-banks, general government)

Coverage: 70+ reporting countries, annual (some semi-annual)
Period: 2001-present

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
CPIS_PATH = IMF_PATH / "CPIS"
CPIS_PATH.mkdir(parents=True, exist_ok=True)


class IMFCPISCollector:
    """
    Collect IMF CPIS (Coordinated Portfolio Investment Survey) data.

    CPIS provides bilateral portfolio investment positions showing
    which countries hold securities issued by which countries.
    """

    def __init__(self):
        """Initialize CPIS collector."""
        # Use HTTPS for IMF Data Services
        self.base_url = "https://dataservices.imf.org/REST/SDMX_JSON.svc"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Lewis Economics Platform)',
            'Accept': 'application/json'
        })
        self.tracker = CollectionTracker() if HAS_TRACKER else None

        # Key CPIS indicators
        self.indicators = {
            'PORTFOLIO_TOTAL': 'Total Portfolio Investment',
            'EQUITY': 'Portfolio Equity',
            'DEBT': 'Debt Securities',
            'DEBT_LT': 'Long-term Debt Securities',
            'DEBT_ST': 'Short-term Debt Securities'
        }

        print("\n" + "="*80)
        print("IMF CPIS DATA COLLECTOR")
        print("="*80)
        print(f"Dataset: Coordinated Portfolio Investment Survey")
        print(f"Coverage: Bilateral portfolio holdings")
        print(f"Output: {CPIS_PATH}")

    def test_api_access(self) -> bool:
        """Test IMF API connectivity."""
        print("\n[TEST] Testing IMF CPIS API access...")

        try:
            # Test with dataflow query
            test_url = f"{self.base_url}/Dataflow"

            response = self.session.get(test_url, timeout=30)

            if response.status_code == 200:
                print("  [OK] IMF API accessible")
                print(f"  Base URL: {self.base_url}")
                return True
            else:
                print(f"  [ERROR] HTTP {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"  [ERROR] Connection failed: {str(e)}")
            print(f"  Note: Try using HTTP instead of HTTPS if firewall blocks port 443")
            return False

    def get_cpis_data(self, start_year: int = 2010, end_year: int = None,
                     sample_countries: bool = True) -> pd.DataFrame:
        """
        Get CPIS bilateral portfolio investment data.

        Parameters
        ----------
        start_year : int
            Start year (CPIS available from 2001)
        end_year : int, optional
            End year (defaults to current year)
        sample_countries : bool
            If True, collects major economies only (faster)
            If False, attempts all reporters (slower, may hit rate limits)

        Returns
        -------
        pd.DataFrame
            CPIS data with bilateral portfolio positions
        """
        if end_year is None:
            end_year = datetime.now().year

        print(f"\n[CPIS] Collecting bilateral portfolio investment data...")
        print(f"  Period: {start_year}-{end_year}")
        print(f"  Mode: {'Sample (major economies)' if sample_countries else 'Full coverage'}")

        # Major portfolio investors/issuers
        if sample_countries:
            countries = [
                'US', 'GB', 'DE', 'FR', 'IT', 'JP', 'CA',  # G7
                'CN', 'AU', 'KR', 'BR', 'IN',  # Major EM
                'NL', 'CH', 'SE', 'ES', 'BE', 'IE', 'LU'  # European financial centers
            ]
        else:
            countries = self._get_cpis_reporters()

        print(f"  Reporters: {len(countries)} countries")

        all_data = []

        for i, country in enumerate(countries, 1):
            try:
                print(f"  [{i}/{len(countries)}] Fetching {country}...", end=' ', flush=True)

                # Build CPIS query
                # Format: CompactData/CPIS/{frequency}.{reporter}.{counterpart}.{asset}
                # A = Annual, W00 = World total, EA = Equity+Debt
                url = f"{self.base_url}/CompactData/CPIS/A.{country}.W00.EA"

                response = self.session.get(url, timeout=60)

                if response.status_code == 200:
                    data = response.json()
                    records = self._parse_cpis_response(data, country, start_year, end_year)

                    if records:
                        all_data.extend(records)
                        print(f"OK ({len(records)} obs)")
                    else:
                        print("No data")

                elif response.status_code == 429:
                    print("Rate limit")
                    print("\n  [PAUSE] Rate limit hit, waiting 60 seconds...")
                    time.sleep(60)
                    # Retry
                    response = self.session.get(url, timeout=60)
                    if response.status_code == 200:
                        data = response.json()
                        records = self._parse_cpis_response(data, country, start_year, end_year)
                        if records:
                            all_data.extend(records)
                            print(f"  [RETRY OK] {len(records)} observations")

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
            print(f"  Reporters: {df['reporter'].nunique()}")
            print(f"  Years: {df['year'].min()}-{df['year'].max()}")

            # Save to file
            output_file = CPIS_PATH / f"cpis_bilateral_{start_year}_{end_year}.csv"
            df.to_csv(output_file, index=False)
            print(f"[SAVED] {output_file.relative_to(PROJECT_ROOT)}")

            return df
        else:
            print("[WARNING] No data collected")
            return pd.DataFrame()

    def _parse_cpis_response(self, data: dict, reporter: str,
                            start_year: int, end_year: int) -> List[dict]:
        """Parse IMF CPIS JSON response."""
        records = []

        try:
            compact_data = data.get('CompactData', {})
            dataset = compact_data.get('DataSet', {})

            if 'Series' in dataset:
                series = dataset['Series']
                if not isinstance(series, list):
                    series = [series]

                for series_item in series:
                    # Get dimensions
                    indicator = series_item.get('@INDICATOR', '')
                    counterpart = series_item.get('@COUNTERPART_AREA', '')

                    # Get observations
                    obs = series_item.get('Obs', [])
                    if not isinstance(obs, list):
                        obs = [obs]

                    for observation in obs:
                        year_str = observation.get('@TIME_PERIOD', '')
                        value_str = observation.get('@OBS_VALUE', '')

                        if year_str and value_str:
                            year = int(year_str)

                            if start_year <= year <= end_year:
                                try:
                                    value = float(value_str)
                                except (ValueError, TypeError):
                                    value = None

                                records.append({
                                    'reporter': reporter,
                                    'counterpart': counterpart,
                                    'indicator': indicator,
                                    'year': year,
                                    'value': value,
                                    'unit': 'USD_Millions'
                                })

        except Exception as e:
            print(f"\n    [WARN] Parse error for {reporter}: {str(e)[:50]}")

        return records

    def _get_cpis_reporters(self) -> List[str]:
        """Get list of CPIS reporting countries."""
        # CPIS major reporters (70+ countries participate)
        return [
            # G7
            'US', 'GB', 'DE', 'FR', 'IT', 'JP', 'CA',
            # Other advanced
            'AU', 'AT', 'BE', 'DK', 'FI', 'IE', 'LU', 'NL', 'NO', 'SE', 'CH', 'ES', 'PT', 'GR',
            # Asia
            'CN', 'HK', 'SG', 'KR', 'TW', 'IN', 'TH', 'MY', 'ID', 'PH',
            # Americas
            'BR', 'MX', 'AR', 'CL', 'CO',
            # Middle East
            'SA', 'AE', 'IL',
            # Eastern Europe
            'PL', 'CZ', 'HU', 'RO',
            # Africa
            'ZA', 'EG', 'NG'
        ]

    def create_bilateral_matrix(self, df: pd.DataFrame, year: int,
                               indicator: str = 'PORTFOLIO_TOTAL') -> pd.DataFrame:
        """
        Create bilateral portfolio holdings matrix for a specific year.

        Parameters
        ----------
        df : pd.DataFrame
            CPIS data
        year : int
            Year to create matrix for
        indicator : str
            Which portfolio component

        Returns
        -------
        pd.DataFrame
            Matrix with reporters as rows, counterparts as columns
        """
        # Filter data
        year_data = df[(df['year'] == year) & (df['indicator'].str.contains(indicator, na=False))]

        if year_data.empty:
            print(f"[WARN] No data for {year}, {indicator}")
            return pd.DataFrame()

        # Pivot to matrix
        matrix = year_data.pivot_table(
            index='reporter',
            columns='counterpart',
            values='value',
            aggfunc='sum'
        )

        print(f"[OK] Created bilateral matrix: {matrix.shape[0]} reporters x {matrix.shape[1]} counterparts")

        return matrix


def main():
    """Main execution."""
    print("\n" + "="*80)
    print("IMF CPIS BILATERAL PORTFOLIO INVESTMENT DATA COLLECTION")
    print("="*80)

    collector = IMFCPISCollector()

    # Test API
    if collector.test_api_access():
        print("\n[INFO] API test successful. Starting collection...")

        # Collect CPIS data (2010-2024, major economies)
        cpis_data = collector.get_cpis_data(
            start_year=2010,
            end_year=2024,
            sample_countries=True  # Start with major economies
        )

        if not cpis_data.empty:
            # Create sample bilateral matrix for latest year
            latest_year = cpis_data['year'].max()
            print(f"\n[INFO] Creating bilateral matrix for {latest_year}...")

            matrix = collector.create_bilateral_matrix(cpis_data, latest_year)

            if not matrix.empty:
                matrix_file = CPIS_PATH / f"cpis_bilateral_matrix_{latest_year}.csv"
                matrix.to_csv(matrix_file)
                print(f"[SAVED] {matrix_file.relative_to(PROJECT_ROOT)}")

        print("\n[COMPLETE] CPIS data collection finished!")

    else:
        print("\n[ERROR] API test failed. Check network connectivity.")
        print("[TIP] If firewall blocks HTTPS (port 443), may need to use HTTP (port 80)")


if __name__ == "__main__":
    main()

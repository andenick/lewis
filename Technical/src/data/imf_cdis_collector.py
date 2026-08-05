"""
IMF CDIS (Coordinated Direct Investment Survey) Data Collector
===============================================================

Collect bilateral FDI position data from IMF.

The CDIS provides bilateral direct investment positions:
- Inward FDI positions by investor country
- Outward FDI positions by destination country
- Represents holdings with >=10% voting power

Coverage: 100+ reporting countries, annual
Period: 2009-present

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
CDIS_PATH = IMF_PATH / "CDIS"
CDIS_PATH.mkdir(parents=True, exist_ok=True)


class IMFCDISCollector:
    """
    Collect IMF CDIS (Coordinated Direct Investment Survey) data.

    CDIS provides bilateral FDI positions showing which countries
    have direct investments in which countries.
    """

    def __init__(self):
        """Initialize CDIS collector."""
        self.base_url = "https://dataservices.imf.org/REST/SDMX_JSON.svc"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Lewis Economics Platform)',
            'Accept': 'application/json'
        })
        self.tracker = CollectionTracker() if HAS_TRACKER else None

        # CDIS indicators
        self.indicators = {
            'INWARD': 'Inward Direct Investment Position',
            'OUTWARD': 'Outward Direct Investment Position'
        }

        print("\n" + "="*80)
        print("IMF CDIS DATA COLLECTOR")
        print("="*80)
        print(f"Dataset: Coordinated Direct Investment Survey")
        print(f"Coverage: Bilateral FDI positions")
        print(f"Output: {CDIS_PATH}")

    def test_api_access(self) -> bool:
        """Test IMF API connectivity."""
        print("\n[TEST] Testing IMF CDIS API access...")

        try:
            test_url = f"{self.base_url}/Dataflow"
            response = self.session.get(test_url, timeout=30)

            if response.status_code == 200:
                print("  [OK] IMF API accessible (HTTPS)")
                return True
            else:
                print(f"  [ERROR] HTTP {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"  [ERROR] Connection failed: {str(e)}")

            # Try HTTP fallback
            print("\n  [RETRY] Trying HTTP instead of HTTPS...")
            self.base_url = "http://dataservices.imf.org/REST/SDMX_JSON.svc"

            try:
                test_url = f"{self.base_url}/Dataflow"
                response = self.session.get(test_url, timeout=30)

                if response.status_code == 200:
                    print("  [OK] IMF API accessible (HTTP fallback)")
                    return True
                else:
                    print(f"  [ERROR] HTTP fallback also failed")
                    return False

            except requests.exceptions.RequestException as e2:
                print(f"  [ERROR] HTTP fallback failed: {str(e2)}")
                return False

    def get_cdis_data(self, start_year: int = 2015, end_year: int = None,
                     sample_countries: bool = True, direction: str = 'INWARD') -> pd.DataFrame:
        """
        Get CDIS bilateral FDI position data.

        Parameters
        ----------
        start_year : int
            Start year (CDIS available from 2009)
        end_year : int, optional
            End year
        sample_countries : bool
            If True, major economies only
        direction : str
            'INWARD' or 'OUTWARD' FDI positions

        Returns
        -------
        pd.DataFrame
            CDIS bilateral FDI data
        """
        if end_year is None:
            end_year = datetime.now().year

        print(f"\n[CDIS] Collecting bilateral FDI positions...")
        print(f"  Direction: {direction}")
        print(f"  Period: {start_year}-{end_year}")
        print(f"  Mode: {'Sample' if sample_countries else 'Full coverage'}")

        # Major FDI source/destination countries
        if sample_countries:
            countries = [
                'US', 'GB', 'DE', 'FR', 'IT', 'JP', 'CA',  # G7
                'CN', 'NL', 'CH', 'IE', 'LU', 'SG', 'HK',  # Major FDI hubs
                'BR', 'IN', 'AU', 'KR', 'MX', 'ES'  # Large emerging/advanced
            ]
        else:
            countries = self._get_cdis_reporters()

        print(f"  Reporters: {len(countries)} countries")

        all_data = []

        for i, country in enumerate(countries, 1):
            try:
                print(f"  [{i}/{len(countries)}] Fetching {country} {direction.lower()}...", end=' ', flush=True)

                # Build CDIS query
                # Format: CompactData/CDIS/{frequency}.{reporter}.{counterpart}.{direction}
                # A = Annual
                # IWD = Inward Direct Investment, OWD = Outward
                direction_code = 'IWD' if direction == 'INWARD' else 'OWD'
                url = f"{self.base_url}/CompactData/CDIS/A.{country}.W00.{direction_code}"

                response = self.session.get(url, timeout=60)

                if response.status_code == 200:
                    data = response.json()
                    records = self._parse_cdis_response(data, country, direction, start_year, end_year)

                    if records:
                        all_data.extend(records)
                        print(f"OK ({len(records)} obs)")
                    else:
                        print("No data")

                elif response.status_code == 429:
                    print("Rate limit - pausing...")
                    time.sleep(60)

                elif response.status_code == 404:
                    print("Not available")

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
            print(f"  Counterparts: {df['counterpart'].nunique() if 'counterpart' in df else 'N/A'}")
            print(f"  Years: {df['year'].min()}-{df['year'].max()}")

            # Save to file
            output_file = CDIS_PATH / f"cdis_{direction.lower()}_{start_year}_{end_year}.csv"
            df.to_csv(output_file, index=False)
            print(f"[SAVED] {output_file.relative_to(PROJECT_ROOT)}")

            return df
        else:
            print("[WARNING] No data collected")
            return pd.DataFrame()

    def _parse_cdis_response(self, data: dict, reporter: str, direction: str,
                            start_year: int, end_year: int) -> List[dict]:
        """Parse IMF CDIS JSON response."""
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
                    counterpart = series_item.get('@COUNTERPART_AREA', '')
                    indicator = series_item.get('@INDICATOR', '')

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
                                    'direction': direction,
                                    'indicator': indicator,
                                    'year': year,
                                    'value': value,
                                    'unit': 'USD_Millions'
                                })

        except Exception as e:
            pass  # Silent failure for individual series

        return records

    def _get_cdis_reporters(self) -> List[str]:
        """Get list of CDIS reporting countries (100+)."""
        return [
            # G7
            'US', 'GB', 'DE', 'FR', 'IT', 'JP', 'CA',
            # Other advanced
            'AU', 'AT', 'BE', 'DK', 'FI', 'IE', 'LU', 'NL', 'NO', 'SE', 'CH', 'ES', 'PT', 'GR', 'NZ',
            # FDI hubs
            'HK', 'SG', 'CY', 'MT', 'BM', 'KY', 'VG',
            # Asia
            'CN', 'KR', 'TW', 'IN', 'TH', 'MY', 'ID', 'PH', 'VN',
            # Americas
            'BR', 'MX', 'AR', 'CL', 'CO', 'PE',
            # Middle East
            'SA', 'AE', 'IL', 'QA',
            # Eastern Europe
            'PL', 'CZ', 'HU', 'RO', 'BG',
            # Africa
            'ZA', 'EG', 'NG', 'KE', 'MA'
        ]

    def create_bilateral_matrix(self, df: pd.DataFrame, year: int,
                               direction: str = 'INWARD') -> pd.DataFrame:
        """
        Create bilateral FDI position matrix for a specific year.

        Parameters
        ----------
        df : pd.DataFrame
            CDIS data
        year : int
            Year
        direction : str
            'INWARD' or 'OUTWARD'

        Returns
        -------
        pd.DataFrame
            Bilateral FDI matrix
        """
        year_data = df[(df['year'] == year) & (df['direction'] == direction)]

        if year_data.empty:
            print(f"[WARN] No data for {year}, {direction}")
            return pd.DataFrame()

        # Pivot to matrix
        matrix = year_data.pivot_table(
            index='reporter',
            columns='counterpart',
            values='value',
            aggfunc='sum'
        )

        print(f"[OK] Created bilateral FDI matrix: {matrix.shape[0]} reporters x {matrix.shape[1]} counterparts")

        return matrix


def main():
    """Main execution."""
    print("\n" + "="*80)
    print("IMF CDIS BILATERAL FDI DATA COLLECTION")
    print("="*80)

    collector = IMFCDISCollector()

    if collector.test_api_access():
        print("\n[INFO] API test successful. Starting collection...")

        # Collect inward FDI positions
        inward_data = collector.get_cdis_data(
            start_year=2015,
            end_year=2024,
            sample_countries=True,
            direction='INWARD'
        )

        # Collect outward FDI positions
        outward_data = collector.get_cdis_data(
            start_year=2015,
            end_year=2024,
            sample_countries=True,
            direction='OUTWARD'
        )

        print("\n[COMPLETE] CDIS data collection finished!")

    else:
        print("\n[ERROR] API test failed.")
        print("[NOTE] IMF API may be blocked by firewall.")
        print("[TIP] Try running from different network or using VPN.")


if __name__ == "__main__":
    main()

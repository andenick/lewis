"""
Banco de México (Banxico) Data Collector
=========================================

Collects Mexican economic data from Banco de México SIE API.

Data Sources:
- Balance of Payments
- Trade Statistics
- Exchange Rates
- Economic Indicators

Requires API token (free registration).

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

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
OUTPUT_ROOT = Path(os.environ.get("OUTPUT_ROOT", "outputs"))
BANXICO_PATH = OUTPUT_ROOT / "Banco_de_Mexico"


class BanxicoDataCollector:
    """
    Collect data from Banco de México SIE API.

    Sistema de Información Económica (SIE) provides 190,000+ time series.
    """

    def __init__(self, api_token: str):
        """
        Initialize Banxico data collector.

        Parameters
        ----------
        api_token : str
            Banxico SIE API token
        """
        self.api_token = api_token
        self.base_url = "https://www.banxico.org.mx/SieAPIRest/service/v1/series"
        self.session = requests.Session()
        self.session.headers.update({'Bmx-Token': api_token})

        # Set up output directories
        self.bop_path = BANXICO_PATH / "Balance_of_Payments"
        self.trade_path = BANXICO_PATH / "Trade"
        self.fx_path = BANXICO_PATH / "Exchange_Rates"

        for path in [self.bop_path, self.trade_path, self.fx_path]:
            path.mkdir(parents=True, exist_ok=True)

        print("\n" + "="*80)
        print("Banco de Mexico (Banxico) Data Collector Initialized")
        print("="*80)
        print(f"Output directory: {BANXICO_PATH.relative_to(PROJECT_ROOT)}")

    def get_series(self, series_ids: List[str],
                   start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Get time series data from Banxico.

        Parameters
        ----------
        series_ids : list of str
            Banxico series IDs (e.g., 'SF43718' for current account)
        start_date : str, optional
            Start date in YYYY-MM-DD format
        end_date : str, optional
            End date in YYYY-MM-DD format

        Returns
        -------
        pd.DataFrame
            Time series data
        """
        if start_date is None:
            start_date = "2000-01-01"
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")

        # Build URL - can request multiple series at once
        series_str = ','.join(series_ids)
        url = f"{self.base_url}/{series_str}/datos/{start_date}/{end_date}"

        try:
            print(f"  Fetching {len(series_ids)} series from Banxico...", end=' ')
            response = self.session.get(url, timeout=60)

            if response.status_code == 200:
                data = response.json()

                all_data = []

                # Parse response
                if 'bmx' in data and 'series' in data['bmx']:
                    for series in data['bmx']['series']:
                        series_id = series.get('idSerie', '')
                        series_title = series.get('titulo', '')

                        if 'datos' in series:
                            for obs in series['datos']:
                                date_str = obs.get('fecha', '')
                                value_str = obs.get('dato', '')

                                # Parse value (may contain commas)
                                try:
                                    value = float(value_str.replace(',', ''))
                                except:
                                    continue

                                all_data.append({
                                    'series_id': series_id,
                                    'series_title': series_title,
                                    'date': pd.to_datetime(date_str, format='%d/%m/%Y'),
                                    'value': value
                                })

                if all_data:
                    df = pd.DataFrame(all_data)
                    print(f"OK ({len(df):,} observations)")
                    return df
                else:
                    print("No data")
                    return pd.DataFrame()
            else:
                print(f"Error {response.status_code}")
                return pd.DataFrame()

        except Exception as e:
            print(f"ERROR: {e}")
            return pd.DataFrame()

    def get_balance_of_payments(self, start_year: int = 2000,
                                end_year: int = None) -> pd.DataFrame:
        """
        Get Mexico Balance of Payments data.

        Parameters
        ----------
        start_year : int, default 2000
            Start year
        end_year : int, optional
            End year

        Returns
        -------
        pd.DataFrame
            Balance of Payments data
        """
        if end_year is None:
            end_year = datetime.now().year

        print(f"\n[Banxico BOP] Collecting Balance of Payments...")
        print(f"  Period: {start_year}-{end_year}")

        # Key BoP series from Banxico
        # Series IDs from Banxico SIE catalog
        bop_series = {
            'SF43718': 'Current_Account',
            'SF43739': 'Goods_Trade_Balance',
            'SF43742': 'Services_Balance',
            'SF46410': 'Financial_Account',
            'SF46426': 'Direct_Investment',
            'SF46425': 'Portfolio_Investment',
        }

        start_date = f"{start_year}-01-01"
        end_date = f"{end_year}-12-31"

        # Get all series
        df = self.get_series(list(bop_series.keys()), start_date, end_date)

        if not df.empty:
            # Add readable names
            df['indicator_name'] = df['series_id'].map(bop_series)

            # Extract year and quarter
            df['year'] = df['date'].dt.year
            df['quarter'] = df['date'].dt.quarter

            # Save
            output_file = self.bop_path / f"banxico_bop_{start_year}_{end_year}.csv"
            df.to_csv(output_file, index=False)
            print(f"[SAVED] {output_file.relative_to(PROJECT_ROOT)}")

            # Summary
            print(f"\nSummary:")
            print(f"  Total observations: {len(df):,}")
            print(f"  Series: {df['series_id'].nunique()}")
            print(f"  Date range: {df['date'].min().date()} to {df['date'].max().date()}")

            return df
        else:
            print("[WARNING] No data collected")
            return pd.DataFrame()

    def get_trade_data(self, start_year: int = 2000,
                      end_year: int = None) -> pd.DataFrame:
        """
        Get Mexico trade statistics.

        Parameters
        ----------
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

        print(f"\n[Banxico Trade] Collecting trade statistics...")
        print(f"  Period: {start_year}-{end_year}")

        # Key trade series
        trade_series = {
            'SF43694': 'Total_Exports',
            'SF43695': 'Total_Imports',
            'SF43739': 'Trade_Balance',
        }

        start_date = f"{start_year}-01-01"
        end_date = f"{end_year}-12-31"

        df = self.get_series(list(trade_series.keys()), start_date, end_date)

        if not df.empty:
            df['indicator_name'] = df['series_id'].map(trade_series)
            df['year'] = df['date'].dt.year

            output_file = self.trade_path / f"banxico_trade_{start_year}_{end_year}.csv"
            df.to_csv(output_file, index=False)
            print(f"[SAVED] {output_file.relative_to(PROJECT_ROOT)}")

            print(f"\nSummary:")
            print(f"  Total observations: {len(df):,}")
            print(f"  Date range: {df['date'].min().date()} to {df['date'].max().date()}")

            return df
        else:
            print("[WARNING] No data collected")
            return pd.DataFrame()

    def get_exchange_rates(self, start_year: int = 2000,
                          end_year: int = None) -> pd.DataFrame:
        """
        Get exchange rate data.

        Parameters
        ----------
        start_year : int, default 2000
            Start year
        end_year : int, optional
            End year

        Returns
        -------
        pd.DataFrame
            Exchange rate data
        """
        if end_year is None:
            end_year = datetime.now().year

        print(f"\n[Banxico FX] Collecting exchange rates...")
        print(f"  Period: {start_year}-{end_year}")

        # Key exchange rate series
        fx_series = {
            'SF43718': 'USD_MXN_Rate',
        }

        start_date = f"{start_year}-01-01"
        end_date = f"{end_year}-12-31"

        df = self.get_series(list(fx_series.keys()), start_date, end_date)

        if not df.empty:
            df['year'] = df['date'].dt.year

            output_file = self.fx_path / f"banxico_fx_{start_year}_{end_year}.csv"
            df.to_csv(output_file, index=False)
            print(f"[SAVED] {output_file.relative_to(PROJECT_ROOT)}")

            return df
        else:
            print("[WARNING] No data collected")
            return pd.DataFrame()

    def collect_all(self, start_year: int = 2000, end_year: int = None):
        """
        Collect all available Banxico data.

        Parameters
        ----------
        start_year : int, default 2000
            Start year
        end_year : int, optional
            End year
        """
        print("\n" + "="*80)
        print("BANCO DE MEXICO COMPREHENSIVE DATA COLLECTION")
        print("="*80)

        # Collect Balance of Payments
        bop_data = self.get_balance_of_payments(start_year, end_year)

        # Collect Trade
        trade_data = self.get_trade_data(start_year, end_year)

        print("\n" + "="*80)
        print("BANXICO DATA COLLECTION COMPLETE")
        print("="*80)
        print(f"\nData saved to: {BANXICO_PATH.relative_to(PROJECT_ROOT)}")

        return {
            'bop': bop_data,
            'trade': trade_data
        }


def main():
    """Main execution: collect Banxico data."""

    # Banxico SIE API token. Get a free token at
    # https://www.banxico.org.mx/SieAPIRest/service/v1/token and set BANXICO_TOKEN.
    API_TOKEN = os.environ.get("BANXICO_TOKEN")
    if not API_TOKEN:
        raise SystemExit("BANXICO_TOKEN not set. See README (Setup) for a free token.")

    print("\n" + "="*80)
    print("Banco de Mexico International Economics Data Collection")
    print("="*80)

    collector = BanxicoDataCollector(api_token=API_TOKEN)

    # Collect data for 2000-2024
    data = collector.collect_all(start_year=2000, end_year=2024)

    print("\n[COMPLETE] Banxico data collection finished!")


if __name__ == "__main__":
    main()

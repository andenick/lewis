"""
UN Comtrade Data Collector for Lewis Platform
============================================

Comprehensive integration with UN Comtrade API to collect bilateral
trade flow data between countries, providing detailed trade statistics
by commodity, partner, and time period.

Author: Lewis Platform
Date: October 14, 2025
"""

import pandas as pd
import numpy as np
import requests
import time
import logging
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import json
from datetime import datetime, timedelta

class UNComtradeCollector:
    """
    Comprehensive UN Comtrade data collector with caching, validation,
    and error handling for bilateral trade flow data.
    """

    def __init__(self, cache_dir: Path = None, api_base_url: str = "https://comtrade.un.org/api"):
        """Initialize UN Comtrade collector with caching and validation."""
        self.api_base_url = api_base_url
        # Alternative API URLs to try if main one fails
        self.alternative_urls = [
            "https://comtrade.un.org/api",
            "https://comtradeplus.un.org/api/v1",
            "https://api.comtrade.un.org"
        ]
        self.cache_dir = cache_dir or Path(__file__).parent.parent.parent / "data" / "cache" / "un_comtrade"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Set up logging
        self.logger = logging.getLogger(__name__)

        # Rate limiting for free API (1 call per second)
        self.requests_per_second = 1
        self.last_request_time = None

        # Country code mappings (ISO3 to Comtrade codes)
        self.country_codes = {
            'USA': '842',   # United States
            'GBR': '826',   # United Kingdom
            'DEU': '276',   # Germany
            'FRA': '250',   # France
            'ITA': '380',   # Italy
            'CAN': '124',   # Canada
            'JPN': '392',   # Japan
            'CHN': '156',   # China
            'IND': '356',   # India
            'BRA': '76',    # Brazil
            'ALL': 'all'    # All countries
        }

        # Commodity classifications
        self.classifications = {
            'HS': 'Harmonized System',
            'S1': 'SITC Revision 1',
            'S2': 'SITC Revision 2',
            'S3': 'SITC Revision 3',
            'S4': 'SITC Revision 4',
            'BEC': 'Broad Economic Categories'
        }

        # Trade flows
        self.trade_flows = {
            'import': '1',
            'export': '2',
            'all': 'all'
        }

        # Frequencies
        self.frequencies = {
            'annual': 'A',
            'monthly': 'M',
            'quarterly': 'Q'
        }

    def _rate_limit_check(self):
        """Implement rate limiting for free API (1 call per second)."""
        current_time = time.time()

        if self.last_request_time is not None:
            time_since_last = current_time - self.last_request_time
            if time_since_last < (1.0 / self.requests_per_second):
                sleep_time = (1.0 / self.requests_per_second) - time_since_last
                self.logger.info(f"Rate limiting: waiting {sleep_time:.1f} seconds")
                time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _make_api_request(self, params: Dict) -> Dict:
        """Make API request with error handling and rate limiting."""
        self._rate_limit_check()

        # Try main API first, then alternatives
        urls_to_try = [self.api_base_url] + self.alternative_urls

        for base_url in urls_to_try:
            try:
                full_url = f"{base_url}/get"
                self.logger.debug(f"Trying API URL: {full_url}")

                response = requests.get(full_url, params=params, timeout=60)

                if response.status_code == 200:
                    return response.json()
                else:
                    self.logger.warning(f"API request to {full_url} failed with status {response.status_code}")
                    continue

            except requests.exceptions.RequestException as e:
                self.logger.warning(f"API request to {base_url} failed: {e}")
                continue
            except json.JSONDecodeError as e:
                self.logger.warning(f"Failed to decode JSON response from {base_url}: {e}")
                continue

        self.logger.error("All API endpoints failed")
        return {}

    def _get_cache_filename(self, reporter: str, partner: str, year: str,
                           commodity_code: str, flow: str) -> Path:
        """Generate cache filename for API responses."""
        safe_commodity = commodity_code.replace(':', '_').replace(',', '_')
        return self.cache_dir / f"{reporter}_{partner}_{year}_{flow}_{safe_commodity}.json"

    def _is_cache_valid(self, cache_file: Path, max_age_hours: int = 168) -> bool:
        """Check if cached data is still valid (default 1 week)."""
        if not cache_file.exists():
            return False

        file_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
        return file_age < timedelta(hours=max_age_hours)

    def _load_from_cache(self, cache_file: Path) -> Optional[Dict]:
        """Load data from cache file."""
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.logger.warning(f"Failed to load cache file {cache_file}: {e}")
            return None

    def _save_to_cache(self, data: Dict, cache_file: Path):
        """Save data to cache file."""
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.warning(f"Failed to save cache file {cache_file}: {e}")

    def _process_trade_data(self, api_data: Dict, reporter: str, partner: str) -> pd.DataFrame:
        """Process UN Comtrade API response into clean DataFrame."""
        if 'dataset' not in api_data:
            self.logger.warning("No 'dataset' field in API response")
            return pd.DataFrame()

        try:
            # Extract dataset
            dataset = api_data['dataset']
            if not dataset:
                return pd.DataFrame()

            # Convert to DataFrame
            df = pd.DataFrame(dataset)

            if df.empty:
                return df

            # Standardize column names (handle long column names)
            column_mapping = {
                'yr': 'year',
                'period': 'period',
                'rgCode': 'flow_code',
                'rgDesc': 'flow_description',
                'rtCode': 'reporter_code',
                'rtTitle': 'reporter_name',
                'rt3ISO': 'reporter_iso3',
                'ptCode': 'partner_code',
                'ptTitle': 'partner_name',
                'pt3ISO': 'partner_iso3',
                'cmdCode': 'commodity_code',
                'cmdDescE': 'commodity_description',
                'qtCode': 'quantity_code',
                'qtDesc': 'quantity_description',
                'TradeValue': 'trade_value_usd',
                'CifValue': 'cif_value_usd',
                'FobValue': 'fob_value_usd',
                'PrimaryValue': 'primary_value',
                'NetWeight': 'net_weight_kg',
                'GrossWeight': 'gross_weight_kg',
                'TradeQuantity': 'trade_quantity'
            }

            # Rename columns that exist
            for old_name, new_name in column_mapping.items():
                if old_name in df.columns:
                    df = df.rename(columns={old_name: new_name})

            # Add metadata
            df['data_source'] = 'UN_Comtrade'
            df['collected_date'] = datetime.now()
            df['reporter_iso3'] = reporter
            df['partner_iso3'] = partner

            # Convert data types
            if 'year' in df.columns:
                df['year'] = pd.to_numeric(df['year'], errors='coerce')

            if 'trade_value_usd' in df.columns:
                df['trade_value_usd'] = pd.to_numeric(df['trade_value_usd'], errors='coerce')

            if 'primary_value' in df.columns:
                df['primary_value'] = pd.to_numeric(df['primary_value'], errors='coerce')

            # Sort by year and value
            if 'year' in df.columns and 'trade_value_usd' in df.columns:
                df = df.sort_values(['year', 'trade_value_usd'], ascending=[True, False])

            return df

        except Exception as e:
            self.logger.error(f"Error processing trade data: {e}")
            return pd.DataFrame()

    def fetch_bilateral_trade(self, reporter: str, partner: str, years: List[str],
                             commodity_code: str = 'TOTAL', flow: str = 'all',
                             classification: str = 'HS', frequency: str = 'A') -> pd.DataFrame:
        """
        Fetch bilateral trade data between two countries.

        Args:
            reporter: Reporting country ISO3 code (e.g., 'USA', 'CHN')
            partner: Partner country ISO3 code (e.g., 'GBR', 'DEU')
            years: List of years (e.g., ['2020', '2021', '2022'])
            commodity_code: Commodity code ('TOTAL' for all goods, or specific codes)
            flow: Trade flow ('import', 'export', 'all')
            classification: Classification system ('HS', 'S2', etc.)
            frequency: Data frequency ('A' for annual, 'M' for monthly)

        Returns:
            DataFrame with bilateral trade data
        """
        all_data = []

        for year in years:
            # Build API parameters
            params = {
                'max': '50000',  # Maximum records per request
                'type': 'C',     # Goods trade
                'freq': frequency,
                'px': classification,
                'ps': year,
                'r': self.country_codes.get(reporter, reporter),
                'p': self.country_codes.get(partner, partner),
                'rg': self.trade_flows.get(flow, flow),
                'cc': commodity_code
            }

            # Check cache
            cache_file = self._get_cache_filename(reporter, partner, year, commodity_code, flow)

            if self._is_cache_valid(cache_file):
                cached_data = self._load_from_cache(cache_file)
                if cached_data:
                    df = self._process_trade_data(cached_data, reporter, partner)
                    if not df.empty:
                        all_data.append(df)
                        continue

            # Make API request
            api_data = self._make_api_request(params)

            if api_data:
                # Save to cache
                self._save_to_cache(api_data, cache_file)

                # Process data
                df = self._process_trade_data(api_data, reporter, partner)
                if not df.empty:
                    all_data.append(df)

        # Combine all years
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            return combined_df

        return pd.DataFrame()

    def fetch_multilateral_trade(self, reporter: str, partners: List[str], years: List[str],
                                commodity_code: str = 'TOTAL', flow: str = 'all') -> pd.DataFrame:
        """
        Fetch trade data between one reporter and multiple partners.

        Args:
            reporter: Reporting country ISO3 code
            partners: List of partner country ISO3 codes
            years: List of years
            commodity_code: Commodity code
            flow: Trade flow direction

        Returns:
            DataFrame with multilateral trade data
        """
        all_data = []

        for partner in partners:
            self.logger.info(f"Fetching {reporter} {flow} data with {partner} for years {years}")
            df = self.fetch_bilateral_trade(reporter, partner, years, commodity_code, flow)
            if not df.empty:
                all_data.append(df)

            # Small delay between partner requests
            time.sleep(0.5)

        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            return combined_df

        return pd.DataFrame()

    def fetch_world_trade_summary(self, reporter: str, years: List[str],
                                 commodity_code: str = 'TOTAL') -> pd.DataFrame:
        """
        Fetch trade data between reporter and all world partners.

        Args:
            reporter: Reporting country ISO3 code
            years: List of years
            commodity_code: Commodity code

        Returns:
            DataFrame with world trade summary
        """
        return self.fetch_bilateral_trade(
            reporter=reporter,
            partner='ALL',
            years=years,
            commodity_code=commodity_code,
            flow='all'
        )

    def fetch_major_economies_trade(self, years: List[str],
                                    commodity_code: str = 'TOTAL') -> Dict[str, pd.DataFrame]:
        """
        Fetch trade data for major economies (G7 + China).

        Args:
            years: List of years
            commodity_code: Commodity code

        Returns:
            Dictionary with country-specific DataFrames
        """
        major_economies = ['USA', 'CHN', 'GBR', 'DEU', 'JPN', 'FRA', 'ITA', 'CAN']
        results = {}

        for economy in major_economies:
            self.logger.info(f"Fetching world trade summary for {economy}")
            df = self.fetch_world_trade_summary(economy, years, commodity_code)
            if not df.empty:
                results[economy] = df

        return results

    def fetch_commodity_specific_trade(self, commodity_code: str, years: List[str],
                                     countries: List[str] = None) -> pd.DataFrame:
        """
        Fetch trade data for specific commodity across multiple countries.

        Args:
            commodity_code: Commodity code (e.g., '2709' for petroleum)
            years: List of years
            countries: List of reporter countries (default: major economies)

        Returns:
            DataFrame with commodity-specific trade data
        """
        if countries is None:
            countries = ['USA', 'CHN', 'GBR', 'DEU', 'JPN', 'FRA', 'ITA', 'CAN']

        all_data = []

        for country in countries:
            self.logger.info(f"Fetching {commodity_code} trade data for {country}")
            df = self.fetch_world_trade_summary(country, years, commodity_code)
            if not df.empty:
                all_data.append(df)

        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            return combined_df

        return pd.DataFrame()

    def create_trade_matrix(self, year: str, countries: List[str] = None,
                           commodity_code: str = 'TOTAL') -> pd.DataFrame:
        """
        Create bilateral trade matrix for specified year and countries.

        Args:
            year: Year for trade matrix
            countries: List of countries (default: major economies)
            commodity_code: Commodity code

        Returns:
            DataFrame with trade matrix (reporter x partner)
        """
        if countries is None:
            countries = ['USA', 'CHN', 'GBR', 'DEU', 'JPN', 'FRA', 'ITA', 'CAN']

        trade_matrix = []

        for reporter in countries:
            for partner in countries:
                if reporter == partner:
                    continue  # Skip same-country pairs

                df = self.fetch_bilateral_trade(
                    reporter=reporter,
                    partner=partner,
                    years=[year],
                    commodity_code=commodity_code,
                    flow='all'
                )

                if not df.empty:
                    # Aggregate flows for this country pair
                    total_value = df['trade_value_usd'].sum()
                    exports = df[df['flow_code'] == 2]['trade_value_usd'].sum()
                    imports = df[df['flow_code'] == 1]['trade_value_usd'].sum()

                    trade_matrix.append({
                        'reporter': reporter,
                        'partner': partner,
                        'year': int(year),
                        'commodity_code': commodity_code,
                        'total_trade_usd': total_value,
                        'exports_usd': exports,
                        'imports_usd': imports,
                        'trade_balance_usd': exports - imports
                    })

        return pd.DataFrame(trade_matrix)

    def get_trade_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate summary statistics from trade data.

        Args:
            df: Trade data DataFrame

        Returns:
            Dictionary with summary statistics
        """
        if df.empty:
            return {'error': 'Empty DataFrame'}

        stats = {
            'total_observations': len(df),
            'date_range': {},
            'total_trade_value': 0,
            'top_trading_partners': {},
            'commodity_breakdown': {},
            'flow_breakdown': {}
        }

        # Date range
        if 'year' in df.columns:
            stats['date_range'] = {
                'start_year': df['year'].min(),
                'end_year': df['year'].max(),
                'years_covered': df['year'].nunique()
            }

        # Total trade value
        if 'trade_value_usd' in df.columns:
            stats['total_trade_value'] = df['trade_value_usd'].sum()

        # Top trading partners
        if 'partner_name' in df.columns and 'trade_value_usd' in df.columns:
            partner_totals = df.groupby('partner_name')['trade_value_usd'].sum().sort_values(ascending=False)
            stats['top_trading_partners'] = partner_totals.head(10).to_dict()

        # Flow breakdown
        if 'flow_description' in df.columns and 'trade_value_usd' in df.columns:
            flow_totals = df.groupby('flow_description')['trade_value_usd'].sum()
            stats['flow_breakdown'] = flow_totals.to_dict()

        # Commodity breakdown
        if 'commodity_description' in df.columns and 'trade_value_usd' in df.columns:
            comm_totals = df.groupby('commodity_description')['trade_value_usd'].sum().sort_values(ascending=False)
            stats['commodity_breakdown'] = comm_totals.head(10).to_dict()

        return stats

    def validate_trade_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate trade data quality and completeness.

        Args:
            df: Trade data DataFrame

        Returns:
            Dictionary with validation results
        """
        if df.empty:
            return {'error': 'Empty DataFrame', 'valid': False}

        validation = {
            'valid': True,
            'issues': [],
            'warnings': [],
            'completeness': {}
        }

        # Check required columns
        required_columns = ['year', 'trade_value_usd', 'reporter_iso3', 'partner_iso3']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            validation['valid'] = False
            validation['issues'].append(f"Missing required columns: {missing_columns}")

        # Check for null values
        null_counts = df.isnull().sum()
        high_null_columns = null_counts[null_counts > len(df) * 0.1].to_dict()
        if high_null_columns:
            validation['warnings'].append(f"High null values in: {list(high_null_columns.keys())}")

        # Check data types
        if 'trade_value_usd' in df.columns:
            non_numeric_values = df['trade_value_usd'].apply(lambda x: not pd.api.types.is_numeric_dtype(type(x)))
            if non_numeric_values.any():
                validation['issues'].append(f"Non-numeric values in trade_value_usd")

        # Check date continuity
        if 'year' in df.columns:
            years = sorted(df['year'].unique())
            expected_years = list(range(min(years), max(years) + 1))
            missing_years = set(expected_years) - set(years)
            if missing_years:
                validation['warnings'].append(f"Missing years: {sorted(missing_years)}")

        # Calculate completeness percentage
        total_possible = len(required_columns) + len(expected_years)
        actual_present = (len(required_columns) - len(missing_columns)) + len(years)
        validation['completeness']['percentage'] = (actual_present / total_possible) * 100

        return validation


# Example usage and testing
def main():
    """Test UN Comtrade collector functionality."""
    collector = UNComtradeCollector()

    print("UN Comtrade Data Collector Test")
    print("=" * 50)

    # Test fetching bilateral trade data
    print("\nTesting bilateral trade data fetch...")
    try:
        # Recent years to avoid API limits
        test_years = ['2022', '2023']

        # Fetch US-China trade data
        us_china_trade = collector.fetch_bilateral_trade(
            reporter='USA',
            partner='CHN',
            years=test_years,
            commodity_code='TOTAL',
            flow='all'
        )

        if not us_china_trade.empty:
            print(f"SUCCESS: Fetched {len(us_china_trade)} US-China trade observations")
            print(f"Date range: {us_china_trade['year'].min()} - {us_china_trade['year'].max()}")
            if 'trade_value_usd' in us_china_trade.columns:
                total_value = us_china_trade['trade_value_usd'].sum()
                print(f"Total trade value: ${total_value:,.0f}")
        else:
            print("FAILED: No US-China trade data fetched")

    except Exception as e:
        print(f"ERROR: Failed to fetch bilateral trade data: {e}")

    # Test trade statistics
    if not us_china_trade.empty:
        print("\nGenerating trade statistics...")
        stats = collector.get_trade_statistics(us_china_trade)
        print(f"Total observations: {stats.get('total_observations', 0)}")
        print(f"Date range: {stats.get('date_range', {})}")
        print(f"Total trade value: ${stats.get('total_trade_value', 0):,.0f}")

    # Test validation
    if not us_china_trade.empty:
        print("\nValidating data quality...")
        validation = collector.validate_trade_data(us_china_trade)
        print(f"Data valid: {validation.get('valid', False)}")
        print(f"Completeness: {validation['completeness'].get('percentage', 0):.1f}%")
        if validation.get('issues'):
            print(f"Issues: {validation['issues']}")
        if validation.get('warnings'):
            print(f"Warnings: {validation['warnings']}")

    print("\nUN Comtrade collector test completed.")


if __name__ == "__main__":
    main()
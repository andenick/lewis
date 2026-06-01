"""
DBnomics Data Collector for Lewis Platform
==========================================

Comprehensive integration with DBnomics API to collect international
economic data from multiple providers including OECD, Eurostat, IMF,
World Bank, and other official sources.

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

class DBnomicsCollector:
    """
    Comprehensive DBnomics data collector with caching, validation,
    and error handling for international economic data.
    """

    def __init__(self, cache_dir: Path = None, api_base_url: str = "https://api.db.nomics.world/v22"):
        """Initialize DBnomics collector with caching and validation."""
        self.api_base_url = api_base_url
        self.cache_dir = cache_dir or Path(__file__).parent.parent.parent / "data" / "cache" / "dbnomics"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Set up logging
        self.logger = logging.getLogger(__name__)

        # Rate limiting
        self.requests_per_minute = 60  # Conservative rate limit
        self.last_request_time = None
        self.request_count = 0

        # Key providers for international economics
        self.providers = {
            'OECD': 'Organization for Economic Co-operation and Development',
            'Eurostat': 'European Commission Statistical Office',
            'IMF': 'International Monetary Fund',
            'WorldBank': 'World Bank',
            'BIS': 'Bank for International Settlements',
            'ECB': 'European Central Bank',
            'BEA': 'U.S. Bureau of Economic Analysis'
        }

        # Key datasets for balance of payments and international economics
        self.target_datasets = {
            'OECD': {
                'MEI': 'Main Economic Indicators',
                'STAN': 'Structural Analysis',
                'BOP': 'Balance of Payments',
                'QNA': 'Quarterly National Accounts'
            },
            'Eurostat': {
                'bop_gdp_q': 'Balance of payments - GDP',
                'bop_its6_itg': 'International trade in services',
                'nama_10_gdp': 'Quarterly national accounts',
                'ei_bsin_q': 'Business investment'
            },
            'IMF': {
                'BOP': 'Balance of Payments Statistics',
                'WEO': 'World Economic Outlook',
                'IFS': 'International Financial Statistics',
                'CDIS': 'Coordinated Direct Investment Survey'
            },
            'WorldBank': {
                'WDI': 'World Development Indicators',
                'GEM': 'Global Economic Monitor',
                'BMG': 'Bond Market Indicators'
            }
        }

    def _rate_limit_check(self):
        """Implement rate limiting to avoid API throttling."""
        current_time = time.time()

        if self.last_request_time is None:
            self.last_request_time = current_time
            self.request_count = 1
            return

        # Reset counter if more than a minute has passed
        if current_time - self.last_request_time > 60:
            self.last_request_time = current_time
            self.request_count = 1
            return

        # If we're approaching the rate limit, wait
        if self.request_count >= self.requests_per_minute:
            sleep_time = 60 - (current_time - self.last_request_time)
            if sleep_time > 0:
                self.logger.info(f"Rate limit reached, waiting {sleep_time:.1f} seconds")
                time.sleep(sleep_time)
                self.last_request_time = time.time()
                self.request_count = 1
        else:
            self.request_count += 1

    def _make_api_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make API request with error handling and rate limiting."""
        self._rate_limit_check()

        url = f"{self.api_base_url}/{endpoint}"

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed for {url}: {e}")
            return {}
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON response from {url}: {e}")
            return {}

    def _get_cache_filename(self, provider: str, dataset: str, series_code: str = None) -> Path:
        """Generate cache filename for API responses."""
        if series_code:
            # Replace problematic characters in series code
            safe_series = series_code.replace('/', '_').replace('.', '_').replace('+', '_')
            return self.cache_dir / f"{provider}_{dataset}_{safe_series}.json"
        else:
            return self.cache_dir / f"{provider}_{dataset}.json"

    def _is_cache_valid(self, cache_file: Path, max_age_hours: int = 24) -> bool:
        """Check if cached data is still valid."""
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

    def get_providers(self) -> pd.DataFrame:
        """Get list of all available providers."""
        cache_file = self.cache_dir / "providers.json"

        if self._is_cache_valid(cache_file):
            cached_data = self._load_from_cache(cache_file)
            if cached_data and 'providers' in cached_data:
                providers_data = cached_data['providers'].get('docs', [])
                return pd.DataFrame(providers_data)

        data = self._make_api_request("providers")
        if data and 'providers' in data:
            self._save_to_cache(data, cache_file)
            providers_data = data['providers'].get('docs', [])
            return pd.DataFrame(providers_data)

        return pd.DataFrame()

    def get_provider_datasets(self, provider_code: str) -> pd.DataFrame:
        """Get all datasets for a specific provider."""
        cache_file = self.cache_dir / f"datasets_{provider_code}.json"

        if self._is_cache_valid(cache_file):
            cached_data = self._load_from_cache(cache_file)
            if cached_data:
                return pd.DataFrame(cached_data.get('datasets', []))

        data = self._make_api_request(f"datasets/{provider_code}")
        if data and 'datasets' in data:
            self._save_to_cache(data, cache_file)
            return pd.DataFrame(data['datasets'])

        return pd.DataFrame()

    def search_series(self, query: str, provider_code: str = None, limit: int = 100) -> pd.DataFrame:
        """Search for time series matching a query."""
        params = {
            'q': query,
            'limit': limit
        }
        if provider_code:
            params['provider_code'] = provider_code

        data = self._make_api_request("search", params)
        if data and 'series' in data:
            return pd.DataFrame(data['series'])

        return pd.DataFrame()

    def fetch_series(self, provider_code: str, dataset_code: str,
                    series_code: str = None, use_cache: bool = True) -> pd.DataFrame:
        """
        Fetch time series data from DBnomics.

        Args:
            provider_code: Provider code (e.g., 'OECD', 'Eurostat')
            dataset_code: Dataset code (e.g., 'MEI', 'BOP')
            series_code: Series code (optional, fetches all series if None)
            use_cache: Whether to use cached data

        Returns:
            DataFrame with time series data
        """
        cache_file = self._get_cache_filename(provider_code, dataset_code, series_code)

        # Check cache first
        if use_cache and self._is_cache_valid(cache_file):
            cached_data = self._load_from_cache(cache_file)
            if cached_data and 'series' in cached_data:
                return self._process_series_response(cached_data)

        # Build API endpoint with observations
        if series_code:
            endpoint = f"series/{provider_code}/{dataset_code}/{series_code}?observations=true"
        else:
            endpoint = f"series/{provider_code}/{dataset_code}?observations=true"

        data = self._make_api_request(endpoint)

        if data and 'series' in data:
            # Save to cache
            if use_cache:
                self._save_to_cache(data, cache_file)

            # Process the response
            return self._process_series_response(data)

        return pd.DataFrame()

    def _process_series_response(self, data: Dict) -> pd.DataFrame:
        """Process DBnomics series response into DataFrame."""
        if 'series' not in data or 'docs' not in data['series']:
            return pd.DataFrame()

        series_docs = data['series']['docs']
        if not series_docs:
            return pd.DataFrame()

        # If there are multiple series, combine them
        all_data = []
        for series_doc in series_docs:
            if 'period' in series_doc and 'value' in series_doc:
                # Create DataFrame for this series
                series_df = pd.DataFrame({
                    'date': series_doc['period'],
                    'value': series_doc['value'],
                    'frequency': series_doc.get('@frequency', ''),
                    'series_code': series_doc.get('series_code', ''),
                    'series_name': series_doc.get('series_name', ''),
                    'provider_code': series_doc.get('provider_code', ''),
                    'dataset_code': series_doc.get('dataset_code', ''),
                    'dataset_name': series_doc.get('dataset_name', '')
                })
                all_data.append(series_df)

        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            return self._clean_series_data(combined_df)

        return pd.DataFrame()

    def fetch_balance_of_payments_data(self, countries: List[str] = None) -> Dict[str, pd.DataFrame]:
        """
        Fetch balance of payments data for specified countries.

        Args:
            countries: List of country codes (e.g., ['US', 'GB', 'DE'])

        Returns:
            Dictionary with country-specific DataFrames
        """
        if countries is None:
            countries = ['US', 'GB', 'DE', 'FR', 'IT', 'CA', 'JP']

        results = {}

        # OECD Balance of Payments data
        oecd_bop_series = [
            # Current Account Balance
            "USA.B6BLTT01.CXCUSA.Q",  # US Current Account
            "GBR.B6BLTT01.CXCGBR.Q",  # UK Current Account
            "DEU.B6BLTT01.CXCDEU.Q",  # Germany Current Account
            "FRA.B6BLTT01.XCFRA.Q",   # France Current Account
            "ITA.B6BLTT01.XCITA.Q",   # Italy Current Account
            "CAN.B6BLTT01.XCCAN.Q",   # Canada Current Account
            "JPN.B6BLTT01.XCJPN.Q",   # Japan Current Account
        ]

        for series_code in oecd_bop_series:
            try:
                country = series_code.split('.')[0]
                df = self.fetch_series('OECD', 'MEI', series_code)

                if not df.empty:
                    # Process and standardize the data
                    df = self._process_bop_series(df, country)
                    results[country] = df

            except Exception as e:
                self.logger.error(f"Failed to fetch {series_code}: {e}")
                continue

        # Try Eurostat BOP data for EU countries
        eu_countries = ['GB', 'DE', 'FR', 'IT']
        for country in eu_countries:
            try:
                # Eurostat BOP quarterly data
                eu_series = f"balance.{country.lower()}.b6.q"
                df = self.fetch_series('Eurostat', 'bop_gdp_q', eu_series)

                if not df.empty:
                    df = self._process_eurostat_bop(df, country)
                    if country not in results:
                        results[country] = df
                    else:
                        # Merge with existing data
                        results[country] = pd.concat([results[country], df], ignore_index=True)

            except Exception as e:
                self.logger.warning(f"Failed to fetch Eurostat BOP for {country}: {e}")

        return results

    def fetch_trade_data(self, countries: List[str] = None) -> Dict[str, pd.DataFrame]:
        """
        Fetch international trade data for specified countries.

        Args:
            countries: List of country codes

        Returns:
            Dictionary with trade data DataFrames
        """
        if countries is None:
            countries = ['US', 'GB', 'DE', 'FR', 'IT', 'CA', 'JP']

        results = {}

        # OECD Trade data
        trade_series = {
            'US': 'USA.B6BLTT02.CXCUSA.Q',  # US Trade Balance
            'GB': 'GBR.B6BLTT02.CXCGBR.Q',  # UK Trade Balance
            'DE': 'DEU.B6BLTT02.CXCDEU.Q',  # Germany Trade Balance
            'FR': 'FRA.B6BLTT02.XCFRA.Q',   # France Trade Balance
            'IT': 'ITA.B6BLTT02.XCITA.Q',   # Italy Trade Balance
            'CA': 'CAN.B6BLTT02.XCCAN.Q',   # Canada Trade Balance
            'JP': 'JPN.B6BLTT02.XCJPN.Q',   # Japan Trade Balance
        }

        for country, series_code in trade_series.items():
            try:
                df = self.fetch_series('OECD', 'MEI', series_code)

                if not df.empty:
                    df = self._process_trade_series(df, country)
                    results[country] = df

            except Exception as e:
                self.logger.error(f"Failed to fetch trade data for {country}: {e}")

        return results

    def fetch_gdp_data(self, countries: List[str] = None) -> Dict[str, pd.DataFrame]:
        """
        Fetch GDP data for specified countries.

        Args:
            countries: List of country codes

        Returns:
            Dictionary with GDP data DataFrames
        """
        if countries is None:
            countries = ['US', 'GB', 'DE', 'FR', 'IT', 'CA', 'JP']

        results = {}

        # OECD GDP data
        gdp_series = {
            'US': 'USA.LFWAATTT.CXMUSA.Q',    # US Real GDP
            'GB': 'GBR.LFWAATTT.CXMGBR.Q',    # UK Real GDP
            'DE': 'DEU.LFWAATTT.CXMDEU.Q',    # Germany Real GDP
            'FR': 'FRA.LFWAATTT.XCFRA.Q',     # France Real GDP
            'IT': 'ITA.LFWAATTT.XCITA.Q',     # Italy Real GDP
            'CA': 'CAN.LFWAATTT.XCCAN.Q',     # Canada Real GDP
            'JP': 'JPN.LFWAATTT.XCJPN.Q',     # Japan Real GDP
        }

        for country, series_code in gdp_series.items():
            try:
                df = self.fetch_series('OECD', 'MEI', series_code)

                if not df.empty:
                    df = self._process_gdp_series(df, country)
                    results[country] = df

            except Exception as e:
                self.logger.error(f"Failed to fetch GDP data for {country}: {e}")

        return results

    def _clean_series_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize time series data."""
        if df.empty:
            return df

        # Standardize column names
        column_mapping = {
            'period': 'date',
            'value': 'value',
            'original_period': 'original_date',
            '@frequency': 'frequency',
            'series_code': 'series_code',
            'series_name': 'series_name'
        }

        df = df.rename(columns={col: new_col for col, new_col in column_mapping.items() if col in df.columns})

        # Convert date column
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')

        # Clean value column
        if 'value' in df.columns:
            df['value'] = pd.to_numeric(df['value'], errors='coerce')

        # Sort by date
        if 'date' in df.columns:
            df = df.sort_values('date').reset_index(drop=True)

        return df

    def _process_bop_series(self, df: pd.DataFrame, country: str) -> pd.DataFrame:
        """Process balance of payments series data."""
        if df.empty:
            return df

        # Add metadata
        df['country'] = country
        df['indicator_type'] = 'balance_of_payments'
        df['data_source'] = 'DBnomics-OECD'

        # Standardize value column to millions USD
        if 'value' in df.columns:
            df['value_usd_millions'] = df['value']

        # Add period information
        if 'date' in df.columns:
            df['year'] = df['date'].dt.year
            df['quarter'] = df['date'].dt.quarter

        return df

    def _process_eurostat_bop(self, df: pd.DataFrame, country: str) -> pd.DataFrame:
        """Process Eurostat balance of payments data."""
        if df.empty:
            return df

        # Similar processing as BOP series but for Eurostat format
        df['country'] = country
        df['indicator_type'] = 'balance_of_payments'
        df['data_source'] = 'DBnomics-Eurostat'

        if 'value' in df.columns:
            df['value_usd_millions'] = df['value']

        if 'date' in df.columns:
            df['year'] = df['date'].dt.year
            df['quarter'] = df['date'].dt.quarter

        return df

    def _process_trade_series(self, df: pd.DataFrame, country: str) -> pd.DataFrame:
        """Process trade series data."""
        if df.empty:
            return df

        df['country'] = country
        df['indicator_type'] = 'trade_balance'
        df['data_source'] = 'DBnomics-OECD'

        if 'value' in df.columns:
            df['value_usd_millions'] = df['value']

        if 'date' in df.columns:
            df['year'] = df['date'].dt.year
            df['quarter'] = df['date'].dt.quarter

        return df

    def _process_gdp_series(self, df: pd.DataFrame, country: str) -> pd.DataFrame:
        """Process GDP series data."""
        if df.empty:
            return df

        df['country'] = country
        df['indicator_type'] = 'gdp'
        df['data_source'] = 'DBnomics-OECD'

        if 'value' in df.columns:
            df['value_local_currency'] = df['value']

        if 'date' in df.columns:
            df['year'] = df['date'].dt.year
            df['quarter'] = df['date'].dt.quarter

        return df

    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary of available data from DBnomics."""
        summary = {
            'providers': {},
            'total_providers': 0,
            'target_datasets_found': 0,
            'data_coverage': {}
        }

        # Get all providers
        providers_df = self.get_providers()
        if not providers_df.empty:
            summary['total_providers'] = len(providers_df)

            # Check for target providers
            for provider_code, provider_name in self.providers.items():
                if provider_code in providers_df['code'].values:
                    summary['providers'][provider_code] = {
                        'name': provider_name,
                        'dataset_count': 'Available',
                        'found': True
                    }
                    summary['target_datasets_found'] += 1
                else:
                    summary['providers'][provider_code] = {
                        'name': provider_name,
                        'dataset_count': 0,
                        'found': False
                    }

        return summary

    def validate_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate data quality and return quality metrics."""
        if df.empty:
            return {'error': 'Empty DataFrame'}

        quality_metrics = {
            'total_observations': len(df),
            'null_values': df.isnull().sum().to_dict(),
            'date_range': {},
            'frequency_distribution': {},
            'data_completeness': 0.0
        }

        # Date range
        if 'date' in df.columns:
            quality_metrics['date_range'] = {
                'start': df['date'].min(),
                'end': df['date'].max(),
                'years_covered': df['date'].dt.year.nunique()
            }

        # Frequency distribution
        if 'frequency' in df.columns:
            quality_metrics['frequency_distribution'] = df['frequency'].value_counts().to_dict()

        # Data completeness
        if 'value' in df.columns:
            non_null_values = df['value'].notna().sum()
            quality_metrics['data_completeness'] = (non_null_values / len(df)) * 100

        return quality_metrics


# Example usage and testing
def main():
    """Test DBnomics collector functionality."""
    collector = DBnomicsCollector()

    print("DBnomics Data Collector Test")
    print("=" * 50)

    # Test provider information
    print("Getting provider information...")
    providers = collector.get_providers()
    print(f"Found {len(providers)} providers")

    # Check target providers
    target_found = 0
    for provider_code in collector.providers.keys():
        if provider_code in providers['code'].values:
            target_found += 1
            print(f"FOUND: {provider_code}")
        else:
            print(f"MISSING: {provider_code}")

    print(f"\nTarget providers found: {target_found}/{len(collector.providers)}")

    # Test fetching some data
    print("\nTesting data fetch...")
    try:
        # Fetch some OECD data
        test_data = collector.fetch_series('OECD', 'MEI', 'USA.B6BLTT01.CXCUSA.Q')
        if not test_data.empty:
            print(f"SUCCESS: Fetched {len(test_data)} observations for US Current Account")
            print(f"Date range: {test_data['date'].min()} to {test_data['date'].max()}")
        else:
            print("FAILED: No data fetched")
    except Exception as e:
        print(f"ERROR: Failed fetching data: {e}")

    # Test balance of payments collection
    print("\nTesting BOP data collection...")
    try:
        bop_data = collector.fetch_balance_of_payments_data(['US', 'GB', 'DE'])
        for country, df in bop_data.items():
            print(f"SUCCESS: {country}: {len(df)} observations")
    except Exception as e:
        print(f"ERROR: Failed collecting BOP data: {e}")

    # Get data summary
    print("\nGenerating data summary...")
    summary = collector.get_data_summary()
    print(f"Target providers found: {summary['target_datasets_found']}")
    print("Provider details:")
    for code, info in summary['providers'].items():
        status = "FOUND" if info['found'] else "MISSING"
        print(f"  {status} {code}: {info['dataset_count']} datasets")


if __name__ == "__main__":
    main()
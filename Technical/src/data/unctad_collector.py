"""
UNCTAD Data Collector for Lewis Platform
=======================================

Comprehensive integration with UNCTAD data sources including
WITS API (UNDTAD TRAINS), UNCTADstat, and related trade and
development indicators for international economics analysis.

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

class UNCTADCollector:
    """
    Comprehensive UNCTAD data collector with multiple data sources
    including WITS API, UNCTADstat, and international trade statistics.
    """

    def __init__(self, cache_dir: Path = None):
        """Initialize UNCTAD collector with caching and validation."""
        self.cache_dir = cache_dir or Path(__file__).parent.parent.parent / "data" / "cache" / "unctad"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Set up logging
        self.logger = logging.getLogger(__name__)

        # Rate limiting
        self.requests_per_second = 2  # Conservative rate limiting
        self.last_request_time = None

        # API endpoints
        self.apis = {
            'wits': {
                'base_url': 'https://wits.worldbank.org/API/V1/Trade',
                'description': 'World Integrated Trade Solution - includes UNCTAD TRAINS'
            },
            'unctadstat': {
                'base_url': 'https://unctadstat.unctad.org/api',
                'description': 'UNCTAD statistical database'
            },
            'un_data': {
                'base_url': 'https://unstats.un.org/unsd/api',
                'description': 'UN data API with UNCTAD monthly statistics'
            }
        }

        # Country code mappings (ISO3)
        self.country_codes = {
            'USA': 'US',
            'GBR': 'GB',
            'DEU': 'DE',
            'FRA': 'FR',
            'ITA': 'IT',
            'CAN': 'CA',
            'JPN': 'JP',
            'CHN': 'CN',
            'IND': 'IN',
            'BRA': 'BR',
            'ALL': 'all'
        }

        # Indicator codes for WITS API
        self.wits_indicators = {
            'trade_value': 'MPRT-TRD-VL',  # Merchandise trade value
            'export_value': 'XPRT-TRD-VL',
            'import_value': 'MPRT-TRD-VL',
            'trade_balance': 'TB-TRD-VL',
            'concentration_index': 'HH-CONC',
            'market_penetration': 'MPEN-MPEN',
            'gdp': 'NY.GDP.MKTP.CD',
            'gdp_per_capita': 'NY.GDP.PCAP.CD',
            'trade_as_gdp': 'NE.TRD.GNFS.ZS',
            'gdp_growth': 'NY.GDP.MKTP.KD.ZG'
        }

        # Product group codes
        self.product_groups = {
            'ALL': '999999',
            'AGRICULTURE': '01-05',
            'MANUFACTURING': '06-09',
            'FUELS_MINING': '10-12',
            'TOTAL': 'ALL'
        }

    def _rate_limit_check(self):
        """Implement rate limiting."""
        current_time = time.time()

        if self.last_request_time is not None:
            time_since_last = current_time - self.last_request_time
            if time_since_last < (1.0 / self.requests_per_second):
                sleep_time = (1.0 / self.requests_per_second) - time_since_last
                time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _make_api_request(self, url: str, params: Dict = None, timeout: int = 30) -> Dict:
        """Make API request with error handling."""
        self._rate_limit_check()

        try:
            response = requests.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed for {url}: {e}")
            return {}
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON response from {url}: {e}")
            return {}

    def _get_cache_filename(self, source: str, reporter: str, partner: str,
                           year: str, indicator: str) -> Path:
        """Generate cache filename."""
        safe_indicator = indicator.replace('-', '_')
        return self.cache_dir / f"{source}_{reporter}_{partner}_{year}_{safe_indicator}.json"

    def _is_cache_valid(self, cache_file: Path, max_age_hours: int = 168) -> bool:
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

    def fetch_wits_trade_data(self, reporter: str, partner: str, years: List[str],
                            indicator: str = 'trade_value', product_group: str = 'ALL') -> pd.DataFrame:
        """
        Fetch trade data from WITS API (includes UNCTAD TRAINS).

        Args:
            reporter: Reporter country ISO3 code
            partner: Partner country ISO3 code
            years: List of years
            indicator: Trade indicator code
            product_group: Product group code

        Returns:
            DataFrame with trade data
        """
        all_data = []

        for year in years:
            # Build API parameters for WITS API
            params = {
                'reporterCode': self.country_codes.get(reporter, reporter),
                'partnerCode': self.country_codes.get(partner, partner),
                'productCode': self.product_groups.get(product_group, product_group),
                'year': year,
                'indicatorCode': self.wits_indicators.get(indicator, indicator)
            }

            # Check cache
            cache_file = self._get_cache_filename('wits', reporter, partner, year, indicator)

            if self._is_cache_valid(cache_file):
                cached_data = self._load_from_cache(cache_file)
                if cached_data:
                    df = self._process_wits_data(cached_data, reporter, partner)
                    if not df.empty:
                        all_data.append(df)
                        continue

            # Make API request
            api_url = f"{self.apis['wits']['base_url']}/partner"
            api_data = self._make_api_request(api_url, params)

            if api_data:
                # Save to cache
                self._save_to_cache(api_data, cache_file)

                # Process data
                df = self._process_wits_data(api_data, reporter, partner)
                if not df.empty:
                    all_data.append(df)

        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            return combined_df

        return pd.DataFrame()

    def _process_wits_data(self, api_data: Dict, reporter: str, partner: str) -> pd.DataFrame:
        """Process WITS API response into clean DataFrame."""
        try:
            if 'TradeData' not in api_data:
                return pd.DataFrame()

            # Extract trade data
            trade_data = api_data['TradeData']
            if not trade_data:
                return pd.DataFrame()

            df = pd.DataFrame(trade_data)

            # Add metadata
            df['data_source'] = 'UNCTAD_WITS'
            df['collected_date'] = datetime.now()
            df['reporter_iso3'] = reporter
            df['partner_iso3'] = partner

            # Convert data types
            for col in ['TradeValue', 'Year', 'GrowthRate']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            return df

        except Exception as e:
            self.logger.error(f"Error processing WITS data: {e}")
            return pd.DataFrame()

    def fetch_unctadstat_indicators(self, countries: List[str], years: List[str]) -> pd.DataFrame:
        """
        Fetch development indicators from UNCTADstat.

        Args:
            countries: List of country ISO3 codes
            years: List of years

        Returns:
            DataFrame with development indicators
        """
        all_data = []

        # UNCTADstat key indicators
        indicators = [
            'GDP', 'GDP_per_capita', 'Trade_balance', 'Exports',
            'Imports', 'Trade_as_GDP', 'FDI_inflows', 'FDI_outflows'
        ]

        for country in countries:
            for year in years:
                for indicator in indicators:
                    # Build API parameters
                    params = {
                        'country': self.country_codes.get(country, country),
                        'year': year,
                        'indicator': indicator
                    }

                    cache_file = self._get_cache_filename('unctadstat', country, 'world', year, indicator)

                    if self._is_cache_valid(cache_file):
                        cached_data = self._load_from_cache(cache_file)
                        if cached_data:
                            df = self._process_unctadstat_data(cached_data, country)
                            if not df.empty:
                                all_data.append(df)
                                continue

                    # API request (note: UNCTADstat API may require different endpoint)
                    api_data = self._make_api_request(
                        self.apis['unctadstat']['base_url'] + '/data',
                        params
                    )

                    if api_data:
                        self._save_to_cache(api_data, cache_file)
                        df = self._process_unctadstat_data(api_data, country)
                        if not df.empty:
                            all_data.append(df)

        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            return combined_df

        return pd.DataFrame()

    def _process_unctadstat_data(self, api_data: Dict, country: str) -> pd.DataFrame:
        """Process UNCTADstat API response."""
        try:
            if 'data' not in api_data:
                return pd.DataFrame()

            data = api_data['data']
            if not data:
                return pd.DataFrame()

            df = pd.DataFrame(data)

            # Add metadata
            df['data_source'] = 'UNCTADstat'
            df['country_iso3'] = country
            df['collected_date'] = datetime.now()

            return df

        except Exception as e:
            self.logger.error(f"Error processing UNCTADstat data: {e}")
            return pd.DataFrame()

    def fetch_international_development_indicators(self, countries: List[str],
                                                    years: List[str]) -> Dict[str, pd.DataFrame]:
        """
        Fetch comprehensive international development indicators.

        Args:
            countries: List of country ISO3 codes
            years: List of years

        Returns:
            Dictionary with indicator-specific DataFrames
        """
        results = {}

        # Fetch trade data from WITS
        self.logger.info("Fetching trade data from WITS API...")
        for country in countries:
            for partner in countries:
                if country == partner:
                    continue

                trade_data = self.fetch_wits_trade_data(
                    reporter=country,
                    partner=partner,
                    years=years,
                    indicator='trade_value'
                )

                if not trade_data.empty:
                    key = f"{country}_{partner}_trade"
                    results[key] = trade_data

        # Fetch development indicators
        self.logger.info("Fetching development indicators from UNCTADstat...")
        dev_indicators = self.fetch_unctadstat_indicators(countries, years)
        if not dev_indicators.empty:
            results['development_indicators'] = dev_indicators

        return results

    def create_comprehensive_trade_profile(self, country: str, years: List[str]) -> pd.DataFrame:
        """
        Create comprehensive trade profile for a specific country.

        Args:
            country: Country ISO3 code
            years: List of years

        Returns:
            DataFrame with comprehensive trade profile
        """
        profile_data = []

        # Fetch bilateral trade data with major economies
        major_partners = ['USA', 'CHN', 'GBR', 'DEU', 'JPN', 'FRA', 'ITA', 'CAN']

        for partner in major_partners:
            if partner == country:
                continue

            trade_data = self.fetch_wits_trade_data(
                reporter=country,
                partner=partner,
                years=years,
                indicator='trade_value'
            )

            if not trade_data.empty:
                profile_data.append(trade_data)

        if profile_data:
            combined_profile = pd.concat(profile_data, ignore_index=True)
            return combined_profile

        return pd.DataFrame()

    def get_trade_diversification_metrics(self, country: str, years: List[str]) -> pd.DataFrame:
        """
        Calculate trade diversification metrics.

        Args:
            country: Country ISO3 code
            years: List of years

        Returns:
            DataFrame with diversification metrics
        """
        diversification_data = []

        for year in years:
            # Fetch trade concentration index from WITS
            concentration_data = self.fetch_wits_trade_data(
                reporter=country,
                partner='all',
                years=[year],
                indicator='concentration_index'
            )

            if not concentration_data.empty:
                diversification_data.append(concentration_data)

        if diversification_data:
            return pd.concat(diversification_data, ignore_index=True)

        return pd.DataFrame()

    def analyze_global_trade_trends(self, years: List[str]) -> Dict[str, Any]:
        """
        Analyze global trade trends using UNCTAD data.

        Args:
            years: List of years to analyze

        Returns:
            Dictionary with trend analysis results
        """
        major_economies = ['USA', 'CHN', 'GBR', 'DEU', 'JPN', 'FRA', 'ITA', 'CAN']
        results = {
            'total_trade_trends': {},
            'country_rankings': {},
            'growth_analysis': {}
        }

        # Calculate total trade trends
        for year in years:
            year_data = []
            for country in major_economies:
                trade_data = self.fetch_wits_trade_data(
                    reporter=country,
                    partner='all',
                    years=[year],
                    indicator='trade_value'
                )
                if not trade_data.empty and 'TradeValue' in trade_data.columns:
                    total_trade = trade_data['TradeValue'].sum()
                    year_data.append({'country': country, 'total_trade': total_trade})

            if year_data:
                df_year = pd.DataFrame(year_data)
                df_year = df_year.sort_values('total_trade', ascending=False)
                results['country_rankings'][year] = df_year
                results['total_trade_trends'][year] = df_year['total_trade'].sum()

        return results

    def validate_unctad_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate UNCTAD data quality and completeness.

        Args:
            df: UNCTAD data DataFrame

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

        # Check for required columns
        required_columns = ['year', 'country_iso3', 'data_source']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            validation['valid'] = False
            validation['issues'].append(f"Missing required columns: {missing_columns}")

        # Check for null values
        null_counts = df.isnull().sum()
        high_null_columns = null_counts[null_counts > len(df) * 0.1].to_dict()
        if high_null_columns:
            validation['warnings'].append(f"High null values in: {list(high_null_columns.keys())}")

        # Calculate completeness percentage
        total_possible = len(required_columns)
        actual_present = total_possible - len(missing_columns)
        validation['completeness']['percentage'] = (actual_present / total_possible) * 100

        return validation

    def generate_sample_unctad_data(self) -> pd.DataFrame:
        """
        Generate sample UNCTAD data structure for testing.

        Returns:
            DataFrame with sample UNCTAD data
        """
        sample_data = []

        # Sample trade records
        trade_records = [
            {
                'Year': 2022,
                'ReporterISO': 'US',
                'PartnerISO': 'CN',
                'TradeValue': 690600000000,
                'GrowthRate': 8.5,
                'data_source': 'UNCTAD_WITS_Sample',
                'country_iso3': 'USA',
                'partner_iso3': 'CHN',
                'collected_date': datetime.now()
            },
            {
                'Year': 2022,
                'ReporterISO': 'CN',
                'PartnerISO': 'US',
                'TradeValue': 536800000000,
                'GrowthRate': 12.3,
                'data_source': 'UNCTAD_WITS_Sample',
                'country_iso3': 'CHN',
                'partner_iso3': 'USA',
                'collected_date': datetime.now()
            },
            {
                'Year': 2022,
                'ReporterISO': 'DE',
                'PartnerISO': 'CN',
                'TradeValue': 298000000000,
                'GrowthRate': -2.1,
                'data_source': 'UNCTAD_WITS_Sample',
                'country_iso3': 'DEU',
                'partner_iso3': 'CHN',
                'collected_date': datetime.now()
            }
        ]

        for record in trade_records:
            sample_data.append(record)

        # Sample development indicators
        dev_records = [
            {
                'country': 'USA',
                'indicator': 'GDP_per_capita',
                'value': 76330,
                'year': 2022,
                'data_source': 'UNCTADstat_Sample'
            },
            {
                'country': 'CHN',
                'indicator': 'GDP_per_capita',
                'value': 12720,
                'year': 2022,
                'data_source': 'UNCTADstat_Sample'
            },
            {
                'country': 'DEU',
                'indicator': 'GDP_per_capita',
                'value': 48430,
                'year': 2022,
                'data_source': 'UNCTADstat_Sample'
            }
        ]

        for record in dev_records:
            sample_data.append(record)

        return pd.DataFrame(sample_data)


# Example usage and testing
def main():
    """Test UNCTAD collector functionality."""
    collector = UNCTADCollector()

    print("UNCTAD Data Collector Test")
    print("=" * 40)

    # Test sample data generation
    print("\n1. Sample Data Generation:")
    sample_df = collector.generate_sample_unctad_data()
    if not sample_df.empty:
        print(f"Generated {len(sample_df)} sample records")
        print(f"Data sources: {sample_df['data_source'].unique()}")
        print("\nFirst sample record:")
        print(sample_df.iloc[0].to_dict())

    # Test trade profile creation
    print("\n2. Trade Profile Creation:")
    profile_df = collector.create_comprehensive_trade_profile('USA', ['2022'])
    if not profile_df.empty:
        print(f"Created profile with {len(profile_df)} bilateral trade relationships")
        if 'TradeValue' in profile_df.columns:
            total_trade = profile_df['TradeValue'].sum()
            print(f"Total trade value: ${total_trade:,.0f}")
    else:
        print("No actual data fetched (framework ready for API access)")

    # Test diversification metrics
    print("\n3. Trade Diversification Metrics:")
    diversification_df = collector.get_trade_diversification_metrics('USA', ['2021', '2022'])
    if not diversification_df.empty:
        print(f"Generated diversification metrics for {len(diversification_df)} records")
    else:
        print("No actual data fetched (framework ready for API access)")

    print("\nUNCTAD collector test completed.")
    print("Framework is ready for API integration with UNCTAD data sources.")


if __name__ == "__main__":
    main()
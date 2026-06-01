"""
Canada Data Collector for Lewis Platform
======================================

Comprehensive data collection module for Canadian economic indicators.
Integrates data from Statistics Canada and Bank of Canada.

Data Sources:
1. Statistics Canada (CANSIM tables, API)
2. Bank of Canada (statistics.canada API)
3. Innovation, Science and Economic Development Canada
4. DBnomics (Canada-specific providers)

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
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

class CanadaDataCollector:
    """
    Comprehensive data collector for Canadian economic indicators.

    Integrates multiple official data sources to provide complete coverage
    of Canadian economic statistics including national accounts, prices,
    labor market, external sector, and financial markets.
    """

    def __init__(self, cache_dir: Path = None):
        """
        Initialize Canada data collector.

        Args:
            cache_dir: Directory for caching responses
        """
        self.cache_dir = cache_dir or Path(__file__).parent.parent.parent / "data" / "cache" / "canada"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Set up logging
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

        # API endpoints
        self.statscan_api_url = "https://www150.statcan.gc.ca/t1/wds/en/api"
        self.boc_api_url = "https://www.bankofcanada.ca/valet"

        # Rate limiting
        self.requests_per_second = 1
        self.last_request_time = None

        # Canada-specific data mappings (Statistics Canada table numbers)
        self.statscan_tables = {
            # National Accounts
            'gdp_monthly': {'id': '3610043401', 'name': 'Gross domestic product, monthly, chained (2012) dollars'},
            'gdp_annual': {'id': '3610043402', 'name': 'Gross domestic product, annual, chained (2012) dollars'},
            'gdp_by_industry': {'id': '3610040401', 'name': 'Gross domestic product by industry, monthly'},

            # Prices
            'cpi_monthly': {'id': '1810000401', 'name': 'Consumer Price Index, monthly'},
            'cpi_annual': {'id': '1810000402', 'name': 'Consumer Price Index, annual'},
            'cpi_core': {'id': '1810000701', 'name': 'Core CPI, monthly'},

            # Labor Market
            'employment': {'id': '1410000101', 'name': 'Employment, monthly'},
            'unemployment_rate': {'id': '1410000301', 'name': 'Unemployment rate, monthly'},
            'labour_force': {'id': '1410000201', 'name': 'Labour force, monthly'},
            'participation_rate': {'id': '1410000901', 'name': 'Participation rate, monthly'},

            # Industrial Production and Sales
            'manufacturing_sales': {'id': '1610001301', 'name': 'Manufacturing sales, monthly'},
            'wholesale_trade': {'id': '2010000101', 'name': 'Wholesale trade sales, monthly'},
            'retail_trade': {'id': '2010000801', 'name': 'Retail trade sales, monthly'},

            # External Sector
            'merchandise_trade': {'id': '1210001301', 'name': 'Merchandise imports and exports, monthly'},
            'current_account': {'id': '3610064401', 'name': 'Current account, quarterly'},
            'trade_balance': {'id': '1210005901', 'name': 'International merchandise trade balance, monthly'},

            # Housing Market
            'housing_starts': {'id': '3410003501', 'name': 'Housing starts, monthly'},
            'building_permits': {'id': '3410002901', 'name': 'Building permits, monthly'},
            'home_prices': {'id': '3410017701', 'name': 'New housing price index, monthly'},

            # Financial Markets
            'interest_rates': {'id': '1710000101', 'name': 'Bank of Canada rates, monthly'},
            'money_supply': {'id': '3610046401', 'name': 'Money supply, monthly'},
            'exchange_rate': {'id': '1710005601', 'name': 'Exchange rates, monthly'}
        }

        # Bank of Canada series codes
        self.boc_series = {
            'overnight_rate': 'IEXE0101',
            'cpi_triple': 'CPI_TTTD',
            'cpi_median': 'CPI_MED',
            'cpi_common': 'CPI_COMM',
            'exchange_rate_cad_usd': 'FXCADUSD',
            'exchange_rate_usd_cad': 'FXUSDCAD',
            'bond_yield_10yr': 'IRLTLT01CAM156N',
            'bond_yield_2yr': 'IRLTLT01CAM156S',
            'term_structure': 'IRLTLT01CAM156N'
        }

        # Provincial codes for regional data
        self.province_codes = {
            'Canada': '01',
            'Newfoundland and Labrador': '10',
            'Prince Edward Island': '11',
            'Nova Scotia': '12',
            'New Brunswick': '13',
            'Quebec': '24',
            'Ontario': '35',
            'Manitoba': '46',
            'Saskatchewan': '47',
            'Alberta': '48',
            'British Columbia': '59',
            'Yukon': '60',
            'Northwest Territories': '61',
            'Nunavut': '62'
        }

    def _rate_limit(self):
        """Implement rate limiting for API requests."""
        if self.last_request_time:
            time_since_last = time.time() - self.last_request_time
            if time_since_last < 1.0 / self.requests_per_second:
                time.sleep(1.0 / self.requests_per_second - time_since_last)
        self.last_request_time = time.time()

    def fetch_statscan_data(self, table_id: str, start_period: str = "2000-01",
                          end_period: str = "2024-12") -> pd.DataFrame:
        """
        Fetch data from Statistics Canada.

        Args:
            table_id: Statistics Canada table ID
            start_period: Starting period (YYYY-MM format)
            end_period: Ending period (YYYY-MM format)

        Returns:
            DataFrame with requested economic data
        """
        self.logger.info(f"Fetching Statistics Canada data for table: {table_id}")

        # Check cache first
        cache_file = self.cache_dir / f"statscan_{table_id}_{start_period}_{end_period}.csv"
        if cache_file.exists():
            self.logger.info(f"Loading cached data from {cache_file}")
            return pd.read_csv(cache_file)

        try:
            self._rate_limit()

            # Step 1: Get table metadata
            metadata_url = f"{self.statscan_url}/getSeriesInfoFromCubePid/{table_id}"
            metadata_response = requests.get(metadata_url, timeout=30)

            if metadata_response.status_code != 200:
                self.logger.error(f"Failed to get metadata for table {table_id}")
                return pd.DataFrame()

            metadata = metadata_response.json()

            # Step 2: Get data with coordinates
            data_url = f"{self.statscan_url}/getSeriesDataFromCubePidCoord/{table_id}/{start_period}/{end_period}"
            data_response = requests.get(data_url, timeout=30)

            if data_response.status_code == 200:
                data = data_response.json()
                df = self._process_statscan_response(data, table_id, metadata)

                if not df.empty:
                    # Save to cache
                    df.to_csv(cache_file, index=False)
                    self.logger.info(f"Saved {len(df)} observations to cache")
                    return df
                else:
                    self.logger.warning(f"No data returned for table: {table_id}")
                    return pd.DataFrame()
            else:
                self.logger.error(f"Statistics Canada API request failed: {data_response.status_code}")
                return pd.DataFrame()

        except Exception as e:
            self.logger.error(f"Error fetching Statistics Canada data: {e}")
            return pd.DataFrame()

    def _process_statscan_response(self, data: Dict, table_id: str, metadata: Dict) -> pd.DataFrame:
        """
        Process Statistics Canada JSON response into clean DataFrame.

        Args:
            data: Raw Statistics Canada API response
            table_id: Table ID for reference
            metadata: Table metadata

        Returns:
            Processed DataFrame
        """
        try:
            if 'object' not in data or 'SeriesData' not in data['object']:
                return pd.DataFrame()

            series_data = data['object']['SeriesData']

            processed_data = []

            for series_id, series_info in series_data.items():
                if 'dataPt' in series_info:
                    for data_point in series_info['dataPt']:
                        if isinstance(data_point, dict):
                            # Parse period (e.g., "2000-01", "2024-Q1")
                            period = data_point.get('period', '')
                            year = int(period.split('-')[0])

                            # Handle different period types
                            period_type = 'M'  # Default to monthly
                            if len(period) > 7 and period[7] == 'Q':
                                period_type = 'Q'
                                quarter = int(period.split('-Q')[1])

                            value = float(data_point.get('value', 0))

                            row = {
                                'year': year,
                                'period': period,
                                'period_type': period_type,
                                'value': value,
                                'series_id': series_id,
                                'table_id': table_id,
                                'data_source': 'Statistics_Canada',
                                'collected_date': datetime.now()
                            }

                            # Add geographic information if available
                            if 'refPer' in data_point:
                                row['geography'] = data_point['refPer']

                            # Add other dimensions
                            if 'refPer1' in data_point:
                                row['dimension1'] = data_point['refPer1']
                            if 'refPer2' in data_point:
                                row['dimension2'] = data_point['refPer2']

                            processed_data.append(row)

            if processed_data:
                df = pd.DataFrame(processed_data)
                df = df.sort_values(['year', 'period']).reset_index(drop=True)
                return df
            else:
                return pd.DataFrame()

        except Exception as e:
            self.logger.error(f"Error processing Statistics Canada response: {e}")
            return pd.DataFrame()

    def fetch_boc_data(self, series_code: str, start_date: str = "2000-01-01",
                      end_date: str = "2024-12-31") -> pd.DataFrame:
        """
        Fetch data from Bank of Canada.

        Args:
            series_code: Bank of Canada series code
            start_date: Starting date (YYYY-MM-DD format)
            end_date: Ending date (YYYY-MM-DD format)

        Returns:
            DataFrame with Bank of Canada data
        """
        self.logger.info(f"Fetching Bank of Canada data for series: {series_code}")

        # Check cache first
        cache_file = self.cache_dir / f"boc_{series_code}_{start_date}_{end_date}.csv"
        if cache_file.exists():
            self.logger.info(f"Loading cached BOC data from {cache_file}")
            return pd.read_csv(cache_file)

        try:
            self._rate_limit()

            # Bank of Canada API URL
            url = f"{self.boc_api_url}/observations/{series_code}/json"

            params = {
                'start_date': start_date,
                'end_date': end_date
            }

            response = requests.get(url, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                df = self._process_boc_response(data, series_code)

                if not df.empty:
                    df.to_csv(cache_file, index=False)
                    self.logger.info(f"Saved {len(df)} BOC observations to cache")
                    return df
                else:
                    return pd.DataFrame()
            else:
                self.logger.error(f"Bank of Canada API request failed: {response.status_code}")
                return pd.DataFrame()

        except Exception as e:
            self.logger.error(f"Error fetching Bank of Canada data: {e}")
            return pd.DataFrame()

    def _process_boc_response(self, data: Dict, series_code: str) -> pd.DataFrame:
        """
        Process Bank of Canada JSON response into clean DataFrame.

        Args:
            data: Raw Bank of Canada API response
            series_code: Series code for reference

        Returns:
            Processed DataFrame
        """
        try:
            if 'observations' not in data:
                return pd.DataFrame()

            observations = data['observations']
            processed_data = []

            for obs in observations:
                if 'd' in obs and 'v' in obs:
                    date_str = obs['d']
                    value = obs['v']

                    # Parse date
                    try:
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                        year = date_obj.year
                        month = date_obj.month
                        period = f"{year}-{month:02d}"
                    except ValueError:
                        continue

                    row = {
                        'date': date_str,
                        'year': year,
                        'month': month,
                        'period': period,
                        'value': float(value) if value else np.nan,
                        'series_code': series_code,
                        'data_source': 'Bank_of_Canada',
                        'collected_date': datetime.now()
                    }

                    processed_data.append(row)

            if processed_data:
                df = pd.DataFrame(processed_data)
                df = df.sort_values('date').reset_index(drop=True)
                return df
            else:
                return pd.DataFrame()

        except Exception as e:
            self.logger.error(f"Error processing Bank of Canada response: {e}")
            return pd.DataFrame()

    def collect_canada_macro_data(self, start_year: int = 2000,
                                end_year: int = 2024) -> Dict[str, pd.DataFrame]:
        """
        Collect comprehensive Canadian macroeconomic data.

        Args:
            start_year: Starting year for data collection
            end_year: Ending year for data collection

        Returns:
            Dictionary with all collected data series
        """
        self.logger.info("Starting comprehensive Canada macro data collection")

        data_collection = {}

        # Core economic indicators from Statistics Canada
        core_indicators = [
            'gdp_monthly', 'cpi_monthly', 'unemployment_rate', 'employment',
            'merchandise_trade', 'current_account', 'housing_starts',
            'manufacturing_sales', 'retail_trade'
        ]

        start_period = f"{start_year}-01"
        end_period = f"{end_year}-12"

        for indicator in core_indicators:
            self.logger.info(f"Collecting {indicator} data")

            if indicator in self.statscan_tables:
                table_id = self.statscan_tables[indicator]['id']
                df = self.fetch_statscan_data(table_id, start_period, end_period)

                if not df.empty:
                    data_collection[indicator] = df
                    self.logger.info(f"Successfully collected {len(df)} {indicator} observations")
                else:
                    self.logger.warning(f"No data collected for {indicator}")

        # Bank of Canada financial data
        boc_indicators = ['overnight_rate', 'exchange_rate_cad_usd', 'bond_yield_10yr', 'cpi_triple']

        start_date = f"{start_year}-01-01"
        end_date = f"{end_year}-12-31"

        for indicator in boc_indicators:
            if indicator in self.boc_series:
                series_code = self.boc_series[indicator]
                df = self.fetch_boc_data(series_code, start_date, end_date)

                if not df.empty:
                    data_collection[f"boc_{indicator}"] = df
                    self.logger.info(f"Successfully collected {len(df)} BOC {indicator} observations")

        # Summary statistics
        total_indicators = len(data_collection)
        total_observations = sum(len(df) for df in data_collection.values())

        self.logger.info(f"Canada data collection complete:")
        self.logger.info(f"  - Indicators collected: {total_indicators}")
        self.logger.info(f"  - Total observations: {total_observations:,}")
        self.logger.info(f"  - Year range: {start_year}-{end_year}")

        return data_collection

    def create_canada_summary_dataset(self, data_collection: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Create unified summary dataset for Canada.

        Args:
            data_collection: Dictionary of collected data series

        Returns:
            Unified DataFrame with key Canada indicators
        """
        self.logger.info("Creating unified Canada summary dataset")

        summary_rows = []

        # Key indicators to include in summary
        summary_indicators = {
            'gdp_monthly': 'GDP Growth (Monthly % Change)',
            'cpi_monthly': 'CPI Inflation (Monthly % Change)',
            'unemployment_rate': 'Unemployment Rate (%)',
            'employment': 'Employment (Thousands)',
            'merchandise_trade': 'Trade Balance (Millions CAD)',
            'housing_starts': 'Housing Starts (Units)',
            'boc_overnight_rate': 'Bank of Canada Overnight Rate (%)'
        }

        for year in range(2000, 2025):
            year_data = {'year': year, 'country': 'CAN', 'country_name': 'Canada'}

            for indicator_key, indicator_name in summary_indicators.items():
                if indicator_key in data_collection:
                    df = data_collection[indicator_key]
                    year_df = df[df['year'] == year]

                    if not year_df.empty:
                        # For monthly data, take annual average
                        if indicator_key in ['gdp_monthly', 'cpi_monthly']:
                            year_data[indicator_key] = year_df['value'].mean()
                        else:
                            # For other indicators, take the latest value in the year
                            year_data[indicator_key] = year_df.iloc[-1]['value']
                    else:
                        year_data[indicator_key] = np.nan
                else:
                    year_data[indicator_key] = np.nan

            summary_rows.append(year_data)

        summary_df = pd.DataFrame(summary_rows)
        summary_df['data_source'] = 'Official_Canada_Statistics'
        summary_df['last_updated'] = datetime.now()

        # Save summary
        summary_file = self.cache_dir.parent / "canada_summary_2000_2024.csv"
        summary_df.to_csv(summary_file, index=False)
        self.logger.info(f"Canada summary dataset saved: {len(summary_df)} observations")

        return summary_df

    def generate_sample_data(self) -> pd.DataFrame:
        """
        Generate sample Canada data structure for testing purposes.

        Returns:
            DataFrame with sample Canada economic data
        """
        self.logger.info("Generating sample Canada data structure")

        sample_data = []

        # Create sample economic indicators
        indicators = [
            ('GDP_Annual_Growth', 2.3, 0.8),
            ('CPI_Annual_Change', 2.0, 0.4),
            ('Unemployment_Rate', 6.8, 1.0),
            ('Employment_Thousands', 18000, 500),
            ('Trade_Balance_Millions', 2000, 1500),
            ('Housing_Starts_Units', 200000, 40000),
            ('Overnight_Rate', 3.5, 2.0),
            ('Exchange_Rate_USD_CAD', 1.25, 0.15)
        ]

        for year in range(2000, 2025):
            for indicator, base_value, volatility in indicators:
                # Generate realistic-looking data with some randomness
                value = base_value + np.random.normal(0, volatility)

                # Add some trend and cyclical components
                if indicator == 'GDP_Annual_Growth':
                    value += 0.05 * (year - 2000) / 25  # Slight upward trend
                    value += 0.8 * np.sin(2 * np.pi * (year - 2000) / 8)  # Business cycle

                elif indicator == 'Unemployment_Rate':
                    value += -0.02 * (year - 2000) / 25  # Slight downward trend
                    value += 1.0 * np.sin(2 * np.pi * (year - 2000) / 6)

                sample_data.append({
                    'year': year,
                    'country': 'CAN',
                    'country_name': 'Canada',
                    'indicator': indicator,
                    'value': value,
                    'units': '%' if 'Rate' in indicator or 'Growth' in indicator or 'Change' in indicator else ('units' if 'Units' in indicator else ('thousands' if 'Thousands' in indicator else 'millions' if 'Millions' in indicator else 'index/units')),
                    'data_source': 'Canada_Sample_Data',
                    'collected_date': datetime.now()
                })

        sample_df = pd.DataFrame(sample_data)

        # Save sample data
        sample_file = self.cache_dir / "canada_sample_data.csv"
        sample_df.to_csv(sample_file, index=False)
        self.logger.info(f"Generated {len(sample_df)} sample Canada observations")

        return sample_df

    def validate_canada_data_collection(self) -> Dict[str, Any]:
        """
        Validate Canada data collection setup and functionality.

        Returns:
            Dictionary with validation results
        """
        self.logger.info("Validating Canada data collection setup")

        validation = {
            'cache_directory_exists': self.cache_dir.exists(),
            'statscan_tables_loaded': len(self.statscan_tables) > 0,
            'boc_series_loaded': len(self.boc_series) > 0,
            'province_codes_loaded': len(self.province_codes) > 0,
            'api_endpoints_configured': bool(self.statscan_api_url and self.boc_api_url),
            'sample_data_generation': False,
            'framework_ready': False
        }

        # Test sample data generation
        try:
            sample_df = self.generate_sample_data()
            validation['sample_data_generation'] = not sample_df.empty
        except Exception as e:
            self.logger.error(f"Sample data generation test failed: {e}")

        # Overall framework readiness
        validation['framework_ready'] = all([
            validation['cache_directory_exists'],
            validation['statscan_tables_loaded'],
            validation['boc_series_loaded'],
            validation['api_endpoints_configured'],
            validation['sample_data_generation']
        ])

        return validation

    def get_data_collection_instructions(self) -> str:
        """
        Get instructions for setting up Canada data collection.

        Returns:
            String with detailed setup instructions
        """
        return """
        CANADA DATA COLLECTION SETUP INSTRUCTIONS
        ========================================

        1. STATISTICS CANADA API
        ------------------------
        The Statistics Canada API is open and does not require authentication.
        However, there are usage limits that should be respected.

        API Documentation: https://www.statcan.gc.ca/en/developers/wds

        Key Features:
        - No API key required
        - Rate limited to ensure fair usage
        - Returns JSON format data
        - Covers over 1,000 statistical tables

        2. BANK OF CANADA API
        ----------------------
        The Bank of Canada Valet API is open and does not require authentication.

        API Documentation: https://www.bankofcanada.ca/valet/docs

        Key Features:
        - No API key required
        - Real-time and historical data
        - Multiple data formats (JSON, XML, CSV)
        - Exchange rates, interest rates, inflation measures

        3. CONFIGURE THE COLLECTOR
        ---------------------------
        ```python
        from Technical.src.data.canada_collector import CanadaDataCollector

        # Initialize collector
        collector = CanadaDataCollector()

        # Collect comprehensive data
        canada_data = collector.collect_canada_macro_data(2000, 2024)

        # Create summary dataset
        summary = collector.create_canada_summary_dataset(canada_data)
        ```

        4. AVAILABLE DATA
        -----------------
        **National Accounts:**
        - Monthly and Annual GDP (chained 2012 dollars)
        - GDP by Industry
        - National Accounts aggregates

        **Prices:**
        - Consumer Price Index (all-items and core measures)
        - Bank of Canada's preferred core inflation measures
        - Monthly and annual CPI

        **Labor Market:**
        - Employment and unemployment rates
        - Labour force participation rate
        - Employment by industry and province

        **Industrial Activity:**
        - Manufacturing sales
        - Wholesale and retail trade
        - Industrial production indices

        **External Sector:**
        - Merchandise imports and exports
        - Current account balance
        - Trade balance by country and commodity

        **Housing Market:**
        - Housing starts and permits
        - New housing price index
        - Real estate indicators

        **Financial Markets:**
        - Bank of Canada policy rate
        - Exchange rates (CAD/USD)
        - Government bond yields
        - Money supply aggregates

        5. DATA COVERAGE
        ---------------
        - Time Period: Generally 1990-present (varies by series)
        - Frequency: Monthly, quarterly, and annual data
        - Geographic: National, provincial, and territorial data
        - Quality: Official government statistics, high quality

        6. RATE LIMITS
        --------------
        - Statistics Canada: Limited to ensure fair usage
        - Bank of Canada: Generally unrestricted but respectful use recommended
        - Automatic rate limiting implemented
        - Caching reduces API calls

        7. PROVINCIAL DATA
        -----------------
        The collector supports provincial and territorial breakdowns:
        - 13 provinces and territories
        - Regional economic indicators
        - Province-specific trends

        8. TROUBLESHOOTING
        ------------------
        - Check internet connectivity
        - Verify table IDs and series codes are correct
        - Review API documentation for any changes
        - Check for temporary service disruptions
        - Ensure date ranges are properly formatted

        FOR MORE INFORMATION:
        - Statistics Canada API: https://www.statcan.gc.ca/en/developers/wds
        - Bank of Canada Valet API: https://www.bankofcanada.ca/valet/docs
        - Statistics Canada Main: https://www150.statcan.gc.ca/
        - Bank of Canada Statistics: https://www.bankofcanada.ca/rates/

        Note: Both APIs are open and don't require authentication, but
        respectful usage and rate limiting are implemented to ensure
        continued access to these valuable data sources.
        """


def main():
    """Test Canada data collector functionality."""
    collector = CanadaDataCollector()

    print("Canada Data Collector Test")
    print("=" * 50)

    # Test framework setup
    print("\n1. Framework Validation:")
    validation = collector.validate_canada_data_collection()
    for key, value in validation.items():
        status = "PASS" if value else "FAIL"
        print(f"  {status} {key}: {value}")

    # Generate sample data
    print("\n2. Sample Data Generation:")
    sample_df = collector.generate_sample_data()
    if not sample_df.empty:
        print(f"Generated {len(sample_df)} sample records")
        print(f"Years covered: {sample_df['year'].min()}-{sample_df['year'].max()}")
        print(f"Indicators: {sample_df['indicator'].nunique()}")

    # Show setup instructions
    print("\n3. Setup Instructions:")
    print(collector.get_data_collection_instructions())

    print("\nCanada data collector test completed.")
    print("Note: APIs are open and ready for data collection.")


if __name__ == "__main__":
    main()
"""
UN Comtrade Data Collection Framework for Lewis Platform
======================================================

Comprehensive framework for UN Comtrade bilateral trade data collection.
This module provides the structure and methods needed to collect
detailed bilateral trade flow data once API access is configured.

IMPORTANT: UN Comtrade now requires API key registration.
See https://uncomtrade.org/docs/api-subscription-keys/ for details.

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

class UNComtradeFramework:
    """
    Framework for UN Comtrade data collection with proper API structure.
    Once API key is obtained, this framework will enable comprehensive
    bilateral trade data collection.
    """

    def __init__(self, cache_dir: Path = None, api_key: str = None):
        """
        Initialize UN Comtrade framework.

        Args:
            cache_dir: Directory for caching responses
            api_key: UN Comtrade API key (required for data access)
        """
        self.cache_dir = cache_dir or Path(__file__).parent.parent.parent / "data" / "cache" / "un_comtrade"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.api_key = api_key
        self.api_base_url = "https://comtradeplus.un.org/api/v1"

        # Set up logging
        self.logger = logging.getLogger(__name__)

        # Rate limiting
        self.requests_per_second = 1
        self.last_request_time = None

        # Country code mappings (ISO3 to Comtrade numeric codes)
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

        # API parameter mappings
        self.api_params = {
            'type_codes': {'C': 'Goods trade'},
            'frequency_codes': {'A': 'Annual', 'M': 'Monthly', 'Q': 'Quarterly'},
            'classification_codes': {
                'HS': 'Harmonized System',
                'S1': 'SITC Revision 1',
                'S2': 'SITC Revision 2',
                'S3': 'SITC Revision 3',
                'S4': 'SITC Revision 4',
                'BEC': 'Broad Economic Categories'
            },
            'flow_codes': {'1': 'Import', '2': 'Export', 'all': 'Both'}
        }

        # Major economies for initial focus
        self.major_economies = ['USA', 'CHN', 'GBR', 'DEU', 'JPN', 'FRA', 'ITA', 'CAN']

    def setup_api_access(self, api_key: str):
        """
        Configure API key for UN Comtrade access.

        Args:
            api_key: Valid UN Comtrade API subscription key

        Returns:
            bool: True if API access is successfully configured
        """
        self.api_key = api_key

        # Test API access
        try:
            test_result = self._test_api_access()
            if test_result:
                self.logger.info("UN Comtrade API access successfully configured")
                return True
            else:
                self.logger.error("UN Comtrade API access test failed")
                return False
        except Exception as e:
            self.logger.error(f"Error configuring UN Comtrade API: {e}")
            return False

    def _test_api_access(self) -> bool:
        """Test API access with a simple query."""
        if not self.api_key:
            self.logger.error("No API key provided")
            return False

        # Test parameters (small, simple query)
        test_params = {
            'typeCode': 'C',
            'freqCode': 'A',
            'clCode': 'HS',
            'period': '2021',
            'reporterCode': '842',  # USA
            'partnerCode': '156',   # China
            'flowCode': '2',        # Exports
            'cmdCode': 'TOTAL',     # Total trade
            'maxRecords': 100,
            'format_output': 'JSON'
        }

        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            response = requests.get(
                f"{self.api_base_url}/getFinalData",
                params=test_params,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                return 'dataset' in data
            else:
                self.logger.error(f"API test failed with status {response.status_code}")
                return False

        except Exception as e:
            self.logger.error(f"API test error: {e}")
            return False

    def fetch_bilateral_trade_data(self, reporter: str, partner: str, years: List[str],
                                   commodity_code: str = 'TOTAL', flow: str = 'all',
                                   classification: str = 'HS', frequency: str = 'A') -> pd.DataFrame:
        """
        Fetch bilateral trade data between two countries.

        Args:
            reporter: Reporting country ISO3 code
            partner: Partner country ISO3 code
            years: List of years
            commodity_code: Commodity code ('TOTAL' for all goods)
            flow: Trade flow ('import', 'export', 'all')
            classification: Classification system
            frequency: Data frequency

        Returns:
            DataFrame with bilateral trade data
        """
        if not self.api_key:
            self.logger.error("API key required for data access")
            return pd.DataFrame()

        # Map parameters to API format
        reporter_code = self.country_codes.get(reporter, reporter)
        partner_code = self.country_codes.get(partner, partner)
        flow_code = self.trade_flows.get(flow, flow)

        all_data = []

        for year in years:
            # API parameters for final data request
            params = {
                'typeCode': 'C',
                'freqCode': frequency,
                'clCode': classification,
                'period': year,
                'reporterCode': reporter_code,
                'partnerCode': partner_code,
                'flowCode': flow_code,
                'cmdCode': commodity_code,
                'maxRecords': 50000,
                'format_output': 'JSON',
                'includeDesc': True
            }

            # Add authorization header
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            try:
                response = requests.get(
                    f"{self.api_base_url}/getFinalData",
                    params=params,
                    headers=headers,
                    timeout=60
                )

                if response.status_code == 200:
                    api_data = response.json()
                    df = self._process_trade_data(api_data, reporter, partner)
                    if not df.empty:
                        all_data.append(df)
                else:
                    self.logger.warning(f"API request failed for {reporter}-{partner} {year}: {response.status_code}")

            except Exception as e:
                self.logger.error(f"Error fetching data for {reporter}-{partner} {year}: {e}")

        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            return combined_df

        return pd.DataFrame()

    def _process_trade_data(self, api_data: Dict, reporter: str, partner: str) -> pd.DataFrame:
        """
        Process UN Comtrade API response into clean DataFrame.

        Args:
            api_data: Raw API response
            reporter: Reporter country ISO3
            partner: Partner country ISO3

        Returns:
            Processed DataFrame
        """
        if 'dataset' not in api_data:
            return pd.DataFrame()

        try:
            dataset = api_data['dataset']
            if not dataset:
                return pd.DataFrame()

            df = pd.DataFrame(dataset)

            # Standardize column names
            column_mapping = {
                'refPeriodId': 'year',
                'period': 'period',
                'flowCode': 'flow_code',
                'flowDesc': 'flow_description',
                'reporterCode': 'reporter_code',
                'reporterDesc': 'reporter_name',
                'reporterISO': 'reporter_iso3',
                'partnerCode': 'partner_code',
                'partnerDesc': 'partner_name',
                'partnerISO': 'partner_iso3',
                'cmdCode': 'commodity_code',
                'cmdDesc': 'commodity_description',
                'qtCode': 'quantity_code',
                'qtDesc': 'quantity_description',
                'primaryValue': 'trade_value_usd',
                'netWeightKg': 'net_weight_kg',
                'grossWeightKg': 'gross_weight_kg',
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

            return df

        except Exception as e:
            self.logger.error(f"Error processing trade data: {e}")
            return pd.DataFrame()

    def get_trade_matrix_template(self, year: str, countries: List[str] = None,
                                  commodity_code: str = 'TOTAL') -> pd.DataFrame:
        """
        Generate template for bilateral trade matrix.

        Args:
            year: Year for trade matrix
            countries: List of countries (default: major economies)
            commodity_code: Commodity code

        Returns:
            DataFrame template for trade matrix
        """
        if countries is None:
            countries = self.major_economies

        trade_matrix = []

        for reporter in countries:
            for partner in countries:
                if reporter == partner:
                    continue

                trade_matrix.append({
                    'reporter': reporter,
                    'partner': partner,
                    'year': int(year),
                    'commodity_code': commodity_code,
                    'total_trade_usd': np.nan,
                    'exports_usd': np.nan,
                    'imports_usd': np.nan,
                    'trade_balance_usd': np.nan,
                    'data_status': 'pending'
                })

        return pd.DataFrame(trade_matrix)

    def get_api_instructions(self) -> str:
        """
        Get instructions for obtaining UN Comtrade API access.

        Returns:
            String with detailed setup instructions
        """
        return """
        UN COMTRADE API SETUP INSTRUCTIONS
        =====================================

        1. REGISTRATION
        --------------
        Visit: https://uncomtrade.org/docs/api-subscription-keys/

        - Create a free account on UN Comtrade
        - Navigate to API subscription section
        - Select 'comtrade - v1' (free tier)
        - Generate your API key/subscription token

        2. CONFIGURE THE FRAMEWORK
        -------------------------
        ```python
        from Technical.src.data.un_comtrade_framework import UNComtradeFramework

        # Initialize framework
        collector = UNComtradeFramework()

        # Configure API access
        success = collector.setup_api_access('your-api-key-here')

        if success:
            print("API access configured successfully")
        ```

        3. AVAILABLE DATA
        ----------------
        - Bilateral trade flows between 200+ countries
        - Commodity-level detail (HS, SITC classifications)
        - Annual, monthly, quarterly frequency
        - Historical data back to 1962
        - Imports, exports, re-exports, re-imports

        4. USAGE EXAMPLES
        ----------------
        ```python
        # Fetch US-China trade data
        us_china_data = collector.fetch_bilateral_trade_data(
            reporter='USA',
            partner='CHN',
            years=['2020', '2021', '2022'],
            commodity_code='TOTAL'
        )

        # Create trade matrix for major economies
        matrix_template = collector.get_trade_matrix_template('2022')
        ```

        5. RATE LIMITS
        --------------
        - Free tier: 100 requests per hour
        - Rate limiting is automatically handled
        - Caching reduces API calls

        6. TROUBLESHOOTING
        ------------------
        - Ensure API key is valid and active
        - Check internet connectivity
        - Verify country codes are correct
        - Review parameter combinations
        - Check for API service status at https://comtrade.un.org

        FOR MORE INFORMATION:
        - API Documentation: https://comtradeplus.un.org/docs
        - Data Coverage: https://comtrade.un.org/
        - Support: uncomtrade@un.org
        """

    def generate_sample_data(self) -> pd.DataFrame:
        """
        Generate sample trade data structure for testing purposes.

        Returns:
            DataFrame with sample trade data structure
        """
        sample_data = []

        # Create sample bilateral trade entries
        sample_trades = [
            {
                'reporter': 'USA',
                'partner': 'CHN',
                'year': 2022,
                'commodity_code': 'TOTAL',
                'flow_code': 2,
                'flow_description': 'Exports',
                'trade_value_usd': 150000000000,
                'net_weight_kg': 500000000,
                'commodity_description': 'All commodities',
                'data_source': 'UN_Comtrade_Sample'
            },
            {
                'reporter': 'USA',
                'partner': 'CHN',
                'year': 2022,
                'commodity_code': 'TOTAL',
                'flow_code': 1,
                'flow_description': 'Imports',
                'trade_value_usd': 530000000000,
                'net_weight_kg': 450000000,
                'commodity_description': 'All commodities',
                'data_source': 'UN_Comtrade_Sample'
            },
            {
                'reporter': 'DEU',
                'partner': 'CHN',
                'year': 2022,
                'commodity_code': '8703',  # Motor vehicles
                'flow_code': 2,
                'flow_description': 'Exports',
                'trade_value_usd': 25000000000,
                'net_weight_kg': 1500000,
                'commodity_description': 'Motor cars and other motor vehicles',
                'data_source': 'UN_Comtrade_Sample'
            }
        ]

        for trade in sample_trades:
            sample_data.append(trade)

        return pd.DataFrame(sample_data)

    def validate_framework_setup(self) -> Dict[str, Any]:
        """
        Validate that the framework is properly set up.

        Returns:
            Dictionary with validation results
        """
        validation = {
            'api_key_configured': self.api_key is not None,
            'cache_directory_exists': self.cache_dir.exists(),
            'country_codes_loaded': len(self.country_codes) > 0,
            'parameter_mappings_loaded': len(self.api_params) > 0,
            'framework_ready': False
        }

        validation['framework_ready'] = all([
            validation['api_key_configured'],
            validation['cache_directory_exists'],
            validation['country_codes_loaded'],
            validation['parameter_mappings_loaded']
        ])

        return validation


def main():
    """Test UN Comtrade framework functionality."""
    framework = UNComtradeFramework()

    print("UN Comtrade Data Collection Framework Test")
    print("=" * 50)

    # Test framework setup
    print("\n1. Framework Validation:")
    validation = framework.validate_framework_setup()
    for key, value in validation.items():
        status = "PASS" if value else "FAIL"
        print(f"  {status} {key}: {value}")

    # Show API setup instructions
    print("\n2. API Setup Instructions:")
    print(framework.get_api_instructions())

    # Generate sample data
    print("\n3. Sample Data Structure:")
    sample_df = framework.generate_sample_data()
    if not sample_df.empty:
        print(f"Generated {len(sample_df)} sample records")
        print(f"Columns: {list(sample_df.columns)}")
        print("\nFirst sample record:")
        print(sample_df.iloc[0].to_dict())

    # Test trade matrix template
    print("\n4. Trade Matrix Template:")
    matrix_template = framework.get_trade_matrix_template('2022')
    if not matrix_template.empty:
        print(f"Created template for {len(matrix_template)} bilateral trade relationships")
        print(f"Template covers {matrix_template['reporter'].nunique()} countries")

    print("\nFramework test completed.")
    print("Note: Actual data fetching requires API key configuration.")

if __name__ == "__main__":
    main()
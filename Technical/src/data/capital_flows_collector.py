#!/usr/bin/env python3
"""
Capital flows Data Collector - Lewis Platform Integration
============================================================

Comprehensive capital flows data collector using the FRED API protocol.
Collects real international capital flows data from the data store FRED database
and working copies from the local data store for sophisticated analysis.

This module leverages the existing data infrastructure to collect:
- Balance of Payments data (BOPGSTB, BOPGEXP, BOPGIMP)
- Foreign Direct Investment flows
- Portfolio investment data
- International banking statistics
- Related macroeconomic indicators

Key Features:
- FRED API integration for FRED data collection
- the local data store working data integration
- Real data series discovery via data source comprehensive collector
- data source-compatible error handling and retry logic
- data source authentication and rate limiting protocols

Author: Lewis Platform
Date: 2025-10-27
Version: 1.0 - Data integration
"""

import os
import sys
import json
import pandas as pd
import numpy as np
import requests
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import time
import logging
from typing import Dict, List, Optional, Union, Tuple, Any
from dataclasses import dataclass

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Path roots (override with env vars). DATA_ROOT = where source data is read;
# OUTPUT_ROOT = where this project writes its outputs.
DATA_ROOT = Path(os.environ.get("DATA_ROOT", "data"))
OUTPUT_ROOT = Path(os.environ.get("OUTPUT_ROOT", "outputs"))
TECHNICAL_ROOT = Path(__file__).resolve().parents[2]  # repo .../Technical

@dataclass
class CapitalFlowsConfig:
    """Configuration for data source capital flows data collection."""
    start_year: int = 1992  # Start of available BOP data in the data store
    end_year: int = 2025
    frequency: str = "monthly"  # source data frequency
    api_key: str = os.environ.get("FRED_API_KEY", "")  # set via FRED_API_KEY
    base_url: str = "https://api.stlouisfed.org/fred"
    rate_limit: int = 120  # data source rate limit (requests per minute)
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: int = 30
    use_source_working_data: bool = True

class CapitalFlowsCollector:
    """
    Comprehensive capital flows data collector using FRED API protocol.

    Integrates with existing data infrastructure to collect real international
    capital flows data for sophisticated econometric analysis.
    """

    def __init__(self, config: CapitalFlowsConfig = None):
        """Initialize the data source capital flows collector."""
        self.config = config or CapitalFlowsConfig()

        # Source data paths (under DATA_ROOT)
        self.data_root = DATA_ROOT
        self.working_data_path = self.data_root / "international"
        self.fred_data_path = self.data_root / "fred"

        # Initialize collection stats
        self.stats = {
            "series_discovered": 0,
            "series_collected": 0,
            "observations_collected": 0,
            "errors": 0,
            "start_time": datetime.now()
        }

        logger.info("Capital flows Collector initialized")
        logger.info(f"API Key: {self.config.api_key[:8]}...")
        logger.info(f"Data period: {self.config.start_year}-{self.config.end_year}")
        logger.info(f"working data path: {self.working_data_path}")

    def collect_all_capital_flows_data(self) -> Dict[str, pd.DataFrame]:
        """
        Collect all capital flows data using the data store protocol.

        Returns:
            Dict[str, pd.DataFrame]: Collected capital flows datasets
        """
        logger.info("Starting comprehensive data source capital flows data collection...")

        all_data = {}

        # 0. First, check for existing data source working copies in Lewis project
        logger.info("Phase 0: Checking for existing data source working copies...")
        existing_source_data = self._collect_existing_source_data()
        if existing_source_data:
            all_data.update(existing_source_data)
            logger.info(f"[PASS] Found {len(existing_source_data)} existing data series")
        else:
            logger.info("[INFO] No existing source data found, proceeding with collection")

        # 1. Collect working data from the local data store if available
        if self.config.use_source_working_data:
            logger.info("Phase 1: Collecting working data from the local data store...")
            working_data = self._collect_source_working_data()
            all_data.update(working_data)

        # 2. Use existing data source FRED collectors if available
        logger.info("Phase 2: Using data source FRED collectors...")
        fred_data = self._collect_from_source_fred_collectors()
        all_data.update(fred_data)

        # 3. Collect additional FRED series as fallback
        if len(all_data) < 5:  # If we don't have enough data, try direct API
            logger.info("Phase 3: Collecting additional FRED series...")
            additional_data = self._collect_fred_capital_flows()
            all_data.update(additional_data)

        # 4. Enhance with related macroeconomic indicators
        logger.info("Phase 4: Collecting related macroeconomic indicators...")
        macro_data = self._collect_macro_indicators()
        all_data.update(macro_data)

        # 5. Harmonize and validate all data
        logger.info("Phase 5: Harmonizing and validating data...")
        harmonized_data = self._harmonize_data(all_data)

        self._log_collection_summary()

        logger.info(f"[OK] data source capital flows data collection completed")
        return harmonized_data

    def _collect_existing_source_data(self) -> Dict[str, pd.DataFrame]:
        """Collect existing data source working copies from Lewis project - PRIORITIZE EXISTING DATA FIRST."""
        existing_data = {}

        # Define search paths for existing data - PRIORITIZE LEWIS PROJECT DATA
        potential_paths = [
            DATA_ROOT,
            DATA_ROOT / "external",
            DATA_ROOT / "fred",
            OUTPUT_ROOT,
            TECHNICAL_ROOT / "data",
            Path("data"),
            Path("output"),
            Path("../data"),
            Path("../output")
        ]

        # Common macroeconomic and financial data files to look for
        target_files = {
            'gdp': ['GDPC1.csv', 'GDP.csv', 'real_gdp.csv', 'gdp.csv'],
            'cpi': ['CPIAUCSL.csv', 'CPI.csv', 'inflation.csv', 'cpi.csv'],
            'fedfunds': ['FEDFUNDS.csv', 'fed_funds.csv', 'fed_funds_rate.csv'],
            'unrate': ['UNRATE.csv', 'unemployment.csv', 'unemployment_rate.csv'],
            'dgs10': ['DGS10.csv', '10y_treasury.csv', 'treasury_10y.csv'],
            'dgs2': ['DGS2.csv', '2y_treasury.csv', 'treasury_2y.csv'],
            'dexuseu': ['DEXUSEU.csv', 'usd_eur.csv', 'euro_usd.csv'],
            'bopgstb': ['BOPGSTB.csv', 'trade_balance.csv', 'balance_of_trade.csv'],
            'bopgexp': ['BOPGEXP.csv', 'goods_exports.csv', 'exports.csv'],
            'bopgimp': ['BOPGIMP.csv', 'goods_imports.csv', 'imports.csv'],
            'tb6sm': ['TB6SM.csv', 'treasury_bills_6m.csv'],
            't10y2y': ['T10Y2Y.csv', '10y_minus_2y_spread.csv'],
            't10y3m': ['T10Y3M.csv', '10y_minus_3m_spread.csv']
        }

        for path in potential_paths:
            if not path.exists():
                continue

            logger.info(f"Checking {path} for existing data files...")

            # Look for CSV files that match our target data
            for csv_file in path.glob("*.csv"):
                file_stem = csv_file.stem.upper()

                # Check if this file matches any of our target categories
                for category, possible_names in target_files.items():
                    if file_stem in [name.upper() for name in possible_names]:
                        if category not in existing_data:  # Only take the first match
                            try:
                                df = pd.read_csv(csv_file)

                                # Standardize column names
                                if 'DATE' in df.columns:
                                    df = df.rename(columns={'DATE': 'date'})
                                elif 'Date' in df.columns:
                                    df = df.rename(columns={'Date': 'date'})
                                elif 'date' not in df.columns and len(df.columns) > 0:
                                    # Assume first column is date
                                    df = df.rename(columns={df.columns[0]: 'date'})

                                if 'date' in df.columns:
                                    df['date'] = pd.to_datetime(df['date'])
                                    df = df.set_index('date')

                                    # Filter by analysis period
                                    start_date = pd.to_datetime(f"{self.config.start_year}-01-01")
                                    end_date = pd.to_datetime(f"{self.config.end_year}-12-31")
                                    df = df[(df.index >= start_date) & (df.index <= end_date)]

                                    if not df.empty:
                                        existing_data[category] = df
                                        logger.info(f"[PASS] Found existing data: {category} from {csv_file.name} ({len(df)} observations)")
                                        break
                            except Exception as e:
                                logger.warning(f"Could not read {csv_file}: {e}")

        # Also check for any JSON data files that might contain FRED data
        for path in potential_paths:
            if path.exists():
                for json_file in path.glob("*.json"):
                    if "fred" in json_file.name.lower() or "series" in json_file.name.lower():
                        try:
                            with open(json_file, 'r') as f:
                                json_data = json.load(f)
                                logger.info(f"[INFO] Found JSON data file: {json_file.name}")
                        except Exception as e:
                            logger.warning(f"Could not read JSON file {json_file}: {e}")

        logger.info(f"[PASS] Collected {len(existing_data)} existing data series from Lewis project")
        return existing_data

    def _collect_from_source_fred_collectors(self) -> Dict[str, pd.DataFrame]:
        """Collect data using existing data source FRED collectors."""
        fred_data = {}

        # Try to use a local comprehensive FRED collector under DATA_ROOT
        local_collector_path = DATA_ROOT / "comprehensive_fred_collector.py"
        if local_collector_path.exists():
            try:
                logger.info("Found local comprehensive FRED collector")
                # Import and use the local collector
                sys.path.append(str(local_collector_path.parent))
                from comprehensive_fred_collector import ComprehensiveFREDCollector

                # Initialize the local collector
                collector = ComprehensiveFREDCollector(data_dir=str(DATA_ROOT / "fred_collected"))

                # Get collected data from the local store
                if hasattr(collector, 'get_collected_data'):
                    collected_data = collector.get_collected_data()
                    if collected_data:
                        # Filter for capital flows related series
                        capital_flows_series = [
                            'BOPGSTB', 'BOPGEXP', 'BOPGIMP', 'GDP', 'UNRATE',
                            'FEDFUNDS', 'CPIAUCSL', 'INDPRO'
                        ]

                        for series_id in capital_flows_series:
                            if series_id in collected_data:
                                fred_data[series_id.lower()] = collected_data[series_id]
                                logger.info(f"[PASS] Found {series_id} in local store")

            except Exception as e:
                logger.warning(f"Could not use local comprehensive FRED collector: {e}")

        return fred_data

    def _collect_source_working_data(self) -> Dict[str, pd.DataFrame]:
        """Collect working data from the local data store directory."""
        working_data = {}

        # BOP series from the data store working data
        bop_series = {
            'BOPGSTB': 'Trade Balance: Goods and Services',
            'BOPGEXP': 'Exports of Goods',
            'BOPGIMP': 'Imports of Goods'
        }

        for series_id, description in bop_series.items():
            try:
                # Try multiple file patterns
                file_patterns = [
                    f"{series_id}_Monthly_Seasonally Adjusted.csv",
                    f"{series_id}.csv",
                    f"{series_id}_monthly.csv"
                ]

                data = None
                for pattern in file_patterns:
                    file_path = self.working_data_path / pattern
                    if file_path.exists():
                        data = self._load_source_csv(file_path, series_id)
                        break

                if data is not None:
                    working_data[f'{series_id.lower()}_monthly'] = data
                    logger.info(f"[OK] Loaded {description}: {len(data)} observations")
                    self.stats["series_collected"] += 1
                else:
                    logger.warning(f"[X] {description} not found in the data store working data")

            except Exception as e:
                logger.error(f"Error loading {series_id}: {e}")
                self.stats["errors"] += 1

        return working_data

    def _collect_fred_capital_flows(self) -> Dict[str, pd.DataFrame]:
        """Collect capital flows data using the data store FRED API."""
        fred_data = {}

        # Key FRED series for capital flows analysis - UPDATED WITH CORRECT SERIES IDs
        target_series = [
            # Core Economic Indicators (these should definitely exist)
            {'id': 'GDPC1', 'name': 'Real Gross Domestic Product', 'category': 'Economic Indicators'},
            {'id': 'CPIAUCSL', 'name': 'Consumer Price Index for All Urban Consumers', 'category': 'Economic Indicators'},
            {'id': 'UNRATE', 'name': 'Unemployment Rate', 'category': 'Economic Indicators'},
            {'id': 'FEDFUNDS', 'name': 'Federal Funds Effective Rate', 'category': 'Economic Indicators'},
            {'id': 'DGS10', 'name': '10-Year Treasury Constant Maturity Rate', 'category': 'Economic Indicators'},
            {'id': 'DGS2', 'name': '2-Year Treasury Constant Maturity Rate', 'category': 'Economic Indicators'},
            {'id': 'DEXUSEU', 'name': 'U.S. / Euro Exchange Rate', 'category': 'Economic Indicators'},

            # Trade and Balance of Payments (corrected series IDs)
            {'id': 'BOPGSTB', 'name': 'Trade Balance: Goods and Services', 'category': 'Balance of Payments'},
            {'id': 'BOPGEXP', 'name': 'Exports of Goods and Services', 'category': 'Balance of Payments'},
            {'id': 'BOPGIMP', 'name': 'Imports of Goods and Services', 'category': 'Balance of Payments'},
            {'id': 'BOPLEAD', 'name': 'Net U.S. International Investment Position', 'category': 'Balance of Payments'},

            # Treasury and Foreign Holdings (more reliable series)
            {'id': 'TREAST', 'name': 'U.S. Treasury Securities Held by Foreign Residents', 'category': 'Portfolio Investment'},
            {'id': 'FYGFD', 'name': 'U.S. Financial Assets, Liabilities, and Net Worth', 'category': 'Portfolio Investment'},
            {'id': 'EXCSRESNW', 'name': 'Excess Reserves of Depository Institutions', 'category': 'Monetary Indicators'},

            # Additional Financial Indicators
            {'id': 'TB6SM', 'name': '6-Month Treasury Bill: Secondary Market Rate', 'category': 'Economic Indicators'},
            {'id': 'T10Y2Y', 'name': '10-Year Treasury Constant Maturity Minus 2-Year', 'category': 'Economic Indicators'},
            {'id': 'T10Y3M', 'name': '10-Year Treasury Constant Maturity Minus 3-Month', 'category': 'Economic Indicators'},
            {'id': 'DFF', 'name': 'Daily Federal Funds Rate', 'category': 'Economic Indicators'},
            {'id': 'DGS10', 'name': 'Market Yield on U.S. Treasury Securities at 10-Year Constant Maturity', 'category': 'Economic Indicators'},
            {'id': 'DEXUSEU', 'name': 'U.S. / Euro Exchange Rate', 'category': 'Exchange Rates'},
            {'id': 'DEXJPUS', 'name': 'U.S. / Japan Exchange Rate', 'category': 'Exchange Rates'},
            {'id': 'DEXCHUS', 'name': 'U.S. / China Exchange Rate', 'category': 'Exchange Rates'}
        ]

        for series_info in target_series:
            try:
                data = self._collect_fred_series(series_info)
                if data is not None and not data.empty:
                    fred_data[series_info['id'].lower()] = data
                    logger.info(f"[OK] Collected {series_info['name']}: {len(data)} observations")
                    self.stats["series_collected"] += 1
                    self.stats["observations_collected"] += len(data)
                else:
                    logger.warning(f"[X] {series_info['name']} not available")

            except Exception as e:
                logger.error(f"Error collecting {series_info['id']}: {e}")
                self.stats["errors"] += 1

        return fred_data

    def _collect_macro_indicators(self) -> Dict[str, pd.DataFrame]:
        """Collect additional macroeconomic indicators for analysis."""
        macro_data = {}

        # Additional macro series
        additional_series = [
            {'id': 'CPIAUCSL', 'name': 'Consumer Price Index for All Urban Consumers'},
            {'id': 'PCEPI', 'name': 'Personal Consumption Expenditures Price Index'},
            {'id': 'INDPRO', 'name': 'Industrial Production Index'},
            {'id': 'HOUST', 'name': 'Housing Starts: Total'},
            {'id': 'UMCSENT', 'name': 'University of Michigan Consumer Sentiment'},
            {'id': 'VIXCLS', 'name': 'CBOE Volatility Index: VIX'},
            {'id': 'DGS2', 'name': 'Market Yield on U.S. Treasury Securities at 2-Year Constant Maturity'},
            {'id': 'DGS30', 'name': 'Market Yield on U.S. Treasury Securities at 30-Year Constant Maturity'},
            {'id': 'DEXUSUK', 'name': 'U.S. / U.K. Exchange Rate'},
            {'id': 'DEXCAUS', 'name': 'U.S. / Canada Exchange Rate'}
        ]

        for series_info in additional_series:
            try:
                data = self._collect_fred_series(series_info)
                if data is not None and not data.empty:
                    macro_data[series_info['id'].lower()] = data
                    logger.info(f"[OK] Collected {series_info['name']}: {len(data)} observations")

            except Exception as e:
                logger.warning(f"Could not collect {series_info['id']}: {e}")

        return macro_data

    def _collect_fred_series(self, series_info: Dict[str, str]) -> Optional[pd.DataFrame]:
        """Collect a single FRED series using FRED API protocol."""
        series_id = series_info['id']

        try:
            # FRED API request for series observations
            params = {
                'api_key': self.config.api_key,
                'series_id': series_id,
                'observation_start': f'{self.config.start_year}-01-01',
                'observation_end': f'{self.config.end_year}-12-31',
                'frequency': self.config.frequency,
                'file_type': 'json'
            }

            url = f"{self.config.base_url}/series/observations"

            for attempt in range(self.config.max_retries + 1):
                try:
                    response = requests.get(url, params=params, timeout=self.config.timeout)

                    if response.status_code == 200:
                        data = response.json()

                        if 'observations' in data and data['observations']:
                            # Convert to DataFrame
                            df = pd.DataFrame(data['observations'])
                            df['date'] = pd.to_datetime(df['date'])
                            df['value'] = pd.to_numeric(df['value'], errors='coerce')
                            df = df.dropna(subset=['value'])
                            df = df.set_index('date')
                            df = df.sort_index()

                            # Convert series_id to lowercase for consistency
                            df.columns = ['value']
                            df = df.rename(columns={'value': series_id.lower()})

                            return df
                        else:
                            logger.warning(f"No observations found for {series_id}")
                            return None

                    elif response.status_code == 429:  # Rate limit exceeded
                        wait_time = 60 / self.config.rate_limit * (attempt + 1)
                        logger.warning(f"Rate limit exceeded for {series_id}, waiting {wait_time:.1f}s")
                        time.sleep(wait_time)
                        continue

                    else:
                        logger.error(f"FRED API error for {series_id}: {response.status_code}")
                        return None

                except requests.exceptions.RequestException as e:
                    if attempt < self.config.max_retries:
                        logger.warning(f"Retry {attempt + 1} for {series_id}: {e}")
                        time.sleep(self.config.retry_delay * (2 ** attempt))
                    else:
                        logger.error(f"Failed to collect {series_id} after {self.config.max_retries} attempts")
                        return None

        except Exception as e:
            logger.error(f"Error collecting FRED series {series_id}: {e}")
            return None

        return None

    def _load_source_csv(self, file_path: Path, series_id: str) -> pd.DataFrame:
        """Load CSV data from the data store working directory."""
        try:
            # Read data source CSV file
            df = pd.read_csv(file_path)

            # data source CSV format typically has 'DATE' and 'VALUE' columns
            if 'DATE' in df.columns and 'VALUE' in df.columns:
                df['date'] = pd.to_datetime(df['DATE'])
                df['value'] = pd.to_numeric(df['VALUE'], errors='coerce')
                df = df.dropna(subset=['value'])
                df = df.set_index('date')
                df = df.sort_index()

                # Keep only date range
                start_date = pd.to_datetime(f'{self.config.start_year}-01-01')
                end_date = pd.to_datetime(f'{self.config.end_year}-12-31')
                df = df[(df.index >= start_date) & (df.index <= end_date)]

                # Rename value column to series_id
                df = df.rename(columns={'value': series_id.lower()})
                df = df[[series_id.lower()]]  # Keep only the value column

                return df
            else:
                logger.warning(f"Unexpected column format in {file_path}")
                return None

        except Exception as e:
            logger.error(f"Error loading data source CSV {file_path}: {e}")
            return None

    def _harmonize_data(self, all_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Harmonize all collected data to consistent format and frequency."""
        harmonized_data = {}

        # Create common date range
        start_date = pd.to_datetime(f'{self.config.start_year}-01-01')
        end_date = pd.to_datetime(f'{self.config.end_year}-12-31')

        # Process each dataset
        for series_id, data in all_data.items():
            if data is None or data.empty:
                continue

            try:
                # Ensure date index
                if not isinstance(data.index, pd.DatetimeIndex):
                    continue

                # Filter date range
                data = data[(data.index >= start_date) & (data.index <= end_date)]

                # Convert to quarterly frequency if needed (for analysis consistency)
                if self.config.frequency == 'monthly':
                    # Keep monthly but ensure consistent frequency
                    data = data.resample('M').mean()
                else:
                    # Convert to quarterly
                    data = data.resample('Q').mean()

                # Remove any remaining NaN values
                data = data.dropna()

                if not data.empty:
                    harmonized_data[series_id] = data

            except Exception as e:
                logger.warning(f"Error harmonizing {series_id}: {e}")

        logger.info(f"Harmonized {len(harmonized_data)} data series")
        return harmonized_data

    def _log_collection_summary(self):
        """Log summary of collection results."""
        elapsed_time = (datetime.now() - self.stats["start_time"]).total_seconds()

        logger.info("=" * 60)
        logger.info("SOURCE CAPITAL FLOWS DATA COLLECTION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Series Discovered: {self.stats['series_discovered']}")
        logger.info(f"Series Collected: {self.stats['series_collected']}")
        logger.info(f"Observations Collected: {self.stats['observations_collected']}")
        logger.info(f"Errors Encountered: {self.stats['errors']}")
        logger.info(f"Collection Time: {elapsed_time:.2f} seconds")
        logger.info(f"Data Period: {self.config.start_year}-{self.config.end_year}")
        logger.info("=" * 60)

    def get_collection_metadata(self) -> Dict[str, Any]:
        """Get metadata about the collected data."""
        return {
            'collection_date': datetime.now().isoformat(),
            'config': {
                'start_year': self.config.start_year,
                'end_year': self.config.end_year,
                'frequency': self.config.frequency,
                'api_source': 'data source FRED API',
                'working_data_used': self.config.use_source_working_data
            },
            'statistics': self.stats,
            'output_roots': {
                'working_data': str(self.working_data_path),
                'fred_data': str(self.fred_data_path)
            }
        }

# Utility function for easy use
def collect_capital_flows_data(start_year: int = 1992,
                                    end_year: int = 2025,
                                    use_working_data: bool = True) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:
    """
    Utility function to collect data source capital flows data.

    Args:
        start_year: Start year for data collection
        end_year: End year for data collection
        use_working_data: Whether to use working data

    Returns:
        Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]: Collected data and metadata
    """
    config = CapitalFlowsConfig(
        start_year=start_year,
        end_year=end_year,
        use_source_working_data=use_working_data
    )

    collector = CapitalFlowsCollector(config)
    data = collector.collect_all_capital_flows_data()
    metadata = collector.get_collection_metadata()

    return data, metadata

if __name__ == "__main__":
    # Demonstration
    logger.info("Demonstrating Capital flows Data Collector...")

    # Collect data using the data store protocol
    data, metadata = collect_capital_flows_data(
        start_year=1992,
        end_year=2025,
        use_working_data=True
    )

    print(f"\ndata source Data Collection Results:")
    print(f"Series Collected: {len(data)}")
    print(f"Total Observations: {sum(len(df) for df in data.values())}")

    print(f"\nCollected Series:")
    for series_id, df in data.items():
        print(f"  {series_id}: {len(df)} observations ({df.index.min().date()} to {df.index.max().date()})")

    print(f"\nCollection Metadata:")
    print(json.dumps(metadata, indent=2, default=str))
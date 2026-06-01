#!/usr/bin/env python3
"""
FRED Z.1 Data Collector - Lewis Platform Integration
==========================================================

Enhanced Z.1 Flow of Funds data collector using the FRED API protocol.
Integrates with existing data source FRED API management system for comprehensive
Flow of Funds analysis with Balance of Payments integration.

This module bridges the Lewis Platform with the data infrastructure,
providing seamless access to Federal Reserve Z.1 data through the established
FRED API protocols and authentication systems.

Key Features:
- FRED API integration for FRED data collection
- Complete Z.1 Flow of Funds coverage
- Balance of Payments data integration
- data source compatibility
- Advanced error handling and retry logic
- performance monitoring integration

Author: Lewis Platform
Date: 2025-10-27
Version: 1.0
"""

import os
import sys
import json
import pandas as pd
import numpy as np
import requests
import time
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
import logging
from dataclasses import dataclass, asdict

# Data root: where source data lives. Override with the DATA_ROOT env var.
DATA_ROOT = Path(os.environ.get("DATA_ROOT", "data"))

# Optionally use a local fred_api_manager module if one is available on the
# import path. If not, the direct FRED REST API is used (see fallback below).
try:
    from fred_api_manager import FREDAPIManager, FREDConfig  # type: ignore
    FRED_MANAGER_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("Local FRED API manager imported")
except ImportError as e:
    FRED_MANAGER_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.info("No local FRED API manager; using direct FRED REST API")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class Z1Config:
    """Configuration for data source Z.1 data collection."""
    use_fred_manager: bool = True
    data_dir: str = str(DATA_ROOT / "FRED_Z1")
    fallback_api_key: Optional[str] = None
    cache_dir: str = "cache/z1"
    db_path: str = "data/flow_z1_database.db"
    start_year: int = 1950
    end_year: Optional[int] = None
    include_bop: bool = True
    validate_data: bool = True
    rate_limit_delay: float = 0.5
    max_retries: int = 3

@dataclass
class Z1SeriesInfo:
    """Container for Z.1 series information."""
    series_id: str
    title: str
    column_name: str
    units: str
    frequency: str
    seasonal_adjustment: str
    sector: str
    component: str
    subcomponent: str
    data_type: str

class FREDZ1Collector:
    """
    FRED Z.1 Flow of Funds data collector.

    Uses the FRED API protocol for seamless integration with the existing
    data infrastructure while providing Lewis Platform compatibility.
    """

    def __init__(self, config: Z1Config = None):
        """Initialize FRED Z.1 collector."""
        self.config = config or Z1Config()

        # Initialize FRED API manager if available
        if self.config.use_fred_manager and FRED_MANAGER_AVAILABLE:
            try:
                self.fred_manager = self._init_fred_manager()
                self.api_source = "manager"
                logger.info("Using local FRED API manager for data collection")
            except Exception as e:
                logger.error(f"Failed to initialize FRED API manager: {e}")
                self.fred_manager = None
                self.api_source = "fallback"
        else:
            self.fred_manager = None
            self.api_source = "fallback"

        # Initialize database
        self._init_database()

        # Z.1 series mappings
        self.z1_series = self._get_z1_series_mappings()

        # Balance of Payments series
        self.bop_series = self._get_bop_series_mappings()

        # Create cache directory
        Path(self.config.cache_dir).mkdir(parents=True, exist_ok=True)

        logger.info(f"FRED Z.1 Collector initialized (API source: {self.api_source})")

    def _init_fred_manager(self) -> Any:
        """Initialize the local FRED API manager."""
        try:
            # Try to get API key from the source store centralized system
            api_key = self._get_manager_api_key()

            if not api_key:
                raise ValueError("No FRED API key available (set FRED_API_KEY)")

            # Initialize FRED API manager
            fred_config = FREDConfig(
                api_key=api_key,
                rate_limit=120,
                max_retries=self.config.max_retries,
                retry_delay=self.config.rate_limit_delay,
                timeout=30
            )

            api_manager = FREDAPIManager(
                api_key=api_key,
                data_dir=self.config.data_dir
            )

            return api_manager

        except Exception as e:
            logger.error(f"Error initializing FRED API manager: {e}")
            raise

    def _get_manager_api_key(self) -> Optional[str]:
        """Get the FRED API key from the environment."""
        try:
            # Prefer FRED_API_KEY; also accept a key file under DATA_ROOT.
            key_paths = [
                os.environ.get('FRED_API_KEY'),
                str(DATA_ROOT / "fred_api_key.txt"),
                os.path.expanduser("~/.fred/fred_api_key.txt"),
            ]

            for key_path in key_paths:
                if key_path is None:
                    continue

                path = Path(key_path)
                if path.exists():
                    if path.suffix == '.json':
                        with open(path, 'r') as f:
                            data = json.load(f)
                            return data.get('fred_api_key')
                    else:
                        with open(path, 'r') as f:
                            return f.read().strip()

            env_key = os.getenv('FRED_API_KEY')
            if env_key:
                return env_key

            logger.warning("No FRED API key found (set FRED_API_KEY)")
            return None

        except Exception as e:
            logger.error(f"Error getting FRED API key: {e}")
            return None

    def _init_database(self):
        """Initialize SQLite database for Z.1 data storage."""
        try:
            db_file = Path(self.config.db_path)
            db_file.parent.mkdir(parents=True, exist_ok=True)

            with sqlite3.connect(self.config.db_path) as conn:
                # Main Z.1 data table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS flow_z1_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        series_id TEXT NOT NULL,
                        date TEXT NOT NULL,
                        value REAL NOT NULL,
                        sector TEXT,
                        component TEXT,
                        subcomponent TEXT,
                        data_type TEXT,
                        units TEXT,
                        frequency TEXT,
                        api_source TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(series_id, date)
                    )
                ''')

                # Series metadata table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS flow_z1_series_metadata (
                        series_id TEXT PRIMARY KEY,
                        title TEXT,
                        units TEXT,
                        frequency TEXT,
                        seasonal_adjustment TEXT,
                        sector TEXT,
                        component TEXT,
                        subcomponent TEXT,
                        data_type TEXT,
                        api_source TEXT,
                        last_updated TEXT,
                        observation_start TEXT,
                        observation_end TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Balance of Payments data table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS flow_bop_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        series_id TEXT NOT NULL,
                        date TEXT NOT NULL,
                        value REAL NOT NULL,
                        account TEXT,
                        subaccount TEXT,
                        component TEXT,
                        units TEXT,
                        frequency TEXT,
                        api_source TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(series_id, date)
                    )
                ''')

                # Create indexes for performance
                conn.execute('CREATE INDEX IF NOT EXISTS idx_flow_z1_series_date ON flow_z1_data(series_id, date)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_flow_z1_sector ON flow_z1_data(sector, component)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_flow_bop_series_date ON flow_bop_data(series_id, date)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_flow_api_source ON flow_z1_data(api_source)')

                conn.commit()

            logger.info("data source Z.1 database initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize data source Z.1 database: {e}")
            raise

    def _get_z1_series_mappings(self) -> Dict[str, Dict[str, Z1SeriesInfo]]:
        """Get comprehensive Z.1 series mappings with data source integration."""
        return {
            # Household Sector
            "household": {
                "total_assets": Z1SeriesInfo(
                    series_id="FA1562150055.Q",
                    title="Households and Nonprofit Organizations; Total Assets",
                    column_name="household_total_assets",
                    units="Billions of Dollars",
                    frequency="Quarterly",
                    seasonal_adjustment="Seasonally Adjusted Annual Rate",
                    sector="household",
                    component="balance_sheet",
                    subcomponent="assets",
                    data_type="flow_of_funds"
                ),
                "total_liabilities": Z1SeriesInfo(
                    series_id="FA1562150056.Q",
                    title="Households and Nonprofit Organizations; Total Liabilities",
                    column_name="household_total_liabilities",
                    units="Billions of Dollars",
                    frequency="Quarterly",
                    seasonal_adjustment="Seasonally Adjusted Annual Rate",
                    sector="household",
                    component="balance_sheet",
                    subcomponent="liabilities",
                    data_type="flow_of_funds"
                ),
                "net_worth": Z1SeriesInfo(
                    series_id="TNWBSHNO",
                    title="Households and Nonprofit Organizations; Net Worth",
                    column_name="household_net_worth",
                    units="Billions of Dollars",
                    frequency="Quarterly",
                    seasonal_adjustment="Seasonally Adjusted Annual Rate",
                    sector="household",
                    component="balance_sheet",
                    subcomponent="net_worth",
                    data_type="flow_of_funds"
                ),
                "real_estate_assets": Z1SeriesInfo(
                    series_id="FA1562150013.Q",
                    title="Households and Nonprofit Organizations; Real Estate Assets",
                    column_name="household_real_estate",
                    units="Billions of Dollars",
                    frequency="Quarterly",
                    seasonal_adjustment="Seasonally Adjusted Annual Rate",
                    sector="household",
                    component="assets",
                    subcomponent="real_estate",
                    data_type="flow_of_funds"
                ),
                "financial_assets": Z1SeriesInfo(
                    series_id="FA1562150033.Q",
                    title="Households and Nonprofit Organizations; Financial Assets",
                    column_name="household_financial_assets",
                    units="Billions of Dollars",
                    frequency="Quarterly",
                    seasonal_adjustment="Seasonally Adjusted Annual Rate",
                    sector="household",
                    component="assets",
                    subcomponent="financial",
                    data_type="flow_of_funds"
                ),
                "mortgage_debt": Z1SeriesInfo(
                    series_id="MORTGAGE15US",
                    title="Households; Mortgage Debt",
                    column_name="household_mortgage_debt",
                    units="Billions of Dollars",
                    frequency="Quarterly",
                    seasonal_adjustment="Seasonally Adjusted Annual Rate",
                    sector="household",
                    component="liabilities",
                    subcomponent="mortgage",
                    data_type="flow_of_funds"
                ),
                "consumer_credit": Z1SeriesInfo(
                    series_id="CCBAL",
                    title="Households; Consumer Credit",
                    column_name="household_consumer_credit",
                    units="Billions of Dollars",
                    frequency="Quarterly",
                    seasonal_adjustment="Seasonally Adjusted Annual Rate",
                    sector="household",
                    component="liabilities",
                    subcomponent="consumer_credit",
                    data_type="flow_of_funds"
                )
            },

            # Non-financial Corporate Sector
            "nonfinancial_corporate": {
                "total_assets": Z1SeriesInfo(
                    series_id="FA1562140055.Q",
                    title="Nonfinancial Corporate Business; Total Assets",
                    column_name="corporate_total_assets",
                    units="Billions of Dollars",
                    frequency="Quarterly",
                    seasonal_adjustment="Seasonally Adjusted Annual Rate",
                    sector="nonfinancial_corporate",
                    component="balance_sheet",
                    subcomponent="assets",
                    data_type="flow_of_funds"
                ),
                "total_liabilities": Z1SeriesInfo(
                    series_id="FA1562140056.Q",
                    title="Nonfinancial Corporate Business; Total Liabilities",
                    column_name="corporate_total_liabilities",
                    units="Billions of Dollars",
                    frequency="Quarterly",
                    seasonal_adjustment="Seasonally Adjusted Annual Rate",
                    sector="nonfinancial_corporate",
                    component="balance_sheet",
                    subcomponent="liabilities",
                    data_type="flow_of_funds"
                ),
                "net_worth": Z1SeriesInfo(
                    series_id="TNWBSNFCB",
                    title="Nonfinancial Corporate Business; Net Worth",
                    column_name="corporate_net_worth",
                    units="Billions of Dollars",
                    frequency="Quarterly",
                    seasonal_adjustment="Seasonally Adjusted Annual Rate",
                    sector="nonfinancial_corporate",
                    component="balance_sheet",
                    subcomponent="net_worth",
                    data_type="flow_of_funds"
                ),
                "cash_and_deposits": Z1SeriesInfo(
                    series_id="FA1562140035.Q",
                    title="Nonfinancial Corporate Business; Cash and Deposits",
                    column_name="corporate_cash_deposits",
                    units="Billions of Dollars",
                    frequency="Quarterly",
                    seasonal_adjustment="Seasonally Adjusted Annual Rate",
                    sector="nonfinancial_corporate",
                    component="assets",
                    subcomponent="cash",
                    data_type="flow_of_funds"
                ),
                "fixed_assets": Z1SeriesInfo(
                    series_id="FA1562140013.Q",
                    title="Nonfinancial Corporate Business; Fixed Assets",
                    column_name="corporate_fixed_assets",
                    units="Billions of Dollars",
                    frequency="Quarterly",
                    seasonal_adjustment="Seasonally Adjusted Annual Rate",
                    sector="nonfinancial_corporate",
                    component="assets",
                    subcomponent="fixed",
                    data_type="flow_of_funds"
                )
            },

            # Financial Sector
            "financial": {
                "total_assets": Z1SeriesInfo(
                    series_id="FA1562240055.Q",
                    title="Financial Business; Total Assets",
                    column_name="financial_total_assets",
                    units="Billions of Dollars",
                    frequency="Quarterly",
                    seasonal_adjustment="Seasonally Adjusted Annual Rate",
                    sector="financial",
                    component="balance_sheet",
                    subcomponent="assets",
                    data_type="flow_of_funds"
                ),
                "total_liabilities": Z1SeriesInfo(
                    series_id="FA1562240056.Q",
                    title="Financial Business; Total Liabilities",
                    column_name="financial_total_liabilities",
                    units="Billions of Dollars",
                    frequency="Quarterly",
                    seasonal_adjustment="Seasonally Adjusted Annual Rate",
                    sector="financial",
                    component="balance_sheet",
                    subcomponent="liabilities",
                    data_type="flow_of_funds"
                ),
                "net_worth": Z1SeriesInfo(
                    series_id="TNWBSFB",
                    title="Financial Business; Net Worth",
                    column_name="financial_net_worth",
                    units="Billions of Dollars",
                    frequency="Quarterly",
                    seasonal_adjustment="Seasonally Adjusted Annual Rate",
                    sector="financial",
                    component="balance_sheet",
                    subcomponent="net_worth",
                    data_type="flow_of_funds"
                ),
                "bank_credit": Z1SeriesInfo(
                    series_id="LOANINV",
                    title="Bank Credit, All Commercial Banks",
                    column_name="financial_bank_credit",
                    units="Billions of Dollars",
                    frequency="Quarterly",
                    seasonal_adjustment="Seasonally Adjusted Annual Rate",
                    sector="financial",
                    component="credit",
                    subcomponent="bank",
                    data_type="flow_of_funds"
                )
            },

            # Government Sector
            "government": {
                "federal_total_assets": Z1SeriesInfo(
                    series_id="FA1562330055.Q",
                    title="Federal Government; Total Assets",
                    column_name="govt_federal_assets",
                    units="Billions of Dollars",
                    frequency="Quarterly",
                    seasonal_adjustment="Seasonally Adjusted Annual Rate",
                    sector="government",
                    component="assets",
                    subcomponent="federal",
                    data_type="flow_of_funds"
                ),
                "federal_total_liabilities": Z1SeriesInfo(
                    series_id="FA1562330056.Q",
                    title="Federal Government; Total Liabilities",
                    column_name="govt_federal_liabilities",
                    units="Billions of Dollars",
                    frequency="Quarterly",
                    seasonal_adjustment="Seasonally Adjusted Annual Rate",
                    sector="government",
                    component="liabilities",
                    subcomponent="federal",
                    data_type="flow_of_funds"
                ),
                "federal_debt": Z1SeriesInfo(
                    series_id="GFDEBTN",
                    title="Federal Debt: Total Public Debt",
                    column_name="govt_federal_debt",
                    units="Billions of Dollars",
                    frequency="Quarterly",
                    seasonal_adjustment="Seasonally Adjusted Annual Rate",
                    sector="government",
                    component="debt",
                    subcomponent="federal",
                    data_type="flow_of_funds"
                )
            },

            # Rest of World (International)
            "rest_of_world": {
                "us_assets_abroad": Z1SeriesInfo(
                    series_id="FA1562660035.Q",
                    title="Rest of World; U.S. Assets Abroad",
                    column_name="row_us_assets_abroad",
                    units="Billions of Dollars",
                    frequency="Quarterly",
                    seasonal_adjustment="Seasonally Adjusted Annual Rate",
                    sector="rest_of_world",
                    component="assets",
                    subcomponent="us_abroad",
                    data_type="flow_of_funds"
                ),
                "foreign_assets_in_us": Z1SeriesInfo(
                    series_id="FA1562660036.Q",
                    title="Rest of World; Foreign Assets in U.S.",
                    column_name="row_foreign_assets_us",
                    units="Billions of Dollars",
                    frequency="Quarterly",
                    seasonal_adjustment="Seasonally Adjusted Annual Rate",
                    sector="rest_of_world",
                    component="assets",
                    subcomponent="foreign_us",
                    data_type="flow_of_funds"
                ),
                "net_foreign_assets": Z1SeriesInfo(
                    series_id="TNWBSROW",
                    title="Rest of World; Net Foreign Assets",
                    column_name="row_net_foreign_assets",
                    units="Billions of Dollars",
                    frequency="Quarterly",
                    seasonal_adjustment="Seasonally Adjusted Annual Rate",
                    sector="rest_of_world",
                    component="net_position",
                    subcomponent="foreign",
                    data_type="flow_of_funds"
                )
            }
        }

    def _get_bop_series_mappings(self) -> Dict[str, Dict[str, Z1SeriesInfo]]:
        """Get Balance of Payments series mappings."""
        return {
            "current_account": {
                "trade_balance": Z1SeriesInfo(
                    series_id="BOPGSTB",
                    title="Trade Balance: Goods and Services",
                    column_name="bop_trade_balance",
                    units="Billions of Dollars",
                    frequency="Quarterly",
                    seasonal_adjustment="Seasonally Adjusted Annual Rate",
                    sector="external",
                    component="current_account",
                    subcomponent="trade",
                    data_type="balance_of_payments"
                ),
                "primary_income": Z1SeriesInfo(
                    series_id="BOPPI",
                    title="Primary Income",
                    column_name="bop_primary_income",
                    units="Billions of Dollars",
                    frequency="Quarterly",
                    seasonal_adjustment="Seasonally Adjusted Annual Rate",
                    sector="external",
                    component="current_account",
                    subcomponent="primary_income",
                    data_type="balance_of_payments"
                )
            },
            "financial_account": {
                "direct_investment": Z1SeriesInfo(
                    series_id="BOPFDI",
                    title="Direct Investment",
                    column_name="bop_direct_investment",
                    units="Billions of Dollars",
                    frequency="Quarterly",
                    seasonal_adjustment="Seasonally Adjusted Annual Rate",
                    sector="external",
                    component="financial_account",
                    subcomponent="direct_investment",
                    data_type="balance_of_payments"
                ),
                "portfolio_investment": Z1SeriesInfo(
                    series_id="BOPFPI",
                    title="Portfolio Investment",
                    column_name="bop_portfolio_investment",
                    units="Billions of Dollars",
                    frequency="Quarterly",
                    seasonal_adjustment="Seasonally Adjusted Annual Rate",
                    sector="external",
                    component="financial_account",
                    subcomponent="portfolio",
                    data_type="balance_of_payments"
                )
            }
        }

    def collect_fred_series(self, series_info: Z1SeriesInfo, start_date: str = None,
                           end_date: str = None) -> Optional[pd.DataFrame]:
        """
        Collect data series using FRED API or fallback.

        Args:
            series_info: Series information object
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            DataFrame with date and value columns
        """
        try:
            if self.api_source == "manager" and self.fred_manager:
                return self._collect_with_manager(series_info, start_date, end_date)
            else:
                return self._collect_with_fallback_api(series_info, start_date, end_date)

        except Exception as e:
            logger.error(f"Error collecting series {series_info.series_id}: {e}")
            return None

    def _collect_with_manager(self, series_info: Z1SeriesInfo, start_date: str = None,
                              end_date: str = None) -> Optional[pd.DataFrame]:
        """Collect data using the local FRED API manager."""
        try:
            # Use FRED API manager to collect data
            start_date = start_date or f"{self.config.start_year}-01-01"
            end_date = end_date or f"{datetime.now().year}-12-31"

            # FRED API call (implementation depends on FRED API manager interface)
            params = {
                "series_id": series_info.series_id,
                "observation_start": start_date,
                "observation_end": end_date,
                "frequency": series_info.frequency.lower(),
                "aggregation_method": "avg" if series_info.seasonal_adjustment == "Seasonally Adjusted Annual Rate" else "eop"
            }

            # Make API call through data source manager
            response = self.fred_manager.get_series_data(series_info.series_id, params)

            if response and not response.empty:
                response['date'] = pd.to_datetime(response['date'])
                response['value'] = pd.to_numeric(response['value'], errors='coerce')
                response = response.dropna(subset=['value'])
                return response[['date', 'value']]

            logger.warning(f"No data returned from FRED API for series {series_info.series_id}")
            return None

        except Exception as e:
            logger.error(f"Error with FRED API for series {series_info.series_id}: {e}")
            return None

    def _collect_with_fallback_api(self, series_info: Z1SeriesInfo, start_date: str = None,
                                 end_date: str = None) -> Optional[pd.DataFrame]:
        """Collect data using fallback FRED API."""
        try:
            # Use fallback API key
            api_key = self.config.fallback_api_key or os.environ.get("FRED_API_KEY")

            if not api_key:
                logger.warning(f"No valid API key available for series {series_info.series_id}")
                return None

            base_url = "https://api.stlouisfed.org/fred/series/observations"

            params = {
                "series_id": series_info.series_id,
                "api_key": api_key,
                "file_type": "json",
                "observation_start": start_date or f"{self.config.start_year}-01-01",
                "observation_end": end_date or f"{datetime.now().year}-12-31",
                "frequency": "q"  # Quarterly
            }

            response = requests.get(base_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if 'observations' in data:
                df = pd.DataFrame(data['observations'])
                df['date'] = pd.to_datetime(df['date'])
                df['value'] = pd.to_numeric(df['value'], errors='coerce')
                df = df.dropna(subset=['value'])
                return df[['date', 'value']]

            logger.warning(f"No observations returned for series {series_info.series_id}")
            return None

        except Exception as e:
            logger.error(f"Error with fallback API for series {series_info.series_id}: {e}")
            return None

    def collect_all_z1_data(self) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Collect all Z.1 data for all sectors using FRED API.

        Returns:
            Nested dictionary with structure: {sector: {component: DataFrame}}
        """
        logger.info("Starting data source Z.1 data collection...")

        collected_data = {}
        total_series = sum(len(components) for components in self.z1_series.values())
        collected_count = 0

        for sector, components in self.z1_series.items():
            logger.info(f"Collecting data for sector: {sector}")
            sector_data = {}

            for component_name, series_info in components.items():
                logger.info(f"  Collecting component: {component_name} ({series_info.series_id})")

                # Check if data already exists in database
                if self._series_exists_in_db(series_info.series_id):
                    logger.info(f"    Series {series_info.series_id} already in database")
                    sector_data[component_name] = self._get_series_from_db(series_info.series_id)
                    collected_count += 1
                    continue

                # Collect from API
                df = self.collect_fred_series(series_info)

                if df is not None and not df.empty:
                    # Store in database
                    self._store_series_in_db(series_info, df)

                    sector_data[component_name] = df
                    collected_count += 1
                    logger.info(f"    Successfully collected {len(df)} observations")
                else:
                    logger.warning(f"    Failed to collect {component_name}")

                # Rate limiting
                time.sleep(self.config.rate_limit_delay)

            if sector_data:
                collected_data[sector] = sector_data

        logger.info(f"data source Z.1 data collection completed. Collected {collected_count}/{total_series} series")
        return collected_data

    def collect_bop_data(self) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Collect Balance of Payments data using FRED API.

        Returns:
            Nested dictionary with BOP data structure
        """
        if not self.config.include_bop:
            return {}

        logger.info("Starting BOP data collection...")

        collected_data = {}

        for account, components in self.bop_series.items():
            logger.info(f"Collecting BOP account: {account}")
            account_data = {}

            for component_name, series_info in components.items():
                logger.info(f"  Collecting component: {component_name}")

                df = self.collect_fred_series(series_info)

                if df is not None and not df.empty:
                    # Store in BOP database
                    self._store_bop_series_in_db(series_info, df)

                    account_data[component_name] = df
                    logger.info(f"    Successfully collected {len(df)} observations")
                else:
                    logger.warning(f"    Failed to collect {component_name}")

                # Rate limiting
                time.sleep(self.config.rate_limit_delay)

            if account_data:
                collected_data[account] = account_data

        logger.info(f"BOP data collection completed. Collected data for {len(collected_data)} accounts")
        return collected_data

    def _series_exists_in_db(self, series_id: str) -> bool:
        """Check if series exists in database."""
        try:
            with sqlite3.connect(self.config.db_path) as conn:
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM flow_z1_data WHERE series_id = ?",
                    (series_id,)
                )
                return cursor.fetchone()[0] > 0
        except Exception as e:
            logger.error(f"Error checking series existence: {e}")
            return False

    def _get_series_from_db(self, series_id: str) -> pd.DataFrame:
        """Get series data from database."""
        try:
            with sqlite3.connect(self.config.db_path) as conn:
                df = pd.read_sql_query(
                    "SELECT date, value FROM flow_z1_data WHERE series_id = ? ORDER BY date",
                    conn,
                    params=(series_id,)
                )
                df['date'] = pd.to_datetime(df['date'])
                return df
        except Exception as e:
            logger.error(f"Error getting series from database: {e}")
            return pd.DataFrame()

    def _store_series_in_db(self, series_info: Z1SeriesInfo, df: pd.DataFrame):
        """Store series data in database."""
        try:
            with sqlite3.connect(self.config.db_path) as conn:
                # Store metadata
                conn.execute('''
                    INSERT OR REPLACE INTO flow_z1_series_metadata
                    (series_id, title, units, frequency, seasonal_adjustment,
                     sector, component, subcomponent, data_type, api_source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    series_info.series_id,
                    series_info.title,
                    series_info.units,
                    series_info.frequency,
                    series_info.seasonal_adjustment,
                    series_info.sector,
                    series_info.component,
                    series_info.subcomponent,
                    series_info.data_type,
                    self.api_source
                ))

                # Store data
                for _, row in df.iterrows():
                    conn.execute('''
                        INSERT OR REPLACE INTO flow_z1_data
                        (series_id, date, value, sector, component, subcomponent,
                         data_type, units, frequency, api_source)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        series_info.series_id,
                        row['date'].strftime('%Y-%m-%d'),
                        float(row['value']),
                        series_info.sector,
                        series_info.component,
                        series_info.subcomponent,
                        series_info.data_type,
                        series_info.units,
                        series_info.frequency,
                        self.api_source
                    ))

                conn.commit()

        except Exception as e:
            logger.error(f"Error storing series in database: {e}")

    def _store_bop_series_in_db(self, series_info: Z1SeriesInfo, df: pd.DataFrame):
        """Store Balance of Payments series data in database."""
        try:
            with sqlite3.connect(self.config.db_path) as conn:
                for _, row in df.iterrows():
                    conn.execute('''
                        INSERT OR REPLACE INTO flow_bop_data
                        (series_id, date, value, account, subaccount, component,
                         units, frequency, api_source)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        series_info.series_id,
                        row['date'].strftime('%Y-%m-%d'),
                        float(row['value']),
                        series_info.sector,
                        series_info.component,
                        series_info.subcomponent,
                        series_info.units,
                        series_info.frequency,
                        self.api_source
                    ))

                conn.commit()

        except Exception as e:
            logger.error(f"Error storing BOP series in database: {e}")

    def get_z1_data(self, sector: str = None, component: str = None,
                   start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Get Z.1 data with optional filtering.

        Args:
            sector: Filter by sector
            component: Filter by component
            start_date: Start date filter
            end_date: End date filter

        Returns:
            DataFrame with requested data
        """
        try:
            with sqlite3.connect(self.config.db_path) as conn:
                query = "SELECT * FROM flow_z1_data WHERE 1=1"
                params = []

                if sector:
                    query += " AND sector = ?"
                    params.append(sector)

                if component:
                    query += " AND component = ?"
                    params.append(component)

                if start_date:
                    query += " AND date >= ?"
                    params.append(start_date)

                if end_date:
                    query += " AND date <= ?"
                    params.append(end_date)

                query += " ORDER BY sector, component, date"

                df = pd.read_sql_query(query, conn, params=params)
                df['date'] = pd.to_datetime(df['date'])

                return df

        except Exception as e:
            logger.error(f"Error getting Z.1 data: {e}")
            return pd.DataFrame()

    def get_bop_data(self, account: str = None, component: str = None,
                    start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Get Balance of Payments data with optional filtering.

        Args:
            account: Filter by account
            component: Filter by component
            start_date: Start date filter
            end_date: End date filter

        Returns:
            DataFrame with requested data
        """
        try:
            with sqlite3.connect(self.config.db_path) as conn:
                query = "SELECT * FROM flow_bop_data WHERE 1=1"
                params = []

                if account:
                    query += " AND account = ?"
                    params.append(account)

                if component:
                    query += " AND subaccount = ?"
                    params.append(component)

                if start_date:
                    query += " AND date >= ?"
                    params.append(start_date)

                if end_date:
                    query += " AND date <= ?"
                    params.append(end_date)

                query += " ORDER BY account, subaccount, date"

                df = pd.read_sql_query(query, conn, params=params)
                df['date'] = pd.to_datetime(df['date'])

                return df

        except Exception as e:
            logger.error(f"Error getting BOP data: {e}")
            return pd.DataFrame()

    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary of collected data."""
        try:
            with sqlite3.connect(self.config.db_path) as conn:
                # Z.1 data summary
                z1_summary = conn.execute('''
                    SELECT
                        COUNT(DISTINCT series_id) as total_series,
                        COUNT(*) as total_observations,
                        MIN(date) as earliest_date,
                        MAX(date) as latest_date,
                        COUNT(DISTINCT sector) as sectors_covered,
                        COUNT(DISTINCT component) as components_covered,
                        api_source
                    FROM flow_z1_data
                    GROUP BY api_source
                ''').fetchall()

                # BOP data summary
                bop_summary = conn.execute('''
                    SELECT
                        COUNT(DISTINCT series_id) as total_series,
                        COUNT(*) as total_observations,
                        MIN(date) as earliest_date,
                        MAX(date) as latest_date,
                        COUNT(DISTINCT account) as accounts_covered,
                        api_source
                    FROM flow_bop_data
                    GROUP BY api_source
                ''').fetchall()

                return {
                    'z1_data': {
                        'by_api_source': [
                            {
                                'api_source': row[6],
                                'total_series': row[0],
                                'total_observations': row[1],
                                'earliest_date': row[2],
                                'latest_date': row[3],
                                'sectors_covered': row[4],
                                'components_covered': row[5]
                            }
                            for row in z1_summary
                        ]
                    },
                    'bop_data': {
                        'by_api_source': [
                            {
                                'api_source': row[5],
                                'total_series': row[0],
                                'total_observations': row[1],
                                'earliest_date': row[2],
                                'latest_date': row[3],
                                'accounts_covered': row[4]
                            }
                            for row in bop_summary
                        ]
                    },
                    'api_source': self.api_source
                }

        except Exception as e:
            logger.error(f"Error getting data summary: {e}")
            return {}

    def export_data(self, output_path: str, format: str = 'csv') -> bool:
        """
        Export collected data to file.

        Args:
            output_path: Output file path
            format: Export format ('csv', 'excel', 'json')

        Returns:
            True if export successful, False otherwise
        """
        try:
            # Get all data
            z1_df = self.get_z1_data()
            bop_df = self.get_bop_data()

            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            if format.lower() == 'csv':
                # Export Z.1 data
                z1_output = output_file.parent / f"{output_file.stem}_flow_z1_data.csv"
                z1_df.to_csv(z1_output, index=False)

                # Export BOP data
                if not bop_df.empty:
                    bop_output = output_file.parent / f"{output_file.stem}_flow_bop_data.csv"
                    bop_df.to_csv(bop_output, index=False)

            elif format.lower() == 'excel':
                with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                    z1_df.to_excel(writer, sheet_name='Z1_Data', index=False)

                    if not bop_df.empty:
                        bop_df.to_excel(writer, sheet_name='BOP_Data', index=False)

                    # Add summary sheet
                    summary = self.get_data_summary()
                    summary_df = pd.DataFrame([summary])
                    summary_df.to_excel(writer, sheet_name='Summary', index=False)

            elif format.lower() == 'json':
                export_data = {
                    'z1_data': z1_df.to_dict('records') if not z1_df.empty else [],
                    'bop_data': bop_df.to_dict('records') if not bop_df.empty else [],
                    'summary': self.get_data_summary(),
                    'export_timestamp': datetime.now().isoformat(),
                    'api_source': self.api_source
                }

                with open(output_path, 'w') as f:
                    json.dump(export_data, f, indent=2, default=str)

            logger.info(f"data source Z.1 data exported to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return False

    def close(self):
        """Close connections and clean up resources."""
        try:
            if hasattr(self, 'fred_manager') and self.fred_manager:
                # Close the FRED API manager if it has a close method
                if hasattr(self.fred_manager, 'close'):
                    self.fred_manager.close()
            logger.info("FRED Z.1 Collector closed")
        except Exception as e:
            logger.error(f"Error closing collector: {e}")

# Main execution function
def collect_z1_data(start_year: int = 1950, use_fred_manager: bool = True) -> FREDZ1Collector:
    """
    Main function to collect Z.1 data using FRED API protocol.

    Args:
        start_year: Starting year for data collection
        use_robin_api: Whether to use FRED API (falls back to direct API if unavailable)

    Returns:
        Initialized data source Z.1 collector with collected data
    """
    config = Z1Config(
        use_fred_manager=use_fred_manager,
        start_year=start_year,
        include_bop=True,
        validate_data=True,
        rate_limit_delay=0.5,
        max_retries=3
    )

    collector = FREDZ1Collector(config)

    # Collect all data
    logger.info("Starting data source Z.1 data collection...")

    # Collect Z.1 data
    z1_data = collector.collect_all_z1_data()

    # Collect BOP data if requested
    if config.include_bop:
        bop_data = collector.collect_bop_data()

    # Print summary
    summary = collector.get_data_summary()
    logger.info("data source Z.1 data collection completed successfully!")
    logger.info(f"API Source: {summary.get('api_source', 'unknown')}")

    if 'z1_data' in summary and 'by_api_source' in summary['z1_data']:
        for source_data in summary['z1_data']['by_api_source']:
            logger.info(f"Z.1 Data ({source_data['api_source']}): {source_data['total_observations']} observations across {source_data['total_series']} series")

    if 'bop_data' in summary and 'by_api_source' in summary['bop_data']:
        for source_data in summary['bop_data']['by_api_source']:
            logger.info(f"BOP Data ({source_data['api_source']}): {source_data['total_observations']} observations across {source_data['total_series']} series")

    return collector

if __name__ == "__main__":
    # Example usage
    collector = collect_z1_data(start_year=1950, use_fred_manager=True)

    # Export data
    collector.export_data("output/fred_z1_data.xlsx", format="excel")

    collector.close()
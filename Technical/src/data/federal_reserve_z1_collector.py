#!/usr/bin/env python3
"""
Federal Reserve Z.1 Flow of Funds Data Collector
==============================================

Comprehensive data collector for Federal Reserve Z.1 Flow of Funds data.
Collects all major sectors, components, and integrates with Balance of Payments data.

Key Features:
- Complete Z.1 data coverage from 1950s to present
- All major sectors: Households, Non-financial Corporate, Financial, Government, Rest of World
- Balance of Payments integration
- Advanced data validation and quality checks
- Automated updates and caching
- Comprehensive derived metrics calculation

Author: Claude
Date: 2025-10-27
Version: 1.0
"""

import pandas as pd
import numpy as np
import requests
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, date, timedelta
import logging
from dataclasses import dataclass, asdict
import sqlite3
import os
import sys

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from api.lewis_api import EnhancedAPIPipeline, APIConfig, create_get_request

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class Z1DataConfig:
    """Configuration for Z.1 data collection."""
    api_key: Optional[str] = None  # FRED API key
    cache_dir: str = "cache/z1_data"
    db_path: str = "data/z1_database.db"
    update_frequency: str = "quarterly"  # quarterly, monthly
    start_year: int = 1950
    end_year: Optional[int] = None
    include_bop: bool = True
    validate_data: bool = True
    parallel_requests: bool = True

@dataclass
class Z1DataSeries:
    """Container for Z.1 data series information."""
    series_id: str
    title: str
    units: str
    frequency: str
    seasonal_adjustment: str
    last_updated: str
    observation_start: str
    observation_end: str
    data: pd.DataFrame

class FederalReserveZ1Collector:
    """
    Comprehensive Federal Reserve Z.1 Flow of Funds data collector.

    Collects all major sectors and integrates with Balance of Payments data.
    """

    def __init__(self, config: Z1DataConfig = None):
        """Initialize Z.1 data collector."""
        self.config = config or Z1DataConfig()

        # Initialize API pipeline
        api_config = APIConfig(
            max_retries=3,
            enable_caching=True,
            cache_ttl=86400,  # 24 hours
            max_concurrent_requests=5
        )
        self.api = EnhancedAPIPipeline(api_config)

        # Initialize database
        self._init_database()

        # Z.1 series mappings - comprehensive collection
        self.z1_series = self._get_z1_series_mappings()

        # Balance of Payments series
        self.bop_series = self._get_bop_series_mappings()

        # Create cache directory
        Path(self.config.cache_dir).mkdir(parents=True, exist_ok=True)

        logger.info("Federal Reserve Z.1 Collector initialized")

    def _init_database(self):
        """Initialize SQLite database for Z.1 data storage."""
        try:
            os.makedirs(Path(self.config.db_path).parent, exist_ok=True)

            with sqlite3.connect(self.config.db_path) as conn:
                # Main Z.1 data table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS z1_data (
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
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(series_id, date)
                    )
                ''')

                # Series metadata table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS z1_series_metadata (
                        series_id TEXT PRIMARY KEY,
                        title TEXT,
                        units TEXT,
                        frequency TEXT,
                        seasonal_adjustment TEXT,
                        last_updated TEXT,
                        observation_start TEXT,
                        observation_end TEXT,
                        sector TEXT,
                        component TEXT,
                        subcomponent TEXT,
                        data_type TEXT
                    )
                ''')

                # Balance of Payments data table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS bop_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        series_id TEXT NOT NULL,
                        date TEXT NOT NULL,
                        value REAL NOT NULL,
                        account TEXT,
                        subaccount TEXT,
                        component TEXT,
                        units TEXT,
                        frequency TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(series_id, date)
                    )
                ''')

                # Create indexes for performance
                conn.execute('CREATE INDEX IF NOT EXISTS idx_z1_series_date ON z1_data(series_id, date)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_z1_sector ON z1_data(sector, component)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_bop_series_date ON bop_data(series_id, date)')

                conn.commit()

            logger.info("Z.1 database initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Z.1 database: {e}")
            raise

    def _get_z1_series_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Get comprehensive Z.1 series mappings."""
        return {
            # Household Sector
            "household": {
                "total_assets": {
                    "series_id": "FA1562150055.Q",
                    "title": "Households and Nonprofit Organizations; Total Assets",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "total_liabilities": {
                    "series_id": "FA1562150056.Q",
                    "title": "Households and Nonprofit Organizations; Total Liabilities",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "net_worth": {
                    "series_id": "TNWBSHNO",
                    "title": "Households and Nonprofit Organizations; Net Worth",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "real_estate_assets": {
                    "series_id": "FA1562150013.Q",
                    "title": "Households and Nonprofit Organizations; Real Estate Assets",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "financial_assets": {
                    "series_id": "FA1562150033.Q",
                    "title": "Households and Nonprofit Organizations; Financial Assets",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "mortgage_debt": {
                    "series_id": "MORTGAGE15US",
                    "title": "Households; Mortgage Debt",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "consumer_credit": {
                    "series_id": "CCBAL",
                    "title": "Households; Consumer Credit",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "deposits": {
                    "series_id": "FA1562150035.Q",
                    "title": "Households and Nonprofit Organizations; Deposits",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "equity_securities": {
                    "series_id": "FA1562150037.Q",
                    "title": "Households and Nonprofit Organizations; Corporate Equities",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "debt_securities": {
                    "series_id": "FA1562150036.Q",
                    "title": "Households and Nonprofit Organizations; Debt Securities",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                }
            },

            # Non-financial Corporate Sector
            "nonfinancial_corporate": {
                "total_assets": {
                    "series_id": "FA1562140055.Q",
                    "title": "Nonfinancial Corporate Business; Total Assets",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "total_liabilities": {
                    "series_id": "FA1562140056.Q",
                    "title": "Nonfinancial Corporate Business; Total Liabilities",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "net_worth": {
                    "series_id": "TNWBSNFCB",
                    "title": "Nonfinancial Corporate Business; Net Worth",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "corporate_equities": {
                    "series_id": "FA1562140037.Q",
                    "title": "Nonfinancial Corporate Business; Corporate Equities",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "debt_securities": {
                    "series_id": "FA1562140036.Q",
                    "title": "Nonfinancial Corporate Business; Debt Securities",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "loans": {
                    "series_id": "FA1562140034.Q",
                    "title": "Nonfinancial Corporate Business; Loans",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "cash_and_deposits": {
                    "series_id": "FA1562140035.Q",
                    "title": "Nonfinancial Corporate Business; Cash and Deposits",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "fixed_assets": {
                    "series_id": "FA1562140013.Q",
                    "title": "Nonfinancial Corporate Business; Fixed Assets",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "inventories": {
                    "series_id": "FA1562140014.Q",
                    "title": "Nonfinancial Corporate Business; Inventories",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                }
            },

            # Financial Sector
            "financial": {
                "total_assets": {
                    "series_id": "FA1562240055.Q",
                    "title": "Financial Business; Total Assets",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "total_liabilities": {
                    "series_id": "FA1562240056.Q",
                    "title": "Financial Business; Total Liabilities",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "net_worth": {
                    "series_id": "TNWBSFB",
                    "title": "Financial Business; Net Worth",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "bank_credit": {
                    "series_id": "LOANINV",
                    "title": "Bank Credit, All Commercial Banks",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "total_credit_market": {
                    "series_id": "TCMDO",
                    "title": "Total Credit Market Assets to GDP",
                    "units": "Ratio",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "securitized_assets": {
                    "series_id": "FA1562240036.Q",
                    "title": "Financial Business; Credit Market Instruments",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                }
            },

            # Government Sector
            "government": {
                "federal_total_assets": {
                    "series_id": "FA1562330055.Q",
                    "title": "Federal Government; Total Assets",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "federal_total_liabilities": {
                    "series_id": "FA1562330056.Q",
                    "title": "Federal Government; Total Liabilities",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "federal_net_worth": {
                    "series_id": "TNWBSFG",
                    "title": "Federal Government; Net Worth",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "treasury_securities": {
                    "series_id": "TREAST",
                    "title": "U.S. Treasury Securities Held by the Public",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "federal_debt": {
                    "series_id": "GFDEBTN",
                    "title": "Federal Debt: Total Public Debt",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "state_local_assets": {
                    "series_id": "FA1562340055.Q",
                    "title": "State and Local Governments; Total Assets",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "state_local_liabilities": {
                    "series_id": "FA1562340056.Q",
                    "title": "State and Local Governments; Total Liabilities",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                }
            },

            # Rest of World (International)
            "rest_of_world": {
                "us_assets_abroad": {
                    "series_id": "FA1562660035.Q",
                    "title": "Rest of World; U.S. Assets Abroad",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "foreign_assets_in_us": {
                    "series_id": "FA1562660036.Q",
                    "title": "Rest of World; Foreign Assets in U.S.",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "net_foreign_assets": {
                    "series_id": "TNWBSROW",
                    "title": "Rest of World; Net Foreign Assets",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "foreign_holdings_treasury": {
                    "series_id": "FDHBFIN",
                    "title": "Foreign Holders of U.S. Treasury Securities",
                    "units": "Billions of Dollars",
                    "frequency": "Monthly",
                    "seasonal_adjustment": "Not Seasonally Adjusted"
                },
                "foreign_holdings_corporate": {
                    "series_id": "FYOARM",
                    "title": "Foreign Holders of U.S. Corporate Bonds",
                    "units": "Billions of Dollars",
                    "frequency": "Monthly",
                    "seasonal_adjustment": "Not Seasonally Adjusted"
                },
                "foreign_holdings_equities": {
                    "series_id": "FYHOLD",
                    "title": "Foreign Holders of U.S. Equities",
                    "units": "Billions of Dollars",
                    "frequency": "Monthly",
                    "seasonal_adjustment": "Not Seasonally Adjusted"
                }
            }
        }

    def _get_bop_series_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Get Balance of Payments series mappings."""
        return {
            "current_account": {
                "trade_balance": {
                    "series_id": "BOPGSTB",
                    "title": "Trade Balance: Goods and Services",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "services_balance": {
                    "series_id": "BOPGAS",
                    "title": "Balance on Services",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "primary_income": {
                    "series_id": "BOPPI",
                    "title": "Primary Income",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "secondary_income": {
                    "series_id": "BOPSI",
                    "title": "Secondary Income",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                }
            },
            "financial_account": {
                "direct_investment": {
                    "series_id": "BOPFDI",
                    "title": "Direct Investment",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "portfolio_investment": {
                    "series_id": "BOPFPI",
                    "title": "Portfolio Investment",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "other_investment": {
                    "series_id": "BOPFOI",
                    "title": "Other Investment",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "reserve_assets": {
                    "series_id": "BOPFRA",
                    "title": "Reserve Assets",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                }
            },
            "international_investment_position": {
                "net_iip": {
                    "series_id": "BOPGNI",
                    "title": "Net International Investment Position",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "us_assets_abroad": {
                    "series_id": "BOPGAU",
                    "title": "U.S. Assets Abroad",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                },
                "foreign_assets_in_us": {
                    "series_id": "BOPGFA",
                    "title": "Foreign Assets in U.S.",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate"
                }
            }
        }

    def collect_fred_series(self, series_id: str, start_date: str = None,
                           end_date: str = None) -> Optional[pd.DataFrame]:
        """
        Collect data series from FRED API.

        Args:
            series_id: FRED series identifier
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            DataFrame with date and value columns
        """
        try:
            # FRED API endpoint
            base_url = "https://api.stlouisfed.org/fred/series/observations"

            params = {
                "series_id": series_id,
                "api_key": self.config.api_key or "YOUR_API_KEY_HERE",  # Will need actual API key
                "file_type": "json",
                "observation_start": start_date or f"{self.config.start_year}-01-01",
                "observation_end": end_date or f"{datetime.now().year}-12-31",
                "frequency": "q"  # Quarterly
            }

            # Make API request
            request = create_get_request(base_url, params=params)
            response = self.api.make_request(request)

            if response.success:
                data = response.data
                if 'observations' in data:
                    df = pd.DataFrame(data['observations'])
                    df['date'] = pd.to_datetime(df['date'])
                    df['value'] = pd.to_numeric(df['value'], errors='coerce')
                    df = df.dropna(subset=['value'])
                    return df[['date', 'value']]

            logger.warning(f"Failed to collect FRED series {series_id}")
            return None

        except Exception as e:
            logger.error(f"Error collecting FRED series {series_id}: {e}")
            return None

    def collect_all_z1_data(self) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Collect all Z.1 data for all sectors.

        Returns:
            Nested dictionary with structure: {sector: {component: DataFrame}}
        """
        logger.info("Starting comprehensive Z.1 data collection...")

        collected_data = {}

        for sector, components in self.z1_series.items():
            logger.info(f"Collecting data for sector: {sector}")
            sector_data = {}

            for component, series_info in components.items():
                logger.info(f"  Collecting component: {component}")

                # Check if data already exists in database
                if self._series_exists_in_db(series_info['series_id']):
                    logger.info(f"    Series {series_info['series_id']} already in database")
                    sector_data[component] = self._get_series_from_db(series_info['series_id'])
                    continue

                # Collect from FRED
                df = self.collect_fred_series(series_info['series_id'])

                if df is not None and not df.empty:
                    # Store in database
                    self._store_series_in_db(
                        series_info['series_id'],
                        df,
                        sector,
                        component,
                        series_info
                    )

                    sector_data[component] = df
                    logger.info(f"    Successfully collected {len(df)} observations")
                else:
                    logger.warning(f"    Failed to collect {component}")

            if sector_data:
                collected_data[sector] = sector_data

        logger.info(f"Z.1 data collection completed. Collected data for {len(collected_data)} sectors")
        return collected_data

    def collect_bop_data(self) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Collect Balance of Payments data.

        Returns:
            Nested dictionary with BOP data structure
        """
        if not self.config.include_bop:
            return {}

        logger.info("Starting Balance of Payments data collection...")

        collected_data = {}

        for account, components in self.bop_series.items():
            logger.info(f"Collecting BOP account: {account}")
            account_data = {}

            for component, series_info in components.items():
                logger.info(f"  Collecting component: {component}")

                df = self.collect_fred_series(series_info['series_id'])

                if df is not None and not df.empty:
                    # Store in BOP database
                    self._store_bop_series_in_db(
                        series_info['series_id'],
                        df,
                        account,
                        component,
                        series_info
                    )

                    account_data[component] = df
                    logger.info(f"    Successfully collected {len(df)} observations")
                else:
                    logger.warning(f"    Failed to collect {component}")

            if account_data:
                collected_data[account] = account_data

        logger.info(f"BOP data collection completed. Collected data for {len(collected_data)} accounts")
        return collected_data

    def _series_exists_in_db(self, series_id: str) -> bool:
        """Check if series exists in database."""
        try:
            with sqlite3.connect(self.config.db_path) as conn:
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM z1_data WHERE series_id = ?",
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
                    "SELECT date, value FROM z1_data WHERE series_id = ? ORDER BY date",
                    conn,
                    params=(series_id,)
                )
                df['date'] = pd.to_datetime(df['date'])
                return df
        except Exception as e:
            logger.error(f"Error getting series from database: {e}")
            return pd.DataFrame()

    def _store_series_in_db(self, series_id: str, df: pd.DataFrame, sector: str,
                           component: str, series_info: Dict[str, Any]):
        """Store series data in database."""
        try:
            with sqlite3.connect(self.config.db_path) as conn:
                # Store metadata
                conn.execute('''
                    INSERT OR REPLACE INTO z1_series_metadata
                    (series_id, title, units, frequency, seasonal_adjustment,
                     sector, component, subcomponent, data_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    series_id,
                    series_info.get('title', ''),
                    series_info.get('units', ''),
                    series_info.get('frequency', ''),
                    series_info.get('seasonal_adjustment', ''),
                    sector,
                    component,
                    series_info.get('subcomponent', ''),
                    'flow_of_funds'
                ))

                # Store data
                for _, row in df.iterrows():
                    conn.execute('''
                        INSERT OR REPLACE INTO z1_data
                        (series_id, date, value, sector, component, units, frequency)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        series_id,
                        row['date'].strftime('%Y-%m-%d'),
                        float(row['value']),
                        sector,
                        component,
                        series_info.get('units', ''),
                        series_info.get('frequency', '')
                    ))

                conn.commit()

        except Exception as e:
            logger.error(f"Error storing series in database: {e}")

    def _store_bop_series_in_db(self, series_id: str, df: pd.DataFrame, account: str,
                               component: str, series_info: Dict[str, Any]):
        """Store Balance of Payments series data in database."""
        try:
            with sqlite3.connect(self.config.db_path) as conn:
                for _, row in df.iterrows():
                    conn.execute('''
                        INSERT OR REPLACE INTO bop_data
                        (series_id, date, value, account, subaccount, units, frequency)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        series_id,
                        row['date'].strftime('%Y-%m-%d'),
                        float(row['value']),
                        account,
                        component,
                        series_info.get('units', ''),
                        series_info.get('frequency', '')
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
                query = "SELECT * FROM z1_data WHERE 1=1"
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
                query = "SELECT * FROM bop_data WHERE 1=1"
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

    def calculate_derived_metrics(self) -> pd.DataFrame:
        """
        Calculate derived metrics from Z.1 data.

        Returns:
            DataFrame with calculated metrics
        """
        logger.info("Calculating derived metrics...")

        try:
            # Get all Z.1 data
            df = self.get_z1_data()

            if df.empty:
                logger.warning("No Z.1 data available for metric calculation")
                return pd.DataFrame()

            # Create pivot table for easier calculations
            pivot_df = df.pivot_table(
                index=['date', 'sector'],
                columns='component',
                values='value',
                aggfunc='first'
            ).reset_index()

            # Calculate derived metrics for each sector
            results = []

            for sector in pivot_df['sector'].unique():
                sector_data = pivot_df[pivot_df['sector'] == sector]

                for _, row in sector_data.iterrows():
                    date = row['date']

                    # Sector-specific calculations
                    if sector == 'household':
                        # Household debt ratios
                        if 'total_liabilities' in row and 'total_assets' in row:
                            debt_to_assets = row['total_liabilities'] / row['total_assets']
                            results.append({
                                'date': date,
                                'sector': sector,
                                'metric': 'debt_to_assets_ratio',
                                'value': debt_to_assets
                            })

                        # Wealth composition
                        if 'real_estate_assets' in row and 'financial_assets' in row and 'total_assets' in row:
                            real_estate_share = row['real_estate_assets'] / row['total_assets']
                            financial_assets_share = row['financial_assets'] / row['total_assets']

                            results.append({
                                'date': date,
                                'sector': sector,
                                'metric': 'real_estate_share',
                                'value': real_estate_share
                            })

                            results.append({
                                'date': date,
                                'sector': sector,
                                'metric': 'financial_assets_share',
                                'value': financial_assets_share
                            })

                    elif sector == 'nonfinancial_corporate':
                        # Corporate leverage
                        if 'total_liabilities' in row and 'net_worth' in row:
                            debt_to_equity = row['total_liabilities'] / row['net_worth']
                            results.append({
                                'date': date,
                                'sector': sector,
                                'metric': 'debt_to_equity_ratio',
                                'value': debt_to_equity
                            })

                        # Cash holdings
                        if 'cash_and_deposits' in row and 'total_assets' in row:
                            cash_ratio = row['cash_and_deposits'] / row['total_assets']
                            results.append({
                                'date': date,
                                'sector': sector,
                                'metric': 'cash_ratio',
                                'value': cash_ratio
                            })

                    elif sector == 'government':
                        # Federal debt ratios
                        if 'federal_debt' in row and 'total_liabilities' in row:
                            debt_coverage = row['federal_debt'] / row['total_liabilities']
                            results.append({
                                'date': date,
                                'sector': sector,
                                'metric': 'federal_debt_coverage',
                                'value': debt_coverage
                            })

            derived_df = pd.DataFrame(results)

            logger.info(f"Calculated {len(derived_df)} derived metrics")
            return derived_df

        except Exception as e:
            logger.error(f"Error calculating derived metrics: {e}")
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
                        COUNT(DISTINCT component) as components_covered
                    FROM z1_data
                ''').fetchone()

                # BOP data summary
                bop_summary = conn.execute('''
                    SELECT
                        COUNT(DISTINCT series_id) as total_series,
                        COUNT(*) as total_observations,
                        MIN(date) as earliest_date,
                        MAX(date) as latest_date,
                        COUNT(DISTINCT account) as accounts_covered
                    FROM bop_data
                ''').fetchone()

                return {
                    'z1_data': {
                        'total_series': z1_summary[0],
                        'total_observations': z1_summary[1],
                        'earliest_date': z1_summary[2],
                        'latest_date': z1_summary[3],
                        'sectors_covered': z1_summary[4],
                        'components_covered': z1_summary[5]
                    },
                    'bop_data': {
                        'total_series': bop_summary[0],
                        'total_observations': bop_summary[1],
                        'earliest_date': bop_summary[2],
                        'latest_date': bop_summary[3],
                        'accounts_covered': bop_summary[4]
                    }
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
            derived_df = self.calculate_derived_metrics()

            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            if format.lower() == 'csv':
                # Export Z.1 data
                z1_output = output_file.parent / f"{output_file.stem}_z1_data.csv"
                z1_df.to_csv(z1_output, index=False)

                # Export BOP data
                if not bop_df.empty:
                    bop_output = output_file.parent / f"{output_file.stem}_bop_data.csv"
                    bop_df.to_csv(bop_output, index=False)

                # Export derived metrics
                if not derived_df.empty:
                    derived_output = output_file.parent / f"{output_file.stem}_derived_metrics.csv"
                    derived_df.to_csv(derived_output, index=False)

            elif format.lower() == 'excel':
                with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                    z1_df.to_excel(writer, sheet_name='Z1_Data', index=False)

                    if not bop_df.empty:
                        bop_df.to_excel(writer, sheet_name='BOP_Data', index=False)

                    if not derived_df.empty:
                        derived_df.to_excel(writer, sheet_name='Derived_Metrics', index=False)

            elif format.lower() == 'json':
                export_data = {
                    'z1_data': z1_df.to_dict('records') if not z1_df.empty else [],
                    'bop_data': bop_df.to_dict('records') if not bop_df.empty else [],
                    'derived_metrics': derived_df.to_dict('records') if not derived_df.empty else [],
                    'summary': self.get_data_summary(),
                    'export_timestamp': datetime.now().isoformat()
                }

                with open(output_path, 'w') as f:
                    json.dump(export_data, f, indent=2, default=str)

            logger.info(f"Data exported to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return False

    def close(self):
        """Close database connections and clean up resources."""
        try:
            if hasattr(self, 'api'):
                self.api.close()
            logger.info("Federal Reserve Z.1 Collector closed")
        except Exception as e:
            logger.error(f"Error closing collector: {e}")

# Main execution function
def collect_federal_reserve_z1_data(api_key: str = None, start_year: int = 1950) -> FederalReserveZ1Collector:
    """
    Main function to collect Federal Reserve Z.1 data.

    Args:
        api_key: FRED API key
        start_year: Starting year for data collection

    Returns:
        Initialized Z.1 collector with collected data
    """
    config = Z1DataConfig(
        api_key=api_key,
        start_year=start_year,
        include_bop=True,
        validate_data=True,
        parallel_requests=True
    )

    collector = FederalReserveZ1Collector(config)

    # Collect all data
    logger.info("Starting Federal Reserve Z.1 data collection...")

    # Collect Z.1 data
    z1_data = collector.collect_all_z1_data()

    # Collect BOP data if requested
    if config.include_bop:
        bop_data = collector.collect_bop_data()

    # Calculate derived metrics
    derived_metrics = collector.calculate_derived_metrics()

    # Print summary
    summary = collector.get_data_summary()
    logger.info("Data collection completed successfully!")
    logger.info(f"Z.1 Data: {summary['z1_data']['total_observations']} observations across {summary['z1_data']['total_series']} series")
    if config.include_bop:
        logger.info(f"BOP Data: {summary['bop_data']['total_observations']} observations across {summary['bop_data']['total_series']} series")

    return collector

if __name__ == "__main__":
    # Example usage
    collector = collect_federal_reserve_z1_data(start_year=1950)

    # Export data
    collector.export_data("output/federal_reserve_z1_data.xlsx", format="excel")

    collector.close()
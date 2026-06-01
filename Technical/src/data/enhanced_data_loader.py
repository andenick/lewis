"""
Enhanced Data Loader
==========================

Comprehensive integration with data source economic database to massively expand
Lewis platform data coverage from 116K to 1M+ observations.

This module provides access to:
- Extended FRED series (15 economic categories, 500K+ obs)
- ALFRED historical vintages (4.1M obs)
- Census county data (346K obs)
- Financial market data (100K+ obs)
- Multi-country indicators via World Bank/OECD

Author: Lewis Platform
Date: 2025-10-27
Version: 2.0 - Enhanced Data integration
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Union, Tuple
from datetime import datetime, timedelta
import warnings
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# DATA_ROOT = where source data is read; OUTPUT_ROOT = where outputs are written.
import os
DATA_ROOT = Path(os.environ.get("DATA_ROOT", "data"))
OUTPUT_ROOT = Path(os.environ.get("OUTPUT_ROOT", "outputs"))


class EnhancedDataLoader:
    """
    Enhanced data loader for comprehensive data source integration.

    Provides access to the source economic database including:
    - Extended FRED series (15 categories)
    - ALFRED historical vintages
    - Census demographic and economic data
    - Financial market data
    - Multi-country indicators
    """

    def __init__(self):
        """Initialize the enhanced data loader."""
        self.data_root = DATA_ROOT
        self.lewis_output = OUTPUT_ROOT
        self.cache = {}

        # Define source data paths (under DATA_ROOT)
        self.fred_path = self.data_root / "FRED"
        self.alfred_path = self.data_root / "ALFRED"
        self.census_path = self.data_root / "CENSUS"
        self.alpha_vantage_path = self.data_root / "ALPHA_VANTAGE"

        # FRED data categories available in the source store
        self.fred_categories = {
            'trade': 'fred_trade_20250929.csv',
            'interest_rates': 'fred_interest_rates_20250929.csv',
            'financial_stress': 'fred_financial_stress_20250929.csv',
            'gdp_growth': 'fred_gdp_growth_20250929.csv',
            'inflation': 'fred_inflation_20250929.csv',
            'employment': 'fred_employment_20250929.csv',
            'housing': 'fred_housing_20250929.csv',
            'money_banking': 'fred_money_banking_20250929.csv',
            'production': 'fred_production_20250929.csv',
            'income_spending': 'fred_income_spending_20250929.csv',
            'demographics': 'fred_demographics_20250929.csv',
            'labor_productivity': 'fred_labor_productivity_20250929.csv',
            'fiscal': 'fred_fiscal_20250929.csv',
            'regional': 'fred_regional_20250929.csv',
            'business': 'fred_business_20250929.csv'
        }

        # Auto-discover FRED data files in the source store
        self._discover_fred_files()

        logger.info("Enhanced data source Loader initialized")
        logger.info(f"Data path: {self.data_root}")
        logger.info(f"Available FRED categories: {len(self.fred_categories)}")

    def load_fred_category(self, category: str, start_date: Optional[str] = None,
                          end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Load a specific FRED data category from the source store.

        Args:
            category: FRED category name (e.g., 'trade', 'interest_rates')
            start_date: Optional start date filter (YYYY-MM-DD)
            end_date: Optional end date filter (YYYY-MM-DD)

        Returns:
            DataFrame with FRED data for the category
        """
        if category not in self.fred_categories:
            available = ', '.join(self.fred_categories.keys())
            raise ValueError(f"Unknown category '{category}'. Available: {available}")

        cache_key = f"fred_{category}_{start_date}_{end_date}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        filename = self.fred_categories[category]
        filepath = self.fred_path / filename

        if not filepath.exists():
            raise FileNotFoundError(f"FRED data file not found: {filepath}")

        logger.info(f"Loading FRED {category} data from {filename}")

        # Load data
        df = pd.read_csv(filepath)

        # Parse dates
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])

        # Filter by date range if provided
        if start_date:
            start_date = pd.to_datetime(start_date)
            df = df[df['date'] >= start_date]

        if end_date:
            end_date = pd.to_datetime(end_date)
            df = df[df['date'] <= end_date]

        # Cache result
        self.cache[cache_key] = df

        logger.info(f"Loaded {len(df)} observations for FRED {category}")
        return df

    def load_all_fred_data(self, start_date: Optional[str] = None,
                          end_date: Optional[str] = None) -> Dict[str, pd.DataFrame]:
        """
        Load all FRED categories from the source store.

        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            Dictionary mapping category names to DataFrames
        """
        logger.info("Loading all FRED categories from the source store...")

        all_data = {}
        total_obs = 0

        for category in self.fred_categories.keys():
            try:
                df = self.load_fred_category(category, start_date, end_date)
                all_data[category] = df
                total_obs += len(df)
                logger.info(f"✓ {category}: {len(df)} observations")
            except Exception as e:
                logger.error(f"✗ Failed to load {category}: {e}")

        logger.info(f"Loaded total: {total_obs:,} observations across {len(all_data)} categories")
        return all_data

    def load_alfred_vintages(self, series_id: Optional[str] = None,
                           categories: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Load ALFRED historical vintages from the source store.

        Args:
            series_id: Optional specific FRED series ID
            categories: Optional list of categories to load

        Returns:
            DataFrame with ALFRED vintage data
        """
        logger.info("Loading ALFRED historical vintages...")

        # Available ALFRED files in the source store
        alfred_files = {
            'trade': 'alfred_trade_20251002_1344.csv',
            'gdp': 'alfred_gdp_20251002_1344.csv',
            'inflation': 'alfred_inflation_20251002_1344.csv',
            'employment': 'alfred_employment_20251002_1344.csv',
            'interest_rates': 'alfred_interest_rates_20251002_1344.csv'
        }

        dfs = []
        total_obs = 0

        for category, filename in alfred_files.items():
            if categories and category not in categories:
                continue

            filepath = self.alfred_path / filename
            if not filepath.exists():
                logger.warning(f"ALFRED file not found: {filename}")
                continue

            try:
                df = pd.read_csv(filepath)
                df['category'] = category

                # Filter by series_id if specified
                if series_id and 'series_id' in df.columns:
                    df = df[df['series_id'] == series_id]

                dfs.append(df)
                total_obs += len(df)
                logger.info(f"✓ ALFRED {category}: {len(df)} vintages")

            except Exception as e:
                logger.error(f"✗ Failed to load ALFRED {category}: {e}")

        if dfs:
            combined_df = pd.concat(dfs, ignore_index=True)
            logger.info(f"Loaded {total_obs:,} ALFRED vintage observations")
            return combined_df
        else:
            logger.warning("No ALFRED data loaded")
            return pd.DataFrame()

    def load_census_data(self, data_type: str = 'timeseries') -> pd.DataFrame:
        """
        Load Census demographic and economic data from the source store.

        Args:
            data_type: Type of census data ('timeseries', 'demographics', 'business')

        Returns:
            DataFrame with Census data
        """
        logger.info(f"Loading Census {data_type} data...")

        # Find Census CSV files
        census_files = list(self.census_path.glob("**/*.csv"))

        if not census_files:
            logger.warning("No Census CSV files found in the source store")
            return pd.DataFrame()

        dfs = []
        total_obs = 0

        for filepath in census_files:
            try:
                df = pd.read_csv(filepath)
                df['source_file'] = filepath.name
                dfs.append(df)
                total_obs += len(df)

            except Exception as e:
                logger.warning(f"Failed to load {filepath.name}: {e}")

        if dfs:
            combined_df = pd.concat(dfs, ignore_index=True)
            logger.info(f"Loaded {total_obs:,} Census observations from {len(dfs)} files")
            return combined_df
        else:
            return pd.DataFrame()

    def load_financial_markets(self) -> pd.DataFrame:
        """
        Load financial market data from the source store (Alpha Vantage).

        Returns:
            DataFrame with financial market data
        """
        logger.info("Loading financial market data...")

        # Find Alpha Vantage CSV files
        av_files = list(self.alpha_vantage_path.glob("**/*.csv"))

        if not av_files:
            logger.warning("No Alpha Vantage files found in the source store")
            return pd.DataFrame()

        dfs = []
        total_obs = 0

        for filepath in av_files:
            try:
                df = pd.read_csv(filepath)
                df['source_file'] = filepath.name

                # Standardize date column if present
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'])
                elif 'timestamp' in df.columns:
                    df['date'] = pd.to_datetime(df['timestamp'])

                dfs.append(df)
                total_obs += len(df)

            except Exception as e:
                logger.warning(f"Failed to load {filepath.name}: {e}")

        if dfs:
            combined_df = pd.concat(dfs, ignore_index=True)
            logger.info(f"Loaded {total_obs:,} financial market observations")
            return combined_df
        else:
            return pd.DataFrame()

    def create_unified_dataset(self, start_date: Optional[str] = None,
                             end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Create a unified dataset combining multiple data source sources.

        Args:
            start_date: Optional start date
            end_date: Optional end date

        Returns:
            Unified DataFrame with multiple data sources
        """
        logger.info("Creating unified dataset from the source store sources...")

        # Load key FRED categories
        key_categories = ['trade', 'gdp_growth', 'inflation', 'interest_rates', 'employment']
        unified_data = {}

        for category in key_categories:
            try:
                df = self.load_fred_category(category, start_date, end_date)
                if 'date' in df.columns and 'value' in df.columns:
                    # Create pivot-friendly format
                    if 'series_id' in df.columns:
                        pivot_df = df.pivot_table(
                            index='date',
                            columns='series_id',
                            values='value',
                            aggfunc='first'
                        )
                        for col in pivot_df.columns:
                            unified_data[f"{category}_{col}"] = pivot_df[col]
                    else:
                        unified_data[category] = df.set_index('date')['value']

            except Exception as e:
                logger.warning(f"Failed to process {category}: {e}")

        # Combine all series
        if unified_data:
            unified_df = pd.DataFrame(unified_data)
            logger.info(f"Created unified dataset: {len(unified_df)} dates, {len(unified_df.columns)} series")
            return unified_df
        else:
            logger.warning("No data available for unified dataset")
            return pd.DataFrame()

    def get_data_summary(self) -> Dict:
        """
        Get summary statistics of available source data.

        Returns:
            Dictionary with data summary statistics
        """
        summary = {
            'fred_categories': {},
            'total_observations': 0,
            'date_range': {},
            'available_sources': []
        }

        # Check FRED files
        for category, filename in self.fred_categories.items():
            filepath = self.fred_path / filename
            if filepath.exists():
                try:
                    size_mb = filepath.stat().st_size / (1024 * 1024)
                    df_sample = pd.read_csv(filepath, nrows=5)

                    summary['fred_categories'][category] = {
                        'filename': filename,
                        'size_mb': round(size_mb, 2),
                        'columns': list(df_sample.columns),
                        'available': True
                    }
                    summary['total_observations'] += size_mb * 1000  # Rough estimate

                except Exception as e:
                    summary['fred_categories'][category] = {
                        'available': False,
                        'error': str(e)
                    }

        # Check other sources
        other_sources = {
            'ALFRED': self.alfred_path,
            'Census': self.census_path,
            'Alpha_Vantage': self.alpha_vantage_path
        }

        for source_name, source_path in other_sources.items():
            if source_path.exists():
                file_count = len(list(source_path.glob("**/*.csv")))
                summary['available_sources'].append({
                    'name': source_name,
                    'path': str(source_path),
                    'file_count': file_count,
                    'available': True
                })

        return summary

    def export_to_lewis_output(self, data: pd.DataFrame,
                             filename: str,
                             data_type: str = 'enhanced_robin') -> Path:
        """
        Export data to Lewis Output directory with proper naming.

        Args:
            data: DataFrame to export
            filename: Base filename (without extension)
            data_type: Type of data for subdirectory organization

        Returns:
            Path to exported file
        """
        # Create subdirectory if needed
        output_dir = self.lewis_output / data_type.upper()
        output_dir.mkdir(parents=True, exist_ok=True)

        # Add timestamp to filename
        timestamp = datetime.now().strftime("%Y.%m.%d")
        full_filename = f"[{timestamp}] {filename}.csv"
        output_path = output_dir / full_filename

        # Export data
        data.to_csv(output_path, index=False)

        logger.info(f"Exported {len(data)} observations to {output_path}")
        return output_path

    def load_enhanced_international_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load enhanced international economics data from the source store sources.

        Returns:
            Dictionary with enhanced international data
        """
        logger.info("Loading enhanced international economics data...")

        enhanced_data = {}

        # Core international series
        international_series = {
            'trade_balance': ('trade', 'BOPGSTB'),
            'exports': ('trade', 'EXPGS'),
            'imports': ('trade', 'IMPGS'),
            'net_exports': ('trade', 'NETFI'),
            'exchange_rates': ('interest_rates', 'DEXUSEU'),  # Sample series
            'gdp_growth': ('gdp_growth', 'A191RL1Q225SBEA'),  # Sample series
        }

        for name, (category, series_id) in international_series.items():
            try:
                df = self.load_fred_category(category)
                if 'series_id' in df.columns:
                    series_data = df[df['series_id'] == series_id].copy()
                    if not series_data.empty:
                        enhanced_data[name] = series_data
                        logger.info(f"✓ {name}: {len(series_data)} observations")
                    else:
                        logger.warning(f"✗ No data found for {series_id}")
                else:
                    enhanced_data[name] = df
                    logger.info(f"✓ {name}: {len(df)} observations")

            except Exception as e:
                logger.error(f"✗ Failed to load {name}: {e}")

        return enhanced_data


# Convenience function for quick loading
def load_enhanced_data(categories: Optional[List[str]] = None) -> Dict[str, pd.DataFrame]:
    """
    Convenience function to load enhanced source data.

    Args:
        categories: List of FRED categories to load (None = all)

    Returns:
        Dictionary mapping category names to DataFrames
    """
    loader = EnhancedDataLoader()

    if categories:
        data = {}
        for category in categories:
            try:
                data[category] = loader.load_fred_category(category)
            except Exception as e:
                logger.warning(f"Failed to load {category}: {e}")
        return data
    else:
        return loader.load_all_fred_data()


if __name__ == "__main__":
    # Example usage and testing
    loader = EnhancedDataLoader()

    print("=== Enhanced Data Loader ===")
    print(f"Data root: {loader.data_root}")

    # Get data summary
    print("\n=== Data Summary ===")
    summary = loader.get_data_summary()
    print(f"FRED categories available: {len(summary['fred_categories'])}")
    print(f"Other sources: {[s['name'] for s in summary['available_sources']]}")

    # Load sample data
    print("\n=== Loading Sample Data ===")
    try:
        trade_data = loader.load_fred_category('trade')
        print(f"Trade data: {len(trade_data)} observations")
        print(f"Date range: {trade_data['date'].min()} to {trade_data['date'].max()}")

        # Create unified dataset
        unified = loader.create_unified_dataset('2020-01-01', '2024-12-31')
        print(f"Unified dataset: {unified.shape}")

    except Exception as e:
        print(f"Error loading data: {e}")
        print("Make sure data source is accessible at the expected path")
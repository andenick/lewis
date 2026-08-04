"""
Enhanced International Trade Data Loader
=========================================

Extended data loading functionality for the comprehensive international trade
dataset including 19 FRED series, G20 World Bank data, and individual series access.

New Features:
- Load individual FRED series by name
- Load all exchange rates
- Load trade indices
- Load G20 World Bank imports data
- Series metadata access

Author: Lewis Platform
Date: October 6, 2025
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Union
import json

# Import base loader
# Make sibling modules importable whether this file is run as a script or
# imported as `analysis.<module>` from `Technical/src`.
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent))

from trade_data_loader import TradeDataLoader


class EnhancedTradeDataLoader(TradeDataLoader):
    """Extended data loader with access to all FRED series and G20 data."""

    def __init__(self):
        """Initialize enhanced loader with paths to all data sources."""
        super().__init__()

        # Additional paths
        self.by_series_path = self.output_root / "BY_SERIES"
        self.comprehensive_path = self.output_root / "COMPREHENSIVE_COLLECTION"

    def load_fred_series(self, series_id: str) -> pd.DataFrame:
        """
        Load individual FRED trade series.

        Args:
            series_id: FRED series identifier (e.g., 'BOPGSTB', 'EXPGS', 'DEXJPUS')

        Returns:
            DataFrame with date and value columns

        Available Series:
            Balance of Payments: BOPBCA
            Trade Balances: BOPGSTB, BOPGTB
            Exports/Imports: BOPTEXP, BOPTIMP, EXPGS, IMPGS
            Financial: NETFI
            Exchange Rates: DEXCAUS, DEXCHUS, DEXJPUS, DEXUSEU, DEXUSUK
            Indices: DTWEXBGS, DTWEXM, IEAMGS, IEAXGS
            Trade Values: XTEXVA01USQ188S, XTIMVA01USQ188S
        """
        series_file = self.by_series_path / f"{series_id}.csv"

        if not series_file.exists():
            raise FileNotFoundError(
                f"Series {series_id} not found. Check BY_SERIES/SERIES_CATALOG.md for available series."
            )

        df = pd.read_csv(series_file)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')

        print(f"Loaded {series_id}: {len(df)} observations from {df['date'].min()} to {df['date'].max()}")

        return df[['date', 'value', 'series_id']]

    def load_all_exchange_rates(self) -> Dict[str, pd.DataFrame]:
        """
        Load all available exchange rate series.

        Returns:
            Dictionary with currency pair as key, DataFrame as value
        """
        exchange_rates = {}

        rate_series = {
            'USD_CAD': 'DEXCAUS',
            'USD_CNY': 'DEXCHUS',
            'USD_JPY': 'DEXJPUS',
            'USD_EUR': 'DEXUSEU',
            'USD_GBP': 'DEXUSUK'
        }

        for pair, series_id in rate_series.items():
            exchange_rates[pair] = self.load_fred_series(series_id)

        print(f"Loaded {len(exchange_rates)} exchange rate series")
        return exchange_rates

    def load_trade_indices(self) -> Dict[str, pd.DataFrame]:
        """
        Load all trade-related indices.

        Returns:
            Dictionary with index name as key, DataFrame as value
        """
        indices = {}

        index_series = {
            'Trade_Weighted_Dollar_Broad': 'DTWEXBGS',
            'Trade_Weighted_Dollar_Major': 'DTWEXM',
            'Import_Price_Index': 'IEAMGS',
            'Export_Price_Index': 'IEAXGS',
            'Export_Value_Index': 'XTEXVA01USQ188S',
            'Import_Value_Index': 'XTIMVA01USQ188S'
        }

        for name, series_id in index_series.items():
            indices[name] = self.load_fred_series(series_id)

        print(f"Loaded {len(indices)} trade indices")
        return indices

    def load_g20_imports(self) -> pd.DataFrame:
        """
        Load World Bank G20 imports data.

        Returns:
            DataFrame with country, year, and import values
        """
        wb_file = self.comprehensive_path / "worldbank_imports_g20_20250929.csv"

        if not wb_file.exists():
            raise FileNotFoundError(f"World Bank G20 data not found: {wb_file}")

        df = pd.read_csv(wb_file)

        print(f"Loaded World Bank G20 imports: {len(df)} observations for {df['country_code'].nunique()} countries")

        return df

    def get_series_metadata(self) -> Dict:
        """
        Load metadata for all FRED series.

        Returns:
            Dictionary with series information
        """
        metadata_file = self.by_series_path / "series_metadata.json"

        if not metadata_file.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_file}")

        with open(metadata_file, 'r') as f:
            metadata = json.load(f)

        return metadata

    def get_available_series(self) -> pd.DataFrame:
        """
        Get list of all available FRED series with descriptions.

        Returns:
            DataFrame with series information
        """
        metadata = self.get_series_metadata()

        series_list = []
        for series_id, info in metadata['series'].items():
            series_list.append({
                'Series_ID': series_id,
                'Name': info['name'],
                'Category': info['category'],
                'Frequency': info['frequency'],
                'Start_Date': info['start_date'],
                'End_Date': info['end_date'],
                'Records': info['records']
            })

        return pd.DataFrame(series_list)

    def load_comprehensive_dataset_enhanced(self) -> Dict[str, pd.DataFrame]:
        """
        Create comprehensive dataset including all new FRED series.

        Returns:
            Dictionary with all available datasets
        """
        datasets = self.create_integrated_dataset()  # Base datasets from parent class

        # Add FRED individual series
        print("\nLoading FRED individual series...")
        datasets['fred_current_account'] = self.load_fred_series('BOPBCA')
        datasets['fred_trade_balance_gs'] = self.load_fred_series('BOPGSTB')
        datasets['fred_exports'] = self.load_fred_series('EXPGS')
        datasets['fred_imports'] = self.load_fred_series('IMPGS')

        # Add exchange rates
        print("\nLoading exchange rates...")
        datasets['exchange_rates'] = self.load_all_exchange_rates()

        # Add trade indices
        print("\nLoading trade indices...")
        datasets['trade_indices'] = self.load_trade_indices()

        # Add G20 data
        print("\nLoading World Bank G20 data...")
        datasets['worldbank_g20_imports'] = self.load_g20_imports()

        print(f"\n{'='*60}")
        print(f"Enhanced dataset created with {len(datasets)} components")
        print(f"{'='*60}")

        return datasets

    def get_data_coverage_summary(self) -> pd.DataFrame:
        """
        Get summary of data coverage across all sources.

        Returns:
            DataFrame with coverage information
        """
        coverage = []

        # Country-specific annual data
        for country in ['US', 'UK', 'GER']:
            try:
                df = self.load_annual_pct_data(country)
                coverage.append({
                    'Source': f'{country} Annual BoP',
                    'Type': 'Country-Specific',
                    'Frequency': 'Annual',
                    'Start': df['Year'].min(),
                    'End': df['Year'].max(),
                    'Years': len(df),
                    'Variables': len(df.columns) - 1
                })
            except:
                pass

        # FRED series
        metadata = self.get_series_metadata()
        for series_id, info in metadata['series'].items():
            coverage.append({
                'Source': series_id,
                'Type': info['category'],
                'Frequency': info['frequency'],
                'Start': pd.to_datetime(info['start_date']).year,
                'End': pd.to_datetime(info['end_date']).year,
                'Years': pd.to_datetime(info['end_date']).year - pd.to_datetime(info['start_date']).year + 1,
                'Variables': 1
            })

        # G20 imports
        try:
            g20 = self.load_g20_imports()
            coverage.append({
                'Source': 'World Bank G20 Imports',
                'Type': 'Multi-Country',
                'Frequency': 'Annual',
                'Start': g20['year'].min(),
                'End': g20['year'].max(),
                'Years': g20['year'].nunique(),
                'Variables': g20['country_code'].nunique()
            })
        except:
            pass

        return pd.DataFrame(coverage).sort_values(['Type', 'Source'])


def main():
    """Example usage of EnhancedTradeDataLoader."""

    print("\n" + "="*80)
    print("ENHANCED INTERNATIONAL TRADE DATA LOADER")
    print("="*80 + "\n")

    loader = EnhancedTradeDataLoader()

    # Show available series
    print("Available FRED Series:")
    print("="*80)
    available = loader.get_available_series()
    print(available.to_string(index=False))

    print("\n" + "="*80)
    print("Data Coverage Summary:")
    print("="*80)
    coverage = loader.get_data_coverage_summary()
    print(coverage.to_string(index=False))

    print("\n" + "="*80)
    print("Example: Loading US-Japan Exchange Rate")
    print("="*80)
    usd_jpy = loader.load_fred_series('DEXJPUS')
    print(f"\nFirst 5 observations:")
    print(usd_jpy.head().to_string(index=False))
    print(f"\nLast 5 observations:")
    print(usd_jpy.tail().to_string(index=False))

    print("\n" + "="*80)
    print("Enhanced data loader ready!")
    print("="*80)


if __name__ == "__main__":
    main()

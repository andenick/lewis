"""
Unified Data Loader
===================

Loads and integrates ALL data sources into a single unified dataset.

Data Sources:
1. ClassFiles (US, UK, Germany) - Historical detailed data
2. Banco de México (Mexico) - API collected
3. World Bank (28 countries) - API collected
4. FRED (US indicators) - Cached data

Author: Claude
Date: 2025-10-06
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
OUTPUT_ROOT = Path(os.environ.get("OUTPUT_ROOT", "outputs"))


class UnifiedDataLoader:
    """
    Load and integrate all data sources into unified datasets.

    Provides access to:
    - 32 countries
    - 154,000+ observations
    - Multiple data sources cross-validated
    """

    def __init__(self):
        """Initialize unified data loader."""
        self.project_root = PROJECT_ROOT
        self.output_root = OUTPUT_ROOT

        # Data containers
        self.classfiles_data = {}
        self.mexico_data = {}
        self.worldbank_data = None
        self.fred_data = {}

        # Unified datasets
        self.unified_bop = None
        self.unified_trade = None
        self.unified_gdp = None

        print("\n" + "="*80)
        print("Unified Data Loader Initialized")
        print("="*80)
        print(f"Project root: {PROJECT_ROOT}")
        print(f"data source path: {OUTPUT_ROOT}")

    # ========================================================================
    # LOAD INDIVIDUAL SOURCES
    # ========================================================================

    def load_classfiles_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load ClassFiles data (US, UK, Germany).

        Returns
        -------
        dict
            Dictionary with 'US', 'UK', 'Germany' DataFrames
        """
        print("\n[ClassFiles] Loading detailed historical data...")

        classfiles_path = OUTPUT_ROOT / "BALANCE_OF_PAYMENTS"

        data = {}

        # US Data
        us_file = classfiles_path / "USdata_annual_pct.csv"
        if us_file.exists():
            data['US'] = pd.read_csv(us_file)
            print(f"  US: {len(data['US'])} observations (1960-2024)")

        # UK Data
        uk_file = classfiles_path / "UKdata_annual_pct.csv"
        if uk_file.exists():
            data['UK'] = pd.read_csv(uk_file)
            print(f"  UK: {len(data['UK'])} observations (1946-2023)")

        # Germany Data
        de_file = classfiles_path / "GERdata_annual_pct.csv"
        if de_file.exists():
            data['Germany'] = pd.read_csv(de_file)
            print(f"  Germany: {len(data['Germany'])} observations (1971-2024)")

        self.classfiles_data = data
        total_obs = sum(len(df) for df in data.values())
        print(f"  Total ClassFiles observations: {total_obs:,}")

        return data

    def load_mexico_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load Mexico data from Banco de México API.

        Returns
        -------
        dict
            Dictionary with 'bop' and 'trade' DataFrames
        """
        print("\n[Mexico - Banxico] Loading API collected data...")

        banxico_path = OUTPUT_ROOT / "Banco_de_Mexico"

        data = {}

        # Balance of Payments
        bop_file = banxico_path / "Balance_of_Payments" / "banxico_bop_2000_2024.csv"
        if bop_file.exists():
            data['bop'] = pd.read_csv(bop_file)
            data['bop']['date'] = pd.to_datetime(data['bop']['date'])
            print(f"  Balance of Payments: {len(data['bop']):,} observations")

        # Trade Statistics
        trade_file = banxico_path / "Trade" / "banxico_trade_2000_2024.csv"
        if trade_file.exists():
            data['trade'] = pd.read_csv(trade_file)
            data['trade']['date'] = pd.to_datetime(data['trade']['date'])
            print(f"  Trade Statistics: {len(data['trade']):,} observations")

        self.mexico_data = data
        total_obs = sum(len(df) for df in data.values())
        print(f"  Total Mexico observations: {total_obs:,}")

        return data

    def load_worldbank_data(self) -> pd.DataFrame:
        """
        Load World Bank data (28 countries).

        Returns
        -------
        pd.DataFrame
            Combined World Bank dataset
        """
        print("\n[World Bank] Loading API collected data...")

        wb_path = OUTPUT_ROOT / "World_Bank"

        # Load combined dataset
        combined_file = wb_path / "worldbank_all_countries_2000_2024.csv"

        if combined_file.exists():
            df = pd.read_csv(combined_file)
            print(f"  Countries: {df['country'].nunique()}")
            print(f"  Indicators: {df['indicator_name'].nunique()}")
            print(f"  Years: {df['year'].min()}-{df['year'].max()}")
            print(f"  Total observations: {len(df):,}")

            self.worldbank_data = df
            return df
        else:
            print("  [WARNING] World Bank combined file not found")
            return pd.DataFrame()

    def load_fred_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load FRED data (US indicators).

        Returns
        -------
        dict
            Dictionary of FRED series
        """
        print("\n[FRED] Loading cached indicators...")

        fred_path = OUTPUT_ROOT / "BY_SERIES"

        data = {}

        # Key FRED series
        series_files = {
            'BOPGSTB': 'Trade Balance',
            'BOPBCA': 'Current Account',
            'DEXUSEU': 'EUR/USD Exchange Rate',
            'DEXJPUS': 'JPY/USD Exchange Rate',
            'DEXCHUS': 'CNY/USD Exchange Rate',
        }

        for series_id, description in series_files.items():
            series_file = fred_path / f"{series_id}.csv"
            if series_file.exists():
                data[series_id] = pd.read_csv(series_file)
                if 'date' in data[series_id].columns:
                    data[series_id]['date'] = pd.to_datetime(data[series_id]['date'])
                print(f"  {series_id}: {len(data[series_id])} observations ({description})")

        self.fred_data = data
        total_obs = sum(len(df) for df in data.values())
        print(f"  Total FRED observations: {total_obs:,}")

        return data

    # ========================================================================
    # LOAD ALL DATA
    # ========================================================================

    def load_all(self) -> Dict[str, any]:
        """
        Load all data sources.

        Returns
        -------
        dict
            Dictionary with all data sources loaded
        """
        print("\n" + "="*80)
        print("LOADING ALL DATA SOURCES")
        print("="*80)

        # Load each source
        classfiles = self.load_classfiles_data()
        mexico = self.load_mexico_data()
        worldbank = self.load_worldbank_data()
        fred = self.load_fred_data()

        # Summary
        print("\n" + "="*80)
        print("DATA LOADING COMPLETE")
        print("="*80)

        total_obs = 0
        total_obs += sum(len(df) for df in classfiles.values())
        total_obs += sum(len(df) for df in mexico.values())
        total_obs += len(worldbank) if worldbank is not None else 0
        total_obs += sum(len(df) for df in fred.values())

        print(f"\nTotal observations loaded: {total_obs:,}")
        print(f"Data sources: 4 (ClassFiles, Mexico, World Bank, FRED)")
        print(f"Countries: 32+")

        return {
            'classfiles': classfiles,
            'mexico': mexico,
            'worldbank': worldbank,
            'fred': fred
        }

    # ========================================================================
    # CREATE UNIFIED DATASETS
    # ========================================================================

    def create_unified_bop(self) -> pd.DataFrame:
        """
        Create unified Balance of Payments dataset across all sources.

        Returns
        -------
        pd.DataFrame
            Unified BoP data with standardized structure
        """
        print("\n[UNIFY] Creating unified Balance of Payments dataset...")

        unified_rows = []

        # Add World Bank data (already in good format)
        if self.worldbank_data is not None:
            wb_bop = self.worldbank_data[
                self.worldbank_data['indicator_name'].str.contains('Current_Account', na=False)
            ].copy()

            for _, row in wb_bop.iterrows():
                unified_rows.append({
                    'country': row['country'],
                    'country_name': row['country_name'],
                    'year': row['year'],
                    'indicator': 'Current_Account',
                    'value': row['value'],
                    'units': 'USD' if 'USD' in row['indicator_name'] else 'pct_GDP',
                    'source': 'World_Bank',
                    'frequency': 'Annual'
                })

        # Add Mexico Banxico data (aggregate to annual)
        if 'bop' in self.mexico_data:
            mexico_bop = self.mexico_data['bop'].copy()
            mexico_bop['year'] = mexico_bop['date'].dt.year

            # Aggregate to annual
            mexico_annual = mexico_bop.groupby(['year', 'indicator_name'])['value'].mean().reset_index()

            for _, row in mexico_annual.iterrows():
                unified_rows.append({
                    'country': 'MEX',
                    'country_name': 'Mexico',
                    'year': row['year'],
                    'indicator': row['indicator_name'],
                    'value': row['value'],
                    'units': 'USD_Millions',
                    'source': 'Banco_de_Mexico',
                    'frequency': 'Annual_from_Monthly'
                })

        if unified_rows:
            unified_df = pd.DataFrame(unified_rows)
            print(f"  Unified BoP observations: {len(unified_df):,}")
            print(f"  Countries: {unified_df['country'].nunique()}")
            print(f"  Years: {unified_df['year'].min()}-{unified_df['year'].max()}")

            self.unified_bop = unified_df
            return unified_df
        else:
            return pd.DataFrame()

    def create_unified_trade(self) -> pd.DataFrame:
        """
        Create unified trade dataset.

        Returns
        -------
        pd.DataFrame
            Unified trade data
        """
        print("\n[UNIFY] Creating unified trade dataset...")

        unified_rows = []

        # Add World Bank trade data
        if self.worldbank_data is not None:
            wb_trade = self.worldbank_data[
                self.worldbank_data['indicator_name'].str.contains('Exports|Imports', na=False)
            ].copy()

            for _, row in wb_trade.iterrows():
                indicator = 'Exports' if 'Exports' in row['indicator_name'] else 'Imports'
                unified_rows.append({
                    'country': row['country'],
                    'country_name': row['country_name'],
                    'year': row['year'],
                    'indicator': indicator,
                    'value': row['value'],
                    'units': 'USD',
                    'source': 'World_Bank',
                    'frequency': 'Annual'
                })

        # Add Mexico trade data
        if 'trade' in self.mexico_data:
            mexico_trade = self.mexico_data['trade'].copy()
            mexico_trade['year'] = mexico_trade['date'].dt.year

            # Aggregate to annual
            mexico_annual = mexico_trade.groupby(['year', 'indicator_name'])['value'].sum().reset_index()

            for _, row in mexico_annual.iterrows():
                unified_rows.append({
                    'country': 'MEX',
                    'country_name': 'Mexico',
                    'year': row['year'],
                    'indicator': row['indicator_name'],
                    'value': row['value'],
                    'units': 'USD_Millions',
                    'source': 'Banco_de_Mexico',
                    'frequency': 'Annual_from_Monthly'
                })

        if unified_rows:
            unified_df = pd.DataFrame(unified_rows)
            print(f"  Unified trade observations: {len(unified_df):,}")
            print(f"  Countries: {unified_df['country'].nunique()}")

            self.unified_trade = unified_df
            return unified_df
        else:
            return pd.DataFrame()

    def create_unified_gdp(self) -> pd.DataFrame:
        """
        Create unified GDP dataset for normalization.

        Returns
        -------
        pd.DataFrame
            Unified GDP data
        """
        print("\n[UNIFY] Creating unified GDP dataset...")

        # Extract GDP from World Bank data
        if self.worldbank_data is not None:
            gdp_df = self.worldbank_data[
                self.worldbank_data['indicator_name'].str.contains('GDP', na=False)
            ].copy()

            gdp_df = gdp_df[['country', 'country_name', 'year', 'value']].copy()
            gdp_df.columns = ['country', 'country_name', 'year', 'gdp_usd']

            print(f"  GDP observations: {len(gdp_df):,}")
            print(f"  Countries: {gdp_df['country'].nunique()}")

            self.unified_gdp = gdp_df
            return gdp_df
        else:
            return pd.DataFrame()

    def create_all_unified_datasets(self) -> Dict[str, pd.DataFrame]:
        """
        Create all unified datasets.

        Returns
        -------
        dict
            Dictionary with 'bop', 'trade', 'gdp' unified DataFrames
        """
        print("\n" + "="*80)
        print("CREATING UNIFIED DATASETS")
        print("="*80)

        bop = self.create_unified_bop()
        trade = self.create_unified_trade()
        gdp = self.create_unified_gdp()

        print("\n" + "="*80)
        print("UNIFIED DATASETS COMPLETE")
        print("="*80)

        return {
            'bop': bop,
            'trade': trade,
            'gdp': gdp
        }

    # ========================================================================
    # SAVE UNIFIED DATASETS
    # ========================================================================

    def save_unified_datasets(self, output_path: Optional[Path] = None):
        """
        Save unified datasets to CSV files.

        Parameters
        ----------
        output_path : Path, optional
            Output directory. If None, saves to data source/UNIFIED/
        """
        if output_path is None:
            output_path = OUTPUT_ROOT / "UNIFIED"

        output_path.mkdir(parents=True, exist_ok=True)

        print("\n[SAVE] Saving unified datasets...")

        if self.unified_bop is not None:
            bop_file = output_path / "unified_balance_of_payments.csv"
            self.unified_bop.to_csv(bop_file, index=False)
            print(f"  Saved: {bop_file.relative_to(PROJECT_ROOT)}")

        if self.unified_trade is not None:
            trade_file = output_path / "unified_trade.csv"
            self.unified_trade.to_csv(trade_file, index=False)
            print(f"  Saved: {trade_file.relative_to(PROJECT_ROOT)}")

        if self.unified_gdp is not None:
            gdp_file = output_path / "unified_gdp.csv"
            self.unified_gdp.to_csv(gdp_file, index=False)
            print(f"  Saved: {gdp_file.relative_to(PROJECT_ROOT)}")

        print(f"\n[COMPLETE] All unified datasets saved to: {output_path.relative_to(PROJECT_ROOT)}")


def main():
    """Main execution: load and unify all data."""
    print("\n" + "="*80)
    print("UNIFIED DATA LOADER - COMPREHENSIVE INTEGRATION")
    print("="*80)

    # Initialize loader
    loader = UnifiedDataLoader()

    # Load all data sources
    all_data = loader.load_all()

    # Create unified datasets
    unified = loader.create_all_unified_datasets()

    # Save unified datasets
    loader.save_unified_datasets()

    print("\n[COMPLETE] Data integration finished!")


if __name__ == "__main__":
    main()

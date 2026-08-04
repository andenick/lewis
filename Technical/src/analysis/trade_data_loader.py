"""
International Trade Data Loader
================================

This module provides functions to load and process international trade and
balance of payments data from various sources including data source exports,
FRED data, and manually collected country-specific datasets.

Data Sources:
- the data store: US trade balance data (FRED/ALFRED)
- Manual Collection: Balance of Payments data for US, UK, Germany
- World Bank: GDP data for normalization

Author: Lewis Platform
Date: October 6, 2025
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import warnings

# Project paths
import os
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_ROOT = Path(os.environ.get("DATA_ROOT", "data"))
OUTPUT_ROOT = Path(os.environ.get("OUTPUT_ROOT", "outputs"))
OUTPUT_DATA = OUTPUT_ROOT
TECHNICAL_DATA = PROJECT_ROOT / "Technical" / "data"


class TradeDataLoader:
    """Load and process international trade data from multiple sources."""

    def __init__(self):
        """Initialize the data loader with standard paths."""
        self.output_root = OUTPUT_ROOT
        self.results_path = OUTPUT_DATA / "Results"
        self.source_path = OUTPUT_DATA / "Source"
        self.raw_path = TECHNICAL_DATA / "raw"

    def load_source_trade_data(self) -> pd.DataFrame:
        """
        Load US trade balance data from data source exports.

        Returns:
            DataFrame with columns: date, value, series_id, category
        """
        fred_file = self.output_root / "fred_trade_20250929.csv"

        if not fred_file.exists():
            raise FileNotFoundError(f"data source FRED trade data not found: {fred_file}")

        df = pd.read_csv(fred_file)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')

        print(f"Loaded data source FRED trade data: {len(df)} observations from {df['date'].min()} to {df['date'].max()}")
        return df

    def load_source_alfred_data(self) -> pd.DataFrame:
        """
        Load ALFRED vintage trade data from data source.

        Returns:
            DataFrame with vintage date information
        """
        alfred_file = self.output_root / "alfred_trade_20251002_1344.csv"

        if not alfred_file.exists():
            raise FileNotFoundError(f"data source ALFRED data not found: {alfred_file}")

        df = pd.read_csv(alfred_file)
        df['date'] = pd.to_datetime(df['date'])
        df['vintage_date'] = pd.to_datetime(df['vintage_date'])
        df = df.sort_values(['date', 'vintage_date'])

        print(f"Loaded data source ALFRED data: {len(df)} observations with vintage dates")
        return df

    def load_bop_monthly_data(self) -> pd.DataFrame:
        """
        Load monthly Balance of Payments (Goods & Services) data from the data store.

        Returns:
            DataFrame with monthly BoP trade balance data
        """
        bop_file = self.output_root / "BOPGSTB_Monthly_Seasonally Adjusted.csv"

        if not bop_file.exists():
            raise FileNotFoundError(f"BoP monthly data not found: {bop_file}")

        df = pd.read_csv(bop_file)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')

        print(f"Loaded monthly BoP data: {len(df)} observations from {df['date'].min()} to {df['date'].max()}")
        return df

    def load_country_bop_data(self, country: str = 'US') -> pd.DataFrame:
        """
        Load processed Balance of Payments data for a specific country.

        Args:
            country: Country code ('US', 'UK', or 'Germany')

        Returns:
            DataFrame with annual BoP data as % of GDP
        """
        file_mapping = {
            'US': 'BoP_USRData_NA.xlsx',
            'UK': 'BoP_UKRData_NA.xlsx',
            'Germany': 'BoP_GermanyRData_NA.xlsx'
        }

        if country not in file_mapping:
            raise ValueError(f"Country must be one of {list(file_mapping.keys())}")

        file_path = self.results_path / file_mapping[country]

        if not file_path.exists():
            raise FileNotFoundError(f"BoP data for {country} not found: {file_path}")

        df = pd.read_excel(file_path)
        print(f"Loaded {country} BoP data: {len(df)} annual observations")
        return df

    def load_annual_pct_data(self, country: str = 'US') -> pd.DataFrame:
        """
        Load annual percentage data for a specific country.

        Args:
            country: Country code ('US', 'UK', or 'GER')

        Returns:
            DataFrame with detailed BoP components as % of GDP
        """
        file_mapping = {
            'US': 'USdata_annual_pct.csv',
            'UK': 'UKdata_annual_pct.csv',
            'GER': 'GERdata_annual_pct.csv'
        }

        if country not in file_mapping:
            raise ValueError(f"Country must be one of {list(file_mapping.keys())}")

        file_path = self.results_path / file_mapping[country]

        if not file_path.exists():
            raise FileNotFoundError(f"Annual % data for {country} not found: {file_path}")

        df = pd.read_csv(file_path)
        print(f"Loaded {country} annual % data: {len(df)} years")
        return df

    def load_gdp_data(self) -> pd.DataFrame:
        """
        Load World Bank GDP data.

        Returns:
            DataFrame with GDP data for multiple countries
        """
        gdp_file = self.results_path / "BoP_WBankGDP_NA.xlsx"

        if not gdp_file.exists():
            raise FileNotFoundError(f"World Bank GDP data not found: {gdp_file}")

        df = pd.read_excel(gdp_file)
        print(f"Loaded World Bank GDP data: {len(df)} observations")
        return df

    def create_integrated_dataset(self) -> Dict[str, pd.DataFrame]:
        """
        Create an integrated dataset combining source data and country-specific data.

        Returns:
            Dictionary with keys: 'source_monthly', 'us', 'uk', 'germany', 'gdp'
        """
        datasets = {}

        print("Creating integrated international trade dataset...")
        print("-" * 60)

        # Load source data
        datasets['source_fred'] = self.load_source_trade_data()
        datasets['source_alfred'] = self.load_source_alfred_data()
        datasets['source_bop_monthly'] = self.load_bop_monthly_data()

        # Load country-specific data
        datasets['us_bop'] = self.load_country_bop_data('US')
        datasets['uk_bop'] = self.load_country_bop_data('UK')
        datasets['germany_bop'] = self.load_country_bop_data('Germany')

        # Load annual percentage data
        datasets['us_annual_pct'] = self.load_annual_pct_data('US')
        datasets['uk_annual_pct'] = self.load_annual_pct_data('UK')
        datasets['germany_annual_pct'] = self.load_annual_pct_data('GER')

        # Load GDP data
        datasets['gdp'] = self.load_gdp_data()

        print("-" * 60)
        print(f"Integrated dataset created with {len(datasets)} components")

        return datasets

    def get_data_summary(self) -> pd.DataFrame:
        """
        Get a summary of all available datasets.

        Returns:
            DataFrame with dataset names, sizes, and date ranges
        """
        summary_data = []

        try:
            datasets = self.create_integrated_dataset()

            for name, df in datasets.items():
                if 'date' in df.columns:
                    date_col = 'date'
                elif 'Year' in df.columns:
                    date_col = 'Year'
                else:
                    date_col = None

                summary_data.append({
                    'Dataset': name,
                    'Rows': len(df),
                    'Columns': len(df.columns),
                    'Start': df[date_col].min() if date_col else 'N/A',
                    'End': df[date_col].max() if date_col else 'N/A'
                })

        except Exception as e:
            print(f"Error creating summary: {e}")

        return pd.DataFrame(summary_data)


def main():
    """Example usage of the TradeDataLoader."""
    loader = TradeDataLoader()

    # Get summary of all datasets
    print("\n" + "="*60)
    print("INTERNATIONAL TRADE DATA SUMMARY")
    print("="*60 + "\n")

    summary = loader.get_data_summary()
    print(summary.to_string(index=False))

    print("\n" + "="*60)
    print("Data successfully loaded and validated!")
    print("="*60)


if __name__ == "__main__":
    main()

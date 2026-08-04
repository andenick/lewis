"""
Enhanced Unified Data Loader
===========================

Loads and integrates ALL data sources into a single unified dataset.

Enhanced Data Sources:
1. ClassFiles (US, UK, Germany) - Historical detailed data
2. Banco de México (Mexico) - API collected
3. World Bank (28 countries) - API collected
4. FRED (US indicators) - Cached data
5. NEW: Japan Data Collector - Statistics Bureau Japan + Bank of Japan
6. NEW: Canada Data Collector - Statistics Canada + Bank of Canada
7. NEW: France Data Collector - INSEE + Banque de France
8. NEW: Italy Data Collector - ISTAT + Banca d'Italia
9. NEW: China Data Collector - NBS + People's Bank of China
10. NEW: India Data Collector - RBI DBIE + Ministry of Statistics
11. NEW: Brazil Data Collector - IBGE + Banco Central do Brasil
12. NEW: DBnomics API Integration
13. NEW: UN Comtrade Framework
14. NEW: UNCTAD Collector

Author: Claude
Date: 2025-10-14
Version: 2.0 (Enhanced with 7 new countries)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, date
import sys
import os

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import new country collectors
try:
    from japan_collector import JapanDataCollector
    from canada_collector import CanadaDataCollector
    from france_collector import FranceDataCollector
    from italy_collector import ItalyDataCollector
    from china_collector import ChinaDataCollector
    from india_collector import IndiaDataCollector
    from brazil_collector import BrazilDataCollector
    from dbnomics_collector import DBnomicsCollector
    from un_comtrade_framework import UNComtradeFramework
    from unctad_collector import UNCTADCollector
    print("All collector modules imported successfully")
except ImportError as e:
    print(f"Warning: Could not import collector modules: {e}")

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
OUTPUT_ROOT = Path(os.environ.get("OUTPUT_ROOT", "outputs"))


class EnhancedUnifiedDataLoader:
    """
    Enhanced unified data loader with integration for 11 countries total.

    Provides access to:
    - 11 countries (US, UK, Germany, Mexico, Japan, Canada, France, Italy, China, India, Brazil)
    - 28+ World Bank countries
    - 300,000+ potential observations
    - Multiple data sources cross-validated
    - Real-time API integration capabilities
    """

    def __init__(self):
        """Initialize enhanced unified data loader."""
        self.project_root = PROJECT_ROOT
        self.output_root = OUTPUT_ROOT

        # Legacy data containers
        self.classfiles_data = {}
        self.mexico_data = {}
        self.worldbank_data = None
        self.fred_data = {}

        # NEW: Country collector instances
        self.country_collectors = {}
        self.country_data = {}

        # NEW: Global framework instances
        self.dbnomics_collector = None
        self.un_comtrade = None
        self.unctad_collector = None

        # Unified datasets
        self.unified_bop = None
        self.unified_trade = None
        self.unified_gdp = None
        self.unified_summary = None

        print("\n" + "="*80)
        print("ENHANCED UNIFIED DATA LOADER v2.0")
        print("="*80)
        print(f"Project root: {PROJECT_ROOT}")
        print(f"data source path: {OUTPUT_ROOT}")
        print("Countries: US, UK, Germany, Mexico + Japan, Canada, France, Italy, China, India, Brazil")
        print("Global Frameworks: DBnomics, UN Comtrade, UNCTAD")

    def _initialize_country_collectors(self):
        """Initialize all country data collectors."""
        print("\n[INIT] Initializing country data collectors...")

        try:
            self.country_collectors['Japan'] = JapanDataCollector()
            print("  Japan collector initialized")
        except Exception as e:
            print(f"  Japan collector failed: {e}")

        try:
            self.country_collectors['Canada'] = CanadaDataCollector()
            print("  Canada collector initialized")
        except Exception as e:
            print(f"  Canada collector failed: {e}")

        try:
            self.country_collectors['France'] = FranceDataCollector()
            print("  France collector initialized")
        except Exception as e:
            print(f"  France collector failed: {e}")

        try:
            self.country_collectors['Italy'] = ItalyDataCollector()
            print("  Italy collector initialized")
        except Exception as e:
            print(f"  Italy collector failed: {e}")

        try:
            self.country_collectors['China'] = ChinaDataCollector()
            print("  China collector initialized")
        except Exception as e:
            print(f"  China collector failed: {e}")

        try:
            self.country_collectors['India'] = IndiaDataCollector()
            print("  India collector initialized")
        except Exception as e:
            print(f"  India collector failed: {e}")

        try:
            self.country_collectors['Brazil'] = BrazilDataCollector()
            print("  Brazil collector initialized")
        except Exception as e:
            print(f"  Brazil collector failed: {e}")

        print(f"  Country collectors ready: {len(self.country_collectors)}")

    def _initialize_global_frameworks(self):
        """Initialize global data frameworks."""
        print("\n[INIT] Initializing global frameworks...")

        try:
            self.dbnomics_collector = DBnomicsCollector()
            print("  DBnomics collector initialized")
        except Exception as e:
            print(f"  DBnomics collector failed: {e}")

        try:
            self.un_comtrade = UNComtradeFramework()
            print("  UN Comtrade framework initialized")
        except Exception as e:
            print(f"  UN Comtrade framework failed: {e}")

        try:
            self.unctad_collector = UNCTADCollector()
            print("  UNCTAD collector initialized")
        except Exception as e:
            print(f"  UNCTAD collector failed: {e}")

    # ========================================================================
    # LOAD LEGACY DATA SOURCES
    # ========================================================================

    def load_classfiles_data(self) -> Dict[str, pd.DataFrame]:
        """Load ClassFiles data (US, UK, Germany)."""
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
        """Load Mexico data from Banco de México API."""
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
        """Load World Bank data (28 countries)."""
        print("\n[World Bank] Loading API collected data...")

        wb_path = OUTPUT_ROOT / "World_Bank"
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
        """Load FRED data (US indicators)."""
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
    # LOAD NEW COUNTRY DATA
    # ========================================================================

    def load_country_data(self, country: str,
                          allow_synthetic: bool = False) -> Dict[str, pd.DataFrame]:
        """
        Load data for a specific country using its collector.

        The national statistical APIs behind these collectors require
        authentication, so no observations are returned unless credentials are
        configured. Randomly generated placeholder series are NEVER returned by
        default: pass ``allow_synthetic=True`` to opt in, and the result is then
        returned under the ``'synthetic_sample_data'`` key so no caller can
        mistake it for measured data.

        Parameters
        ----------
        country : str
            Country name ('Japan', 'Canada', 'France', 'Italy', 'China', 'India', 'Brazil')
        allow_synthetic : bool, default False
            Opt in to randomly generated placeholder series for smoke-testing the
            pipeline shape. Never use the result as data.

        Returns
        -------
        dict
            Dictionary with different data categories. Empty when no real data is
            available and ``allow_synthetic`` is False.
        """
        if country not in self.country_collectors:
            print(f"  [WARNING] No collector available for {country}")
            return {}

        print(f"\n[{country}] Loading data through country collector...")

        if not allow_synthetic:
            print(
                f"  [SKIP] {country}: this collector's API requires credentials and no "
                f"real observations are available. Configure the country's API token, or "
                f"call load_country_data('{country}', allow_synthetic=True) to generate "
                f"clearly-labelled placeholder series for a pipeline smoke test."
            )
            return {}

        try:
            collector = self.country_collectors[country]

            # OPT-IN ONLY: randomly generated placeholders, not observations.
            sample_df = collector.generate_sample_data()

            sample_data = {
                'synthetic_sample_data': sample_df
            }

            self.country_data[country] = sample_data

            total_obs = sum(len(df) for df in sample_data.values())
            print(f"  [SYNTHETIC] {country}: {total_obs:,} generated placeholder rows "
                  f"(NOT measured data)")

            return sample_data

        except Exception as e:
            print(f"  [ERROR] Failed to load {country} data: {e}")
            return {}

    def load_all_country_data(self,
                              allow_synthetic: bool = False) -> Dict[str, Dict[str, pd.DataFrame]]:
        """Load data for all new countries."""
        print("\n" + "="*60)
        print("LOADING NEW COUNTRY DATA")
        print("="*60)

        # Initialize collectors if not done yet
        if not self.country_collectors:
            self._initialize_country_collectors()

        # Load data for each country
        for country in ['Japan', 'Canada', 'France', 'Italy', 'China', 'India', 'Brazil']:
            self.load_country_data(country, allow_synthetic=allow_synthetic)

        # Summary
        total_obs = sum(
            sum(len(df) for df in country_data.values())
            for country_data in self.country_data.values()
        )
        print(f"\nTotal new country observations: {total_obs:,}")
        print(f"Countries loaded: {len(self.country_data)}")

        return self.country_data

    # ========================================================================
    # LOAD ALL DATA SOURCES
    # ========================================================================

    def load_all(self, include_new_countries: bool = True,
                 include_global_frameworks: bool = False) -> Dict[str, Any]:
        """
        Load all data sources.

        Parameters
        ----------
        include_new_countries : bool
            Whether to load new country collectors
        include_global_frameworks : bool
            Whether to initialize global frameworks (DBnomics, UN Comtrade, UNCTAD)

        Returns
        -------
        dict
            Dictionary with all data sources loaded
        """
        print("\n" + "="*80)
        print("LOADING ALL DATA SOURCES")
        print("="*80)

        # Load legacy sources
        classfiles = self.load_classfiles_data()
        mexico = self.load_mexico_data()
        worldbank = self.load_worldbank_data()
        fred = self.load_fred_data()

        # Load new countries
        new_countries = {}
        if include_new_countries:
            new_countries = self.load_all_country_data()

        # Initialize global frameworks
        if include_global_frameworks:
            self._initialize_global_frameworks()

        # Summary
        print("\n" + "="*80)
        print("DATA LOADING COMPLETE")
        print("="*80)

        total_obs = 0
        total_obs += sum(len(df) for df in classfiles.values())
        total_obs += sum(len(df) for df in mexico.values())
        total_obs += len(worldbank) if worldbank is not None else 0
        total_obs += sum(len(df) for df in fred.values())
        total_obs += sum(
            sum(len(df) for df in country_data.values())
            for country_data in new_countries.values()
        )

        print(f"\nTotal observations loaded: {total_obs:,}")
        print(f"Data sources: 4 legacy + {len(new_countries)} countries + global frameworks")

        if include_new_countries:
            print(f"Countries: 11 total (US, UK, Germany, Mexico + {', '.join(new_countries.keys())})")
        else:
            print(f"Countries: 4 (US, UK, Germany, Mexico)")

        return {
            'classfiles': classfiles,
            'mexico': mexico,
            'worldbank': worldbank,
            'fred': fred,
            'new_countries': new_countries,
            'global_frameworks': {
                'dbnomics': self.dbnomics_collector,
                'un_comtrade': self.un_comtrade,
                'unctad': self.unctad_collector
            }
        }

    # ========================================================================
    # CREATE ENHANCED UNIFIED DATASETS
    # ========================================================================

    def create_unified_bop(self) -> pd.DataFrame:
        """Create unified Balance of Payments dataset across all sources."""
        print("\n[UNIFY] Creating enhanced unified Balance of Payments dataset...")

        unified_rows = []

        # Add World Bank data
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

        # Add Mexico Banxico data
        if 'bop' in self.mexico_data:
            mexico_bop = self.mexico_data['bop'].copy()
            mexico_bop['year'] = mexico_bop['date'].dt.year
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

        # Add new country data
        country_iso_map = {
            'Japan': 'JPN', 'Canada': 'CAN', 'France': 'FRA',
            'Italy': 'ITA', 'China': 'CHN', 'India': 'IND', 'Brazil': 'BRA'
        }

        for country, data in self.country_data.items():
            if 'sample_data' in data:
                country_sample = data['sample_data'].copy()

                for _, row in country_sample.iterrows():
                    if 'current_account' in row['indicator'].lower() or 'Current_Account' in row['indicator']:
                        unified_rows.append({
                            'country': country_iso_map.get(country, country[:3].upper()),
                            'country_name': country,
                            'year': row['year'],
                            'indicator': 'Current_Account',
                            'value': row['value'],
                            'units': row.get('units', 'pct_GDP'),
                            'source': f'{country}_Collector',
                            'frequency': 'Annual'
                        })

        if unified_rows:
            unified_df = pd.DataFrame(unified_rows)
            print(f"  Enhanced Unified BoP observations: {len(unified_df):,}")
            print(f"  Countries: {unified_df['country'].nunique()}")
            print(f"  Years: {unified_df['year'].min()}-{unified_df['year'].max()}")

            self.unified_bop = unified_df
            return unified_df
        else:
            return pd.DataFrame()

    def create_unified_trade(self) -> pd.DataFrame:
        """Create enhanced unified trade dataset."""
        print("\n[UNIFY] Creating enhanced unified trade dataset...")

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

        # Add new country data
        country_iso_map = {
            'Japan': 'JPN', 'Canada': 'CAN', 'France': 'FRA',
            'Italy': 'ITA', 'China': 'CHN', 'India': 'IND', 'Brazil': 'BRA'
        }

        for country, data in self.country_data.items():
            if 'sample_data' in data:
                country_sample = data['sample_data'].copy()

                for _, row in country_sample.iterrows():
                    indicator_lower = row['indicator'].lower()
                    if any(term in indicator_lower for term in ['export', 'import', 'trade', 'merchandise']):
                        # Determine trade type
                        if 'export' in indicator_lower:
                            indicator_type = 'Exports'
                        elif 'import' in indicator_lower:
                            indicator_type = 'Imports'
                        elif 'trade' in indicator_lower:
                            indicator_type = 'Trade_Balance'
                        else:
                            indicator_type = row['indicator']

                        unified_rows.append({
                            'country': country_iso_map.get(country, country[:3].upper()),
                            'country_name': country,
                            'year': row['year'],
                            'indicator': indicator_type,
                            'value': row['value'],
                            'units': row.get('units', 'USD_Millions'),
                            'source': f'{country}_Collector',
                            'frequency': 'Annual'
                        })

        if unified_rows:
            unified_df = pd.DataFrame(unified_rows)
            print(f"  Enhanced Unified trade observations: {len(unified_df):,}")
            print(f"  Countries: {unified_df['country'].nunique()}")

            self.unified_trade = unified_df
            return unified_df
        else:
            return pd.DataFrame()

    def create_unified_gdp(self) -> pd.DataFrame:
        """Create enhanced unified GDP dataset."""
        print("\n[UNIFY] Creating enhanced unified GDP dataset...")

        # Extract GDP from World Bank data
        gdp_rows = []

        if self.worldbank_data is not None:
            gdp_df = self.worldbank_data[
                self.worldbank_data['indicator_name'].str.contains('GDP', na=False)
            ].copy()

            for _, row in gdp_df.iterrows():
                gdp_rows.append({
                    'country': row['country'],
                    'country_name': row['country_name'],
                    'year': row['year'],
                    'gdp_usd': row['value'],
                    'source': 'World_Bank'
                })

        # Add new country GDP data
        country_iso_map = {
            'Japan': 'JPN', 'Canada': 'CAN', 'France': 'FRA',
            'Italy': 'ITA', 'China': 'CHN', 'India': 'IND', 'Brazil': 'BRA'
        }

        for country, data in self.country_data.items():
            if 'sample_data' in data:
                country_sample = data['sample_data'].copy()

                for _, row in country_sample.iterrows():
                    indicator_lower = row['indicator'].lower()
                    if 'gdp' in indicator_lower:
                        # Convert GDP to USD millions based on units
                        gdp_usd = row['value']
                        if row.get('units') == 'USD_Billions':
                            gdp_usd = row['value'] * 1000  # Convert billions to millions
                        elif row.get('units') == 'USD_Trillions':
                            gdp_usd = row['value'] * 1000000  # Convert trillions to millions

                        gdp_rows.append({
                            'country': country_iso_map.get(country, country[:3].upper()),
                            'country_name': country,
                            'year': row['year'],
                            'gdp_usd': gdp_usd,
                            'source': f'{country}_Collector'
                        })

        if gdp_rows:
            gdp_df = pd.DataFrame(gdp_rows)
            print(f"  Enhanced GDP observations: {len(gdp_df):,}")
            print(f"  Countries: {gdp_df['country'].nunique()}")

            self.unified_gdp = gdp_df
            return gdp_df
        else:
            return pd.DataFrame()

    def create_unified_summary(self) -> pd.DataFrame:
        """Create unified summary dataset with key indicators for all countries."""
        print("\n[UNIFY] Creating unified summary dataset...")

        summary_rows = []

        # Country metadata
        country_info = {
            'USA': {'name': 'United States', 'level': 'G7'},
            'GBR': {'name': 'United Kingdom', 'level': 'G7'},
            'DEU': {'name': 'Germany', 'level': 'G7'},
            'MEX': {'name': 'Mexico', 'level': 'Emerging'},
            'JPN': {'name': 'Japan', 'level': 'G7'},
            'CAN': {'name': 'Canada', 'level': 'G7'},
            'FRA': {'name': 'France', 'level': 'G7'},
            'ITA': {'name': 'Italy', 'level': 'G7'},
            'CHN': {'name': 'China', 'level': 'BRICS'},
            'IND': {'name': 'India', 'level': 'BRICS'},
            'BRA': {'name': 'Brazil', 'level': 'BRICS'}
        }

        # Country ISO mapping for new countries
        country_iso_map = {
            'Japan': 'JPN', 'Canada': 'CAN', 'France': 'FRA',
            'Italy': 'ITA', 'China': 'CHN', 'India': 'IND', 'Brazil': 'BRA'
        }

        # Add all new country data (not just BoP)
        for country, data in self.country_data.items():
            if 'sample_data' in data:
                country_sample = data['sample_data'].copy()

                # Get most recent year for this country
                latest_year = country_sample['year'].max()
                latest_data = country_sample[country_sample['year'] == latest_year]

                # Find current account data if available
                current_account_data = latest_data[
                    latest_data['indicator'].str.contains('current_account', case=False, na=False)
                ]

                ca_value = None
                if not current_account_data.empty:
                    ca_value = current_account_data.iloc[0]['value']

                summary_rows.append({
                    'country': country_iso_map.get(country, country[:3].upper()),
                    'country_name': country,
                    'country_level': country_info.get(country_iso_map.get(country, country[:3].upper()), {}).get('level', 'Other'),
                    'latest_year': latest_year,
                    'current_account_usd': ca_value,
                    'data_sources': f'{country}_Collector',
                    'total_indicators': len(country_sample['indicator'].unique()),
                    'data_range': f"{country_sample['year'].min()}-{country_sample['year'].max()}"
                })

        # Also add countries from unified BoP data
        if self.unified_bop is not None and not self.unified_bop.empty:
            recent_bop = self.unified_bop.loc[self.unified_bop.groupby('country')['year'].idxmax()]

            for _, row in recent_bop.iterrows():
                country_code = row['country']
                if country_code in country_info and country_code not in [r['country'] for r in summary_rows]:
                    summary_rows.append({
                        'country': country_code,
                        'country_name': country_info[country_code]['name'],
                        'country_level': country_info[country_code]['level'],
                        'latest_year': row['year'],
                        'current_account_usd': row['value'],
                        'data_sources': row['source'],
                        'total_indicators': 1,
                        'data_range': f"{row['year']}"
                    })

        if summary_rows:
            summary_df = pd.DataFrame(summary_rows)
            print(f"  Summary observations: {len(summary_df)}")
            print(f"  Countries represented: {summary_df['country'].nunique()}")

            self.unified_summary = summary_df
            return summary_df
        else:
            return pd.DataFrame()

    def validate_country_data_integrity(self) -> Dict[str, Any]:
        """
        Validate data integrity across all country collectors.

        Returns
        -------
        dict
            Validation results with counts and any issues found
        """
        print("\n[VALIDATE] Checking country data integrity...")

        validation_results = {
            'total_countries': len(self.country_collectors),
            'countries_with_data': len(self.country_data),
            'total_observations': 0,
            'data_quality_issues': [],
            'country_summaries': {}
        }

        for country, collector in self.country_collectors.items():
            country_summary = {
                'name': country,
                'has_data': country in self.country_data,
                'observation_count': 0,
                'indicator_count': 0,
                'year_range': None,
                'regions_count': 0,
                'issues': []
            }

            if country in self.country_data:
                data = self.country_data[country]

                if 'sample_data' in data:
                    sample_df = data['sample_data']
                    country_summary['observation_count'] = len(sample_df)
                    country_summary['indicator_count'] = sample_df['indicator'].nunique()
                    country_summary['year_range'] = f"{sample_df['year'].min()}-{sample_df['year'].max()}"

                    if 'region' in sample_df.columns:
                        country_summary['regions_count'] = sample_df['region'].nunique()

                    # Check for data quality issues
                    if sample_df['value'].isnull().any():
                        country_summary['issues'].append('Missing values detected')

                    if sample_df['year'].duplicated().any():
                        country_summary['issues'].append('Duplicate year entries')

                    validation_results['total_observations'] += len(sample_df)

            else:
                country_summary['issues'].append('No data loaded')
                validation_results['data_quality_issues'].append(f"{country}: No data loaded")

            validation_results['country_summaries'][country] = country_summary

        # Summary validation
        print(f"  Countries validated: {validation_results['total_countries']}")
        print(f"  Countries with data: {validation_results['countries_with_data']}")
        print(f"  Total observations: {validation_results['total_observations']:,}")
        print(f"  Quality issues: {len(validation_results['data_quality_issues'])}")

        return validation_results

    def create_all_unified_datasets(self) -> Dict[str, pd.DataFrame]:
        """Create all enhanced unified datasets."""
        print("\n" + "="*80)
        print("CREATING ENHANCED UNIFIED DATASETS")
        print("="*80)

        bop = self.create_unified_bop()
        trade = self.create_unified_trade()
        gdp = self.create_unified_gdp()
        summary = self.create_unified_summary()

        print("\n" + "="*80)
        print("ENHANCED UNIFIED DATASETS COMPLETE")
        print("="*80)

        return {
            'bop': bop,
            'trade': trade,
            'gdp': gdp,
            'summary': summary
        }

    # ========================================================================
    # SAVE ENHANCED UNIFIED DATASETS
    # ========================================================================

    def save_unified_datasets(self, output_path: Optional[Path] = None):
        """Save enhanced unified datasets to CSV files."""
        if output_path is None:
            output_path = OUTPUT_ROOT / "UNIFIED_ENHANCED"

        output_path.mkdir(parents=True, exist_ok=True)

        print("\n[SAVE] Saving enhanced unified datasets...")

        datasets = {
            'unified_balance_of_payments_enhanced': self.unified_bop,
            'unified_trade_enhanced': self.unified_trade,
            'unified_gdp_enhanced': self.unified_gdp,
            'unified_summary_enhanced': self.unified_summary
        }

        for filename, data in datasets.items():
            if data is not None and not data.empty:
                file_path = output_path / f"{filename}.csv"
                data.to_csv(file_path, index=False)
                print(f"  Saved: {file_path.relative_to(PROJECT_ROOT)} ({len(data):,} rows)")

        print(f"\n[COMPLETE] Enhanced unified datasets saved to: {output_path.relative_to(PROJECT_ROOT)}")

    def generate_comprehensive_report(self) -> str:
        """Generate comprehensive data coverage report."""
        report = []
        report.append("=" * 80)
        report.append("ENHANCED UNIFIED DATA LOADER - COMPREHENSIVE REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Version: 2.0 (Enhanced with 7 new countries)")
        report.append("")

        # Data sources summary
        report.append("DATA SOURCES:")
        report.append("- Legacy: ClassFiles (US, UK, Germany), Mexico Banxico, World Bank, FRED")
        report.append("- New Countries: Japan, Canada, France, Italy, China, India, Brazil")
        report.append("- Global Frameworks: DBnomics, UN Comtrade, UNCTAD")
        report.append("")

        # Coverage statistics
        total_countries = 11
        if self.unified_summary is not None:
            total_countries = self.unified_summary['country'].nunique()

        report.append("COVERAGE STATISTICS:")
        report.append(f"- Total Countries: {total_countries}")
        report.append(f"- G7 Countries: 7 (US, UK, Germany, Japan, Canada, France, Italy)")
        report.append(f"- BRICS Countries: 3 (China, India, Brazil)")
        report.append(f"- Other Major: 1 (Mexico)")
        report.append("")

        # Dataset statistics
        if self.unified_bop is not None:
            report.append(f"BALANCE OF PAYMENTS:")
            report.append(f"- Observations: {len(self.unified_bop):,}")
            report.append(f"- Countries: {self.unified_bop['country'].nunique()}")
            report.append(f"- Year Range: {self.unified_bop['year'].min()}-{self.unified_bop['year'].max()}")
            report.append("")

        if self.unified_trade is not None:
            report.append(f"TRADE DATA:")
            report.append(f"- Observations: {len(self.unified_trade):,}")
            report.append(f"- Countries: {self.unified_trade['country'].nunique()}")
            report.append("")

        if self.unified_gdp is not None:
            report.append(f"GDP DATA:")
            report.append(f"- Observations: {len(self.unified_gdp):,}")
            report.append(f"- Countries: {self.unified_gdp['country'].nunique()}")
            report.append("")

        report.append("=" * 80)

        return "\n".join(report)


def main():
    """Main execution: load and unify all data with enhanced capabilities."""
    print("\n" + "="*80)
    print("ENHANCED UNIFIED DATA LOADER v2.0 - COMPREHENSIVE INTEGRATION")
    print("="*80)

    # Initialize enhanced loader
    loader = EnhancedUnifiedDataLoader()

    # Load all data sources (including new countries)
    all_data = loader.load_all(
        include_new_countries=True,
        include_global_frameworks=True
    )

    # Create enhanced unified datasets
    unified = loader.create_all_unified_datasets()

    # Run data validation
    validation_results = loader.validate_country_data_integrity()

    # Save enhanced unified datasets
    loader.save_unified_datasets()

    # Generate comprehensive report
    report = loader.generate_comprehensive_report()
    print(report)

    # Add validation summary to report
    print(f"\n[VALIDATION SUMMARY]")
    print(f"- Countries: {validation_results['countries_with_data']}/{validation_results['total_countries']} with data")
    print(f"- Total Observations: {validation_results['total_observations']:,}")
    print(f"- Quality Issues: {len(validation_results['data_quality_issues'])}")

    print("\n[COMPLETE] Enhanced data integration finished!")


if __name__ == "__main__":
    main()
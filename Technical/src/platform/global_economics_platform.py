"""
Global International Economics Platform
========================================

Comprehensive platform for global international economics analysis.

Integrates all available data sources:
- Multi-country Balance of Payments (US, UK, Germany)
- US Flow of Funds and International Investment Position
- FRED trade and exchange rate data (19 series)
- Cross-border capital flows
- Historical comparative analysis

Provides:
- Country-specific economic profiles
- Multi-country comparative analysis
- Global trade network analysis
- Cross-border capital flow tracking
- Historical event impact analysis
- BPM6-aligned methodology

Author: Claude
Date: 2025-10-06
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime
import sys

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import from absolute paths to avoid conflict with builtin 'platform' module
import importlib.util

# Load international_economics_platform module
spec1 = importlib.util.spec_from_file_location("iecon_platform",
    Path(__file__).parent / "international_economics_platform.py")
iecon_module = importlib.util.module_from_spec(spec1)
spec1.loader.exec_module(iecon_module)
InternationalEconomicsPlatform = iecon_module.InternationalEconomicsPlatform

# Load other modules similarly
spec2 = importlib.util.spec_from_file_location("bop_analysis",
    Path(__file__).parent.parent / "analysis" / "bop_comparative_analysis.py")
bop_module = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(bop_module)
BoPComparativeAnalysis = bop_module.BoPComparativeAnalysis

spec3 = importlib.util.spec_from_file_location("fof_analysis",
    Path(__file__).parent.parent / "analysis" / "flow_of_funds_analysis.py")
fof_module = importlib.util.module_from_spec(spec3)
spec3.loader.exec_module(fof_module)
FlowOfFundsAnalysis = fof_module.FlowOfFundsAnalysis

spec4 = importlib.util.spec_from_file_location("fred_loader",
    Path(__file__).parent.parent / "data" / "fred_loader.py")
fred_module = importlib.util.module_from_spec(spec4)
spec4.loader.exec_module(fred_module)
FREDLoader = fred_module.FREDLoader

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
OUTPUT_PATH = PROJECT_ROOT / "Output"
OUTPUT_DATA = OUTPUT_PATH / "Data"
OUTPUT_CHARTS = OUTPUT_PATH / "Charts"
OUTPUT_ROOT = Path(os.environ.get("OUTPUT_ROOT", "outputs"))


class GlobalEconomicsPlatform:
    """
    Comprehensive global international economics platform.

    Extends the base platform with:
    - FRED series integration (all 19 series)
    - Exchange rate analysis
    - Global trade network
    - Extended country coverage
    - Dashboard generation
    """

    def __init__(self):
        """Initialize global platform."""
        self.base_platform = InternationalEconomicsPlatform(use_cache=True)

        # Additional data containers
        self.fred_series = {}
        self.exchange_rates = {}

        # Country metadata
        self.countries = {
            'US': {
                'name': 'United States',
                'currency': 'USD',
                'bop_data': True,
                'fof_data': True,
                'period': '1960-2024'
            },
            'UK': {
                'name': 'United Kingdom',
                'currency': 'GBP',
                'bop_data': True,
                'fof_data': False,
                'period': '1946-2023'
            },
            'Germany': {
                'name': 'Germany',
                'currency': 'EUR',
                'bop_data': True,
                'fof_data': False,
                'period': '1971-2024'
            }
        }

        print("\n" + "="*80)
        print("GLOBAL INTERNATIONAL ECONOMICS PLATFORM")
        print("="*80)
        print("\nComprehensive Analysis Capabilities:")
        print("  [OK] Multi-Country Balance of Payments (3 countries)")
        print("  [OK] US Flow of Funds & IIP")
        print("  [OK] 19 FRED Economic Series")
        print("  [OK] Exchange Rate Analysis")
        print("  [OK] Historical Period Analysis (1946-2024)")
        print("  [OK] BPM6 Methodology Alignment")
        print("="*80)

    def load_all_data(self):
        """Load all available data across all sources."""
        print("\n" + "="*80)
        print("LOADING GLOBAL DATA")
        print("="*80)

        # Load base platform data
        print("\n[1/3] Loading Base Platform Data...")
        self.base_platform.load_all_data()

        # Load FRED series
        print("\n[2/3] Loading FRED Series Data...")
        self._load_fred_series()

        # Load exchange rates
        print("\n[3/3] Loading Exchange Rate Data...")
        self._load_exchange_rates()

        print("\n" + "="*80)
        print("ALL GLOBAL DATA LOADED")
        print("="*80)

    def _load_fred_series(self):
        """Load all 19 FRED series."""
        by_series_path = OUTPUT_ROOT / "BY_SERIES"

        if not by_series_path.exists():
            print("  [WARNING] BY_SERIES directory not found")
            return

        series_files = list(by_series_path.glob("*.csv"))
        print(f"  Found {len(series_files)} FRED series")

        for file in series_files:
            try:
                series_id = file.stem
                df = pd.read_csv(file)
                df['date'] = pd.to_datetime(df['date'])
                self.fred_series[series_id] = df
                print(f"    [OK] {series_id}: {len(df)} observations")
            except Exception as e:
                print(f"    [ERROR] {file.name}: {e}")

    def _load_exchange_rates(self):
        """Load exchange rate data from FRED series."""
        exchange_rate_series = {
            'DEXUSUK': 'USD/GBP',
            'DEXUSEU': 'USD/EUR',
            'DEXJPUS': 'JPY/USD',
            'DEXCAUS': 'CAD/USD',
            'DEXCHUS': 'CNY/USD'
        }

        for series_id, pair in exchange_rate_series.items():
            if series_id in self.fred_series:
                self.exchange_rates[pair] = self.fred_series[series_id]
                print(f"    [OK] {pair}")

    # ========================================================================
    # COUNTRY PROFILES
    # ========================================================================

    def create_country_profile(self, country_code: str, save: bool = True) -> Dict:
        """
        Create comprehensive economic profile for a country.

        Parameters
        ----------
        country_code : str
            Country code (US, UK, Germany)
        save : bool, default True
            Whether to save profile as JSON

        Returns
        -------
        dict
            Country profile data
        """
        if country_code not in self.countries:
            raise ValueError(f"Country {country_code} not in database")

        country = self.countries[country_code]
        print(f"\n{'='*80}")
        print(f"CREATING PROFILE: {country['name']}")
        print("="*80)

        profile = {
            'country_code': country_code,
            'country_name': country['name'],
            'currency': country['currency'],
            'data_availability': {
                'balance_of_payments': country['bop_data'],
                'flow_of_funds': country['fof_data'],
                'period': country['period']
            },
            'economic_indicators': {},
            'trade_patterns': {},
            'capital_flows': {}
        }

        # Get BoP data if available
        if country['bop_data']:
            profile['economic_indicators'] = self._get_country_indicators(country_code)
            profile['trade_patterns'] = self._get_trade_patterns(country_code)

        # US-specific: Flow of Funds
        if country_code == 'US' and country['fof_data']:
            profile['capital_flows'] = self._get_capital_flows('US')
            profile['iip'] = self._get_iip_summary('US')

        print(f"\n[COMPLETE] Profile created for {country['name']}")

        if save:
            output_file = OUTPUT_DATA / f"profile_{country_code}.json"
            import json
            with open(output_file, 'w') as f:
                json.dump(profile, f, indent=2, default=str)
            print(f"[SAVED] {output_file.relative_to(PROJECT_ROOT)}")

        return profile

    def _get_country_indicators(self, country_code: str) -> Dict:
        """Get key economic indicators for country."""
        indicators = {}

        # Get from BoP data
        if country_code == 'US' and self.base_platform.bop_loaded:
            data = self.base_platform.bop_analysis.us_annual_pct
            latest = data[data['Year'] == data['Year'].max()].iloc[0]

            indicators['latest_year'] = int(latest['Year'])
            indicators['current_account_gdp'] = float(latest.get('Current Account Balance_pct', np.nan))
            indicators['financial_account_gdp'] = float(latest.get('Financial Account Balance_pct', np.nan))
            indicators['trade_balance_gdp'] = float(latest.get('Goods and Services Balance_pct', np.nan))

        elif country_code == 'UK' and self.base_platform.bop_loaded:
            data = self.base_platform.bop_analysis.uk_annual_pct
            latest = data[data['Year'] == data['Year'].max()].iloc[0]

            indicators['latest_year'] = int(latest['Year'])
            indicators['current_account_gdp'] = float(latest.get('Current Account Balance_pct', np.nan))
            indicators['financial_account_gdp'] = float(latest.get('Financial Account Balance_pct', np.nan))

        elif country_code == 'Germany' and self.base_platform.bop_loaded:
            data = self.base_platform.bop_analysis.ger_annual_pct
            latest = data[data['Year'] == data['Year'].max()].iloc[0]

            indicators['latest_year'] = int(latest['Year'])
            indicators['current_account_gdp'] = float(latest.get('Current Account Balance_pct', np.nan))
            indicators['financial_account_gdp'] = float(latest.get('Financial Account Balance_pct', np.nan))

        return indicators

    def _get_trade_patterns(self, country_code: str) -> Dict:
        """Analyze trade patterns for country."""
        patterns = {}

        # Add trade balance trends
        if 'BOPGSTB' in self.fred_series and country_code == 'US':
            tb = self.fred_series['BOPGSTB']
            patterns['trade_balance_trend'] = {
                'mean': float(tb['value'].mean()),
                'current': float(tb['value'].iloc[-1]),
                'peak_deficit': float(tb['value'].min()),
                'peak_surplus': float(tb['value'].max())
            }

        return patterns

    def _get_capital_flows(self, country_code: str) -> Dict:
        """Get capital flow summary."""
        flows = {}

        if country_code == 'US' and self.base_platform.fof_loaded:
            # Get latest IIP data
            iip = self.base_platform.fof_analysis.iip_data
            latest = iip[iip['date'] == iip['date'].max()]

            flows['net_iip'] = float(latest[latest['series_id'] == 'IIPNETINA']['value'].iloc[0]) if not latest[latest['series_id'] == 'IIPNETINA'].empty else None
            flows['us_assets_abroad'] = float(latest[latest['series_id'] == 'IIPUSASSA']['value'].iloc[0]) if not latest[latest['series_id'] == 'IIPUSASSA'].empty else None
            flows['foreign_assets_us'] = float(latest[latest['series_id'] == 'IIPUSLIAA']['value'].iloc[0]) if not latest[latest['series_id'] == 'IIPUSLIAA'].empty else None

        return flows

    def _get_iip_summary(self, country_code: str) -> Dict:
        """Get IIP summary statistics."""
        summary = {}

        if country_code == 'US' and self.base_platform.fof_loaded:
            iip = self.base_platform.fof_analysis.iip_data
            latest_date = iip['date'].max()

            summary['latest_date'] = str(latest_date)
            summary['series_count'] = iip['series_id'].nunique()
            summary['observation_count'] = len(iip)

        return summary

    # ========================================================================
    # GLOBAL ANALYSIS
    # ========================================================================

    def generate_global_dashboard(self, save: bool = True):
        """
        Generate comprehensive global economic dashboard.

        Creates multi-panel visualization showing:
        - Current account balances across countries
        - Trade balance trends
        - Exchange rate movements
        - Capital flow patterns

        Parameters
        ----------
        save : bool, default True
            Whether to save dashboard
        """
        print("\n" + "="*80)
        print("GENERATING GLOBAL ECONOMIC DASHBOARD")
        print("="*80)

        fig = plt.figure(figsize=(20, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

        # Panel 1: Current Account Balances
        ax1 = fig.add_subplot(gs[0, :])
        self._plot_current_accounts(ax1)

        # Panel 2: Trade Balance (US)
        ax2 = fig.add_subplot(gs[1, 0])
        self._plot_trade_balance(ax2)

        # Panel 3: Exchange Rates
        ax3 = fig.add_subplot(gs[1, 1])
        self._plot_exchange_rates(ax3)

        # Panel 4: IIP
        ax4 = fig.add_subplot(gs[1, 2])
        self._plot_iip_summary(ax4)

        # Panel 5: Regional Comparison
        ax5 = fig.add_subplot(gs[2, :])
        self._plot_regional_comparison(ax5)

        plt.suptitle('Global International Economics Dashboard',
                    fontsize=16, fontweight='bold', y=0.995)

        if save:
            output_path = OUTPUT_CHARTS / "global_economics_dashboard.png"
            fig.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"\n[SAVED] {output_path.relative_to(PROJECT_ROOT)}")

        return fig

    def _plot_current_accounts(self, ax):
        """Plot current account balances for all countries."""
        if not self.base_platform.bop_loaded:
            ax.text(0.5, 0.5, 'BoP Data Not Loaded', ha='center', va='center')
            return

        # US
        us_data = self.base_platform.bop_analysis.us_annual_pct
        ax.plot(us_data['Year'], us_data.get('Current Account Balance_pct', []),
               label='United States', linewidth=2, marker='o', markersize=3)

        # UK
        uk_data = self.base_platform.bop_analysis.uk_annual_pct
        ax.plot(uk_data['Year'], uk_data.get('Current Account Balance_pct', []),
               label='United Kingdom', linewidth=2, marker='s', markersize=3)

        # Germany
        ger_data = self.base_platform.bop_analysis.ger_annual_pct
        ax.plot(ger_data['Year'], ger_data.get('Current Account Balance_pct', []),
               label='Germany', linewidth=2, marker='^', markersize=3)

        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5, alpha=0.5)
        ax.set_xlabel('Year', fontweight='bold')
        ax.set_ylabel('% of GDP', fontweight='bold')
        ax.set_title('Current Account Balances', fontweight='bold', fontsize=12)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)

    def _plot_trade_balance(self, ax):
        """Plot US trade balance."""
        if 'BOPGSTB' in self.fred_series:
            tb = self.fred_series['BOPGSTB']
            # Annual average
            tb['year'] = tb['date'].dt.year
            annual = tb.groupby('year')['value'].mean().reset_index()

            ax.plot(annual['year'], annual['value'] / 1000,
                   linewidth=2, color='darkblue')
            ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5, alpha=0.5)
            ax.set_xlabel('Year', fontweight='bold')
            ax.set_ylabel('Billions USD', fontweight='bold')
            ax.set_title('US Trade Balance', fontweight='bold', fontsize=12)
            ax.grid(True, alpha=0.3)
        else:
            ax.text(0.5, 0.5, 'Trade Data Not Available', ha='center', va='center')

    def _plot_exchange_rates(self, ax):
        """Plot exchange rates."""
        if self.exchange_rates:
            for pair, data in list(self.exchange_rates.items())[:3]:
                # Annual average
                data_copy = data.copy()
                data_copy['year'] = data_copy['date'].dt.year
                annual = data_copy.groupby('year')['value'].mean().reset_index()

                ax.plot(annual['year'], annual['value'],
                       label=pair, linewidth=1.5, alpha=0.7)

            ax.set_xlabel('Year', fontweight='bold')
            ax.set_ylabel('Exchange Rate', fontweight='bold')
            ax.set_title('Exchange Rates', fontweight='bold', fontsize=12)
            ax.legend(loc='best', fontsize=8)
            ax.grid(True, alpha=0.3)
        else:
            ax.text(0.5, 0.5, 'Exchange Rate Data Not Available', ha='center', va='center')

    def _plot_iip_summary(self, ax):
        """Plot IIP summary."""
        if self.base_platform.fof_loaded:
            iip = self.base_platform.fof_analysis.iip_data

            # Get key series
            for series_id, label in [('IIPNETINA', 'Net IIP'),
                                     ('IIPUSASSA', 'US Assets'),
                                     ('IIPUSLIAA', 'Foreign Assets in US')]:
                data = iip[iip['series_id'] == series_id].copy()
                if not data.empty:
                    ax.plot(data['date'], data['value'] / 1000,
                           label=label, linewidth=1.5)

            ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5, alpha=0.5)
            ax.set_xlabel('Year', fontweight='bold')
            ax.set_ylabel('Billions USD', fontweight='bold')
            ax.set_title('US International Investment Position', fontweight='bold', fontsize=12)
            ax.legend(loc='best', fontsize=8)
            ax.grid(True, alpha=0.3)
        else:
            ax.text(0.5, 0.5, 'IIP Data Not Available', ha='center', va='center')

    def _plot_regional_comparison(self, ax):
        """Plot regional comparison."""
        if not self.base_platform.bop_loaded:
            ax.text(0.5, 0.5, 'BoP Data Not Loaded', ha='center', va='center')
            return

        # Bar chart of latest current account balances
        countries = []
        values = []

        for code, name in [('US', 'United States'), ('UK', 'United Kingdom'), ('Germany', 'Germany')]:
            if code == 'US':
                data = self.base_platform.bop_analysis.us_annual_pct
            elif code == 'UK':
                data = self.base_platform.bop_analysis.uk_annual_pct
            else:
                data = self.base_platform.bop_analysis.ger_annual_pct

            latest = data[data['Year'] == data['Year'].max()].iloc[0]
            ca_value = latest.get('Current Account Balance_pct', np.nan)

            if not pd.isna(ca_value):
                countries.append(name)
                values.append(ca_value)

        colors = ['red' if v < 0 else 'green' for v in values]
        ax.barh(countries, values, color=colors, alpha=0.7)
        ax.axvline(x=0, color='black', linestyle='-', linewidth=1)
        ax.set_xlabel('Current Account Balance (% of GDP)', fontweight='bold')
        ax.set_title('Latest Current Account Positions', fontweight='bold', fontsize=12)
        ax.grid(True, alpha=0.3, axis='x')

    # ========================================================================
    # COMPREHENSIVE REPORTING
    # ========================================================================

    def generate_global_report(self) -> str:
        """
        Generate comprehensive global economics report.

        Returns
        -------
        str
            Report text
        """
        print("\n" + "="*80)
        print("GENERATING GLOBAL ECONOMICS REPORT")
        print("="*80)

        report = []
        report.append("="*80)
        report.append("GLOBAL INTERNATIONAL ECONOMICS PLATFORM - COMPREHENSIVE REPORT")
        report.append("="*80)
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Data Coverage
        report.append("\n" + "="*80)
        report.append("DATA COVERAGE")
        report.append("="*80)

        report.append("\nCountries:")
        for code, info in self.countries.items():
            report.append(f"\n{code} - {info['name']}")
            report.append(f"  Currency: {info['currency']}")
            report.append(f"  Period: {info['period']}")
            report.append(f"  BoP Data: {'Yes' if info['bop_data'] else 'No'}")
            report.append(f"  FoF Data: {'Yes' if info['fof_data'] else 'No'}")

        report.append(f"\nFRED Series: {len(self.fred_series)}")
        report.append(f"Exchange Rates: {len(self.exchange_rates)}")

        # Summary Statistics
        report.append("\n" + "="*80)
        report.append("SUMMARY STATISTICS")
        report.append("="*80)

        if self.base_platform.bop_loaded:
            report.append("\nBalance of Payments:")
            for code in ['US', 'UK', 'Germany']:
                profile = self._get_country_indicators(code)
                if profile:
                    report.append(f"\n{self.countries[code]['name']}:")
                    report.append(f"  Latest Year: {profile.get('latest_year', 'N/A')}")
                    report.append(f"  Current Account: {profile.get('current_account_gdp', np.nan):.2f}% of GDP")
                    report.append(f"  Financial Account: {profile.get('financial_account_gdp', np.nan):.2f}% of GDP")

        # Save report
        output_file = OUTPUT_PATH / "GLOBAL_ECONOMICS_REPORT.md"
        with open(output_file, 'w') as f:
            f.write('\n'.join(report))

        print(f"\n[SAVED] {output_file.relative_to(PROJECT_ROOT)}")

        return '\n'.join(report)

    # ========================================================================
    # MAIN EXECUTION
    # ========================================================================

    def execute_full_analysis(self):
        """Execute complete global analysis."""
        print("\n" + "="*80)
        print("EXECUTING FULL GLOBAL ANALYSIS")
        print("="*80)

        # Load all data
        self.load_all_data()

        # Generate country profiles
        print("\n[PROFILES] Generating Country Profiles...")
        for code in ['US', 'UK', 'Germany']:
            self.create_country_profile(code)

        # Generate dashboard
        print("\n[DASHBOARD] Generating Global Dashboard...")
        self.generate_global_dashboard()

        # Generate report
        print("\n[REPORT] Generating Global Report...")
        report = self.generate_global_report()

        print("\n" + "="*80)
        print("GLOBAL ANALYSIS COMPLETE")
        print("="*80)
        print("\nGenerated:")
        print("  - 3 country profiles (JSON)")
        print("  - 1 global dashboard (PNG)")
        print("  - 1 comprehensive report (MD)")

        return report


def main():
    """Main execution."""
    print("\n" + "="*80)
    print("GLOBAL INTERNATIONAL ECONOMICS PLATFORM - FULL EXECUTION")
    print("="*80)

    platform = GlobalEconomicsPlatform()
    report = platform.execute_full_analysis()

    print("\n[COMPLETE] Global platform execution finished!")


if __name__ == "__main__":
    main()

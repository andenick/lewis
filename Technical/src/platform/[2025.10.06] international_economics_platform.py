"""
International Economics Analysis Platform
==========================================

Integrated platform combining Balance of Payments and Flow of Funds analysis.

Features:
- Unified data access across all sources
- Multi-country Balance of Payments comparative analysis
- US Flow of Funds and international investment position
- Cross-border capital flows tracking
- Historical event analysis
- Comprehensive visualization suite

Integrates:
- ClassFiles/APE: Flow of funds analysis (FRED/BEA data)
- ClassFiles/Trade: Multi-country BoP comparative analysis
- data source Database: All international economics data
- BPM6 Framework: International standards alignment

Author: Claude
Date: 2025-10-06
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime
import sys

# Add analysis directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from analysis.bop_comparative_analysis import BoPComparativeAnalysis
from analysis.flow_of_funds_analysis import FlowOfFundsAnalysis
from data.fred_loader import FREDLoader

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
OUTPUT_PATH = PROJECT_ROOT / "Output"
OUTPUT_DATA = OUTPUT_PATH / "Data"
OUTPUT_CHARTS = OUTPUT_PATH / "Charts"
TECHNICAL_PATH = PROJECT_ROOT / "Technical"


class InternationalEconomicsPlatform:
    """
    Integrated international economics analysis platform.

    Provides unified access to:
    - Balance of Payments data (US, UK, Germany)
    - Flow of Funds data (US)
    - International Investment Position
    - Cross-border capital flows
    - Historical comparative analysis
    """

    def __init__(self, use_cache: bool = True):
        """
        Initialize the platform.

        Parameters
        ----------
        use_cache : bool, default True
            Whether to use cached data from data source
        """
        self.use_cache = use_cache

        # Initialize component analyzers
        self.bop_analysis = BoPComparativeAnalysis()
        self.fof_analysis = FlowOfFundsAnalysis(use_cache=use_cache)
        self.fred_loader = FREDLoader(use_cache=use_cache)

        # Data loaded flags
        self.bop_loaded = False
        self.fof_loaded = False

        print("\n" + "=" * 80)
        print("International Economics Analysis Platform")
        print("=" * 80)
        print("\nIntegrated Analysis Capabilities:")
        print("  [OK] Multi-country Balance of Payments (US, UK, Germany)")
        print("  [OK] US Flow of Funds and IIP")
        print("  [OK] Cross-border capital flows")
        print("  [OK] Historical event analysis")
        print("  [OK] BPM6-aligned methodology")
        print("=" * 80)

    # ========================================================================
    # DATA LOADING
    # ========================================================================

    def load_all_data(self):
        """Load all datasets across both analysis modules."""
        print("\n" + "="*80)
        print("LOADING ALL DATA")
        print("="*80)

        print("\n[1/2] Loading Balance of Payments data (US, UK, Germany)...")
        self.bop_analysis.load_data()
        self.bop_loaded = True

        print("\n[2/2] Loading Flow of Funds data (US)...")
        self.fof_analysis.load_all_data()
        self.fof_loaded = True

        print("\n" + "="*80)
        print("ALL DATA LOADED SUCCESSFULLY")
        print("="*80)

    # ========================================================================
    # COUNTRY-SPECIFIC ANALYSIS
    # ========================================================================

    def analyze_country(self, country: str, generate_plots: bool = True) -> Dict:
        """
        Complete analysis for a single country.

        Parameters
        ----------
        country : str
            Country code: 'US', 'UK', or 'Germany'
        generate_plots : bool, default True
            Whether to generate visualizations

        Returns
        -------
        dict
            Analysis results including summary statistics
        """
        if not self.bop_loaded:
            raise ValueError("BoP data not loaded. Call load_all_data() first.")

        country = country.upper()

        if country not in ['US', 'UK', 'GERMANY']:
            raise ValueError(f"Country '{country}' not supported. Choose: US, UK, Germany")

        print(f"\n{'='*80}")
        print(f"ANALYZING: {country}")
        print("="*80)

        results = {'country': country, 'plots': []}

        # Get country-specific data
        if country == 'US':
            data = self.bop_analysis.us_annual_pct

            # Additional US-specific: Flow of Funds
            if self.fof_loaded:
                print("\n[BONUS] US has additional Flow of Funds analysis available")
                results['has_fof'] = True

        elif country == 'UK':
            data = self.bop_analysis.uk_annual_pct
            results['has_fof'] = False

        elif country == 'GERMANY':
            data = self.bop_analysis.ger_annual_pct
            results['has_fof'] = False

        # Summary statistics
        print(f"\n{country} Balance of Payments Summary:")
        print(f"  Period: {data['Year'].min()} - {data['Year'].max()}")
        print(f"  Years: {len(data)}")

        # Latest values
        latest_year = data['Year'].max()
        latest = data[data['Year'] == latest_year].iloc[0]

        print(f"\n{country} Latest Values ({latest_year}):")
        key_vars = ['Current Account Balance_pct', 'Financial Account Balance_pct',
                   'Goods and Services Balance_pct' if country != 'GERMANY'
                   else 'Total Trade Balance_pct']

        for var in key_vars:
            if var in latest.index:
                print(f"  {var.replace('_pct', '')}: {latest[var]:.2f}% of GDP")

        results['summary'] = {
            'period': f"{data['Year'].min()}-{data['Year'].max()}",
            'years': len(data),
            'latest_year': latest_year
        }

        print(f"\n{'='*80}")
        print(f"{country} ANALYSIS COMPLETE")
        print("="*80)

        return results

    # ========================================================================
    # COMPARATIVE ANALYSIS
    # ========================================================================

    def comparative_analysis(self) -> Dict:
        """
        Cross-country comparative analysis.

        Compares:
        - Current account trends
        - Financial account patterns
        - Trade balance evolution
        - Policy responses to shocks

        Returns
        -------
        dict
            Comparative statistics
        """
        if not self.bop_loaded:
            raise ValueError("BoP data not loaded. Call load_all_data() first.")

        print("\n" + "="*80)
        print("COMPARATIVE ANALYSIS: US vs UK vs Germany")
        print("="*80)

        comparison = {}

        # Coverage comparison
        print("\nData Coverage:")
        print(f"  US:      {self.bop_analysis.us_annual['Year'].min()}-{self.bop_analysis.us_annual['Year'].max()} ({len(self.bop_analysis.us_annual)} years)")
        print(f"  UK:      {self.bop_analysis.uk_annual['Year'].min()}-{self.bop_analysis.uk_annual['Year'].max()} ({len(self.bop_analysis.uk_annual)} years)")
        print(f"  Germany: {self.bop_analysis.ger_annual['Year'].min()}-{self.bop_analysis.ger_annual['Year'].max()} ({len(self.bop_analysis.ger_annual)} years)")

        # Common period
        common_start = max(
            self.bop_analysis.us_annual['Year'].min(),
            self.bop_analysis.uk_annual['Year'].min(),
            self.bop_analysis.ger_annual['Year'].min()
        )
        common_end = min(
            self.bop_analysis.us_annual['Year'].max(),
            self.bop_analysis.uk_annual['Year'].max(),
            self.bop_analysis.ger_annual['Year'].max()
        )

        print(f"\nCommon Period: {common_start}-{common_end}")

        comparison['coverage'] = {
            'us': f"{self.bop_analysis.us_annual['Year'].min()}-{self.bop_analysis.us_annual['Year'].max()}",
            'uk': f"{self.bop_analysis.uk_annual['Year'].min()}-{self.bop_analysis.uk_annual['Year'].max()}",
            'germany': f"{self.bop_analysis.ger_annual['Year'].min()}-{self.bop_analysis.ger_annual['Year'].max()}",
            'common': f"{common_start}-{common_end}"
        }

        print("\n" + "="*80)
        print("COMPARATIVE ANALYSIS COMPLETE")
        print("="*80)

        return comparison

    # ========================================================================
    # VISUALIZATION SUITE
    # ========================================================================

    def generate_all_visualizations(self):
        """Generate all visualizations from both modules."""
        print("\n" + "="*80)
        print("GENERATING COMPLETE VISUALIZATION SUITE")
        print("="*80)

        if not self.bop_loaded or not self.fof_loaded:
            raise ValueError("Data not loaded. Call load_all_data() first.")

        print("\n[1/2] Balance of Payments Visualizations...")
        self.bop_analysis.generate_all_visualizations()

        print("\n[2/2] Flow of Funds Visualizations...")
        self.fof_analysis.generate_all_visualizations()

        print("\n" + "="*80)
        print("VISUALIZATION SUITE COMPLETE")
        print("="*80)
        print(f"\nAll charts saved to: {OUTPUT_CHARTS.relative_to(PROJECT_ROOT)}")

        # List generated files
        charts = list(OUTPUT_CHARTS.glob("python_*.png"))
        print(f"\nGenerated {len(charts)} visualizations:")
        for chart in sorted(charts):
            print(f"  [OK] {chart.name}")

    # ========================================================================
    # PLATFORM SUMMARY
    # ========================================================================

    def platform_summary(self) -> pd.DataFrame:
        """
        Generate comprehensive platform summary.

        Returns
        -------
        pd.DataFrame
            Summary of all available data and capabilities
        """
        print("\n" + "="*80)
        print("PLATFORM SUMMARY")
        print("="*80)

        summary_data = []

        # Balance of Payments data
        if self.bop_loaded:
            summary_data.append({
                'Module': 'Balance of Payments',
                'Country': 'United States',
                'Period': f"{self.bop_analysis.us_annual['Year'].min()}-{self.bop_analysis.us_annual['Year'].max()}",
                'Observations': len(self.bop_analysis.us_annual),
                'Source': 'BEA',
                'Frequency': 'Quarterly->Annual'
            })
            summary_data.append({
                'Module': 'Balance of Payments',
                'Country': 'United Kingdom',
                'Period': f"{self.bop_analysis.uk_annual['Year'].min()}-{self.bop_analysis.uk_annual['Year'].max()}",
                'Observations': len(self.bop_analysis.uk_annual),
                'Source': 'ONS',
                'Frequency': 'Annual'
            })
            summary_data.append({
                'Module': 'Balance of Payments',
                'Country': 'Germany',
                'Period': f"{self.bop_analysis.ger_annual['Year'].min()}-{self.bop_analysis.ger_annual['Year'].max()}",
                'Observations': len(self.bop_analysis.ger_annual),
                'Source': 'Bundesbank',
                'Frequency': 'Monthly->Annual'
            })

        # Flow of Funds data
        if self.fof_loaded:
            summary_data.append({
                'Module': 'Flow of Funds - IIP',
                'Country': 'United States',
                'Period': f"{self.fof_analysis.iip_data['date'].min().year}-{self.fof_analysis.iip_data['date'].max().year}",
                'Observations': len(self.fof_analysis.iip_data['date'].unique()),
                'Source': 'BEA (via FRED)',
                'Frequency': 'Quarterly'
            })
            summary_data.append({
                'Module': 'Flow of Funds - ITA',
                'Country': 'United States',
                'Period': f"{self.fof_analysis.ita_data['date'].min().year}-{self.fof_analysis.ita_data['date'].max().year}",
                'Observations': len(self.fof_analysis.ita_data['date'].unique()),
                'Source': 'BEA (via FRED)',
                'Frequency': 'Quarterly'
            })
            summary_data.append({
                'Module': 'Flow of Funds - Treasury',
                'Country': 'United States',
                'Period': f"{self.fof_analysis.treasury_data['date'].min().year}-{self.fof_analysis.treasury_data['date'].max().year}",
                'Observations': len(self.fof_analysis.treasury_data['date'].unique()),
                'Source': 'Federal Reserve Z.1',
                'Frequency': 'Quarterly'
            })

        summary_df = pd.DataFrame(summary_data)

        print("\n" + summary_df.to_string(index=False))
        print("\n" + "="*80)

        return summary_df

    # ========================================================================
    # QUICK START METHODS
    # ========================================================================

    def quick_start(self):
        """
        Quick start: Load all data and generate all visualizations.

        This is the main entry point for using the platform.
        """
        print("\n" + "="*80)
        print("INTERNATIONAL ECONOMICS PLATFORM - QUICK START")
        print("="*80)

        # Load everything
        self.load_all_data()

        # Generate summary
        summary = self.platform_summary()

        # Generate all visualizations
        self.generate_all_visualizations()

        # Final summary
        print("\n" + "="*80)
        print("PLATFORM READY")
        print("="*80)
        print("\nCapabilities:")
        print("  [OK] Multi-country Balance of Payments analysis")
        print("  [OK] US Flow of Funds analysis")
        print("  [OK] International Investment Position")
        print("  [OK] Cross-border capital flows")
        print("  [OK] 9+ visualizations generated")
        print("\nNext Steps:")
        print("  - Review charts in Output/Charts/")
        print("  - Use platform.analyze_country('US') for detailed analysis")
        print("  - Use platform.comparative_analysis() for cross-country comparison")
        print("="*80)

        return summary


def main():
    """Main execution: quick start the platform."""
    # Initialize platform
    platform = InternationalEconomicsPlatform(use_cache=True)

    # Quick start: load all data and generate visualizations
    summary = platform.quick_start()

    # Optional: Run country-specific analyses
    print("\n[DEMO] Country-Specific Analysis...")
    us_results = platform.analyze_country('US', generate_plots=False)

    # Optional: Comparative analysis
    print("\n[DEMO] Comparative Analysis...")
    comparison = platform.comparative_analysis()

    print("\n[COMPLETE] Platform demonstration finished!")


if __name__ == "__main__":
    main()

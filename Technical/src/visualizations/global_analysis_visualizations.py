"""
Global Analysis Visualizations
==============================

Create comprehensive visualizations for the global integrated analysis.

Generates:
1. Country coverage comparison charts
2. Regional distribution visualizations
3. Temporal coverage trends
4. GDP rankings charts

Author: Claude
Date: 2025-10-06
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Optional
DATA_ROOT = Path(os.environ.get("DATA_ROOT", "data"))

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
ANALYSIS_PATH = DATA_ROOT / "GLOBAL_ANALYSIS"
OUTPUT_PATH = PROJECT_ROOT / "Output" / "Charts" / "Global_Analysis"
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10


class GlobalAnalysisVisualizer:
    """
    Create visualizations for global integrated analysis.
    """

    def __init__(self):
        """Initialize visualizer."""
        self.analysis_path = ANALYSIS_PATH
        self.output_path = OUTPUT_PATH

        # Data containers
        self.country_summary = None
        self.regional_analysis = None
        self.temporal_analysis = None

        print("\n" + "="*80)
        print("GLOBAL ANALYSIS VISUALIZATIONS")
        print("="*80)
        print(f"Analysis path: {ANALYSIS_PATH}")
        print(f"Output path: {OUTPUT_PATH}")

    # ========================================================================
    # LOAD DATA
    # ========================================================================

    def load_data(self):
        """Load analysis data from CSV files."""
        print("\n[LOAD] Loading analysis data...")

        # Load country summary
        country_file = self.analysis_path / "country_summary.csv"
        if country_file.exists():
            self.country_summary = pd.read_csv(country_file)
            print(f"  Country summary: {len(self.country_summary)} countries")

        # Load regional analysis
        regional_file = self.analysis_path / "regional_analysis.csv"
        if regional_file.exists():
            self.regional_analysis = pd.read_csv(regional_file)
            print(f"  Regional analysis: {len(self.regional_analysis)} regions")

        # Load temporal analysis
        temporal_file = self.analysis_path / "temporal_analysis.csv"
        if temporal_file.exists():
            self.temporal_analysis = pd.read_csv(temporal_file)
            print(f"  Temporal analysis: {len(self.temporal_analysis)} years")

    # ========================================================================
    # COUNTRY VISUALIZATIONS
    # ========================================================================

    def plot_country_coverage(self):
        """Create country coverage comparison chart."""
        print("\n[VIZ] Creating country coverage chart...")

        if self.country_summary is None:
            print("  [SKIP] No country summary data")
            return

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

        # Top 15 countries by total observations
        top_15 = self.country_summary.nlargest(15, 'total_observations')

        # Chart 1: Total observations
        colors = sns.color_palette("viridis", len(top_15))
        ax1.barh(range(len(top_15)), top_15['total_observations'], color=colors)
        ax1.set_yticks(range(len(top_15)))
        ax1.set_yticklabels(top_15['country_name'])
        ax1.set_xlabel('Total Observations')
        ax1.set_title('Top 15 Countries by Data Coverage', fontsize=14, fontweight='bold')
        ax1.grid(axis='x', alpha=0.3)

        # Add value labels
        for i, v in enumerate(top_15['total_observations']):
            ax1.text(v + 2, i, str(int(v)), va='center', fontsize=9)

        # Chart 2: Observations by source (stacked)
        sources_data = top_15[['country_name', 'bop_observations', 'trade_observations', 'gdp_observations']].set_index('country_name')
        sources_data.plot(kind='barh', stacked=True, ax=ax2,
                         color=['#1f77b4', '#ff7f0e', '#2ca02c'],
                         legend=True)
        ax2.set_xlabel('Observations')
        ax2.set_title('Data Coverage by Source Type', fontsize=14, fontweight='bold')
        ax2.legend(['Balance of Payments', 'Trade', 'GDP'], loc='lower right')
        ax2.grid(axis='x', alpha=0.3)

        plt.tight_layout()
        output_file = self.output_path / "country_coverage.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  Saved: {output_file.relative_to(PROJECT_ROOT)}")
        plt.close()

    def plot_gdp_rankings(self):
        """Create GDP rankings chart."""
        print("\n[VIZ] Creating GDP rankings chart...")

        if self.country_summary is None:
            print("  [SKIP] No country summary data")
            return

        # Filter countries with GDP data
        gdp_data = self.country_summary[self.country_summary['latest_gdp_usd'].notna()].copy()

        if len(gdp_data) == 0:
            print("  [SKIP] No GDP data available")
            return

        # Top 15 by GDP
        top_15_gdp = gdp_data.nlargest(15, 'latest_gdp_usd')

        fig, ax = plt.subplots(figsize=(14, 8))

        # Convert to trillions for readability
        gdp_trillions = top_15_gdp['latest_gdp_usd'] / 1e12

        colors = sns.color_palette("mako", len(top_15_gdp))
        bars = ax.barh(range(len(top_15_gdp)), gdp_trillions, color=colors)

        ax.set_yticks(range(len(top_15_gdp)))
        ax.set_yticklabels(top_15_gdp['country_name'])
        ax.set_xlabel('GDP (Trillions USD)', fontsize=12)
        ax.set_title('Top 15 Countries by GDP (Latest Available Year)',
                    fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)

        # Add value labels
        for i, (v, year) in enumerate(zip(gdp_trillions, top_15_gdp['latest_gdp_year'])):
            if v > 0:
                ax.text(v + 0.1, i, f'${v:.2f}T ({int(year)})', va='center', fontsize=9)

        plt.tight_layout()
        output_file = self.output_path / "gdp_rankings.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  Saved: {output_file.relative_to(PROJECT_ROOT)}")
        plt.close()

    # ========================================================================
    # REGIONAL VISUALIZATIONS
    # ========================================================================

    def plot_regional_distribution(self):
        """Create regional distribution visualizations."""
        print("\n[VIZ] Creating regional distribution charts...")

        if self.regional_analysis is None:
            print("  [SKIP] No regional analysis data")
            return

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

        # Chart 1: Observations by region
        colors = sns.color_palette("Set2", len(self.regional_analysis))
        ax1.bar(range(len(self.regional_analysis)),
               self.regional_analysis['total_observations'],
               color=colors)
        ax1.set_xticks(range(len(self.regional_analysis)))
        ax1.set_xticklabels(self.regional_analysis['region'], rotation=45, ha='right')
        ax1.set_ylabel('Total Observations')
        ax1.set_title('Data Coverage by Region', fontsize=14, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)

        # Add value labels
        for i, v in enumerate(self.regional_analysis['total_observations']):
            ax1.text(i, v + 10, str(int(v)), ha='center', fontsize=9)

        # Chart 2: Country counts by region
        ax2.bar(range(len(self.regional_analysis)),
               self.regional_analysis['total_countries'],
               color=colors)
        ax2.set_xticks(range(len(self.regional_analysis)))
        ax2.set_xticklabels(self.regional_analysis['region'], rotation=45, ha='right')
        ax2.set_ylabel('Number of Countries')
        ax2.set_title('Country Count by Region', fontsize=14, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)

        # Add value labels
        for i, v in enumerate(self.regional_analysis['total_countries']):
            ax2.text(i, v + 0.1, str(int(v)), ha='center', fontsize=9)

        plt.tight_layout()
        output_file = self.output_path / "regional_distribution.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  Saved: {output_file.relative_to(PROJECT_ROOT)}")
        plt.close()

    def plot_regional_gdp(self):
        """Create regional GDP comparison chart."""
        print("\n[VIZ] Creating regional GDP chart...")

        if self.regional_analysis is None:
            print("  [SKIP] No regional analysis data")
            return

        # Filter regions with GDP data
        gdp_regions = self.regional_analysis[
            self.regional_analysis['latest_aggregate_gdp_usd'] > 0
        ].copy()

        if len(gdp_regions) == 0:
            print("  [SKIP] No regional GDP data available")
            return

        # Sort by GDP
        gdp_regions = gdp_regions.sort_values('latest_aggregate_gdp_usd', ascending=True)

        fig, ax = plt.subplots(figsize=(12, 8))

        # Convert to trillions
        gdp_trillions = gdp_regions['latest_aggregate_gdp_usd'] / 1e12

        colors = sns.color_palette("rocket", len(gdp_regions))
        bars = ax.barh(range(len(gdp_regions)), gdp_trillions, color=colors)

        ax.set_yticks(range(len(gdp_regions)))
        ax.set_yticklabels(gdp_regions['region'])
        ax.set_xlabel('Aggregate GDP (Trillions USD)', fontsize=12)
        ax.set_title('Regional GDP Comparison (Latest Available Year)',
                    fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)

        # Add value labels
        for i, v in enumerate(gdp_trillions):
            ax.text(v + 0.5, i, f'${v:.2f}T', va='center', fontsize=9)

        plt.tight_layout()
        output_file = self.output_path / "regional_gdp.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  Saved: {output_file.relative_to(PROJECT_ROOT)}")
        plt.close()

    # ========================================================================
    # TEMPORAL VISUALIZATIONS
    # ========================================================================

    def plot_temporal_coverage(self):
        """Create temporal coverage trend charts."""
        print("\n[VIZ] Creating temporal coverage charts...")

        if self.temporal_analysis is None:
            print("  [SKIP] No temporal analysis data")
            return

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

        # Chart 1: Total observations over time
        ax1.plot(self.temporal_analysis['year'],
                self.temporal_analysis['total_observations'],
                marker='o', linewidth=2, color='#1f77b4', markersize=4)
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Total Observations')
        ax1.set_title('Data Coverage Over Time', fontsize=12, fontweight='bold')
        ax1.grid(alpha=0.3)
        ax1.fill_between(self.temporal_analysis['year'],
                         self.temporal_analysis['total_observations'],
                         alpha=0.3, color='#1f77b4')

        # Chart 2: Countries covered over time
        ax2.plot(self.temporal_analysis['year'],
                self.temporal_analysis['total_countries'],
                marker='s', linewidth=2, color='#ff7f0e', markersize=4)
        ax2.set_xlabel('Year')
        ax2.set_ylabel('Number of Countries')
        ax2.set_title('Country Coverage Over Time', fontsize=12, fontweight='bold')
        ax2.grid(alpha=0.3)
        ax2.fill_between(self.temporal_analysis['year'],
                         self.temporal_analysis['total_countries'],
                         alpha=0.3, color='#ff7f0e')

        # Chart 3: Observations by source (stacked area)
        ax3.fill_between(self.temporal_analysis['year'],
                         0, self.temporal_analysis['bop_observations'],
                         label='Balance of Payments', alpha=0.7, color='#1f77b4')
        ax3.fill_between(self.temporal_analysis['year'],
                         self.temporal_analysis['bop_observations'],
                         self.temporal_analysis['bop_observations'] + self.temporal_analysis['trade_observations'],
                         label='Trade', alpha=0.7, color='#ff7f0e')
        ax3.fill_between(self.temporal_analysis['year'],
                         self.temporal_analysis['bop_observations'] + self.temporal_analysis['trade_observations'],
                         self.temporal_analysis['total_observations'],
                         label='GDP', alpha=0.7, color='#2ca02c')
        ax3.set_xlabel('Year')
        ax3.set_ylabel('Observations')
        ax3.set_title('Coverage by Data Source Over Time', fontsize=12, fontweight='bold')
        ax3.legend(loc='upper left')
        ax3.grid(alpha=0.3)

        # Chart 4: Global GDP trend (if available)
        if 'global_gdp_trillions' in self.temporal_analysis.columns:
            gdp_data = self.temporal_analysis[self.temporal_analysis['global_gdp_trillions'] > 0]
            if len(gdp_data) > 0:
                ax4.plot(gdp_data['year'], gdp_data['global_gdp_trillions'],
                        marker='o', linewidth=2, color='#d62728', markersize=4)
                ax4.set_xlabel('Year')
                ax4.set_ylabel('GDP (Trillions USD)')
                ax4.set_title('Aggregate GDP Trend Over Time', fontsize=12, fontweight='bold')
                ax4.grid(alpha=0.3)
                ax4.fill_between(gdp_data['year'], gdp_data['global_gdp_trillions'],
                                alpha=0.3, color='#d62728')
            else:
                ax4.text(0.5, 0.5, 'No GDP data available',
                        ha='center', va='center', transform=ax4.transAxes)
                ax4.axis('off')
        else:
            ax4.text(0.5, 0.5, 'No GDP data available',
                    ha='center', va='center', transform=ax4.transAxes)
            ax4.axis('off')

        plt.tight_layout()
        output_file = self.output_path / "temporal_coverage.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  Saved: {output_file.relative_to(PROJECT_ROOT)}")
        plt.close()

    # ========================================================================
    # SUMMARY DASHBOARD
    # ========================================================================

    def create_summary_dashboard(self):
        """Create comprehensive summary dashboard."""
        print("\n[VIZ] Creating summary dashboard...")

        if self.country_summary is None or self.regional_analysis is None:
            print("  [SKIP] Missing required data")
            return

        fig = plt.figure(figsize=(18, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

        # Top left: Top 10 countries
        ax1 = fig.add_subplot(gs[0:2, 0])
        top_10 = self.country_summary.nlargest(10, 'total_observations')
        colors = sns.color_palette("viridis", len(top_10))
        ax1.barh(range(len(top_10)), top_10['total_observations'], color=colors)
        ax1.set_yticks(range(len(top_10)))
        ax1.set_yticklabels(top_10['country_name'], fontsize=9)
        ax1.set_xlabel('Observations')
        ax1.set_title('Top 10 Countries by Coverage', fontsize=11, fontweight='bold')
        ax1.grid(axis='x', alpha=0.3)

        # Top middle: Regional pie chart
        ax2 = fig.add_subplot(gs[0, 1])
        region_obs = self.regional_analysis.nlargest(5, 'total_observations')
        ax2.pie(region_obs['total_observations'], labels=region_obs['region'],
               autopct='%1.1f%%', startangle=90, colors=sns.color_palette("Set2", len(region_obs)))
        ax2.set_title('Regional Distribution (Top 5)', fontsize=11, fontweight='bold')

        # Top right: Data source distribution
        ax3 = fig.add_subplot(gs[0, 2])
        total_bop = self.country_summary['bop_observations'].sum()
        total_trade = self.country_summary['trade_observations'].sum()
        total_gdp = self.country_summary['gdp_observations'].sum()
        sources = ['BoP', 'Trade', 'GDP']
        values = [total_bop, total_trade, total_gdp]
        ax3.pie(values, labels=sources, autopct='%1.1f%%', startangle=90,
               colors=['#1f77b4', '#ff7f0e', '#2ca02c'])
        ax3.set_title('Data Source Distribution', fontsize=11, fontweight='bold')

        # Middle left: Temporal trend (already covered by ax1)

        # Middle middle: Country count by region
        ax4 = fig.add_subplot(gs[1, 1])
        regions_sorted = self.regional_analysis.sort_values('total_countries', ascending=False)
        ax4.bar(range(len(regions_sorted)), regions_sorted['total_countries'],
               color=sns.color_palette("Set2", len(regions_sorted)))
        ax4.set_xticks(range(len(regions_sorted)))
        ax4.set_xticklabels(regions_sorted['region'], rotation=45, ha='right', fontsize=8)
        ax4.set_ylabel('Countries')
        ax4.set_title('Countries per Region', fontsize=11, fontweight='bold')
        ax4.grid(axis='y', alpha=0.3)

        # Middle right: Coverage quality
        ax5 = fig.add_subplot(gs[1, 2])
        quality_bins = [0, 50, 100, 150, 1000]
        quality_labels = ['Low\n(0-50)', 'Medium\n(50-100)', 'High\n(100-150)', 'Very High\n(150+)']
        quality_counts = pd.cut(self.country_summary['total_observations'],
                               bins=quality_bins, labels=quality_labels).value_counts()
        colors_quality = ['#d62728', '#ff7f0e', '#2ca02c', '#1f77b4']
        ax5.bar(range(len(quality_counts)), quality_counts.values,
               color=colors_quality[:len(quality_counts)])
        ax5.set_xticks(range(len(quality_counts)))
        ax5.set_xticklabels(quality_counts.index, fontsize=9)
        ax5.set_ylabel('Number of Countries')
        ax5.set_title('Coverage Quality Distribution', fontsize=11, fontweight='bold')
        ax5.grid(axis='y', alpha=0.3)

        # Bottom: Temporal trend
        if self.temporal_analysis is not None:
            ax6 = fig.add_subplot(gs[2, :])
            ax6.plot(self.temporal_analysis['year'],
                    self.temporal_analysis['total_observations'],
                    marker='o', linewidth=2, color='#1f77b4', markersize=3)
            ax6.set_xlabel('Year')
            ax6.set_ylabel('Total Observations')
            ax6.set_title('Data Coverage Over Time (2000-2024)', fontsize=11, fontweight='bold')
            ax6.grid(alpha=0.3)
            ax6.fill_between(self.temporal_analysis['year'],
                            self.temporal_analysis['total_observations'],
                            alpha=0.3, color='#1f77b4')

        # Add title
        fig.suptitle('Global Economics Data Platform - Summary Dashboard',
                    fontsize=16, fontweight='bold', y=0.98)

        output_file = self.output_path / "summary_dashboard.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  Saved: {output_file.relative_to(PROJECT_ROOT)}")
        plt.close()

    # ========================================================================
    # MAIN EXECUTION
    # ========================================================================

    def create_all_visualizations(self):
        """Create all visualizations."""
        print("\n" + "="*80)
        print("CREATING ALL VISUALIZATIONS")
        print("="*80)

        # Load data
        self.load_data()

        # Country visualizations
        self.plot_country_coverage()
        self.plot_gdp_rankings()

        # Regional visualizations
        self.plot_regional_distribution()
        self.plot_regional_gdp()

        # Temporal visualizations
        self.plot_temporal_coverage()

        # Summary dashboard
        self.create_summary_dashboard()

        print("\n" + "="*80)
        print("VISUALIZATIONS COMPLETE")
        print("="*80)
        print(f"\nAll visualizations saved to: {self.output_path.relative_to(PROJECT_ROOT)}")


def main():
    """Main execution."""
    visualizer = GlobalAnalysisVisualizer()
    visualizer.create_all_visualizations()


if __name__ == "__main__":
    main()

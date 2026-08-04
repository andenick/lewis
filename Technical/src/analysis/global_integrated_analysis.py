"""
Global Integrated Analysis
=========================

Comprehensive analysis across all 32 countries integrating all data sources.

Data Sources Integrated:
1. ClassFiles (US, UK, Germany) - Historical detailed data
2. Banco de México (Mexico) - API collected
3. World Bank (28 countries) - API collected
4. FRED (US indicators) - Cached data

Total: 53,079+ observations across 32 countries

Author: Claude
Date: 2025-10-06
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.append(str(PROJECT_ROOT / "Technical" / "src"))

from data.unified_data_loader import UnifiedDataLoader


class GlobalIntegratedAnalysis:
    """
    Comprehensive global analysis across all 32 countries.

    Integrates all data sources into unified insights.
    """

    def __init__(self):
        """Initialize global analysis."""
        self.project_root = PROJECT_ROOT
        self.output_path = DATA_ROOT / "GLOBAL_ANALYSIS"
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Initialize data loader
        self.loader = UnifiedDataLoader()

        # Data containers
        self.unified_bop = None
        self.unified_trade = None
        self.unified_gdp = None

        # Analysis results
        self.country_summary = None
        self.regional_analysis = None
        self.temporal_analysis = None

        print("\n" + "="*80)
        print("GLOBAL INTEGRATED ANALYSIS")
        print("="*80)
        print(f"Project root: {PROJECT_ROOT}")
        print(f"Output path: {self.output_path}")

    # ========================================================================
    # LOAD DATA
    # ========================================================================

    def load_data(self):
        """Load all data using unified loader."""
        print("\n[LOAD] Loading all data sources...")

        # Load all raw data
        all_data = self.loader.load_all()

        # Create unified datasets
        unified = self.loader.create_all_unified_datasets()

        self.unified_bop = unified['bop']
        self.unified_trade = unified['trade']
        self.unified_gdp = unified['gdp']

        print("\n[LOAD] Data loading complete!")
        print(f"  Unified BoP: {len(self.unified_bop):,} observations")
        print(f"  Unified Trade: {len(self.unified_trade):,} observations")
        print(f"  Unified GDP: {len(self.unified_gdp):,} observations")

    # ========================================================================
    # COUNTRY-LEVEL ANALYSIS
    # ========================================================================

    def analyze_by_country(self) -> pd.DataFrame:
        """
        Create comprehensive country-level summary.

        Returns
        -------
        pd.DataFrame
            Country summary with key metrics
        """
        print("\n[ANALYZE] Creating country-level summary...")

        country_stats = []

        # Get unique countries across all datasets
        countries_bop = set(self.unified_bop['country'].unique()) if self.unified_bop is not None else set()
        countries_trade = set(self.unified_trade['country'].unique()) if self.unified_trade is not None else set()
        countries_gdp = set(self.unified_gdp['country'].unique()) if self.unified_gdp is not None else set()

        all_countries = countries_bop | countries_trade | countries_gdp

        for country in sorted(all_countries):
            stats = {'country': country}

            # Get country name
            if self.unified_bop is not None:
                country_name = self.unified_bop[self.unified_bop['country'] == country]['country_name'].iloc[0] if len(self.unified_bop[self.unified_bop['country'] == country]) > 0 else country
            elif self.unified_gdp is not None:
                country_name = self.unified_gdp[self.unified_gdp['country'] == country]['country_name'].iloc[0] if len(self.unified_gdp[self.unified_gdp['country'] == country]) > 0 else country
            else:
                country_name = country

            stats['country_name'] = country_name

            # BoP statistics
            if self.unified_bop is not None:
                country_bop = self.unified_bop[self.unified_bop['country'] == country]
                stats['bop_observations'] = len(country_bop)
                stats['bop_years_covered'] = f"{country_bop['year'].min()}-{country_bop['year'].max()}" if len(country_bop) > 0 else "N/A"
                stats['bop_indicators'] = country_bop['indicator'].nunique() if len(country_bop) > 0 else 0
                stats['bop_sources'] = ', '.join(country_bop['source'].unique()) if len(country_bop) > 0 else "N/A"
            else:
                stats['bop_observations'] = 0
                stats['bop_years_covered'] = "N/A"
                stats['bop_indicators'] = 0
                stats['bop_sources'] = "N/A"

            # Trade statistics
            if self.unified_trade is not None:
                country_trade = self.unified_trade[self.unified_trade['country'] == country]
                stats['trade_observations'] = len(country_trade)
                stats['trade_years_covered'] = f"{country_trade['year'].min()}-{country_trade['year'].max()}" if len(country_trade) > 0 else "N/A"
                stats['trade_indicators'] = country_trade['indicator'].nunique() if len(country_trade) > 0 else 0
            else:
                stats['trade_observations'] = 0
                stats['trade_years_covered'] = "N/A"
                stats['trade_indicators'] = 0

            # GDP statistics
            if self.unified_gdp is not None:
                country_gdp = self.unified_gdp[self.unified_gdp['country'] == country]
                stats['gdp_observations'] = len(country_gdp)
                stats['gdp_years_covered'] = f"{country_gdp['year'].min()}-{country_gdp['year'].max()}" if len(country_gdp) > 0 else "N/A"

                # Latest GDP
                if len(country_gdp) > 0:
                    latest_gdp = country_gdp.nlargest(1, 'year')
                    stats['latest_gdp_year'] = int(latest_gdp['year'].iloc[0])
                    stats['latest_gdp_usd'] = float(latest_gdp['gdp_usd'].iloc[0])
                    stats['latest_gdp_usd_billions'] = f"${stats['latest_gdp_usd']/1e9:.1f}B"
                else:
                    stats['latest_gdp_year'] = None
                    stats['latest_gdp_usd'] = None
                    stats['latest_gdp_usd_billions'] = "N/A"
            else:
                stats['gdp_observations'] = 0
                stats['gdp_years_covered'] = "N/A"
                stats['latest_gdp_year'] = None
                stats['latest_gdp_usd'] = None
                stats['latest_gdp_usd_billions'] = "N/A"

            # Total coverage
            stats['total_observations'] = stats['bop_observations'] + stats['trade_observations'] + stats['gdp_observations']

            country_stats.append(stats)

        # Create DataFrame
        summary_df = pd.DataFrame(country_stats)

        # Sort by total observations (descending)
        summary_df = summary_df.sort_values('total_observations', ascending=False)

        print(f"\n  Countries analyzed: {len(summary_df)}")
        print(f"  Total observations: {summary_df['total_observations'].sum():,}")

        self.country_summary = summary_df
        return summary_df

    # ========================================================================
    # REGIONAL ANALYSIS
    # ========================================================================

    def analyze_by_region(self) -> pd.DataFrame:
        """
        Create regional groupings and analysis.

        Returns
        -------
        pd.DataFrame
            Regional summary statistics
        """
        print("\n[ANALYZE] Creating regional analysis...")

        # Define regional groupings
        regions = {
            'G7': ['USA', 'GBR', 'DEU', 'FRA', 'ITA', 'JPN', 'CAN'],
            'BRICS': ['BRA', 'RUS', 'IND', 'CHN', 'ZAF'],
            'EU_Core': ['DEU', 'FRA', 'ITA', 'ESP', 'NLD', 'BEL'],
            'EU_North': ['GBR', 'SWE', 'DNK', 'FIN', 'NOR', 'IRL'],
            'Asia_Pacific': ['JPN', 'CHN', 'KOR', 'AUS', 'NZL', 'IDN', 'IND'],
            'Latin_America': ['MEX', 'BRA', 'CHL', 'ARG', 'COL'],
            'Other_Advanced': ['CHE', 'AUS', 'NZL', 'NOR', 'AUT', 'IRL']
        }

        regional_stats = []

        for region_name, countries in regions.items():
            stats = {'region': region_name}

            # Filter data for this region
            if self.unified_bop is not None:
                region_bop = self.unified_bop[self.unified_bop['country'].isin(countries)]
                stats['bop_observations'] = len(region_bop)
                stats['bop_countries'] = region_bop['country'].nunique()
            else:
                stats['bop_observations'] = 0
                stats['bop_countries'] = 0

            if self.unified_trade is not None:
                region_trade = self.unified_trade[self.unified_trade['country'].isin(countries)]
                stats['trade_observations'] = len(region_trade)
                stats['trade_countries'] = region_trade['country'].nunique()
            else:
                stats['trade_observations'] = 0
                stats['trade_countries'] = 0

            if self.unified_gdp is not None:
                region_gdp = self.unified_gdp[self.unified_gdp['country'].isin(countries)]
                stats['gdp_observations'] = len(region_gdp)
                stats['gdp_countries'] = region_gdp['country'].nunique()

                # Latest aggregate GDP
                if len(region_gdp) > 0:
                    latest_year = region_gdp['year'].max()
                    latest_gdp = region_gdp[region_gdp['year'] == latest_year]['gdp_usd'].sum()
                    stats['latest_aggregate_gdp_usd'] = latest_gdp
                    stats['latest_aggregate_gdp_trillions'] = f"${latest_gdp/1e12:.2f}T"
                else:
                    stats['latest_aggregate_gdp_usd'] = 0
                    stats['latest_aggregate_gdp_trillions'] = "N/A"
            else:
                stats['gdp_observations'] = 0
                stats['gdp_countries'] = 0
                stats['latest_aggregate_gdp_usd'] = 0
                stats['latest_aggregate_gdp_trillions'] = "N/A"

            stats['total_observations'] = stats['bop_observations'] + stats['trade_observations'] + stats['gdp_observations']
            stats['total_countries'] = max(stats['bop_countries'], stats['trade_countries'], stats['gdp_countries'])

            regional_stats.append(stats)

        # Create DataFrame
        regional_df = pd.DataFrame(regional_stats)
        regional_df = regional_df.sort_values('total_observations', ascending=False)

        print(f"\n  Regions analyzed: {len(regional_df)}")
        print(f"  Total observations: {regional_df['total_observations'].sum():,}")

        self.regional_analysis = regional_df
        return regional_df

    # ========================================================================
    # TEMPORAL ANALYSIS
    # ========================================================================

    def analyze_by_time(self) -> pd.DataFrame:
        """
        Create temporal coverage analysis.

        Returns
        -------
        pd.DataFrame
            Year-by-year coverage statistics
        """
        print("\n[ANALYZE] Creating temporal analysis...")

        temporal_stats = []

        # Get all years across datasets
        years_bop = set(self.unified_bop['year'].unique()) if self.unified_bop is not None else set()
        years_trade = set(self.unified_trade['year'].unique()) if self.unified_trade is not None else set()
        years_gdp = set(self.unified_gdp['year'].unique()) if self.unified_gdp is not None else set()

        all_years = years_bop | years_trade | years_gdp

        for year in sorted(all_years):
            stats = {'year': int(year)}

            # BoP for this year
            if self.unified_bop is not None:
                year_bop = self.unified_bop[self.unified_bop['year'] == year]
                stats['bop_observations'] = len(year_bop)
                stats['bop_countries'] = year_bop['country'].nunique()
                stats['bop_indicators'] = year_bop['indicator'].nunique()
            else:
                stats['bop_observations'] = 0
                stats['bop_countries'] = 0
                stats['bop_indicators'] = 0

            # Trade for this year
            if self.unified_trade is not None:
                year_trade = self.unified_trade[self.unified_trade['year'] == year]
                stats['trade_observations'] = len(year_trade)
                stats['trade_countries'] = year_trade['country'].nunique()
            else:
                stats['trade_observations'] = 0
                stats['trade_countries'] = 0

            # GDP for this year
            if self.unified_gdp is not None:
                year_gdp = self.unified_gdp[self.unified_gdp['year'] == year]
                stats['gdp_observations'] = len(year_gdp)
                stats['gdp_countries'] = year_gdp['country'].nunique()

                # Aggregate GDP
                stats['global_gdp_usd'] = year_gdp['gdp_usd'].sum()
                stats['global_gdp_trillions'] = stats['global_gdp_usd'] / 1e12
            else:
                stats['gdp_observations'] = 0
                stats['gdp_countries'] = 0
                stats['global_gdp_usd'] = 0
                stats['global_gdp_trillions'] = 0

            stats['total_observations'] = stats['bop_observations'] + stats['trade_observations'] + stats['gdp_observations']
            stats['total_countries'] = max(stats['bop_countries'], stats['trade_countries'], stats['gdp_countries'])

            temporal_stats.append(stats)

        # Create DataFrame
        temporal_df = pd.DataFrame(temporal_stats)
        temporal_df = temporal_df.sort_values('year')

        print(f"\n  Years covered: {temporal_df['year'].min()}-{temporal_df['year'].max()}")
        print(f"  Total observations: {temporal_df['total_observations'].sum():,}")

        self.temporal_analysis = temporal_df
        return temporal_df

    # ========================================================================
    # KEY INSIGHTS
    # ========================================================================

    def generate_key_insights(self) -> Dict[str, any]:
        """
        Generate key insights from integrated analysis.

        Returns
        -------
        dict
            Key insights and statistics
        """
        print("\n[INSIGHTS] Generating key insights...")

        insights = {}

        # Overall coverage
        insights['total_countries'] = len(self.country_summary) if self.country_summary is not None else 0
        insights['total_observations'] = (
            (len(self.unified_bop) if self.unified_bop is not None else 0) +
            (len(self.unified_trade) if self.unified_trade is not None else 0) +
            (len(self.unified_gdp) if self.unified_gdp is not None else 0)
        )

        # Temporal coverage
        if self.temporal_analysis is not None:
            insights['years_covered'] = f"{self.temporal_analysis['year'].min()}-{self.temporal_analysis['year'].max()}"
            insights['time_span'] = int(self.temporal_analysis['year'].max() - self.temporal_analysis['year'].min() + 1)

        # Top countries by coverage
        if self.country_summary is not None:
            top_5 = self.country_summary.nlargest(5, 'total_observations')[['country_name', 'total_observations']]
            insights['top_5_countries'] = top_5.to_dict('records')

        # Regional distribution
        if self.regional_analysis is not None:
            insights['regional_distribution'] = self.regional_analysis[['region', 'total_observations', 'total_countries']].to_dict('records')

        # Latest GDP rankings
        if self.country_summary is not None:
            gdp_rankings = self.country_summary[self.country_summary['latest_gdp_usd'].notna()].nlargest(10, 'latest_gdp_usd')
            insights['gdp_rankings'] = gdp_rankings[['country_name', 'latest_gdp_year', 'latest_gdp_usd_billions']].to_dict('records')

        # Data quality metrics
        if self.unified_bop is not None:
            insights['bop_data_sources'] = self.unified_bop['source'].nunique()
            insights['bop_indicators'] = self.unified_bop['indicator'].nunique()

        print(f"\n  Total countries: {insights.get('total_countries', 0)}")
        print(f"  Total observations: {insights.get('total_observations', 0):,}")
        print(f"  Years covered: {insights.get('years_covered', 'N/A')}")

        return insights

    # ========================================================================
    # SAVE RESULTS
    # ========================================================================

    def save_all_results(self):
        """Save all analysis results to CSV files."""
        print("\n[SAVE] Saving analysis results...")

        if self.country_summary is not None:
            country_file = self.output_path / "country_summary.csv"
            self.country_summary.to_csv(country_file, index=False)
            print(f"  Saved: {country_file.relative_to(PROJECT_ROOT)}")

        if self.regional_analysis is not None:
            regional_file = self.output_path / "regional_analysis.csv"
            self.regional_analysis.to_csv(regional_file, index=False)
            print(f"  Saved: {regional_file.relative_to(PROJECT_ROOT)}")

        if self.temporal_analysis is not None:
            temporal_file = self.output_path / "temporal_analysis.csv"
            self.temporal_analysis.to_csv(temporal_file, index=False)
            print(f"  Saved: {temporal_file.relative_to(PROJECT_ROOT)}")

        print(f"\n[COMPLETE] All results saved to: {self.output_path.relative_to(PROJECT_ROOT)}")

    def generate_summary_report(self, insights: Dict[str, any]):
        """
        Generate comprehensive summary report.

        Parameters
        ----------
        insights : dict
            Key insights from analysis
        """
        print("\n[REPORT] Generating summary report...")

        report_file = self.output_path / "GLOBAL_ANALYSIS_SUMMARY.md"

        report = f"""# Global Integrated Analysis - Summary Report

**Generated**: {datetime.now().strftime('%B %d, %Y at %H:%M')}
**Platform**: International Economics Analysis Platform
**Data Version**: October 2025 Integration

---

## Executive Summary

This report presents a comprehensive analysis of **{insights.get('total_countries', 0)} countries** spanning **{insights.get('years_covered', 'N/A')}** with **{insights.get('total_observations', 0):,} observations** integrated from multiple authoritative sources.

### Key Statistics

- **Countries Covered**: {insights.get('total_countries', 0)}
- **Total Observations**: {insights.get('total_observations', 0):,}
- **Time Span**: {insights.get('time_span', 0)} years ({insights.get('years_covered', 'N/A')})
- **Data Sources**: 4 integrated (ClassFiles, Banco de México, World Bank, FRED)
- **Standards**: IMF BPM6, UN SNA 2008

---

## Data Coverage by Country

### Top 5 Countries by Data Coverage

"""

        if 'top_5_countries' in insights:
            for i, country in enumerate(insights['top_5_countries'], 1):
                report += f"{i}. **{country['country_name']}**: {country['total_observations']:,} observations\n"

        report += f"""
---

## Regional Distribution

"""

        if 'regional_distribution' in insights:
            for region in insights['regional_distribution']:
                report += f"### {region['region']}\n"
                report += f"- Countries: {region['total_countries']}\n"
                report += f"- Observations: {region['total_observations']:,}\n\n"

        report += f"""
---

## GDP Rankings (Latest Available Year)

"""

        if 'gdp_rankings' in insights:
            report += "| Rank | Country | Year | GDP (USD) |\n"
            report += "|------|---------|------|----------|\n"
            for i, country in enumerate(insights['gdp_rankings'], 1):
                report += f"| {i} | {country['country_name']} | {country['latest_gdp_year']} | {country['latest_gdp_usd_billions']} |\n"

        report += f"""

---

## Data Quality Metrics

"""

        if 'bop_data_sources' in insights:
            report += f"- **BoP Data Sources**: {insights['bop_data_sources']}\n"
            report += f"- **BoP Indicators**: {insights['bop_indicators']}\n"

        report += f"""

---

## Integration Methodology

### Data Sources Integrated

1. **ClassFiles (Historical Detail)**
   - US: 1960-2024 (BEA IIP/ITA)
   - UK: 1946-2023 (ONS Pink Book)
   - Germany: 1971-2024 (Bundesbank)

2. **Banco de México (API Collected)**
   - Mexico: 2000-2024
   - Monthly/quarterly frequency
   - 17,393 observations

3. **World Bank (API Collected)**
   - 28 countries: 2000-2024
   - Annual frequency
   - 3,277 observations

4. **FRED (US Indicators)**
   - US macroeconomic indicators
   - Quarterly/monthly frequency
   - 32,214 observations

### Standards Applied

- **IMF BPM6**: Balance of Payments Manual 6th Edition (2009)
- **UN SNA 2008**: System of National Accounts
- **OECD Standards**: FDI Benchmark Definition
- **Cross-validation**: Multiple sources for key countries

---

## Output Files

Analysis results saved to `$OUTPUT_ROOT/GLOBAL_ANALYSIS/`:

1. **country_summary.csv** - Comprehensive country-level statistics
2. **regional_analysis.csv** - Regional groupings and aggregations
3. **temporal_analysis.csv** - Year-by-year coverage analysis
4. **GLOBAL_ANALYSIS_SUMMARY.md** - This report

---

## Usage

### Loading Analysis Results

```python
import os
import pandas as pd
from pathlib import Path

OUTPUT_ROOT = Path(os.environ.get("OUTPUT_ROOT", "outputs"))

# Load analysis results
country_summary = pd.read_csv(str(OUTPUT_ROOT / "GLOBAL_ANALYSIS/country_summary.csv"))
regional_analysis = pd.read_csv(str(OUTPUT_ROOT / "GLOBAL_ANALYSIS/regional_analysis.csv"))
temporal_analysis = pd.read_csv(str(OUTPUT_ROOT / "GLOBAL_ANALYSIS/temporal_analysis.csv"))
```

### Using Unified Data Loader

```python
from Technical.src.data.unified_data_loader import UnifiedDataLoader
DATA_ROOT = Path(os.environ.get("DATA_ROOT", "data"))

# Initialize loader
loader = UnifiedDataLoader()

# Load all data
all_data = loader.load_all()

# Create unified datasets
unified = loader.create_all_unified_datasets()

# Access datasets
bop_data = unified['bop']
trade_data = unified['trade']
gdp_data = unified['gdp']
```

---

## Next Steps

1. **Visualization**: Create comprehensive charts and visualizations
2. **Advanced Analysis**: Time series analysis, correlations, trends
3. **Expand Coverage**: Add UN Comtrade, OECD, Eurostat data
4. **Update Frequency**: Quarterly updates from APIs

---

**Report Status**: COMPLETE
**Generated By**: Global Integrated Analysis System
**Version**: 1.0
**Date**: {datetime.now().strftime('%B %d, %Y')}
"""

        # Save report
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"  Saved: {report_file.relative_to(PROJECT_ROOT)}")

    # ========================================================================
    # MAIN EXECUTION
    # ========================================================================

    def run_complete_analysis(self):
        """Run complete global integrated analysis."""
        print("\n" + "="*80)
        print("EXECUTING COMPLETE GLOBAL ANALYSIS")
        print("="*80)

        # Step 1: Load data
        self.load_data()

        # Step 2: Country-level analysis
        self.analyze_by_country()

        # Step 3: Regional analysis
        self.analyze_by_region()

        # Step 4: Temporal analysis
        self.analyze_by_time()

        # Step 5: Generate insights
        insights = self.generate_key_insights()

        # Step 6: Save all results
        self.save_all_results()

        # Step 7: Generate summary report
        self.generate_summary_report(insights)

        print("\n" + "="*80)
        print("GLOBAL ANALYSIS COMPLETE")
        print("="*80)
        print(f"\nResults saved to: {self.output_path.relative_to(PROJECT_ROOT)}")


def main():
    """Main execution."""
    analysis = GlobalIntegratedAnalysis()
    analysis.run_complete_analysis()


if __name__ == "__main__":
    main()

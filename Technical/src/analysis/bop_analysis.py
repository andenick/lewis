"""
Balance of Payments Analysis
=============================

This module provides analytical functions for international trade and balance
of payments data analysis. It includes functions for:

- Time series analysis of trade balances
- Cross-country comparisons
- Historical trend analysis
- Key economic event analysis (NAFTA, Nixon Shock, Maastricht Treaty, etc.)

Author: Lewis Platform
Date: October 6, 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Optional, Tuple
# Make sibling modules importable whether this file is run as a script or
# imported as `analysis.<module>` from `Technical/src`.
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent))

from trade_data_loader import TradeDataLoader

# Set plotting style
plt.style.use('seaborn-v0_8-darkgrid')


class BalanceOfPaymentsAnalyzer:
    """Analyze balance of payments and international trade data."""

    def __init__(self):
        """Initialize the analyzer with data loader."""
        self.loader = TradeDataLoader()
        self.datasets = None
        self.charts_path = Path(__file__).parent.parent.parent / "Output" / "Charts"

    def load_data(self):
        """Load all integrated datasets."""
        if self.datasets is None:
            self.datasets = self.loader.create_integrated_dataset()
        return self.datasets

    def analyze_current_account(self, country: str = 'US') -> pd.DataFrame:
        """
        Analyze current account balance trends.

        Args:
            country: Country code ('US', 'UK', or 'GER')

        Returns:
            DataFrame with current account analysis
        """
        self.load_data()

        data = self.datasets[f'{country.lower()}_annual_pct']

        analysis = pd.DataFrame({
            'Year': data['Year'],
            'Current_Account_Balance': data['Current Account Balance_pct'],
            'Goods_Services_Balance': data['Goods and Services Balance_pct'],
            'Primary_Income_Balance': data.get('Primary Income Balance_pct', 0),
            'Secondary_Income_Balance': data.get('Secondary Income Balance_pct', 0)
        })

        return analysis

    def compare_trade_balances(self, start_year: int = 1960, end_year: int = 2020) -> pd.DataFrame:
        """
        Compare trade balances across US, UK, and Germany.

        Args:
            start_year: Start year for comparison
            end_year: End year for comparison

        Returns:
            DataFrame with comparative trade balance data
        """
        self.load_data()

        comparison = None

        for country in ['us', 'uk', 'germany']:
            data = self.datasets[f'{country}_annual_pct']

            # Filter by year range
            data_filtered = data[
                (data['Year'] >= start_year) &
                (data['Year'] <= end_year)
            ].copy()

            # Get trade balance column (varies by country)
            if 'Goods and Services Balance_pct' in data_filtered.columns:
                trade_col = 'Goods and Services Balance_pct'
            elif 'Merchandise Trade Balance_pct' in data_filtered.columns:
                trade_col = 'Merchandise Trade Balance_pct'
            else:
                continue

            # Create temporary dataframe for this country
            temp_df = data_filtered[['Year', trade_col]].copy()
            temp_df = temp_df.rename(columns={trade_col: f'{country.upper()}_trade_balance'})

            # Merge with comparison dataframe
            if comparison is None:
                comparison = temp_df
            else:
                comparison = comparison.merge(temp_df, on='Year', how='outer')

        # Sort by year and handle case where no data was found
        if comparison is not None:
            comparison = comparison.sort_values('Year').reset_index(drop=True)
        else:
            comparison = pd.DataFrame()

        return comparison

    def identify_historical_periods(self, country: str = 'US') -> Dict[str, Tuple[int, int]]:
        """
        Identify key historical periods for trade analysis.

        Args:
            country: Country code

        Returns:
            Dictionary mapping period names to (start_year, end_year) tuples
        """
        if country == 'US':
            return {
                'Post_WWII': (1950, 1970),
                'Nixon_Shock': (1971, 1973),
                'Oil_Crisis': (1973, 1980),
                'Reagan_Era': (1981, 1989),
                'Pre_NAFTA': (1985, 1993),
                'NAFTA_Era': (1994, 2001),
                'China_WTO': (2001, 2008),
                'Financial_Crisis': (2008, 2010),
                'Post_Crisis': (2010, 2020)
            }
        elif country == 'Germany':
            return {
                'Reunification': (1989, 1995),
                'Pre_Maastricht': (1985, 1992),
                'Maastricht_Treaty': (1992, 1999),
                'Euro_Adoption': (1999, 2002),
                'Euro_Era': (2002, 2008),
                'Financial_Crisis': (2008, 2010),
                'Euro_Crisis': (2010, 2015),
                'Post_Crisis': (2015, 2020)
            }
        else:
            return {}

    def calculate_trade_statistics(self, country: str = 'US') -> pd.DataFrame:
        """
        Calculate summary statistics for trade data.

        Args:
            country: Country code

        Returns:
            DataFrame with summary statistics by period
        """
        self.load_data()

        data = self.datasets[f'{country.lower()}_annual_pct']
        periods = self.identify_historical_periods(country)

        stats = []

        for period_name, (start, end) in periods.items():
            period_data = data[
                (data['Year'] >= start) &
                (data['Year'] <= end)
            ]

            if not period_data.empty:
                if 'Current Account Balance_pct' in period_data.columns:
                    ca_balance = period_data['Current Account Balance_pct']

                    stats.append({
                        'Period': period_name,
                        'Start_Year': start,
                        'End_Year': end,
                        'Mean_CA_Balance': ca_balance.mean(),
                        'Std_CA_Balance': ca_balance.std(),
                        'Min_CA_Balance': ca_balance.min(),
                        'Max_CA_Balance': ca_balance.max()
                    })

        return pd.DataFrame(stats)

    def analyze_trade_components(self, country: str = 'US', year: Optional[int] = None) -> pd.Series:
        """
        Analyze components of the trade balance.

        Args:
            country: Country code
            year: Specific year (if None, uses most recent)

        Returns:
            Series with trade balance components
        """
        self.load_data()

        data = self.datasets[f'{country.lower()}_annual_pct']

        if year is not None:
            row = data[data['Year'] == year]
        else:
            row = data.iloc[-1:]

        if row.empty:
            raise ValueError(f"No data found for {country} in year {year}")

        # Extract key components
        components = {
            'Year': row['Year'].values[0],
            'Merchandise_Exports': row.get('Merchandise Exports_pct', [0])[0],
            'Merchandise_Imports': row.get('Merchandise Imports_pct', [0])[0],
            'Service_Exports': row.get('Service Exports_pct', [0])[0],
            'Service_Imports': row.get('Service Imports_pct', [0])[0],
            'Goods_Services_Balance': row.get('Goods and Services Balance_pct', [0])[0],
            'Current_Account_Balance': row.get('Current Account Balance_pct', [0])[0]
        }

        return pd.Series(components)

    def export_analysis_results(self, output_name: str = 'trade_analysis_results'):
        """
        Export comprehensive analysis results to Excel.

        Args:
            output_name: Base name for output file
        """
        self.load_data()

        output_path = Path(__file__).parent.parent.parent.parent / "Output" / "Data" / "Results"
        output_file = output_path / f"{output_name}.xlsx"

        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Summary of all datasets
            summary = self.loader.get_data_summary()
            summary.to_excel(writer, sheet_name='Data_Summary', index=False)

            # US analysis
            us_ca = self.analyze_current_account('US')
            us_ca.to_excel(writer, sheet_name='US_Current_Account', index=False)

            us_stats = self.calculate_trade_statistics('US')
            us_stats.to_excel(writer, sheet_name='US_Period_Stats', index=False)

            # Germany analysis (if available)
            try:
                ger_ca = self.analyze_current_account('GER')
                ger_ca.to_excel(writer, sheet_name='Germany_Current_Account', index=False)

                ger_stats = self.calculate_trade_statistics('Germany')
                ger_stats.to_excel(writer, sheet_name='Germany_Period_Stats', index=False)
            except:
                pass

            # Trade balance comparison
            comparison = self.compare_trade_balances()
            comparison.to_excel(writer, sheet_name='Cross_Country_Comparison', index=False)

        print(f"Analysis results exported to: {output_file}")


def main():
    """Run main analysis."""
    print("\n" + "="*60)
    print("BALANCE OF PAYMENTS ANALYSIS")
    print("="*60 + "\n")

    analyzer = BalanceOfPaymentsAnalyzer()

    # Load data
    analyzer.load_data()

    # Analyze US current account
    print("US Current Account Analysis (Last 10 years):")
    us_ca = analyzer.analyze_current_account('US')
    print(us_ca.tail(10).to_string(index=False))

    print("\n" + "-"*60 + "\n")

    # Period statistics
    print("US Trade Statistics by Historical Period:")
    us_stats = analyzer.calculate_trade_statistics('US')
    print(us_stats.to_string(index=False))

    print("\n" + "-"*60 + "\n")

    # Export results
    analyzer.export_analysis_results()

    print("\n" + "="*60)
    print("Analysis complete!")
    print("="*60)


if __name__ == "__main__":
    main()

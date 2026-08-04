"""
Balance of Payments Comparative Analysis
=========================================

Replicates the Trade ClassFiles R analysis in Python.
Provides comparative Balance of Payments analysis for US, UK, and Germany.

Key Features:
- Load BoP data for multiple countries
- Normalize by GDP
- Visualize historical periods (Nixon shock, NAFTA, German reunification, Maastricht)
- Compare current account and financial account relationships

Based on: Classfiles/Trade/final_Trade/Trade_Visualization_NA.Rmd

Author: Claude
Date: 2025-10-06
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
OUTPUT_ROOT = Path(os.environ.get("OUTPUT_ROOT", "outputs"))
BOP_PATH = OUTPUT_ROOT / "BALANCE_OF_PAYMENTS"
GDP_PATH = OUTPUT_ROOT / "GDP"
OUTPUT_CHARTS = PROJECT_ROOT / "Output" / "Charts"


class BoPComparativeAnalysis:
    """
    Comparative Balance of Payments analysis for multiple countries.

    Replicates R analysis from ClassFiles/Trade project with enhancements.
    """

    def __init__(self):
        """Initialize BoP comparative analysis."""
        self.us_data = None
        self.uk_data = None
        self.ger_data = None
        self.gdp_data = None

        # Set plotting style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (14, 8)
        plt.rcParams['font.size'] = 10

    # ========================================================================
    # DATA LOADING
    # ========================================================================

    def load_data(self):
        """
        Load all Balance of Payments and GDP data.

        Loads:
        - US quarterly BoP (1960-2020) from BEA
        - UK annual BoP (1948-2020) from ONS
        - Germany monthly BoP (1991-2020) from Bundesbank
        - World Bank GDP data for all countries
        """
        print("\n" + "=" * 80)
        print("Loading Balance of Payments Data")
        print("=" * 80)

        # Load raw Excel files
        self.us_data = pd.read_excel(BOP_PATH / "US_BEA" / "BoP_USRData_NA.xlsx")
        self.uk_data = pd.read_excel(BOP_PATH / "UK_ONS" / "BoP_UKRData_NA.xlsx")
        self.ger_data = pd.read_excel(BOP_PATH / "Germany_Bundesbank" / "BoP_GermanyRData_NA.xlsx")
        self.gdp_data = pd.read_excel(GDP_PATH / "World_Bank" / "BoP_WBankGDP_NA.xlsx")

        print(f"[OK] US data: {self.us_data.shape}")
        print(f"[OK] UK data: {self.uk_data.shape}")
        print(f"[OK] Germany data: {self.ger_data.shape}")
        print(f"[OK] GDP data: {self.gdp_data.shape}")

        # Process data
        self._process_us_data()
        self._process_uk_data()
        self._process_ger_data()

        print("\n[COMPLETE] All data loaded and processed")

    def _process_us_data(self):
        """Process US quarterly data to annual and normalize by GDP."""
        print("\n[PROCESSING] US data...")

        # Extract year from quarterly Date column
        # Format is like "2020Q1"
        self.us_data['Year'] = self.us_data['Date'].astype(str).str[:4].astype(int)

        # Aggregate to annual (sum all numeric columns)
        numeric_cols = self.us_data.select_dtypes(include=[np.number]).columns.tolist()
        numeric_cols = [c for c in numeric_cols if c != 'Year']

        us_annual = self.us_data.groupby('Year')[numeric_cols].sum().reset_index()

        # Get US GDP from World Bank data
        us_gdp = self.gdp_data[['Date', 'USAGDP_Wbank']].copy()
        us_gdp.columns = ['Year', 'GDP']
        # Date is already numeric year
        us_gdp['Year'] = us_gdp['Year'].astype(int, errors='ignore')

        # Merge GDP
        us_annual = us_annual.merge(us_gdp, on='Year', how='left')

        # Create percentage of GDP version
        us_pct = us_annual.copy()
        for col in numeric_cols:
            if col in us_pct.columns:
                us_pct[col + '_pct'] = (us_pct[col] / us_pct['GDP']) * 1e6  # Match R scaling

        self.us_annual = us_annual
        self.us_annual_pct = us_pct

        print(f"   Annual data: {us_annual.shape}")
        print(f"   Years: {us_annual['Year'].min()} - {us_annual['Year'].max()}")

    def _process_uk_data(self):
        """Process UK annual data and normalize by GDP."""
        print("\n[PROCESSING] UK data...")

        # UK data is already annual with 'Year' column
        if 'Year' not in self.uk_data.columns:
            self.uk_data['Year'] = self.uk_data['Date'].astype(int)
        else:
            self.uk_data['Year'] = self.uk_data['Year'].astype(int)

        # Get UK GDP (use ONS version if Wbank has NaN)
        if 'UKGDP_ONS_WBank' in self.gdp_data.columns:
            # Use ONS version which has earlier data
            uk_gdp = self.gdp_data[['Date', 'UKGDP_ONS_WBank']].copy()
            uk_gdp.columns = ['Year', 'GDP']
        else:
            uk_gdp = self.gdp_data[['Date', 'UKGDP_Wbank']].copy()
            uk_gdp.columns = ['Year', 'GDP']
        uk_gdp['Year'] = uk_gdp['Year'].astype(int, errors='ignore')

        # Merge
        uk_annual = self.uk_data.merge(uk_gdp, on='Year', how='left')

        # Create percentage version
        uk_pct = uk_annual.copy()
        numeric_cols = uk_annual.select_dtypes(include=[np.number]).columns.tolist()
        numeric_cols = [c for c in numeric_cols if c not in ['Year', 'GDP']]

        for col in numeric_cols:
            if col in uk_pct.columns:
                uk_pct[col + '_pct'] = (uk_pct[col] / uk_pct['GDP']) * 1e6

        self.uk_annual = uk_annual
        self.uk_annual_pct = uk_pct

        print(f"   Annual data: {uk_annual.shape}")
        print(f"   Years: {uk_annual['Year'].min()} - {uk_annual['Year'].max()}")

    def _process_ger_data(self):
        """Process Germany monthly data to annual and normalize by GDP."""
        print("\n[PROCESSING] Germany data...")

        # Convert Date to datetime and extract year and month
        self.ger_data['Date'] = pd.to_datetime(self.ger_data['Date'])
        self.ger_data['Year'] = self.ger_data['Date'].dt.year
        self.ger_data['Month'] = self.ger_data['Date'].dt.month

        # Aggregate to annual
        numeric_cols = self.ger_data.select_dtypes(include=[np.number]).columns.tolist()
        numeric_cols = [c for c in numeric_cols if c not in ['Year', 'Month']]

        ger_annual = self.ger_data.groupby('Year')[numeric_cols].sum().reset_index()

        # Get Germany GDP
        ger_gdp = self.gdp_data[['Date', 'GerGDP_Wbank']].copy()
        ger_gdp.columns = ['Year', 'GDP']
        ger_gdp['Year'] = ger_gdp['Year'].astype(int, errors='ignore')

        # Merge
        ger_annual = ger_annual.merge(ger_gdp, on='Year', how='left')

        # Create percentage version
        ger_pct = ger_annual.copy()
        for col in numeric_cols:
            if col in ger_pct.columns:
                ger_pct[col + '_pct'] = (ger_pct[col] / ger_pct['GDP']) * 1e6

        self.ger_annual = ger_annual
        self.ger_annual_pct = ger_pct

        print(f"   Annual data: {ger_annual.shape}")
        print(f"   Years: {ger_annual['Year'].min()} - {ger_annual['Year'].max()}")

    # ========================================================================
    # VISUALIZATION METHODS
    # ========================================================================

    def plot_us_nixon_shock(self, save: bool = True) -> plt.Figure:
        """
        Visualize US Balance of Payments around Nixon shock (1971).

        Shows period 1960-1980 with focus on:
        - End of Bretton Woods (1971)
        - Shift from surplus to deficit
        - Financial account changes

        Parameters
        ----------
        save : bool, default True
            Whether to save figure to Output/Charts

        Returns
        -------
        matplotlib.figure.Figure
            The generated figure
        """
        if self.us_annual_pct is None:
            raise ValueError("Data not loaded. Call load_data() first.")

        print("\n[PLOTTING] US Balance of Payments - Nixon Shock (1960-1980)")

        # Filter to period
        data = self.us_annual_pct[(self.us_annual_pct['Year'] >= 1960) &
                                   (self.us_annual_pct['Year'] <= 1980)]

        fig, ax = plt.subplots(figsize=(14, 8))

        # Plot key series (use actual column names)
        ax.plot(data['Year'], data.get('Current Account Balance_pct', np.nan),
                label='Current Account', linewidth=2, marker='o')
        ax.plot(data['Year'], data.get('Financial Account Balance_pct', np.nan),
                label='Financial Account', linewidth=2, marker='s')
        ax.plot(data['Year'], data.get('Goods and Services Balance_pct', np.nan),
                label='Goods & Services', linewidth=2, marker='^')

        # Add Nixon shock line
        ax.axvline(x=1971, color='red', linestyle='--', linewidth=2,
                   label='Nixon Shock (Aug 1971)', alpha=0.7)

        # Add zero line
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5, alpha=0.5)

        ax.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax.set_ylabel('% of GDP (millions)', fontsize=12, fontweight='bold')
        ax.set_title('US Balance of Payments: Nixon Shock Era (1960-1980)',
                     fontsize=14, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save:
            output_path = OUTPUT_CHARTS / "python_us_balance_of_payments_nixon_shock.png"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"[SAVED] {output_path.relative_to(PROJECT_ROOT)}")

        return fig

    def plot_us_nafta_period(self, save: bool = True) -> plt.Figure:
        """
        Visualize US Balance of Payments around NAFTA implementation (1994).

        Shows period 1985-2015 with focus on:
        - NAFTA implementation (1994)
        - Trade deficit expansion
        - China WTO accession (2001)

        Parameters
        ----------
        save : bool, default True
            Whether to save figure

        Returns
        -------
        matplotlib.figure.Figure
        """
        if self.us_annual_pct is None:
            raise ValueError("Data not loaded. Call load_data() first.")

        print("\n[PLOTTING] US Balance of Payments - NAFTA Period (1985-2015)")

        data = self.us_annual_pct[(self.us_annual_pct['Year'] >= 1985) &
                                   (self.us_annual_pct['Year'] <= 2015)]

        fig, ax = plt.subplots(figsize=(14, 8))

        # Plot key series (use actual column names)
        ax.plot(data['Year'], data.get('Current Account Balance_pct', np.nan),
                label='Current Account', linewidth=2, marker='o')
        ax.plot(data['Year'], data.get('Financial Account Balance_pct', np.nan),
                label='Financial Account', linewidth=2, marker='s')
        ax.plot(data['Year'], data.get('Goods and Services Balance_pct', np.nan),
                label='Goods & Services', linewidth=2, marker='^')

        # Add key events
        ax.axvline(x=1994, color='blue', linestyle='--', linewidth=2,
                   label='NAFTA (Jan 1994)', alpha=0.7)
        ax.axvline(x=2001, color='green', linestyle='--', linewidth=2,
                   label='China WTO (Dec 2001)', alpha=0.7)
        ax.axvline(x=2008, color='red', linestyle='--', linewidth=2,
                   label='Financial Crisis (2008)', alpha=0.7)

        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5, alpha=0.5)

        ax.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax.set_ylabel('% of GDP (millions)', fontsize=12, fontweight='bold')
        ax.set_title('US Balance of Payments: NAFTA Era (1985-2015)',
                     fontsize=14, fontweight='bold')
        ax.legend(loc='best', fontsize=9)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save:
            output_path = OUTPUT_CHARTS / "python_us_balance_of_payments_nafta.png"
            fig.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"[SAVED] {output_path.relative_to(PROJECT_ROOT)}")

        return fig

    def plot_germany_reunification(self, save: bool = True) -> plt.Figure:
        """
        Visualize Germany Balance of Payments around reunification (1990).

        Shows the impact of German reunification on:
        - Current account (shift to deficit)
        - Capital inflows
        - Trade balance changes

        Parameters
        ----------
        save : bool, default True
            Whether to save figure

        Returns
        -------
        matplotlib.figure.Figure
        """
        if self.ger_annual_pct is None:
            raise ValueError("Data not loaded. Call load_data() first.")

        print("\n[PLOTTING] Germany Balance of Payments - Reunification (1991-2000)")

        data = self.ger_annual_pct[(self.ger_annual_pct['Year'] >= 1991) &
                                    (self.ger_annual_pct['Year'] <= 2000)]

        fig, ax = plt.subplots(figsize=(14, 8))

        # Plot Germany series (use actual column names)
        ax.plot(data['Year'], data.get('Current Account Balance_pct', np.nan),
                label='Current Account', linewidth=2, marker='o')
        ax.plot(data['Year'], data.get('Financial Account Balance_pct', np.nan),
                label='Financial Account', linewidth=2, marker='s')
        ax.plot(data['Year'], data.get('Total Trade Balance_pct', np.nan),
                label='Trade Balance', linewidth=2, marker='^')

        # Reunification date
        ax.axvline(x=1990, color='red', linestyle='--', linewidth=2,
                   label='Reunification (Oct 1990)', alpha=0.7)
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5, alpha=0.5)

        ax.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax.set_ylabel('% of GDP (millions)', fontsize=12, fontweight='bold')
        ax.set_title('Germany Balance of Payments: Reunification Era (1991-2000)',
                     fontsize=14, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save:
            output_path = OUTPUT_CHARTS / "python_german_balance_of_payments_reunification.png"
            fig.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"[SAVED] {output_path.relative_to(PROJECT_ROOT)}")

        return fig

    def plot_germany_maastricht(self, save: bool = True) -> plt.Figure:
        """
        Visualize Germany Balance of Payments around Maastricht Treaty (1992).

        Shows the period leading to Euro adoption:
        - Maastricht Treaty (1992)
        - Euro introduction (1999)
        - Current account evolution

        Parameters
        ----------
        save : bool, default True
            Whether to save figure

        Returns
        -------
        matplotlib.figure.Figure
        """
        if self.ger_annual_pct is None:
            raise ValueError("Data not loaded. Call load_data() first.")

        print("\n[PLOTTING] Germany Balance of Payments - Maastricht (1991-2005)")

        data = self.ger_annual_pct[(self.ger_annual_pct['Year'] >= 1991) &
                                    (self.ger_annual_pct['Year'] <= 2005)]

        fig, ax = plt.subplots(figsize=(14, 8))

        # Plot Germany series
        ax.plot(data['Year'], data.get('Current Account Balance_pct', np.nan),
                label='Current Account', linewidth=2, marker='o')
        ax.plot(data['Year'], data.get('Financial Account Balance_pct', np.nan),
                label='Financial Account', linewidth=2, marker='s')

        # Key European events
        ax.axvline(x=1992, color='blue', linestyle='--', linewidth=2,
                   label='Maastricht Treaty (1992)', alpha=0.7)
        ax.axvline(x=1999, color='green', linestyle='--', linewidth=2,
                   label='Euro Introduction (1999)', alpha=0.7)
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5, alpha=0.5)

        ax.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax.set_ylabel('% of GDP (millions)', fontsize=12, fontweight='bold')
        ax.set_title('Germany Balance of Payments: Maastricht to Euro (1991-2005)',
                     fontsize=14, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save:
            output_path = OUTPUT_CHARTS / "python_german_balance_of_payments_maastricht.png"
            fig.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"[SAVED] {output_path.relative_to(PROJECT_ROOT)}")

        return fig

    def plot_comparative_current_financial(self, save: bool = True) -> plt.Figure:
        """
        Compare current account and financial account across countries.

        Demonstrates the fundamental BOP identity:
        Current Account + Financial Account + Errors = 0

        Parameters
        ----------
        save : bool, default True
            Whether to save figure

        Returns
        -------
        matplotlib.figure.Figure
        """
        if any(d is None for d in [self.us_annual_pct, self.uk_annual_pct, self.ger_annual_pct]):
            raise ValueError("Data not loaded. Call load_data() first.")

        print("\n[PLOTTING] Comparative Current vs Financial Accounts")

        fig, axes = plt.subplots(1, 3, figsize=(18, 6))

        # US
        us = self.us_annual_pct
        axes[0].scatter(us.get('Current Account Balance_pct'),
                       us.get('Financial Account Balance_pct'),
                       alpha=0.6, s=50)
        axes[0].axhline(y=0, color='black', linestyle='-', linewidth=0.5, alpha=0.5)
        axes[0].axvline(x=0, color='black', linestyle='-', linewidth=0.5, alpha=0.5)
        axes[0].set_xlabel('Current Account (% of GDP)', fontsize=10, fontweight='bold')
        axes[0].set_ylabel('Financial Account (% of GDP)', fontsize=10, fontweight='bold')
        axes[0].set_title('United States', fontsize=12, fontweight='bold')
        axes[0].grid(True, alpha=0.3)

        # UK
        uk = self.uk_annual_pct
        axes[1].scatter(uk.get('Current Account Balance_pct'),
                       uk.get('Financial Account Balance_pct'),
                       alpha=0.6, s=50, color='orange')
        axes[1].axhline(y=0, color='black', linestyle='-', linewidth=0.5, alpha=0.5)
        axes[1].axvline(x=0, color='black', linestyle='-', linewidth=0.5, alpha=0.5)
        axes[1].set_xlabel('Current Account (% of GDP)', fontsize=10, fontweight='bold')
        axes[1].set_ylabel('Financial Account (% of GDP)', fontsize=10, fontweight='bold')
        axes[1].set_title('United Kingdom', fontsize=12, fontweight='bold')
        axes[1].grid(True, alpha=0.3)

        # Germany
        ger = self.ger_annual_pct
        axes[2].scatter(ger.get('Current Account Balance_pct'),
                       ger.get('Financial Account Balance_pct'),
                       alpha=0.6, s=50, color='green')
        axes[2].axhline(y=0, color='black', linestyle='-', linewidth=0.5, alpha=0.5)
        axes[2].axvline(x=0, color='black', linestyle='-', linewidth=0.5, alpha=0.5)
        axes[2].set_xlabel('Current Account (% of GDP)', fontsize=10, fontweight='bold')
        axes[2].set_ylabel('Financial Account (% of GDP)', fontsize=10, fontweight='bold')
        axes[2].set_title('Germany', fontsize=12, fontweight='bold')
        axes[2].grid(True, alpha=0.3)

        plt.suptitle('Current Account vs Financial Account Relationship',
                     fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()

        if save:
            output_path = OUTPUT_CHARTS / "python_comparative_current_financial_accounts.png"
            fig.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"[SAVED] {output_path.relative_to(PROJECT_ROOT)}")

        return fig

    def generate_all_visualizations(self):
        """Generate all visualizations from the original R analysis."""
        print("\n" + "=" * 80)
        print("Generating All Visualizations")
        print("=" * 80)

        self.plot_us_nixon_shock()
        self.plot_us_nafta_period()
        self.plot_germany_reunification()
        self.plot_germany_maastricht()
        self.plot_comparative_current_financial()

        print("\n" + "=" * 80)
        print("All Visualizations Complete!")
        print("=" * 80)
        print(f"\nSaved to: {OUTPUT_CHARTS.relative_to(PROJECT_ROOT)}")


def main():
    """Main execution: replicate Trade ClassFiles R analysis."""
    print("\n" + "=" * 80)
    print("Balance of Payments Comparative Analysis")
    print("Replication of ClassFiles/Trade R Analysis")
    print("=" * 80)

    # Initialize
    analysis = BoPComparativeAnalysis()

    # Load data
    analysis.load_data()

    # Generate all visualizations
    analysis.generate_all_visualizations()

    print("\n[COMPLETE] Analysis replication finished successfully!")


if __name__ == "__main__":
    main()

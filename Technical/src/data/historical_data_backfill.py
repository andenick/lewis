"""
Historical Data Backfill Script
===============================

Automated script to backfill 20+ years of historical economic data using DBnomics API.
This script fetches real data to replace sample data for the Lewis platform.

Author: Claude
Date: 2025-10-14
Version: 1.0
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os
import json
from datetime import datetime, timedelta
import time
import logging

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from dbnomics_collector import DBnomicsCollector
    print("SUCCESS: DBnomics collector imported")
except ImportError as e:
    print(f"FAILED: Could not import DBnomics collector: {e}")
    sys.exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class HistoricalDataBackfill:
    """
    Automated historical data backfill system for Lewis platform.
    """

    def __init__(self, output_dir: Path = None):
        """Initialize backfill system."""
        self.output_dir = output_dir or Path(__file__).parent.parent / "data" / "historical_backfill"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize DBnomics collector
        self.dbnomics = DBnomicsCollector()
        print("SUCCESS: DBnomics collector initialized")

        # Countries to backfill (expanded from our 7 new countries)
        self.target_countries = {
            'Japan': 'JPN',
            'Canada': 'CAN',
            'France': 'FRA',
            'Italy': 'ITA',
            'China': 'CHN',
            'India': 'IND',
            'Brazil': 'BRA',
            'United States': 'USA',
            'United Kingdom': 'GBR',
            'Germany': 'DEU'
        }

        # Data types to collect
        self.data_types = {
            'balance_of_payments': {
                'description': 'Balance of Payments data',
                'priority': 'high'
            },
            'trade_data': {
                'description': 'International trade data',
                'priority': 'high'
            },
            'gdp_data': {
                'description': 'Gross Domestic Product data',
                'priority': 'medium'
            },
            'exchange_rates': {
                'description': 'Exchange rate data',
                'priority': 'medium'
            }
        }

        # Progress tracking
        self.backfill_log = {
            'start_time': datetime.now(),
            'countries_processed': [],
            'data_collected': {},
            'errors': [],
            'summary': {}
        }

    def fetch_historical_bop_data(self, countries: list = None, start_year: int = 2000) -> dict:
        """
        Fetch historical balance of payments data.

        Args:
            countries: List of country names (if None, use all target countries)
            start_year: Starting year for historical data

        Returns:
            Dictionary with country-specific BOP data
        """
        if countries is None:
            countries = list(self.target_countries.keys())

        print(f"\n{'='*60}")
        print("FETCHING HISTORICAL BALANCE OF PAYMENTS DATA")
        print(f"Countries: {', '.join(countries)}")
        print(f"Period: {start_year} to present")
        print(f"{'='*60}")

        bop_results = {}

        for country in countries:
            print(f"\n[{country}] Fetching BOP data...")
            country_code = self.target_countries.get(country, country[:3].upper())

            try:
                # Use the collector's BOP functionality
                country_bop = self.dbnomics.fetch_balance_of_payments_data([country_code])

                if country_bop and country_code in country_bop:
                    df = country_bop[country_code]

                    if not df.empty:
                        # Filter for historical period
                        if 'date' in df.columns:
                            df = df[df['date'].dt.year >= start_year]

                        print(f"  SUCCESS: {len(df)} observations")
                        if 'date' in df.columns:
                            print(f"    Period: {df['date'].min()} to {df['date'].max()}")

                        # Save individual country data
                        output_file = self.output_dir / f"bop_{country_code.lower()}_historical.csv"
                        df.to_csv(output_file, index=False)
                        print(f"    Saved: {output_file.name}")

                        bop_results[country_code] = {
                            'data': df,
                            'observations': len(df),
                            'period_start': df['date'].min() if 'date' in df.columns else None,
                            'period_end': df['date'].max() if 'date' in df.columns else None,
                            'saved_to': str(output_file)
                        }

                        self.backfill_log['countries_processed'].append(country)
                    else:
                        print(f"  INFO: No BOP data available")
                        bop_results[country_code] = {'data': pd.DataFrame(), 'observations': 0}
                else:
                    print(f"  INFO: No BOP data returned")
                    bop_results[country_code] = {'data': pd.DataFrame(), 'observations': 0}

            except Exception as e:
                print(f"  ERROR: Failed to fetch BOP data - {e}")
                self.backfill_log['errors'].append(f"BOP data for {country}: {e}")
                bop_results[country_code] = {'data': pd.DataFrame(), 'error': str(e)}

        self.backfill_log['data_collected']['balance_of_payments'] = bop_results
        return bop_results

    def fetch_historical_trade_data(self, countries: list = None, start_year: int = 2000) -> dict:
        """
        Fetch historical trade data.

        Args:
            countries: List of country names
            start_year: Starting year for historical data

        Returns:
            Dictionary with country-specific trade data
        """
        if countries is None:
            countries = list(self.target_countries.keys())

        print(f"\n{'='*60}")
        print("FETCHING HISTORICAL TRADE DATA")
        print(f"Countries: {', '.join(countries)}")
        print(f"Period: {start_year} to present")
        print(f"{'='*60}")

        trade_results = {}

        for country in countries:
            print(f"\n[{country}] Fetching trade data...")
            country_code = self.target_countries.get(country, country[:3].upper())

            try:
                # Use the collector's trade functionality
                country_trade = self.dbnomics.fetch_trade_data([country_code])

                if country_trade and country_code in country_trade:
                    df = country_trade[country_code]

                    if not df.empty:
                        # Filter for historical period
                        if 'date' in df.columns:
                            df = df[df['date'].dt.year >= start_year]

                        print(f"  SUCCESS: {len(df)} observations")
                        if 'date' in df.columns:
                            print(f"    Period: {df['date'].min()} to {df['date'].max()}")

                        # Save individual country data
                        output_file = self.output_dir / f"trade_{country_code.lower()}_historical.csv"
                        df.to_csv(output_file, index=False)
                        print(f"    Saved: {output_file.name}")

                        trade_results[country_code] = {
                            'data': df,
                            'observations': len(df),
                            'period_start': df['date'].min() if 'date' in df.columns else None,
                            'period_end': df['date'].max() if 'date' in df.columns else None,
                            'saved_to': str(output_file)
                        }
                    else:
                        print(f"  INFO: No trade data available")
                        trade_results[country_code] = {'data': pd.DataFrame(), 'observations': 0}
                else:
                    print(f"  INFO: No trade data returned")
                    trade_results[country_code] = {'data': pd.DataFrame(), 'observations': 0}

            except Exception as e:
                print(f"  ERROR: Failed to fetch trade data - {e}")
                self.backfill_log['errors'].append(f"Trade data for {country}: {e}")
                trade_results[country_code] = {'data': pd.DataFrame(), 'error': str(e)}

        self.backfill_log['data_collected']['trade_data'] = trade_results
        return trade_results

    def fetch_historical_gdp_data(self, countries: list = None, start_year: int = 2000) -> dict:
        """
        Fetch historical GDP data.

        Args:
            countries: List of country names
            start_year: Starting year for historical data

        Returns:
            Dictionary with country-specific GDP data
        """
        if countries is None:
            countries = list(self.target_countries.keys())

        print(f"\n{'='*60}")
        print("FETCHING HISTORICAL GDP DATA")
        print(f"Countries: {', '.join(countries)}")
        print(f"Period: {start_year} to present")
        print(f"{'='*60}")

        gdp_results = {}

        for country in countries:
            print(f"\n[{country}] Fetching GDP data...")
            country_code = self.target_countries.get(country, country[:3].upper())

            try:
                # Use the collector's GDP functionality
                country_gdp = self.dbnomics.fetch_gdp_data([country_code])

                if country_gdp and country_code in country_gdp:
                    df = country_gdp[country_code]

                    if not df.empty:
                        # Filter for historical period
                        if 'date' in df.columns:
                            df = df[df['date'].dt.year >= start_year]

                        print(f"  SUCCESS: {len(df)} observations")
                        if 'date' in df.columns:
                            print(f"    Period: {df['date'].min()} to {df['date'].max()}")

                        # Save individual country data
                        output_file = self.output_dir / f"gdp_{country_code.lower()}_historical.csv"
                        df.to_csv(output_file, index=False)
                        print(f"    Saved: {output_file.name}")

                        gdp_results[country_code] = {
                            'data': df,
                            'observations': len(df),
                            'period_start': df['date'].min() if 'date' in df.columns else None,
                            'period_end': df['date'].max() if 'date' in df.columns else None,
                            'saved_to': str(output_file)
                        }
                    else:
                        print(f"  INFO: No GDP data available")
                        gdp_results[country_code] = {'data': pd.DataFrame(), 'observations': 0}
                else:
                    print(f"  INFO: No GDP data returned")
                    gdp_results[country_code] = {'data': pd.DataFrame(), 'observations': 0}

            except Exception as e:
                print(f"  ERROR: Failed to fetch GDP data - {e}")
                self.backfill_log['errors'].append(f"GDP data for {country}: {e}")
                gdp_results[country_code] = {'data': pd.DataFrame(), 'error': str(e)}

        self.backfill_log['data_collected']['gdp_data'] = gdp_results
        return gdp_results

    def create_master_datasets(self) -> dict:
        """Create master datasets combining all countries and data types."""
        print(f"\n{'='*60}")
        print("CREATING MASTER HISTORICAL DATASETS")
        print(f"{'='*60}")

        master_datasets = {}

        # Combine all BOP data
        print("\nCreating master BOP dataset...")
        all_bop = []
        if 'balance_of_payments' in self.backfill_log['data_collected']:
            for country_code, data_info in self.backfill_log['data_collected']['balance_of_payments'].items():
                if 'data' in data_info and not data_info['data'].empty:
                    df = data_info['data'].copy()
                    all_bop.append(df)

        if all_bop:
            master_bop = pd.concat(all_bop, ignore_index=True)
            master_bop_file = self.output_dir / "master_balance_of_payments_historical.csv"
            master_bop.to_csv(master_bop_file, index=False)
            print(f"SUCCESS: Master BOP dataset created - {len(master_bop)} observations")
            print(f"Saved: {master_bop_file.name}")
            master_datasets['balance_of_payments'] = {
                'observations': len(master_bop),
                'countries': master_bop['country'].nunique() if 'country' in master_bop.columns else 0,
                'file': str(master_bop_file)
            }

        # Combine all trade data
        print("\nCreating master trade dataset...")
        all_trade = []
        if 'trade_data' in self.backfill_log['data_collected']:
            for country_code, data_info in self.backfill_log['data_collected']['trade_data'].items():
                if 'data' in data_info and not data_info['data'].empty:
                    df = data_info['data'].copy()
                    all_trade.append(df)

        if all_trade:
            master_trade = pd.concat(all_trade, ignore_index=True)
            master_trade_file = self.output_dir / "master_trade_historical.csv"
            master_trade.to_csv(master_trade_file, index=False)
            print(f"SUCCESS: Master trade dataset created - {len(master_trade)} observations")
            print(f"Saved: {master_trade_file.name}")
            master_datasets['trade_data'] = {
                'observations': len(master_trade),
                'countries': master_trade['country'].nunique() if 'country' in master_trade.columns else 0,
                'file': str(master_trade_file)
            }

        # Combine all GDP data
        print("\nCreating master GDP dataset...")
        all_gdp = []
        if 'gdp_data' in self.backfill_log['data_collected']:
            for country_code, data_info in self.backfill_log['data_collected']['gdp_data'].items():
                if 'data' in data_info and not data_info['data'].empty:
                    df = data_info['data'].copy()
                    all_gdp.append(df)

        if all_gdp:
            master_gdp = pd.concat(all_gdp, ignore_index=True)
            master_gdp_file = self.output_dir / "master_gdp_historical.csv"
            master_gdp.to_csv(master_gdp_file, index=False)
            print(f"SUCCESS: Master GDP dataset created - {len(master_gdp)} observations")
            print(f"Saved: {master_gdp_file.name}")
            master_datasets['gdp_data'] = {
                'observations': len(master_gdp),
                'countries': master_gdp['country'].nunique() if 'country' in master_gdp.columns else 0,
                'file': str(master_gdp_file)
            }

        self.backfill_log['master_datasets'] = master_datasets
        return master_datasets

    def generate_backfill_report(self) -> str:
        """Generate comprehensive backfill report."""
        print(f"\n{'='*80}")
        print("HISTORICAL DATA BACKFILL REPORT")
        print(f"{'='*80}")

        end_time = datetime.now()
        duration = end_time - self.backfill_log['start_time']

        report_lines = [
            f"Backfill Period: {self.backfill_log['start_time'].strftime('%Y-%m-%d %H:%M:%S')} to {end_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Duration: {duration}",
            "",
            f"Countries Processed: {len(self.backfill_log['countries_processed'])}",
            f"Countries: {', '.join(self.backfill_log['countries_processed'])}",
            "",
            "Data Collection Summary:"
        ]

        # Data collection summary
        for data_type, results in self.backfill_log['data_collected'].items():
            total_observations = sum(info.get('observations', 0) for info in results.values())
            countries_with_data = len([info for info in results.values() if info.get('observations', 0) > 0])
            report_lines.append(f"  {data_type}: {total_observations:,} observations across {countries_with_data} countries")

        # Master datasets summary
        if 'master_datasets' in self.backfill_log:
            report_lines.append("")
            report_lines.append("Master Datasets Created:")
            for data_type, info in self.backfill_log['master_datasets'].items():
                report_lines.append(f"  {data_type}: {info['observations']:,} observations, {info['countries']} countries")

        # Errors
        if self.backfill_log['errors']:
            report_lines.append("")
            report_lines.append(f"Errors Encountered: {len(self.backfill_log['errors'])}")
            for error in self.backfill_log['errors'][:5]:  # Show first 5 errors
                report_lines.append(f"  - {error}")
            if len(self.backfill_log['errors']) > 5:
                report_lines.append(f"  ... and {len(self.backfill_log['errors']) - 5} more errors")

        report_lines.append("")
        report_lines.append(f"Output Directory: {self.output_dir}")
        report_lines.append("="*80)

        report = "\n".join(report_lines)
        print(report)

        return report

    def save_backfill_log(self):
        """Save detailed backfill log."""
        log_file = self.output_dir / f"backfill_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        # Convert datetime objects to strings for JSON serialization
        log_copy = self.backfill_log.copy()
        log_copy['start_time'] = log_copy['start_time'].isoformat()

        # Convert DataFrame objects to summary info
        for data_type, results in log_copy['data_collected'].items():
            for country_code, info in results.items():
                if 'data' in info:
                    # Remove actual DataFrame, keep summary info
                    df = info['data']
                    info.pop('data', None)
                    if not df.empty:
                        info['summary'] = {
                            'columns': list(df.columns),
                            'dtypes': df.dtypes.to_dict(),
                            'shape': df.shape
                        }

        with open(log_file, 'w') as f:
            json.dump(log_copy, f, indent=2, default=str)

        print(f"\nDetailed backfill log saved to: {log_file}")
        return log_file

    def run_complete_backfill(self, countries: list = None, start_year: int = 2000):
        """Run complete historical data backfill."""
        print("STARTING COMPLETE HISTORICAL DATA BACKFILL")
        print("="*80)
        print(f"Target Countries: {countries if countries else 'All target countries'}")
        print(f"Start Year: {start_year}")
        print(f"Output Directory: {self.output_dir}")
        print("="*80)

        # Fetch all data types
        self.fetch_historical_bop_data(countries, start_year)
        self.fetch_historical_trade_data(countries, start_year)
        self.fetch_historical_gdp_data(countries, start_year)

        # Create master datasets
        self.create_master_datasets()

        # Generate report
        report = self.generate_backfill_report()

        # Save log
        self.save_backfill_log()

        # Save report
        report_file = self.output_dir / f"backfill_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w') as f:
            f.write(report)

        print(f"\nBackfill report saved to: {report_file}")
        print("COMPLETE: Historical data backfill finished!")

        return self.backfill_log


def main():
    """Main execution for historical data backfill."""
    print("HISTORICAL DATA BACKFILL SYSTEM")
    print("=" * 50)
    print("Automated backfill of 20+ years of economic data using DBnomics API")

    # Initialize backfill system
    backfill = HistoricalDataBackfill()

    # Run backfill for our target countries
    countries = ['Japan', 'Canada', 'France', 'Italy', 'China', 'India', 'Brazil']

    print(f"\nRunning backfill for countries: {', '.join(countries)}")

    # Execute complete backfill
    results = backfill.run_complete_backfill(
        countries=countries,
        start_year=2000
    )

    # Summary
    total_observations = 0
    for data_type, country_data in results['data_collected'].items():
        for country_code, info in country_data.items():
            total_observations += info.get('observations', 0)

    print(f"\nBACKFILL SUMMARY:")
    print(f"- Total observations collected: {total_observations:,}")
    print(f"- Countries processed: {len(results['countries_processed'])}")
    print(f"- Errors encountered: {len(results['errors'])}")
    print(f"- Output directory: {backfill.output_dir}")

    if total_observations > 0:
        print(f"\nSUCCESS: Historical data backfill completed successfully!")
        print(f"The Lewis platform now has real economic data to replace sample data.")
    else:
        print(f"\nINFO: No historical data was collected. This may be due to API limitations.")
        print(f"Sample data will continue to be used for analysis.")

    return results


if __name__ == "__main__":
    main()
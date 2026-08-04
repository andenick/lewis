"""
World Bank Data Collector - Phase 2 Expansion
==============================================

Expand beyond the initial 60 countries to cover more global economies.

Phase 2 adds 30 additional countries for total coverage of 90 countries.

Author: Claude
Date: 2025-10-06
"""

import os
import pandas as pd
import requests
import time
from pathlib import Path
from typing import List, Dict, Optional
import sys

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.append(str(PROJECT_ROOT / "Technical" / "src"))

from data.collection_tracker import CollectionTracker

# Paths
OUTPUT_ROOT = Path(os.environ.get("OUTPUT_ROOT", "outputs"))
WB_PHASE2_PATH = OUTPUT_ROOT / "World_Bank_Phase2"
WB_PHASE2_PATH.mkdir(parents=True, exist_ok=True)


class WorldBankPhase2Collector:
    """
    Collect World Bank data for Phase 2 countries.

    Adds 30 more countries beyond the initial 60.
    """

    def __init__(self):
        """Initialize collector."""
        self.base_url = "https://api.worldbank.org/v2"
        self.session = requests.Session()
        self.tracker = CollectionTracker()

        # Phase 2 countries (30 additional)
        self.phase2_countries = [
            # Additional Europe (5)
            'EST', 'LVA', 'LTU', 'MLT', 'CYP',

            # Additional Middle East (4)
            'JOR', 'LBN', 'OMN', 'BHR',

            # Additional Asia (8)
            'KHM', 'MMR', 'NPL', 'AFG', 'UZB', 'KAZ', 'MNG', 'LAO',

            # Additional Latin America (8)
            'ECU', 'GTM', 'CRI', 'URY', 'PAN', 'PRY', 'BOL', 'HND',

            # Additional Africa (5)
            'GHA', 'ETH', 'TZA', 'UGA', 'CMR',
        ]

        # Same 34 indicators as Phase 1
        self.indicators = {
            # GDP and Growth (5)
            'NY.GDP.MKTP.CD': 'GDP_Current_USD',
            'NY.GDP.MKTP.KD': 'GDP_Constant_2015_USD',
            'NY.GDP.MKTP.KD.ZG': 'GDP_Growth_Annual_Pct',
            'NY.GDP.PCAP.CD': 'GDP_Per_Capita_Current_USD',
            'NY.GDP.PCAP.KD': 'GDP_Per_Capita_Constant_2015_USD',

            # Trade (11)
            'NE.EXP.GNFS.CD': 'Exports_Goods_Services_USD',
            'NE.EXP.GNFS.ZS': 'Exports_Pct_GDP',
            'NE.EXP.GNFS.KD': 'Exports_Goods_Services_Constant_USD',
            'NE.IMP.GNFS.CD': 'Imports_Goods_Services_USD',
            'NE.IMP.GNFS.KD': 'Imports_Goods_Services_Constant_USD',
            'NE.IMP.GNFS.ZS': 'Imports_Pct_GDP',
            'TG.VAL.TOTL.GD.ZS': 'Merchandise_Trade_Pct_GDP',
            'TX.VAL.TECH.CD': 'High_Tech_Exports_USD',
            'TM.VAL.MRCH.CD.WT': 'Merchandise_Imports_USD',
            'TX.VAL.MRCH.CD.WT': 'Merchandise_Exports_USD',
            'BM.GSR.GNFS.CD': 'Imports_Goods_Services_BoP_USD',

            # Balance of Payments (4)
            'BN.CAB.XOKA.CD': 'Current_Account_USD',
            'BN.CAB.XOKA.GD.ZS': 'Current_Account_Pct_GDP',
            'BX.GSR.GNFS.CD': 'Exports_Goods_Services_BoP_USD',
            'BN.KLT.PTXL.CD': 'Portfolio_Investment_Net',

            # Investment (4)
            'BX.KLT.DINV.CD.WD': 'FDI_Net_Inflows_USD',
            'BX.KLT.DINV.WD.GD.ZS': 'FDI_Net_Inflows_Pct_GDP',
            'BM.KLT.DINV.CD.WD': 'FDI_Net_Outflows_USD',
            'NE.GDI.TOTL.ZS': 'Gross_Capital_Formation_Pct_GDP',

            # External Debt (4)
            'DT.DOD.DECT.CD': 'External_Debt_Stocks_Total_USD',
            'DT.DOD.DECT.GN.ZS': 'External_Debt_Stocks_Pct_GNI',
            'DT.TDS.DECT.CD': 'Debt_Service_Total_USD',
            'DT.TDS.DECT.GN.ZS': 'Debt_Service_Pct_GNI',

            # Labor (2)
            'SL.UEM.TOTL.ZS': 'Unemployment_Total_Pct',
            'SL.TLF.TOTL.IN': 'Labor_Force_Total',

            # Remittances (2)
            'BX.TRF.PWKR.CD.DT': 'Personal_Remittances_Received_USD',
            'BM.TRF.PWKR.CD.DT': 'Personal_Remittances_Paid_USD',

            # Tourism (2)
            'ST.INT.RCPT.CD': 'International_Tourism_Receipts_USD',
            'ST.INT.XPND.CD': 'International_Tourism_Expenditures_USD',
        }

        print("="*80)
        print("WORLD BANK PHASE 2 COLLECTOR")
        print("="*80)
        print(f"Phase 2 Countries: {len(self.phase2_countries)}")
        print(f"Indicators: {len(self.indicators)}")
        print(f"Output: {WB_PHASE2_PATH}")
        print()

    def get_country_data(self, country: str, start_year: int = 2000,
                        end_year: int = 2024) -> pd.DataFrame:
        """Get all indicators for a country."""
        print(f"\n[{country}] Collecting World Bank data...")

        all_data = []
        success_count = 0
        skip_count = 0
        error_count = 0

        for indicator_code, indicator_name in self.indicators.items():
            # Check if already collected
            if self.tracker.is_collected('World_Bank_Phase2', country,
                                        indicator_code, start_year, end_year):
                skip_count += 1
                continue

            # Build URL
            url = f"{self.base_url}/country/{country}/indicator/{indicator_code}"
            params = {
                'date': f'{start_year}:{end_year}',
                'format': 'json',
                'per_page': 500
            }

            try:
                response = self.session.get(url, params=params, timeout=30)

                if response.status_code == 200:
                    data = response.json()

                    if len(data) > 1 and data[1]:
                        records = []
                        for obs in data[1]:
                            if obs['value'] is not None:
                                records.append({
                                    'country': country,
                                    'country_name': obs.get('country', {}).get('value', country),
                                    'indicator_code': indicator_code,
                                    'indicator_name': indicator_name,
                                    'year': int(obs['date']),
                                    'value': float(obs['value'])
                                })

                        if records:
                            df = pd.DataFrame(records)
                            all_data.append(df)
                            success_count += 1
                            print(f"  [OK] {indicator_code}: {len(records)} obs")

                            # Record success
                            self.tracker.record_collection(
                                source='World_Bank_Phase2',
                                country=country,
                                indicator=indicator_code,
                                start_year=start_year,
                                end_year=end_year,
                                observations=len(records),
                                file_path=str(WB_PHASE2_PATH / f"wb_phase2_{country}_{indicator_code}.csv"),
                                success=True
                            )
                        else:
                            error_count += 1
                            self.tracker.record_collection(
                                source='World_Bank_Phase2',
                                country=country,
                                indicator=indicator_code,
                                start_year=start_year,
                                end_year=end_year,
                                observations=0,
                                file_path="",
                                success=False,
                                error="No data available"
                            )
                    else:
                        error_count += 1
                        self.tracker.record_collection(
                            source='World_Bank_Phase2',
                            country=country,
                            indicator=indicator_code,
                            start_year=start_year,
                            end_year=end_year,
                            observations=0,
                            file_path="",
                            success=False,
                            error="No data in response"
                        )
                else:
                    error_count += 1
                    self.tracker.record_collection(
                        source='World_Bank_Phase2',
                        country=country,
                        indicator=indicator_code,
                        start_year=start_year,
                        end_year=end_year,
                        observations=0,
                        file_path="",
                        success=False,
                        error=f"HTTP {response.status_code}"
                    )

                # Rate limiting
                time.sleep(0.1)

            except Exception as e:
                error_count += 1
                self.tracker.record_collection(
                    source='World_Bank_Phase2',
                    country=country,
                    indicator=indicator_code,
                    start_year=start_year,
                    end_year=end_year,
                    observations=0,
                    file_path="",
                    success=False,
                    error=str(e)
                )
                time.sleep(0.5)

        print(f"  Summary: {success_count} success, {skip_count} skipped, {error_count} failed")

        if all_data:
            return pd.concat(all_data, ignore_index=True)
        else:
            return pd.DataFrame()

    def collect_all_countries(self, batch_size: int = 5):
        """Collect all Phase 2 countries in batches."""
        print("\n" + "="*80)
        print(f"COLLECTING PHASE 2: {len(self.phase2_countries)} COUNTRIES")
        print("="*80)

        total_obs = 0

        for i in range(0, len(self.phase2_countries), batch_size):
            batch = self.phase2_countries[i:i+batch_size]
            batch_num = i//batch_size + 1

            print(f"\n{'='*80}")
            print(f"BATCH {batch_num}: {', '.join(batch)}")
            print(f"{'='*80}")

            batch_data = []

            for country in batch:
                df = self.get_country_data(country)
                if len(df) > 0:
                    batch_data.append(df)
                    total_obs += len(df)

            # Save batch
            if batch_data:
                batch_df = pd.concat(batch_data, ignore_index=True)
                batch_file = WB_PHASE2_PATH / f"Batch_{batch_num}.csv"
                batch_df.to_csv(batch_file, index=False, encoding='utf-8')
                print(f"\n  [SAVED] {batch_file.name} ({len(batch_df):,} obs)")

            # Pause between batches
            if i + batch_size < len(self.phase2_countries):
                print("\n  [PAUSE] 10 seconds...")
                time.sleep(10)

        print("\n" + "="*80)
        print("PHASE 2 COLLECTION COMPLETE")
        print("="*80)
        print(f"Total observations: {total_obs:,}")

        return total_obs

    def combine_all_batches(self):
        """Combine all batch files."""
        print("\n[COMBINE] Combining batches...")

        all_files = list(WB_PHASE2_PATH.glob("Batch_*.csv"))

        if not all_files:
            print("  No batch files found.")
            return

        all_data = [pd.read_csv(f) for f in all_files]
        combined = pd.concat(all_data, ignore_index=True)

        # Save combined
        combined_file = WB_PHASE2_PATH / "worldbank_phase2_all.csv"
        combined.to_csv(combined_file, index=False, encoding='utf-8')

        print(f"  Saved: {combined_file.name}")
        print(f"  Total observations: {len(combined):,}")
        print(f"  Countries: {combined['country'].nunique()}")
        print(f"  Indicators: {combined['indicator_code'].nunique()}")


def main():
    """Main execution."""
    collector = WorldBankPhase2Collector()

    # Check for --auto flag
    auto = '--auto' in sys.argv or not sys.stdin.isatty()

    if auto:
        collector.collect_all_countries(batch_size=5)
        collector.combine_all_batches()
    else:
        response = input("\nStart Phase 2 collection (30 countries)? (y/n): ")
        if response.lower() == 'y':
            collector.collect_all_countries(batch_size=5)
            collector.combine_all_batches()


if __name__ == "__main__":
    main()

"""
World Bank Expanded Country Coverage
=====================================

Expand World Bank data collection from 26 priority countries to 150+ countries.

This will massively increase the platform's geographic coverage while maintaining
data quality through the reliable World Bank API.

Target:
- 150+ countries (vs current 26)
- BoP, Trade, GDP indicators
- 2000-2024 time period
- Expected: 30,000+ new observations

Author: Claude (Lewis Platform)
Date: 2025-10-11
"""

import sys
from pathlib import Path

# Add project to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.append(str(PROJECT_ROOT / "Technical" / "src" / "data"))

# Import existing collector
from worldbank_data_collector import WorldBankDataCollector

# Comprehensive country list (150+ countries)
COMPREHENSIVE_COUNTRIES = [
    # G7
    'USA', 'GBR', 'DEU', 'FRA', 'ITA', 'JPN', 'CAN',

    # G20
    'CHN', 'IND', 'BRA', 'MEX', 'ARG', 'AUS', 'KOR', 'IDN', 'TUR', 'SAU', 'ZAF', 'RUS',

    # EU27 (all members)
    'AUT', 'BEL', 'BGR', 'HRV', 'CYP', 'CZE', 'DNK', 'EST', 'FIN', 'FRA',
    'DEU', 'GRC', 'HUN', 'IRL', 'ITA', 'LVA', 'LTU', 'LUX', 'MLT', 'NLD',
    'POL', 'PRT', 'ROU', 'SVK', 'SVN', 'ESP', 'SWE',

    # Other European
    'CHE', 'NOR', 'ISL', 'GBR', 'UKR', 'BLR', 'MDA', 'SRB', 'MKD', 'ALB',
    'BIH', 'MNE', 'XKX',

    # Asia-Pacific (Advanced)
    'SGP', 'HKG', 'TWN', 'NZL',

    # Asia-Pacific (Emerging)
    'THA', 'MYS', 'PHL', 'VNM', 'BGD', 'PAK', 'LKA', 'MMR', 'KHM', 'LAO',
    'NPL', 'BTN', 'MDV', 'MNG', 'FJI', 'PNG', 'WSM', 'TON', 'VUT', 'SLB',

    # Central Asia
    'KAZ', 'UZB', 'TKM', 'KGZ', 'TJK', 'AZE', 'ARM', 'GEO',

    # Middle East & North Africa
    'ARE', 'QAT', 'KWT', 'BHR', 'OMN', 'ISR', 'EGY', 'MAR', 'TUN', 'DZA',
    'LBY', 'LBN', 'JOR', 'IRQ', 'YEM', 'PSE',

    # Sub-Saharan Africa (All regions)
    # West Africa
    'NGA', 'GHA', 'CIV', 'SEN', 'MLI', 'BFA', 'NER', 'BEN', 'TGO', 'GIN',
    'GNB', 'LBR', 'SLE', 'GMB', 'CPV', 'MRT',

    # East Africa
    'KEN', 'ETH', 'TZA', 'UGA', 'RWA', 'BDI', 'SOM', 'ERI', 'DJI', 'SSD',
    'SYC', 'COM', 'MUS',

    # Southern Africa
    'ZAF', 'ZWE', 'ZMB', 'BWA', 'NAM', 'MOZ', 'AGO', 'MWI', 'SWZ', 'LSO',

    # Central Africa
    'COD', 'CAF', 'CMR', 'TCD', 'GAB', 'COG', 'GNQ', 'STP',

    # Latin America & Caribbean
    # South America
    'BRA', 'ARG', 'CHL', 'COL', 'PER', 'VEN', 'ECU', 'BOL', 'PRY', 'URY',
    'GUY', 'SUR', 'FLK',

    # Central America
    'MEX', 'GTM', 'HND', 'SLV', 'NIC', 'CRI', 'PAN', 'BLZ',

    # Caribbean
    'CUB', 'DOM', 'HTI', 'JAM', 'TTO', 'BHS', 'BRB', 'GRD', 'LCA', 'VCT',
    'ATG', 'DMA', 'KNA', 'ABW', 'CUW', 'SXM', 'BES',

    # Pacific Islands
    'PLW', 'FSM', 'MHL', 'NRU', 'KIR', 'TUV',

    # North America (additional)
    'USA', 'CAN', 'GRL',
]


def main():
    """Run expanded World Bank collection."""
    print("\n" + "="*80)
    print("WORLD BANK EXPANDED GEOGRAPHIC COVERAGE")
    print("="*80)
    print(f"\nExpanding from 26 priority countries to {len(set(COMPREHENSIVE_COUNTRIES))} countries")
    print("\nData to collect:")
    print("  - Balance of Payments indicators (7)")
    print("  - Trade indicators (6)")
    print("  - GDP indicators (4)")
    print("  - Period: 2000-2024")
    print(f"\nExpected output: ~30,000 new observations")

    # Initialize collector
    collector = WorldBankDataCollector()

    # Get unique countries (remove duplicates)
    countries = sorted(set(COMPREHENSIVE_COUNTRIES))

    print(f"\n[INFO] Final country count: {len(countries)}")
    print(f"[INFO] Starting collection...")

    # Collect all data
    data = collector.collect_all(
        countries=countries,
        start_year=2000,
        end_year=2024
    )

    print("\n" + "="*80)
    print("EXPANDED COLLECTION COMPLETE")
    print("="*80)

    if data:
        total_obs = sum(len(df) for df in data.values() if not df.empty)
        print(f"\nTotal observations collected: {total_obs:,}")
        print(f"Countries covered: {len(countries)}")

        print(f"\nBreakdown:")
        for dataset_name, df in data.items():
            if not df.empty:
                print(f"  {dataset_name.upper()}: {len(df):,} observations, "
                      f"{df['country'].nunique()} countries")

    print(f"\n[SUCCESS] Lewis platform geographic coverage significantly expanded!")


if __name__ == "__main__":
    main()

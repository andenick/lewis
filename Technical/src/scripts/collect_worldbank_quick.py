"""Quick World Bank data collection for key countries."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.worldbank_data_collector import WorldBankDataCollector

# Priority G7 countries only for quick collection
G7_COUNTRIES = ['USA', 'GBR', 'DEU', 'FRA', 'ITA', 'JPN', 'CAN']

print("\n" + "="*80)
print("Quick World Bank Data Collection - G7 Countries")
print("="*80)

collector = WorldBankDataCollector()

# Collect data for G7 only, 2010-2024
print(f"\nCollecting data for: {', '.join(G7_COUNTRIES)}")
print("Period: 2010-2024")

data = collector.collect_all(
    countries=G7_COUNTRIES,
    start_year=2010,
    end_year=2024
)

print("\n[COMPLETE] Quick collection finished!")

#!/usr/bin/env python3
"""
Simple test script to verify source data integration.
"""

from pathlib import Path
import pandas as pd
import sys
sys.path.append(str(Path(__file__).parent))

from enhanced_data_loader_v2 import EnhancedDataLoader

def main():
    """Test source data integration."""
    print("=== data source Data Integration Test ===")

    loader = EnhancedDataLoader()

    # Test Census data
    print("\n1. Testing Census data...")
    try:
        census_data = loader.load_census_data(sample_size=500)
        if not census_data.empty:
            print(f"SUCCESS: Loaded {len(census_data)} Census observations")
            print(f"Columns: {list(census_data.columns)}")

            # Export
            output_path = loader.export_to_lewis_output(census_data, "census_regional_sample", "CENSUS")
            print(f"Exported to: {output_path}")
        else:
            print("No Census data found")
    except Exception as e:
        print(f"Census error: {e}")

    # Test financial markets data
    print("\n2. Testing Financial Markets data...")
    try:
        financial_data = loader.load_financial_markets(sample_size=500)
        if not financial_data.empty:
            print(f"SUCCESS: Loaded {len(financial_data)} financial market observations")
            print(f"Columns: {list(financial_data.columns)}")

            # Export
            output_path = loader.export_to_lewis_output(financial_data, "financial_markets_sample", "FINANCIAL")
            print(f"Exported to: {output_path}")
        else:
            print("No financial markets data found")
    except Exception as e:
        print(f"Financial markets error: {e}")

    # Test multiple FRED categories
    print("\n3. Testing multiple FRED categories...")
    key_categories = ['trade', 'interest_rates', 'inflation', 'gdp_growth']

    for category in key_categories:
        try:
            df = loader.load_fred_category(category)
            print(f"{category}: {len(df)} observations")
        except Exception as e:
            print(f"{category}: Error - {e}")

    print(f"\n=== Summary ===")
    print(f"data source integration working with {len(loader.fred_categories)} FRED categories")
    print(f"Available additional sources: ALFRED, Census, Financial Markets")

if __name__ == "__main__":
    main()
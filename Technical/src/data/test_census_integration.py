#!/usr/bin/env python3
"""
Test script to integrate Census data from the source store into Lewis platform.
"""

from pathlib import Path
import pandas as pd
import sys
sys.path.append(str(Path(__file__).parent))

from enhanced_data_loader_v2 import EnhancedDataLoader

def test_census_integration():
    """Test Census data integration from the source store."""
    print("=== Census Data Integration Test ===")

    loader = EnhancedDataLoader()

    # Test loading Census data
    print("\n1. Loading Census data (sample)...")
    census_data = loader.load_census_data(sample_size=1000)

    if not census_data.empty:
        print(f"✓ Loaded {len(census_data)} Census observations")
        print(f"✓ Columns: {list(census_data.columns)}")
        print(f"✓ Source files: {census_data['source_file'].nunique()} different files")

        # Show sample data
        print("\n2. Sample Census data:")
        print(census_data.head())

        # Export to Lewis output
        print("\n3. Exporting to Lewis output...")
        output_path = loader.export_to_lewis_output(
            census_data,
            "census_sample_data",
            "CENSUS_REGIONAL"
        )
        print(f"✓ Exported to: {output_path}")

        return True
    else:
        print("✗ No Census data found")
        return False

def test_financial_markets_integration():
    """Test financial markets data integration from the source store."""
    print("\n=== Financial Markets Integration Test ===")

    loader = EnhancedDataLoader()

    # Test loading financial markets data
    print("\n1. Loading financial markets data (sample)...")
    financial_data = loader.load_financial_markets(sample_size=1000)

    if not financial_data.empty:
        print(f"✓ Loaded {len(financial_data)} financial market observations")
        print(f"✓ Columns: {list(financial_data.columns)}")
        print(f"✓ Source files: {financial_data['source_file'].nunique()} different files")

        # Show sample data
        print("\n2. Sample financial markets data:")
        print(financial_data.head())

        # Export to Lewis output
        print("\n3. Exporting to Lewis output...")
        output_path = loader.export_to_lewis_output(
            financial_data,
            "financial_markets_sample",
            "FINANCIAL_MARKETS"
        )
        print(f"✓ Exported to: {output_path}")

        return True
    else:
        print("✗ No financial markets data found")
        return False

if __name__ == "__main__":
    census_success = test_census_integration()
    financial_success = test_financial_markets_integration()

    print(f"\n=== Integration Results ===")
    print(f"Census integration: {'✓ SUCCESS' if census_success else '✗ FAILED'}")
    print(f"Financial markets integration: {'✓ SUCCESS' if financial_success else '✗ FAILED'}")
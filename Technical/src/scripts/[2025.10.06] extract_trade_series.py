"""
Extract and Organize International Trade Series
================================================

This script extracts individual trade series from the comprehensive FRED trade
dataset and organizes them into separate files for easier analysis.

Series Extracted:
- Balance of Payments components
- Trade balances (goods, services, combined)
- Exports and imports
- Exchange rates
- Trade-weighted dollar indices

Author: Lewis Platform
Date: October 6, 2025
"""

import os
import pandas as pd
from pathlib import Path
import json
from datetime import datetime
DATA_ROOT = Path(os.environ.get("DATA_ROOT", "data"))


def extract_trade_series():
    """Extract individual series from comprehensive FRED trade file."""

    # Paths
    project_root = Path(__file__).parent.parent.parent.parent  # Go up to project root
    comprehensive_dir = DATA_ROOT / "COMPREHENSIVE_COLLECTION"
    output_dir = DATA_ROOT / "BY_SERIES"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load comprehensive trade file
    trade_file = comprehensive_dir / "fred_trade_20250929.csv"
    print(f"Loading comprehensive FRED trade data from {trade_file}...")
    df = pd.read_csv(trade_file)

    # Series definitions
    series_info = {
        'BOPBCA': {
            'name': 'Current Account Balance',
            'description': 'US Balance of Payments - Current Account',
            'units': 'Millions of Dollars',
            'frequency': 'Quarterly',
            'category': 'Balance of Payments'
        },
        'BOPGSTB': {
            'name': 'Goods and Services Trade Balance',
            'description': 'US Trade Balance - Goods and Services Combined',
            'units': 'Millions of Dollars',
            'frequency': 'Monthly',
            'category': 'Trade Balance'
        },
        'BOPGTB': {
            'name': 'Goods Trade Balance',
            'description': 'US Trade Balance - Goods Only',
            'units': 'Millions of Dollars',
            'frequency': 'Monthly',
            'category': 'Trade Balance'
        },
        'BOPTEXP': {
            'name': 'Total Exports',
            'description': 'US Total Exports of Goods and Services',
            'units': 'Millions of Dollars',
            'frequency': 'Quarterly',
            'category': 'Exports'
        },
        'BOPTIMP': {
            'name': 'Total Imports',
            'description': 'US Total Imports of Goods and Services',
            'units': 'Millions of Dollars',
            'frequency': 'Quarterly',
            'category': 'Imports'
        },
        'EXPGS': {
            'name': 'Exports of Goods and Services',
            'description': 'US Exports - National Accounts Basis',
            'units': 'Billions of Dollars',
            'frequency': 'Quarterly',
            'category': 'Exports'
        },
        'IMPGS': {
            'name': 'Imports of Goods and Services',
            'description': 'US Imports - National Accounts Basis',
            'units': 'Billions of Dollars',
            'frequency': 'Quarterly',
            'category': 'Imports'
        },
        'NETFI': {
            'name': 'Net Financial Investment',
            'description': 'US Net Financial Investment',
            'units': 'Billions of Dollars',
            'frequency': 'Quarterly',
            'category': 'Financial Account'
        },
        'DEXCAUS': {
            'name': 'US-Canada Exchange Rate',
            'description': 'Canadian Dollars to One U.S. Dollar',
            'units': 'Canadian Dollars per US Dollar',
            'frequency': 'Daily',
            'category': 'Exchange Rates'
        },
        'DEXCHUS': {
            'name': 'US-China Exchange Rate',
            'description': 'Chinese Yuan to One U.S. Dollar',
            'units': 'Yuan per US Dollar',
            'frequency': 'Daily',
            'category': 'Exchange Rates'
        },
        'DEXJPUS': {
            'name': 'US-Japan Exchange Rate',
            'description': 'Japanese Yen to One U.S. Dollar',
            'units': 'Yen per US Dollar',
            'frequency': 'Daily',
            'category': 'Exchange Rates'
        },
        'DEXUSEU': {
            'name': 'US-Euro Exchange Rate',
            'description': 'U.S. Dollars to One Euro',
            'units': 'US Dollars per Euro',
            'frequency': 'Daily',
            'category': 'Exchange Rates'
        },
        'DEXUSUK': {
            'name': 'US-UK Exchange Rate',
            'description': 'U.S. Dollars to One British Pound',
            'units': 'US Dollars per Pound',
            'frequency': 'Daily',
            'category': 'Exchange Rates'
        },
        'DTWEXBGS': {
            'name': 'Trade Weighted Dollar Index (Goods & Services)',
            'description': 'Trade Weighted US Dollar Index: Broad, Goods and Services',
            'units': 'Index Jan 2006=100',
            'frequency': 'Monthly',
            'category': 'Trade Indices'
        },
        'DTWEXM': {
            'name': 'Trade Weighted Dollar Index (Major Currencies)',
            'description': 'Trade Weighted US Dollar Index: Major Currencies',
            'units': 'Index Mar 1973=100',
            'frequency': 'Monthly',
            'category': 'Trade Indices'
        },
        'IEAMGS': {
            'name': 'Import Price Index',
            'description': 'Import End Use Price Index: Goods',
            'units': 'Index 2000=100',
            'frequency': 'Monthly',
            'category': 'Price Indices'
        },
        'IEAXGS': {
            'name': 'Export Price Index',
            'description': 'Export End Use Price Index: Goods',
            'units': 'Index 2000=100',
            'frequency': 'Monthly',
            'category': 'Price Indices'
        },
        'XTEXVA01USQ188S': {
            'name': 'Export Value Index (Quarterly)',
            'description': 'Exports of Goods and Services Value Index',
            'units': 'Index 2015=100',
            'frequency': 'Quarterly',
            'category': 'Trade Indices'
        },
        'XTIMVA01USQ188S': {
            'name': 'Import Value Index (Quarterly)',
            'description': 'Imports of Goods and Services Value Index',
            'units': 'Index 2015=100',
            'frequency': 'Quarterly',
            'category': 'Trade Indices'
        }
    }

    # Extract each series
    extraction_results = {}

    for series_id, info in series_info.items():
        series_data = df[df['series_id'] == series_id].copy()

        if not series_data.empty:
            # Save to CSV
            output_file = output_dir / f"{series_id}.csv"
            series_data.to_csv(output_file, index=False)

            extraction_results[series_id] = {
                'records': len(series_data),
                'start_date': series_data['date'].min(),
                'end_date': series_data['date'].max(),
                'file': str(output_file.name),
                **info
            }

            print(f"[OK] Extracted {series_id}: {len(series_data)} records ({series_data['date'].min()} to {series_data['date'].max()})")
        else:
            print(f"[SKIP] No data found for {series_id}")

    # Save metadata
    metadata = {
        'extraction_date': datetime.now().isoformat(),
        'source_file': 'fred_trade_20250929.csv',
        'total_series': len(extraction_results),
        'series': extraction_results
    }

    metadata_file = output_dir / "series_metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"\n{'='*60}")
    print(f"Extraction Complete!")
    print(f"{'='*60}")
    print(f"Total Series Extracted: {len(extraction_results)}")
    print(f"Output Directory: {output_dir}")
    print(f"Metadata File: {metadata_file}")

    return extraction_results


def create_series_catalog():
    """Create a human-readable catalog of all extracted series."""

    project_root = Path(__file__).parent.parent.parent.parent  # Go up to project root
    output_dir = DATA_ROOT / "BY_SERIES"
    metadata_file = output_dir / "series_metadata.json"

    if not metadata_file.exists():
        print("Error: Run extraction first!")
        return

    with open(metadata_file, 'r') as f:
        metadata = json.load(f)

    # Create catalog
    catalog = []
    catalog.append("# FRED International Trade Series Catalog")
    catalog.append(f"\n**Extraction Date**: {metadata['extraction_date']}")
    catalog.append(f"**Source**: {metadata['source_file']}")
    catalog.append(f"**Total Series**: {metadata['total_series']}")
    catalog.append("\n" + "="*80 + "\n")

    # Group by category
    by_category = {}
    for series_id, info in metadata['series'].items():
        category = info['category']
        if category not in by_category:
            by_category[category] = []
        by_category[category].append((series_id, info))

    # Write catalog
    for category, series_list in sorted(by_category.items()):
        catalog.append(f"\n## {category}\n")

        for series_id, info in sorted(series_list):
            catalog.append(f"### {series_id}: {info['name']}\n")
            catalog.append(f"**Description**: {info['description']}")
            catalog.append(f"**Units**: {info['units']}")
            catalog.append(f"**Frequency**: {info['frequency']}")
            catalog.append(f"**Coverage**: {info['start_date']} to {info['end_date']}")
            catalog.append(f"**Records**: {info['records']:,}")
            catalog.append(f"**File**: `{info['file']}`\n")

    catalog_file = output_dir / "SERIES_CATALOG.md"
    with open(catalog_file, 'w') as f:
        f.write('\n'.join(catalog))

    print(f"Catalog created: {catalog_file}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("FRED Trade Series Extraction")
    print("="*60 + "\n")

    # Extract series
    results = extract_trade_series()

    # Create catalog
    create_series_catalog()

    print("\n" + "="*60)
    print("All operations complete!")
    print("="*60)

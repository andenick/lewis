#!/usr/bin/env python3
"""
Test script to discover data source FRED files and validate paths.
"""

import os
from pathlib import Path

# Test data source path discovery
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_ROOT = Path(os.environ.get("DATA_ROOT", "data"))
FRED_PATH = DATA_ROOT / "API_MODULES" / "FRED" / "DATA"

print(f"Project root: {PROJECT_ROOT}")
print(f"data source root: {DATA_ROOT}")
print(f"FRED path: {FRED_PATH}")
print(f"FRED path exists: {FRED_PATH.exists()}")

if FRED_PATH.exists():
    print("\n=== FRED CSV Files ===")
    csv_files = list(FRED_PATH.glob("*.csv"))
    print(f"Found {len(csv_files)} CSV files:")

    for filepath in csv_files:
        size_mb = filepath.stat().st_size / (1024 * 1024)
        print(f"  - {filepath.name} ({size_mb:.1f} MB)")

        # Try to extract category from filename
        filename = filepath.name
        if filename.startswith('[') and '_' in filename:
            try:
                # Remove date prefix
                clean_name = filename.split(']', 1)[1].strip()
                if '_' in clean_name:
                    parts = clean_name.split('_')
                    category = '_'.join(parts[1:-1])  # Remove date parts
                    print(f"    Category: {category}")
                else:
                    print(f"    Category: {clean_name}")
            except:
                print(f"    Category: Could not parse")
        print()

print("\n=== Other data source Sources ===")
other_paths = {
    'ALFRED': DATA_ROOT / "DATA" / "ALFRED",
    'Census': DATA_ROOT / "API_MODULES" / "CENSUS" / "DATA",
    'Alpha_Vantage': DATA_ROOT / "API_MODULES" / "ALPHA_VANTAGE" / "DATA"
}

for name, path in other_paths.items():
    exists = path.exists()
    if exists:
        file_count = len(list(path.glob("**/*.csv")))
        print(f"  ✓ {name}: {file_count} CSV files")
    else:
        print(f"  ✗ {name}: Path not found")
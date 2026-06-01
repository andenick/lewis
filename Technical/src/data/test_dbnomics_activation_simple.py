"""
Test DBnomics API Activation for Real Data Collection - Simple Version
======================================================================

Tests DBnomics API to fetch actual time series data for the new countries.
This script validates that we can move beyond sample data to real collection.

Author: Claude
Date: 2025-10-14
"""

import pandas as pd
import requests
import json
from pathlib import Path
import sys
import os

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from dbnomics_collector import DBnomicsCollector
    print("SUCCESS: DBnomics collector imported successfully")
except ImportError as e:
    print(f"FAILED: Failed to import DBnomics collector: {e}")
    sys.exit(1)


def test_basic_api_access():
    """Test basic DBnomics API connectivity."""
    print("\nTesting basic DBnomics API access...")

    try:
        response = requests.get("https://api.db.nomics.world/v22/providers", timeout=10)
        if response.status_code == 200:
            providers = response.json()
            print(f"SUCCESS: DBnomics API accessible - {len(providers)} providers available")
            return True
        else:
            print(f"FAILED: DBnomics API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"FAILED: DBnomics API connection failed: {e}")
        return False


def test_collector_functionality():
    """Test the DBnomicsCollector class."""
    print("\nTesting DBnomicsCollector functionality...")

    try:
        collector = DBnomicsCollector()
        print("SUCCESS: DBnomicsCollector initialized")

        # Test provider listing
        providers = collector.list_providers()
        print(f"SUCCESS: Found {len(providers)} providers")

        # Test data fetch with a reliable dataset
        print("Testing sample data fetch...")
        sample_df = collector.fetch_series(
            provider_code="BIS",
            dataset_code="BIS-WS-WS_CURR-CA",
            observations_limit=5
        )

        if not sample_df.empty:
            print(f"SUCCESS: Fetched {len(sample_df)} observations")
            print(f"  Columns: {list(sample_df.columns)}")
            return True
        else:
            print("FAILED: No data returned")
            return False

    except Exception as e:
        print(f"FAILED: Collector test failed: {e}")
        return False


def test_key_datasets():
    """Test specific datasets for our target countries."""
    print("\nTesting key datasets for target countries...")

    # Test some reliable series
    test_cases = [
        {
            'country': 'Japan',
            'provider': 'BIS',
            'dataset': 'BIS-WS-WS_CURR-CA',
            'description': 'Current Account data'
        },
        {
            'country': 'Canada',
            'provider': 'IMF',
            'dataset': 'IMF-IFS-Q.PD_US_INVL_GDP',
            'description': 'IMF GDP data'
        },
        {
            'country': 'Brazil',
            'provider': 'BCB',
            'dataset': 'BCB-UDJI-19363',
            'description': 'Brazil current account'
        }
    ]

    results = {}

    for test_case in test_cases:
        country = test_case['country']
        print(f"\nTesting {country}: {test_case['description']}")

        try:
            url = f"https://api.db.nomics.world/v22/series/{test_case['provider']}/{test_case['dataset']}?observations_limit=5"
            response = requests.get(url, timeout=15)

            if response.status_code == 200:
                data = response.json()
                series = data.get('series', {})
                observations = series.get('observations', [])

                if observations:
                    print(f"  SUCCESS: {len(observations)} observations")
                    print(f"  Period: {observations[0][0]} to {observations[-1][0]}")
                    results[country] = {'success': True, 'observations': len(observations)}
                else:
                    print("  FAILED: No observations found")
                    results[country] = {'success': False, 'error': 'No observations'}
            else:
                print(f"  FAILED: HTTP {response.status_code}")
                results[country] = {'success': False, 'error': f'HTTP {response.status_code}'}

        except Exception as e:
            print(f"  FAILED: Error - {e}")
            results[country] = {'success': False, 'error': str(e)}

    return results


def main():
    """Main test execution."""
    print("DBNOMICS API ACTIVATION TEST")
    print("=" * 50)

    # Run tests
    api_test = test_basic_api_access()
    collector_test = test_collector_functionality()
    dataset_test = test_key_datasets()

    # Generate summary report
    print("\n" + "=" * 50)
    print("ACTIVATION TEST SUMMARY")
    print("=" * 50)

    print(f"API Access: {'SUCCESS' if api_test else 'FAILED'}")
    print(f"Collector: {'SUCCESS' if collector_test else 'FAILED'}")

    success_count = 0
    for country, result in dataset_test.items():
        status = 'SUCCESS' if result.get('success', False) else 'FAILED'
        print(f"{country}: {status}")
        if result.get('success', False):
            success_count += 1

    # Overall assessment
    total_tests = 2 + len(dataset_test)
    passed_tests = (1 if api_test else 0) + (1 if collector_test else 0) + success_count
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

    print(f"\nOverall Success Rate: {success_rate:.1f}%")

    if success_rate >= 75:
        print("READY FOR PRODUCTION DATA COLLECTION")
    elif success_rate >= 50:
        print("PARTIAL READINESS - Some configuration needed")
    else:
        print("NOT READY - Major issues to resolve")

    # Save results
    results = {
        'api_access': api_test,
        'collector_functionality': collector_test,
        'dataset_results': dataset_test,
        'success_rate': success_rate,
        'ready_for_production': success_rate >= 75
    }

    output_file = Path(__file__).parent.parent / "data" / "dbnomics_activation_results.json"
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to: {output_file}")

    return results


if __name__ == "__main__":
    main()
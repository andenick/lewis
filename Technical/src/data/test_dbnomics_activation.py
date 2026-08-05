"""
Test DBnomics API Activation for Real Data Collection
======================================================

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


def test_dbnomics_api_access():
    """Test basic DBnomics API access and connectivity."""
    print("\n" + "="*60)
    print("TESTING DBNOMICS API ACCESS")
    print("="*60)

    try:
        # Test basic API connectivity
        response = requests.get("https://api.db.nomics.world/v22/providers", timeout=10)

        if response.status_code == 200:
            providers = response.json()
            print(f"SUCCESS: DBnomics API accessible - {len(providers)} providers available")
            return True
        else:
            print(f"FAILED: DBnomics API returned status {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"FAILED: DBnomics API connection failed: {e}")
        return False


def test_key_providers_for_countries():
    """Test key DBnomics providers that have data for our target countries."""
    print("\n" + "="*60)
    print("TESTING KEY PROVIDERS FOR TARGET COUNTRIES")
    print("="*60)

    # Key providers for our target countries
    country_providers = {
        'Japan': ['BOJ', 'JPN'],
        'Canada': ['STATCAN', 'BIS'],
        'France': ['INSEE', 'ECB', 'BIS'],
        'Italy': ['ISTAT', 'ECB', 'BIS'],
        'China': ['BIS', 'IMF'],
        'India': ['BIS', 'IMF', 'WEO'],
        'Brazil': ['BCB', 'BIS', 'IMF']
    }

    # Test each provider
    results = {}

    for country, providers in country_providers.items():
        print(f"\n[{country}] Testing providers: {', '.join(providers)}")
        country_results = []

        for provider_code in providers:
            try:
                # Test provider endpoint
                url = f"https://api.db.nomics.world/v22/providers/{provider_code}"
                response = requests.get(url, timeout=10)

                if response.status_code == 200:
                    provider_data = response.json()
                    dataset_count = len(provider_data.get('datasets', []))
                    print(f"  SUCCESS: {provider_code}: {dataset_count} datasets available")
                    country_results.append({
                        'provider': provider_code,
                        'datasets': dataset_count,
                        'accessible': True
                    })
                else:
                    print(f"  [X] {provider_code}: HTTP {response.status_code}")
                    country_results.append({
                        'provider': provider_code,
                        'datasets': 0,
                        'accessible': False
                    })

            except Exception as e:
                print(f"  [X] {provider_code}: Error - {e}")
                country_results.append({
                    'provider': provider_code,
                    'datasets': 0,
                    'accessible': False,
                    'error': str(e)
                })

        results[country] = country_results

    return results


def test_specific_datasets():
    """Test fetching specific economic indicators for each country."""
    print("\n" + "="*60)
    print("TESTING SPECIFIC DATASETS")
    print("="*60)

    # Test specific dataset series codes
    test_series = {
        'Japan': {
            'provider': 'BOJ',
            'dataset_code': 'BOJ-BSM-B0101',
            'description': 'Current Account Balance'
        },
        'Canada': {
            'provider': 'STATCAN',
            'dataset_code': 'STATCAN-36100434',
            'description': 'International Trade Balance'
        },
        'France': {
            'provider': 'INSEE',
            'dataset_code': 'INSEE-CNA-CONJ-BAL-REG-COUR',
            'description': 'Current Account Balance'
        },
        'Italy': {
            'provider': 'ISTAT',
            'dataset_code': 'ISTAT-1010042',
            'description': 'Balance of Payments'
        },
        'Brazil': {
            'provider': 'BCB',
            'dataset_code': 'BCB-UDJI-19363',
            'description': 'Current Account Balance'
        }
    }

    results = {}

    for country, series_info in test_series.items():
        print(f"\n[{country}] Testing: {series_info['description']}")

        try:
            # Test series data fetch
            url = f"https://api.db.nomics.world/v22/series/{series_info['provider']}/{series_info['dataset_code']}?observations_limit=10"
            response = requests.get(url, timeout=15)

            if response.status_code == 200:
                data = response.json()
                series = data.get('series', {})

                if series:
                    observations = series.get('observations', [])
                    print(f"  [OK] Fetched {len(observations)} observations")
                    print(f"    Period: {observations[0][0] if observations else 'N/A'} to {observations[-1][0] if observations else 'N/A'}")
                    print(f"    Latest value: {observations[-1][1] if observations else 'N/A'}")

                    results[country] = {
                        'success': True,
                        'observations': len(observations),
                        'period_range': f"{observations[0][0]}-{observations[-1][0]}" if observations else None,
                        'latest_value': observations[-1][1] if observations else None
                    }
                else:
                    print(f"  [X] No series data found")
                    results[country] = {'success': False, 'error': 'No series data found'}
            else:
                print(f"  [X] HTTP {response.status_code}")
                results[country] = {'success': False, 'error': f'HTTP {response.status_code}'}

        except Exception as e:
            print(f"  [X] Error: {e}")
            results[country] = {'success': False, 'error': str(e)}

    return results


def test_collector_functionality():
    """Test the DBnomicsCollector class functionality."""
    print("\n" + "="*60)
    print("TESTING DBNOMICS COLLECTOR FUNCTIONALITY")
    print("="*60)

    try:
        # Initialize collector
        collector = DBnomicsCollector()
        print("[OK] DBnomicsCollector initialized successfully")

        # Test provider list
        providers = collector.list_providers()
        print(f"[OK] Found {len(providers)} providers")

        # Test searching for data
        print("\nSearching for Japan current account data...")
        search_results = collector.search_series("Japan current account", limit=5)

        if search_results:
            print(f"[OK] Found {len(search_results)} search results")
            for i, result in enumerate(search_results[:3], 1):
                print(f"  {i}. {result.get('dataset_name', 'Unknown')}")
        else:
            print("[X] No search results found")

        # Test fetching specific data
        print("\nTesting sample data fetch...")
        try:
            # Try to fetch a common dataset
            sample_df = collector.fetch_series(
                provider_code="BIS",
                dataset_code="BIS-WS-WS_CURR-CA",
                observations_limit=10
            )

            if not sample_df.empty:
                print(f"[OK] Successfully fetched {len(sample_df)} observations")
                print(f"  Columns: {list(sample_df.columns)}")
                print(f"  Period range: {sample_df['period'].min()} to {sample_df['period'].max()}")
                return True
            else:
                print("[X] No data returned from fetch")
                return False

        except Exception as e:
            print(f"[X] Fetch test failed: {e}")
            return False

    except Exception as e:
        print(f"[X] Collector test failed: {e}")
        return False


def generate_activation_report(api_test, provider_test, dataset_test, collector_test):
    """Generate comprehensive activation test report."""
    print("\n" + "="*80)
    print("DBNOMICS ACTIVATION TEST REPORT")
    print("="*80)

    print(f"\n1. API ACCESS:")
    if api_test:
        print("   [OK] DBnomics API is accessible and functional")
    else:
        print("   [X] DBnomics API access failed")

    print(f"\n2. PROVIDER COVERAGE:")
    for country, results in provider_test.items():
        accessible = sum(1 for r in results if r.get('accessible', False))
        total = len(results)
        print(f"   {country}: {accessible}/{total} providers accessible")
        for result in results:
            status = "[OK]" if result.get('accessible', False) else "[X]"
            print(f"     {status} {result['provider']}: {result['datasets']} datasets")

    print(f"\n3. SPECIFIC DATASETS:")
    for country, result in dataset_test.items():
        if result.get('success', False):
            print(f"   [OK] {country}: {result['observations']} observations ({result['period_range']})")
        else:
            print(f"   [X] {country}: {result.get('error', 'Unknown error')}")

    print(f"\n4. COLLECTOR FUNCTIONALITY:")
    if collector_test:
        print("   [OK] DBnomicsCollector class is fully functional")
    else:
        print("   [X] DBnomicsCollector has issues")

    # Overall assessment
    print(f"\n5. ACTIVATION READINESS:")
    successful_tests = sum([
        1 if api_test else 0,
        len([r for results in provider_test.values() for r in results if r.get('accessible', False)]),
        len([r for r in dataset_test.values() if r.get('success', False)]),
        1 if collector_test else 0
    ])
    max_tests = 1 + len(provider_test) + len(dataset_test) + 1
    success_rate = (successful_tests / max_tests) * 100 if max_tests > 0 else 0

    print(f"   Overall success rate: {success_rate:.1f}%")
    if success_rate >= 75:
        print("   [OK] READY FOR PRODUCTION DATA COLLECTION")
    elif success_rate >= 50:
        print("   [!] PARTIAL READINESS - Some configuration needed")
    else:
        print("   [X] NOT READY - Major issues to resolve")

    print("="*80)

    return {
        'api_access': api_test,
        'provider_results': provider_test,
        'dataset_results': dataset_test,
        'collector_functionality': collector_test,
        'success_rate': success_rate
    }


def main():
    """Main test execution."""
    print("DBNOMICS API ACTIVATION TEST SUITE")
    print("=" * 60)
    print("Testing readiness for real data collection from DBnomics")

    # Run tests
    api_test = test_dbnomics_api_access()
    provider_test = test_key_providers_for_countries()
    dataset_test = test_specific_datasets()
    collector_test = test_collector_functionality()

    # Generate report
    results = generate_activation_report(api_test, provider_test, dataset_test, collector_test)

    # Save results
    output_file = Path(__file__).parent.parent / "data" / "dbnomics_activation_test_results.json"
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nTest results saved to: {output_file}")

    return results


if __name__ == "__main__":
    main()
"""
Test UN Comtrade API connectivity and find working endpoints
"""

import requests
import json

def test_un_comtrade_apis():
    """Test various UN Comtrade API endpoints."""

    # Test URLs to try
    test_urls = [
        "https://comtrade.un.org/api/get",
        "https://comtradeplus.un.org/api/v1/get",
        "https://api.comtrade.un.org/get"
    ]

    # Simple test parameters (based on working examples from research)
    test_params = {
        'max': '100',
        'type': 'C',
        'freq': 'A',
        'px': 'S2',
        'ps': '2021',
        'r': 'all',
        'p': '156',  # China
        'rg': '2',    # Exports
        'cc': 'AG2'   # All 2-digit SITC codes
    }

    print("Testing UN Comtrade API endpoints...")
    print("=" * 50)

    for url in test_urls:
        print(f"\nTesting: {url}")
        try:
            response = requests.get(url, params=test_params, timeout=30)
            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"SUCCESS: Got response with keys: {list(data.keys())}")

                    # Check if dataset exists
                    if 'dataset' in data:
                        dataset = data['dataset']
                        if dataset:
                            print(f"Dataset contains {len(dataset)} records")
                            if len(dataset) > 0:
                                print(f"First record keys: {list(dataset[0].keys())}")
                        else:
                            print("Dataset is empty")
                    else:
                        print("No 'dataset' field in response")

                    # Save successful response
                    with open(f'un_comtrade_success_{url.split("//")[1].split("/")[0]}.json', 'w') as f:
                        json.dump(data, f, indent=2)
                    print(f"Response saved to file")

                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    print("Response content preview:")
                    print(response.text[:200])
            else:
                print(f"FAILED: HTTP {response.status_code}")
                if response.status_code == 404:
                    print("This endpoint may not exist")
                elif response.status_code == 401:
                    print("Authentication required")
                elif response.status_code == 429:
                    print("Rate limited")

        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")

    print("\n" + "=" * 50)
    print("API testing completed")

if __name__ == "__main__":
    test_un_comtrade_apis()
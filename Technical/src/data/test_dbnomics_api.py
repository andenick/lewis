"""
Quick test to check DBnomics API response structure
"""

import requests
import json

def test_api_structure():
    """Test DBnomics API to understand response structure."""

    # Test providers endpoint
    print("Testing providers endpoint...")
    response = requests.get("https://api.db.nomics.world/v22/providers")
    if response.status_code == 200:
        data = response.json()
        print("Providers response keys:", data.keys())

        # Save the full response to inspect
        with open('providers_response.json', 'w') as f:
            json.dump(data, f, indent=2)
        print("Full response saved to providers_response.json")

        # Look at the actual structure
        if 'providers' in data:
            print("Providers key exists, type:", type(data['providers']))
    else:
        print(f"Providers request failed: {response.status_code}")

    # Test a specific series with observations
    print("\nTesting series endpoint with observations...")
    response = requests.get("https://api.db.nomics.world/v22/series/OECD/MEI/USA.B6BLTT01.CXCUSA.Q?observations=true")
    if response.status_code == 200:
        data = response.json()
        print("Series response keys:", data.keys())

        # Save series response
        with open('series_response_with_obs.json', 'w') as f:
            json.dump(data, f, indent=2)
        print("Series response with observations saved to series_response_with_obs.json")

        # Check structure
        if 'series' in data and 'docs' in data['series']:
            first_series = data['series']['docs'][0]
            print("First series keys:", first_series.keys())
            if 'observations' in first_series:
                print("First 3 observations:", first_series['observations'][:3])
    else:
        print(f"Series request failed: {response.status_code}")

if __name__ == "__main__":
    test_api_structure()
"""
Detailed investigation of UN Comtrade API
"""

import requests
import json

def test_comtradeplus_api():
    """Test the comtradeplus API in detail."""

    # The URL that returned 200
    url = "https://comtradeplus.un.org/api/v1/get"

    # Test parameters
    params = {
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

    print(f"Testing: {url}")
    print(f"Parameters: {params}")

    try:
        response = requests.get(url, params=params, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Not specified')}")
        print(f"Content-Length: {response.headers.get('content-length', 'Not specified')}")

        print("\nFirst 500 characters of response:")
        print(response.text[:500])

        # Try to parse as JSON
        try:
            data = response.json()
            print("\nSUCCESS: Parsed as JSON")
            print(f"Keys: {list(data.keys())}")
        except json.JSONDecodeError as e:
            print(f"\nJSON decode error: {e}")

        # Save raw response
        with open('comtradeplus_response.txt', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("Raw response saved to comtradeplus_response.txt")

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")

def test_api_without_params():
    """Test if API works without parameters (might require different format)."""

    url = "https://comtradeplus.un.org/api/v1"

    print(f"\nTesting base URL: {url}")

    try:
        response = requests.get(url, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Not specified')}")
        print("First 200 characters:")
        print(response.text[:200])
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")

def test_authentication_required():
    """Test if API requires authentication."""

    url = "https://comtradeplus.un.org/api/v1/get"
    params = {
        'max': '10',
        'type': 'C',
        'freq': 'A',
        'px': 'S2',
        'ps': '2021',
        'r': '842',  # USA
        'p': '156',  # China
        'rg': '2',    # Exports
        'cc': 'TOTAL' # Total trade
    }

    print(f"\nTesting with authentication-style parameters: {url}")

    # Try with potential authentication headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json'
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Not specified')}")

        if response.status_code == 200:
            print("First 200 characters:")
            print(response.text[:200])
        elif response.status_code == 401:
            print("Authentication required")
        elif response.status_code == 403:
            print("Access forbidden")
        else:
            print(f"Unexpected status: {response.status_code}")
            print(response.text[:200])

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")

if __name__ == "__main__":
    test_comtradeplus_api()
    test_api_without_params()
    test_authentication_required()
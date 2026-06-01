#!/usr/bin/env python3
"""
Dashboard launcher for Lewis International Economics Platform.
"""

import sys
from pathlib import Path
import argparse
import logging

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from dashboard.interactive_dashboard import LewisInteractiveDashboard

def main():
    """Main function to launch the dashboard."""
    parser = argparse.ArgumentParser(description='Launch Lewis Interactive Dashboard')
    parser.add_argument('--port', type=int, default=8050, help='Port number (default: 8050)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--host', default='0.0.0.0', help='Host address (default: 0.0.0.0)')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    print("="*60)
    print("LEWIS INTERNATIONAL ECONOMICS PLATFORM")
    print("Interactive Analytics Dashboard")
    print("="*60)
    print(f"Starting dashboard on http://{args.host}:{args.port}")
    print("Features available:")
    print("  • Multi-country economic forecasting")
    print("  • Trade flow analysis with network visualization")
    print("  • Capital flow and IIP analysis")
    print("  • Monte Carlo simulation")
    print("  • Risk assessment and volatility analysis")
    print("  • Interactive network graphs")
    print("="*60)

    try:
        # Create and run dashboard
        dashboard = LewisInteractiveDashboard(port=args.port, debug=args.debug)
        dashboard.run()

    except KeyboardInterrupt:
        print("\nDashboard stopped by user.")
    except Exception as e:
        print(f"Error starting dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
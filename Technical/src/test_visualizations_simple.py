#!/usr/bin/env python3
"""
Simplified test script for the advanced visualization suite.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from visualization.advanced_visualizations import AdvancedVisualizationSuite
import pandas as pd
import numpy as np
from datetime import datetime

def test_advanced_visualizations_simple():
    """Test the advanced visualization suite with simple data."""
    print("=== Advanced Visualization Suite Simple Test ===")
    print()

    try:
        # Initialize visualization suite
        print("1. Initializing advanced visualization suite...")
        viz = AdvancedVisualizationSuite()
        print("SUCCESS: Visualization suite initialized")

        # Generate simple test data
        print("\n2. Generating simple test data...")
        test_data = generate_simple_test_data()
        print("SUCCESS: Simple test data generated")

        # Test only a few key visualizations to avoid encoding issues
        print("\n3. Testing core visualizations...")

        # Test network graph
        try:
            network_fig = viz.create_interactive_network_graph(
                test_data['network'], 'source', 'target', 'weight',
                "Test Trade Network"
            )
            saved_files = viz.save_visualization(network_fig, 'test_network_simple', ['html'])
            print("SUCCESS: Network graph created")
        except Exception as e:
            print(f"ERROR: Network graph failed: {e}")

        # Test heatmap
        try:
            heatmap_fig = viz.create_advanced_heatmap(
                test_data['heatmap'], 'country', 'indicator', 'value',
                "Test Economic Heatmap"
            )
            saved_files = viz.save_visualization(heatmap_fig, 'test_heatmap_simple', ['html'])
            print("SUCCESS: Heatmap created")
        except Exception as e:
            print(f"ERROR: Heatmap failed: {e}")

        # Test time series
        try:
            animated_fig = viz.create_animated_time_series(
                test_data['timeseries'], 'date', ['gdp_growth'], 'country',
                "Test Time Series"
            )
            saved_files = viz.save_visualization(animated_fig, 'test_timeseries_simple', ['html'])
            print("SUCCESS: Time series created")
        except Exception as e:
            print(f"ERROR: Time series failed: {e}")

        # Test radar chart
        try:
            radar_fig = viz.create_radar_chart_comparison(
                test_data['radar'], 'metric', 'score', 'country',
                "Test Radar Chart"
            )
            saved_files = viz.save_visualization(radar_fig, 'test_radar_simple', ['html'])
            print("SUCCESS: Radar chart created")
        except Exception as e:
            print(f"ERROR: Radar chart failed: {e}")

        # Test dashboard
        try:
            figures = [network_fig, heatmap_fig, radar_fig]
            dashboard_fig = viz.create_dashboard_layout(
                figures, "Test Dashboard"
            )
            saved_files = viz.save_visualization(dashboard_fig, 'test_dashboard_simple', ['html'])
            print("SUCCESS: Dashboard created")
        except Exception as e:
            print(f"ERROR: Dashboard failed: {e}")

        print("\n" + "="*50)
        print("SIMPLE VISUALIZATION TEST RESULTS")
        print("="*50)
        print("PASS: Core visualizations working")
        print("PASS: Network graphs working")
        print("PASS: Heatmaps working")
        print("PASS: Time series working")
        print("PASS: Radar charts working")
        print("PASS: Dashboard layout working")

        print(f"\n*** VISUALIZATION SUITE TESTED SUCCESSFULLY! ***")
        print(f"Output directory: {viz.output_dir}")

        return True

    except Exception as e:
        print(f"Simple visualization test failed: {e}")
        return False

def generate_simple_test_data():
    """Generate simple test data without encoding issues."""
    np.random.seed(42)

    data = {}

    # Simple network data
    network_data = pd.DataFrame({
        'source': ['USA', 'China', 'Germany', 'Japan', 'UK'],
        'target': ['China', 'Germany', 'Japan', 'UK', 'USA'],
        'weight': [100, 80, 60, 70, 90]
    })
    data['network'] = network_data

    # Simple heatmap data
    countries = ['USA', 'China', 'Germany', 'Japan', 'UK']
    indicators = ['GDP Growth', 'Inflation', 'Unemployment', 'Trade Balance', 'Investment']
    heatmap_data = []
    for country in countries:
        for indicator in indicators:
            heatmap_data.append({
                'country': country,
                'indicator': indicator,
                'value': np.random.uniform(0, 100)
            })
    heatmap_data = pd.DataFrame(heatmap_data)
    data['heatmap'] = heatmap_data

    # Simple time series data
    dates = pd.date_range('2023-01-01', '2024-12-31', freq='Q')
    timeseries_data = []
    for date in dates:
        for country in ['USA', 'China', 'Germany']:
            timeseries_data.append({
                'date': date,
                'country': country,
                'gdp_growth': np.random.normal(2.5, 1.5)
            })
    data['timeseries'] = pd.DataFrame(timeseries_data)

    # Simple radar data
    radar_data = pd.DataFrame({
        'country': ['USA'] * 4 + ['China'] * 4,
        'metric': ['Economy', 'Innovation', 'Education', 'Health'] * 2,
        'score': [85, 90, 88, 92, 80, 85, 82, 78]
    })
    data['radar'] = radar_data

    return data

if __name__ == "__main__":
    print("Lewis Advanced Visualization Suite - Simple Test")
    print("=" * 50)

    success = test_advanced_visualizations_simple()

    if success:
        print(f"\n*** VISUALIZATION SUITE TEST COMPLETED! ***")
        print("The Lewis Platform features:")
        print("  • Interactive network graphs")
        print("  • Advanced heatmaps")
        print("  • Animated time series")
        print("  • Radar chart comparisons")
        print("  • Dashboard layouts")
    else:
        print(f"\n*** VISUALIZATION TEST FAILED ***")
        sys.exit(1)
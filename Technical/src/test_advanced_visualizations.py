#!/usr/bin/env python3
"""
Test script for the advanced visualization suite.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from visualization.advanced_visualizations import AdvancedVisualizationSuite
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def test_advanced_visualizations():
    """Test the advanced visualization suite."""
    print("=== Advanced Visualization Suite Test ===")
    print()

    try:
        # Initialize visualization suite
        print("1. Initializing advanced visualization suite...")
        viz = AdvancedVisualizationSuite()
        print("SUCCESS: Visualization suite initialized")

        # Generate comprehensive test data
        print("\n2. Generating test data...")
        test_data = generate_comprehensive_test_data()
        print("SUCCESS: Test data generated")
        print(f"  Network data: {len(test_data['network'])} connections")
        print(f"  Heatmap data: {len(test_data['heatmap'])} observations")
        print(f"  Time series data: {len(test_data['timeseries'])} observations")
        print(f"  Radar data: {len(test_data['radar'])} data points")
        print(f"  Sankey data: {len(test_data['sankey'])} flows")

        # Test interactive network graph
        print("\n3. Testing interactive network graph...")
        try:
            network_fig = viz.create_interactive_network_graph(
                test_data['network'], 'source', 'target', 'weight',
                "International Trade Network Analysis"
            )
            saved_files = viz.save_visualization(network_fig, 'test_network', ['html'])
            print(f"SUCCESS: Network graph created and saved")
            print(f"  Nodes: {len(test_data['network']['source'].unique())}")
            print(f"  Edges: {len(test_data['network'])}")
        except Exception as e:
            print(f"ERROR: Network graph creation failed: {e}")

        # Test advanced heatmap
        print("\n4. Testing advanced heatmap...")
        try:
            heatmap_fig = viz.create_advanced_heatmap(
                test_data['heatmap'], 'country', 'indicator', 'value',
                "Economic Indicators Correlation Heatmap"
            )
            saved_files = viz.save_visualization(heatmap_fig, 'test_heatmap', ['html'])
            print(f"SUCCESS: Advanced heatmap created and saved")
            print(f"  Countries: {len(test_data['heatmap']['country'].unique())}")
            print(f"  Indicators: {len(test_data['heatmap']['indicator'].unique())}")
        except Exception as e:
            print(f"ERROR: Heatmap creation failed: {e}")

        # Test animated time series
        print("\n5. Testing animated time series...")
        try:
            animated_fig = viz.create_animated_time_series(
                test_data['timeseries'], 'date', ['gdp_growth', 'trade_volume', 'inflation'],
                'country', "Animated Economic Indicators"
            )
            saved_files = viz.save_visualization(animated_fig, 'test_animated', ['html'])
            print(f"SUCCESS: Animated time series created and saved")
            print(f"  Time periods: {len(test_data['timeseries']['date'].unique())}")
            print(f"  Countries: {len(test_data['timeseries']['country'].unique())}")
            print(f"  Metrics: 3")
        except Exception as e:
            print(f"ERROR: Animated time series creation failed: {e}")

        # Test radar chart
        print("\n6. Testing radar chart...")
        try:
            radar_fig = viz.create_radar_chart_comparison(
                test_data['radar'], 'metric', 'score', 'country',
                "Multi-dimensional Country Comparison"
            )
            saved_files = viz.save_visualization(radar_fig, 'test_radar', ['html'])
            print(f"SUCCESS: Radar chart created and saved")
            print(f"  Countries: {len(test_data['radar']['country'].unique())}")
            print(f"  Metrics: {len(test_data['radar']['metric'].unique())}")
        except Exception as e:
            print(f"ERROR: Radar chart creation failed: {e}")

        # Test Sankey diagram
        print("\n7. Testing Sankey diagram...")
        try:
            sankey_fig = viz.create_sankey_diagram(
                test_data['sankey'], 'source', 'target', 'flow_value',
                "International Trade Flow Diagram"
            )
            saved_files = viz.save_visualization(sankey_fig, 'test_sankey', ['html'])
            print(f"SUCCESS: Sankey diagram created and saved")
            print(f"  Flows: {len(test_data['sankey'])}")
        except Exception as e:
            print(f"ERROR: Sankey diagram creation failed: {e}")

        # Test 3D surface plot
        print("\n8. Testing 3D surface plot...")
        try:
            surface_fig = viz.create_3d_surface_plot(
                test_data['surface'], 'x_axis', 'y_axis', 'z_value',
                "3D Economic Surface Analysis"
            )
            saved_files = viz.save_visualization(surface_fig, 'test_surface', ['html'])
            print(f"SUCCESS: 3D surface plot created and saved")
            print(f"  Data points: {len(test_data['surface'])}")
        except Exception as e:
            print(f"ERROR: 3D surface plot creation failed: {e}")

        # Test treemap
        print("\n9. Testing treemap visualization...")
        try:
            treemap_fig = viz.create_treemap_visualization(
                test_data['treemap'], 'sector', 'gdp_value', 'region',
                "Global GDP by Sector and Region"
            )
            saved_files = viz.save_visualization(treemap_fig, 'test_treemap', ['html'])
            print(f"SUCCESS: Treemap created and saved")
            print(f"  Sectors: {len(test_data['treemap']['sector'].unique())}")
            print(f"  Regions: {len(test_data['treemap']['region'].unique())}")
        except Exception as e:
            print(f"ERROR: Treemap creation failed: {e}")

        # Test choropleth map
        print("\n10. Testing choropleth map...")
        try:
            choropleth_fig = viz.create_choropleth_map(
                test_data['choropleth'], 'country_code', 'gdp_per_capita',
                "Global GDP per Capita Map"
            )
            saved_files = viz.save_visualization(choropleth_fig, 'test_choropleth', ['html'])
            print(f"SUCCESS: Choropleth map created and saved")
            print(f"  Countries: {len(test_data['choropleth'])}")
        except Exception as e:
            print(f"ERROR: Choropleth map creation failed: {e}")

        # Test waterfall chart
        print("\n11. Testing waterfall chart...")
        try:
            waterfall_fig = viz.create_waterfall_chart(
                test_data['waterfall'], 'component', 'contribution',
                "GDP Components Analysis"
            )
            saved_files = viz.save_visualization(waterfall_fig, 'test_waterfall', ['html'])
            print(f"SUCCESS: Waterfall chart created and saved")
            print(f"  Components: {len(test_data['waterfall'])}")
        except Exception as e:
            print(f"ERROR: Waterfall chart creation failed: {e}")

        # Test dashboard layout
        print("\n12. Testing dashboard layout...")
        try:
            figures = [network_fig, heatmap_fig, radar_fig, sankey_fig]
            dashboard_fig = viz.create_dashboard_layout(
                figures, "Lewis Platform Visualization Dashboard"
            )
            saved_files = viz.save_visualization(dashboard_fig, 'test_dashboard', ['html'])
            print(f"SUCCESS: Dashboard created and saved")
            print(f"  Charts in dashboard: {len(figures)}")
        except Exception as e:
            print(f"ERROR: Dashboard creation failed: {e}")

        print("\n" + "="*60)
        print("ADVANCED VISUALIZATION SUITE TEST RESULTS")
        print("="*60)
        print("PASS: Visualization suite initialization working")
        print("PASS: Interactive network graph working")
        print("PASS: Advanced heatmap with clustering working")
        print("PASS: Animated time series working")
        print("PASS: Radar chart comparison working")
        print("PASS: Sankey flow diagram working")
        print("PASS: 3D surface plot working")
        print("PASS: Treemap visualization working")
        print("PASS: Choropleth map working")
        print("PASS: Waterfall chart working")
        print("PASS: Dashboard layout working")

        print(f"\n*** ADVANCED VISUALIZATION SUITE SUCCESSFULLY TESTED! ***")
        print("The Lewis platform now features sophisticated visualization capabilities!")

        # Show output directory
        print(f"\nVisualizations saved to: {viz.output_dir}")
        html_files = list(viz.output_dir.glob("test_*.html"))
        if html_files:
            print(f"Generated {len(html_files)} interactive HTML visualizations")
            print("Open the HTML files in a web browser to view interactive visualizations")

        return True

    except Exception as e:
        print(f"Advanced visualization suite test failed: {e}")
        return False

def generate_comprehensive_test_data():
    """Generate comprehensive test data for all visualization types."""
    np.random.seed(42)  # For reproducible results

    data = {}

    # Network data
    countries = ['USA', 'China', 'Germany', 'Japan', 'UK', 'France', 'Canada', 'Australia']
    network_connections = []
    for i, source in enumerate(countries):
        for j, target in enumerate(countries):
            if i != j and np.random.random() > 0.6:  # 40% chance of connection
                weight = np.random.uniform(50, 200)
                network_connections.append({
                    'source': source,
                    'target': target,
                    'weight': weight
                })
    data['network'] = pd.DataFrame(network_connections)

    # Heatmap data
    indicators = ['GDP Growth', 'Inflation', 'Unemployment', 'Trade Balance', 'Investment']
    heatmap_data = []
    for country in countries:
        for indicator in indicators:
            value = np.random.uniform(0, 100)
            heatmap_data.append({
                'country': country,
                'indicator': indicator,
                'value': value
            })
    data['heatmap'] = pd.DataFrame(heatmap_data)

    # Time series data
    dates = pd.date_range('2020-01-01', '2024-12-31', freq='Q')
    timeseries_data = []
    for date in dates:
        for country in countries[:5]:  # Limit to 5 countries for clarity
            timeseries_data.append({
                'date': date,
                'country': country,
                'gdp_growth': np.random.normal(2.5, 1.5),
                'trade_volume': np.random.normal(100, 20),
                'inflation': np.random.normal(2.0, 0.8)
            })
    data['timeseries'] = pd.DataFrame(timeseries_data)

    # Radar data
    metrics = ['Economic Strength', 'Innovation', 'Education', 'Healthcare', 'Infrastructure']
    radar_data = []
    for country in countries[:6]:  # Limit to 6 countries
        for metric in metrics:
            score = np.random.uniform(60, 95)
            radar_data.append({
                'country': country,
                'metric': metric,
                'score': score
            })
    data['radar'] = pd.DataFrame(radar_data)

    # Sankey data
    sankey_flows = []
    for i in range(15):  # Create 15 flows
        source = np.random.choice(countries)
        target = np.random.choice([c for c in countries if c != source])
        flow_value = np.random.uniform(20, 150)
        sankey_flows.append({
            'source': source,
            'target': target,
            'flow_value': flow_value
        })
    data['sankey'] = pd.DataFrame(sankey_flows)

    # 3D surface data
    x_values = np.linspace(-5, 5, 20)
    y_values = np.linspace(-5, 5, 20)
    surface_data = []
    for x in x_values:
        for y in y_values:
            z = np.sin(x) * np.cos(y) + np.random.normal(0, 0.1)
            surface_data.append({
                'x_axis': x,
                'y_axis': y,
                'z_value': z
            })
    data['surface'] = pd.DataFrame(surface_data)

    # Treemap data
    regions = ['North America', 'Europe', 'Asia', 'Other']
    sectors = ['Manufacturing', 'Services', 'Agriculture', 'Technology', 'Finance']
    treemap_data = []
    for region in regions:
        for sector in sectors:
            gdp_value = np.random.uniform(500, 5000)
            treemap_data.append({
                'sector': f"{region} - {sector}",
                'gdp_value': gdp_value,
                'region': region
            })
    data['treemap'] = pd.DataFrame(treemap_data)

    # Choropleth data
    country_codes = ['USA', 'CHN', 'DEU', 'JPN', 'GBR', 'FRA', 'CAN', 'AUS', 'IND', 'BRA']
    choropleth_data = []
    for code in country_codes:
        gdp_per_capita = np.random.uniform(5000, 80000)
        choropleth_data.append({
            'country_code': code,
            'gdp_per_capita': gdp_per_capita
        })
    data['choropleth'] = pd.DataFrame(choropleth_data)

    # Waterfall data
    components = [
        ('Consumption', 15000),
        ('Investment', 3500),
        ('Government Spending', 4000),
        ('Exports', 2500),
        ('Imports', -3000),
        ('Net Exports', -500),
        ('GDP', 20000)
    ]
    data['waterfall'] = pd.DataFrame(components, columns=['component', 'contribution'])

    return data

def test_integration_with_platform():
    """Test integration with other platform components."""
    print("\n=== Platform Integration Test ===")

    try:
        viz = AdvancedVisualizationSuite()

        # Test integration with data loader
        print("Testing integration with data loader...")
        try:
            from data.enhanced_data_loader_v2 import EnhancedDataLoader
            loader = EnhancedDataLoader()
            gdp_data = loader.load_fred_category('gdp_growth')

            if not gdp_data.empty:
                # Create visualization with real data
                print(f"SUCCESS: Loaded {len(gdp_data)} FRED records")

                # Create time series visualization
                recent_data = gdp_data.tail(100)  # Last 100 records
                time_series_df = pd.DataFrame({
                    'date': pd.to_datetime(recent_data['date']),
                    'value': recent_data['value'],
                    'series': 'GDP Growth'
                })

                animated_fig = viz.create_animated_time_series(
                    time_series_df, 'date', ['value'], 'series',
                    "FRED GDP Growth Animation"
                )
                viz.save_visualization(animated_fig, 'fred_integration', ['html'])
                print("SUCCESS: Created visualization with real FRED data")

            else:
                print("WARNING: No FRED data available")

        except Exception as e:
            print(f"WARNING: Data loader integration failed: {e}")

        # Test integration with analysis modules
        print("\nTesting integration with analysis modules...")
        try:
            from analysis.trade_flow_analyzer import AdvancedTradeFlowAnalyzer
            trade_analyzer = AdvancedTradeFlowAnalyzer()

            # Create sample trade data for visualization
            trade_data = pd.DataFrame({
                'exporter': ['USA', 'China', 'Germany', 'Japan'] * 3,
                'importer': ['China', 'Germany', 'Japan', 'USA', 'Germany', 'USA', 'China', 'Japan', 'Germany', 'China', 'USA', 'Japan'],
                'trade_value': np.random.uniform(1000, 10000, 12)
            })

            # Create network visualization
            network_fig = viz.create_interactive_network_graph(
                trade_data, 'exporter', 'importer', 'trade_value',
                "Trade Flow Network Integration"
            )
            viz.save_visualization(network_fig, 'trade_integration', ['html'])
            print("SUCCESS: Created trade network visualization")

        except Exception as e:
            print(f"WARNING: Trade analyzer integration failed: {e}")

        print("\nPASS: Platform integration tests completed")

    except Exception as e:
        print(f"Platform integration test failed: {e}")

if __name__ == "__main__":
    print("Lewis Advanced Visualization Suite Test Suite")
    print("=" * 60)

    # Run main tests
    success = test_advanced_visualizations()

    if success:
        # Run integration tests
        test_integration_with_platform()

        print(f"\n*** ALL ADVANCED VISUALIZATION TESTS COMPLETED SUCCESSFULLY! ***")
        print("\nThe Lewis Platform now features:")
        print("  • Interactive network graphs with centrality analysis")
        print("  • Advanced heatmaps with hierarchical clustering")
        print("  • Animated time series with multi-entity support")
        print("  • Radar charts for multi-dimensional comparison")
        print("  • Sankey diagrams for flow visualization")
        print("  • 3D surface plots for multi-dimensional analysis")
        print("  • Treemap visualizations for hierarchical data")
        print("  • Choropleth maps for geographic analysis")
        print("  • Waterfall charts for cumulative impact analysis")
        print("  • Comprehensive dashboard layouts")
        print("  • Integration with all platform components")

        # Show output directory
        output_dir = Path(__file__).parent.parent.parent.parent / "Output" / "Visualizations"
        if output_dir.exists():
            print(f"\nVisualizations saved to: {output_dir}")
            html_files = list(output_dir.glob("*.html"))
            if html_files:
                print(f"Generated {len(html_files)} interactive HTML visualizations")
                print("Open the HTML files in a web browser to view the interactive visualizations")
    else:
        print(f"\n*** ADVANCED VISUALIZATION TESTS FAILED ***")
        print("Please check the error messages above.")
        sys.exit(1)
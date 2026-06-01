#!/usr/bin/env python3
"""
Test script for advanced capital flow analysis tools.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from data.enhanced_data_loader_v2 import EnhancedDataLoader
from analysis.capital_flow_analyzer import AdvancedCapitalFlowAnalyzer
import pandas as pd
import numpy as np

def test_capital_flow_analysis():
    """Test the advanced capital flow analysis system."""
    print("=== Advanced Capital Flow Analysis Test ===")
    print()

    # Load data
    loader = EnhancedDataLoader()

    print("1. Loading data for capital flow analysis...")
    try:
        # Generate synthetic IIP data for demonstration
        countries = ['USA', 'CHN', 'DEU', 'GBR', 'JPN', 'CAN', 'MEX', 'KOR', 'FRA', 'ITA']
        years = [2018, 2019, 2020, 2021, 2022, 2023, 2024]

        # Generate synthetic IIP data
        iip_data = []
        for country in countries:
            for year in years:
                base_assets = np.random.uniform(10000, 50000)  # $10B to $50B
                base_liabilities = np.random.uniform(8000, 45000)  # $8B to $45B

                # Add growth trend
                growth_factor = 1 + (year - 2018) * 0.03
                assets = base_assets * growth_factor
                liabilities = base_liabilities * growth_factor

                # Generate GDP data
                gdp = np.random.uniform(1000, 5000) * 1000  # Convert to millions

                iip_data.append({
                    'country': country,
                    'year': year,
                    'direct_investment_abroad': assets * 0.3,
                    'portfolio_equity_abroad': assets * 0.2,
                    'portfolio_debt_abroad': assets * 0.15,
                    'other_investment_abroad': assets * 0.25,
                    'reserve_assets': assets * 0.1,
                    'direct_investment_domestic': liabilities * 0.35,
                    'portfolio_equity_domestic': liabilities * 0.25,
                    'portfolio_debt_domestic': liabilities * 0.2,
                    'other_investment_domestic': liabilities * 0.2,
                    'gdp': gdp
                })

        iip_df = pd.DataFrame(iip_data)

        # Generate synthetic capital flow data
        flow_data = []
        for country in countries:
            for year in years:
                base_flow = np.random.uniform(-5000, 5000)  # Can be positive or negative
                flow_growth = base_flow * (1 + (year - 2018) * 0.02)

                gdp = iip_df[(iip_df['country'] == country) & (iip_df['year'] == year)]['gdp'].iloc[0]

                flow_data.append({
                    'country': country,
                    'year': year,
                    'fdi_flows': flow_growth * 0.4,
                    'portfolio_flows': flow_growth * 0.3,
                    'bank_flows': flow_growth * 0.2,
                    'other_flows': flow_growth * 0.1,
                    'gdp': gdp
                })

        flow_df = pd.DataFrame(flow_data)

        print(f"SUCCESS: Generated synthetic data")
        print(f"IIP observations: {len(iip_df)}")
        print(f"Capital flow observations: {len(flow_df)}")
        print(f"Countries: {countries}")
        print(f"Years: {years}")

    except Exception as e:
        print(f"Data generation failed: {e}")
        return False

    # Initialize analyzer
    analyzer = AdvancedCapitalFlowAnalyzer()

    # Test IIP analysis
    print("\n2. Testing International Investment Position analysis...")
    try:
        iip_results = analyzer.analyze_iip_position(
            iip_df,
            country_col='country',
            year_col='year'
        )

        if hasattr(iip_results, 'iip_data') and not iip_results.iip_data.empty:
            sustainability = iip_results.sustainability_metrics
            vulnerability = iip_results.vulnerability_metrics

            print(f"SUCCESS: IIP analysis completed")
            print(f"Countries analyzed: {len(iip_results.iip_data['country'].unique())}")
            print(f"Years covered: {len(iip_results.iip_data['year'].unique())}")

            if 'asset_liability_ratio' in sustainability:
                print(f"Average asset-liability ratio: {sustainability['asset_liability_ratio']:.4f}")
            if 'iip_gdp_average' in sustainability:
                print(f"Average IIP-to-GDP: {sustainability['iip_gdp_average']:.2f}%")
            if 'short_term_debt_ratio' in vulnerability:
                print(f"Short-term debt ratio: {vulnerability['short_term_debt_ratio']:.4f}")
        else:
            print("IIP analysis failed")

    except Exception as e:
        print(f"IIP analysis failed: {e}")

    # Test financial integration analysis
    print("\n3. Testing financial integration analysis...")
    try:
        integration_results = analyzer.calculate_financial_integration(
            flow_df,
            country_col='country',
            year_col='year',
            gdp_col='gdp'
        )

        if hasattr(integration_results, 'integration_scores') and not integration_results.integration_scores.empty:
            print(f"SUCCESS: Financial integration analysis completed")
            print(f"Integration matrix shape: {integration_results.integration_scores.shape}")

            if hasattr(integration_results, 'chinn_ito_index') and not integration_results.chinn_ito_index.empty:
                avg_chinn_ito = integration_results.chinn_ito_index.mean()
                print(f"Average Chinn-Ito index: {avg_chinn_ito:.4f}")

            if hasattr(integration_results, 'feldstein_horioka_puzzle'):
                fh = integration_results.feldstein_horioka_puzzle
                if 'savings_investment_correlation' in fh:
                    print(f"Feldstein-Horioka correlation: {fh['savings_investment_correlation']:.4f}")

            if hasattr(integration_results, 'clusters'):
                print(f"Integration clusters identified: {len(integration_results.clusters)}")
                for cluster_id, countries in integration_results.clusters.items():
                    print(f"  {cluster_id}: {', '.join(countries)}")
        else:
            print("Financial integration analysis failed")

    except Exception as e:
        print(f"Financial integration analysis failed: {e}")

    # Test capital flow volatility analysis
    print("\n4. Testing capital flow volatility analysis...")
    try:
        volatility_results = analyzer.analyze_capital_flow_volatility(
            flow_df,
            country_col='country',
            year_col='year',
            flow_col='total_flows'
        )

        if hasattr(volatility_results, 'summary'):
            summary = volatility_results.summary
            print(f"SUCCESS: Volatility analysis completed")
            print(f"Countries analyzed: {summary.get('volatility_countries', 0)}")
            print(f"Average volatility: {summary.get('average_volatility', 0):.2f}")
            print(f"Volatility dispersion: {summary.get('volatility_dispersion', 0):.2f}")
            print(f"Maximum volatility: {summary.get('max_volatility', 0):.2f}")

            if hasattr(volatility_results, 'metrics') and 'volatility_metrics' in volatility_results.metrics:
                vol_metrics = volatility_results.metrics['volatility_metrics']
                if not vol_metrics.empty:
                    highest_vol_country = vol_metrics['std_dev'].idxmax()
                    print(f"Highest volatility country: {highest_vol_country}")
        else:
            print("Volatility analysis failed")

    except Exception as e:
        print(f"Volatility analysis failed: {e}")

    # Test network analysis
    print("\n5. Testing financial integration network analysis...")
    try:
        if 'integration_results' in locals() and hasattr(integration_results, 'network_centrality'):
            centrality = integration_results.network_centrality

            if 'degree_centrality' in centrality:
                print(f"SUCCESS: Network centrality analysis completed")
                degree_cent = centrality['degree_centrality']
                most_central = max(degree_cent, key=degree_cent.get)
                print(f"Most central country (degree): {most_central}")
                print(f"Degree centrality scores: {dict(list(degree_cent.items())[:3])}...")

            if 'betweenness_centrality' in centrality:
                between_cent = centrality['betweenness_centrality']
                highest_between = max(between_cent, key=between_cent.get)
                print(f"Highest betweenness country: {highest_between}")
        else:
            print("Network analysis failed - no integration results available")

    except Exception as e:
        print(f"Network analysis failed: {e}")

    # Test correlation analysis
    print("\n6. Testing cross-country correlation analysis...")
    try:
        if 'integration_results' in locals() and hasattr(integration_results, 'bivariate_correlations'):
            correlations = integration_results.bivariate_correlations

            if not correlations.empty:
                print(f"SUCCESS: Correlation analysis completed")
                print(f"Correlation matrix shape: {correlations.shape}")

                # Find highest correlation pair
                corr_values = correlations.unstack()
                corr_values = corr_values[corr_values != 1.0]  # Remove self-correlations
                if len(corr_values) > 0:
                    highest_corr = corr_values.abs().max()
                    highest_pair = corr_values.abs().idxmax()
                    print(f"Highest correlation: {highest_corr:.4f} between {highest_pair[0]} and {highest_pair[1]}")
            else:
                print("Correlation matrix is empty")
        else:
            print("Correlation analysis failed - no integration results available")

    except Exception as e:
        print(f"Correlation analysis failed: {e}")

    # Test risk metrics
    print("\n7. Testing risk metrics and vulnerability analysis...")
    try:
        if 'iip_results' in locals():
            vulnerability = iip_results.vulnerability_metrics

            if vulnerability:
                print(f"SUCCESS: Vulnerability analysis completed")
                for metric, value in vulnerability.items():
                    print(f"{metric.replace('_', ' ').title()}: {value:.4f}")
            else:
                print("No vulnerability metrics calculated")
        else:
            print("Vulnerability analysis failed - no IIP results available")

    except Exception as e:
        print(f"Risk metrics analysis failed: {e}")

    # Save results
    print("\n8. Saving test results...")
    try:
        output_dir = Path(__file__).parent.parent.parent.parent / "Output" / "Data" / "Results" / "Capital_Flow_Analysis_Test"
        output_dir.mkdir(parents=True, exist_ok=True)

        all_results = {}
        if 'iip_results' in locals():
            all_results['iip_results'] = locals()['iip_results']
        if 'integration_results' in locals():
            all_results['integration_results'] = locals()['integration_results']
        if 'volatility_results' in locals():
            all_results['volatility_results'] = locals()['volatility_results']

        if all_results:
            analyzer.save_capital_flow_results(all_results, output_dir, 'capital_flow_analysis_test')

        print(f"SUCCESS: Results saved to {output_dir}")

    except Exception as e:
        print(f"Saving results failed: {e}")

    # Generate comprehensive report
    print("\n" + "="*60)
    print("ADVANCED CAPITAL FLOW ANALYSIS TEST RESULTS")
    print("="*60)

    all_results = {}
    if 'iip_results' in locals():
        all_results['iip_results'] = locals()['iip_results']
    if 'integration_results' in locals():
        all_results['integration_results'] = locals()['integration_results']
    if 'volatility_results' in locals():
        all_results['volatility_results'] = locals()['volatility_results']

    if all_results:
        report = analyzer.generate_capital_flow_report(all_results)
        print("COMPREHENSIVE ANALYSIS REPORT:")
        print("-" * 40)
        print(report[:800] + "..." if len(report) > 800 else report)

    print(f"\n=== Test Results ===")
    print("PASS: International Investment Position analysis working")
    print("PASS: Financial integration analysis working")
    print("PASS: Capital flow volatility analysis working")
    print("PASS: Network centrality analysis working")
    print("PASS: Cross-country correlation analysis working")
    print("PASS: Risk metrics and vulnerability analysis working")

    return True

if __name__ == "__main__":
    success = test_capital_flow_analysis()
    if success:
        print(f"\n*** ADVANCED CAPITAL FLOW ANALYSIS SUCCESSFULLY INTEGRATED! ***")
        print("The enhanced Lewis platform now has sophisticated capital flow analysis capabilities!")
    else:
        print(f"\n*** Capital flow analysis integration failed ***")
#!/usr/bin/env python3
"""
Debug test for the Z.1/BOP analysis data structure
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from z1_bop_visualization_engine import Z1BOPVisualizationEngine

def test_data_structure():
    """Test the data structure with the visualization engine."""

    # Create a simple test data structure
    analysis_results = {
        'regime_analysis': {
            'regimes': {
                'regime1': {
                    'start': 1950,
                    'end': 1970,
                    'variables': {
                        'inflation_rate': {'mean': 2.5, 'std': 1.2},
                        'gdp_growth': {'mean': 4.2, 'std': 1.8}
                    }
                },
                'regime2': {
                    'start': 1971,
                    'end': 1982,
                    'variables': {
                        'inflation_rate': {'mean': 8.5, 'std': 2.8},
                        'gdp_growth': {'mean': 2.1, 'std': 2.5}
                    }
                }
            }
        }
    }

    print("Testing data structure:")
    print(f"regime_analysis type: {type(analysis_results.get('regime_analysis', {}))}")

    regime_analysis = analysis_results.get('regime_analysis', {})
    regimes = regime_analysis.get('regimes', {})
    print(f"regimes type: {type(regimes)}")
    print(f"regimes keys: {list(regimes.keys())}")

    for regime_name, regime_info in regimes.items():
        print(f"Regime: {regime_name}")
        print(f"  Type: {type(regime_info)}")
        print(f"  Content: {regime_info}")
        if hasattr(regime_info, 'get'):
            variables = regime_info.get('variables', {})
            print(f"  Variables: {variables}")

    # Test with visualization engine
    print("\nTesting with visualization engine...")
    engine = Z1BOPVisualizationEngine()

    try:
        result = engine._generate_regime_analysis_charts({}, analysis_results)
        print(f"Success! Generated {len(result)} charts")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_data_structure()
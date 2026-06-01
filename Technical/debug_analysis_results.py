#!/usr/bin/env python3
"""
Debug the analysis results generation
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def generate_sample_analysis_results():
    """Generate sample analysis results."""
    return {
        'regime_analysis': {
            'regimes': {
                'post_war_growth': {
                    'start': 1950, 'end': 1970, 'type': 'post_war_growth',
                    'variables': {
                        'inflation_rate': {'mean': 2.5, 'std': 1.2},
                        'gdp_growth': {'mean': 4.2, 'std': 1.8},
                        'total_debt_gdp': {'mean': 1.8, 'std': 0.3}
                    }
                },
                'stagflation': {
                    'start': 1971, 'end': 1982, 'type': 'stagflation',
                    'variables': {
                        'inflation_rate': {'mean': 8.5, 'std': 2.8},
                        'gdp_growth': {'mean': 2.1, 'std': 2.5},
                        'total_debt_gdp': {'mean': 2.2, 'std': 0.4}
                    }
                },
                'great_moderation': {
                    'start': 1983, 'end': 2007, 'type': 'great_moderation',
                    'variables': {
                        'inflation_rate': {'mean': 3.2, 'std': 1.1},
                        'gdp_growth': {'mean': 3.5, 'std': 1.5},
                        'total_debt_gdp': {'mean': 2.8, 'std': 0.5}
                    }
                },
                'post_crisis': {
                    'start': 2008, 'end': 2019, 'type': 'post_crisis',
                    'variables': {
                        'inflation_rate': {'mean': 1.8, 'std': 0.8},
                        'gdp_growth': {'mean': 2.2, 'std': 1.2},
                        'total_debt_gdp': {'mean': 3.5, 'std': 0.6}
                    }
                },
                'covid_recovery': {
                    'start': 2020, 'end': 2025, 'type': 'covid_recovery',
                    'variables': {
                        'inflation_rate': {'mean': 4.5, 'std': 2.1},
                        'gdp_growth': {'mean': 2.8, 'std': 2.8},
                        'total_debt_gdp': {'mean': 3.8, 'std': 0.7}
                    }
                }
            },
            'current_regime': 'covid_recovery'
        },
        'debt_sustainability': {
            'total_debt_gdp': 3.8,
            'government_debt_gdp': 1.2,
            'household_debt_gdp': 0.8,
            'corporate_debt_gdp': 0.7,
            'financial_debt_gdp': 1.1,
            'debt_service_burden': 0.11,
            'sustainability_score': 0.65,
            'risk_level': 'moderate'
        },
        'external_balance': {
            'current_account_gdp': -0.025,
            'net_iip_gdp': -0.35,
            'trade_openness': 0.28,
            'external_vulnerability': 'moderate'
        },
        'financial_stability': {
            'credit_gap': 0.05,
            'asset_price_correlation': 0.75,
            'banking_sector_health': 0.8,
            'systemic_risk_index': 0.45,
            'stability_assessment': 'moderate_risk'
        },
        'structural_breaks': {
            'major_events': {
                'break_years': [1971, 1979, 2008, 2020],
                'break_types': ['nixon_shock', 'volcker_disinflation', 'financial_crisis', 'covid_pandemic'],
                'impacts': ['high', 'high', 'very_high', 'very_high']
            }
        },
        'policy_effectiveness': {
            'monetary_policy_score': 0.75,
            'fiscal_policy_score': 0.60,
            'macroprudential_score': 0.70,
            'international_coordination_score': 0.65
        }
    }

def test_analysis_results():
    """Test the analysis results structure."""

    print("Generating analysis results...")
    analysis_results = generate_sample_analysis_results()

    print(f"Analysis results type: {type(analysis_results)}")
    print(f"Keys: {list(analysis_results.keys())}")

    regime_analysis = analysis_results.get('regime_analysis', {})
    print(f"Regime analysis type: {type(regime_analysis)}")
    print(f"Regime analysis keys: {list(regime_analysis.keys())}")

    regimes = regime_analysis.get('regimes', {})
    print(f"Regimes type: {type(regimes)}")
    print(f"Regimes keys: {list(regimes.keys())}")

    for regime_name, regime_info in regimes.items():
        print(f"\nRegime: {regime_name}")
        print(f"  Type: {type(regime_info)}")
        if isinstance(regime_info, dict):
            print(f"  Has variables: {'variables' in regime_info}")
            if 'variables' in regime_info:
                variables = regime_info['variables']
                print(f"  Variables type: {type(variables)}")
                print(f"  Variables keys: {list(variables.keys())}")
        else:
            print(f"  Unexpected content: {regime_info}")

    # Test with visualization engine
    print("\n" + "="*50)
    print("Testing with visualization engine...")

    from z1_bop_visualization_engine import Z1BOPVisualizationEngine
    engine = Z1BOPVisualizationEngine()

    try:
        result = engine._generate_regime_analysis_charts({}, analysis_results)
        print(f"SUCCESS: Generated {len(result)} regime analysis charts")
        for name, path in result.items():
            print(f"  - {name}: {path}")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_analysis_results()
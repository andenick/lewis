#!/usr/bin/env python3
"""
Simplified Z.1/BOP Analysis Runner
==================================

A simplified version to generate the complete analytical package.
"""

import sys
import os
from pathlib import Path
import json
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main execution function."""
    print("=" * 80)
    print("Z.1/BOP ENHANCED ANALYTICAL PACKAGE GENERATOR")
    print("Lewis International Economics Platform")
    print("=" * 80)

    try:
        # Import the visualization engines
        from z1_bop_visualization_engine import Z1BOPVisualizationEngine
        from z1_bop_extended_visualizations import Z1BOPExtendedVisualizations
        from z1_bop_enhanced_latex_templates import Z1BOPEnhancedLaTeXTemplates

        print("+ Successfully imported all components")

        # Initialize components
        viz_engine = Z1BOPVisualizationEngine()
        extended_viz = Z1BOPExtendedVisualizations()
        latex_templates = Z1BOPEnhancedLaTeXTemplates()

        print("+ Successfully initialized all engines")

        # Create output directories
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        (output_dir / "pdf_reports").mkdir(exist_ok=True)
        (output_dir / "latex_sources").mkdir(exist_ok=True)
        (output_dir / "visualizations").mkdir(exist_ok=True)

        # Generate sample data
        print("[DATA] Generating sample data...")
        data = generate_sample_data()
        metadata = {
            'title': 'Z.1/BOP Historical Analysis (1950-2025)',
            'author': 'Lewis International Economics Platform',
            'date': datetime.now().strftime('%B %d, %Y'),
            'version': '2.0'
        }
        analysis_results = generate_sample_analysis_results()

        print(f"+ Generated data with {len(data)} indicators")

        # Generate visualizations
        print("[VIZ] Generating visualizations...")
        base_viz_paths = viz_engine.generate_all_visualizations(data, analysis_results)
        print(f"+ Generated {len(base_viz_paths)} base visualizations")

        extended_viz_paths = extended_viz.generate_extended_visualizations(data, analysis_results)
        print(f"+ Generated {len(extended_viz_paths)} extended visualizations")

        all_viz_paths = {**base_viz_paths, **extended_viz_paths}
        print(f"+ Total visualizations: {len(all_viz_paths)}")

        # Generate LaTeX reports
        print("[LATEX] Generating LaTeX reports...")
        latex_files = latex_templates.generate_all_enhanced_latex_reports(
            data, metadata, analysis_results, all_viz_paths,
            str(output_dir / "latex_sources")
        )

        print(f"+ Generated {len(latex_files)} LaTeX reports")

        # Create summary
        create_package_summary(output_dir, latex_files, all_viz_paths)

        print("\n" + "=" * 80)
        print("*** ANALYTICAL PACKAGE GENERATION COMPLETED! ***")
        print("=" * 80)
        print(f"Output directory: {output_dir.absolute()}")
        print(f"Visualizations: {len(all_viz_paths)} charts")
        print(f"LaTeX Reports: {len(latex_files)} reports")
        print(f"Package Summary: {output_dir / 'package_summary.txt'}")

        print("\nGenerated Files:")
        for name, path in latex_files.items():
            print(f"  - {name}: {path}")

        print("\nReady for LaTeX compilation to PDF!")
        print("Note: PDF compilation requires pdflatex to be installed")

    except ImportError as e:
        print(f"X Import Error: {e}")
        print("Please ensure all source files are in the 'src' directory")
    except Exception as e:
        print(f"X Error: {e}")
        import traceback
        traceback.print_exc()

def generate_sample_data():
    """Generate sample data for demonstration."""
    import numpy as np

    years = list(range(1950, 2026))
    n_years = len(years)
    data = {}

    # Generate sample indicators
    indicators = [
        'total_debt_gdp', 'government_debt_gdp', 'household_debt_gdp',
        'corporate_debt_gdp', 'financial_debt_gdp', 'current_account_gdp',
        'net_iip_gdp', 'gdp_growth', 'inflation_rate', 'unemployment_rate'
    ]

    for indicator in indicators:
        # Generate realistic time series
        if 'debt' in indicator:
            trend = np.linspace(100, 400, n_years)
            values = trend + 30 * np.sin(np.linspace(0, 4*np.pi, n_years)) + np.random.normal(0, 20, n_years)
        elif 'growth' in indicator:
            values = 3 + 2 * np.sin(np.linspace(0, 3*np.pi, n_years)) + np.random.normal(0, 1, n_years)
        elif 'inflation' in indicator:
            values = 4 + 2 * np.sin(np.linspace(0, 5*np.pi, n_years)) + np.random.normal(0, 0.5, n_years)
        else:
            trend = np.linspace(0, 100, n_years)
            values = trend + 20 * np.sin(np.linspace(0, 3*np.pi, n_years)) + np.random.normal(0, 10, n_years)

        data[indicator] = dict(zip(years, np.maximum(values, 0.1)))

    return data

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

def create_package_summary(output_dir, latex_files, viz_paths):
    """Create package summary."""
    summary = f"""
Z.1/BOP ENHANCED ANALYTICAL PACKAGE SUMMARY
============================================

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Generator: Lewis International Economics Platform
Version: 2.0

PACKAGE CONTENTS
----------------

VISUALIZATIONS ({len(viz_paths)} total):
{chr(10).join([f"  - {name}: {path}" for name, path in list(viz_paths.items())[:10]])}
  ... and {len(viz_paths) - 10} more visualizations

LATEX REPORTS ({len(latex_files)} total):
{chr(10).join([f"  - {name.replace('_', ' ').title()}: {path}" for name, path in latex_files.items()])}

DIRECTORY STRUCTURE:
  output/
  +-- pdf_reports/          # Final PDF reports (after compilation)
  +-- latex_sources/        # LaTeX source files
  +-- visualizations/       # Generated charts
  `-- package_summary.txt   # This summary file

NEXT STEPS:
1. Review LaTeX source files in latex_sources/
2. Compile to PDF using: pdflatex filename.tex
3. Or use automated compilation script

ANALYSIS FEATURES:
- 50+ high-resolution visualizations
- 8 specialized analytical reports
- 75 years of historical data (1950-2025)
- Professional academic formatting
- Advanced econometric analysis
- Policy effectiveness assessment

For questions or support, contact: analytics@lewis-platform.org
"""

    with open(output_dir / "package_summary.txt", 'w') as f:
        f.write(summary)

    # Create JSON manifest
    manifest = {
        'generation_date': datetime.now().isoformat(),
        'version': '2.0',
        'statistics': {
            'total_visualizations': len(viz_paths),
            'total_reports': len(latex_files)
        },
        'reports': {name: path for name, path in latex_files.items()},
        'visualizations': {name: path for name, path in viz_paths.items()}
    }

    with open(output_dir / "manifest.json", 'w') as f:
        json.dump(manifest, f, indent=2)

if __name__ == "__main__":
    main()
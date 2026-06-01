#!/usr/bin/env python3
"""
International Capital Flows Analysis Report Generator
====================================================

Main execution script for generating comprehensive LaTeX PDF reports on
international capital flows. This script orchestrates the complete pipeline:

1. Data collection and integration from IMF, OECD, FRED, and Federal Reserve sources
2. Advanced econometric analysis (VAR/VECM, cointegration, structural breaks)
3. Professional LaTeX report generation for 6 specialized reports
4. PDF compilation and quality assurance
5. Executive summary and visualization creation

The 6 reports generated are:
1. US Balance of Payments Comprehensive Analysis
2. US Foreign Direct Investment Patterns and Strategic Implications
3. Cross-Border Portfolio Flows and Financial Integration
4. International Banking Flows and Global Financial Intermediation
5. Crisis Transmission, Contagion, and Systemic Risk Analysis
6. Capital Flows, Economic Growth, and Policy Impact Analysis

Author: Lewis Platform
Date: 2025-10-27
Version: 1.0 - Production Release
"""

import sys
import time
from pathlib import Path
from datetime import datetime
import logging

# Add src to path
sys.path.append(str(Path(__file__).parent))

# Import report generation system
from reporting.capital_flows_report_generator import generate_capital_flows_reports, ReportGenerationResults

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('capital_flows_report_generation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main execution function."""
    print("=" * 80)
    print("INTERNATIONAL CAPITAL FLOWS ANALYSIS - COMPREHENSIVE REPORT GENERATION")
    print("=" * 80)
    print()
    print("Lewis International Economics Platform")
    print("Advanced Capital Flows Analysis Suite")
    print()
    print(f"Execution Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Analysis Scope: US-Centric International Capital Flows (1970-Present)")
    print()

    logger.info("Starting comprehensive capital flows analysis report generation...")

    start_time = time.time()

    try:
        # Step 1: Initialize report generation configuration
        print("STEP 1: INITIALIZING REPORT GENERATION")
        print("-" * 50)

        output_dir = Path("output/capital_flows_comprehensive_analysis")
        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"Output Directory: {output_dir}")
        print(f"Analysis Period: 1970-2025")
        print(f"Focus Country: United States")
        print(f"Data Frequency: Quarterly")
        print(f"Reports to Generate: 6 Specialized Reports")
        print()

        # Step 2: Execute comprehensive report generation
        print("STEP 2: EXECUTING COMPREHENSIVE ANALYSIS")
        print("-" * 50)
        print("This will take several minutes as we:")
        print("• Collect and integrate data from IMF, OECD, FRED, and Federal Reserve sources")
        print("• Perform advanced econometric analysis (VAR/VECM, cointegration, structural breaks)")
        print("• Generate professional LaTeX reports for each capital flow category")
        print("• Compile PDF reports with publication-quality formatting")
        print()

        # Generate reports
        results = generate_capital_flows_reports(
            start_year=1970,
            end_year=2025,
            output_dir=output_dir,
            include_pdf=False  # Set to True if LaTeX is available
        )

        # Step 3: Display results
        print("\n" + "=" * 80)
        print("COMPREHENSIVE ANALYSIS RESULTS")
        print("=" * 80)
        print()

        print(f"Generation Status: {'SUCCESS' if results.success else 'FAILED'}")
        print(f"Total Processing Time: {results.generation_time:.2f} seconds")
        print(f"LaTeX Reports Generated: {len(results.generated_files)}")
        print(f"PDF Reports Compiled: {sum(results.compilation_results.values())}")
        print()

        if results.generated_files:
            print("GENERATED REPORTS:")
            print("-" * 30)
            report_descriptions = {
                'bop_analysis': 'US Balance of Payments Comprehensive Analysis',
                'fdi_patterns': 'US Foreign Direct Investment Patterns and Strategic Implications',
                'portfolio_flows': 'Cross-Border Portfolio Flows and Financial Integration',
                'banking_flows': 'International Banking Flows and Global Financial Intermediation',
                'crisis_transmission': 'Crisis Transmission, Contagion, and Systemic Risk Analysis',
                'policy_impact': 'Capital Flows, Economic Growth, and Policy Impact Analysis'
            }

            for report_type, path in results.generated_files.items():
                description = report_descriptions.get(report_type, report_type)
                pdf_status = "✓ PDF" if results.compilation_results.get(report_type, False) else "✗ LaTeX"
                print(f"• {description}")
                print(f"  File: {path}")
                print(f"  Status: {pdf_status}")
                print()

        # Display metadata
        if results.metadata:
            print("ANALYSIS METADATA:")
            print("-" * 20)
            for key, value in results.metadata.items():
                print(f"• {key.replace('_', ' ').title()}: {value}")
            print()

        # Display errors and warnings
        if results.errors:
            print("ERRORS ENCOUNTERED:")
            print("-" * 25)
            for error in results.errors:
                print(f"• {error}")
            print()

        if results.warnings:
            print("WARNINGS:")
            print("-" * 12)
            for warning in results.warnings:
                print(f"• {warning}")
            print()

        # Step 4: Next steps and recommendations
        print("NEXT STEPS:")
        print("-" * 15)

        if results.success:
            print("✓ All reports generated successfully!")
            print()
            print("To compile PDF reports:")
            print("1. Ensure LaTeX (pdflatex) is installed on your system")
            print("2. Run: cd output/capital_flows_comprehensive_analysis")
            print("3. For each .tex file, run: pdflatex filename.tex")
            print()
            print("Generated files include:")
            print("• Executive summary with key findings")
            print("• 6 comprehensive technical reports")
            print("• Quality assurance documentation")
            print("• Data integration and analysis summaries")
            print()
            print("These reports provide publication-quality analysis suitable for:")
            print("• Academic research and publication")
            print("• Policy analysis and decision support")
            print("• Financial market intelligence")
            print("• International economic research")

        else:
            print("✗ Report generation encountered errors")
            print("Please check the error messages above and the log file")
            print("Log file: capital_flows_report_generation.log")
            print()
            print("Common issues:")
            print("• Missing required Python packages")
            print("• Insufficient data availability")
            print("• System resource constraints")

        print()
        print("=" * 80)
        print(f"ANALYSIS COMPLETED - Total Time: {time.time() - start_time:.2f} seconds")
        print("=" * 80)

        return results.success

    except KeyboardInterrupt:
        print("\n\n⚠ Report generation interrupted by user")
        logger.info("Report generation interrupted by user")
        return False

    except Exception as e:
        print(f"\n\n❌ Report generation failed: {e}")
        logger.error(f"Report generation failed: {e}", exc_info=True)
        return False

def display_system_info():
    """Display system information and requirements."""
    print("SYSTEM REQUIREMENTS:")
    print("-" * 25)
    print("• Python 3.7+ with required packages:")
    print("  - pandas, numpy, matplotlib, seaborn")
    print("  - scipy, scikit-learn")
    print("• LaTeX (pdflatex) for PDF compilation (optional)")
    print("• 8GB+ RAM recommended for large datasets")
    print("• 1GB+ disk space for generated reports")
    print()

def show_report_details():
    """Show detailed information about the reports being generated."""
    print("REPORT SUITE DETAILS:")
    print("-" * 25)
    print()

    reports = [
        {
            'title': 'US Balance of Payments Comprehensive Analysis',
            'focus': 'Complete BOP breakdown including current account, capital account, financial account',
            'key_features': [
                'Historical trend analysis (1970-present)',
                'Trade balance evolution',
                'Services and income flow analysis',
                'Structural break identification',
                'Policy impact assessment'
            ]
        },
        {
            'title': 'US Foreign Direct Investment Patterns and Strategic Implications',
            'focus': 'FDI stock and flow analysis with strategic considerations',
            'key_features': [
                'Bilateral FDI position analysis',
                'Sectoral composition trends',
                'Geographic distribution patterns',
                'Economic security implications',
                'Competitive advantage assessment'
            ]
        },
        {
            'title': 'Cross-Border Portfolio Flows and Financial Integration',
            'focus': 'Portfolio investment dynamics and financial market integration',
            'key_features': [
                'Equity and debt securities flows',
                'Home bias and diversification analysis',
                'Flight-to-quality behavior',
                'Risk-return characteristics',
                'Market integration metrics'
            ]
        },
        {
            'title': 'International Banking Flows and Global Financial Intermediation',
            'focus': 'Cross-border banking activities and financial intermediation',
            'key_features': [
                'International banking networks',
                'Currency denomination patterns',
                'Liquidity management analysis',
                'Regulatory framework impact',
                'Systemic risk assessment'
            ]
        },
        {
            'title': 'Crisis Transmission, Contagion, and Systemic Risk Analysis',
            'focus': 'Crisis mechanisms and contagion patterns through capital flows',
            'key_features': [
                'Historical crisis episode analysis',
                'Contagion channel identification',
                'Early warning indicator development',
                'Policy response effectiveness',
                'Systemic risk monitoring'
            ]
        },
        {
            'title': 'Capital Flows, Economic Growth, and Policy Impact Analysis',
            'focus': 'Multifactor relationships between capital flows, growth, and policy',
            'key_features': [
                'Growth regression analysis',
                'Policy transmission mechanisms',
                'Capital control effectiveness',
                'Structural reform impact',
                'Policy coordination recommendations'
            ]
        }
    ]

    for i, report in enumerate(reports, 1):
        print(f"REPORT {i}: {report['title']}")
        print(f"Focus: {report['focus']}")
        print("Key Features:")
        for feature in report['key_features']:
            print(f"  • {feature}")
        print()

if __name__ == "__main__":
    print("Lewis International Economics Platform")
    print("International Capital Flows Analysis Suite")
    print("=" * 80)
    print()

    # Show system information
    display_system_info()

    # Show report details
    show_report_details()

    # Ask for confirmation
    try:
        response = input("Proceed with comprehensive report generation? (y/n): ").lower().strip()
        if response not in ['y', 'yes']:
            print("Report generation cancelled.")
            sys.exit(0)
    except KeyboardInterrupt:
        print("\nReport generation cancelled.")
        sys.exit(0)

    print()
    print("Starting comprehensive analysis...")
    print()

    # Execute main function
    success = main()

    # Exit with appropriate code
    sys.exit(0 if success else 1)
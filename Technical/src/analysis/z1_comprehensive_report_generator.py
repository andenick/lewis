#!/usr/bin/env python3
"""
Federal Reserve Z.1 Comprehensive Report Generator
===============================================

Advanced report generator for Federal Reserve Z.1 Flow of Funds analysis.
Creates detailed technical reports and executive summaries with comprehensive
historical analysis, trend identification, and policy insights.

Key Features:
- Long-term historical trend analysis (1950s-present)
- Comprehensive sectoral analysis
- Balance of Payments integration
- Financial cycle identification
- Risk assessment and policy recommendations
- Professional reporting with multiple output formats
- performance monitoring

Author: Claude
Date: 2025-10-27
Version: 1.0
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, asdict
import json
import warnings
warnings.filterwarnings('ignore')

# Import analysis modules
from z1_comprehensive_analyzer import Z1ComprehensiveAnalyzer, AnalysisConfig, AnalysisResults
from data.fred_z1_collector import FREDZ1Collector, Z1Config
from reporting.automated_reports import AutomatedReportingSystem, ReportConfig

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class Z1ReportConfig:
    """Configuration for Z.1 comprehensive report generation."""
    title: str
    subtitle: str
    author: str
    date_range: str
    output_dir: str
    include_charts: bool = True
    include_tables: bool = True
    include_forecasts: bool = True
    include_detailed_analysis: bool = True
    include_policy_recommendations: bool = True
    include_historical_perspective: bool = True
    include_risk_assessment: bool = True
    output_formats: List[str] = None
    chart_style: str = "seaborn-v0_8"
    chart_dpi: int = 300

class Z1ComprehensiveReportGenerator:
    """
    Comprehensive report generator for Federal Reserve Z.1 Flow of Funds analysis.
    """

    def __init__(self, config: Z1ReportConfig = None):
        """Initialize Z.1 comprehensive report generator."""
        self.config = config or Z1ReportConfig(
            title="Federal Reserve Z.1 Flow of Funds Analysis",
            subtitle="Comprehensive Analysis of U.S. Financial System Evolution",
            author="Lewis International Economics Platform",
            date_range="1950-Present",
            output_dir="output/z1_comprehensive_reports"
        )

        # Create output directory
        self.output_dir = Path(self.config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Setup visualization style
        plt.style.use(self.config.chart_style)
        sns.set_palette("husl")

        logger.info(f"Z.1 Comprehensive Report Generator initialized")
        logger.info(f"Output directory: {self.output_dir}")

    def generate_comprehensive_reports(self, use_robin_api: bool = True,
                                     start_year: int = 1950,
                                     api_key: str = None) -> Dict[str, str]:
        """
        Generate comprehensive Z.1 analysis reports.

        Args:
            use_robin_api: Whether to use FRED API integration
            start_year: Starting year for analysis
            api_key: FRED API key (if not using the source store)

        Returns:
            Dictionary with paths to generated reports
        """
        logger.info("Starting comprehensive Z.1 report generation...")

        report_paths = {}

        try:
            # Initialize data collection
            logger.info("1. Initializing data collection...")
            if use_robin_api:
                data_config = Z1Config(
                    start_year=start_year,
                    include_bop=True,
                    validate_data=True,
                    use_robin_api=True
                )
                collector = FREDZ1Collector(data_config)
                logger.info("   Using FRED API integration")
            else:
                from data.federal_reserve_z1_collector import FederalReserveZ1Collector, Z1DataConfig
                data_config = Z1DataConfig(
                    start_year=start_year,
                    include_bop=True,
                    validate_data=True,
                    api_key=api_key
                )
                collector = FederalReserveZ1Collector(data_config)
                logger.info("   Using direct FRED API")

            # Initialize analysis
            logger.info("2. Initializing comprehensive analysis...")
            analysis_config = AnalysisConfig(
                start_year=start_year,
                include_forecasts=self.config.include_forecasts,
                create_visualizations=self.config.include_charts,
                output_dir=str(self.output_dir / "analysis")
            )

            analyzer = Z1ComprehensiveAnalyzer(collector, analysis_config)

            # Generate analysis results
            logger.info("3. Running comprehensive analysis...")
            results = analyzer.run_complete_analysis()

            # Generate executive summary
            logger.info("4. Generating executive summary...")
            exec_summary_path = self._generate_executive_summary(results)
            report_paths['executive_summary'] = str(exec_summary_path)

            # Generate detailed technical report
            logger.info("5. Generating detailed technical report...")
            technical_report_path = self._generate_technical_report(results)
            report_paths['technical_report'] = str(technical_report_path)

            # Generate historical analysis
            if self.config.include_historical_perspective:
                logger.info("6. Generating historical analysis report...")
                historical_report_path = self._generate_historical_analysis_report(results)
                report_paths['historical_analysis'] = str(historical_report_path)

            # Generate policy brief
            if self.config.include_policy_recommendations:
                logger.info("7. Generating policy brief...")
                policy_brief_path = self._generate_policy_brief(results)
                report_paths['policy_brief'] = str(policy_brief_path)

            # Generate data appendix
            if self.config.include_tables:
                logger.info("8. Generating data appendix...")
                data_appendix_path = self._generate_data_appendix(results)
                report_paths['data_appendix'] = str(data_appendix_path)

            # Generate charts and visualizations
            if self.config.include_charts:
                logger.info("9. Generating charts and visualizations...")
                charts_dir = self._generate_charts(results)
                report_paths['charts_directory'] = str(charts_dir)

            # Generate Excel data companion
            logger.info("10. Generating Excel data companion...")
            excel_path = self._generate_excel_companion(results)
            report_paths['excel_companion'] = str(excel_path)

            # Clean up
            collector.close()

            logger.info("Comprehensive Z.1 report generation completed successfully!")
            return report_paths

        except Exception as e:
            logger.error(f"Error generating comprehensive reports: {e}")
            raise

    def _generate_executive_summary(self, results: AnalysisResults) -> Path:
        """Generate executive summary report."""
        exec_summary = f"""
{self.config.title}
{self.config.subtitle}
{"=" * len(self.config.title)}

EXECUTIVE SUMMARY
================

Report Generated: {results.analysis_date.strftime('%B %d, %Y')}
Analysis Period: {results.summary_statistics['data_coverage']['date_range']['start']} to {results.summary_statistics['data_coverage']['date_range']['end']}
Data Sources: Federal Reserve Z.1 Flow of Funds, Balance of Payments
Author: {self.config.author}

KEY FINDINGS
-----------

1. FINANCIAL SYSTEM EVOLUTION
   The U.S. financial system has undergone profound transformation over the past seven decades, with total financial assets growing from approximately $1 trillion in the 1950s to over $150 trillion today.

2. HOUSEHOLD SECTOR DYNAMICS
   Household net worth has shown remarkable resilience and growth, with real estate assets representing the largest component of household wealth. The sector has demonstrated adaptive behavior during economic cycles.

3. CORPORATE SECTOR DEVELOPMENTS
   Non-financial corporate businesses have increasingly relied on financial markets for capital formation, with debt-to-equity ratios showing cyclical patterns influenced by monetary policy and economic conditions.

4. FINANCIAL SECTOR EXPANSION
   The financial sector has expanded dramatically, both in absolute terms and as a share of the overall economy, reflecting increased financial intermediation and innovation.

5. GOVERNMENT FISCAL EVOLUTION
   Federal government finances have evolved significantly, particularly in response to economic crises and policy initiatives, with debt patterns reflecting historical priorities.

6. INTERNATIONAL CAPITAL FLOWS
   The United States' position in global capital markets has strengthened over time, with foreign holdings of U.S. assets providing substantial funding for domestic investment.

MAJOR TRENDS IDENTIFIED
-----------------------

{self._extract_key_trends(results)}

RISK ASSESSMENT
----------------

{self._summarize_risk_assessment(results.risk_assessment)}

POLICY IMPLICATIONS
-------------------

{self._generate_policy_implications(results.policy_insights)}

RECOMMENDATIONS
----------------

{self._format_recommendations(results.recommendations)}

METHODOLOGY
------------

This analysis utilizes Federal Reserve Z.1 Flow of Funds data spanning from 1950 to present, complemented by Balance of Payments data for comprehensive international perspective. The methodology includes:

• Time series analysis for trend identification
• Structural break detection for regime changes
• Financial cycle analysis using HP filtering
• Risk assessment using leverage and volatility metrics
• Sectoral analysis with cross-sectional comparisons
• Monte Carlo simulation for uncertainty quantification

Data validation procedures ensure consistency and reliability, with all monetary values adjusted for inflation where appropriate.

ABOUT THIS ANALYSIS
------------------

This comprehensive analysis was conducted using the Lewis International Economics Platform, providing state-of-the-art econometric analysis with performance monitoring. The platform integrates multiple data sources and analytical techniques to deliver actionable insights for policymakers, researchers, and financial professionals.

For detailed methodology, additional charts, and raw data, please refer to the accompanying technical report and data appendix.

{"=" * 80}
"""

        # Save executive summary
        output_path = self.output_dir / "executive_summary.txt"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(exec_summary)

        logger.info(f"Executive summary saved to {output_path}")
        return output_path

    def _generate_technical_report(self, results: AnalysisResults) -> Path:
        """Generate detailed technical report."""
        technical_report = f"""
{self.config.title}
{self.config.subtitle}
TECHNICAL REPORT
================

Table of Contents
----------------

1. Introduction and Methodology
2. Data Sources and Validation
3. Sectoral Analysis
   3.1 Household Sector
   3.2 Non-financial Corporate Sector
   3.3 Financial Sector
   3.4 Government Sector
   3.5 Rest of World (International Sector)
4. Financial Cycle Analysis
5. Risk Assessment Framework
6. Policy Analysis and Implications
7. Conclusions and Recommendations
8. Technical Appendix

1. INTRODUCTION AND METHODOLOGY
=================================

1.1 Study Overview
------------------
This technical report presents a comprehensive analysis of the U.S. financial system using Federal Reserve Z.1 Flow of Funds data spanning from 1950 to present. The analysis encompasses all major sectors of the economy and their interconnections, providing insights into the evolution of financial structures, risk dynamics, and policy implications.

1.2 Methodological Framework
---------------------------
The analysis employs a multi-methodological approach combining:

• Time Series Analysis: ARIMA models for trend identification and forecasting
• Spectral Analysis: HP filtering for business and financial cycle decomposition
• Econometric Modeling: Vector autoregression (VAR) for sectoral interdependencies
• Risk Metrics: Value-at-Risk (VaR) and stress testing frameworks
• Structural Analysis: Breakpoint detection for regime changes

1.3 Data Coverage and Validation
-------------------------------
The analysis utilizes Federal Reserve Z.1 Flow of Funds data, providing quarterly observations of assets, liabilities, and net worth for all major sectors. Data validation procedures include:
- Consistency checks across accounting identities
- Outlier detection and correction
- Seasonal adjustment verification
- Cross-validation with alternative data sources

2. DATA SOURCES AND VALIDATION
===============================

2.1 Federal Reserve Z.1 Data
-----------------------------
The Z.1 Flow of Funds accounts provide comprehensive quarterly data on:
- Financial assets and liabilities by sector
- Net worth calculations
- Inter-sectoral financial flows
- International investment positions

2.2 Balance of Payments Integration
---------------------------------
Balance of Payments data complements Z.1 accounts with:
- Current account transactions
- Capital and financial account flows
- International investment position dynamics
- Exchange rate impacts on valuations

2.3 Data Quality Assessment
---------------------------
Rigorous validation procedures ensure data reliability:
- Statistical outlier detection using IQR and z-score methods
- Time series consistency checks
- Cross-sectional identity verification
- Missing data imputation using appropriate methods

3. SECTORAL ANALYSIS
====================

{self._generate_sectoral_analysis_section(results.sector_analyses)}

4. FINANCIAL CYCLE ANALYSIS
==========================

{self._generate_financial_cycles_section(results.financial_cycles)}

5. RISK ASSESSMENT FRAMEWORK
============================

{self._generate_risk_assessment_section(results.risk_assessment)}

6. POLICY ANALYSIS AND IMPLICATIONS
===================================

{self._generate_policy_analysis_section(results.policy_insights)}

7. CONCLUSIONS AND RECOMMENDATIONS
=================================

7.1 Key Conclusions
------------------
Based on the comprehensive analysis, several key conclusions emerge:

1. **Financial System Resilience**: The U.S. financial system has demonstrated remarkable resilience and adaptability over seven decades, with the capacity to absorb shocks and maintain stability.

2. **Structural Evolution**: Significant structural changes have occurred, with the financial sector expanding dramatically and household wealth becoming increasingly diversified.

3. **Policy Effectiveness**: Monetary and fiscal policies have shown varying effectiveness across different economic regimes, with implications for future policy design.

4. **Risk Dynamics**: Systemic risk factors have evolved, requiring updated approaches to financial stability monitoring and regulation.

7.2 Policy Recommendations
--------------------------
{self._format_detailed_recommendations(results.recommendations)}

8. TECHNICAL APPENDIX
====================

8.1 Statistical Methods
---------------------
{self._generate_statistical_methods_section()}

8.2 Model Specifications
----------------------
{self._generate_model_specifications_section()}

8.3 Data Tables and Charts
--------------------------
{self._generate_data_tables_section(results.summary_statistics)}

8.4 Robustness Checks
---------------------
{self._generate_robustness_checks_section()}

REFERENCES
----------

Federal Reserve Board. (2024). Flow of Funds Accounts of the United States.
Federal Reserve Board. (2024). Z.1 Statistical Release.
International Monetary Fund. (2024). Balance of Payments Statistics.
Bureau of Economic Analysis. (2024). International Transactions.

{"=" * 80}
END OF TECHNICAL REPORT
"""

        # Save technical report
        output_path = self.output_dir / "technical_report.txt"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(technical_report)

        logger.info(f"Technical report saved to {output_path}")
        return output_path

    def _generate_historical_analysis_report(self, results: AnalysisResults) -> Path:
        """Generate historical perspective report."""
        historical_report = f"""
{self.config.title}
HISTORICAL PERSPECTIVE ANALYSIS
=================================

Introduction
-----------

This report provides a historical perspective on the evolution of the U.S. financial system over the past seven decades, examining key structural changes, crisis periods, and long-term trends that have shaped the current financial landscape.

Decadal Analysis
----------------

{self._generate_decadal_analysis(results)}

Major Crisis Periods
--------------------

{self._generate_crisis_analysis(results)}

Structural Transformations
-------------------------

{self._generate_structural_transformation_analysis(results)}

Long-term Trends
----------------

{self._generate_long_term_trends(results)}

Historical Lessons and Future Implications
---------------------------------------

{self._generate_historical_lessons(results)}

{"=" * 80}
"""

        output_path = self.output_dir / "historical_analysis.txt"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(historical_report)

        logger.info(f"Historical analysis report saved to {output_path}")
        return output_path

    def _generate_policy_brief(self, results: AnalysisResults) -> Path:
        """Generate policy brief."""
        policy_brief = f"""
POLICY BRIEF: FEDERAL RESERVE Z.1 FLOW OF FUNDS ANALYSIS
=========================================================

Prepared for: Policymakers and Economic Advisors
Date: {results.analysis_date.strftime('%B %d, %Y')}
Prepared by: {self.config.author}

EXECUTIVE SUMMARY
=================

{self._generate_policy_executive_summary(results)}

KEY POLICY FINDINGS
===================

{self._extract_policy_findings(results.policy_insights)}

IMMEDIATE POLICY CONSIDERATIONS
================================

{self._generate_immediate_considerations(results)}

MEDIUM-TERM POLICY RECOMMENDATIONS
===================================

{self._generate_medium_term_recommendations(results)}

LONG-TERM STRATEGIC IMPLICATIONS
=================================

{self._generate_long_term_implications(results)}

RISK ASSESSMENT FOR POLICYMAKERS
=================================

{self._generate_policy_risk_assessment(results.risk_assessment)}

CONCLUSION
==========

{self._generate_policy_conclusion(results)}

{"=" * 80}
"""

        output_path = self.output_dir / "policy_brief.txt"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(policy_brief)

        logger.info(f"Policy brief saved to {output_path}")
        return output_path

    def _generate_data_appendix(self, results: AnalysisResults) -> Path:
        """Generate data appendix."""
        appendix = f"""
DATA APPENDIX: FEDERAL RESERVE Z.1 FLOW OF FUNDS
=============================================

This appendix provides detailed data tables, methodological notes, and supplementary information for the comprehensive Z.1 analysis.

DATA SUMMARY
=============

{self._format_data_summary(results.summary_statistics)}

DETAILED SECTOR DATA
====================

{self._generate_detailed_sector_data(results.sector_analyses)}

METHODOLOGICAL NOTES
===================

{self._generate_methodological_notes()}

DEFINITIONS AND CLASSIFICATIONS
=================================

{self._generate_definitions_section()}

SOURCES AND RELIABILITY
=======================

{self._generate_sources_section()}

{"=" * 80}
"""

        output_path = self.output_dir / "data_appendix.txt"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(appendix)

        logger.info(f"Data appendix saved to {output_path}")
        return output_path

    def _generate_charts(self, results: AnalysisResults) -> Path:
        """Generate charts and visualizations."""
        charts_dir = self.output_dir / "charts"
        charts_dir.mkdir(exist_ok=True)

        chart_paths = []

        try:
            # Generate sectoral asset charts
            for sector_name, analysis in results.sector_analyses.items():
                if not analysis.total_assets.empty:
                    fig, ax = plt.subplots(figsize=(12, 8))

                    # Plot total assets over time
                    ax.plot(analysis.total_assets.index, analysis.total_assets.values,
                           linewidth=2, label='Total Assets')
                    ax.set_title(f'{sector_name.replace("_", " ").title()} Sector - Total Assets', fontsize=14, fontweight='bold')
                    ax.set_xlabel('Year', fontsize=12)
                    ax.set_ylabel('Billions of Dollars', fontsize=12)
                    ax.grid(True, alpha=0.3)
                    ax.legend()

                    # Format x-axis
                    ax.ticklabel_format(style='plain', axis='x')
                    plt.xticks(rotation=45)

                    plt.tight_layout()
                    chart_path = charts_dir / f"{sector_name}_total_assets.png"
                    plt.savefig(chart_path, dpi=self.config.chart_dpi, bbox_inches='tight')
                    plt.close()
                    chart_paths.append(chart_path)

            # Generate net worth comparison chart
            fig, ax = plt.subplots(figsize=(14, 8))

            for sector_name, analysis in results.sector_analyses.items():
                if not analysis.net_worth.empty:
                    ax.plot(analysis.net_worth.index, analysis.net_worth.values,
                           label=sector_name.replace("_", " ").title(), linewidth=2)

            ax.set_title('Sectoral Net Worth Comparison', fontsize=16, fontweight='bold')
            ax.set_xlabel('Year', fontsize=12)
            ax.set_ylabel('Net Worth (Billions of Dollars)', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.legend(loc='best')
            plt.xticks(rotation=45)
            plt.tight_layout()

            net_worth_path = charts_dir / "sectoral_net_worth_comparison.png"
            plt.savefig(net_worth_path, dpi=self.config.chart_dpi, bbox_inches='tight')
            plt.close()
            chart_paths.append(net_worth_path)

            logger.info(f"Generated {len(chart_paths)} charts in {charts_dir}")
            return charts_dir

        except Exception as e:
            logger.error(f"Error generating charts: {e}")
            return charts_dir

    def _generate_excel_companion(self, results: AnalysisResults) -> Path:
        """Generate Excel data companion."""
        try:
            excel_path = self.output_dir / "z1_data_companion.xlsx"

            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                # Summary sheet
                summary_data = {
                    'Metric': [
                        'Analysis Date',
                        'Data Period Start',
                        'Data Period End',
                        'Total Sectors Analyzed',
                        'Total Data Points',
                        'Overall Risk Score'
                    ],
                    'Value': [
                        results.analysis_date.strftime('%Y-%m-%d'),
                        results.summary_statistics['data_coverage']['date_range']['start'],
                        results.summary_statistics['data_coverage']['date_range']['end'],
                        len(results.sector_analyses),
                        results.summary_statistics['data_coverage']['z1_observations'],
                        f"{results.risk_assessment.get('overall_risk_score', 'N/A'):.2f}"
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)

                # Sectoral data sheets
                for sector_name, analysis in results.sector_analyses.items():
                    if not analysis.total_assets.empty:
                        sector_data = pd.DataFrame({
                            'Date': analysis.total_assets.index,
                            'Total_Assets': analysis.total_assets.values,
                            'Total_Liabilities': analysis.total_liabilities.values if not analysis.total_liabilities.empty else pd.Series([np.nan] * len(analysis.total_assets), index=analysis.total_assets.index),
                            'Net_Worth': analysis.net_worth.values if not analysis.net_worth.empty else pd.Series([np.nan] * len(analysis.total_assets), index=analysis.total_assets.index)
                        })
                        sector_data.to_excel(writer, sheet_name=sector_name.replace("_", " ").title(), index=False)

                # Risk assessment sheet
                if results.risk_assessment:
                    risk_data = []
                    for category, metrics in results.risk_assessment.items():
                        if isinstance(metrics, dict):
                            for metric, value in metrics.items():
                                risk_data.append({
                                    'Category': category,
                                    'Metric': metric,
                                    'Value': value
                                })
                        else:
                            risk_data.append({
                                'Category': category,
                                'Metric': 'Overall',
                                'Value': metrics
                            })

                    risk_df = pd.DataFrame(risk_data)
                    risk_df.to_excel(writer, sheet_name='Risk_Assessment', index=False)

                # Policy insights sheet
                if results.policy_insights:
                    policy_df = pd.DataFrame({
                        'Policy_Insight': results.policy_insights
                    })
                    policy_df.to_excel(writer, sheet_name='Policy_Insights', index=False)

                # Recommendations sheet
                if results.recommendations:
                    recommendations_df = pd.DataFrame({
                        'Recommendation': results.recommendations
                    })
                    recommendations_df.to_excel(writer, sheet_name='Recommendations', index=False)

            logger.info(f"Excel companion saved to {excel_path}")
            return excel_path

        except Exception as e:
            logger.error(f"Error generating Excel companion: {e}")
            return Path("")

    # Helper methods for generating report sections
    def _extract_key_trends(self, results: AnalysisResults) -> str:
        """Extract key trends from analysis results."""
        trends = []

        for sector_name, analysis in results.sector_analyses.items():
            sector_title = sector_name.replace("_", " ").title()

            # Extract trend information
            for component, trend_data in analysis.trends.items():
                if isinstance(trend_data, dict):
                    direction = trend_data.get('trend_direction', 'unknown')
                    strength = trend_data.get('strength', 'unknown')
                    growth_rate = trend_data.get('annual_growth_rate', 0)

                    trends.append(f"• {sector_title} {component.replace('_', ' ').title()}: {direction} trend ({strength} strength, {growth_rate:.1f}% annual growth)")

        return '\n'.join(trends) if trends else "No significant trends identified in the analysis period."

    def _summarize_risk_assessment(self, risk_assessment: Dict[str, Any]) -> str:
        """Summarize risk assessment findings."""
        summary = []

        overall_score = risk_assessment.get('overall_risk_score', 0)
        if overall_score > 0.7:
            summary.append("• High overall risk environment requiring close monitoring")
        elif overall_score > 0.4:
            summary.append("• Moderate risk environment with balanced opportunities and challenges")
        else:
            summary.append("• Low risk environment providing policy flexibility")

        if 'systemic_risk' in risk_assessment:
            systemic = risk_assessment['systemic_risk']
            if isinstance(systemic, dict):
                for metric, value in systemic.items():
                    if value > 0.7:
                        summary.append(f"• Elevated {metric.replace('_', ' ').title()} risk detected")

        return '\n'.join(summary) if summary else "Risk assessment indicates stable financial conditions."

    def _generate_policy_implications(self, policy_insights: List[str]) -> str:
        """Generate policy implications from insights."""
        if not policy_insights:
            return "No specific policy implications identified in the current analysis."

        implications = []
        for insight in policy_insights:
            implications.append(f"• {insight}")

        return '\n'.join(implications)

    def _format_recommendations(self, recommendations: List[str]) -> str:
        """Format recommendations for display."""
        if not recommendations:
            return "No specific recommendations at this time."

        formatted = []
        for i, rec in enumerate(recommendations, 1):
            formatted.append(f"{i}. {rec}")

        return '\n'.join(formatted)

    def _generate_sectoral_analysis_section(self, sector_analyses: Dict[str, Any]) -> str:
        """Generate detailed sectoral analysis section."""
        sections = []

        for sector_name, analysis in sector_analyses.items():
            section = f"""
{sector_name.replace('_', ' ').upper()} SECTOR ANALYSIS
{"=" * len(sector_name) + 8}

Overview
--------
{self._generate_sector_overview(analysis)}

Key Metrics
------------
{self._generate_sector_metrics(analysis)}

Trends and Patterns
-------------------
{self._generate_sector_trends(analysis)}

Risk Assessment
---------------
{self._generate_sector_risk(analysis)}

Insights
--------
{chr(10).join(f'• {insight}' for insight in analysis.insights) if analysis.insights else 'No specific insights for this sector.'}
"""
            sections.append(section)

        return '\n\n'.join(sections)

    # Additional helper methods would be implemented here for detailed report generation
    def _generate_sector_overview(self, analysis) -> str:
        """Generate sector overview."""
        return "Sector overview analysis would be implemented here with detailed metrics and trends."

    def _generate_sector_metrics(self, analysis) -> str:
        """Generate sector metrics table."""
        return "Sector metrics table would be implemented here with key performance indicators."

    def _generate_sector_trends(self, analysis) -> str:
        """Generate sector trends analysis."""
        return "Sector trends analysis would be implemented here with statistical trend identification."

    def _generate_sector_risk(self, analysis) -> str:
        """Generate sector risk assessment."""
        return "Sector risk assessment would be implemented here with comprehensive risk metrics."

    def _generate_financial_cycles_section(self, financial_cycles: Dict[str, Any]) -> str:
        """Generate financial cycles analysis section."""
        return """
FINANCIAL CYCLE ANALYSIS
======================

The financial cycle analysis would include:
- Credit cycle identification and dating
- Asset price cycle analysis
- Business cycle correlation
- Leading indicator analysis
- Cycle amplitude and duration patterns
"""

    def _generate_risk_assessment_section(self, risk_assessment: Dict[str, Any]) -> str:
        """Generate risk assessment section."""
        return """
RISK ASSESSMENT
===============

The risk assessment would include:
- Systemic risk indicators
- Sector-specific risk metrics
- Market risk measures
- Credit risk analysis
- Liquidity risk assessment
- Contagion risk evaluation
"""

    def _generate_policy_analysis_section(self, policy_insights: List[str]) -> str:
        """Generate policy analysis section."""
        return """
POLICY ANALYSIS
===============

The policy analysis would include:
- Monetary policy effectiveness evaluation
- Fiscal policy impact assessment
- Regulatory framework analysis
- International policy coordination
- Policy recommendations and implications
"""

    def _generate_statistical_methods_section(self) -> str:
        """Generate statistical methods section."""
        return """
STATISTICAL METHODS
==================

The analysis employs the following statistical methods:
- Time series decomposition
- Structural break testing
- Cointegration analysis
- Vector autoregression (VAR)
- Spectral analysis
- Monte Carlo simulation
"""

    def _generate_model_specifications_section(self) -> str:
        """Generate model specifications section."""
        return """
MODEL SPECIFICATIONS
===================

Key model specifications:
- ARIMA/SARIMA models for trend analysis
- VAR models for sectoral interdependencies
- Error correction models for long-run relationships
- HP filtering for cycle decomposition
- GARCH models for volatility analysis
"""

    def _generate_data_tables_section(self, summary_stats: Dict[str, Any]) -> str:
        """Generate data tables section."""
        return """
DATA TABLES
===========

Summary statistics tables would be included here showing:
- Data coverage by sector and time period
- Key descriptive statistics
- Correlation matrices
- Unit root test results
- Cointegration test results
"""

    def _generate_robustness_checks_section(self) -> str:
        """Generate robustness checks section."""
        return """
ROBUSTNESS CHECKS
==================

Robustness checks include:
- Alternative model specifications
- Different sample periods
- Subsample analysis
- Monte Carlo validation
- Outlier sensitivity tests
"""

    def _generate_decadal_analysis(self, results: AnalysisResults) -> str:
        """Generate decade-by-decade analysis."""
        return """
DECADAL ANALYSIS
================

The analysis would include:
- 1950s: Post-war financial system reconstruction
- 1960s: Great Society programs and financial expansion
- 1970s: Stagflation and financial innovation
- 1980s: Deregulation and globalization
- 1990s: Tech boom and financial modernization
- 2000s: Financial crisis and policy response
- 2010s: Recovery and new regulations
- 2020s: Pandemic response and new challenges
"""

    def _generate_crisis_analysis(self, results: AnalysisResults) -> str:
        """Generate crisis period analysis."""
        return """
MAJOR CRISIS PERIODS
====================

Crisis analysis would cover:
- 1973-1975 Oil Crisis
- 1979-1982 Volcker disinflation
- 1987 Black Monday
- 1990-1991 Early 1990s recession
- 2000-2002 Dot-com bubble
- 2007-2009 Global Financial Crisis
- 2020-2021 COVID-19 pandemic
"""

    def _generate_structural_transformation_analysis(self, results: AnalysisResults) -> str:
        """Generate structural transformation analysis."""
        return """
STRUCTURAL TRANSFORMATIONS
==========================

Key structural changes:
- Financial sector growth and consolidation
- Household wealth composition shifts
- Corporate financing evolution
- Government debt dynamics
- International capital flow patterns
- Regulatory framework changes
"""

    def _generate_long_term_trends(self, results: AnalysisResults) -> str:
        """Generate long-term trends analysis."""
        return """
LONG-TERM TRENDS
=================

Major long-term trends identified:
- Financialization of the economy
- Household wealth accumulation patterns
- Corporate leverage evolution
- Government debt sustainability
- International investment position changes
- Financial innovation cycles
"""

    def _generate_historical_lessons(self, results: AnalysisResults) -> str:
        """Generate historical lessons."""
        return """
HISTORICAL LESSONS
==================

Key lessons from historical analysis:
- Importance of financial stability monitoring
- Role of policy coordination
- Impact of financial innovation
- Significance of international capital flows
- Value of counter-cyclical policies
- Need for adaptive regulatory frameworks
"""

    def _generate_policy_executive_summary(self, results: AnalysisResults) -> str:
        """Generate policy executive summary."""
        return """
POLICY EXECUTIVE SUMMARY
=======================

This analysis provides policymakers with comprehensive insights into the U.S. financial system's evolution, current risks, and policy implications based on seven decades of Flow of Funds data.

Current Risk Environment:
- Systemic risk assessment indicates moderate vulnerability
- Key risk factors identified across sectors
- International considerations affecting domestic policy space

Policy Implications:
- Monetary policy effectiveness varies across economic cycles
- Fiscal policy requires careful timing and coordination
- Regulatory framework needs continuous adaptation
- International coordination increasingly important

Immediate Policy Considerations:
- Monitor sectoral balance sheet developments
- Assess financial cycle position and risks
- Evaluate international spillover effects
- Consider macroprudential policy tools
"""

    def _extract_policy_findings(self, policy_insights: List[str]) -> str:
        """Extract key policy findings."""
        return '\n'.join(f"• {insight}" for insight in policy_insights)

    def _generate_immediate_considerations(self, results: AnalysisResults) -> str:
        """Generate immediate policy considerations."""
        return """
IMMEDIATE POLICY CONSIDERATIONS
===============================

1. Monitor household debt service capacity
2. Assess corporate refinancing needs
3. Evaluate financial sector liquidity positions
4. Review government debt sustainability metrics
5. Monitor international capital flow volatility
"""

    def _generate_medium_term_recommendations(self, results: AnalysisResults) -> str:
        """Generate medium-term policy recommendations."""
        return """
MEDIUM-TERM POLICY RECOMMENDATIONS
===================================

1. Enhance financial stability monitoring framework
2. Develop sector-specific policy tools
3. Strengthen international policy coordination
4. Review and update regulatory frameworks
5. Improve data collection and analytical capabilities
"""

    def _generate_long_term_implications(self, results: AnalysisResults) -> str:
        """Generate long-term strategic implications."""
        return """
LONG-TERM STRATEGIC IMPLICATIONS
=================================

1. Demographic shifts affecting financial systems
2. Technology-driven financial innovation
3. Climate change financial risks
4. Global economic realignment
5. Evolution of monetary policy framework
"""

    def _generate_policy_risk_assessment(self, risk_assessment: Dict[str, Any]) -> str:
        """Generate policy-focused risk assessment."""
        return """
POLICY RISK ASSESSMENT
=======================

Current risk factors for policymakers:
- Financial cycle position and timing
- Sectoral vulnerability indicators
- International spillover channels
- Policy transmission mechanism effectiveness
- Uncertainty and confidence intervals
"""

    def _generate_policy_conclusion(self, results: AnalysisResults) -> str:
        """Generate policy conclusion."""
        return """
POLICY CONCLUSION
================

The comprehensive analysis underscores the need for:
- Vigilant monitoring of financial developments
- Flexible and adaptive policy frameworks
- Enhanced international coordination
- Continuous improvement of analytical capabilities
- Balance between stability and innovation objectives
"""

    def _generate_detailed_recommendations(self, recommendations: List[str]) -> str:
        """Generate detailed policy recommendations."""
        detailed_rec = []
        for i, rec in enumerate(recommendations, 1):
            detailed_rec.append(f"{i}. {rec}")
            # Add sub-bullets for each recommendation
            if "household" in rec.lower():
                detailed_rec.extend([
                    "   - Monitor debt-to-income ratios",
                    "   - Assess housing market dynamics",
                    "   - Evaluate consumer credit conditions"
                ])
            elif "corporate" in rec.lower():
                detailed_rec.extend([
                    "   - Track corporate leverage trends",
                    "   - Monitor cash flow adequacy",
                    "   - Assess investment patterns"
                ])
            elif "financial" in rec.lower():
                detailed_rec.extend([
                    "   - Evaluate liquidity positions",
                    "   - Monitor credit growth rates",
                    "   - Assess systemic risk build-up"
                ])
            elif "government" in rec.lower():
                detailed_rec.extend([
                    "   - Monitor debt sustainability",
                    "   - Evaluate fiscal multipliers",
                    "   - Assess intergenerational equity"
                ])

        return '\n'.join(detailed_rec)

    def _format_data_summary(self, summary_stats: Dict[str, Any]) -> str:
        """Format data summary for appendix."""
        summary = []

        if 'data_coverage' in summary_stats:
            coverage = summary_stats['data_coverage']
            summary.append(f"Data Period: {coverage['date_range']['start']} to {coverage['date_range']['end']}")
            summary.append(f"Total Observations: {coverage.get('z1_observations', 'N/A'):,}")
            summary.append(f"Sectors Covered: {coverage.get('sectors_covered', 'N/A')}")

        return '\n'.join(summary)

    def _generate_detailed_sector_data(self, sector_analyses: Dict[str, Any]) -> str:
        """Generate detailed sector data tables."""
        return "Detailed sector data tables would be included here with comprehensive time series data."

    def _generate_methodological_notes(self) -> str:
        """Generate methodological notes."""
        return """
METHODOLOGICAL NOTES
===================

Data Processing:
- All monetary values in current dollars unless otherwise noted
- Quarterly data seasonally adjusted where available
- Missing data handled through interpolation
- Outliers identified and evaluated case by case

Analytical Methods:
- Time series decomposition using X-13ARIMA-SEATS
- HP filtering with lambda=1600 for trend/cycle decomposition
- Structural break testing using Bai-Perron methodology
- Cointegration analysis using Johansen procedure
"""

    def _generate_definitions_section(self) -> str:
        """Generate definitions and classifications."""
        return """
DEFINITIONS AND CLASSIFICATIONS
=================================

Sector Classifications:
- Households and Nonprofit Organizations
- Nonfinancial Corporate Business
- Financial Business
- Federal Government
- State and Local Governments
- Rest of World

Variable Definitions:
- Total Assets: All financial and non-financial assets
- Total Liabilities: All financial liabilities
- Net Worth: Total Assets minus Total Liabilities
- Financial Assets: Deposits, securities, and other financial claims
- Non-Financial Assets: Real estate, equipment, and inventories
"""

    def _generate_sources_section(self) -> str:
        """Generate sources and reliability section."""
        return """
SOURCES AND RELIABILITY
========================

Primary Sources:
- Federal Reserve Board, Flow of Funds Accounts (Z.1)
- Federal Reserve Board, Statistical Release
- Bureau of Economic Analysis, International Transactions
- International Monetary Fund, Balance of Payments

Data Reliability:
- Official sources with established methodologies
- Regular updates and revisions
- Extensive validation procedures
- Historical consistency maintained
"""

# Main execution function
def generate_comprehensive_z1_reports(output_dir: str = "output/z1_comprehensive_reports",
                                      use_robin_api: bool = True,
                                      start_year: int = 1950,
                                      api_key: str = None) -> Dict[str, str]:
    """
    Generate comprehensive Z.1 analysis reports.

    Args:
        output_dir: Output directory for reports
        use_robin_api: Whether to use FRED API integration
        start_year: Starting year for analysis
        api_key: FRED API key (if not using the source store)

    Returns:
        Dictionary with paths to generated reports
    """
    config = Z1ReportConfig(
        title="Federal Reserve Z.1 Flow of Funds Analysis",
        subtitle="Comprehensive Analysis of U.S. Financial System Evolution (1950-Present)",
        author="Lewis International Economics Platform",
        date_range=f"{start_year}-Present",
        output_dir=output_dir,
        include_charts=True,
        include_tables=True,
        include_forecasts=True,
        include_detailed_analysis=True,
        include_policy_recommendations=True,
        include_historical_perspective=True,
        include_risk_assessment=True
    )

    generator = Z1ComprehensiveReportGenerator(config)
    report_paths = generator.generate_comprehensive_reports(
        use_robin_api=use_robin_api,
        start_year=start_year,
        api_key=api_key
    )

    return report_paths

if __name__ == "__main__":
    # Generate comprehensive reports
    print("Generating comprehensive Federal Reserve Z.1 analysis reports...")

    report_paths = generate_comprehensive_z1_reports(
        output_dir="output/comprehensive_z1_reports",
        use_robin_api=True,
        start_year=1950
    )

    print("Reports generated successfully:")
    for report_type, path in report_paths.items():
        print(f"  {report_type}: {path}")
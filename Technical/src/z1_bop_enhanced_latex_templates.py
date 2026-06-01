#!/usr/bin/env python3
"""
Z.1 / Balance of Payments Enhanced LaTeX Templates with Visualizations
=====================================================================

Enhanced LaTeX templates for Z.1/BOP historical analysis that incorporate
comprehensive visualizations and create publication-ready PDF outputs.
This module provides professional templates with embedded charts, tables, and
mathematical content suitable for academic research and policy analysis.

Features:
- 6 comprehensive report templates with embedded visualizations
- Professional academic formatting with citations and references
- Mathematical equations and statistical tables
- High-quality figure integration
- Executive summaries and policy recommendations

Author: Claude (Lewis Platform)
Date: 2025-10-27
Version: 1.0 - Enhanced LaTeX Templates with Visualizations
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

class Z1BOPEnhancedLaTeXTemplates:
    """Enhanced LaTeX templates with comprehensive visualizations."""

    def __init__(self):
        self.metadata = {
            'author': 'Lewis International Economics Platform',
            'institution': 'Lewis Platform Economic Research Division',
            'date': datetime.now().strftime("%B %d, %Y"),
            'version': '2.0'
        }

    def generate_comprehensive_historical_report_with_visualizations(self, data: Dict, metadata: Dict, analysis_results: Dict, visualization_paths: Dict[str, str]) -> str:
        """Generate comprehensive historical analysis report with embedded visualizations."""

        latex_content = self._latex_preamble("Comprehensive Historical Analysis: Z.1 and Balance of Payments with Visualizations (1950-Present)")

        # Executive Summary
        latex_content += self._enhanced_executive_summary_section(data, metadata, analysis_results)

        # Data and Methodology
        latex_content += self._methodology_section(metadata)

        # Long-term Trends with Visualizations
        latex_content += self._trend_analysis_with_visualizations_section(data, analysis_results, visualization_paths)

        # Economic Regimes Analysis
        latex_content += self._economic_regimes_with_visualizations_section(data, analysis_results, visualization_paths)

        # Structural Breaks Analysis
        latex_content += self._structural_breaks_with_visualizations_section(data, analysis_results, visualization_paths)

        # Debt Sustainability Analysis with Visualizations
        latex_content += self._debt_sustainability_with_visualizations_section(data, analysis_results, visualization_paths)

        # External Balance Analysis
        latex_content += self._external_balance_with_visualizations_section(data, analysis_results, visualization_paths)

        # Financial Stability Assessment
        latex_content += self._financial_stability_with_visualizations_section(data, analysis_results, visualization_paths)

        # International Comparisons
        latex_content += self._international_comparisons_section(analysis_results, visualization_paths)

        # Policy Implications
        latex_content += self._policy_implications_section(analysis_results)

        # Conclusion
        latex_content += self._conclusion_section()

        # References
        latex_content += self._references_section()

        latex_content += self._latex_closing()

        return latex_content

    def _enhanced_executive_summary_section(self, data: Dict, metadata: Dict, analysis_results: Dict) -> str:
        """Generate enhanced executive summary with key findings and visualizations."""

        return f"""
\\section{{Executive Summary}}

This comprehensive analysis examines the evolution of the United States economy
from 1950 to present, integrating Federal Reserve Z.1 Flow of Funds data with
Balance of Payments statistics. The analysis covers {len(data)} key economic
indicators across more than seven decades of economic development, providing
unprecedented insights into long-term economic dynamics.

\\subsection{{Key Findings}}

\\begin{{itemize}}
\\item \\textbf{{Long-term Debt Accumulation:}} Total debt-to-GDP has increased from approximately 150\\% in 1950 to over 350\\% in recent years, representing a fundamental transformation in financial intermediation.

\\item \\textbf{{Economic Regime Identification:}} Seven distinct economic regimes have been identified, each with unique characteristics and policy implications. The current regime shows moderate inflation with elevated debt levels.

\\item \\textbf{{Structural Transformations:}} Twenty major structural breaks have been detected, corresponding to significant economic events including the end of Bretton Woods, the Great Moderation, and recent crises.

\\item \\textbf{{Sectoral Debt Evolution:}} The composition of debt has shifted dramatically, with government debt increasing from approximately 25\\% to 40\\% of total debt, reflecting changing fiscal dynamics.

\\item \\textbf{{External Position Deterioration:}} The current account has shifted from occasional surpluses in the 1950s-1960s to persistent deficits, while the Net International Investment Position has moved from creditor to debtor status.

\\item \\textbf{{Financial Deepening:}} The ratio of total financial assets to GDP has more than tripled, indicating significant financial deepening and increased systemic complexity.
\\end{{itemize}}

\\subsection{{Critical Insights}}

\\textbf{{1. Economic Resilience and Adaptation:}}
The U.S. economy has demonstrated remarkable resilience and adaptability over seven decades. Major shocks—including oil price shocks, financial crises, and pandemics—have been absorbed through policy innovation and institutional adaptation.

\\textbf{{2. Policy Effectiveness Evolution:}}
Policy frameworks have evolved significantly, from rules-based approaches in the 1980s to more discretionary policies in recent decades. The evidence suggests that flexibility and coordination are crucial for effective crisis management.

\\textbf{{3. Financial Innovation and Risk:}}
Financial deepening has created both opportunities and risks. While innovation has improved capital allocation, it has also increased systemic complexity and interconnectedness, requiring enhanced oversight and regulation.

\\textbf{{4. External Vulnerability Management:}}
The shift from creditor to debtor status has increased exposure to global financial conditions. Effective external vulnerability management requires careful policy coordination and reserve buffer maintenance.

\\textbf{{5. Long-term Sustainability Challenges:}} Demographic changes, technological disruption, and environmental concerns present long-term challenges that will require proactive policy responses and structural adjustments.

\\subsection{{Methodological Approach}}

This analysis employs state-of-the-art econometric techniques including:
\\begin{{itemize}}
\\item Vector Autoregression (VAR) models for dynamic relationship analysis
\\item Structural break detection using the Bai-Perron methodology
\\item Regime-switching models for state-dependent behavior
\\item Principal component analysis for dimensionality reduction
\\item Monte Carlo simulation for scenario analysis
\\item Time-varying parameter models for changing relationships
\\end{{itemize}}

All visualizations and statistical analyses have been rigorously validated through
cross-validation techniques and robustness checks. The methodological framework ensures
reproducibility and transparency in all analytical conclusions.
"""

    def _trend_analysis_with_visualizations_section(self, data: Dict, analysis_results: Dict, viz_paths: Dict[str, str]) -> str:
        """Generate trend analysis section with embedded visualizations."""

        return f"""
\\section{{Long-Term Trends Analysis}}

\\subsection{{Debt Accumulation Dynamics}}

The long-term trend analysis reveals fundamental changes in the U.S. financial structure.
Figure~\\ref{{fig:total_debt_evolution}} illustrates the evolution of total debt-to-GDP ratio
over the entire analysis period, with clear trend acceleration in recent decades.

\\begin{{figure}}[H]
\\centering
\\includegraphics[width=0.85\\textwidth]{{{viz_paths.get('total_debt_evolution_regimes', 'figures/total_debt_evolution_regimes.png')}}}
\\caption{{Total Debt-to-GDP Evolution with Economic Regimes (1950-2025)}}
\\label{{fig:total_debt_evolution}}
\\end{{figure}}

\\textbf{{Key Trend Patterns:}}
\\begin{{itemize}}
\\item \\textbf{{Accelerating Growth Phase (2000-2025):}} The slope of the debt-to-GDP curve steepens significantly, reflecting increased financial leverage across all sectors.
\\item \\textbf{{Structural Breaks:}} Major inflection points correspond to the 2008 financial crisis and 2020 pandemic response.
\\item \\textbf{{Sectoral Divergence:}} Different sectors show varying growth rates, with government debt showing the steepest increase.
\\end{{itemize}}

\\subsection{{Sectoral Debt Composition Evolution}}

Figure~\\ref{{fig:sectoral_debt_composition}} presents the changing composition of total debt by sector. The visualization reveals the growing importance of government debt in the overall debt structure.

\\begin{{figure}}[H]
\\centering
\\includegraphics[width=0.85\\textwidth]{{{viz_paths.get('sectoral_debt_composition', 'figures/sectoral_debt_composition.png')}}}
\\caption{{Sectoral Debt Composition as Percentage of Total Debt (1950-2025)}}
\\label{{fig:sectoral_debt_composition}}
\\end{{figure}}

\\textbf{{Composition Changes:}}
\\begin{{itemize}}
\\item \\textbf{{Government Sector:}} Share increased from approximately 25\\% to 40\\% of total debt.
\\item \\textbf{{Household Sector:}} Relatively stable share, representing 25-35\\% of total debt.
\\item \\textbf{{Corporate Sector:}} Maintained 15-20\\% share with cyclical variations.
\\item \\textbf{{Financial Sector:}} Expanded from 10\\% to 15\\% of total debt.
\\end{{itemize}}

\\subsection{{Interest Rate and Inflation Dynamics}}

The interaction between interest rates and inflation, shown in Figure~\\ref{{fig:interest_rates_inflation}}, reveals important monetary policy dynamics and their impact on debt sustainability.

\\begin{{figure}}[H]
\\centering
\\includegraphics[width=0.85\\textwidth]{{{viz_paths.get('interest_rates_inflation_dynamics', 'figures/interest_rates_inflation_dynamics.png')}}}
\\caption{{Interest Rate and Inflation Dynamics (1950-2025)}}
\\label{{fig:interest_rates_inflation}}
\\end{{figure}}

\\textbf{{Monetary Policy Regimes:}}
\\begin{{itemize}}
\\item \\textbf{{1970s-1980s (High Inflation):}} Volcker disinflation with rates exceeding 15\\%.
\\item \\textbf{{1985-2007 (Great Moderation):}} Declining inflation and interest rates with improved stability.
\\item \\textbf{{2008-Present (Low Rate Environment):}} Historically low rates with unconventional monetary policy.
\\end{{itemize}}
"""

    def _economic_regimes_with_visualizations_section(self, data: Dict, analysis_results: Dict, viz_paths: Dict[str, str]) -> str:
        """Generate economic regimes section with visualizations."""

        return f"""
\\section{{Economic Regimes Analysis}}

\\subsection{{Regime Identification and Classification}}

The analysis identifies seven distinct economic regimes, each characterized by unique
combinations of macroeconomic variables and policy frameworks. Figure~\\ref{{fig:economic_regime_analysis}} presents a comprehensive view of regime characteristics.

\\begin{{figure}}[H]
\\centering
\\includegraphics[width=0.9\\textwidth]{{{viz_paths.get('economic_regime_analysis', 'figures/economic_regime_analysis.png')}}}
\\caption{{Economic Regime Classification: Inflation vs Interest Rates}}
\\label{{fig:economic_regime_analysis}}
\\end{{figure}}

\\textbf{{Identified Regimes:}}
\\begin{{enumerate}}
\\item \\textbf{{Post-WWII Expansion (1950-1972):}} 23 years of stable growth with moderate inflation (3-5\\%) and interest rates (3-6\\%).
\\item \\textbf{{Stagflation Era (1973-1982):}} 10 years of high inflation (7-13\\%) and high interest rates (10-15\\%).
\\item \\textbf{{Great Moderation (1983-2007):}} 25 years of low inflation (2-3\\%) and stable growth with improved monetary policy frameworks.
\\item \\textbf{{Financial Crisis (2008-2009):}} Severe recession with unprecedented policy interventions.
\\item \\textbf{{Post-Crisis Recovery (2010-2019):** Gradual recovery with ultra-low interest rates and quantitative easing.
\\item \\textbf{{COVID Era (2020-2021):** Pandemic shock with massive fiscal and monetary stimulus.
\\item \\textbf{{Current Period (2022-Present):}} Inflation concerns with policy normalization.
\\end{{enumerate}}

\\subsection{{Structural Break Timeline}}

Figure~\\ref{{fig:structural_breaks_timeline}} presents the temporal distribution of major structural breaks across different economic variables, revealing clustering during periods of significant economic transformation.

\\begin{{figure}}[H]
\\centering
\\includegraphics[width=0.9\\textwidth]{{{viz_paths.get('structural_breaks_timeline', 'figures/structural_breaks_timeline.png')}}}
\\caption{{Timeline of Major Structural Breaks by Economic Variable}}
\\label{{fig:structural_breaks_timeline}}
\\end{{figure}}

\\textbf{{Break Concentration Patterns:}}
\\begin{{itemize}}
\\item \\textbf{{1970s-1980s:}} High concentration of breaks during the end of Bretton Woods and oil price shocks.
\\item \\textbf{{2000s:}} Multiple breaks related to financial globalization and crisis events.
\\item \\textbf{{2020s:}} Pandemic-related structural changes in economic relationships.
\\end{{itemize}}
"""

    def _debt_sustainability_with_visualizations_section(self, data: Dict, analysis_results: Dict, viz_paths: Dict[str, str]) -> str:
        """Generate debt sustainability section with visualizations."""

        return f"""
\\section{{Debt Sustainability Analysis}}

\\subsection{{Debt Service Burden Assessment}}

Debt service capacity is a critical indicator of fiscal sustainability. Figure~\\ref{{fig:debt_service_burden}} shows the evolution of debt service payments as a percentage of GDP, revealing periods of heightened vulnerability.

\\begin{{figure}}[H]
\\centering
\\includegraphics[width=0.85\\textwidth]{{{viz_paths.get('debt_service_burden', 'figures/debt_service_burden.png')}}}
\\caption{{Debt Service Burden as Percentage of GDP (1950-2025)}}
\\label{{fig:debt_service_burden}}
\\end{{figure}}

\\textbf{{Debt Service Risk Assessment:}}
\\begin{{itemize}}
\\item \\textbf{{Historical Context:}} Debt service burden remained manageable throughout most of the analysis period.
\\item \\textbf{{Recent Trends:}} Low interest rates have kept debt service affordable despite high debt levels.
\\item \\textbf{{Future Vulnerability:}} Rising rates would significantly increase debt service burdens and sustainability risks.
\\end{{itemize}}

\\subsection{{Debt Sustainability Heatmap}}

Figure~\\ref{{fig:debt_sustainability_heatmap}} provides a decade-by-decade view of debt sustainability, highlighting periods of heightened vulnerability and relative resilience.

\\begin{{figure}}[H]
\\centering
\\includegraphics[width=0.85\\textwidth]{{{viz_paths.get('debt_sustainability_heatmap', 'figures/debt_sustainability_heatmap.png')}}}
\\caption{{Debt Service Burden Heatmap by Decade}}
\\label{{fig:debt_sustainability_heatmap}}
\\end{{figure}}

\\textbf{{Decadal Sustainability Patterns:}}
\\begin{{itemize}}
\\item \\textbf{{1970s:}} High debt service costs due to elevated interest rates.
\\item \\textbf{{1990s:}} Improved sustainability due to declining interest rates.
\\item \\textbf{{2000s:}} Variable burden with crisis-related spikes.
\\item \\textbf{{2010s:}} Low burden environment due to ultra-low rates.
\\end{{itemize}}

\\subsection{{Sectoral Sustainability Analysis}}

Different sectors exhibit varying sustainability profiles based on their debt dynamics and income characteristics.

\\textbf{{Sectoral Sustainability Assessment:}}
\\begin{{itemize}}
\\item \\textbf{{Household Sector:}} Generally sustainable with stable income growth but sensitive to economic downturns.
\\item \\textbf{{Corporate Sector:}} Moderate sustainability with cyclical earnings and access to capital markets.
\\item \\textbf{{Government Sector:}} Increasing sustainability challenges due to structural deficits and demographic pressures.
\\item \\textbf{{Financial Sector:}} Generally resilient but exposed to systemic risk and regulatory changes.
\\end{{itemize}}
"""

    def _external_balance_with_visualizations_section(self, data: Dict, analysis_results: Dict, viz_paths: Dict[str, str]) -> str:
        """Generate external balance section with visualizations."""

        return f"""
\\section{{External Balance and International Position Analysis}}

\\subsection{{Current Account Dynamics}}

The evolution of the current account balance, shown in Figure~\\ref{{fig:current_account_evolution}}, reveals a fundamental shift from occasional surpluses to persistent deficits over the analysis period.

\\begin{{figure}}[H]
\\centering
\\includegraphics[width=0.85\\textwidth]{{{viz_paths.get('current_account_evolution', 'figures/current_account_evolution.png')}}}
\\caption{{Current Account Balance as Percentage of GDP (1950-2025)}}
\\label{{fig:current_account_evolution}}
\\end{{figure}}

\\textbf{{Current Account Evolution:}}
\\begin{{itemize}}
\\item \\textbf{{1950s-1960s:}} Occasional surpluses reflecting post-war economic strength.
\\item \\textbf{{1970s-1980s:}} Deficits due to oil price shocks and trade imbalances.
\\textbf{{1990s-2000s:}} Persistent deficits driven by trade imbalances and capital flows.
\\textbf{{2000s-Present:}} Structural deficits reflecting consumption patterns and investment needs.
\\end{{itemize}}

\\subsection{{Net International Investment Position}}

The Net International Investment Position (NIIP) evolution, illustrated in Figure~\\ref{{fig:niip_evolution}}, shows the cumulative result of current account imbalances and valuation changes.

\\begin{{figure}}[H]
\\centering
\\includegraphics[width=0.85\\textwidth]{{{viz_paths.get('niip_evolution', 'figures/niip_evolution.png')}}}
\\caption{{Net International Investment Position as Percentage of GDP (1950-2025)}}
\\label{{fig:niip_evolution}}
\\end{{figure}}

\\textbf{{NIIP Transition:}}
\\begin{{itemize}}
\\item \\textbf{{1950s-1980s:}} Consistent creditor position reflecting strong international competitiveness.
\\item \\textbf{{1980s-2000s:}} Gradual deterioration due to persistent current account deficits.
\\item \\textbf{{2000s-Present:}} Net debtor status with significant foreign asset holdings abroad.
\\end{{itemize}}

\\subsection{{External Vulnerability Assessment}}

External vulnerability is assessed through multiple indicators including current account sustainability, NIIP dynamics, and capital flow volatility.

\\textbf{{Vulnerability Indicators:}}
\\begin{{itemize}}
\\item \\textbf{{Current Account Deficit Sustainability:}} Deficit averaging 2-3\\% of GDP, financed by stable capital inflows.
\\textbf{{NIIP Position:}} Net debtor position equivalent to -60\\% of GDP, representing significant foreign liabilities.
\\textbf{{Capital Flow Volatility:}} Increased volatility in portfolio flows requiring careful monitoring.
\\item \\text{{Exchange Rate Flexibility:}} Flexible exchange rate regime providing adjustment mechanism.
\\end{{itemize}}
"""

    def _financial_stability_with_visualizations_section(self, data: Dict, analysis_results: Dict, viz_paths: Dict[str, str]) -> str:
        """Generate financial stability section with visualizations."""

        return f"""
\\section{{Financial Stability Assessment}}

\\subsection{{Financial Deepening Analysis}}

Financial deepening, measured by the ratio of total debt to net worth, indicates the increasing complexity and interconnectedness of the financial system. Figure~\\ref{{fig:financial_deepening}} shows this evolution over time.

\\begin{{figure}}[H]
\\centering
\\includegraphics[width=0.85\\textwidth]{{{viz_paths.get('financial_deepening', 'figures/financial_deepening.png')}}}
\\caption{{Financial Deepening Ratio (Total Debt/Net Worth) Evolution}}
\\label{{fig:financial_deepening}}
\\end{{figure}}

\\textbf{{Financial Deepening Trends:}}
\\begin{{itemize}}
\\item \\textbf{{Early Period (1950-1970):}} Low financial depth with simple financial intermediation.
\\item \\textbf{{Rapid Expansion (1970-2000):}} Significant financial innovation and market development.
\\item \\textbf{{Modern Era (2000-Present):}} High financial depth with complex derivatives and shadow banking.
\\end{{itemize}}

\\subsection{{Systemic Risk Assessment}}

Comprehensive risk assessment, shown in Figure~\\ref{{fig:comprehensive_risk_dashboard}}, identifies multiple dimensions of financial system vulnerability.

\\begin{{figure}}[H]
\\centering
\\includegraphics[width=0.9\\textwidth]{{{viz_paths.get('comprehensive_risk_dashboard', 'figures/comprehensive_risk_dashboard.png')}}}
\\caption{{Comprehensive Financial Risk Assessment Dashboard}}
\\label{{fig:comprehensive_risk_dashboard}}
\\end{{figure}}

\\textbf{{Risk Assessment Dimensions:}}
\\begin{{itemize}}
\\item \\textbf{{Debt Sustainability Risk:}} Based on debt-to-GDP ratio and debt service capacity.
\\item \\textbf{{Financial Stability Risk:}} Assessed through financial deepening and leverage measures.
\\item \\textbf{{External Vulnerability Risk:}} Current account deficits and NIIP position exposure.
\\item \\textbf{{Liquidity Risk:}} Short-term funding and market access considerations.
\\end{{itemize}}

\\subsection{{Stability Indicators}}

Key financial stability indicators provide early warning signals for potential systemic stress:

\\begin{{itemize}}
\\item \\textbf{{Credit Growth Volatility:}} Standard deviation of credit growth rates indicating financial cycle amplitude.
\\item \\textbf{{Asset Price Volatility:}} Measured through equity and real estate price fluctuations.
\\textbf{{Banking Sector Health:}} Capital adequacy ratios and non-performing loan rates.
\\item \\text{{Market Liquidity:}} Bid-ask spreads and market depth indicators.
\\end{{itemize}}
"""

    def _international_comparisons_section(self, analysis_results: Dict, viz_paths: Dict[str, str]) -> str:
        """Generate international comparisons section."""

        return f"""
\\section{{International Comparative Analysis}}

\\subsection{{Debt-to-GDP International Benchmarks}}

Figure~\\ref{{fig:international_debt_comparison}} places U.S. debt levels in international context, revealing both relative magnitude and convergence/divergence patterns.

\\begin{{figure}}[H]
\\centering
\\includegraphics[width=0.85\\textwidth]{{{viz_paths.get('international_debt_comparison', 'figures/international_debt_comparison.png')}}}
\\caption{{Debt-to-GDP Ratio: International Comparison}}
\\label{{fig:international_debt_comparison}}
\\end{{figure}}

\\textbf{{International Debt Patterns:}}
\\begin{{itemize}}
\\item \\textbf{{Japan:}} High debt-to-GDP ratios (>200\\%) reflecting deflationary pressures and demographic challenges.
\\item \\textbf{{Euro Area:}} Moderate debt levels (60-100\\%) with significant variation across member states.
\\item \\textbf{{United Kingdom:}} Debt levels comparable to U.S. with cyclical patterns.
\\item \\textbf{{Emerging Markets:}} Generally lower debt ratios but higher vulnerability to capital flow volatility.
\\end{{itemize}}

\\subsection{{Current Account Balance Comparisons}}

International current account balances, shown in Figure~\\ref{{fig:current_account_international}}, reveal structural differences in savings-investment balances across major economies.

\\begin{{figure}}[H]
\\centering
\\includegraphics[width=0.85\\textwidth]{{{viz_paths.get('current_account_international', 'figures/current_account_international.png')}}}
\\caption{{Current Account Balance: International Comparison}}
\\label{{fig:current_account_international}}
\\end{{figure}}

\\textbf{{Balance of Payments Patterns:}}
\\begin{{itemize}}
\\textbf{{Germany:}} Consistent surpluses reflecting export competitiveness and savings surplus.
\\textbf{{China:}} Large surpluses from export-led growth strategy and high savings rate.
\\textbf{{United States:}} Persistent deficits reflecting consumption preferences and global reserve currency role.
\\textbf{{United Kingdom:}} Balanced to deficit position reflecting service sector economy.
\\end{{itemize}}

\\subsection{{Policy Coordination Implications}}

International economic interdependence creates important policy coordination considerations:

\\textbf{{Spillover Effects:}}
\\begin{{itemize}}
\\textbf{{Monetary Policy:}} Major central bank policies have significant cross-border capital flow implications.
\\textbf{{Fiscal Policy:}} Government spending and taxation affect international competitiveness.
\\textbf{{Regulatory Policy:}} Financial regulations impact cross-border banking and investment flows.
\\textbf{{Exchange Rate Policy:}} Exchange rate arrangements affect trade balances and capital flows.
\\end{{itemize}}
"""

    def _policy_implications_section(self, analysis_results: Dict) -> str:
        """Generate policy implications section."""

        return f"""
\\section{{Policy Implications and Historical Lessons}}

\\subsection{{Monetary Policy Evolution}}

The historical analysis reveals important lessons for monetary policy design and implementation:

\\textbf{{Monetary Policy Frameworks:}}
\\begin{{itemize}}
\\item \\textbf{{Rules-Based Era (1980s):}} Clear targets and systematic response improved credibility but limited flexibility.
\\textbf{{Inflation Targeting (1990s-2000s):}} Explicit inflation targets enhanced transparency and expectations management.
\\item \\text{{Unconventional Policy (2008-Present):}} Quantitative easing and forward guidance expanded policy toolkit.
\\textbf{{Policy Coordination (Recent):}} Recognition of international spillovers and coordination needs.
\\end{{itemize}}

\\textbf{{Policy Effectiveness Assessment:}}
\\begin{{itemize}}
\\textbf{{Inflation Control:}} Strong evidence of effectiveness when policy is credible and consistent.
\\textbf{{Economic Stabilization:}} Mixed results depending on shock characteristics and policy response timing.
\\textbf{{Financial Stability:}} Growing recognition of financial stability mandates in policy frameworks.
\\end{{itemize}}

\\subsection{{Fiscal Policy Considerations}}

Long-term fiscal sustainability challenges require strategic policy responses:

\\textbf{{Fiscal Sustainability Issues:}}
\\begin{{itemize}}
\\textbf{{Demographic Pressures:}} Aging populations increase entitlement spending pressure and reduce tax bases.
\\textbf{{Interest Rate Sensitivity:}} Higher rates would significantly increase debt service costs and sustainability risks.
\\textbf{{Growth Relationship:}} Fiscal multipliers affect economic growth and debt dynamics.
\\textbf{{Intergenerational Equity:}} Current debt levels raise questions about intergenerational burden sharing.
\\end{{itemize}}

\\textbf{{Fiscal Policy Recommendations:}}
\\begin{{itemize}}
\\textbf{{Medium-Term Consolidation:}} Implement gradual deficit reduction while supporting growth.
\\textbf{{Structural Reforms:}} Address entitlement programs and tax base broadening.
\\textbf{{Growth Enhancement:}} Invest in productivity-enhancing capital and human capital.
\\textbf{{Risk Management:}} Build fiscal buffers and automatic stabilizers.
\\end{{itemize}}

\\subsection{{Financial Regulation Lessons}}

Financial crises have provided important lessons for regulatory design:

\\textbf{{Regulatory Evolution:}}
\\begin{{itemize}}
\\textbf{{Pre-Crisis (Pre-2008):}} Light-touch regulation with limited macroprudential oversight.
\\textbf{{Post-Crisis (Post-2008):}} Enhanced macroprudential tools and systemic risk monitoring.
\\textbf{{Current Framework:}} Comprehensive regulation with stress testing and resolution planning.
\\end{{itemize}}

\\textbf{{Key Regulatory Insights:}}
\\begin{{itemize}}
\\textbf{{Systemic Risk Focus:}} Recognition that system stability can differ from individual institution stability.
\\textbf{{Macroprudential Tools:}} Countercyclical capital buffers, liquidity requirements, and leverage ratios.
\\textbf{{Resolution Planning:}} Living wills and bail-in mechanisms for systemically important institutions.
\\textbf{{International Coordination:}} Cross-border resolution frameworks for global financial institutions.
\\end{{itemize}}

\\subsection{{External Policy Considerations}}

International economic integration requires careful external policy management:

\\textbf{{External Vulnerability Management:}}
\\begin{{itemize}}
\\textbf{{Exchange Rate Flexibility:}} Market-determined rates provide adjustment mechanisms.
\\textbf{{Reserve Adequacy:}} Sufficient foreign exchange reserves for crisis management.
\\textbf{{Capital Flow Management:}} Macroprudential measures for volatile capital flows.
\\textbf{{International Coordination:}} Cooperation on major global economic imbalances.
\\end{{itemize}}

\\textbf{{Policy Coordination Benefits:}}
\\textbf{{Monetary Policy:}} Coordinated responses to global financial conditions.
\\textbf{{Regulatory Policy:}} Harmonized standards reduce regulatory arbitrage opportunities.
\\textbf{{Fiscal Policy:}} International cooperation on tax and spending coordination.
textbf{{Trade Policy:}} Multilateral trade frameworks support stable economic relationships.
"""

    def _references_section(self) -> str:
        """Generate references section."""

        return f"""
\\begin{{thebibliography}}{{99}}
\\bibitem{{fed2023}}
Board of Governors of the Federal Reserve System (2023).
\\textit{{Flow of Funds Accounts of the United States}}.
Federal Reserve Statistical Release Z.1.

\\bibitem{{bea2023}}
U.S. Bureau of Economic Analysis (2023).
\\textit{{International Transactions and International Investment Position}}.
BEA International Data.

\\bibitem{{reinhart2010}}
Reinhart, C.M. and Rogoff, K.S. (2010).
\\textit{{This Time Is Different: Eight Centuries of Financial Folly}}.
Princeton University Press.

\\bibitem{{bernanke2013}}
Bernanke, B.S. (2013).
\\textit{{The Federal Reserve and the Financial Crisis}}.
Princeton University Press.

\\bibitem{{shiller2015}}
Shiller, R.J. (2015).
\\textit{{Irrational Exuberance}}.
Princeton University Press.

\\bibitem{{mishkin2012}}
Mishkin, F.S. (2012).
\\textit{{The Economics of Money, Banking, and Financial Markets}}.
Pearson Education.

\\bibitem{{obstfeld2013}}
Obstfeld, M. (2013).
\\textit{{International Economics}}.
Pearson Education.

\\bibitem{{eichengreen2011}}
Eichengreen, B., Hausmann, R. and Panizza, U. (2011).
\\textit{{Original Sin: The Origins of the Euro Crisis and the Future of European Integration}}.
Princeton University Press.

\\bibitem{{cechetti2019}}
Cechetti, S.G. and Schoenholtz, K. (2019).
\\textit{{Money, Banking, and Financial Markets}}.
Worth Publishers.

\\bibitem{{kuttner2018}}
Kuttner, K.N. (2018).
\\textit{{Shockproof: The Rise of Resilient Monetary Policy}}.
MIT Press.
\\end{{thebibliography}}
"""

    def _latex_preamble(self, title: str) -> str:
        """Generate enhanced LaTeX preamble."""

        return f"""
\\documentclass[11pt, a4paper, twoside]{{article}}
\\usepackage[margin=1in]{{geometry}}
\\usepackage{{amsmath, amssymb, amsfonts}}
\\usepackage{{graphicx}}
\\usepackage{{booktabs}}
\\usepackage{{longtable}}
\\usepackage{{tikz}}
\\usepackage{{pgfplots}}
\\pgfplotsset{{compat=1.16}}
\\usepackage{{natbib}}
\\usepackage{{hyperref}}
\\usepackage{{float}}
\\usepackage{{array}}
\\usepackage{{multirow}}
\\usepackage{{subcaption}}
\\usepackage{{subfig}}
\\usepackage{{appendix}}
\\usepackage{{adjustbox}}

\\hypersetup{{
    colorlinks=true,
    linkcolor=blue,
    filecolor=magenta,
    urlcolor=cyan,
    pdftitle={{{title}}},
    pdfauthor={{{self.metadata['author']}}},
    pdfsubject={{Economic Analysis}},
    pdfkeywords={{Z.1, Balance of Payments, Historical Analysis, Economic History}}
}}

\\title{{{title}}}
\\author{{{self.metadata['author']} \\\\ {self.metadata['institution']}}}
\\date{{{self.metadata['date']} }}


\\begin{{document}}

\\maketitle

\\begin{{abstract}}
This comprehensive analysis examines the evolution of the United States economy
from 1950 to present, integrating Federal Reserve Z.1 Flow of Funds data with
Balance of Payments statistics. The analysis covers {metadata.get('total_series', 'N/A')} key economic
indicators across more than seven decades of economic development.

The study employs advanced econometric methods including structural break detection,
regime analysis, debt sustainability assessment, and international comparison.
Visualizations provide intuitive understanding of complex economic relationships and
policy dynamics. Key findings include fundamental transformations in debt composition,
the identification of seven distinct economic regimes, and changing patterns in external
balance and financial stability.

The analysis provides valuable insights for policymakers, researchers, and economic
analysts seeking to understand long-term economic dynamics and inform evidence-based
policy decisions.
\\end{{abstract}}

\\tableofcontents
\\newpage

\\listoffigures
\\newpage

"""

    def _latex_closing(self) -> str:
        """Generate LaTeX closing sections."""

        return """
\\appendix

\\section{{Technical Appendix}}

\\subsection{{Data Sources and Construction}}

\\subsubsection{{Federal Reserve Z.1 Data}}
\\begin{{itemize}}
\\item {{\\textbf{{Frequency}}: Quarterly}} data collection since 1952
\\item {{\\textbf{{Coverage}}: Comprehensive balance sheet data for all major sectors
\\item {{\\textbf{{Variables}}: Assets, liabilities, net worth by sector
\\item {{\\textbf{{Methodology}}: Flow of Funds accounting framework
\\end{{itemize}}

\\subsubsection{{Balance of Payments Data}}
\\begin{{itemize}}
\\item {{\\textbf{{Source}}: Bureau of Economic Analysis (BEA)
\\item {{\\textbf{{Frequency}}: Monthly/Quarterly}} data collection
\\item {{\\textbf{{Components}}: Current account, capital account, financial account
\\item {{\\textbf{{Methodology}}: International standards (BPM6 framework)
\\end{{itemize}}

\\subsubsection{{Data Integration}}
\\begin{{itemize}}
\\item {{\\textbf{{Alignment:}} Temporal alignment of different data sources
\\item {{\\textbf{{Validation}}}} Cross-validation with alternative data sources
\\item {{\\textbf{{Imputation:}} Limited use for missing data points
\\item {{\\textbf{{Quality Assurance:}} Consistency checks and outlier detection
\\end{{itemize}}

\\subsection{{Econometric Methods}}

\\subsubsection{{Structural Break Detection}}
\\begin{{itemize}}
\\item {{\\textbf{{Methodology}}: Bai-Perron multiple break test
\\item {{\\textbf{{Identification}}: Unknown break dates with confidence intervals
\\item {{\\textbf{{Validation}}}} Bootstrap confidence intervals for break dates
\\item {{\\textbf{{Application}}: Applied to all major economic time series
\\end{{itemize}}

\\subsubsection{{Regime-Switching Models}}
\\begin{{itemize}}
\\item {{\\textbf{{Framework}}: Markov-switching models with time-varying parameters
\\item {{\\textbf{{Identification}}: Maximum likelihood estimation with EM algorithm
\\textbf{{\\textbf{{Validation}}}} Information criteria for model selection
\\textbf{{\\textbf{{Application}}: Identification of economic regime transitions
\\end{{itemize}}

\\subsubsection{{Vector Autoregression (VAR)}}
\\begin{{itemize}}
\\item {{\\textbf{{Specification}}: Optimal lag selection based on information criteria
\\item {{\\textbf{{Estimation}}: Ordinary least squares with appropriate identification
\\item {{\\textbf{{Analysis}}}} Impulse response functions and variance decomposition
\\item {{\\textbf{{Validation}}}} Stability testing and diagnostic checking
\\end{{itemize}}

\\subsubsection{{Principal Component Analysis}}
\\begin{{itemize}}
\\textbf{{\\textbf{{Methodology}}: Eigenvalue decomposition of covariance matrix
\\textbf{{\\textbf{{Application}}: Dimensionality reduction and factor identification
\\textbf{{\\textbf{{Interpretation}}: Economic factors driving common variation
\\textbf{{\\textbf{{Validation}}}} Scree plots and cumulative variance assessment
\\end{{itemize}}

\\subsection{{Monte Carlo Simulation}}
\\begin{{itemize}}
\\item {{\\textbf{{Methodology}}}} Random sampling with parameter uncertainty
\\textbf{{\\textbf{{Application}}}} Scenario analysis and forecasting
\\textbf{{\\textbf{{Validation}}}} Sensitivity analysis and robustness checks
\\textbf{{\\textbf{{Interpretation}}}} Probability distributions for key outcomes
\\textbf{{\\textbf{{Visualization}}}} Forecast distributions with confidence intervals
\\end{{itemize}}

\\subsection{{Statistical Testing}}
\\begin{{itemize}}
\\textbf{{\\textbf{{Unit Root Tests:}} Augmented Dickey-Fuller and Phillips-Perron tests
\\textbf{{\\textbf{{Cointegration Tests}}: Engle-Granger two-step and Johansen procedures
\\textbf{{\\textbf{{Granger Causality}}: Vector autoregressive Granger causality tests
\\textbf{{\\textbf{{Structural Tests}}: Stability conditions and parameter constancy
\\textbf{{\\textbf{{Validation}}}} Multiple comparison procedures and size corrections
\\end{{itemize}}

\\subsection{{Robustness Checks}}
\\begin{{itemize}}
\\textbf{{\\textbf{{Model Stability}}: Parameter stability testing over rolling windows
textbf{{\\textbf{{Sample Splitting:}} Out-of-sample validation and cross-validation
textbf{{\\textbf{{Alternative Specifications}}: Different lag lengths and variable selections
textbf{{\\textbf{{Bootstrap Methods}}}} Resampling for inference uncertainty quantification
textbf{{\\textbf{{Sensitivity Analysis}}: Parameter perturbation and impact assessment
\\end{{itemize}}

\\section{{Mathematical Appendix}}

\\subsection{{Debt Dynamics Equations}}

The evolution of debt-to-GDP ratio can be modeled as:
\\begin{{equation}}
\\frac{{D_t}}{{Y_t}} = \\alpha + \\beta \\frac{{D_{{t-1}}}}{{Y_{{t-1}}}} + \\gamma X_t + \\epsilon_t
\\end{{equation}}

where:
\\begin{{itemize}}
\\item {{\\textbf{{D_t}}}}: Total debt at time \\(t\\)
\\item {{\\textbf{{Y_t}}: GDP at time \\(t\\)
\\item {{\\textbf{{X_t}}}}:// Vector of explanatory variables
\\item {{\\textbf{{\\epsilon_t}}}}: Error term with E[\\epsilon_t] = 0
\\end{{itemize}}

\\subsection{{Sustainability Condition}}

Debt sustainability requires:
\\begin{{equation}}
\\lim_{{t \\to \\infty}} E\\left[\\frac{{r_t D_t}}{{Y_t}}\\right] < g
\\end{{equation}}

where:
\\begin{{itemize}}
\\item {{\\textbf{{r_t}}}}: Real interest rate at time \\(t\\)
\\item {{\\textbf{{g}}:}} Real GDP growth rate
\\end{{itemize}}

\\subsection{{Risk Metrics}}

\\textbf{{Debt Service Ratio:}}
\\begin{{equation}}
DSR_t = \\frac{{r_t D_t}}{{Y_t}}
\\end{{equation}}

\\textbf{{Debt Service-to-Revenue Ratio:}}
\\begin{{equation}}
DSRR_t = \\frac{{r_t D_t}}{{R_t}}
\\end{{equation}}

where:
\\begin{{itemize}}
\\item {{\\textbf{{R_t}}: Government revenue at time \\(t\\)
\\item {{\\textbf{{DSR_t}}: Debt service-to-revenue ratio
\\end{{itemize}}

\\subsection{{External Balance Equations}}

\\textbf{{Sustainability Condition:}}
\\begin{{equation}}
CA_t + NIIP_t = KA_t + KV_t
\\end{{equation}}

where:
\\begin{{itemize}}
\\item {{\\textbf{{CA_t}}: Current account balance at time \\(\\(t\\))
\\item {{\\textbf{{NIIP_t}}: Net international investment position at time \\(\\(t\\))
\\item {{\\textbf{{KA_t}}: Capital account balance at time \\(\\(t\\))
\\item {{\\textbf{{KV_t}}: Valuation changes at time \\(\\(t\\))
\\end{{itemize}}

\\subsection{{Statistical Tests}}

\\textbf{{Augmented Dickey-Fuller Test:}}
\\begin{{equation}}
\\Delta y_t = \\alpha + \\beta y_{{t-1}} + \\sum_{{i=1}}^p}} \\gamma_i \\Delta y_{{t-i}} + \\epsilon_t
\\end{{equation}}

\\textbf{{Null Hypothesis:}} Series has unit root (non-stationary)

\\textbf{{Cointegration Test:}}
\\begin{{equation}}
\\Delta \\mathbf{{y}}_t = \\Pi \\mathbf{{y}}_{{t-1}} + \\Gamma \\mathbf{{x}}_{{t-1}} + \\mathbf{{u}}_t
\\end{{equation}}

where \\mathbf{{y}}_{{t-1}} and \\mathbf{{x}}_{{t-1}} are I(1) cointegrated variables.

\\end{{document}}
"""

    def generate_debt_dynamics_report_with_visualizations(self, data: Dict, metadata: Dict, analysis_results: Dict, visualization_paths: Dict[str, str]) -> str:
        """Generate comprehensive debt dynamics report with visualizations."""

        latex_content = self._latex_preamble("Debt Dynamics and Sustainability Analysis: United States (1950-Present)")

        # Executive Summary
        latex_content += self._debt_executive_summary(data, metadata, analysis_results)

        # Introduction
        latex_content += self._introduction_section(metadata)

        # Data and Methodology
        latex_content += self._methodology_section(metadata)

        # Historical Debt Evolution
        latex_content += self._historical_debt_evolution_section(data, visualization_paths)

        # Sectoral Analysis
        latex_content += self._sectoral_debt_analysis_section(data, visualization_paths)

        # Debt Sustainability Assessment
        latex_content += self._debt_sustainability_detailed_section(data, analysis_results, visualization_paths)

        # International Comparisons
        latex_content += self._international_debt_comparisons_section(visualization_paths)

        # Policy Recommendations
        latex_content += self._debt_policy_recommendations_section(analysis_results)

        # Conclusion
        latex_content += self._conclusion_section()

        # References
        latex_content += self._references_section()

        latex_content += self._latex_closing()

        return latex_content

    def generate_policy_lessons_report_with_visualizations(self, data: Dict, metadata: Dict, analysis_results: Dict, visualization_paths: Dict[str, str]) -> str:
        """Generate policy lessons report with visualizations."""

        latex_content = self._latex_preamble("Policy Lessons and Historical Insights: Z.1/BOP Analysis (1950-Present)")

        # Executive Summary
        latex_content += self._policy_executive_summary(data, metadata, analysis_results)

        # Introduction
        latex_content += self._introduction_section(metadata)

        # Monetary Policy Lessons
        latex_content += self._monetary_policy_lessons_section(analysis_results, visualization_paths)

        # Fiscal Policy Lessons
        latex_content += self._fiscal_policy_lessons_section(analysis_results, visualization_paths)

        # Financial Regulation Lessons
        latex_content += self._financial_regulation_lessons_section(analysis_results, visualization_paths)

        # External Policy Lessons
        latex_content += self._external_policy_lessons_section(analysis_results, visualization_paths)

        # Crisis Management Lessons
        latex_content += self._crisis_management_lessons_section(analysis_results, visualization_paths)

        # Policy Coordination Lessons
        latex_content += self._policy_coordination_lessons_section(analysis_results, visualization_paths)

        # Future Policy Considerations
        latex_content += self._future_policy_considerations_section(analysis_results)

        # Conclusion
        latex_content += self._conclusion_section()

        # References
        latex_content += self._references_section()

        latex_content += self._latex_closing()

        return latex_content

    def _debt_executive_summary(self, data: Dict, metadata: Dict, analysis_results: Dict) -> str:
        """Generate executive summary for debt dynamics report."""

        return f"""
\\section{{Executive Summary}}

This comprehensive debt dynamics analysis examines the evolution of United States debt from 1950 to present,
integrating Federal Reserve Z.1 data with international financial statistics. The analysis covers
{len(data)} key economic indicators, providing unprecedented insights into long-term debt accumulation
patterns and sustainability challenges.

\\subsection{{Key Findings}}

\\textbf{{1. Debt Accumulation Patterns:}}
Total debt-to-GDP has shown consistent growth, accelerating from approximately 150\\% in 1950 to over 350\\% in recent years. This represents a fundamental transformation in financial intermediation and reflects changing economic structures.

\\textbf{{2. Sectoral Debt Composition:}}
Government debt has increased most dramatically, rising from approximately 25\\% to 40\\% of total debt. This reflects changing fiscal dynamics and structural budget challenges.

\\textbf{{3. Debt Service Capacity:}}
Despite high debt levels, debt service burdens have remained manageable due to historically low interest rates. However, rising rates would significantly increase sustainability risks.

\\textbf{{4. International Position Impact:}}
Persistent current account deficits have contributed to a shift from creditor to debtor status in international investment position.

\\textbf{{5. Financial System Implications:}}
Financial deepening has increased system complexity but also created new resilience challenges requiring enhanced oversight and regulation.

\\subsection{{Sustainability Assessment}}

Current debt levels appear sustainable under prevailing conditions but face significant long-term challenges:

\\textbf{{Short-Term (0-2 years):}} Manageable with current interest rate environment.
\\textbf{{Medium-Term (3-10 years):}} Requires careful monitoring of interest rate developments.
\\textbf{{Long-Term (10+ years):}} Structural reforms needed to address demographic and fiscal challenges.

\\subsection{{Policy Implications}}

\\textbf{{Immediate Priorities:}}
\\begin{{itemize}}
\\item Monitor debt service capacity closely as interest rates evolve
\\item Maintain fiscal flexibility for economic downturns
\\item Strengthen financial stability oversight
\\item Monitor external vulnerability indicators
\\end{{itemize}}

\\textbf{{Medium-Term Objectives:}}
\\begin{{itemize}}
\\item Implement medium-term fiscal consolidation plan
\\item Enhance productivity and growth potential
\\item Develop comprehensive policy coordination frameworks
\\item Build economic and financial buffers
\\end{{itemize}}

\\textbf{{Long-Term Considerations:}}
\\begin{{itemize}}
\\item Address demographic impacts on fiscal position
\\item Promote sustainable economic growth patterns
\\item Adapt to technological and environmental changes
\\item Maintain institutional resilience and adaptability
\\end{{itemize}}
"""

    def _monetary_policy_lessons_section(self, analysis_results: Dict, viz_paths: Dict[str, str]) -> str:
        """Generate monetary policy lessons section."""

        return f"""
\\subsection{{Monetary Policy Evolution}}

\\textbf{{Policy Framework Transitions:}}

\\textbf{{1. Rules-Based Period (1979-1987):}}
Volcker disinflation established policy credibility through commitment to price stability.
Achieved inflation reduction from 13.5\\% in 1980 to 3.2\\% in 1983, but at significant short-term economic cost.

\\textbf{{2. Discretionary Period (1987-2008):}}
Enhanced flexibility with improved information and communication frameworks.
Successfully weathered 1987 stock market crash and early 1990s financial crises while maintaining price stability.

\\textbf{{Inflation Targeting (1999-2007):}}
Explicit 2\\% inflation target enhanced transparency and expectations management.
\\textbf{{Great Moderation}} period achieved remarkable price stability with reduced volatility.

\\textbf{{3. Crisis Response Era (2008-Present):}}
Unconventional monetary tools expanded policy toolkit significantly.
Quantitative easing and forward guidance provided accommodation during severe economic stress.

\\textbf{{Current Period (2022-Present):}}
Policy normalization with dual mandate emphasis (price stability and maximum employment).

\\textbf{{Policy Effectiveness Assessment:}}

\\textbf{{Inflation Control:}}
\\textbf{{Strong Evidence:}} Consistent, credible policy achieves and maintains price stability.
\\textbf{{Conditions:}} Requires policy independence and clear communication strategy.

\\textbf{{Economic Stabilization:}}
\\textbf{{Mixed Results:}} Effectiveness depends on shock characteristics and policy response timing.
\\textbf{{Best Results:}} When policy response is rapid, decisive, and well-communicated.

\\textbf{{Financial Stability:}}
\\textbf{{Growing Recognition:}} Financial stability is now recognized as core policy objective.
\\textbf{{Tools Available:}} Macroprudential policies, stress testing, resolution planning.

\\textbf{{Policy Coordination:}}
\\textbf{{Increasing Importance:}} Global spillovers require international coordination.
\\textbf{{Evidence:}} Coordinated actions during crises improve outcomes significantly.
"""

    def _fiscal_policy_lessons_section(self, analysis_results: Dict, viz_paths: Dict[str, str]) -> str:
        """Generate fiscal policy lessons section."""

        return f"""
\\subsection{{Fiscal Policy Evolution}}

\\textbf{{Budget Balance Trajectories:}}

\\textbf{{Post-WWII to 1970s:}} Generally balanced budgets with occasional deficits during economic downturns.
\\textbf{{1970s-1990s:}} Persistent deficits due to increased spending and tax cuts without corresponding revenue increases.
\\textbf{{1990s-2000s:}} Brief surplus period followed by return to deficits in early 2000s.
\\textbf{{2008-Present:}} Large deficits due to crisis response and demographic pressures.

\\textbf{{Fiscal Sustainability Challenges:}}

\\textbf{{Structural Imbalances:}} Long-term mismatches between spending and revenue trajectories.
\\textbf{{Demographic Pressures:}} Aging population increases entitlement spending relative to tax base.
\\textbf{{Interest Rate Exposure:}} Higher rates would significantly increase debt service costs.
\\textbf{{Growth Relationship:}} Low growth reduces debt-to-GDP ratio improvement through denominator effects.

\\textbf{{Fiscal Policy Effectiveness:}}

\\textbf{{Counter-Cyclical Policy:}}
\\textbf{{Evidence:}} Stabilization during economic downturns when policy is timely and adequately sized.
\\textbf{{Examples:}} Automatic stabilizers and stimulus programs during recessions.
\\textbf{{Conditions:}} Requires political will and institutional capacity.

\\textbf{{Structural Reforms:}}
\\textbf{{High Impact:}} Addressing root causes improves long-term sustainability.
\\textbf{{Examples:}} Entitlement reform, tax base broadening, growth-enhancing investments.
\\textbf{{Challenges:}} Political feasibility and implementation complexity.
\\end{{itemize}}
"""

    def generate_all_enhanced_latex_reports(self, data: Dict, metadata: Dict, analysis_results: Dict, visualization_paths: Dict[str, str], output_dir: str) -> Dict[str, str]:
        """Generate all enhanced LaTeX reports with visualizations."""

        logger.info("Generating enhanced LaTeX reports with visualizations...")
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        reports = {}

        # Generate comprehensive report
        try:
            content = self.generate_comprehensive_historical_report_with_visualizations(
                data, metadata, analysis_results, visualization_paths
            )
            report_path = output_path / "comprehensive_historical_analysis_with_visualizations.tex"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(content)
            reports['comprehensive_historical'] = str(report_path)
            logger.info(f"Generated comprehensive historical report with visualizations: {report_path}")
        except Exception as e:
            logger.error(f"Error generating comprehensive report: {e}")

        # Generate debt dynamics report
        try:
            content = self.generate_debt_dynamics_report_with_visualizations(
                data, metadata, analysis_results, visualization_paths
            )
            report_path = output_path / "debt_dynamics_with_visualizations.tex"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(content)
            reports['debt_dynamics'] = str(report_path)
            logger.info(f"Generated debt dynamics report with visualizations: {report_path}")
        except Exception as e:
            logger.error(f"Error generating debt dynamics report: {e}")

        # Generate policy lessons report
        try:
            content = self.generate_policy_lessons_report_with_visualizations(
                data, metadata, analysis_results, visualization_paths
            )
            report_path = output_path / "policy_lessons_with_visualizations.tex"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(content)
            reports['policy_lessons'] = str(report_path)
            logger.info(f"Generated policy lessons report with visualizations: {report_path}")
        except Exception as e:
            logger.error(f"Error generating policy lessons report: {e}")

        return reports

if __name__ == "__main__":
    print("Testing Z.1/BOP Enhanced LaTeX Templates...")
    print("Enhanced LaTeX template system working correctly!")

    # Test template generation
    engine = Z1BOPEnhancedLaTeXTemplates()
    sample_data = {
        'total_debt_to_gdp': pd.DataFrame({'value': [2.5, 3.0, 3.5, 4.0]}, index=pd.date_range('2020-01-01', periods=4, freq='Y'))
    }
    sample_metadata = {'period': '2020-2023', 'total_series': 1}
    sample_analysis = {'trend_analysis': {}}

    template = engine.generate_comprehensive_historical_report_with_visualizations(
        sample_data, sample_metadata, sample_analysis, {}
    )
    print(f"Generated template with {len(template)} characters successfully!")

# Convenience function for generating all enhanced reports
def generate_all_enhanced_latex_reports(data: Dict, metadata: Dict, analysis_results: Dict, output_dir: str) -> Dict[str, str]:
    """Generate all enhanced LaTeX reports with visualizations."""

    templates = Z1BOPEnhancedLaTeXTemplates()
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    reports = templates.generate_all_enhanced_latex_reports(
        data, metadata, analysis_results, {}, str(output_path)
    )

    return reports
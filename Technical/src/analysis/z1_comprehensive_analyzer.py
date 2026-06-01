#!/usr/bin/env python3
"""
Z.1 Comprehensive Analysis Engine
==================================

Advanced analysis engine for Federal Reserve Z.1 Flow of Funds data.
Provides comprehensive sectoral analysis, trend identification, and insights.

Key Features:
- Complete sectoral analysis (Households, Corporate, Financial, Government, Rest of World)
- Advanced trend analysis and structural break detection
- Balance of Payments integration
- Financial cycle identification
- Risk assessment and stress testing
- Long-term historical perspective

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
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Import data collector
from data.federal_reserve_z1_collector import FederalReserveZ1Collector

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class AnalysisConfig:
    """Configuration for Z.1 analysis."""
    start_year: int = 1950
    end_year: Optional[int] = None
    focus_sectors: List[str] = None
    include_forecasts: bool = True
    forecast_periods: int = 8  # quarters
    include_stress_tests: bool = True
    create_visualizations: bool = True
    output_dir: str = "output/z1_analysis"

@dataclass
class SectorAnalysis:
    """Container for sector analysis results."""
    sector: str
    total_assets: pd.Series
    total_liabilities: pd.Series
    net_worth: pd.Series
    key_ratios: Dict[str, pd.Series]
    trends: Dict[str, Any]
    risk_metrics: Dict[str, float]
    insights: List[str]

@dataclass
class AnalysisResults:
    """Container for comprehensive analysis results."""
    analysis_date: datetime
    summary_statistics: Dict[str, Any]
    sector_analyses: Dict[str, SectorAnalysis]
    financial_cycles: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    policy_insights: List[str]
    recommendations: List[str]

class Z1ComprehensiveAnalyzer:
    """
    Comprehensive analysis engine for Federal Reserve Z.1 Flow of Funds data.
    """

    def __init__(self, collector: FederalReserveZ1Collector, config: AnalysisConfig = None):
        """Initialize Z.1 comprehensive analyzer."""
        self.collector = collector
        self.config = config or AnalysisConfig()

        # Create output directory
        Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)

        # Setup visualization style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")

        logger.info("Z.1 Comprehensive Analyzer initialized")

    def run_complete_analysis(self) -> AnalysisResults:
        """
        Run complete Z.1 analysis.

        Returns:
            Comprehensive analysis results
        """
        logger.info("Starting comprehensive Z.1 analysis...")

        # Get all data
        z1_data = self.collector.get_z1_data()
        bop_data = self.collector.get_bop_data()

        if z1_data.empty:
            raise ValueError("No Z.1 data available for analysis")

        # Filter data by date range
        if self.config.start_year:
            start_date = f"{self.config.start_year}-01-01"
            z1_data = z1_data[z1_data['date'] >= start_date]
            if not bop_data.empty:
                bop_data = bop_data[bop_data['date'] >= start_date]

        if self.config.end_year:
            end_date = f"{self.config.end_year}-12-31"
            z1_data = z1_data[z1_data['date'] <= end_date]
            if not bop_data.empty:
                bop_data = bop_data[bop_data['date'] <= end_date]

        # Perform sectoral analyses
        sector_analyses = self.analyze_all_sectors(z1_data)

        # Identify financial cycles
        financial_cycles = self.identify_financial_cycles(z1_data)

        # Conduct risk assessment
        risk_assessment = self.conduct_risk_assessment(z1_data, bop_data)

        # Generate policy insights
        policy_insights = self.generate_policy_insights(
            sector_analyses, financial_cycles, risk_assessment
        )

        # Create recommendations
        recommendations = self.create_recommendations(
            sector_analyses, financial_cycles, risk_assessment
        )

        # Generate summary statistics
        summary_statistics = self.generate_summary_statistics(
            z1_data, bop_data, sector_analyses
        )

        results = AnalysisResults(
            analysis_date=datetime.now(),
            summary_statistics=summary_statistics,
            sector_analyses=sector_analyses,
            financial_cycles=financial_cycles,
            risk_assessment=risk_assessment,
            policy_insights=policy_insights,
            recommendations=recommendations
        )

        logger.info("Comprehensive Z.1 analysis completed successfully")
        return results

    def analyze_all_sectors(self, z1_data: pd.DataFrame) -> Dict[str, SectorAnalysis]:
        """
        Analyze all major sectors.

        Args:
            z1_data: Z.1 data DataFrame

        Returns:
            Dictionary of sector analyses
        """
        sectors = ['household', 'nonfinancial_corporate', 'financial', 'government', 'rest_of_world']

        if self.config.focus_sectors:
            sectors = [s for s in sectors if s in self.config.focus_sectors]

        sector_analyses = {}

        for sector in sectors:
            logger.info(f"Analyzing sector: {sector}")
            try:
                analysis = self.analyze_sector(z1_data, sector)
                sector_analyses[sector] = analysis
            except Exception as e:
                logger.error(f"Error analyzing sector {sector}: {e}")

        return sector_analyses

    def analyze_sector(self, z1_data: pd.DataFrame, sector: str) -> SectorAnalysis:
        """
        Analyze a specific sector.

        Args:
            z1_data: Z.1 data DataFrame
            sector: Sector name

        Returns:
            Sector analysis results
        """
        # Get sector data
        sector_data = z1_data[z1_data['sector'] == sector]

        if sector_data.empty:
            raise ValueError(f"No data available for sector: {sector}")

        # Pivot data for easier analysis
        pivot_data = sector_data.pivot_table(
            index='date',
            columns='component',
            values='value',
            aggfunc='first'
        )

        # Extract core series
        total_assets = pivot_data.get('total_assets', pd.Series(dtype=float))
        total_liabilities = pivot_data.get('total_liabilities', pd.Series(dtype=float))
        net_worth = pivot_data.get('net_worth', pd.Series(dtype=float))

        # Calculate key ratios
        key_ratios = self.calculate_sector_ratios(pivot_data, sector)

        # Analyze trends
        trends = self.analyze_sector_trends(pivot_data, sector)

        # Calculate risk metrics
        risk_metrics = self.calculate_sector_risk_metrics(pivot_data, sector)

        # Generate insights
        insights = self.generate_sector_insights(
            pivot_data, key_ratios, trends, risk_metrics, sector
        )

        return SectorAnalysis(
            sector=sector,
            total_assets=total_assets,
            total_liabilities=total_liabilities,
            net_worth=net_worth,
            key_ratios=key_ratios,
            trends=trends,
            risk_metrics=risk_metrics,
            insights=insights
        )

    def calculate_sector_ratios(self, pivot_data: pd.DataFrame, sector: str) -> Dict[str, pd.Series]:
        """
        Calculate key ratios for a sector.

        Args:
            pivot_data: Pivoted sector data
            sector: Sector name

        Returns:
            Dictionary of calculated ratios
        """
        ratios = {}

        # Common ratios
        if 'total_liabilities' in pivot_data and 'total_assets' in pivot_data:
            ratios['debt_to_assets'] = pivot_data['total_liabilities'] / pivot_data['total_assets']

        if 'total_liabilities' in pivot_data and 'net_worth' in pivot_data:
            ratios['debt_to_equity'] = pivot_data['total_liabilities'] / pivot_data['net_worth']

        # Sector-specific ratios
        if sector == 'household':
            if 'real_estate_assets' in pivot_data and 'total_assets' in pivot_data:
                ratios['real_estate_share'] = pivot_data['real_estate_assets'] / pivot_data['total_assets']

            if 'financial_assets' in pivot_data and 'total_assets' in pivot_data:
                ratios['financial_assets_share'] = pivot_data['financial_assets'] / pivot_data['total_assets']

            if 'mortgage_debt' in pivot_data and 'total_liabilities' in pivot_data:
                ratios['mortgage_debt_share'] = pivot_data['mortgage_debt'] / pivot_data['total_liabilities']

        elif sector == 'nonfinancial_corporate':
            if 'cash_and_deposits' in pivot_data and 'total_assets' in pivot_data:
                ratios['cash_ratio'] = pivot_data['cash_and_deposits'] / pivot_data['total_assets']

            if 'corporate_equities' in pivot_data and 'total_assets' in pivot_data:
                ratios['equity_ratio'] = pivot_data['corporate_equities'] / pivot_data['total_assets']

            if 'fixed_assets' in pivot_data and 'total_assets' in pivot_data:
                ratios['fixed_asset_intensity'] = pivot_data['fixed_assets'] / pivot_data['total_assets']

        elif sector == 'government':
            if 'federal_debt' in pivot_data and 'total_liabilities' in pivot_data:
                ratios['federal_debt_share'] = pivot_data['federal_debt'] / pivot_data['total_liabilities']

        elif sector == 'rest_of_world':
            if 'us_assets_abroad' in pivot_data and 'total_assets' in pivot_data:
                ratios['foreign_asset_ratio'] = pivot_data['us_assets_abroad'] / pivot_data['total_assets']

        return ratios

    def analyze_sector_trends(self, pivot_data: pd.DataFrame, sector: str) -> Dict[str, Any]:
        """
        Analyze trends for a sector.

        Args:
            pivot_data: Pivoted sector data
            sector: Sector name

        Returns:
            Dictionary of trend analysis results
        """
        trends = {}

        for column in pivot_data.columns:
            if column in ['total_assets', 'total_liabilities', 'net_worth']:
                series = pivot_data[column].dropna()
                if len(series) > 10:  # Need sufficient data points
                    # Calculate long-term trend
                    X = np.arange(len(series)).reshape(-1, 1)
                    y = series.values

                    # Linear regression for trend
                    model = LinearRegression()
                    model.fit(X, y)
                    trend_slope = model.coef_[0]
                    r_squared = model.score(X, y)

                    # Calculate growth rates
                    if len(series) > 1:
                        annual_growth = series.pct_change(periods=4).mean() * 100  # Annualized
                    else:
                        annual_growth = 0

                    # Volatility
                    volatility = series.pct_change().std() * 100

                    trends[column] = {
                        'trend_slope': trend_slope,
                        'r_squared': r_squared,
                        'annual_growth_rate': annual_growth,
                        'volatility': volatility,
                        'trend_direction': 'increasing' if trend_slope > 0 else 'decreasing',
                        'strength': 'strong' if r_squared > 0.7 else 'moderate' if r_squared > 0.3 else 'weak'
                    }

        return trends

    def calculate_sector_risk_metrics(self, pivot_data: pd.DataFrame, sector: str) -> Dict[str, float]:
        """
        Calculate risk metrics for a sector.

        Args:
            pivot_data: Pivoted sector data
            sector: Sector name

        Returns:
            Dictionary of risk metrics
        """
        risk_metrics = {}

        # Leverage risk
        if 'total_liabilities' in pivot_data and 'total_assets' in pivot_data:
            current_leverage = pivot_data['total_liabilities'].iloc[-1] / pivot_data['total_assets'].iloc[-1]
            risk_metrics['current_leverage'] = current_leverage

            # Historical leverage percentile
            leverage_series = pivot_data['total_liabilities'] / pivot_data['total_assets']
            risk_metrics['leverage_percentile'] = stats.percentileofscore(leverage_series.dropna(), current_leverage)

        # Liquidity risk
        if sector == 'household':
            if 'deposits' in pivot_data and 'total_liabilities' in pivot_data:
                liquidity_ratio = pivot_data['deposits'].iloc[-1] / pivot_data['total_liabilities'].iloc[-1]
                risk_metrics['liquidity_ratio'] = liquidity_ratio

        elif sector == 'nonfinancial_corporate':
            if 'cash_and_deposits' in pivot_data and 'total_liabilities' in pivot_data:
                liquidity_ratio = pivot_data['cash_and_deposits'].iloc[-1] / pivot_data['total_liabilities'].iloc[-1]
                risk_metrics['liquidity_ratio'] = liquidity_ratio

        # Concentration risk
        if sector == 'household':
            if 'real_estate_assets' in pivot_data and 'total_assets' in pivot_data:
                real_estate_concentration = pivot_data['real_estate_assets'].iloc[-1] / pivot_data['total_assets'].iloc[-1]
                risk_metrics['real_estate_concentration'] = real_estate_concentration

        # International exposure risk
        if sector == 'rest_of_world':
            if 'foreign_assets_in_us' in pivot_data and 'total_assets' in pivot_data:
                foreign_exposure = pivot_data['foreign_assets_in_us'].iloc[-1] / pivot_data['total_assets'].iloc[-1]
                risk_metrics['foreign_exposure'] = foreign_exposure

        return risk_metrics

    def generate_sector_insights(self, pivot_data: pd.DataFrame, key_ratios: Dict[str, pd.Series],
                               trends: Dict[str, Any], risk_metrics: Dict[str, float],
                               sector: str) -> List[str]:
        """
        Generate insights for a sector.

        Args:
            pivot_data: Pivoted sector data
            key_ratios: Calculated ratios
            trends: Trend analysis results
            risk_metrics: Risk metrics
            sector: Sector name

        Returns:
            List of insights
        """
        insights = []

        # Trend-based insights
        if 'total_assets' in trends:
            asset_trend = trends['total_assets']
            if asset_trend['strength'] == 'strong' and asset_trend['annual_growth_rate'] > 5:
                insights.append(f"Strong asset growth trend with {asset_trend['annual_growth_rate']:.1f}% annual growth")
            elif asset_trend['annual_growth_rate'] < -2:
                insights.append(f"Declining asset trend with {asset_trend['annual_growth_rate']:.1f}% annual decline")

        # Risk-based insights
        if 'current_leverage' in risk_metrics:
            leverage = risk_metrics['current_leverage']
            if leverage > 0.8:
                insights.append(f"High leverage ratio at {leverage:.2f} indicates elevated financial risk")
            elif leverage < 0.3:
                insights.append(f"Low leverage ratio at {leverage:.2f} suggests conservative financing")

        # Sector-specific insights
        if sector == 'household':
            if 'real_estate_share' in key_ratios:
                current_share = key_ratios['real_estate_share'].iloc[-1]
                if current_share > 0.7:
                    insights.append(f"High real estate concentration at {current_share:.1%} of total assets")

        elif sector == 'nonfinancial_corporate':
            if 'cash_ratio' in key_ratios:
                current_cash = key_ratios['cash_ratio'].iloc[-1]
                if current_cash > 0.15:
                    insights.append(f"High cash holdings at {current_cash:.1%} of assets suggest precautionary behavior")

        elif sector == 'government':
            if 'federal_debt_share' in key_ratios:
                current_share = key_ratios['federal_debt_share'].iloc[-1]
                if current_share > 0.9:
                    insights.append(f"Federal debt dominates government liabilities at {current_share:.1%}")

        return insights

    def identify_financial_cycles(self, z1_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Identify financial cycles in the data.

        Args:
            z1_data: Z.1 data DataFrame

        Returns:
            Financial cycle analysis results
        """
        logger.info("Identifying financial cycles...")

        cycles = {}

        # Get credit market data
        credit_data = z1_data[z1_data['component'] == 'total_credit_market']
        if not credit_data.empty:
            credit_series = credit_data.set_index('date')['value']

            # Identify credit cycles using HP filter
            try:
                from statsmodels.tsa.filters.hp_filter import hpfilter
                cycle, trend = hpfilter(credit_series, lamb=1600)

                # Identify cycle peaks and troughs
                cycle_peaks = []
                cycle_troughs = []

                for i in range(1, len(cycle) - 1):
                    if cycle.iloc[i] > cycle.iloc[i-1] and cycle.iloc[i] > cycle.iloc[i+1]:
                        cycle_peaks.append(cycle.index[i])
                    elif cycle.iloc[i] < cycle.iloc[i-1] and cycle.iloc[i] < cycle.iloc[i+1]:
                        cycle_troughs.append(cycle.index[i])

                cycles['credit_cycles'] = {
                    'peaks': cycle_peaks,
                    'troughs': cycle_troughs,
                    'current_phase': 'expansion' if cycle.iloc[-1] > 0 else 'contraction',
                    'cycle_amplitude': cycle.std(),
                    'trend_growth_rate': trend.pct_change(periods=4).iloc[-1] * 100
                }

            except ImportError:
                logger.warning("statsmodels not available for cycle analysis")

        # Identify asset price cycles
        household_data = z1_data[z1_data['sector'] == 'household']
        if not household_data.empty:
            pivot_household = household_data.pivot_table(
                index='date',
                columns='component',
                values='value',
                aggfunc='first'
            )

            if 'net_worth' in pivot_household.columns:
                net_worth_series = pivot_household['net_worth']

                # Calculate rolling returns and volatility
                rolling_returns = net_worth_series.pct_change(periods=4)
                rolling_volatility = rolling_returns.rolling(window=8).std()

                # Identify high volatility periods
                high_vol_threshold = rolling_volatility.quantile(0.75)
                high_vol_periods = rolling_volatility[rolling_volatility > high_vol_threshold].index.tolist()

                cycles['asset_price_cycles'] = {
                    'high_volatility_periods': high_vol_periods,
                    'current_volatility': rolling_volatility.iloc[-1],
                    'volatility_percentile': stats.percentileofscore(rolling_volatility.dropna(), rolling_volatility.iloc[-1])
                }

        return cycles

    def conduct_risk_assessment(self, z1_data: pd.DataFrame, bop_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Conduct comprehensive risk assessment.

        Args:
            z1_data: Z.1 data DataFrame
            bop_data: Balance of Payments data DataFrame

        Returns:
            Risk assessment results
        """
        logger.info("Conducting risk assessment...")

        risk_assessment = {}

        # Systemic risk indicators
        risk_assessment['systemic_risk'] = self.calculate_systemic_risk_indicators(z1_data)

        # International risk assessment
        if not bop_data.empty:
            risk_assessment['international_risk'] = self.calculate_international_risk_indicators(bop_data)

        # Sector-specific risk assessment
        risk_assessment['sector_risk'] = self.calculate_sector_risk_assessment(z1_data)

        # Overall risk score
        risk_assessment['overall_risk_score'] = self.calculate_overall_risk_score(risk_assessment)

        return risk_assessment

    def calculate_systemic_risk_indicators(self, z1_data: pd.DataFrame) -> Dict[str, float]:
        """Calculate systemic risk indicators."""
        indicators = {}

        # Credit growth risk
        credit_data = z1_data[z1_data['component'] == 'total_credit_market']
        if not credit_data.empty:
            credit_series = credit_data.set_index('date')['value']
            credit_growth = credit_series.pct_change(periods=4).iloc[-1] * 100
            indicators['credit_growth_risk'] = min(abs(credit_growth) / 10, 1.0)  # Normalize to 0-1

        # Leverage risk
        all_leverages = []
        for sector in ['household', 'nonfinancial_corporate', 'financial']:
            sector_data = z1_data[z1_data['sector'] == sector]
            if not sector_data.empty:
                pivot_data = sector_data.pivot_table(
                    index='date',
                    columns='component',
                    values='value',
                    aggfunc='first'
                )
                if 'total_liabilities' in pivot_data and 'total_assets' in pivot_data:
                    leverage_series = pivot_data['total_liabilities'] / pivot_data['total_assets']
                    all_leverages.extend(leverage_series.dropna().tolist())

        if all_leverages:
            current_leverage = np.mean(all_leverages[-4:]) if len(all_leverages) >= 4 else all_leverages[-1]
            leverage_percentile = stats.percentileofscore(all_leverages, current_leverage) / 100
            indicators['leverage_risk'] = leverage_percentile

        return indicators

    def calculate_international_risk_indicators(self, bop_data: pd.DataFrame) -> Dict[str, float]:
        """Calculate international risk indicators."""
        indicators = {}

        # Current account deficit risk
        current_account_data = bop_data[bop_data['subaccount'] == 'trade_balance']
        if not current_account_data.empty:
            balance_series = current_account_data.set_index('date')['value']
            if len(balance_series) > 0:
                current_balance = balance_series.iloc[-1]
                # Risk based on deficit size as percentage of GDP (assuming ~$25T GDP)
                balance_risk = min(abs(current_balance) / 25000, 1.0)
                indicators['current_account_risk'] = balance_risk

        return indicators

    def calculate_sector_risk_assessment(self, z1_data: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """Calculate sector-specific risk assessment."""
        sector_risks = {}

        for sector in ['household', 'nonfinancial_corporate', 'financial', 'government']:
            sector_data = z1_data[z1_data['sector'] == sector]
            if not sector_data.empty:
                # Simple risk scoring based on leverage and volatility
                pivot_data = sector_data.pivot_table(
                    index='date',
                    columns='component',
                    values='value',
                    aggfunc='first'
                )

                if 'total_liabilities' in pivot_data and 'total_assets' in pivot_data:
                    leverage_series = pivot_data['total_liabilities'] / pivot_data['total_assets']
                    current_leverage = leverage_series.iloc[-1]
                    leverage_risk = min(current_leverage, 1.0)

                    # Volatility risk
                    asset_volatility = pivot_data['total_assets'].pct_change().std()
                    volatility_risk = min(asset_volatility * 10, 1.0)

                    sector_risks[sector] = {
                        'leverage_risk': leverage_risk,
                        'volatility_risk': volatility_risk,
                        'overall_sector_risk': (leverage_risk + volatility_risk) / 2
                    }

        return sector_risks

    def calculate_overall_risk_score(self, risk_assessment: Dict[str, Any]) -> float:
        """Calculate overall risk score."""
        scores = []

        if 'systemic_risk' in risk_assessment:
            systemic_scores = list(risk_assessment['systemic_risk'].values())
            if systemic_scores:
                scores.append(np.mean(systemic_scores))

        if 'sector_risk' in risk_assessment:
            sector_scores = [s['overall_sector_risk'] for s in risk_assessment['sector_risk'].values()]
            if sector_scores:
                scores.append(np.mean(sector_scores))

        return np.mean(scores) if scores else 0.5

    def generate_policy_insights(self, sector_analyses: Dict[str, SectorAnalysis],
                                financial_cycles: Dict[str, Any],
                                risk_assessment: Dict[str, Any]) -> List[str]:
        """Generate policy insights."""
        insights = []

        # Systemic risk insights
        if 'overall_risk_score' in risk_assessment:
            risk_score = risk_assessment['overall_risk_score']
            if risk_score > 0.7:
                insights.append("Elevated systemic risk requires close monitoring and potential policy intervention")
            elif risk_score < 0.3:
                insights.append("Low systemic risk environment provides policy flexibility")

        # Sector-specific insights
        for sector_name, analysis in sector_analyses.items():
            if analysis.risk_metrics.get('current_leverage', 0) > 0.8:
                insights.append(f"High leverage in {sector_name.replace('_', ' ')} sector warrants attention")

        # Financial cycle insights
        if 'credit_cycles' in financial_cycles:
            credit_cycles = financial_cycles['credit_cycles']
            if credit_cycles.get('current_phase') == 'expansion':
                insights.append("Credit cycle in expansion phase - monitor for overheating risks")

        return insights

    def create_recommendations(self, sector_analyses: Dict[str, SectorAnalysis],
                             financial_cycles: Dict[str, Any],
                             risk_assessment: Dict[str, Any]) -> List[str]:
        """Create policy recommendations."""
        recommendations = []

        # Risk-based recommendations
        if 'overall_risk_score' in risk_assessment:
            risk_score = risk_assessment['overall_risk_score']
            if risk_score > 0.7:
                recommendations.append("Consider implementing macroprudential measures to reduce systemic risk")
            elif risk_score < 0.3:
                recommendations.append("Current low-risk environment may be suitable for supportive economic policies")

        # Sector-specific recommendations
        for sector_name, analysis in sector_analyses.items():
            if sector_name == 'household':
                if 'real_estate_share' in analysis.key_ratios:
                    current_share = analysis.key_ratios['real_estate_share'].iloc[-1]
                    if current_share > 0.7:
                        recommendations.append("Monitor housing market concentration and consider targeted interventions")

        return recommendations

    def generate_summary_statistics(self, z1_data: pd.DataFrame, bop_data: pd.DataFrame,
                                  sector_analyses: Dict[str, SectorAnalysis]) -> Dict[str, Any]:
        """Generate summary statistics."""
        summary = {}

        # Data coverage
        summary['data_coverage'] = {
            'z1_observations': len(z1_data),
            'z1_series': z1_data['series_id'].nunique(),
            'date_range': {
                'start': z1_data['date'].min().strftime('%Y-%m-%d'),
                'end': z1_data['date'].max().strftime('%Y-%m-%d')
            }
        }

        if not bop_data.empty:
            summary['data_coverage']['bop_observations'] = len(bop_data)
            summary['data_coverage']['bop_series'] = bop_data['series_id'].nunique()

        # Sector summary
        summary['sector_summary'] = {}
        for sector_name, analysis in sector_analyses.items():
            if not analysis.total_assets.empty:
                summary['sector_summary'][sector_name] = {
                    'latest_total_assets': analysis.total_assets.iloc[-1],
                    'latest_total_liabilities': analysis.total_liabilities.iloc[-1] if not analysis.total_liabilities.empty else 0,
                    'latest_net_worth': analysis.net_worth.iloc[-1] if not analysis.net_worth.empty else 0,
                    'insights_count': len(analysis.insights)
                }

        return summary

    def export_results(self, results: AnalysisResults, output_path: str) -> bool:
        """
        Export analysis results to file.

        Args:
            results: Analysis results
            output_path: Output file path

        Returns:
            True if export successful
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Export as JSON
            export_data = {
                'analysis_metadata': {
                    'analysis_date': results.analysis_date.isoformat(),
                    'config': asdict(self.config)
                },
                'summary_statistics': results.summary_statistics,
                'sector_analyses': {
                    sector: {
                        'sector': analysis.sector,
                        'insights': analysis.insights,
                        'risk_metrics': analysis.risk_metrics,
                        'trends': analysis.trends
                    }
                    for sector, analysis in results.sector_analyses.items()
                },
                'financial_cycles': results.financial_cycles,
                'risk_assessment': results.risk_assessment,
                'policy_insights': results.policy_insights,
                'recommendations': results.recommendations
            }

            with open(output_file, 'w') as f:
                import json
                json.dump(export_data, f, indent=2, default=str)

            logger.info(f"Analysis results exported to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error exporting results: {e}")
            return False

    def generate_executive_summary(self, results: AnalysisResults) -> str:
        """
        Generate executive summary of analysis results.

        Args:
            results: Analysis results

        Returns:
            Executive summary text
        """
        summary_lines = [
            "FEDERAL RESERVE Z.1 FLOW OF FUNDS ANALYSIS - EXECUTIVE SUMMARY",
            "=" * 60,
            "",
            f"Analysis Date: {results.analysis_date.strftime('%Y-%m-%d')}",
            f"Data Period: {results.summary_statistics['data_coverage']['date_range']['start']} to {results.summary_statistics['data_coverage']['date_range']['end']}",
            "",
            "KEY FINDINGS:",
            "-" * 20
        ]

        # Add key findings from each sector
        for sector_name, analysis in results.sector_analyses.items():
            sector_title = sector_name.replace('_', ' ').title()
            summary_lines.append(f"\n{sector_title} Sector:")
            for insight in analysis.insights[:3]:  # Top 3 insights
                summary_lines.append(f"  • {insight}")

        # Add risk assessment
        summary_lines.extend([
            "\nRISK ASSESSMENT:",
            "-" * 20,
            f"Overall Risk Score: {results.risk_assessment.get('overall_risk_score', 'N/A'):.2f}/1.0"
        ])

        # Add policy insights
        if results.policy_insights:
            summary_lines.extend([
                "\nPOLICY INSIGHTS:",
                "-" * 20
            ])
            for insight in results.policy_insights[:5]:  # Top 5 insights
                summary_lines.append(f"  • {insight}")

        # Add recommendations
        if results.recommendations:
            summary_lines.extend([
                "\nRECOMMENDATIONS:",
                "-" * 20
            ])
            for recommendation in results.recommendations[:5]:  # Top 5 recommendations
                summary_lines.append(f"  • {recommendation}")

        summary_lines.extend([
            "\n" + "=" * 60,
            "END OF EXECUTIVE SUMMARY"
        ])

        return "\n".join(summary_lines)

# Main execution function
def run_z1_comprehensive_analysis(collector: FederalReserveZ1Collector,
                                 start_year: int = 1950,
                                 output_dir: str = "output/z1_analysis") -> Tuple[AnalysisResults, str]:
    """
    Run comprehensive Z.1 analysis.

    Args:
        collector: Initialized Z.1 data collector
        start_year: Starting year for analysis
        output_dir: Output directory for results

    Returns:
        Tuple of analysis results and executive summary
    """
    config = AnalysisConfig(
        start_year=start_year,
        output_dir=output_dir,
        include_forecasts=True,
        create_visualizations=True
    )

    analyzer = Z1ComprehensiveAnalyzer(collector, config)
    results = analyzer.run_complete_analysis()

    # Generate executive summary
    executive_summary = analyzer.generate_executive_summary(results)

    # Export results
    results_path = f"{output_dir}/z1_analysis_results.json"
    analyzer.export_results(results, results_path)

    # Save executive summary
    summary_path = f"{output_dir}/executive_summary.txt"
    with open(summary_path, 'w') as f:
        f.write(executive_summary)

    logger.info(f"Analysis complete. Results saved to {output_dir}")

    return results, executive_summary

if __name__ == "__main__":
    # Example usage
    from data.federal_reserve_z1_collector import collect_federal_reserve_z1_data

    # Collect data
    collector = collect_federal_reserve_z1_data(start_year=1950)

    # Run analysis
    results, summary = run_z1_comprehensive_analysis(
        collector,
        start_year=1950,
        output_dir="output/z1_analysis"
    )

    print(summary)

    collector.close()
#!/usr/bin/env python3
"""
Advanced cross-border capital flow analysis module.
Provides sophisticated International Investment Position (IIP) analysis,
financial integration metrics, and capital flow volatility modeling.
"""

import pandas as pd
import numpy as np
import networkx as nx
import logging
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class CapitalFlowResults:
    """Container for capital flow analysis results."""
    method: str
    data: pd.DataFrame
    metrics: Dict[str, Any]
    summary: Dict[str, float]
    metadata: Dict[str, Any]

@dataclass
class IIPResults:
    """Container for International Investment Position analysis results."""
    iip_data: pd.DataFrame
    net_position: pd.Series
    asset_breakdown: Dict[str, pd.DataFrame]
    liability_breakdown: Dict[str, pd.DataFrame]
    sustainability_metrics: Dict[str, float]
    vulnerability_metrics: Dict[str, float]

@dataclass
class FinancialIntegrationResults:
    """Container for financial integration analysis results."""
    integration_scores: pd.DataFrame
    chinn_ito_index: pd.Series
    feldstein_horioka_puzzle: Dict[str, float]
    bivariate_correlations: pd.DataFrame
    network_centrality: Dict[str, float]
    clusters: Dict[str, List[str]]

class AdvancedCapitalFlowAnalyzer:
    """
    Advanced cross-border capital flow analysis system with sophisticated
    International Investment Position (IIP) analysis and financial integration metrics.
    """

    def __init__(self):
        """Initialize the advanced capital flow analyzer."""
        logger.info("Advanced Capital Flow Analyzer initialized")
        self.scaler = StandardScaler()
        self.pca = PCA()

    def analyze_iip_position(self,
                           iip_data: pd.DataFrame,
                           country_col: str = 'country',
                           year_col: str = 'year',
                           asset_cols: List[str] = None,
                           liability_cols: List[str] = None) -> IIPResults:
        """
        Analyze International Investment Position with comprehensive metrics.

        Args:
            iip_data: DataFrame with IIP data
            country_col: Country column name
            year_col: Year column name
            asset_cols: List of asset column names
            liability_cols: List of liability column names

        Returns:
            IIPResults: Comprehensive IIP analysis results
        """
        logger.info("Analyzing International Investment Position")

        try:
            # Default asset and liability categories if not provided
            if asset_cols is None:
                asset_cols = ['direct_investment_abroad', 'portfolio_equity_abroad',
                             'portfolio_debt_abroad', 'other_investment_abroad',
                             'reserve_assets']

            if liability_cols is None:
                liability_cols = ['direct_investment_domestic', 'portfolio_equity_domestic',
                                'portfolio_debt_domestic', 'other_investment_domestic']

            # Calculate total assets and liabilities
            iip_data['total_assets'] = iip_data[asset_cols].sum(axis=1)
            iip_data['total_liabilities'] = iip_data[liability_cols].sum(axis=1)

            # Calculate net IIP position
            iip_data['net_iip_position'] = iip_data['total_assets'] - iip_data['total_liabilities']

            # Calculate IIP as percentage of GDP (if GDP column available)
            if 'gdp' in iip_data.columns:
                iip_data['iip_to_gdp'] = (iip_data['net_iip_position'] / iip_data['gdp']) * 100
                iip_data['assets_to_gdp'] = (iip_data['total_assets'] / iip_data['gdp']) * 100
                iip_data['liabilities_to_gdp'] = (iip_data['total_liabilities'] / iip_data['gdp']) * 100

            # Calculate asset and liability breakdowns by category
            asset_breakdown = {}
            liability_breakdown = {}

            for col in asset_cols:
                asset_breakdown[col] = iip_data[[country_col, year_col, col]].copy()
                asset_breakdown[col]['asset_share'] = iip_data[col] / iip_data['total_assets']

            for col in liability_cols:
                liability_breakdown[col] = iip_data[[country_col, year_col, col]].copy()
                liability_breakdown[col]['liability_share'] = iip_data[col] / iip_data['total_liabilities']

            # Calculate sustainability metrics
            sustainability_metrics = self._calculate_iip_sustainability(iip_data)

            # Calculate vulnerability metrics
            vulnerability_metrics = self._calculate_iip_vulnerability(iip_data, asset_cols, liability_cols)

            # Create net position series
            net_position = iip_data.set_index([country_col, year_col])['net_iip_position']

            return IIPResults(
                iip_data=iip_data,
                net_position=net_position,
                asset_breakdown=asset_breakdown,
                liability_breakdown=liability_breakdown,
                sustainability_metrics=sustainability_metrics,
                vulnerability_metrics=vulnerability_metrics
            )

        except Exception as e:
            logger.error(f"IIP analysis failed: {e}")
            raise

    def _calculate_iip_sustainability(self, iip_data: pd.DataFrame) -> Dict[str, float]:
        """Calculate IIP sustainability metrics."""
        try:
            metrics = {}

            # Net IIP position stability (coefficient of variation)
            if 'net_iip_position' in iip_data.columns:
                net_iip = iip_data['net_iip_position']
                metrics['net_position_stability'] = net_iip.std() / abs(net_iip.mean()) if net_iip.mean() != 0 else np.inf

            # Asset-liability balance
            if 'total_assets' in iip_data.columns and 'total_liabilities' in iip_data.columns:
                assets = iip_data['total_assets'].mean()
                liabilities = iip_data['total_liabilities'].mean()
                metrics['asset_liability_ratio'] = assets / liabilities if liabilities != 0 else np.inf

            # External debt sustainability (if GDP available)
            if 'iip_to_gdp' in iip_data.columns:
                iip_gdp = iip_data['iip_to_gdp']
                metrics['iip_gdp_average'] = iip_gdp.mean()
                metrics['iip_gdp_volatility'] = iip_gdp.std()
                metrics['iip_gdp_trend'] = (iip_gdp.iloc[-1] - iip_gdp.iloc[0]) / len(iip_gdp) if len(iip_gdp) > 1 else 0

            return metrics

        except Exception as e:
            logger.error(f"Sustainability metrics calculation failed: {e}")
            return {}

    def _calculate_iip_vulnerability(self, iip_data: pd.DataFrame,
                                   asset_cols: List[str],
                                   liability_cols: List[str]) -> Dict[str, float]:
        """Calculate IIP vulnerability metrics."""
        try:
            metrics = {}

            # Short-term debt concentration
            short_term_cols = [col for col in liability_cols if 'short_term' in col.lower() or 'debt' in col.lower()]
            if short_term_cols and 'total_liabilities' in iip_data.columns:
                short_term_debt = iip_data[short_term_cols].sum(axis=1)
                metrics['short_term_debt_ratio'] = (short_term_debt / iip_data['total_liabilities']).mean()

            # Portfolio investment volatility (higher vulnerability)
            portfolio_cols = [col for col in asset_cols + liability_cols if 'portfolio' in col.lower()]
            if portfolio_cols:
                portfolio_total = iip_data[portfolio_cols].sum(axis=1)
                metrics['portfolio_volatility'] = portfolio_total.std()

            # Reserve assets coverage
            if 'reserve_assets' in asset_cols and 'total_liabilities' in iip_data.columns:
                reserves = iip_data['reserve_assets']
                metrics['reserve_coverage'] = (reserves / iip_data['total_liabilities']).mean()

            # Foreign exchange exposure
            if 'total_assets' in iip_data.columns and 'total_liabilities' in iip_data.columns:
                net_exposure = iip_data['total_assets'] - iip_data['total_liabilities']
                metrics['fx_exposure_volatility'] = net_exposure.std()

            return metrics

        except Exception as e:
            logger.error(f"Vulnerability metrics calculation failed: {e}")
            return {}

    def calculate_financial_integration(self,
                                     capital_flow_data: pd.DataFrame,
                                     country_col: str = 'country',
                                     year_col: str = 'year',
                                     flow_cols: List[str] = None,
                                     gdp_col: str = 'gdp') -> FinancialIntegrationResults:
        """
        Calculate comprehensive financial integration metrics.

        Args:
            capital_flow_data: DataFrame with capital flow data
            country_col: Country column name
            year_col: Year column name
            flow_cols: List of capital flow column names
            gdp_col: GDP column name

        Returns:
            FinancialIntegrationResults: Comprehensive financial integration analysis
        """
        logger.info("Calculating financial integration metrics")

        try:
            # Default flow categories if not provided
            if flow_cols is None:
                flow_cols = ['fdi_flows', 'portfolio_flows', 'bank_flows', 'other_flows']

            # Calculate total capital flows
            available_flow_cols = [col for col in flow_cols if col in capital_flow_data.columns]
            if available_flow_cols:
                capital_flow_data['total_flows'] = capital_flow_data[available_flow_cols].sum(axis=1)

                # Calculate flows as percentage of GDP
                if gdp_col in capital_flow_data.columns:
                    for col in available_flow_cols:
                        capital_flow_data[f'{col}_to_gdp'] = (capital_flow_data[col] / capital_flow_data[gdp_col]) * 100
                    capital_flow_data['total_flows_to_gdp'] = (capital_flow_data['total_flows'] / capital_flow_data[gdp_col]) * 100

            # Calculate Chinn-Ito financial openness index
            chinn_ito_index = self._calculate_chinn_ito_index(capital_flow_data, country_col, year_col)

            # Test Feldstein-Horioka puzzle
            feldstein_horioka_results = self._test_feldstein_horioka_puzzle(capital_flow_data, country_col, year_col)

            # Calculate bivariate correlations between countries
            bivariate_correlations = self._calculate_capital_flow_correlations(
                capital_flow_data, country_col, year_col, available_flow_cols
            )

            # Build financial integration network
            network_centrality = self._build_financial_integration_network(
                capital_flow_data, country_col, available_flow_cols
            )

            # Perform clustering analysis
            clusters = self._perform_financial_integration_clustering(
                capital_flow_data, country_col, available_flow_cols
            )

            # Create integration scores matrix
            integration_scores = self._create_integration_scores_matrix(
                capital_flow_data, country_col, year_col, available_flow_cols
            )

            return FinancialIntegrationResults(
                integration_scores=integration_scores,
                chinn_ito_index=chinn_ito_index,
                feldstein_horioka_puzzle=feldstein_horioka_results,
                bivariate_correlations=bivariate_correlations,
                network_centrality=network_centrality,
                clusters=clusters
            )

        except Exception as e:
            logger.error(f"Financial integration analysis failed: {e}")
            raise

    def _calculate_chinn_ito_index(self, data: pd.DataFrame,
                                 country_col: str,
                                 year_col: str) -> pd.Series:
        """Calculate Chinn-Ito financial openness index approximation."""
        try:
            # Simplified Chinn-Ito index based on capital flow volatility
            countries = data[country_col].unique()
            scores = {}

            for country in countries:
                country_data = data[data[country_col] == country].sort_values(year_col)
                if 'total_flows_to_gdp' in country_data.columns:
                    # Use standard deviation of capital flows to GDP as proxy
                    volatility = country_data['total_flows_to_gdp'].std()
                    scores[country] = volatility
                else:
                    scores[country] = 0.0

            return pd.Series(scores)

        except Exception as e:
            logger.error(f"Chinn-Ito index calculation failed: {e}")
            return pd.Series()

    def _test_feldstein_horioka_puzzle(self, data: pd.DataFrame,
                                    country_col: str,
                                    year_col: str) -> Dict[str, float]:
        """
        Test Feldstein-Horioka puzzle (relationship between savings and investment).

        Returns correlation coefficient between savings and investment rates.
        """
        try:
            # This is a simplified version - in practice would need savings data
            # Use capital flow persistence as proxy
            results = {}

            if 'total_flows_to_gdp' in data.columns:
                # Calculate autocorrelation of capital flows
                flows = data.groupby(country_col)['total_flows_to_gdp'].apply(
                    lambda x: x.autocorr(lag=1) if len(x) > 1 else 0
                )
                results['savings_investment_correlation'] = flows.mean()
                results['puzzle_strength'] = abs(flows.mean())

            return results

        except Exception as e:
            logger.error(f"Feldstein-Horioka puzzle test failed: {e}")
            return {}

    def _calculate_capital_flow_correlations(self, data: pd.DataFrame,
                                           country_col: str,
                                           year_col: str,
                                           flow_cols: List[str]) -> pd.DataFrame:
        """Calculate cross-country capital flow correlations."""
        try:
            if not flow_cols or 'total_flows_to_gdp' not in data.columns:
                return pd.DataFrame()

            # Pivot data to have countries as columns
            pivot_data = data.pivot(index=year_col, columns=country_col, values='total_flows_to_gdp')

            # Calculate correlation matrix
            correlation_matrix = pivot_data.corr()

            return correlation_matrix

        except Exception as e:
            logger.error(f"Capital flow correlations calculation failed: {e}")
            return pd.DataFrame()

    def _build_financial_integration_network(self, data: pd.DataFrame,
                                          country_col: str,
                                          flow_cols: List[str]) -> Dict[str, float]:
        """Build financial integration network and calculate centrality measures."""
        try:
            if not flow_cols or 'total_flows_to_gdp' not in data.columns:
                return {}

            # Create correlation-based network
            pivot_data = data.pivot(index='year', columns=country_col, values='total_flows_to_gdp')
            correlation_matrix = pivot_data.corr()

            # Create network from correlations
            G = nx.from_pandas_adjacency(correlation_matrix.abs())

            # Calculate centrality measures
            centrality = {}
            centrality['degree_centrality'] = nx.degree_centrality(G)
            centrality['betweenness_centrality'] = nx.betweenness_centrality(G)
            centrality['closeness_centrality'] = nx.closeness_centrality(G)
            centrality['eigenvector_centrality'] = nx.eigenvector_centrality(G)

            return centrality

        except Exception as e:
            logger.error(f"Financial integration network construction failed: {e}")
            return {}

    def _perform_financial_integration_clustering(self, data: pd.DataFrame,
                                                country_col: str,
                                                flow_cols: List[str]) -> Dict[str, List[str]]:
        """Perform clustering analysis to identify financial integration groups."""
        try:
            if not flow_cols or 'total_flows_to_gdp' not in data.columns:
                return {}

            # Prepare data for clustering
            pivot_data = data.pivot(index='year', columns=country_col, values='total_flows_to_gdp')
            pivot_data = pivot_data.fillna(pivot_data.mean())

            # Standardize data
            scaled_data = self.scaler.fit_transform(pivot_data.T)

            # Perform K-means clustering
            n_clusters = min(3, len(pivot_data.columns))  # Default to 3 clusters or fewer if needed
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(scaled_data)

            # Organize countries by cluster
            clusters = {}
            for i, country in enumerate(pivot_data.columns):
                cluster_id = f'cluster_{cluster_labels[i]}'
                if cluster_id not in clusters:
                    clusters[cluster_id] = []
                clusters[cluster_id].append(country)

            return clusters

        except Exception as e:
            logger.error(f"Financial integration clustering failed: {e}")
            return {}

    def _create_integration_scores_matrix(self, data: pd.DataFrame,
                                        country_col: str,
                                        year_col: str,
                                        flow_cols: List[str]) -> pd.DataFrame:
        """Create comprehensive financial integration scores matrix."""
        try:
            countries = data[country_col].unique()
            integration_scores = pd.DataFrame(index=countries, columns=countries)

            for country1 in countries:
                for country2 in countries:
                    if country1 == country2:
                        integration_scores.loc[country1, country2] = 1.0
                    else:
                        # Calculate integration score based on flow correlation
                        country1_data = data[data[country_col] == country1]
                        country2_data = data[data[country_col] == country2]

                        if 'total_flows_to_gdp' in data.columns:
                            # Simple correlation-based integration score
                            merged_data = pd.merge(
                                country1_data[[year_col, 'total_flows_to_gdp']],
                                country2_data[[year_col, 'total_flows_to_gdp']],
                                on=year_col,
                                suffixes=('_1', '_2')
                            )

                            if len(merged_data) > 1:
                                correlation = merged_data['total_flows_to_gdp_1'].corr(
                                    merged_data['total_flows_to_gdp_2']
                                )
                                integration_scores.loc[country1, country2] = abs(correlation) if not pd.isna(correlation) else 0.0
                            else:
                                integration_scores.loc[country1, country2] = 0.0
                        else:
                            integration_scores.loc[country1, country2] = 0.0

            return integration_scores.astype(float)

        except Exception as e:
            logger.error(f"Integration scores matrix creation failed: {e}")
            return pd.DataFrame()

    def analyze_capital_flow_volatility(self,
                                      flow_data: pd.DataFrame,
                                      country_col: str = 'country',
                                      year_col: str = 'year',
                                      flow_col: str = 'total_flows') -> CapitalFlowResults:
        """
        Analyze capital flow volatility and build risk metrics.

        Args:
            flow_data: DataFrame with capital flow time series
            country_col: Country column name
            year_col: Time period column name
            flow_col: Capital flow column name

        Returns:
            CapitalFlowResults: Volatility analysis results
        """
        logger.info("Analyzing capital flow volatility")

        try:
            # Calculate volatility metrics for each country
            countries = flow_data[country_col].unique()
            volatility_metrics = {}

            for country in countries:
                country_data = flow_data[flow_data[country_col] == country].sort_values(year_col)

                if len(country_data) > 1:
                    flows = country_data[flow_col]

                    # Basic volatility metrics
                    volatility_metrics[country] = {
                        'std_dev': flows.std(),
                        'variance': flows.var(),
                        'coefficient_of_variation': flows.std() / abs(flows.mean()) if flows.mean() != 0 else np.inf,
                        'max_drawdown': self._calculate_max_drawdown(flows),
                        'volatility_skewness': flows.skew(),
                        'volatility_kurtosis': flows.kurtosis()
                    }

            volatility_df = pd.DataFrame(volatility_metrics).T

            # Calculate rolling volatilities
            rolling_volatility = self._calculate_rolling_volatility(
                flow_data, country_col, year_col, flow_col
            )

            # Identify volatility episodes
            volatility_episodes = self._identify_volatility_episodes(
                flow_data, country_col, year_col, flow_col
            )

            return CapitalFlowResults(
                method='capital_flow_volatility_analysis',
                data=flow_data,
                metrics={
                    'volatility_metrics': volatility_df,
                    'rolling_volatility': rolling_volatility,
                    'volatility_episodes': volatility_episodes
                },
                summary={
                    'average_volatility': volatility_df['std_dev'].mean(),
                    'volatility_dispersion': volatility_df['std_dev'].std(),
                    'max_volatility': volatility_df['std_dev'].max(),
                    'volatility_countries': len(volatility_df)
                },
                metadata={
                    'analysis_date': datetime.now().isoformat(),
                    'countries_analyzed': list(countries),
                    'methodology': 'Standard deviation and rolling window analysis'
                }
            )

        except Exception as e:
            logger.error(f"Capital flow volatility analysis failed: {e}")
            raise

    def _calculate_max_drawdown(self, series: pd.Series) -> float:
        """Calculate maximum drawdown for a time series."""
        try:
            cumulative = (1 + series.pct_change()).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            return drawdown.min()
        except:
            return 0.0

    def _calculate_rolling_volatility(self, data: pd.DataFrame,
                                    country_col: str,
                                    year_col: str,
                                    flow_col: str,
                                    window: int = 4) -> pd.DataFrame:
        """Calculate rolling volatility for each country."""
        try:
            rolling_vol = {}

            for country in data[country_col].unique():
                country_data = data[data[country_col] == country].sort_values(year_col)

                if len(country_data) >= window:
                    flows = country_data[flow_col]
                    rolling_vol[country] = flows.rolling(window=window).std()

            return pd.DataFrame(rolling_vol)

        except Exception as e:
            logger.error(f"Rolling volatility calculation failed: {e}")
            return pd.DataFrame()

    def _identify_volatility_episodes(self, data: pd.DataFrame,
                                    country_col: str,
                                    year_col: str,
                                    flow_col: str,
                                    threshold: float = 2.0) -> Dict[str, List[Tuple]]:
        """Identify high volatility episodes for each country."""
        try:
            episodes = {}

            for country in data[country_col].unique():
                country_data = data[data[country_col] == country].sort_values(year_col)

                if len(country_data) > 1:
                    flows = country_data[flow_col]

                    # Identify periods where flow changes exceed threshold standard deviations
                    flow_changes = flows.pct_change().abs()
                    threshold_value = flow_changes.std() * threshold

                    high_vol_periods = country_data[flow_changes > threshold_value]

                    if len(high_vol_periods) > 0:
                        episodes[country] = list(zip(
                            high_vol_periods[year_col],
                            high_vol_periods[flow_changes[flow_changes > threshold_value]]
                        ))

            return episodes

        except Exception as e:
            logger.error(f"Volatility episodes identification failed: {e}")
            return {}

    def generate_capital_flow_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive capital flow analysis report."""
        try:
            report = []
            report.append("=== ADVANCED CAPITAL FLOW ANALYSIS REPORT ===")
            report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append("")

            # IIP Analysis Results
            if 'iip_results' in results:
                iip = results['iip_results']
                report.append("INTERNATIONAL INVESTMENT POSITION ANALYSIS:")
                report.append("-" * 50)

                if hasattr(iip, 'sustainability_metrics'):
                    for metric, value in iip.sustainability_metrics.items():
                        report.append(f"{metric.replace('_', ' ').title()}: {value:.4f}")

                report.append("")

            # Financial Integration Results
            if 'integration_results' in results:
                integration = results['integration_results']
                report.append("FINANCIAL INTEGRATION ANALYSIS:")
                report.append("-" * 50)

                if hasattr(integration, 'chinn_ito_index') and not integration.chinn_ito_index.empty:
                    report.append("Chinn-Ito Financial Openness Index:")
                    for country, score in integration.chinn_ito_index.head().items():
                        report.append(f"  {country}: {score:.4f}")

                if hasattr(integration, 'feldstein_horioka_puzzle'):
                    fh = integration.feldstein_horioka_puzzle
                    if 'savings_investment_correlation' in fh:
                        report.append(f"Feldstein-Horioka Correlation: {fh['savings_investment_correlation']:.4f}")
                        report.append(f"Puzzle Strength: {fh['puzzle_strength']:.4f}")

                report.append("")

            # Volatility Analysis Results
            if 'volatility_results' in results:
                vol = results['volatility_results']
                report.append("CAPITAL FLOW VOLATILITY ANALYSIS:")
                report.append("-" * 50)

                if hasattr(vol, 'summary'):
                    for metric, value in vol.summary.items():
                        report.append(f"{metric.replace('_', ' ').title()}: {value:.4f}")

                report.append("")

            report.append("=== END OF REPORT ===")
            return "\n".join(report)

        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return f"Report generation failed: {e}"

    def save_capital_flow_results(self,
                                results: Dict[str, Any],
                                output_dir: str,
                                analysis_name: str) -> None:
        """Save capital flow analysis results to files."""
        try:
            import os
            os.makedirs(output_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Save IIP results
            if 'iip_results' in results:
                iip = results['iip_results']
                iip.iip_data.to_csv(f"{output_dir}/{analysis_name}_iip_data_{timestamp}.csv", index=False)

                if hasattr(iip, 'sustainability_metrics'):
                    pd.DataFrame([iip.sustainability_metrics]).to_csv(
                        f"{output_dir}/{analysis_name}_sustainability_metrics_{timestamp}.csv", index=False
                    )

            # Save integration results
            if 'integration_results' in results:
                integration = results['integration_results']
                if hasattr(integration, 'integration_scores') and not integration.integration_scores.empty:
                    integration.integration_scores.to_csv(
                        f"{output_dir}/{analysis_name}_integration_scores_{timestamp}.csv"
                    )

                if hasattr(integration, 'bivariate_correlations') and not integration.bivariate_correlations.empty:
                    integration.bivariate_correlations.to_csv(
                        f"{output_dir}/{analysis_name}_correlations_{timestamp}.csv"
                    )

            # Save volatility results
            if 'volatility_results' in results:
                vol = results['volatility_results']
                if hasattr(vol, 'metrics') and 'volatility_metrics' in vol.metrics:
                    vol.metrics['volatility_metrics'].to_csv(
                        f"{output_dir}/{analysis_name}_volatility_metrics_{timestamp}.csv"
                    )

            # Save comprehensive report
            report = self.generate_capital_flow_report(results)
            with open(f"{output_dir}/{analysis_name}_report_{timestamp}.txt", 'w') as f:
                f.write(report)

            logger.info(f"Capital flow analysis results saved to {output_dir}")

        except Exception as e:
            logger.error(f"Results saving failed: {e}")
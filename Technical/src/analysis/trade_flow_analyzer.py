"""
Advanced Trade Flow Analysis Tools
================================

Sophisticated trade flow analysis for international economics.

Provides advanced trade analysis capabilities:
- Gravity model estimation and prediction
- Trade intensity indices and complementarity analysis
- Bilateral trade flow matrices
- Network analysis of international trade relationships
- Trade elasticity estimation
- Trade concentration and diversification metrics

This module transforms trade data into sophisticated network
and econometric analysis suitable for research and policy analysis.

Author: Lewis Platform
Date: 2025-10-27
Version: 1.0 - Advanced Trade Analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import List, Dict, Optional, Union, Tuple
from datetime import datetime, timedelta
import warnings
import logging

# Scientific computing imports
from scipy import stats
from scipy.optimize import minimize
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import pairwise_distances
import networkx as nx

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')


class AdvancedTradeFlowAnalyzer:
    """
    Advanced trade flow analysis system with gravity models and network analysis.

    Provides sophisticated tools for analyzing international trade patterns,
    estimating gravity models, and understanding trade network structures.
    """

    def __init__(self):
        """Initialize the trade flow analyzer."""
        self.gravity_models = {}
        self.trade_networks = {}
        self.analysis_results = {}

        logger.info("Advanced Trade Flow Analyzer initialized")

    def prepare_bilateral_trade_data(self, trade_data: pd.DataFrame,
                                    country_column: str = 'country',
                                    value_column: str = 'value',
                                    year_column: str = 'year') -> pd.DataFrame:
        """
        Prepare bilateral trade data for analysis.

        Args:
            trade_data: Input trade data
            country_column: Column name for countries
            value_column: Column name for trade values
            year_column: Column name for years

        Returns:
            Prepared bilateral trade data
        """
        logger.info(f"Preparing bilateral trade data from {len(trade_data)} observations")

        # Make a copy to avoid modifying original
        df = trade_data.copy()

        # Ensure required columns exist
        required_cols = [country_column, value_column, year_column]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Clean data
        df = df.dropna(subset=required_cols)
        df[value_column] = pd.to_numeric(df[value_column], errors='coerce')
        df = df.dropna(subset=[value_column])

        # Filter out zero or negative values for exports/imports
        df = df[df[value_column] > 0]

        logger.info(f"Prepared bilateral trade data: {len(df)} observations")
        return df

    def estimate_gravity_model(self, trade_data: pd.DataFrame,
                             exporter_col: str,
                             importer_col: str,
                             trade_value_col: str,
                             exporter_gdp_col: str,
                             importer_gdp_col: str,
                             distance_col: str,
                             include_dummies: bool = True) -> Dict:
        """
        Estimate gravity model of bilateral trade.

        Args:
            trade_data: Bilateral trade data
            exporter_col: Exporter country column
            importer_col: Importer country column
            trade_value_col: Trade value column
            exporter_gdp_col: Exporter GDP column
            importer_gdp_col: Importer GDP column
            distance_col: Distance column
            include_dummies: Whether to include country fixed effects

        Returns:
            Dictionary with gravity model results
        """
        logger.info("Estimating gravity model of bilateral trade")

        results = {}

        try:
            # Prepare data for regression
            df = trade_data.copy()

            # Log transform variables (standard gravity model specification)
            df['log_trade'] = np.log(df[trade_value_col])
            df['log_exporter_gdp'] = np.log(df[exporter_gdp_col])
            df['log_importer_gdp'] = np.log(df[importer_gdp_col])
            df['log_distance'] = np.log(df[distance_col])

            # Select variables for regression
            reg_vars = ['log_trade', 'log_exporter_gdp', 'log_importer_gdp', 'log_distance']

            if include_dummies:
                # Add exporter and importer fixed effects
                df = pd.get_dummies(df, columns=[exporter_col, importer_col], drop_first=True)
                dummy_cols = [col for col in df.columns if col.startswith(f'{exporter_col}_') or col.startswith(f'{importer_col}_')]
                reg_vars.extend(dummy_cols)

            regression_df = df[reg_vars].dropna()

            # Separate dependent and independent variables
            y = regression_df['log_trade']
            X = regression_df.drop('log_trade', axis=1)

            # Add constant
            X = np.column_stack([np.ones(len(X)), X])

            # Estimate model using OLS
            X_T_X = X.T @ X
            X_T_y = X.T @ y
            beta = np.linalg.solve(X_T_X, X_T_y)

            # Calculate statistics
            n, k = X.shape
            residuals = y - X @ beta
            sse = np.sum(residuals**2)
            mse = sse / (n - k)
            variance_beta = mse * np.linalg.inv(X_T_X)
            std_errors = np.sqrt(np.diag(variance_beta))

            # R-squared
            tss = np.sum((y - np.mean(y))**2)
            r_squared = 1 - sse / tss

            # Get variable names
            var_names = ['constant'] + [col for col in regression_df.columns if col != 'log_trade']

            # Organize results
            coefficients = {}
            for i, var_name in enumerate(var_names):
                coefficients[var_name] = {
                    'coefficient': beta[i],
                    'std_error': std_errors[i],
                    't_statistic': beta[i] / std_errors[i],
                    'p_value': 2 * (1 - stats.t.cdf(abs(beta[i] / std_errors[i]), n - k))
                }

            results['coefficients'] = coefficients
            results['model_statistics'] = {
                'n_observations': n,
                'n_variables': k,
                'r_squared': r_squared,
                'adjusted_r_squared': 1 - (1 - r_squared) * (n - 1) / (n - k),
                'mse': mse,
                'rmse': np.sqrt(mse),
                'residuals': residuals
            }

            # Model interpretation
            results['interpretation'] = {
                'exporter_gdp_elasticity': coefficients.get('log_exporter_gdp', {}).get('coefficient', 0),
                'importer_gdp_elasticity': coefficients.get('log_importer_gdp', {}).get('coefficient', 0),
                'distance_elasticity': coefficients.get('log_distance', {}).get('coefficient', 0),
                'significance': {
                    'exporter_gdp': coefficients.get('log_exporter_gdp', {}).get('p_value', 1) < 0.05,
                    'importer_gdp': coefficients.get('log_importer_gdp', {}).get('p_value', 1) < 0.05,
                    'distance': coefficients.get('log_distance', {}).get('p_value', 1) < 0.05
                }
            }

            logger.info(f"Gravity model estimated successfully (R²: {r_squared:.3f})")

        except Exception as e:
            logger.error(f"Gravity model estimation failed: {e}")
            results['error'] = str(e)

        return results

    def predict_trade_flows(self, gravity_model: Dict,
                           new_trade_pairs: pd.DataFrame,
                           exporter_gdp_col: str,
                           importer_gdp_col: str,
                           distance_col: str) -> pd.DataFrame:
        """
        Predict trade flows using estimated gravity model.

        Args:
            gravity_model: Estimated gravity model results
            new_trade_pairs: New trade pairs to predict
            exporter_gdp_col: Exporter GDP column
            importer_gdp_col: Importer GDP column
            distance_col: Distance column

        Returns:
            DataFrame with predicted trade flows
        """
        logger.info(f"Predicting trade flows for {len(new_trade_pairs)} pairs")

        if 'coefficients' not in gravity_model:
            raise ValueError("Gravity model coefficients not found")

        try:
            df = new_trade_pairs.copy()

            # Calculate predicted log trade
            df['log_exporter_gdp'] = np.log(df[exporter_gdp_col])
            df['log_importer_gdp'] = np.log(df[importer_gdp_col])
            df['log_distance'] = np.log(df[distance_col])

            # Get coefficients
            coeffs = gravity_model['coefficients']

            # Calculate predicted log trade
            df['predicted_log_trade'] = (
                coeffs.get('constant', {}).get('coefficient', 0) +
                coeffs.get('log_exporter_gdp', {}).get('coefficient', 0) * df['log_exporter_gdp'] +
                coeffs.get('log_importer_gdp', {}).get('coefficient', 0) * df['log_importer_gdp'] +
                coeffs.get('log_distance', {}).get('coefficient', 0) * df['log_distance']
            )

            # Convert back to levels
            df['predicted_trade'] = np.exp(df['predicted_log_trade'])

            # Calculate prediction intervals (simplified)
            model_stats = gravity_model.get('model_statistics', {})
            rmse = model_stats.get('rmse', 0)

            df['prediction_lower'] = np.exp(df['predicted_log_trade'] - 1.96 * rmse)
            df['prediction_upper'] = np.exp(df['predicted_log_trade'] + 1.96 * rmse)

            logger.info(f"Trade flow predictions generated successfully")

        except Exception as e:
            logger.error(f"Trade flow prediction failed: {e}")
            df = new_trade_pairs.copy()

        return df

    def calculate_trade_intensity_index(self, trade_data: pd.DataFrame,
                                      gdp_data: pd.DataFrame,
                                      country_col: str,
                                      value_col: str,
                                      gdp_col: str) -> pd.DataFrame:
        """
        Calculate trade intensity index (trade as % of GDP).

        Args:
            trade_data: Trade data
            gdp_data: GDP data
            country_col: Country column name
            value_col: Trade value column
            gdp_col: GDP column name

        Returns:
            DataFrame with trade intensity indices
        """
        logger.info("Calculating trade intensity indices")

        try:
            # Merge trade and GDP data
            merged = pd.merge(trade_data, gdp_data, on=country_col, how='inner')

            # Calculate trade intensity
            merged['trade_intensity'] = (merged[value_col] / merged[gdp_col]) * 100

            # Calculate descriptive statistics by country
            intensity_stats = merged.groupby(country_col)['trade_intensity'].agg([
                'mean', 'std', 'min', 'max', 'count'
            ]).reset_index()

            # Calculate trade intensity growth rates
            merged_yearly = merged.groupby([country_col, merged[country_col].str[:4].astype(int)])['trade_intensity'].mean().reset_index()
            merged_yearly.columns = [country_col, 'year', 'intensity']

            intensity_growth = []
            for country in merged_yearly[country_col].unique():
                country_data = merged_yearly[merged_yearly[country_col] == country].sort_values('year')
                if len(country_data) > 1:
                    growth_rates = country_data['intensity'].pct_change().dropna()
                    avg_growth = growth_rates.mean()
                    intensity_growth.append({
                        country_col: country,
                        'avg_growth_rate': avg_growth,
                        'growth_volatility': growth_rates.std()
                    })

            growth_df = pd.DataFrame(intensity_growth)

            results = {
                'intensity_data': merged,
                'intensity_stats': intensity_stats,
                'growth_rates': growth_df
            }

            logger.info(f"Trade intensity indices calculated for {len(intensity_stats)} countries")

        except Exception as e:
            logger.error(f"Trade intensity calculation failed: {e}")
            results = {'error': str(e)}

        return results

    def build_trade_network(self, bilateral_data: pd.DataFrame,
                            exporter_col: str,
                            importer_col: str,
                            value_col: str,
                            min_trade_value: float = 1000) -> nx.DiGraph:
        """
        Build international trade network.

        Args:
            bilateral_data: Bilateral trade data
            exporter_col: Exporter column
            importer_col: Importer column
            value_col: Trade value column
            min_trade_value: Minimum trade value to include edge

        Returns:
            NetworkX directed graph
        """
        logger.info("Building international trade network")

        try:
            # Create directed graph
            G = nx.DiGraph()

            # Add nodes (countries)
            exporters = set(bilateral_data[exporter_col].unique())
            importers = set(bilateral_data[importer_col].unique())
            all_countries = exporters.union(importers)

            for country in all_countries:
                G.add_node(country)

            # Add edges (trade flows)
            for _, row in bilateral_data.iterrows():
                exporter = row[exporter_col]
                importer = row[importer_col]
                trade_value = row[value_col]

                if trade_value >= min_trade_value:
                    G.add_edge(exporter, importer, weight=trade_value)

            # Calculate network metrics
            results = {
                'network': G,
                'nodes': G.number_of_nodes(),
                'edges': G.number_of_edges(),
                'density': nx.density(G),
                'is_strongly_connected': nx.is_strongly_connected(G),
                'weakly_connected_components': nx.number_weakly_connected_components(G)
            }

            # Calculate centrality measures
            results['centrality'] = {
                'degree_centrality': nx.degree_centrality(G),
                'betweenness_centrality': nx.betweenness_centrality(G),
                'closeness_centrality': nx.closeness_centrality(G),
                'eigenvector_centrality': nx.eigenvector_centrality(G, max_iter=1000)
            }

            # Calculate trade statistics
            in_degrees = dict(G.in_degree(weight='weight'))
            out_degrees = dict(G.out_degree(weight='weight'))
            results['trade_stats'] = {
                'total_exports': sum(out_degrees.values()),
                'total_imports': sum(in_degrees.values()),
                'net_exports': {country: out_degrees.get(country, 0) - in_degrees.get(country, 0)
                              for country in all_countries}
            }

            self.trade_networks['bilateral'] = results

            logger.info(f"Trade network built: {results['nodes']} nodes, {results['edges']} edges")

        except Exception as e:
            logger.error(f"Trade network construction failed: {e}")
            G = nx.DiGraph()

        return G

    def calculate_trade_complementarity(self, trade_data: pd.DataFrame,
                                       exporter_col: str,
                                       importer_col: str,
                                       value_col: str,
                                       gdp_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate trade complementarity indices between countries.

        Args:
            trade_data: Bilateral trade data
            exporter_col: Exporter column
            importer_col: Importer column
            value_col: Trade value column
            gdp_data: GDP data for normalization

        Returns:
            DataFrame with complementarity indices
        """
        logger.info("Calculating trade complementarity indices")

        try:
            # Create country pairs matrix
            countries = sorted(list(set(trade_data[exporter_col].unique()) | set(trade_data[importer_col].unique())))
            n_countries = len(countries)

            # Initialize matrices
            trade_matrix = pd.DataFrame(0.0, index=countries, columns=countries)
            gdp_series = pd.Series(gdp_data.set_index('country')['gdp']).reindex(countries)

            # Fill trade matrix
            for _, row in trade_data.iterrows():
                exporter = row[exporter_col]
                importer = row[importer_col]
                value = row[value_col]

                if exporter in countries and importer in countries:
                    trade_matrix.loc[exporter, importer] = value

            # Calculate complementarity index
            complementarity_matrix = pd.DataFrame(0.0, index=countries, columns=countries)

            for i, country_i in enumerate(countries):
                for j, country_j in enumerate(countries):
                    if i != j:
                        # Complementarity = 1 - |(Trade_ij/GDP_i) - (Trade_ji/GDP_j)| / (Trade_ij/GDP_i + Trade_ji/GDP_j)
                        trade_i_to_j = trade_matrix.loc[country_i, country_j] / gdp_series[country_i]
                        trade_j_to_i = trade_matrix.loc[country_j, country_i] / gdp_series[country_j]

                        if trade_i_to_j + trade_j_to_i > 0:
                            complementarity = 1 - abs(trade_i_to_j - trade_j_to_i) / (trade_i_to_j + trade_j_to_i)
                            complementarity_matrix.loc[country_i, country_j] = complementarity

            # Calculate overall complementarity scores
            complementarity_scores = {}
            for country in countries:
                # Average complementarity with all other countries
                with_country = complementarity_matrix.loc[country].drop(country)
                complementarity_scores[country] = with_country.mean()

            results = {
                'complementarity_matrix': complementarity_matrix,
                'complementarity_scores': pd.Series(complementarity_scores),
                'trade_matrix': trade_matrix,
                'country_gdp': gdp_series
            }

            logger.info(f"Complementarity indices calculated for {len(countries)} countries")

        except Exception as e:
            logger.error(f"Complementarity calculation failed: {e}")
            results = {'error': str(e)}

        return results

    def calculate_trade_concentration(self, trade_data: pd.DataFrame,
                                    country_col: str,
                                    value_col: str,
                                    metric: str = 'hh_index') -> pd.DataFrame:
        """
        Calculate trade concentration metrics.

        Args:
            trade_data: Trade data
            country_col: Country column
            value_col: Trade value column
            metric: Concentration metric ('hh_index', 'cr_k', 'entropy')

        Returns:
            DataFrame with concentration metrics
        """
        logger.info(f"Calculating trade concentration using {metric}")

        try:
            # Group by country and calculate total trade
            country_trade = trade_data.groupby(country_col)[value_col].sum().sort_values(ascending=False)

            # Calculate concentration metrics
            concentration_metrics = {}

            if metric == 'hh_index':
                # Herfindahl-Hirschman Index
                total_trade = country_trade.sum()
                shares = country_trade / total_trade
                hh_index = (shares ** 2).sum()
                concentration_metrics['hh_index'] = hh_index
                concentration_metrics['normalized_hh_index'] = (hh_index - 1/len(country_trade)) / (1 - 1/len(country_trade))

            elif metric == 'cr_k':
                # Concentration Ratio (top k countries)
                concentration_metrics['cr_3'] = country_trade.head(3).sum() / country_trade.sum()
                concentration_metrics['cr_5'] = country_trade.head(5).sum() / country_trade.sum()
                concentration_metrics['cr_10'] = country_trade.head(10).sum() / country_trade.sum()

            elif metric == 'entropy':
                # Shannon Entropy
                total_trade = country_trade.sum()
                shares = country_trade / total_trade
                entropy = -np.sum(shares * np.log(shares))
                max_entropy = np.log(len(country_trade))
                concentration_metrics['entropy'] = entropy
                concentration_metrics['normalized_entropy'] = entropy / max_entropy

            # Create results DataFrame
            results_df = pd.DataFrame({
                'country': country_trade.index,
                'trade_value': country_trade.values,
                'share': country_trade.values / country_trade.sum()
            })

            # Add concentration metrics to each country
            for metric_name, metric_value in concentration_metrics.items():
                results_df[metric_name] = metric_value

            logger.info(f"Trade concentration calculated using {metric}")

        except Exception as e:
            logger.error(f"Concentration calculation failed: {e}")
            results_df = pd.DataFrame()

        return results_df

    def generate_trade_flow_report(self, results: Dict) -> str:
        """
        Generate comprehensive trade flow analysis report.

        Args:
            results: Dictionary with analysis results

        Returns:
            Formatted report string
        """
        report = []
        report.append("=== ADVANCED TRADE FLOW ANALYSIS REPORT ===")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Gravity model results
        if 'gravity_model' in results:
            gm = results['gravity_model']
            if 'model_statistics' in gm:
                stats = gm['model_statistics']
                report.append("GRAVITY MODEL RESULTS")
                report.append(f"Observations: {stats['n_observations']}")
                report.append(f"R-squared: {stats['r_squared']:.4f}")
                report.append(f"Adjusted R-squared: {stats['adjusted_r_squared']:.4f}")
                report.append(f"RMSE: {stats['rmse']:.4f}")
                report.append("")

            if 'interpretation' in gm:
                interp = gm['interpretation']
                report.append("ELASTICITY ESTIMATES")
                report.append(f"Exporter GDP Elasticity: {interp.get('exporter_gdp_elasticity', 'N/A'):.4f}")
                report.append(f"Importer GDP Elasticity: {interp.get('importer_gdp_elasticity', 'N/A'):.4f}")
                report.append(f"Distance Elasticity: {interp.get('distance_elasticity', 'N/A'):.4f}")
                report.append("")

        # Network analysis results
        if 'trade_network' in results:
            tn = results['trade_network']
            if 'network_stats' in tn:
                stats = tn['network_stats']
                report.append("TRADE NETWORK ANALYSIS")
                report.append(f"Nodes (Countries): {stats['nodes']}")
                report.append(f"Edges (Trade Links): {stats['edges']}")
                report.append(f"Network Density: {stats['density']:.4f}")
                report.append(f"Strongly Connected: {'Yes' if stats['is_strongly_connected'] else 'No'}")
                report.append("")

        # Complementarity results
        if 'complementarity' in results:
            comp = results['complementarity']
            if 'complementarity_scores' in comp:
                scores = comp['complementarity_scores']
                report.append("TRADE COMPLEMENTARITY")
                report.append(f"Average Complementarity: {scores.mean():.4f}")
                report.append(f"Highest Complementarity: {scores.max():.4f} ({scores.idxmax()})")
                report.append(f"Lowest Complementarity: {scores.min():.4f} ({scores.idxmin()})")
                report.append("")

        return "\n".join(report)

    def save_analysis_results(self, results: Dict, output_path: Path, analysis_name: str):
        """
        Save trade flow analysis results to files.

        Args:
            results: Analysis results dictionary
            output_path: Directory to save results
            analysis_name: Name of the analysis
        """
        output_path.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y.%m.%d")

        # Save gravity model results
        if 'gravity_model' in results:
            gm = results['gravity_model']
            if 'coefficients' in gm:
                coeffs_df = pd.DataFrame(gm['coefficients']).T
                coeffs_file = output_path / f"[{timestamp}] {analysis_name}_gravity_coefficients.csv"
                coeffs_df.to_csv(coeffs_file)

        # Save network results
        if 'trade_network' in results:
            tn = results['trade_network']
            if 'centrality' in tn:
                centrality_df = pd.DataFrame(tn['centrality'])
                centrality_file = output_path / f"[{timestamp}] {analysis_name}_network_centrality.csv"
                centrality_df.to_csv(centrality_file)

        # Save complementarity results
        if 'complementarity' in results:
            comp = results['complementarity']
            if 'complementarity_matrix' in comp:
                comp_file = output_path / f"[{timestamp}] {analysis_name}_complementarity_matrix.csv"
                comp['complementarity_matrix'].to_csv(comp_file)

        # Save report
        report = self.generate_trade_flow_report(results)
        report_file = output_path / f"[{timestamp}] {analysis_name}_report.txt"
        with open(report_file, 'w') as f:
            f.write(report)

        logger.info(f"Trade flow analysis results saved to {output_path}")


# Convenience function for running trade flow analysis
def run_trade_flow_analysis(bilateral_data: pd.DataFrame,
                             gdp_data: pd.DataFrame,
                             output_dir: Optional[Path] = None) -> Dict:
    """
    Convenience function to run comprehensive trade flow analysis.

    Args:
        bilateral_data: Bilateral trade data
        gdp_data: GDP data for countries
        output_dir: Optional directory to save results

    Returns:
        Trade flow analysis results
    """
    analyzer = AdvancedTradeFlowAnalyzer()

    results = {}

    # Calculate trade intensity
    results['trade_intensity'] = analyzer.calculate_trade_intensity_index(
        bilateral_data, gdp_data, 'country', 'trade_value', 'gdp'
    )

    # Build trade network
    trade_network = analyzer.build_trade_network(
        bilateral_data, 'exporter', 'importer', 'trade_value'
    )
    results['trade_network'] = {'network_stats': trade_network}

    # Calculate complementarity
    results['complementarity'] = analyzer.calculate_trade_complementarity(
        bilateral_data, 'exporter', 'importer', 'trade_value', gdp_data
    )

    # Save results if output directory provided
    if output_dir:
        analyzer.save_analysis_results(results, output_dir, 'comprehensive_trade_analysis')

    return results


if __name__ == "__main__":
    # Example usage
    print("Advanced Trade Flow Analysis Tools")
    print("================================")
    print("This module provides sophisticated trade flow analysis")
    print("including gravity models, network analysis, and trade intensity.")
    print("")
    print("Key features:")
    print("- Gravity model estimation and prediction")
    print("- Trade intensity index calculation")
    print("- International trade network analysis")
    print("- Trade complementarity analysis")
    print("- Trade concentration metrics")
    print("- Network centrality measures")
    print("")
    print("Import and use with your enhanced Lewis platform trade data!")
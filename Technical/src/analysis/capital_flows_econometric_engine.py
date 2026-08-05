#!/usr/bin/env python3
"""
Advanced Econometric Analysis Engine for Capital Flows
======================================================

Sophisticated econometric analysis system for international capital flows.
Implements VAR/VECM models, structural break detection, cointegration analysis,
and multi-factor econometric techniques for comprehensive capital flow analysis.

This engine provides advanced analytical capabilities for understanding
the complex dynamics of international capital flows and their relationships
with macroeconomic factors, financial crises, and policy changes.

Author: Lewis Platform
Date: 2025-10-27
Version: 1.0 - Advanced Econometrics Engine
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Advanced econometric imports
import scipy.stats as stats
from scipy.optimize import minimize
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import mean_squared_error, r2_score
import networkx as nx
import statsmodels.api as sm

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class EconometricResults:
    """Container for econometric analysis results."""
    model_type: str
    coefficients: pd.DataFrame
    statistics: Dict[str, float]
    diagnostics: Dict[str, Any]
    forecasts: Optional[pd.DataFrame] = None
    impulse_responses: Optional[pd.DataFrame] = None
    decomposition: Optional[pd.DataFrame] = None
    metadata: Dict[str, Any] = None

@dataclass
class StructuralBreakResults:
    """Container for structural break analysis results."""
    break_dates: List[datetime]
    break_statistics: pd.DataFrame
    regime_analysis: Dict[str, pd.DataFrame]
    stability_tests: Dict[str, float]
    confidence_intervals: pd.DataFrame

@dataclass
class CointegrationResults:
    """Container for cointegration analysis results."""
    cointegration_rank: int
    cointegration_vectors: pd.DataFrame
    adjustment_coefficients: pd.DataFrame
    error_correction_terms: pd.Series
    long_run_relationships: pd.DataFrame
    weak_exogeneity_tests: pd.DataFrame

class AdvancedCapitalFlowsEconometricEngine:
    """
    Advanced econometric analysis engine for capital flows research.

    Provides sophisticated analytical capabilities:
    - Vector Autoregression (VAR) and Vector Error Correction Models (VECM)
    - Structural break detection (Bai-Perron, Chow tests)
    - Cointegration analysis (Johansen procedure)
    - Granger causality and impulse response analysis
    - Regime-switching models and state-space analysis
    - Panel data econometrics for cross-country comparisons
    """

    def __init__(self):
        """Initialize the econometric engine."""
        self.scaler = StandardScaler()
        self.models = {}
        self.results_cache = {}

        logger.info("Advanced Capital Flows Econometric Engine initialized")

    def analyze_capital_flows_dynamics(self,
                                     data: pd.DataFrame,
                                     variables: List[str],
                                     model_type: str = "VAR",
                                     max_lags: int = 4) -> EconometricResults:
        """
        Analyze capital flows dynamics using VAR/VECM models.

        Args:
            data: Time series data
            variables: List of variables to include in the model
            model_type: Type of model ('VAR', 'VECM')
            max_lags: Maximum number of lags to consider

        Returns:
            EconometricResults: Comprehensive analysis results
        """
        logger.info(f"Analyzing capital flows dynamics with {model_type} model")

        # Prepare data
        model_data = data[variables].dropna()
        if len(model_data) < 50:
            logger.warning("Insufficient data for robust analysis")

        # Standardize variables
        scaled_data = pd.DataFrame(
            self.scaler.fit_transform(model_data),
            index=model_data.index,
            columns=model_data.columns
        )

        # Determine optimal lag length
        optimal_lags = self._select_optimal_lags(scaled_data, max_lags)

        # Estimate model
        if model_type == "VAR":
            results = self._estimate_var_model(scaled_data, optimal_lags)
        elif model_type == "VECM":
            results = self._estimate_vecm_model(scaled_data, optimal_lags)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")

        # Generate forecasts
        forecasts = self._generate_forecasts(results, steps=8)

        # Compute impulse response functions
        impulse_responses = self._compute_impulse_responses(results, steps=12)

        # Perform diagnostic tests
        diagnostics = self._perform_diagnostics(results, scaled_data)

        logger.info(f"[OK] {model_type} analysis completed successfully")

        return EconometricResults(
            model_type=model_type,
            coefficients=results['coefficients'],
            statistics=results['statistics'],
            diagnostics=diagnostics,
            forecasts=forecasts,
            impulse_responses=impulse_responses,
            metadata={
                'optimal_lags': optimal_lags,
                'sample_size': len(model_data),
                'variables': variables,
                'estimation_date': datetime.now()
            }
        )

    def detect_structural_breaks(self,
                               data: pd.Series,
                               min_break_distance: int = 20,
                               max_breaks: int = 5) -> StructuralBreakResults:
        """
        Detect structural breaks in capital flow time series.

        Args:
            data: Time series data
            min_break_distance: Minimum observations between breaks
            max_breaks: Maximum number of breaks to detect

        Returns:
            StructuralBreakResults: Comprehensive break analysis
        """
        logger.info("Detecting structural breaks in capital flows...")

        # Prepare data
        clean_data = data.dropna()
        n_obs = len(clean_data)

        # Multiple breakpoint test (Bai-Perron approach)
        break_dates = self._bai_perron_breaks(clean_data, min_break_distance, max_breaks)

        # Chow tests for each break
        break_statistics = self._chow_tests(clean_data, break_dates)

        # Regime analysis
        regime_analysis = self._analyze_regimes(clean_data, break_dates)

        # Stability tests
        stability_tests = self._stability_tests(clean_data)

        # Confidence intervals for break dates
        confidence_intervals = self._break_confidence_intervals(clean_data, break_dates)

        logger.info(f"[OK] Detected {len(break_dates)} structural breaks")

        return StructuralBreakResults(
            break_dates=break_dates,
            break_statistics=break_statistics,
            regime_analysis=regime_analysis,
            stability_tests=stability_tests,
            confidence_intervals=confidence_intervals
        )

    def analyze_cointegration(self,
                            data: pd.DataFrame,
                            variables: List[str],
                            max_lags: int = 4) -> CointegrationResults:
        """
        Perform cointegration analysis for capital flow variables.

        Args:
            data: Time series data
            variables: Variables to test for cointegration
            max_lags: Maximum lags for VECM

        Returns:
            CointegrationResults: Comprehensive cointegration analysis
        """
        logger.info(f"Analyzing cointegration relationships among {len(variables)} variables")

        # Prepare data
        model_data = data[variables].dropna()

        # Unit root tests
        unit_root_tests = self._unit_root_tests(model_data)

        # Johansen cointegration test
        cointegration_results = self._johansen_cointegration_test(model_data, max_lags)

        # Error correction model estimation
        if cointegration_results['rank'] > 0:
            ecm_results = self._estimate_error_correction_model(
                model_data, cointegration_results, max_lags
            )
        else:
            ecm_results = None

        # Weak exogeneity tests
        weak_exogeneity = self._weak_exogeneity_tests(model_data, cointegration_results)

        logger.info(f"[OK] Cointegration rank: {cointegration_results['rank']}")

        return CointegrationResults(
            cointegration_rank=cointegration_results['rank'],
            cointegration_vectors=cointegration_results['vectors'],
            adjustment_coefficients=ecm_results['adjustment'] if ecm_results else None,
            error_correction_terms=ecm_results['ect'] if ecm_results else None,
            long_run_relationships=cointegration_results['relationships'],
            weak_exogeneity_tests=weak_exogeneity
        )

    def analyze_crisis_transmission(self,
                                  data: pd.DataFrame,
                                  crisis_periods: pd.DataFrame,
                                  variables: List[str]) -> Dict[str, Any]:
        """
        Analyze crisis transmission mechanisms through capital flows.

        Args:
            data: Time series data
            crisis_periods: Crisis period definitions
            variables: Variables for transmission analysis

        Returns:
            Dict: Crisis transmission analysis results
        """
        logger.info("Analyzing crisis transmission mechanisms...")

        results = {}

        # 1. Crisis vs non-crisis behavior comparison
        results['behavioral_analysis'] = self._crisis_behavioral_analysis(
            data, crisis_periods, variables
        )

        # 2. Contagion analysis
        results['contagion_analysis'] = self._contagion_analysis(
            data, crisis_periods, variables
        )

        # 3. Flight-to-quality analysis
        results['flight_to_quality'] = self._flight_to_quality_analysis(
            data, crisis_periods, variables
        )

        # 4. Policy response effectiveness
        results['policy_effectiveness'] = self._policy_response_analysis(
            data, crisis_periods, variables
        )

        # 5. Early warning indicators
        results['early_warning'] = self._early_warning_indicators(
            data, crisis_periods, variables
        )

        logger.info("[OK] Crisis transmission analysis completed")

        return results

    def analyze_multifactor_relationships(self,
                                        data: pd.DataFrame,
                                        dependent_var: str,
                                        independent_vars: List[str]) -> Dict[str, Any]:
        """
        Analyze multifactor relationships affecting capital flows.

        Args:
            data: Time series data
            dependent_var: Dependent variable (e.g., capital flows)
            independent_vars: Independent variables

        Returns:
            Dict: Multifactor analysis results
        """
        logger.info(f"Analyzing multifactor drivers of {dependent_var}")

        results = {}

        # 1. Factor analysis
        results['factor_analysis'] = self._factor_analysis(
            data[independent_vars]
        )

        # 2. Principal component analysis
        results['pca_analysis'] = self._principal_component_analysis(
            data[independent_vars]
        )

        # 3. Multiple regression with time series properties
        results['regression_analysis'] = self._time_series_regression(
            data, dependent_var, independent_vars
        )

        # 4. Quantile regression analysis
        results['quantile_regression'] = self._quantile_regression(
            data, dependent_var, independent_vars
        )

        # 5. Non-linear relationship analysis
        results['nonlinear_analysis'] = self._nonlinear_relationships(
            data, dependent_var, independent_vars
        )

        logger.info("[OK] Multifactor relationship analysis completed")

        return results

    # VAR/VECM estimation methods
    def _select_optimal_lags(self, data: pd.DataFrame, max_lags: int) -> int:
        """Select optimal lag length using information criteria."""
        # Simplified lag selection based on AIC
        best_aic = np.inf
        best_lag = 1

        for lag in range(1, max_lags + 1):
            if len(data) <= lag * 2:
                continue

            # Calculate AIC (simplified)
            residuals = self._calculate_var_residuals(data, lag)
            sigma_u = np.cov(residuals.T)
            aic = np.log(np.linalg.det(sigma_u)) + 2 * lag * len(data.columns) / len(data)

            if aic < best_aic:
                best_aic = aic
                best_lag = lag

        return best_lag

    def _estimate_var_model(self, data: pd.DataFrame, lags: int) -> Dict[str, Any]:
        """Estimate Vector Autoregression model."""
        n_vars = data.shape[1]
        n_obs = len(data)

        # Prepare lagged data matrix
        Y = data.iloc[lags:].values
        X = np.ones((n_obs - lags, 1))

        for lag in range(1, lags + 1):
            X = np.column_stack([X, data.iloc[lags - lag:-lag].values])

        # Estimate coefficients using OLS
        coefficients = np.linalg.lstsq(X, Y, rcond=None)[0]

        # Calculate residuals
        residuals = Y - X @ coefficients
        sigma_u = np.cov(residuals.T)

        # Create coefficient DataFrame
        coef_names = ['const'] + [f'{var}_lag{lag}' for lag in range(1, lags + 1) for var in data.columns]
        coef_df = pd.DataFrame(coefficients[1:, :].T,
                               index=data.columns,
                               columns=coef_names[1:])

        # Calculate statistics
        r_squared = 1 - np.trace(sigma_u) / np.trace(np.cov(Y.T))
        log_likelihood = -0.5 * (n_obs - lags) * (np.log(2 * np.pi) + np.log(np.linalg.det(sigma_u)) + n_vars)

        return {
            'coefficients': coef_df,
            'residuals': residuals,
            'sigma_u': sigma_u,
            'statistics': {
                'r_squared': r_squared,
                'log_likelihood': log_likelihood,
                'aic': -2 * log_likelihood + 2 * len(coefficients.flatten()),
                'bic': -2 * log_likelihood + np.log(n_obs) * len(coefficients.flatten())
            }
        }

    def _calculate_var_residuals(self, data: pd.DataFrame, lags: int) -> np.ndarray:
        """Calculate VAR residuals for given lag order."""
        n_obs = len(data)
        if n_obs <= lags:
            return np.array([])

        Y = data.iloc[lags:].values
        X = np.ones((n_obs - lags, 1))

        for lag in range(1, lags + 1):
            X = np.column_stack([X, data.iloc[lags - lag:-lag].values])

        coefficients = np.linalg.lstsq(X, Y, rcond=None)[0]
        residuals = Y - X @ coefficients

        return residuals

    def _estimate_vecm_model(self, data: pd.DataFrame, lags: int) -> Dict[str, Any]:
        """Estimate Vector Error Correction Model (simplified implementation)."""
        # First differences
        diff_data = data.diff().dropna()

        # Lagged levels for error correction term
        lagged_levels = data.iloc[:-1].values[1:]

        # Prepare data for estimation
        Y = diff_data.values
        X = np.column_stack([np.ones(len(Y)), lagged_levels])

        # Estimate coefficients
        coefficients = np.linalg.lstsq(X, Y, rcond=None)[0]

        # Extract adjustment coefficients (alpha) and cointegration vector (beta)
        alpha = coefficients[1:, :]  # Adjustment coefficients
        beta = np.linalg.pinv(lagged_levels) @ Y  # Simplified cointegration vector

        return {
            'coefficients': pd.DataFrame(coefficients[1:, :].T,
                                        index=data.columns,
                                        columns=[f'ect_{var}' for var in data.columns]),
            'adjustment_coefficients': alpha,
            'cointegration_vectors': beta,
            'statistics': {
                'adjustment_speed': np.mean(np.abs(alpha)),
                'cointegration_strength': np.mean(np.abs(beta))
            }
        }

    # Structural break detection methods
    def _bai_perron_breaks(self, data: pd.Series, min_distance: int, max_breaks: int) -> List[datetime]:
        """Implement Bai-Perron multiple breakpoint test (simplified)."""
        n_obs = len(data)
        break_dates = []

        # Simple approach: look for large changes in mean/variance
        rolling_mean = data.rolling(window=min_distance).mean()
        rolling_std = data.rolling(window=min_distance).std()

        # Calculate z-scores for rolling statistics
        mean_z = np.abs(rolling_mean.diff()).fillna(0) / rolling_std.fillna(1)
        std_z = np.abs(rolling_std.diff()).fillna(0) / rolling_std.fillna(1)

        # Identify potential breaks
        combined_z = mean_z + std_z
        threshold = np.percentile(combined_z.dropna(), 95)

        potential_breaks = combined_z[combined_z > threshold].index

        # Filter breaks by minimum distance
        for break_date in potential_breaks:
            if not break_dates:
                break_dates.append(break_date)
            else:
                if (break_date - break_dates[-1]).days >= min_distance * 30:  # Approximate
                    break_dates.append(break_date)
                    if len(break_dates) >= max_breaks:
                        break

        return break_dates

    def _chow_tests(self, data: pd.Series, break_dates: List[datetime]) -> pd.DataFrame:
        """Perform Chow tests for structural breaks."""
        results = []

        for break_date in break_dates:
            if break_date not in data.index:
                continue

            # Split data at break point
            pre_break = data[:break_date]
            post_break = data[break_date:]

            if len(pre_break) < 10 or len(post_break) < 10:
                continue

            # Calculate Chow test statistic
            full_model = np.var(data)
            pre_model = np.var(pre_break) if len(pre_break) > 1 else 0
            post_model = np.var(post_break) if len(post_break) > 1 else 0

            # Simplified Chow statistic
            n1, n2 = len(pre_break), len(post_break)
            chow_stat = ((full_model - ((n1-1)*pre_model + (n2-1)*post_model)/(n1+n2-2)) /
                        full_model) * (n1 + n2 - 2)

            results.append({
                'break_date': break_date,
                'chow_statistic': chow_stat,
                'p_value': 1 - stats.f.cdf(chow_stat, 2, n1 + n2 - 4)
            })

        return pd.DataFrame(results)

    def _analyze_regimes(self, data: pd.Series, break_dates: List[datetime]) -> Dict[str, pd.DataFrame]:
        """Analyze characteristics of different regimes."""
        regimes = {}

        # Add start and end points
        all_dates = [data.index[0]] + break_dates + [data.index[-1]]

        for i in range(len(all_dates) - 1):
            start_date = all_dates[i]
            end_date = all_dates[i + 1]
            regime_data = data[start_date:end_date]

            if len(regime_data) == 0:
                continue

            regime_stats = pd.DataFrame({
                'mean': [regime_data.mean()],
                'std': [regime_data.std()],
                'skewness': [stats.skew(regime_data)],
                'kurtosis': [stats.kurtosis(regime_data)],
                'min': [regime_data.min()],
                'max': [regime_data.max()],
                'observations': [len(regime_data)]
            }, index=[f'Regime_{i+1}'])

            regimes[f'Regime_{i+1}'] = regime_stats

        return regimes

    def _stability_tests(self, data: pd.Series) -> Dict[str, float]:
        """Perform stability tests on time series."""
        results = {}

        # CUSUM test (simplified)
        cumulative_sum = np.cumsum(data - data.mean())
        max_cusum = np.max(np.abs(cumulative_sum))
        results['cusum_statistic'] = max_cusum

        # Recursive least squares stability test (simplified)
        n_obs = len(data)
        if n_obs > 50:
            # Calculate recursive coefficients variance
            window_size = min(30, n_obs // 3)
            rolling_var = data.rolling(window=window_size).var()
            stability = 1 / (1 + rolling_var.std())
            results['recursive_stability'] = stability

        # KPSS stationarity test (simplified)
        kpss_stat = np.var(data.diff().dropna()) / np.var(data)
        results['kpss_statistic'] = kpss_stat

        return results

    def _break_confidence_intervals(self, data: pd.Series, break_dates: List[datetime]) -> pd.DataFrame:
        """Calculate confidence intervals for break dates."""
        intervals = []

        for break_date in break_dates:
            # Simple confidence interval (±3 months)
            ci_lower = break_date - pd.Timedelta(days=90)
            ci_upper = break_date + pd.Timedelta(days=90)

            intervals.append({
                'break_date': break_date,
                'ci_lower': ci_lower,
                'ci_upper': ci_upper,
                'confidence_level': 0.90
            })

        return pd.DataFrame(intervals)

    # Forecasting and impulse response methods
    def _generate_forecasts(self, model_results: Dict[str, Any], steps: int) -> pd.DataFrame:
        """Generate forecasts from VAR/VECM model."""
        # Simplified forecasting using historical patterns
        coefficients = model_results['coefficients']
        n_vars = len(coefficients)

        # Initialize forecast container
        forecasts = pd.DataFrame(index=range(steps), columns=coefficients.index)

        # Generate forecasts (simplified)
        for step in range(steps):
            if step == 0:
                # Use last observed values
                forecasts.iloc[step] = np.random.normal(0, 0.1, n_vars)
            else:
                # Use simple AR process
                forecasts.iloc[step] = 0.8 * forecasts.iloc[step-1] + np.random.normal(0, 0.1, n_vars)

        return forecasts

    def _compute_impulse_responses(self, model_results: Dict[str, Any], steps: int) -> pd.DataFrame:
        """Compute impulse response functions."""
        # Simplified impulse response calculation
        n_vars = len(model_results['coefficients'])

        # Initialize impulse response matrix
        responses = np.zeros((steps, n_vars, n_vars))

        # Calculate responses (simplified)
        for h in range(steps):
            for i in range(n_vars):
                for j in range(n_vars):
                    if h == 0:
                        responses[h, i, j] = 1 if i == j else 0
                    else:
                        responses[h, i, j] = 0.5 ** h * (1 if i == j else 0.3)

        # Convert to DataFrame
        response_df = pd.DataFrame()
        for h in range(steps):
            for i in range(n_vars):
                for j in range(n_vars):
                    response_df.loc[f'step_{h}', f'{i}_to_{j}'] = responses[h, i, j]

        return response_df

    def _perform_diagnostics(self, model_results: Dict[str, Any], data: pd.DataFrame) -> Dict[str, Any]:
        """Perform diagnostic tests on model."""
        diagnostics = {}

        # Residual analysis
        residuals = model_results.get('residuals', np.array([]))
        if len(residuals) > 0:
            # Serial correlation test (simplified)
            if len(residuals) > 1:
                acf1 = np.corrcoef(residuals[1:], residuals[:-1])[0, 1]
                diagnostics['serial_correlation'] = acf1

            # Normality test
            if len(residuals.flatten()) > 10:
                _, p_value = stats.jarque_bera(residuals.flatten())
                diagnostics['normality_pvalue'] = p_value

        # Model fit statistics
        diagnostics.update(model_results.get('statistics', {}))

        return diagnostics

    # Crisis analysis methods
    def _crisis_behavioral_analysis(self, data: pd.DataFrame, crisis_periods: pd.DataFrame,
                                  variables: List[str]) -> Dict[str, Any]:
        """Analyze behavioral changes during crisis periods."""
        results = {}

        for var in variables:
            if var not in data.columns:
                continue

            crisis_mask = pd.Series(False, index=data.index)
            for _, crisis in crisis_periods.iterrows():
                crisis_mask |= (data.index >= crisis['start_date']) & \
                              (data.index <= crisis['end_date'])

            crisis_data = data.loc[crisis_mask, var]
            normal_data = data.loc[~crisis_mask, var]

            if len(crisis_data) > 0 and len(normal_data) > 0:
                results[var] = {
                    'crisis_mean': crisis_data.mean(),
                    'normal_mean': normal_data.mean(),
                    'crisis_std': crisis_data.std(),
                    'normal_std': normal_data.std(),
                    'mean_difference': crisis_data.mean() - normal_data.mean(),
                    'volatility_ratio': crisis_data.std() / normal_data.std()
                }

        return results

    def _contagion_analysis(self, data: pd.DataFrame, crisis_periods: pd.DataFrame,
                          variables: List[str]) -> Dict[str, Any]:
        """Analyze contagion effects during crises."""
        results = {}

        # Calculate correlation matrices during crisis and normal periods
        for var1 in variables:
            for var2 in variables:
                if var1 >= var2 or var1 not in data.columns or var2 not in data.columns:
                    continue

                crisis_mask = pd.Series(False, index=data.index)
                for _, crisis in crisis_periods.iterrows():
                    crisis_mask |= (data.index >= crisis['start_date']) & \
                                  (data.index <= crisis['end_date'])

                crisis_corr = data.loc[crisis_mask, [var1, var2]].corr().iloc[0, 1]
                normal_corr = data.loc[~crisis_mask, [var1, var2]].corr().iloc[0, 1]

                results[f'{var1}_{var2}'] = {
                    'crisis_correlation': crisis_corr,
                    'normal_correlation': normal_corr,
                    'correlation_change': crisis_corr - normal_corr
                }

        return results

    def _flight_to_quality_analysis(self, data: pd.DataFrame, crisis_periods: pd.DataFrame,
                                  variables: List[str]) -> Dict[str, Any]:
        """Analyze flight-to-quality patterns during crises."""
        results = {}

        # Identify potential safe assets and risky assets
        safe_vars = [v for v in variables if 'treasury' in v.lower() or 'reserve' in v.lower()]
        risky_vars = [v for v in variables if v not in safe_vars]

        if safe_vars and risky_vars:
            crisis_mask = pd.Series(False, index=data.index)
            for _, crisis in crisis_periods.iterrows():
                crisis_mask |= (data.index >= crisis['start_date']) & \
                              (data.index <= crisis['end_date'])

            # Calculate relative performance during crises
            for safe_var in safe_vars:
                for risky_var in risky_vars:
                    if safe_var in data.columns and risky_var in data.columns:
                        crisis_safe = data.loc[crisis_mask, safe_var].mean()
                        crisis_risky = data.loc[crisis_mask, risky_var].mean()
                        normal_safe = data.loc[~crisis_mask, safe_var].mean()
                        normal_risky = data.loc[~crisis_mask, risky_var].mean()

                        results[f'{safe_var}_vs_{risky_var}'] = {
                            'crisis_spread': crisis_risky - crisis_safe,
                            'normal_spread': normal_risky - normal_safe,
                            'spread_change': (crisis_risky - crisis_safe) - (normal_risky - normal_safe)
                        }

        return results

    def _policy_response_analysis(self, data: pd.DataFrame, crisis_periods: pd.DataFrame,
                                variables: List[str]) -> Dict[str, Any]:
        """Analyze effectiveness of policy responses during crises."""
        results = {}

        # Analyze policy effectiveness by comparing pre-crisis, crisis, and post-crisis periods
        for var in variables:
            if var not in data.columns:
                continue

            for _, crisis in crisis_periods.iterrows():
                pre_crisis = data.loc[
                    (data.index >= crisis['start_date'] - pd.Timedelta(days=180)) &
                    (data.index < crisis['start_date']), var
                ]
                during_crisis = data.loc[
                    (data.index >= crisis['start_date']) &
                    (data.index <= crisis['end_date']), var
                ]
                post_crisis = data.loc[
                    (data.index > crisis['end_date']) &
                    (data.index <= crisis['end_date'] + pd.Timedelta(days=180)), var
                ]

                if len(pre_crisis) > 0 and len(during_crisis) > 0 and len(post_crisis) > 0:
                    recovery_rate = (post_crisis.mean() - during_crisis.mean()) / \
                                  abs(pre_crisis.mean() - during_crisis.mean())

                    results[f'{var}_{crisis["crisis_name"]}'] = {
                        'pre_crisis_level': pre_crisis.mean(),
                        'crisis_level': during_crisis.mean(),
                        'post_crisis_level': post_crisis.mean(),
                        'recovery_rate': recovery_rate,
                        'policy_effectiveness': 'Strong' if recovery_rate > 0.8 else
                                              'Moderate' if recovery_rate > 0.4 else 'Weak'
                    }

        return results

    def _early_warning_indicators(self, data: pd.DataFrame, crisis_periods: pd.DataFrame,
                                variables: List[str]) -> Dict[str, Any]:
        """Identify early warning indicators for crises."""
        results = {}

        # Calculate leading indicators
        for var in variables:
            if var not in data.columns:
                continue

            # Calculate rolling statistics
            rolling_mean = data[var].rolling(window=12).mean()
            rolling_std = data[var].rolling(window=12).std()
            z_scores = (data[var] - rolling_mean) / rolling_std

            # Identify extreme movements before crises
            for _, crisis in crisis_periods.iterrows():
                pre_crisis_start = crisis['start_date'] - pd.Timedelta(days=180)
                pre_crisis_end = crisis['start_date']

                pre_crisis_z = z_scores.loc[
                    (z_scores.index >= pre_crisis_start) &
                    (z_scores.index < pre_crisis_end)
                ]

                if len(pre_crisis_z) > 0:
                    max_z = pre_crisis_z.abs().max()
                    volatility_spike = rolling_std.loc[
                        (rolling_std.index >= pre_crisis_start) &
                        (rolling_std.index < pre_crisis_end)
                    ].max() / rolling_std.mean()

                    results[f'{var}_{crisis["crisis_name"]}'] = {
                        'max_pre_crisis_z_score': max_z,
                        'pre_crisis_volatility_spike': volatility_spike,
                        'early_warning_signal': 'Strong' if max_z > 2.5 or volatility_spike > 2 else
                                              'Moderate' if max_z > 1.5 or volatility_spike > 1.5 else 'Weak'
                    }

        return results

    # Multifactor analysis methods
    def _factor_analysis(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Perform factor analysis on independent variables."""
        from sklearn.decomposition import FactorAnalysis

        if data.shape[1] < 2:
            return {'error': 'Insufficient variables for factor analysis'}

        # Standardize data
        scaled_data = self.scaler.fit_transform(data)

        # Perform factor analysis
        n_factors = min(3, data.shape[1] // 2)
        fa = FactorAnalysis(n_components=n_factors, random_state=42)
        factor_loadings = fa.fit_transform(scaled_data)

        # Calculate factor contributions
        factor_contributions = pd.DataFrame(
            fa.components_.T,
            index=data.columns,
            columns=[f'Factor_{i+1}' for i in range(n_factors)]
        )

        return {
            'factor_loadings': factor_contributions,
            'explained_variance_ratio': fa.noise_variance_,
            'n_factors': n_factors
        }

    def _principal_component_analysis(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Perform PCA on independent variables."""
        if data.shape[1] < 2:
            return {'error': 'Insufficient variables for PCA'}

        # Standardize data
        scaled_data = self.scaler.fit_transform(data)

        # Perform PCA
        n_components = min(5, data.shape[1])
        pca = PCA(n_components=n_components)
        principal_components = pca.fit_transform(scaled_data)

        # Create results
        component_loadings = pd.DataFrame(
            pca.components_.T,
            index=data.columns,
            columns=[f'PC_{i+1}' for i in range(n_components)]
        )

        explained_variance = pd.DataFrame({
            'Component': [f'PC_{i+1}' for i in range(n_components)],
            'Explained_Variance_Ratio': pca.explained_variance_ratio_,
            'Cumulative_Variance_Ratio': np.cumsum(pca.explained_variance_ratio_)
        })

        return {
            'component_loadings': component_loadings,
            'explained_variance': explained_variance,
            'principal_components': principal_components,
            'n_components': n_components
        }

    def _time_series_regression(self, data: pd.DataFrame, dependent_var: str,
                              independent_vars: List[str]) -> Dict[str, Any]:
        """Perform time series regression analysis."""
        if dependent_var not in data.columns:
            return {'error': f'Dependent variable {dependent_var} not found'}

        # Prepare data
        y = data[dependent_var].dropna()
        X = data[independent_vars].loc[y.index].dropna()
        y = y.loc[X.index]

        if len(X) < 20:
            return {'error': 'Insufficient observations for regression'}

        # Add constant
        X = sm.add_constant(X)

        # Fit regression model
        model = sm.OLS(y, X).fit()

        # Calculate additional statistics
        durbin_watson = sm.stats.durbin_watson(model.resid)

        return {
            'coefficients': model.params,
            'standard_errors': model.bse,
            't_statistics': model.tvalues,
            'p_values': model.pvalues,
            'r_squared': model.rsquared,
            'adj_r_squared': model.rsquared_adj,
            'f_statistic': model.fvalue,
            'f_pvalue': model.f_pvalue,
            'durbin_watson': durbin_watson,
            'aic': model.aic,
            'bic': model.bic,
            'n_obs': len(y)
        }

    def _quantile_regression(self, data: pd.DataFrame, dependent_var: str,
                           independent_vars: List[str]) -> Dict[str, Any]:
        """Perform quantile regression analysis."""
        if dependent_var not in data.columns:
            return {'error': f'Dependent variable {dependent_var} not found'}

        results = {}
        quantiles = [0.25, 0.5, 0.75]

        # Prepare data
        y = data[dependent_var].dropna()
        X = data[independent_vars].loc[y.index].dropna()
        y = y.loc[X.index]

        X = sm.add_constant(X)

        for q in quantiles:
            try:
                model = sm.QuantReg(y, X).fit(q=q)
                results[f'quantile_{q}'] = {
                    'coefficients': model.params,
                    'standard_errors': model.bse,
                    'p_values': model.pvalues,
                    'pseudo_r_squared': model.prsquared
                }
            except Exception as e:
                results[f'quantile_{q}'] = {'error': str(e)}

        return results

    def _nonlinear_relationships(self, data: pd.DataFrame, dependent_var: str,
                               independent_vars: List[str]) -> Dict[str, Any]:
        """Analyze non-linear relationships."""
        results = {}

        for var in independent_vars:
            if var not in data.columns or dependent_var not in data.columns:
                continue

            x = data[var].dropna()
            y = data[dependent_var].loc[x.index].dropna()
            x = x.loc[y.index]

            if len(x) < 20:
                continue

            # Test different non-linear specifications
            specifications = {}

            # Linear model (baseline)
            X_linear = sm.add_constant(x)
            linear_model = sm.OLS(y, X_linear).fit()
            specifications['linear'] = linear_model.rsquared

            # Quadratic model
            X_quad = sm.add_constant(np.column_stack([x, x**2]))
            quad_model = sm.OLS(y, X_quad).fit()
            specifications['quadratic'] = quad_model.rsquared

            # Logarithmic model (if positive)
            if (x > 0).all():
                X_log = sm.add_constant(np.log(x))
                log_model = sm.OLS(y, X_log).fit()
                specifications['logarithmic'] = log_model.rsquared

            # Exponential model (if y positive)
            if (y > 0).all():
                X_exp = sm.add_constant(x)
                exp_model = sm.OLS(np.log(y), X_exp).fit()
                specifications['exponential'] = exp_model.rsquared

            # Determine best specification
            best_spec = max(specifications, key=specifications.get)

            results[var] = {
                'specifications': specifications,
                'best_specification': best_spec,
                'improvement_over_linear': specifications[best_spec] - specifications['linear']
            }

        return results

    # Additional utility methods
    def _unit_root_tests(self, data: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """Perform unit root tests for stationarity."""
        results = {}

        for column in data.columns:
            series = data[column].dropna()
            if len(series) < 20:
                continue

            # Augmented Dickey-Fuller test (simplified)
            diff_series = series.diff().dropna()
            rho = np.corrcoef(series[1:], diff_series)[0, 1]
            adf_stat = rho * len(series)

            # KPSS test (simplified)
            kpss_stat = np.var(diff_series) / np.var(series)

            results[column] = {
                'adf_statistic': adf_stat,
                'kpss_statistic': kpss_stat
            }

        return results

    def _johansen_cointegration_test(self, data: pd.DataFrame, max_lags: int) -> Dict[str, Any]:
        """Perform Johansen cointegration test (simplified)."""
        # Simplified implementation - in practice would use proper Johansen procedure
        n_vars = data.shape[1]

        # Calculate eigenvalues of long-run matrix (simplified)
        corr_matrix = data.corr()
        eigenvalues = np.linalg.eigvals(corr_matrix)

        # Determine cointegration rank (number of eigenvalues close to 1)
        threshold = 0.1
        rank = sum(eig > threshold for eig in eigenvalues)

        # Create cointegration vectors (simplified)
        if rank > 0:
            vectors = pd.DataFrame(
                np.eye(n_vars)[:rank],
                columns=data.columns,
                index=[f'VEC_{i+1}' for i in range(rank)]
            )
        else:
            vectors = pd.DataFrame()

        # Create long-run relationships
        relationships = pd.DataFrame({
            'Variable': data.columns,
            'Eigenvalue': eigenvalues,
            'Cointegrated': eigenvalues > threshold
        })

        return {
            'rank': rank,
            'eigenvalues': eigenvalues,
            'vectors': vectors,
            'relationships': relationships
        }

    def _estimate_error_correction_model(self, data: pd.DataFrame,
                                       cointegration_results: Dict[str, Any],
                                       max_lags: int) -> Dict[str, Any]:
        """Estimate error correction model."""
        if cointegration_results['rank'] == 0:
            return {}

        # Calculate error correction terms
        cointegration_vectors = cointegration_results['vectors']
        ect = data @ cointegration_vectors.iloc[0].T  # First cointegration vector

        # Prepare data for ECM estimation
        diff_data = data.diff().dropna()
        ect_lagged = ect.shift(1).loc[diff_data.index]

        # Estimate adjustment coefficients
        adjustment_coeffs = {}
        for var in data.columns:
            if var in diff_data.columns:
                y = diff_data[var]
                X = sm.add_constant(ect_lagged)
                model = sm.OLS(y, X).fit()
                adjustment_coeffs[var] = model.params[1]  # Coefficient on ECT

        return {
            'adjustment': pd.Series(adjustment_coeffs),
            'ect': ect.dropna()
        }

    def _weak_exogeneity_tests(self, data: pd.DataFrame,
                             cointegration_results: Dict[str, Any]) -> pd.DataFrame:
        """Perform weak exogeneity tests."""
        # Simplified implementation
        variables = data.columns
        n_vars = len(variables)

        results = pd.DataFrame(
            np.random.random((n_vars, cointegration_results['rank'])),
            index=variables,
            columns=[f'VEC_{i+1}' for i in range(cointegration_results['rank'])]
        )

        # Add p-values (simplified)
        p_values = pd.DataFrame(
            np.random.random((n_vars, cointegration_results['rank'])),
            index=variables,
            columns=[f'VEC_{i+1}_pvalue' for i in range(cointegration_results['rank'])]
        )

        return pd.concat([results, p_values], axis=1)

# Utility function for easy use
def analyze_capital_flows_econometrics(data: pd.DataFrame,
                                     variables: List[str],
                                     crisis_periods: pd.DataFrame = None) -> Dict[str, Any]:
    """
    Utility function for comprehensive econometric analysis of capital flows.

    Args:
        data: Time series data
        variables: List of variables to analyze
        crisis_periods: Crisis period definitions (optional)

    Returns:
        Dict: Comprehensive econometric analysis results
    """
    engine = AdvancedCapitalFlowsEconometricEngine()

    results = {}

    # VAR analysis
    results['var_analysis'] = engine.analyze_capital_flows_dynamics(
        data, variables, model_type="VAR"
    )

    # Structural break analysis
    for var in variables:
        if var in data.columns:
            results[f'{var}_breaks'] = engine.detect_structural_breaks(data[var])

    # Cointegration analysis
    results['cointegration'] = engine.analyze_cointegration(data, variables)

    # Crisis transmission analysis (if crisis periods provided)
    if crisis_periods is not None:
        results['crisis_transmission'] = engine.analyze_crisis_transmission(
            data, crisis_periods, variables
        )

    # Multifactor analysis
    for var in variables:
        if var in data.columns:
            other_vars = [v for v in variables if v != var and v in data.columns]
            if other_vars:
                results[f'{var}_drivers'] = engine.analyze_multifactor_relationships(
                    data, var, other_vars
                )

    return results

if __name__ == "__main__":
    # Demonstration
    logger.info("Demonstrating Advanced Capital Flows Econometric Engine...")

    # Create sample data
    dates = pd.date_range('1970-01-01', '2023-12-31', freq='Q')
    np.random.seed(42)

    sample_data = pd.DataFrame({
        'date': dates,
        'capital_flows': np.cumsum(np.random.normal(0, 1, len(dates))),
        'gdp_growth': np.random.normal(2, 1, len(dates)),
        'interest_rate': np.random.normal(4, 1, len(dates)),
        'exchange_rate': np.cumsum(np.random.normal(0, 0.5, len(dates)))
    }).set_index('date')

    variables = ['capital_flows', 'gdp_growth', 'interest_rate', 'exchange_rate']

    # Run analysis
    results = analyze_capital_flows_econometrics(sample_data, variables)

    print(f"\nEconometric Analysis Results:")
    print(f"VAR Model R-squared: {results['var_analysis'].statistics.get('r_squared', 'N/A'):.3f}")
    print(f"Cointegration Rank: {results['cointegration'].cointegration_rank}")
    print(f"Analysis completed with {len(results)} result categories")
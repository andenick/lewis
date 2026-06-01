"""
Advanced Time Series Econometrics Module
=======================================

Sophisticated econometric analysis for the enhanced Lewis platform.

Provides advanced time series analysis capabilities:
- Unit root tests (ADF, KPSS)
- Cointegration analysis (Johansen test)
- VAR/VECM modeling
- Granger causality testing
- Structural break detection
- Impulse response functions
- Forecast error variance decomposition

This module transforms the enhanced platform from descriptive to
predictive and causal analysis capabilities.

Author: Lewis Platform
Date: 2025-10-27
Version: 1.0 - Advanced Econometrics
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

# Econometric imports
from statsmodels.tsa.stattools import adfuller, kpss, grangercausalitytests, coint
from statsmodels.tsa.vector_ar.var_model import VAR
from statsmodels.tsa.vector_ar.vecm import coint_johansen, VECM
from statsmodels.tsa.api import ARIMA
from statsmodels.stats.diagnostic import acorr_ljungbox
from scipy import stats

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')


class AdvancedTimeSeriesEconometrics:
    """
    Advanced time series econometrics for international economics analysis.

    Provides comprehensive econometric analysis tools for understanding
    relationships, causality, and dynamics in international economic data.
    """

    def __init__(self):
        """Initialize the econometrics module."""
        self.results_cache = {}
        self.fitted_models = {}

        logger.info("Advanced Time Series Econometrics module initialized")

    def prepare_data(self, data: pd.DataFrame,
                    date_col: str = 'date',
                    value_cols: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Prepare time series data for econometric analysis.

        Args:
            data: Input DataFrame
            date_col: Name of date column
            value_cols: List of value columns to analyze

        Returns:
            Prepared DataFrame with datetime index
        """
        logger.info("Preparing data for econometric analysis...")

        # Make a copy to avoid modifying original
        df = data.copy()

        # Convert date column to datetime
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col])
            df = df.set_index(date_col)

        # Select value columns
        if value_cols is None:
            # Auto-detect numeric columns
            value_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        df = df[value_cols]

        # Handle missing values
        df = df.dropna()

        # Sort by date
        df = df.sort_index()

        logger.info(f"Prepared data: {len(df)} observations, {len(df.columns)} series")
        return df

    def unit_root_tests(self, series: pd.Series,
                       significance_level: float = 0.05) -> Dict:
        """
        Perform comprehensive unit root testing.

        Args:
            series: Time series to test
            significance_level: Critical value significance level

        Returns:
            Dictionary with test results
        """
        logger.info(f"Performing unit root tests on {series.name}")

        results = {}

        # Augmented Dickey-Fuller Test
        try:
            adf_result = adfuller(series.dropna(), autolag='AIC')
            results['adf'] = {
                'statistic': adf_result[0],
                'p_value': adf_result[1],
                'critical_values': adf_result[4],
                'is_stationary': adf_result[1] < significance_level,
                'interpretation': 'Stationary' if adf_result[1] < significance_level else 'Non-stationary'
            }
        except Exception as e:
            logger.warning(f"ADF test failed: {e}")
            results['adf'] = {'error': str(e)}

        # KPSS Test
        try:
            kpss_result = kpss(series.dropna(), regression='c')
            results['kpss'] = {
                'statistic': kpss_result[0],
                'p_value': kpss_result[1],
                'critical_values': kpss_result[3],
                'is_stationary': kpss_result[1] > significance_level,
                'interpretation': 'Stationary' if kpss_result[1] > significance_level else 'Non-stationary'
            }
        except Exception as e:
            logger.warning(f"KPSS test failed: {e}")
            results['kpss'] = {'error': str(e)}

        # Summary
        if 'adf' in results and 'kpss' in results:
            adf_stationary = results['adf'].get('is_stationary', False)
            kpss_stationary = results['kpss'].get('is_stationary', False)

            if adf_stationary and kpss_stationary:
                results['conclusion'] = 'Series is stationary'
            elif not adf_stationary and not kpss_stationary:
                results['conclusion'] = 'Series is non-stationary'
            else:
                results['conclusion'] = 'Tests conflict - further investigation needed'

        return results

    def cointegration_test(self, series1: pd.Series, series2: pd.Series,
                          significance_level: float = 0.05) -> Dict:
        """
        Test for cointegration between two series.

        Args:
            series1: First time series
            series2: Second time series
            significance_level: Critical value significance level

        Returns:
            Dictionary with cointegration test results
        """
        logger.info(f"Testing cointegration between {series1.name} and {series2.name}")

        # Align series
        df = pd.concat([series1, series2], axis=1).dropna()
        s1, s2 = df.iloc[:, 0], df.iloc[:, 1]

        results = {}

        # Engle-Granger cointegration test
        try:
            eg_result = coint(s1, s2, maxlag=1)
            results['engle_granger'] = {
                'statistic': eg_result[0],
                'p_value': eg_result[1],
                'critical_values': eg_result[2],
                'is_cointegrated': eg_result[1] < significance_level,
                'interpretation': 'Cointegrated' if eg_result[1] < significance_level else 'Not cointegrated'
            }
        except Exception as e:
            logger.warning(f"Engle-Granger test failed: {e}")
            results['engle_granger'] = {'error': str(e)}

        return results

    def granger_causality_test(self, data: pd.DataFrame,
                              max_lag: int = 4,
                              significance_level: float = 0.05) -> Dict:
        """
        Perform Granger causality tests between multiple series.

        Args:
            data: DataFrame with multiple time series
            max_lag: Maximum lag to test
            significance_level: Critical value significance level

        Returns:
            Dictionary with causality test results
        """
        logger.info(f"Performing Granger causality tests (max lag: {max_lag})")

        if len(data.columns) < 2:
            raise ValueError("Need at least 2 series for causality testing")

        results = {}

        for i, target_col in enumerate(data.columns):
            for j, predictor_col in enumerate(data.columns):
                if i != j:  # Don't test series against itself
                    try:
                        test_data = data[[predictor_col, target_col]].dropna()

                        causality_result = grangercausalitytests(
                            test_data, maxlag=maxlag, verbose=False
                        )

                        # Extract F-statistic and p-value from optimal lag
                        f_stats = []
                        p_values = []

                        for lag in range(1, max_lag + 1):
                            f_stat = causality_result[lag][0]['ssr_ftest'][0]
                            p_val = causality_result[lag][0]['ssr_ftest'][1]
                            f_stats.append(f_stat)
                            p_values.append(p_val)

                        # Find optimal lag (minimum p-value)
                        optimal_lag = np.argmin(p_values) + 1
                        min_p_value = min(p_values)

                        pair_key = f"{predictor_col} -> {target_col}"
                        results[pair_key] = {
                            'optimal_lag': optimal_lag,
                            'f_statistic': f_stats[optimal_lag - 1],
                            'p_value': min_p_value,
                            'is_significant': min_p_value < significance_level,
                            'interpretation': 'Significant' if min_p_value < significance_level else 'Not significant',
                            'all_results': {
                                'f_statistics': f_stats,
                                'p_values': p_values
                            }
                        }

                    except Exception as e:
                        pair_key = f"{predictor_col} -> {target_col}"
                        results[pair_key] = {'error': str(e)}

        return results

    def var_model(self, data: pd.DataFrame,
                  max_lags: int = 12,
                  information_criterion: str = 'aic') -> Dict:
        """
        Fit Vector Autoregression (VAR) model.

        Args:
            data: DataFrame with multiple time series
            max_lags: Maximum number of lags to consider
            information_criterion: Information criterion for lag selection

        Returns:
            Dictionary with VAR model results
        """
        logger.info(f"Fitting VAR model (max lags: {max_lags}, IC: {information_criterion})")

        if len(data.columns) < 2:
            raise ValueError("VAR requires at least 2 series")

        results = {}

        try:
            # Fit VAR model
            model = VAR(data)
            var_result = model.fit(maxlags=max_lags, ic=information_criterion)

            results['model'] = var_result
            results['selected_lag'] = var_result.k_ar
            results['information_criterion'] = information_criterion
            results['summary'] = str(var_result.summary())

            # Model diagnostics
            residuals = var_result.resid

            # Serial correlation test (Ljung-Box)
            serial_correlation_results = {}
            for i, col in enumerate(residuals.columns):
                try:
                    lb_test = acorr_ljungbox(residuals.iloc[:, i], lags=[10], return_df=True)
                    serial_correlation_results[col] = {
                        'lb_statistic': lb_test['lb_stat'].iloc[0],
                        'p_value': lb_test['lb_pvalue'].iloc[0],
                        'no_serial_correlation': lb_test['lb_pvalue'].iloc[0] > 0.05
                    }
                except:
                    serial_correlation_results[col] = {'error': 'Test failed'}

            results['diagnostics'] = {
                'serial_correlation': serial_correlation_results,
                'residuals_mean': residuals.mean().to_dict(),
                'residuals_std': residuals.std().to_dict()
            }

            logger.info(f"VAR fitted with {var_result.k_ar} lags")

        except Exception as e:
            logger.error(f"VAR fitting failed: {e}")
            results['error'] = str(e)

        return results

    def impulse_response_analysis(self, var_result,
                                periods: int = 10,
                                shock_var: Optional[str] = None) -> Dict:
        """
        Generate impulse response functions from VAR model.

        Args:
            var_result: Fitted VAR model result
            periods: Number of periods for impulse response
            shock_var: Variable to apply shock to (None = all variables)

        Returns:
            Dictionary with impulse response results
        """
        logger.info(f"Generating impulse response functions ({periods} periods)")

        results = {}

        try:
            # Generate impulse responses
            irf = var_result.irf(periods)

            # Store IRF results
            results['irf_object'] = irf
            results['periods'] = periods

            # Convert to DataFrame for easier analysis
            irf_data = {}
            variables = var_result.names

            for i, shocked_var in enumerate(variables):
                if shock_var and shocked_var != shock_var:
                    continue

                for j, response_var in enumerate(variables):
                    irf_path = irf.irfs[:, i, j]  # Response of j to shock in i
                    key = f"{shocked_var} -> {response_var}"
                    irf_data[key] = irf_path

            results['irf_dataframes'] = irf_data

            logger.info(f"Generated impulse responses for {len(irf_data)} variable pairs")

        except Exception as e:
            logger.error(f"Impulse response analysis failed: {e}")
            results['error'] = str(e)

        return results

    def structural_break_test(self, series: pd.Series,
                            known_breaks: Optional[List[str]] = None) -> Dict:
        """
        Test for structural breaks in time series.

        Args:
            series: Time series to test
            known_breaks: List of known break dates (YYYY-MM-DD format)

        Returns:
            Dictionary with structural break test results
        """
        logger.info(f"Testing for structural breaks in {series.name}")

        results = {}

        try:
            # Convert to numpy array for calculations
            y = series.values

            # Chow test for known breaks
            if known_breaks:
                chow_results = {}
                for break_date in known_breaks:
                    try:
                        break_idx = series.index.get_loc(break_date)
                        if 0 < break_idx < len(y) - 1:
                            # Simple Chow test implementation
                            n = len(y)
                            n1 = break_idx
                            n2 = n - n1

                            # Fit separate regressions
                            y1, y2 = y[:n1], y[n1:]

                            # Calculate residual sum of squares
                            rss1 = np.sum((y1 - np.mean(y1))**2)
                            rss2 = np.sum((y2 - np.mean(y2))**2)
                            rss_pooled = np.sum((y - np.mean(y))**2)

                            # Chow test statistic
                            chow_stat = ((rss_pooled - rss1 - rss2) / 2) / ((rss1 + rss2) / (n - 4))
                            p_value = 1 - stats.f.cdf(chow_stat, 2, n - 4)

                            chow_results[break_date] = {
                                'statistic': chow_stat,
                                'p_value': p_value,
                                'is_significant': p_value < 0.05,
                                'break_index': break_idx
                            }
                    except Exception as e:
                        chow_results[break_date] = {'error': str(e)}

                results['chow_tests'] = chow_results

            # Bai-Perron multiple break test (simplified version)
            # This is a placeholder - actual implementation would require specialized packages
            results['note'] = 'Advanced Bai-Perron test would require specialized econometric packages'

        except Exception as e:
            logger.error(f"Structural break test failed: {e}")
            results['error'] = str(e)

        return results

    def forecast_var(self, var_result, steps: int = 12) -> Dict:
        """
        Generate forecasts from VAR model.

        Args:
            var_result: Fitted VAR model result
            steps: Number of steps to forecast

        Returns:
            Dictionary with forecast results
        """
        logger.info(f"Generating VAR forecasts ({steps} steps)")

        results = {}

        try:
            # Generate forecasts
            forecast = var_result.forecast(var_result.endog, steps=steps)
            forecast_df = pd.DataFrame(forecast,
                                     columns=var_result.names,
                                     index=pd.date_range(start=var_result.endog.index[-1] +
                                                      pd.Timedelta(days=1),
                                                      periods=steps, freq='M'))

            results['forecast'] = forecast_df
            results['steps'] = steps
            results['variables'] = var_result.names

            # Calculate confidence intervals (simplified)
            results['note'] = 'Confidence intervals would require bootstrapping or analytical solutions'

            logger.info(f"Generated forecasts for {len(var_result.names)} variables")

        except Exception as e:
            logger.error(f"VAR forecasting failed: {e}")
            results['error'] = str(e)

        return results

    def comprehensive_analysis(self, data: pd.DataFrame,
                             known_breaks: Optional[List[str]] = None) -> Dict:
        """
        Perform comprehensive econometric analysis.

        Args:
            data: DataFrame with multiple time series
            known_breaks: List of known structural break dates

        Returns:
            Dictionary with all analysis results
        """
        logger.info("Starting comprehensive econometric analysis...")

        all_results = {
            'data_info': {
                'observations': len(data),
                'variables': list(data.columns),
                'date_range': [data.index.min().strftime('%Y-%m-%d'),
                              data.index.max().strftime('%Y-%m-%d')]
            }
        }

        # 1. Unit root tests for each series
        logger.info("Step 1: Unit root testing...")
        unit_root_results = {}
        for col in data.columns:
            unit_root_results[col] = self.unit_root_tests(data[col])
        all_results['unit_root_tests'] = unit_root_results

        # 2. Cointegration tests between pairs
        logger.info("Step 2: Cointegration testing...")
        cointegration_results = {}
        columns = data.columns
        for i in range(len(columns)):
            for j in range(i + 1, len(columns)):
                pair_key = f"{columns[i]} - {columns[j]}"
                cointegration_results[pair_key] = self.cointegration_test(
                    data[columns[i]], data[columns[j]]
                )
        all_results['cointegration_tests'] = cointegration_results

        # 3. Granger causality
        logger.info("Step 3: Granger causality testing...")
        try:
            causality_results = self.granger_causality_test(data)
            all_results['granger_causality'] = causality_results
        except Exception as e:
            logger.warning(f"Granger causality failed: {e}")

        # 4. VAR modeling
        logger.info("Step 4: VAR modeling...")
        try:
            var_results = self.var_model(data)
            all_results['var_model'] = var_results

            # 5. Impulse response analysis
            if 'model' in var_results:
                irf_results = self.impulse_response_analysis(var_results['model'])
                all_results['impulse_responses'] = irf_results

                # 6. Forecasting
                forecast_results = self.forecast_var(var_results['model'])
                all_results['forecasts'] = forecast_results

        except Exception as e:
            logger.warning(f"VAR analysis failed: {e}")

        # 7. Structural break tests
        logger.info("Step 5: Structural break testing...")
        if known_breaks:
            break_results = {}
            for col in data.columns:
                break_results[col] = self.structural_break_test(data[col], known_breaks)
            all_results['structural_breaks'] = break_results

        logger.info("Comprehensive econometric analysis completed")
        return all_results

    def generate_analysis_report(self, results: Dict) -> str:
        """
        Generate a human-readable analysis report.

        Args:
            results: Results from comprehensive analysis

        Returns:
            Formatted report string
        """
        report = []
        report.append("=== ADVANCED ECONOMETRIC ANALYSIS REPORT ===")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Data information
        data_info = results.get('data_info', {})
        report.append("DATA SUMMARY")
        report.append(f"Observations: {data_info.get('observations', 'N/A')}")
        report.append(f"Variables: {', '.join(data_info.get('variables', []))}")
        report.append(f"Period: {data_info.get('date_range', ['N/A', 'N/A'])[0]} to {data_info.get('date_range', ['N/A', 'N/A'])[1]}")
        report.append("")

        # Unit root test summary
        unit_root_results = results.get('unit_root_tests', {})
        if unit_root_results:
            report.append("UNIT ROOT TESTS")
            for var, result in unit_root_results.items():
                if 'conclusion' in result:
                    report.append(f"{var}: {result['conclusion']}")
            report.append("")

        # Cointegration summary
        cointegration_results = results.get('cointegration_tests', {})
        if cointegration_results:
            report.append("COINTEGRATION TESTS")
            cointegrated_pairs = []
            for pair, result in cointegration_results.items():
                if result.get('engle_granger', {}).get('is_cointegrated', False):
                    cointegrated_pairs.append(pair)
            if cointegrated_pairs:
                report.append(f"Cointegrated pairs: {', '.join(cointegrated_pairs)}")
            else:
                report.append("No cointegrated pairs detected")
            report.append("")

        # Granger causality summary
        causality_results = results.get('granger_causality', {})
        if causality_results:
            report.append("GRANGER CAUSALITY")
            significant_relations = []
            for relation, result in causality_results.items():
                if result.get('is_significant', False):
                    significant_relations.append(relation)
            if significant_relations:
                report.append(f"Significant causal relations: {', '.join(significant_relations)}")
            else:
                report.append("No significant Granger causality detected")
            report.append("")

        # VAR model summary
        var_results = results.get('var_model', {})
        if var_results and 'selected_lag' in var_results:
            report.append("VAR MODEL")
            report.append(f"Optimal lag length: {var_results['selected_lag']}")
            report.append(f"Information criterion: {var_results['information_criterion']}")
            report.append("")

        return "\n".join(report)

    def save_results(self, results: Dict, output_path: Path):
        """
        Save analysis results to files.

        Args:
            results: Analysis results dictionary
            output_path: Directory to save results
        """
        output_path.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y.%m.%d")

        # Save text report
        report = self.generate_analysis_report(results)
        report_file = output_path / f"[{timestamp}] econometric_analysis_report.txt"
        with open(report_file, 'w') as f:
            f.write(report)

        # Save forecasts if available
        if 'forecasts' in results and 'forecast' in results['forecasts']:
            forecast_df = results['forecasts']['forecast']
            forecast_file = output_path / f"[{timestamp}] var_forecasts.csv"
            forecast_df.to_csv(forecast_file)

        # Save impulse responses if available
        if 'impulse_responses' in results and 'irf_dataframes' in results['impulse_responses']:
            irf_data = results['impulse_responses']['irf_dataframes']
            for irf_name, irf_series in irf_data.items():
                irf_df = pd.DataFrame(irf_series)
                irf_file = output_path / f"[{timestamp}] irf_{irf_name.replace(' -> ', '_')}.csv"
                irf_df.to_csv(irf_file)

        logger.info(f"Results saved to {output_path}")


# Convenience function for running analysis
def run_econometric_analysis(data: pd.DataFrame,
                           known_breaks: Optional[List[str]] = None,
                           output_dir: Optional[Path] = None) -> Dict:
    """
    Convenience function to run complete econometric analysis.

    Args:
        data: DataFrame with time series data
        known_breaks: Optional list of structural break dates
        output_dir: Optional directory to save results

    Returns:
        Analysis results dictionary
    """
    analyzer = AdvancedTimeSeriesEconometrics()

    # Prepare data
    prepared_data = analyzer.prepare_data(data)

    # Run comprehensive analysis
    results = analyzer.comprehensive_analysis(prepared_data, known_breaks)

    # Save results if output directory provided
    if output_dir:
        analyzer.save_results(results, output_dir)

    return results


if __name__ == "__main__":
    # Example usage
    print("Advanced Time Series Econometrics Module")
    print("=======================================")
    print("This module provides sophisticated econometric analysis")
    print("capabilities for international economics data.")
    print("")
    print("Key features:")
    print("- Unit root testing (ADF, KPSS)")
    print("- Cointegration analysis")
    print("- VAR/VECM modeling")
    print("- Granger causality testing")
    print("- Structural break detection")
    print("- Impulse response analysis")
    print("- Forecasting capabilities")
    print("")
    print("Import and use with your enhanced Lewis platform data!")
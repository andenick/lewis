"""
Monte Carlo Economic Simulator
==============================

Advanced Monte Carlo simulation system for economic uncertainty analysis.

Provides sophisticated simulation capabilities:
- Stochastic process simulation for economic variables
- Scenario analysis and stress testing
- Risk assessment and value-at-risk calculations
- Correlated random variable generation
- Bootstrap methods for empirical distributions
- Dynamic stochastic general equilibrium (DSGE) simulation

This module provides comprehensive uncertainty quantification
for economic forecasting and risk analysis.

Author: Lewis Platform
Date: 2025-10-27
Version: 1.0 - Monte Carlo Simulation
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import List, Dict, Optional, Union, Tuple, Callable
from datetime import datetime, timedelta
import warnings
import logging

# Statistical imports
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')


class MonteCarloEconomicSimulator:
    """
    Advanced Monte Carlo simulator for economic variables.

    Provides sophisticated simulation capabilities including stochastic
    processes, scenario analysis, risk assessment, and uncertainty
    quantification for international economics applications.
    """

    def __init__(self, random_seed: Optional[int] = None):
        """
        Initialize the Monte Carlo simulator.

        Args:
            random_seed: Random seed for reproducibility
        """
        if random_seed is not None:
            np.random.seed(random_seed)

        self.simulation_results = {}
        self.correlation_matrices = {}
        self.scenario_results = {}

        logger.info(f"Monte Carlo Economic Simulator initialized (seed: {random_seed})")

    def generate_geometric_brownian_motion(self, initial_value: float,
                                           drift: float,
                                           volatility: float,
                                           time_horizon: float,
                                           n_steps: int,
                                           n_simulations: int) -> np.ndarray:
        """
        Generate geometric Brownian motion paths.

        Args:
            initial_value: Starting value
            drift: Drift parameter (μ)
            volatility: Volatility parameter (σ)
            time_horizon: Total time to simulate
            n_steps: Number of time steps
            n_simulations: Number of simulation paths

        Returns:
            Array of simulated paths
        """
        logger.info(f"Generating GBM: {n_simulations} paths, {n_steps} steps")

        dt = time_horizon / n_steps

        # Generate random shocks
        random_shocks = np.random.standard_normal((n_simulations, n_steps))

        # Generate Brownian motion
        brownian_motion = np.cumsum(random_shocks * np.sqrt(dt), axis=1)

        # Generate GBM paths
        time_array = np.linspace(0, time_horizon, n_steps)
        paths = initial_value * np.exp((drift - 0.5 * volatility**2) * time_array +
                                      volatility * brownian_motion)

        return paths

    def generate_mean_reverting_process(self, initial_value: float,
                                       long_term_mean: float,
                                       mean_reversion_speed: float,
                                       volatility: float,
                                       time_horizon: float,
                                       n_steps: int,
                                       n_simulations: int) -> np.ndarray:
        """
        Generate Ornstein-Uhlenbeck (mean-reverting) process paths.

        Args:
            initial_value: Starting value
            long_term_mean: Long-term mean (θ)
            mean_reversion_speed: Mean reversion speed (κ)
            volatility: Volatility parameter (σ)
            time_horizon: Total time to simulate
            n_steps: Number of time steps
            n_simulations: Number of simulation paths

        Returns:
            Array of simulated paths
        """
        logger.info(f"Generating OU process: {n_simulations} paths, {n_steps} steps")

        dt = time_horizon / n_steps
        paths = np.zeros((n_simulations, n_steps))
        paths[:, 0] = initial_value

        for i in range(1, n_steps):
            # Generate random shocks
            random_shocks = np.random.standard_normal(n_simulations)

            # Ornstein-Uhlenbeck process
            drift = mean_reversion_speed * (long_term_mean - paths[:, i-1]) * dt
            diffusion = volatility * np.sqrt(dt) * random_shocks

            paths[:, i] = paths[:, i-1] + drift + diffusion

        return paths

    def generate_jump_diffusion_process(self, initial_value: float,
                                        drift: float,
                                        volatility: float,
                                        jump_intensity: float,
                                        jump_mean: float,
                                        jump_volatility: float,
                                        time_horizon: float,
                                        n_steps: int,
                                        n_simulations: int) -> np.ndarray:
        """
        Generate Merton jump-diffusion process paths.

        Args:
            initial_value: Starting value
            drift: Drift parameter (μ)
            volatility: Diffusion volatility (σ)
            jump_intensity: Jump intensity (λ)
            jump_mean: Jump size mean (μ_J)
            jump_volatility: Jump size volatility (σ_J)
            time_horizon: Total time to simulate
            n_steps: Number of time steps
            n_simulations: Number of simulation paths

        Returns:
            Array of simulated paths
        """
        logger.info(f"Generating jump-diffusion: {n_simulations} paths, {n_steps} steps")

        dt = time_horizon / n_steps
        paths = np.zeros((n_simulations, n_steps))
        paths[:, 0] = initial_value

        for i in range(1, n_steps):
            # Diffusion component
            diffusion_shocks = np.random.standard_normal(n_simulations)
            diffusion = volatility * np.sqrt(dt) * diffusion_shocks

            # Jump component
            n_jumps = np.random.poisson(jump_intensity * dt, n_simulations)
            jump_sizes = np.random.normal(jump_mean, jump_volatility, n_simulations)
            jumps = n_jumps * jump_sizes

            # Combined process
            drift_component = drift * dt
            paths[:, i] = paths[:, i-1] * (1 + drift_component + diffusion) + jumps

        return np.maximum(paths, 0)  # Ensure non-negative values

    def generate_correlated_variables(self, means: np.ndarray,
                                     volatilities: np.ndarray,
                                     correlation_matrix: np.ndarray,
                                     time_horizon: float,
                                     n_steps: int,
                                     n_simulations: int) -> Dict:
        """
        Generate correlated economic variables.

        Args:
            means: Array of mean values for each variable
            volatilities: Array of volatilities for each variable
            correlation_matrix: Correlation matrix between variables
            time_horizon: Total time to simulate
            n_steps: Number of time steps
            n_simulations: Number of simulation paths

        Returns:
            Dictionary with simulated variables
        """
        logger.info(f"Generating {len(means)} correlated variables")

        n_variables = len(means)

        # Perform Cholesky decomposition
        try:
            chol_matrix = np.linalg.cholesky(correlation_matrix)
        except np.linalg.LinAlgError:
            logger.warning("Correlation matrix not positive definite, using nearest positive definite")
            # Find nearest positive definite matrix
            eigenvals, eigenvecs = np.linalg.eigh(correlation_matrix)
            eigenvals[eigenvals < 0] = 0
            correlation_matrix = eigenvecs @ np.diag(eigenvals) @ eigenvecs.T
            chol_matrix = np.linalg.cholesky(correlation_matrix)

        # Generate correlated random variables
        uncorrelated_shocks = np.random.standard_normal((n_simulations, n_steps, n_variables))
        correlated_shocks = np.zeros_like(uncorrelated_shocks)

        for i in range(n_simulations):
            for j in range(n_steps):
                correlated_shocks[i, j] = chol_matrix @ uncorrelated_shocks[i, j]

        # Generate paths for each variable
        dt = time_horizon / n_steps
        paths = {}

        for var_idx in range(n_variables):
            var_paths = np.zeros((n_simulations, n_steps))
            var_paths[:, 0] = means[var_idx]

            for i in range(1, n_steps):
                drift = means[var_idx] * dt
                diffusion = volatilities[var_idx] * np.sqrt(dt) * correlated_shocks[:, i-1, var_idx]
                var_paths[:, i] = var_paths[:, i-1] + drift + diffusion

            paths[f'variable_{var_idx}'] = var_paths

        return paths

    def bootstrap_simulation(self, historical_data: pd.Series,
                           n_simulations: int,
                           block_size: Optional[int] = None) -> np.ndarray:
        """
        Perform bootstrap simulation from historical data.

        Args:
            historical_data: Historical time series data
            n_simulations: Number of bootstrap simulations
            block_size: Block size for block bootstrap (None = simple bootstrap)

        Returns:
            Bootstrap simulated paths
        """
        logger.info(f"Bootstrap simulation: {n_simulations} paths from {len(historical_data)} observations")

        data_values = historical_data.values
        n_obs = len(data_values)
        paths = []

        if block_size is None:
            # Simple bootstrap
            for _ in range(n_simulations):
                bootstrap_sample = np.random.choice(data_values, size=n_obs, replace=True)
                paths.append(bootstrap_sample)
        else:
            # Block bootstrap
            for _ in range(n_simulations):
                n_blocks = n_obs // block_size
                bootstrap_path = []

                for _ in range(n_blocks):
                    start_idx = np.random.randint(0, n_obs - block_size + 1)
                    block = data_values[start_idx:start_idx + block_size]
                    bootstrap_path.extend(block)

                paths.append(np.array(bootstrap_path[:n_obs]))

        return np.array(paths)

    def scenario_analysis(self, base_simulation: np.ndarray,
                         scenario_params: Dict[str, Dict]) -> Dict:
        """
        Perform scenario analysis on base simulation.

        Args:
            base_simulation: Base simulation results
            scenario_params: Dictionary of scenario parameters
                Format: {'scenario_name': {'drift_adjustment': x, 'volatility_adjustment': y}}

        Returns:
            Dictionary with scenario results
        """
        logger.info(f"Performing scenario analysis: {len(scenario_params)} scenarios")

        results = {'base': base_simulation}

        for scenario_name, params in scenario_params.items():
            adjusted_simulation = base_simulation.copy()

            # Apply drift adjustment
            if 'drift_adjustment' in params:
                drift_adj = params['drift_adjustment']
                time_array = np.linspace(0, 1, base_simulation.shape[1])
                drift_effect = drift_adj * time_array
                adjusted_simulation = adjusted_simulation * (1 + drift_effect)

            # Apply volatility adjustment
            if 'volatility_adjustment' in params:
                vol_adj = params['volatility_adjustment']
                random_shocks = np.random.standard_normal(adjusted_simulation.shape)
                volatility_effect = vol_adj * np.cumsum(random_shocks, axis=1) * np.sqrt(1/adjusted_simulation.shape[1])
                adjusted_simulation = adjusted_simulation * (1 + volatility_effect)

            # Apply shock
            if 'shock_magnitude' in params and 'shock_time' in params:
                shock_magnitude = params['shock_magnitude']
                shock_time = params['shock_time']
                if shock_time < adjusted_simulation.shape[1]:
                    adjusted_simulation[:, shock_time:] *= (1 + shock_magnitude)

            results[scenario_name] = adjusted_simulation

        return results

    def calculate_risk_metrics(self, simulations: np.ndarray,
                              confidence_levels: List[float] = [0.95, 0.99]) -> Dict:
        """
        Calculate risk metrics from simulation results.

        Args:
            simulations: Simulation results array
            confidence_levels: List of confidence levels for VaR

        Returns:
            Dictionary with risk metrics
        """
        logger.info("Calculating risk metrics")

        # Get final values from simulations
        final_values = simulations[:, -1]

        risk_metrics = {}

        # Value at Risk (VaR)
        for cl in confidence_levels:
            var_value = np.percentile(final_values, (1 - cl) * 100)
            risk_metrics[f'VaR_{int(cl*100)}%'] = var_value

        # Expected Shortfall (Conditional VaR)
        for cl in confidence_levels:
            var_threshold = np.percentile(final_values, (1 - cl) * 100)
            tail_losses = final_values[final_values <= var_threshold]
            if len(tail_losses) > 0:
                expected_shortfall = np.mean(tail_losses)
                risk_metrics[f'ES_{int(cl*100)}%'] = expected_shortfall

        # Maximum drawdown
        drawdowns = []
        for path in simulations:
            peak = np.maximum.accumulate(path)
            drawdown = (path - peak) / peak
            drawdowns.append(np.min(drawdown))

        risk_metrics['max_drawdown_mean'] = np.mean(drawdowns)
        risk_metrics['max_drawdown_std'] = np.std(drawdowns)
        risk_metrics['max_drawdown_worst'] = np.min(drawdowns)

        # Statistics
        risk_metrics['mean_final'] = np.mean(final_values)
        risk_metrics['std_final'] = np.std(final_values)
        risk_metrics['percentile_5'] = np.percentile(final_values, 5)
        risk_metrics['percentile_95'] = np.percentile(final_values, 95)

        return risk_metrics

    def monte_carlo_var(self, portfolio_value: float,
                        returns: pd.Series,
                        confidence_levels: List[float] = [0.95, 0.99],
                        n_simulations: int = 10000,
                        time_horizon: int = 1) -> Dict:
        """
        Calculate Monte Carlo Value at Risk.

        Args:
            portfolio_value: Current portfolio value
            returns: Historical returns data
            confidence_levels: Confidence levels for VaR
            n_simulations: Number of Monte Carlo simulations
            time_horizon: Time horizon in days

        Returns:
            Dictionary with VaR results
        """
        logger.info(f"Monte Carlo VaR: {n_simulations} simulations, {time_horizon} days")

        # Estimate parameters from historical returns
        mean_return = returns.mean()
        volatility = returns.std()

        # Generate correlated returns using geometric Brownian motion
        simulated_returns = self.generate_geometric_brownian_motion(
            initial_value=1.0,
            drift=mean_return,
            volatility=volatility,
            time_horizon=time_horizon/252,  # Convert to years
            n_steps=time_horizon,
            n_simulations=n_simulations
        )

        # Calculate portfolio values
        final_returns = simulated_returns[:, -1]
        portfolio_values = portfolio_value * final_returns
        portfolio_losses = portfolio_value - portfolio_values

        # Calculate VaR and Expected Shortfall
        var_results = {}
        for cl in confidence_levels:
            var_value = np.percentile(portfolio_losses, cl * 100)
            var_results[f'VaR_{int(cl*100)}%'] = var_value

            # Expected Shortfall
            tail_losses = portfolio_losses[portfolio_losses >= var_value]
            if len(tail_losses) > 0:
                expected_shortfall = np.mean(tail_losses)
                var_results[f'ES_{int(cl*100)}%'] = expected_shortfall

        var_results['portfolio_value'] = portfolio_value
        var_results['time_horizon_days'] = time_horizon
        var_results['n_simulations'] = n_simulations
        var_results['mean_return'] = mean_return
        var_results['volatility'] = volatility

        return var_results

    def generate_simulation_report(self, results: Dict, title: str = "Monte Carlo Simulation Results") -> str:
        """
        Generate a comprehensive simulation report.

        Args:
            results: Simulation results dictionary
            title: Report title

        Returns:
            Formatted report string
        """
        report = []
        report.append(f"=== {title} ===")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Risk metrics summary
        if 'risk_metrics' in results:
            risk = results['risk_metrics']
            report.append("RISK METRICS")
            report.append(f"Mean Final Value: {risk.get('mean_final', 'N/A'):.4f}")
            report.append(f"Standard Deviation: {risk.get('std_final', 'N/A'):.4f}")
            report.append(f"5th Percentile: {risk.get('percentile_5', 'N/A'):.4f}")
            report.append(f"95th Percentile: {risk.get('percentile_95', 'N/A'):.4f}")
            report.append(f"Worst Maximum Drawdown: {risk.get('max_drawdown_worst', 'N/A'):.4f}")
            report.append("")

            for key, value in risk.items():
                if key.startswith('VaR_') or key.startswith('ES_'):
                    report.append(f"{key}: {value:.4f}")
            report.append("")

        # Simulation parameters
        if 'n_simulations' in results:
            report.append("SIMULATION PARAMETERS")
            report.append(f"Number of Simulations: {results['n_simulations']}")
            if 'time_horizon' in results:
                report.append(f"Time Horizon: {results['time_horizon']}")
            report.append("")

        return "\n".join(report)

    def save_simulation_results(self, results: Dict, output_path: Path, simulation_name: str):
        """
        Save simulation results to files.

        Args:
            results: Simulation results
            output_path: Directory to save results
            simulation_name: Name of the simulation
        """
        output_path.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y.%m.%d")

        # Save simulation paths
        for key, value in results.items():
            if isinstance(value, np.ndarray) and value.ndim == 2:
                df = pd.DataFrame(value)
                sim_file = output_path / f"[{timestamp}] {simulation_name}_{key}.csv"
                df.to_csv(sim_file)

        # Save risk metrics
        if 'risk_metrics' in results:
            risk_df = pd.DataFrame([results['risk_metrics']])
            risk_file = output_path / f"[{timestamp}] {simulation_name}_risk_metrics.csv"
            risk_df.to_csv(risk_file)

        # Save report
        report = self.generate_simulation_report(results, f"{simulation_name} Simulation Results")
        report_file = output_path / f"[{timestamp}] {simulation_name}_report.txt"
        with open(report_file, 'w') as f:
            f.write(report)

        logger.info(f"Simulation results saved to {output_path}")


# Convenience function for running Monte Carlo analysis
def run_monte_carlo_analysis(data: pd.Series,
                           n_simulations: int = 1000,
                           time_horizon: float = 1.0,
                           confidence_levels: List[float] = [0.95, 0.99],
                           output_dir: Optional[Path] = None) -> Dict:
    """
    Convenience function to run complete Monte Carlo analysis.

    Args:
        data: Historical data for parameter estimation
        n_simulations: Number of simulations
        time_horizon: Time horizon for simulation
        confidence_levels: Confidence levels for risk metrics
        output_dir: Optional directory to save results

    Returns:
        Monte Carlo analysis results
    """
    simulator = MonteCarloEconomicSimulator()

    # Estimate parameters
    returns = data.pct_change().dropna()
    mean_return = returns.mean()
    volatility = returns.std()

    # Generate GBM simulations
    simulations = simulator.generate_geometric_brownian_motion(
        initial_value=data.iloc[-1],
        drift=mean_return,
        volatility=volatility,
        time_horizon=time_horizon,
        n_steps=int(time_horizon * 252),  # Assuming daily data
        n_simulations=n_simulations
    )

    # Calculate risk metrics
    risk_metrics = simulator.calculate_risk_metrics(simulations, confidence_levels)

    results = {
        'simulations': simulations,
        'risk_metrics': risk_metrics,
        'parameters': {
            'initial_value': data.iloc[-1],
            'drift': mean_return,
            'volatility': volatility,
            'time_horizon': time_horizon,
            'n_simulations': n_simulations
        }
    }

    # Save results if output directory provided
    if output_dir:
        series_name = data.name or 'simulation_series'
        simulator.save_simulation_results(results, output_dir, series_name)

    return results


if __name__ == "__main__":
    # Example usage
    print("Monte Carlo Economic Simulator")
    print("===============================")
    print("This module provides sophisticated Monte Carlo simulation")
    print("capabilities for economic uncertainty analysis and risk assessment.")
    print("")
    print("Key features:")
    print("- Geometric Brownian motion simulation")
    print("- Mean-reverting process simulation")
    print("- Jump-diffusion process simulation")
    print("- Correlated variable generation")
    print("- Bootstrap simulation methods")
    print("- Scenario analysis and stress testing")
    print("- Value at Risk and risk metrics calculation")
    print("")
    print("Import and use with your enhanced Lewis platform economic data!")
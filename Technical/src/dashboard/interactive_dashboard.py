#!/usr/bin/env python3
"""
Interactive Plotly/Dash dashboard for Lewis International Economics Platform.
Provides multi-country comparisons, interactive visualizations, and real-time analytics.
"""

import dash
from dash import dcc, html, Input, Output, State, callback_context, dash_table
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import sys
from pathlib import Path
import logging
from typing import Dict, List, Optional, Any, Tuple
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from data.enhanced_data_loader_v2 import EnhancedDataLoader
from analysis.forecasting_models import AdvancedEconomicForecaster
from analysis.monte_carlo_simulator import MonteCarloEconomicSimulator
from analysis.trade_flow_analyzer import AdvancedTradeFlowAnalyzer
from analysis.capital_flow_analyzer import AdvancedCapitalFlowAnalyzer

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LewisInteractiveDashboard:
    """
    Interactive dashboard for Lewis International Economics Platform.
    Provides comprehensive visualization and analysis capabilities.
    """

    def __init__(self, port: int = 8050, debug: bool = False):
        """Initialize the interactive dashboard."""
        self.port = port
        self.debug = debug

        # Initialize data components
        self.loader = EnhancedDataLoader()
        self.forecaster = AdvancedEconomicForecaster()
        self.simulator = MonteCarloEconomicSimulator()
        self.trade_analyzer = AdvancedTradeFlowAnalyzer()
        self.capital_analyzer = AdvancedCapitalFlowAnalyzer()

        # Initialize Dash app with Bootstrap theme
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.app.title = "Lewis International Economics Platform"

        # Setup layout and callbacks
        self._setup_layout()
        self._setup_callbacks()

        logger.info("Lewis Interactive Dashboard initialized")

    def _setup_layout(self):
        """Setup the dashboard layout."""
        self.app.layout = dbc.Container([
            # Header
            dbc.Row([
                dbc.Col([
                    html.H1("Lewis International Economics Platform",
                           className="text-center mb-4 text-primary"),
                    html.H4("Advanced Analytics & Interactive Visualization",
                           className="text-center mb-4 text-muted")
                ])
            ]),

            # Control Panel
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Control Panel", className="card-title"),

                            # Country Selection
                            html.Label("Select Countries:"),
                            dcc.Dropdown(
                                id='country-selector',
                                options=[
                                    {'label': 'United States', 'value': 'USA'},
                                    {'label': 'China', 'value': 'CHN'},
                                    {'label': 'Germany', 'value': 'DEU'},
                                    {'label': 'United Kingdom', 'value': 'GBR'},
                                    {'label': 'Japan', 'value': 'JPN'},
                                    {'label': 'Canada', 'value': 'CAN'},
                                    {'label': 'Mexico', 'value': 'MEX'},
                                    {'label': 'South Korea', 'value': 'KOR'},
                                    {'label': 'France', 'value': 'FRA'},
                                    {'label': 'Italy', 'value': 'ITA'}
                                ],
                                value=['USA', 'CHN', 'DEU', 'GBR'],
                                multi=True
                            ),

                            html.Br(),

                            # Analysis Type
                            html.Label("Analysis Type:"),
                            dcc.Dropdown(
                                id='analysis-type',
                                options=[
                                    {'label': 'Economic Forecasting', 'value': 'forecasting'},
                                    {'label': 'Trade Flow Analysis', 'value': 'trade'},
                                    {'label': 'Capital Flow Analysis', 'value': 'capital'},
                                    {'label': 'Monte Carlo Simulation', 'value': 'monte_carlo'},
                                    {'label': 'Comparative Analysis', 'value': 'comparative'}
                                ],
                                value='forecasting'
                            ),

                            html.Br(),

                            # Time Period
                            html.Label("Time Period:"),
                            dcc.Dropdown(
                                id='time-period',
                                options=[
                                    {'label': 'Last 2 Years', 'value': 2},
                                    {'label': 'Last 5 Years', 'value': 5},
                                    {'label': 'Last 10 Years', 'value': 10},
                                    {'label': 'All Available Data', 'value': 'all'}
                                ],
                                value=5
                            ),

                            html.Br(),

                            # Update Button
                            dbc.Button("Update Analysis", id="update-button",
                                     color="primary", className="w-100")
                        ])
                    ])
                ], width=3),

                # Main Content Area
                dbc.Col([
                    # Status Alert
                    dbc.Alert(id="status-alert", is_open=False, dismissable=True),

                    # Key Metrics Cards
                    dbc.Row(id="metrics-cards"),

                    html.Br(),

                    # Main Charts
                    dcc.Tabs(id="chart-tabs", value="overview-tab", children=[
                        dcc.Tab(label="Overview", value="overview-tab"),
                        dcc.Tab(label="Forecasting", value="forecasting-tab"),
                        dcc.Tab(label="Trade Analysis", value="trade-tab"),
                        dcc.Tab(label="Capital Flows", value="capital-tab"),
                        dcc.Tab(label="Risk Analysis", value="risk-tab"),
                        dcc.Tab(label="Network Analysis", value="network-tab")
                    ]),

                    html.Br(),

                    # Chart Container
                    dcc.Loading(
                        id="loading-spinner",
                        children=[html.Div(id="chart-container")],
                        type="default"
                    )
                ], width=9)
            ]),

            # Footer
            dbc.Row([
                dbc.Col([
                    html.Hr(),
                    html.P("Lewis International Economics Platform - Advanced Analytics Dashboard",
                          className="text-center text-muted small")
                ])
            ])

        ], fluid=True)

    def _setup_callbacks(self):
        """Setup dashboard callbacks."""

        @self.app.callback(
            [Output("status-alert", "is_open"),
             Output("status-alert", "children"),
             Output("status-alert", "color")],
            [Input("update-button", "n_clicks")],
            [State("country-selector", "value"),
             State("analysis-type", "value"),
             State("time-period", "value")]
        )
        def update_status(n_clicks, countries, analysis_type, time_period):
            """Update status alert based on user input."""
            if n_clicks:
                if not countries:
                    return True, "Please select at least one country", "warning"

                return (True,
                       f"Analysis updated for {len(countries)} countries - {analysis_type} analysis",
                       "success")

            return False, "", "primary"

        @self.app.callback(
            Output("metrics-cards", "children"),
            [Input("update-button", "n_clicks")],
            [State("country-selector", "value"),
             State("analysis-type", "value")]
        )
        def update_metrics_cards(n_clicks, countries, analysis_type):
            """Update key metrics cards."""
            if n_clicks and countries:
                # Generate sample metrics based on analysis type
                metrics_data = self._generate_metrics_data(countries, analysis_type)

                cards = []
                for i, (title, value, change) in enumerate(metrics_data[:4]):  # Show top 4 metrics
                    color = "success" if change > 0 else "danger" if change < 0 else "secondary"
                    icon = "^" if change > 0 else "v" if change < 0 else "->"

                    cards.append(
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H5(title, className="card-title text-muted small"),
                                    html.H3(f"{value:,.1f}", className="card-text"),
                                    html.Small(f"{icon} {abs(change):.1f}%", className=f"text-{color}")
                                ])
                            ], color="light")
                        ], width=3)
                    )

                return cards

            return []

        @self.app.callback(
            Output("chart-container", "children"),
            [Input("chart-tabs", "value"),
             Input("update-button", "n_clicks")],
            [State("country-selector", "value"),
             State("analysis-type", "value"),
             State("time-period", "value")]
        )
        def update_charts(active_tab, n_clicks, countries, analysis_type, time_period):
            """Update charts based on selected tab and analysis type."""
            if n_clicks and countries:
                try:
                    if active_tab == "overview-tab":
                        return self._create_overview_charts(countries, analysis_type)
                    elif active_tab == "forecasting-tab":
                        return self._create_forecasting_charts(countries)
                    elif active_tab == "trade-tab":
                        return self._create_trade_charts(countries)
                    elif active_tab == "capital-tab":
                        return self._create_capital_charts(countries)
                    elif active_tab == "risk-tab":
                        return self._create_risk_charts(countries)
                    elif active_tab == "network-tab":
                        return self._create_network_charts(countries)
                except Exception as e:
                    return [dbc.Alert(f"Error generating charts: {str(e)}", color="danger")]

            return [html.Div("Select countries and click 'Update Analysis' to begin")]

    def _generate_metrics_data(self, countries: List[str], analysis_type: str) -> List[Tuple[str, float, float]]:
        """Generate sample metrics data for visualization."""
        metrics = []

        if analysis_type == "forecasting":
            metrics = [
                ("Forecast Accuracy", 87.5, 2.3),
                ("Model Confidence", 92.1, 1.8),
                ("Prediction Interval", 45.2, -0.5),
                ("Trend Strength", 78.9, 3.2)
            ]
        elif analysis_type == "trade":
            metrics = [
                ("Trade Volume", 1250.5, 4.2),
                ("Trade Balance", -125.3, -2.1),
                ("Trade Intensity", 65.8, 1.9),
                ("Network Centrality", 0.72, 0.8)
            ]
        elif analysis_type == "capital":
            metrics = [
                ("IIP Position", 2500.2, 3.5),
                ("Capital Flows", 850.7, -1.2),
                ("Integration Index", 0.68, 2.1),
                ("Risk Score", 0.35, -0.9)
            ]
        else:  # comparative
            metrics = [
                ("Economic Growth", 3.2, 0.8),
                ("Inflation Rate", 2.1, -0.3),
                ("Employment", 95.8, 0.2),
                ("GDP per Capita", 45200, 2.7)
            ]

        return metrics

    def _create_overview_charts(self, countries: List[str], analysis_type: str) -> List:
        """Create overview charts for selected countries."""
        charts = []

        # Multi-country comparison chart
        comparison_chart = self._create_multi_country_comparison(countries, analysis_type)
        charts.append(comparison_chart)

        # Time series chart
        timeseries_chart = self._create_timeseries_chart(countries)
        charts.append(timeseries_chart)

        # Correlation heatmap
        correlation_chart = self._create_correlation_heatmap(countries)
        charts.append(correlation_chart)

        return charts

    def _create_forecasting_charts(self, countries: List[str]) -> List:
        """Create forecasting-specific charts."""
        charts = []

        # Forecast vs Actual
        forecast_chart = dcc.Graph(
            figure=self._create_forecast_figure(countries),
            style={'height': '400px'}
        )
        charts.append(forecast_chart)

        # Monte Carlo Simulation
        monte_carlo_chart = dcc.Graph(
            figure=self._create_monte_carlo_figure(countries),
            style={'height': '400px'}
        )
        charts.append(monte_carlo_chart)

        return charts

    def _create_trade_charts(self, countries: List[str]) -> List:
        """Create trade analysis charts."""
        charts = []

        # Trade Network
        trade_network_chart = dcc.Graph(
            figure=self._create_trade_network_figure(countries),
            style={'height': '500px'}
        )
        charts.append(trade_network_chart)

        # Trade Intensity
        trade_intensity_chart = dcc.Graph(
            figure=self._create_trade_intensity_figure(countries),
            style={'height': '400px'}
        )
        charts.append(trade_intensity_chart)

        return charts

    def _create_capital_charts(self, countries: List[str]) -> List:
        """Create capital flow analysis charts."""
        charts = []

        # IIP Position Chart
        iip_chart = dcc.Graph(
            figure=self._create_iip_figure(countries),
            style={'height': '400px'}
        )
        charts.append(iip_chart)

        # Financial Integration
        integration_chart = dcc.Graph(
            figure=self._create_integration_figure(countries),
            style={'height': '400px'}
        )
        charts.append(integration_chart)

        return charts

    def _create_risk_charts(self, countries: List[str]) -> List:
        """Create risk analysis charts."""
        charts = []

        # Risk Metrics
        risk_chart = dcc.Graph(
            figure=self._create_risk_figure(countries),
            style={'height': '400px'}
        )
        charts.append(risk_chart)

        # Volatility Analysis
        volatility_chart = dcc.Graph(
            figure=self._create_volatility_figure(countries),
            style={'height': '400px'}
        )
        charts.append(volatility_chart)

        return charts

    def _create_network_charts(self, countries: List[str]) -> List:
        """Create network analysis charts."""
        charts = []

        # Trade Network
        network_chart = dcc.Graph(
            figure=self._create_network_figure(countries),
            style={'height': '500px'}
        )
        charts.append(network_chart)

        # Centrality Analysis
        centrality_chart = dcc.Graph(
            figure=self._create_centrality_figure(countries),
            style={'height': '400px'}
        )
        charts.append(centrality_chart)

        return charts

    def _create_multi_country_comparison(self, countries: List[str], analysis_type: str) -> dbc.Card:
        """Create multi-country comparison chart."""
        # Generate sample data
        years = list(range(2018, 2025))

        fig = go.Figure()

        for country in countries:
            # Generate different trend for each country
            base_value = np.random.uniform(50, 150)
            trend = np.random.uniform(-2, 5)
            values = [base_value + trend * (year - 2018) + np.random.normal(0, 10) for year in years]

            fig.add_trace(go.Scatter(
                x=years,
                y=values,
                mode='lines+markers',
                name=country,
                line=dict(width=2)
            ))

        fig.update_layout(
            title=f"Multi-Country Comparison - {analysis_type.title()}",
            xaxis_title="Year",
            yaxis_title="Value",
            hovermode='x unified',
            showlegend=True,
            height=400
        )

        return dbc.Card([
            dbc.CardBody([
                dcc.Graph(figure=fig, style={'height': '400px'})
            ])
        ])

    def _create_timeseries_chart(self, countries: List[str]) -> dbc.Card:
        """Create time series chart."""
        # Generate sample time series data
        dates = pd.date_range('2018-01-01', '2024-12-31', freq='Q')

        fig = go.Figure()

        for country in countries:
            values = np.cumsum(np.random.normal(10, 15, len(dates)))
            fig.add_trace(go.Scatter(
                x=dates,
                y=values,
                mode='lines',
                name=country,
                line=dict(width=2)
            ))

        fig.update_layout(
            title="Time Series Analysis",
            xaxis_title="Date",
            yaxis_title="Cumulative Value",
            hovermode='x unified',
            height=350
        )

        return dbc.Card([
            dbc.CardBody([
                dcc.Graph(figure=fig, style={'height': '350px'})
            ])
        ])

    def _create_correlation_heatmap(self, countries: List[str]) -> dbc.Card:
        """Create correlation heatmap."""
        # Generate correlation matrix
        corr_matrix = pd.DataFrame(
            np.random.uniform(-0.3, 0.9, (len(countries), len(countries))),
            index=countries,
            columns=countries
        )

        # Make diagonal 1.0 and symmetric
        np.fill_diagonal(corr_matrix.values, 1.0)
        corr_matrix = (corr_matrix + corr_matrix.T) / 2

        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.index,
            colorscale='RdBu',
            zmid=0,
            text=np.round(corr_matrix.values, 2),
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False
        ))

        fig.update_layout(
            title="Cross-Country Correlation Matrix",
            height=350
        )

        return dbc.Card([
            dbc.CardBody([
                dcc.Graph(figure=fig, style={'height': '350px'})
            ])
        ])

    def _create_forecast_figure(self, countries: List[str]) -> go.Figure:
        """Create forecasting visualization."""
        years = list(range(2018, 2026))  # Include forecast years

        fig = go.Figure()

        for country in countries[:3]:  # Limit to 3 countries for clarity
            # Historical data
            hist_years = years[:7]
            hist_values = [100 + np.random.normal(0, 10) for _ in hist_years]

            # Forecast data
            forecast_years = years[6:]
            forecast_values = [hist_values[-1] + np.random.normal(5, 8) for _ in forecast_years]

            # Confidence intervals
            upper_bound = [v + 15 for v in forecast_values]
            lower_bound = [v - 15 for v in forecast_values]

            # Add historical data
            fig.add_trace(go.Scatter(
                x=hist_years,
                y=hist_values,
                mode='lines+markers',
                name=f'{country} - Historical',
                line=dict(width=2)
            ))

            # Add forecast
            fig.add_trace(go.Scatter(
                x=forecast_years,
                y=forecast_values,
                mode='lines+markers',
                name=f'{country} - Forecast',
                line=dict(width=2, dash='dash')
            ))

            # Add confidence interval
            fig.add_trace(go.Scatter(
                x=forecast_years + forecast_years[::-1],
                y=upper_bound + lower_bound[::-1],
                fill='toself',
                fillcolor=f'rgba({np.random.randint(0, 255)}, {np.random.randint(0, 255)}, {np.random.randint(0, 255)}, 0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                name=f'{country} - Confidence Interval',
                showlegend=False
            ))

        fig.update_layout(
            title="Economic Forecasting with Confidence Intervals",
            xaxis_title="Year",
            yaxis_title="Value",
            hovermode='x unified'
        )

        return fig

    def _create_monte_carlo_figure(self, countries: List[str]) -> go.Figure:
        """Create Monte Carlo simulation visualization."""
        # Generate Monte Carlo paths
        n_paths = 100
        n_steps = 50

        fig = go.Figure()

        for country in countries[:2]:  # Limit for clarity
            for i in range(min(20, n_paths)):  # Show subset of paths
                # Generate random walk
                path = np.cumsum(np.random.normal(0.5, 2, n_steps))

                fig.add_trace(go.Scatter(
                    x=list(range(n_steps)),
                    y=path,
                    mode='lines',
                    line=dict(width=0.5),
                    name=f'{country} Path {i+1}' if i < 3 else None,
                    showlegend=(i < 3),
                    opacity=0.3
                ))

        fig.update_layout(
            title="Monte Carlo Simulation - Possible Future Paths",
            xaxis_title="Time Steps",
            yaxis_title="Value",
            showlegend=True
        )

        return fig

    def _create_trade_network_figure(self, countries: List[str]) -> go.Figure:
        """Create trade network visualization."""
        # Create network layout
        np.random.seed(42)
        n_nodes = len(countries)

        # Generate positions (circular layout)
        angles = np.linspace(0, 2*np.pi, n_nodes, endpoint=False)
        x_pos = np.cos(angles)
        y_pos = np.sin(angles)

        fig = go.Figure()

        # Add edges (trade connections)
        for i in range(n_nodes):
            for j in range(i+1, n_nodes):
                # Edge weight based on random trade intensity
                weight = np.random.uniform(0.1, 1.0)

                fig.add_trace(go.Scatter(
                    x=[x_pos[i], x_pos[j]],
                    y=[y_pos[i], y_pos[j]],
                    mode='lines',
                    line=dict(width=weight*5, color='lightblue'),
                    showlegend=False,
                    hoverinfo='none'
                ))

        # Add nodes
        fig.add_trace(go.Scatter(
            x=x_pos,
            y=y_pos,
            mode='markers+text',
            marker=dict(size=20, color='darkblue'),
            text=countries,
            textposition='middle center',
            textfont=dict(color='white', size=10),
            showlegend=False,
            name='Countries'
        ))

        fig.update_layout(
            title="International Trade Network",
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            hovermode='closest'
        )

        return fig

    def _create_trade_intensity_figure(self, countries: List[str]) -> go.Figure:
        """Create trade intensity bar chart."""
        # Generate sample trade intensity data
        trade_intensity = {country: np.random.uniform(20, 80) for country in countries}

        fig = go.Figure(data=[
            go.Bar(
                x=list(trade_intensity.keys()),
                y=list(trade_intensity.values()),
                marker_color='lightgreen',
                text=[f'{v:.1f}%' for v in trade_intensity.values()],
                textposition='auto'
            )
        ])

        fig.update_layout(
            title="Trade Intensity Index (% of GDP)",
            xaxis_title="Country",
            yaxis_title="Trade Intensity (%)",
            showlegend=False
        )

        return fig

    def _create_iip_figure(self, countries: List[str]) -> go.Figure:
        """Create IIP position chart."""
        # Generate sample IIP data
        years = list(range(2018, 2025))

        fig = go.Figure()

        for country in countries:
            assets = [np.random.uniform(1000, 5000) for _ in years]
            liabilities = [np.random.uniform(800, 4500) for _ in years]

            fig.add_trace(go.Bar(
                x=years,
                y=assets,
                name=f'{country} - Assets',
                marker_color='blue'
            ))

            fig.add_trace(go.Bar(
                x=years,
                y=[-v for v in liabilities],
                name=f'{country} - Liabilities',
                marker_color='red'
            ))

        fig.update_layout(
            title="International Investment Position",
            xaxis_title="Year",
            yaxis_title="IIP Position (in billions)",
            barmode='relative',
            height=400
        )

        return fig

    def _create_integration_figure(self, countries: List[str]) -> go.Figure:
        """Create financial integration chart."""
        # Generate integration scores
        integration_scores = {country: np.random.uniform(0.3, 0.9) for country in countries}

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=list(integration_scores.keys()),
            y=list(integration_scores.values()),
            mode='markers',
            marker=dict(
                size=[v*50 for v in integration_scores.values()],
                color=list(integration_scores.values()),
                colorscale='Viridis',
                showscale=True,
                sizemode='diameter'
            ),
            text=[f'{country}: {score:.3f}' for country, score in integration_scores.items()],
            textposition='top center'
        ))

        fig.update_layout(
            title="Financial Integration Scores",
            xaxis_title="Country",
            yaxis_title="Integration Index",
            showlegend=False,
            height=400
        )

        return fig

    def _create_risk_figure(self, countries: List[str]) -> go.Figure:
        """Create risk analysis chart."""
        # Generate risk metrics
        risk_categories = ['Market Risk', 'Credit Risk', 'Liquidity Risk', 'Operational Risk']

        fig = go.Figure()

        for i, country in enumerate(countries[:4]):  # Limit for clarity
            risk_scores = [np.random.uniform(0.2, 0.8) for _ in risk_categories]

            fig.add_trace(go.Scatterpolar(
                r=risk_scores,
                theta=risk_categories,
                fill='toself',
                name=country
            ))

        fig.update_layout(
            title="Risk Assessment Radar Chart",
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            showlegend=True,
            height=400
        )

        return fig

    def _create_volatility_figure(self, countries: List[str]) -> go.Figure:
        """Create volatility analysis chart."""
        # Generate volatility data
        dates = pd.date_range('2023-01-01', '2024-12-31', freq='M')

        fig = go.Figure()

        for country in countries[:3]:  # Limit for clarity
            volatility = np.abs(np.random.normal(2, 1, len(dates)))

            fig.add_trace(go.Scatter(
                x=dates,
                y=volatility,
                mode='lines',
                name=country,
                line=dict(width=2)
            ))

        fig.update_layout(
            title="Capital Flow Volatility Analysis",
            xaxis_title="Date",
            yaxis_title="Volatility (%)",
            hovermode='x unified',
            height=400
        )

        return fig

    def _create_network_figure(self, countries: List[str]) -> go.Figure:
        """Create comprehensive network analysis figure."""
        # Similar to trade network but more detailed
        np.random.seed(123)
        n_nodes = len(countries)

        # Generate positions using spring layout approximation
        angles = np.linspace(0, 2*np.pi, n_nodes, endpoint=False)
        radius = 1 + np.random.uniform(-0.2, 0.2, n_nodes)
        x_pos = radius * np.cos(angles)
        y_pos = radius * np.sin(angles)

        fig = go.Figure()

        # Add edges with varying weights
        for i in range(n_nodes):
            for j in range(i+1, n_nodes):
                weight = np.random.uniform(0.2, 1.0)

                fig.add_trace(go.Scatter(
                    x=[x_pos[i], x_pos[j]],
                    y=[y_pos[i], y_pos[j]],
                    mode='lines',
                    line=dict(width=weight*8, color=f'rgba(100, 149, 237, {weight})'),
                    showlegend=False,
                    hoverinfo='none'
                ))

        # Add nodes with size based on centrality
        centrality = np.random.uniform(0.3, 1.0, n_nodes)

        fig.add_trace(go.Scatter(
            x=x_pos,
            y=y_pos,
            mode='markers+text',
            marker=dict(
                size=centrality*40,
                color=centrality,
                colorscale='Viridis',
                showscale=True,
                line=dict(width=2, color='white')
            ),
            text=countries,
            textposition='middle center',
            textfont=dict(color='white', size=12, weight='bold'),
            showlegend=False,
            name='Network Centrality'
        ))

        fig.update_layout(
            title="Economic Network Analysis - Node Size = Centrality",
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            hovermode='closest',
            height=500
        )

        return fig

    def _create_centrality_figure(self, countries: List[str]) -> go.Figure:
        """Create centrality analysis bar chart."""
        # Generate centrality metrics
        centrality_types = ['Degree', 'Betweenness', 'Closeness', 'Eigenvector']

        fig = go.Figure()

        for country in countries[:4]:  # Limit for clarity
            centrality_values = [np.random.uniform(0.2, 0.9) for _ in centrality_types]

            fig.add_trace(go.Bar(
                x=centrality_types,
                y=centrality_values,
                name=country,
                opacity=0.8
            ))

        fig.update_layout(
            title="Network Centrality Metrics by Country",
            xaxis_title="Centrality Type",
            yaxis_title="Centrality Score",
            barmode='group',
            height=400
        )

        return fig

    def run(self):
        """Run the dashboard server."""
        logger.info(f"Starting Lewis Interactive Dashboard on port {self.port}")
        self.app.run_server(debug=self.debug, port=self.port, host='0.0.0.0')

def main():
    """Main function to run the dashboard."""
    dashboard = LewisInteractiveDashboard(port=8050, debug=False)
    dashboard.run()

if __name__ == "__main__":
    main()
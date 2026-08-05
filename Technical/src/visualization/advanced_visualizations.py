#!/usr/bin/env python3
"""
Advanced visualization suite for Lewis International Economics Platform.
Provides sophisticated network graphs, interactive heatmaps, and animated visualizations.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import networkx as nx
from datetime import datetime, timedelta
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
import warnings
warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedVisualizationSuite:
    """
    Advanced visualization suite with network graphs, heatmaps, and animations.
    Provides sophisticated visual analytics for international economics data.
    """

    def __init__(self, output_dir: str = None):
        """Initialize the advanced visualization suite."""
        self.output_dir = output_dir or Path(__file__).parent.parent.parent.parent / "Output" / "Visualizations"
        self.output_dir = Path(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set default styles
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")

        logger.info(f"Advanced Visualization Suite initialized with output directory: {self.output_dir}")

    def create_interactive_network_graph(self,
                                       data: pd.DataFrame,
                                       node_col: str,
                                       edge_col: str,
                                       weight_col: str,
                                       title: str = "International Network Analysis") -> go.Figure:
        """
        Create interactive network graph with advanced features.

        Args:
            data: DataFrame with network data
            node_col: Column containing node identifiers
            edge_col: Column containing edge information
            weight_col: Column containing edge weights
            title: Graph title

        Returns:
            go.Figure: Interactive network graph
        """
        logger.info(f"Creating interactive network graph: {title}")

        try:
            # Create NetworkX graph
            G = nx.Graph()

            # Add nodes and edges
            for _, row in data.iterrows():
                if pd.notna(row[node_col]):
                    G.add_node(row[node_col])

            # Add edges with weights
            for _, row in data.iterrows():
                if pd.notna(row[edge_col]) and pd.notna(row[weight_col]):
                    source, target = str(row[node_col]), str(row[edge_col])
                    if source in G.nodes and target in G.nodes:
                        G.add_edge(source, target, weight=row[weight_col])

            # Calculate layout
            pos = nx.spring_layout(G, k=3, iterations=50, seed=42)

            # Extract edge information
            edge_x = []
            edge_y = []
            edge_info = []

            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
                weight = G[edge[0]][edge[1]].get('weight', 1.0)
                edge_info.append(f"{edge[0]} - {edge[1]}<br>Weight: {weight:.2f}")

            # Create edge trace
            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=1.5, color='#888'),
                hoverinfo='none',
                mode='lines'
            )

            # Extract node information
            node_x = []
            node_y = []
            node_text = []
            node_sizes = []

            # Calculate node centralities
            degree_centrality = nx.degree_centrality(G)
            betweenness_centrality = nx.betweenness_centrality(G)

            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                node_text.append(f"{node}<br>Degree: {G.degree(node)}<br>Betweenness: {betweenness_centrality[node]:.3f}")
                # Size based on degree centrality
                node_sizes.append(10 + degree_centrality[node] * 30)

            # Create node trace
            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                hoverinfo='text',
                text=list(G.nodes()),
                textposition="middle center",
                hovertext=node_text,
                marker=dict(
                    showscale=True,
                    colorscale='YlOrRd',
                    reversescale=True,
                    color=[degree_centrality[node] for node in G.nodes()],
                    size=node_sizes,
                    colorbar=dict(
                        thickness=15,
                        len=0.7,
                        x=1.02,
                        title="Degree Centrality"
                    ),
                    line=dict(width=2, color='white')
                ),
                textfont=dict(size=10, color='white')
            )

            # Create figure
            fig = go.Figure(data=[edge_trace, node_trace],
                           layout=go.Layout(
                               title=dict(text=title, font=dict(size=16)),
                               showlegend=False,
                               hovermode='closest',
                               margin=dict(b=20, l=5, r=5, t=40),
                               xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                               yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                               plot_bgcolor='white'
                           ))

            return fig

        except Exception as e:
            logger.error(f"Network graph creation failed: {e}")
            raise

    def create_advanced_heatmap(self,
                              data: pd.DataFrame,
                              index_col: str,
                              columns_col: str,
                              values_col: str,
                              title: str = "Correlation Heatmap",
                              annotation: bool = True) -> go.Figure:
        """
        Create advanced interactive heatmap with clustering and annotations.

        Args:
            data: DataFrame with heatmap data
            index_col: Column for index
            columns_col: Column for columns
            values_col: Column for values
            title: Heatmap title
            annotation: Whether to show annotations

        Returns:
            go.Figure: Interactive heatmap
        """
        logger.info(f"Creating advanced heatmap: {title}")

        try:
            # Pivot data for heatmap
            heatmap_data = data.pivot(index=index_col, columns=columns_col, values=values_col)

            # Handle missing values
            heatmap_data = heatmap_data.fillna(heatmap_data.mean())

            # Calculate clustering for better organization
            from scipy.cluster.hierarchy import linkage, dendrogram
            from scipy.spatial.distance import squareform

            # Perform hierarchical clustering
            if len(heatmap_data) > 1:
                # Row clustering
                row_linkage = linkage(1 - heatmap_data.fillna(0).corr(), method='average')
                row_order = dendrogram(row_linkage, no_plot=True)['leaves']
                heatmap_data = heatmap_data.iloc[row_order]

                # Column clustering
                col_linkage = linkage(1 - heatmap_data.T.fillna(0).corr(), method='average')
                col_order = dendrogram(col_linkage, no_plot=True)['leaves']
                heatmap_data = heatmap_data.iloc[:, col_order]

            # Create heatmap
            fig = go.Figure(data=go.Heatmap(
                z=heatmap_data.values,
                x=heatmap_data.columns,
                y=heatmap_data.index,
                colorscale='RdBu',
                zmid=heatmap_data.values.mean(),
                hoverongaps=False,
                colorbar=dict(
                    title="Value",
                    title_side="right"
                )
            ))

            # Add annotations if requested
            if annotation and heatmap_data.shape[0] <= 15 and heatmap_data.shape[1] <= 15:
                annotations = []
                for i, row in enumerate(heatmap_data.index):
                    for j, col in enumerate(heatmap_data.columns):
                        value = heatmap_data.iloc[i, j]
                        annotations.append(
                            go.layout.Annotation(
                                text=f"{value:.2f}",
                                x=j, y=i,
                                xref="x", yref="y",
                                font=dict(color="white" if abs(value) > heatmap_data.values.mean() else "black"),
                                showarrow=False
                            )
                        )
                fig.update_layout(annotations=annotations)

            # Update layout
            fig.update_layout(
                title=title,
                xaxis_title=columns_col,
                yaxis_title=index_col,
                width=max(800, len(heatmap_data.columns) * 50),
                height=max(600, len(heatmap_data.index) * 40)
            )

            return fig

        except Exception as e:
            logger.error(f"Heatmap creation failed: {e}")
            raise

    def create_animated_time_series(self,
                                  data: pd.DataFrame,
                                  time_col: str,
                                  value_cols: List[str],
                                  entity_col: str = None,
                                  title: str = "Animated Time Series") -> go.Figure:
        """
        Create animated time series visualization.

        Args:
            data: DataFrame with time series data
            time_col: Column containing time values
            value_cols: List of value columns to plot
            entity_col: Column containing entity identifiers (optional)
            title: Animation title

        Returns:
            go.Figure: Animated time series
        """
        logger.info(f"Creating animated time series: {title}")

        try:
            # Prepare data
            if entity_col:
                # Long format for multiple entities
                melted_data = pd.melt(
                    data,
                    id_vars=[time_col, entity_col],
                    value_vars=value_cols,
                    var_name='Metric',
                    value_name='Value'
                )
            else:
                # Single entity
                melted_data = pd.melt(
                    data,
                    id_vars=[time_col],
                    value_vars=value_cols,
                    var_name='Metric',
                    value_name='Value'
                )
                melted_data['Entity'] = 'Value'

            # Create figure with animation
            fig = px.line(
                melted_data,
                x=time_col,
                y='Value',
                color='Metric',
                line_group=entity_col if entity_col else 'Metric',
                animation_frame=time_col if len(data[time_col].unique()) > 1 else None,
                title=title,
                labels={'Value': 'Value', 'Metric': 'Metric', time_col: 'Time'}
            )

            # Update animation settings
            if len(data[time_col].unique()) > 1:
                fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 500
                fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 300

            # Update layout
            fig.update_layout(
                xaxis_title=time_col,
                yaxis_title='Value',
                hovermode='x unified',
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )

            return fig

        except Exception as e:
            logger.error(f"Animated time series creation failed: {e}")
            raise

    def create_radar_chart_comparison(self,
                                    data: pd.DataFrame,
                                    categories_col: str,
                                    values_col: str,
                                    entity_col: str,
                                    title: str = "Radar Chart Comparison") -> go.Figure:
        """
        Create radar chart for multi-dimensional comparison.

        Args:
            data: DataFrame with radar chart data
            categories_col: Column containing category names
            values_col: Column containing values
            entity_col: Column containing entity names
            title: Chart title

        Returns:
            go.Figure: Radar chart
        """
        logger.info(f"Creating radar chart: {title}")

        try:
            # Prepare data
            entities = data[entity_col].unique()
            categories = data[categories_col].unique()

            fig = go.Figure()

            # Add trace for each entity
            for entity in entities:
                entity_data = data[data[entity_col] == entity]
                values = []
                category_labels = []

                for category in categories:
                    cat_data = entity_data[entity_data[categories_col] == category]
                    if len(cat_data) > 0:
                        values.append(cat_data[values_col].iloc[0])
                    else:
                        values.append(0)
                    category_labels.append(category)

                # Close the radar chart
                values.append(values[0])
                category_labels.append(category_labels[0])

                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=category_labels,
                    fill='toself',
                    name=entity,
                    opacity=0.7
                ))

            # Update layout
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, max(data[values_col].max() * 1.1, 1)]
                    )
                ),
                title=title,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )

            return fig

        except Exception as e:
            logger.error(f"Radar chart creation failed: {e}")
            raise

    def create_sankey_diagram(self,
                            data: pd.DataFrame,
                            source_col: str,
                            target_col: str,
                            value_col: str,
                            title: str = "Flow Diagram") -> go.Figure:
        """
        Create Sankey diagram for flow visualization.

        Args:
            data: DataFrame with flow data
            source_col: Column containing source nodes
            target_col: Column containing target nodes
            value_col: Column containing flow values
            title: Diagram title

        Returns:
            go.Figure: Sankey diagram
        """
        logger.info(f"Creating Sankey diagram: {title}")

        try:
            # Get unique nodes
            all_nodes = list(set(data[source_col].unique()) | set(data[target_col].unique()))
            node_dict = {node: i for i, node in enumerate(all_nodes)}

            # Prepare link data
            sources = [node_dict[source] for source in data[source_col]]
            targets = [node_dict[target] for target in data[target_col]]
            values = data[value_col].tolist()

            # Create Sankey diagram
            fig = go.Figure(data=[go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=all_nodes,
                    color="lightblue"
                ),
                link=dict(
                    source=sources,
                    target=targets,
                    value=values,
                    hovertemplate='%{source.label} -> %{target.label}<br>Flow: %{value}<extra></extra>'
                )
            )])

            # Update layout
            fig.update_layout(
                title=title,
                font=dict(size=10, color='black'),
                height=600
            )

            return fig

        except Exception as e:
            logger.error(f"Sankey diagram creation failed: {e}")
            raise

    def create_3d_surface_plot(self,
                             data: pd.DataFrame,
                             x_col: str,
                             y_col: str,
                             z_col: str,
                             title: str = "3D Surface Plot") -> go.Figure:
        """
        Create 3D surface plot for multi-dimensional data visualization.

        Args:
            data: DataFrame with 3D data
            x_col: Column for x-axis
            y_col: Column for y-axis
            z_col: Column for z-axis values
            title: Plot title

        Returns:
            go.Figure: 3D surface plot
        """
        logger.info(f"Creating 3D surface plot: {title}")

        try:
            # Pivot data for surface plot
            pivot_data = data.pivot(index=y_col, columns=x_col, values=z_col)

            # Fill missing values
            pivot_data = pivot_data.fillna(method='ffill').fillna(method='bfill').fillna(0)

            # Create surface plot
            fig = go.Figure(data=[go.Surface(
                z=pivot_data.values,
                x=pivot_data.columns,
                y=pivot_data.index,
                colorscale='Viridis',
                colorbar=dict(title=z_col)
            )])

            # Update layout
            fig.update_layout(
                title=title,
                scene=dict(
                    xaxis_title=x_col,
                    yaxis_title=y_col,
                    zaxis_title=z_col,
                    camera=dict(
                        eye=dict(x=1.5, y=1.5, z=1.5)
                    )
                ),
                height=600
            )

            return fig

        except Exception as e:
            logger.error(f"3D surface plot creation failed: {e}")
            raise

    def create_treemap_visualization(self,
                                   data: pd.DataFrame,
                                   names_col: str,
                                   values_col: str,
                                   parents_col: str = None,
                                   title: str = "Treemap Visualization") -> go.Figure:
        """
        Create treemap for hierarchical data visualization.

        Args:
            data: DataFrame with hierarchical data
            names_col: Column containing names
            values_col: Column containing values
            parents_col: Column containing parent relationships (optional)
            title: Visualization title

        Returns:
            go.Figure: Treemap visualization
        """
        logger.info(f"Creating treemap: {title}")

        try:
            # Prepare data
            names = data[names_col].tolist()
            values = data[values_col].tolist()
            parents = data[parents_col].tolist() if parents_col else [''] * len(names)

            # Create treemap
            fig = go.Figure(go.Treemap(
                labels=names,
                values=values,
                parents=parents,
                textinfo="label+value+percent parent",
                hovertemplate='%{label}<br>Value: %{value}<br>Percentage: %{percentParent:.1%}<extra></extra>'
            ))

            # Update layout
            fig.update_layout(
                title=title,
                height=600
            )

            return fig

        except Exception as e:
            logger.error(f"Treemap creation failed: {e}")
            raise

    def create_choropleth_map(self,
                            data: pd.DataFrame,
                            locations_col: str,
                            values_col: str,
                            title: str = "Choropleth Map") -> go.Figure:
        """
        Create choropleth map for geographic data visualization.

        Args:
            data: DataFrame with geographic data
            locations_col: Column containing country codes
            values_col: Column containing values
            title: Map title

        Returns:
            go.Figure: Choropleth map
        """
        logger.info(f"Creating choropleth map: {title}")

        try:
            # Create choropleth map
            fig = go.Figure(data=go.Choropleth(
                locations=data[locations_col],
                z=data[values_col],
                text=data[locations_col],
                colorscale='Blues',
                autocolorscale=False,
                reversescale=False,
                marker_line_color='darkgray',
                marker_line_width=0.5,
                colorbar_tickprefix='$',
                colorbar_title=values_col,
                hovertemplate='%{location}<br>Value: %{z}<extra></extra>'
            ))

            # Update layout
            fig.update_layout(
                title_text=title,
                geo=dict(
                    showframe=False,
                    showcoastlines=False,
                    projection_type='equirectangular'
                ),
                height=600
            )

            return fig

        except Exception as e:
            logger.error(f"Choropleth map creation failed: {e}")
            raise

    def create_waterfall_chart(self,
                             data: pd.DataFrame,
                             categories_col: str,
                             values_col: str,
                             title: str = "Waterfall Chart") -> go.Figure:
        """
        Create waterfall chart for cumulative impact visualization.

        Args:
            data: DataFrame with waterfall data
            categories_col: Column containing categories
            values_col: Column containing values
            title: Chart title

        Returns:
            go.Figure: Waterfall chart
        """
        logger.info(f"Creating waterfall chart: {title}")

        try:
            # Calculate cumulative values
            data['cumulative'] = data[values_col].cumsum()

            # Create waterfall chart
            fig = go.Figure()

            # Add bars
            for i, row in data.iterrows():
                color = 'rgba(55, 128, 191, 0.7)' if row[values_col] >= 0 else 'rgba(219, 64, 82, 0.7)'

                fig.add_trace(go.Bar(
                    x=[row[categories_col]],
                    y=[row[values_col]],
                    base=[row['cumulative'] - row[values_col]] if i > 0 else [0],
                    marker_color=color,
                    text=[f"{row[values_col]:+.1f}"],
                    textposition='auto',
                    hovertemplate=f'{row[categories_col]}<br>Value: {row[values_col]:.1f}<br>Cumulative: {row["cumulative"]:.1f}<extra></extra>'
                ))

            # Add total line
            total_value = data[values_col].sum()
            fig.add_hline(y=total_value, line_dash="dash", line_color="black",
                         annotation_text=f"Total: {total_value:.1f}")

            # Update layout
            fig.update_layout(
                title=title,
                xaxis_title="Categories",
                yaxis_title="Value",
                showlegend=False,
                height=500
            )

            return fig

        except Exception as e:
            logger.error(f"Waterfall chart creation failed: {e}")
            raise

    def save_visualization(self,
                         fig: go.Figure,
                         filename: str,
                         formats: List[str] = ['html', 'png']) -> Dict[str, str]:
        """
        Save visualization in multiple formats.

        Args:
            fig: Plotly figure
            filename: Base filename
            formats: List of formats to save

        Returns:
            Dict[str, str]: Dictionary of file paths by format
        """
        saved_files = {}

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{filename}_{timestamp}"

        for format_type in formats:
            try:
                file_path = self.output_dir / f"{base_filename}.{format_type}"

                if format_type == 'html':
                    fig.write_html(str(file_path))
                elif format_type == 'png':
                    fig.write_image(str(file_path), width=1200, height=800)
                elif format_type == 'pdf':
                    fig.write_image(str(file_path), format='pdf', width=1200, height=800)
                elif format_type == 'svg':
                    fig.write_image(str(file_path), format='svg', width=1200, height=800)

                saved_files[format_type] = str(file_path)
                logger.info(f"Visualization saved as {format_type}: {file_path}")

            except Exception as e:
                logger.error(f"Failed to save {format_type}: {e}")

        return saved_files

    def create_dashboard_layout(self, figures: List[go.Figure], title: str = "Dashboard") -> go.Figure:
        """
        Create dashboard layout with multiple figures.

        Args:
            figures: List of Plotly figures
            title: Dashboard title

        Returns:
            go.Figure: Dashboard with subplots
        """
        logger.info(f"Creating dashboard: {title}")

        try:
            # Calculate grid layout
            n_figs = len(figures)
            cols = min(2, n_figs)
            rows = (n_figs + cols - 1) // cols

            # Create subplots
            specs = [[{"secondary_y": False} for _ in range(cols)] for _ in range(rows)]
            fig = make_subplots(
                rows=rows,
                cols=cols,
                subplot_titles=[f"Chart {i+1}" for i in range(n_figs)],
                specs=specs,
                vertical_spacing=0.15
            )

            # Add each figure to subplot
            for i, figure in enumerate(figures):
                row = (i // cols) + 1
                col = (i % cols) + 1

                # Extract traces from original figure
                for trace in figure.data:
                    fig.add_trace(trace, row=row, col=col)

            # Update layout
            fig.update_layout(
                title_text=title,
                height=300 * rows,
                showlegend=False,
                title_x=0.5
            )

            return fig

        except Exception as e:
            logger.error(f"Dashboard creation failed: {e}")
            raise

def main():
    """Main function for testing the advanced visualization suite."""
    # Create visualization suite
    viz = AdvancedVisualizationSuite()

    # Generate sample data
    print("Generating sample data for visualization testing...")

    # Network data
    network_data = pd.DataFrame({
        'source': ['USA', 'China', 'Germany', 'Japan', 'UK', 'USA', 'China', 'Germany'],
        'target': ['China', 'Germany', 'Japan', 'UK', 'USA', 'Germany', 'Japan', 'UK'],
        'weight': [100, 80, 60, 70, 90, 75, 85, 65]
    })

    # Heatmap data
    heatmap_data = pd.DataFrame({
        'country': ['USA', 'China', 'Germany', 'Japan', 'UK'],
        'metric': ['GDP', 'Trade', 'Inflation', 'Unemployment', 'Investment'],
        'value': np.random.uniform(0, 100, 25)
    })

    # Time series data
    dates = pd.date_range('2020-01-01', '2024-12-31', freq='Q')
    time_series_data = pd.DataFrame({
        'date': np.repeat(dates, 3),
        'country': np.tile(['USA', 'China', 'Germany'], len(dates)),
        'gdp_growth': np.random.normal(2.5, 1.5, len(dates) * 3),
        'trade_volume': np.random.normal(100, 20, len(dates) * 3),
        'inflation': np.random.normal(2.0, 0.8, len(dates) * 3)
    })

    # Test visualizations
    print("Testing advanced visualizations...")

    try:
        # Network graph
        network_fig = viz.create_interactive_network_graph(
            network_data, 'source', 'target', 'weight', "International Trade Network"
        )
        viz.save_visualization(network_fig, 'trade_network')
        print("[OK] Network graph created")

        # Heatmap
        heatmap_fig = viz.create_advanced_heatmap(
            heatmap_data, 'country', 'metric', 'value', "Economic Indicators Heatmap"
        )
        viz.save_visualization(heatmap_fig, 'economic_heatmap')
        print("[OK] Advanced heatmap created")

        # Animated time series
        animated_fig = viz.create_animated_time_series(
            time_series_data, 'date', ['gdp_growth', 'trade_volume', 'inflation'], 'country',
            "Economic Indicators Animation"
        )
        viz.save_visualization(animated_fig, 'animated_time_series', ['html'])
        print("[OK] Animated time series created")

        # Radar chart
        radar_data = pd.DataFrame({
            'country': ['USA'] * 5 + ['China'] * 5,
            'metric': ['GDP', 'Trade', 'Innovation', 'Education', 'Health'] * 2,
            'score': [85, 90, 95, 88, 92, 80, 85, 75, 82, 78]
        })
        radar_fig = viz.create_radar_chart_comparison(
            radar_data, 'metric', 'score', 'country', "Country Comparison Radar"
        )
        viz.save_visualization(radar_fig, 'radar_comparison')
        print("[OK] Radar chart created")

        # Sankey diagram
        sankey_fig = viz.create_sankey_diagram(
            network_data, 'source', 'target', 'weight', "Trade Flow Sankey"
        )
        viz.save_visualization(sankey_fig, 'trade_sankey')
        print("[OK] Sankey diagram created")

        # Dashboard
        dashboard_fig = viz.create_dashboard_layout(
            [network_fig, heatmap_fig, radar_fig, sankey_fig],
            "Lewis Platform Visualization Dashboard"
        )
        viz.save_visualization(dashboard_fig, 'visualization_dashboard')
        print("[OK] Dashboard created")

        print(f"\n*** ALL VISUALIZATIONS CREATED SUCCESSFULLY! ***")
        print(f"Output directory: {viz.output_dir}")
        print("Generated visualizations:")
        print("  • Interactive network graph")
        print("  • Advanced correlation heatmap")
        print("  • Animated time series")
        print("  • Radar chart comparison")
        print("  • Sankey flow diagram")
        print("  • Comprehensive dashboard")

    except Exception as e:
        print(f"Visualization testing failed: {e}")

if __name__ == "__main__":
    main()
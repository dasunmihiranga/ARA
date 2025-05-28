from typing import Dict, Any, List, Optional, Union
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
from pathlib import Path
import json
import base64
from io import BytesIO

from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class Visualization:
    """Handler for creating visualizations."""

    def __init__(self):
        """Initialize visualization handler."""
        self.default_colors = px.colors.qualitative.Set3
        self.default_layout = {
            "template": "plotly_white",
            "font": {"family": "Arial"},
            "margin": {"t": 50, "b": 50, "l": 50, "r": 50}
        }

    def create_chart(
        self,
        data: Dict[str, Any],
        chart_type: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Create a chart visualization.

        Args:
            data: Data to visualize
            chart_type: Type of chart to create
            options: Additional chart options

        Returns:
            Base64 encoded chart image or None if failed
        """
        try:
            if chart_type == "bar":
                fig = self._create_bar_chart(data, options)
            elif chart_type == "line":
                fig = self._create_line_chart(data, options)
            elif chart_type == "pie":
                fig = self._create_pie_chart(data, options)
            elif chart_type == "scatter":
                fig = self._create_scatter_chart(data, options)
            elif chart_type == "heatmap":
                fig = self._create_heatmap(data, options)
            else:
                logger.error(f"Unsupported chart type: {chart_type}")
                return None

            # Convert to base64
            img_bytes = fig.to_image(format="png")
            return base64.b64encode(img_bytes).decode()

        except Exception as e:
            logger.error(f"Error creating chart: {str(e)}")
            return None

    def create_graph(
        self,
        data: Dict[str, Any],
        graph_type: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Create a graph visualization.

        Args:
            data: Data to visualize
            graph_type: Type of graph to create
            options: Additional graph options

        Returns:
            Base64 encoded graph image or None if failed
        """
        try:
            if graph_type == "network":
                fig = self._create_network_graph(data, options)
            elif graph_type == "tree":
                fig = self._create_tree_graph(data, options)
            elif graph_type == "sankey":
                fig = self._create_sankey_diagram(data, options)
            else:
                logger.error(f"Unsupported graph type: {graph_type}")
                return None

            # Convert to base64
            img_bytes = fig.to_image(format="png")
            return base64.b64encode(img_bytes).decode()

        except Exception as e:
            logger.error(f"Error creating graph: {str(e)}")
            return None

    def _create_bar_chart(
        self,
        data: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> go.Figure:
        """
        Create a bar chart.

        Args:
            data: Data to visualize
            options: Additional chart options

        Returns:
            Plotly figure
        """
        try:
            x = data.get("x", [])
            y = data.get("y", [])
            labels = data.get("labels", {})
            colors = options.get("colors", self.default_colors)

            fig = go.Figure(data=[
                go.Bar(
                    x=x,
                    y=y,
                    text=y,
                    textposition="auto",
                    marker_color=colors
                )
            ])

            fig.update_layout(
                title=labels.get("title", "Bar Chart"),
                xaxis_title=labels.get("x", "X"),
                yaxis_title=labels.get("y", "Y"),
                **self.default_layout
            )

            return fig

        except Exception as e:
            logger.error(f"Error creating bar chart: {str(e)}")
            raise

    def _create_line_chart(
        self,
        data: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> go.Figure:
        """
        Create a line chart.

        Args:
            data: Data to visualize
            options: Additional chart options

        Returns:
            Plotly figure
        """
        try:
            x = data.get("x", [])
            y = data.get("y", [])
            labels = data.get("labels", {})
            colors = options.get("colors", self.default_colors)

            fig = go.Figure(data=[
                go.Scatter(
                    x=x,
                    y=y,
                    mode="lines+markers",
                    marker_color=colors[0]
                )
            ])

            fig.update_layout(
                title=labels.get("title", "Line Chart"),
                xaxis_title=labels.get("x", "X"),
                yaxis_title=labels.get("y", "Y"),
                **self.default_layout
            )

            return fig

        except Exception as e:
            logger.error(f"Error creating line chart: {str(e)}")
            raise

    def _create_pie_chart(
        self,
        data: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> go.Figure:
        """
        Create a pie chart.

        Args:
            data: Data to visualize
            options: Additional chart options

        Returns:
            Plotly figure
        """
        try:
            labels = data.get("labels", [])
            values = data.get("values", [])
            title = data.get("title", "Pie Chart")
            colors = options.get("colors", self.default_colors)

            fig = go.Figure(data=[
                go.Pie(
                    labels=labels,
                    values=values,
                    marker_colors=colors
                )
            ])

            fig.update_layout(
                title=title,
                **self.default_layout
            )

            return fig

        except Exception as e:
            logger.error(f"Error creating pie chart: {str(e)}")
            raise

    def _create_scatter_chart(
        self,
        data: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> go.Figure:
        """
        Create a scatter chart.

        Args:
            data: Data to visualize
            options: Additional chart options

        Returns:
            Plotly figure
        """
        try:
            x = data.get("x", [])
            y = data.get("y", [])
            labels = data.get("labels", {})
            colors = options.get("colors", self.default_colors)

            fig = go.Figure(data=[
                go.Scatter(
                    x=x,
                    y=y,
                    mode="markers",
                    marker_color=colors[0]
                )
            ])

            fig.update_layout(
                title=labels.get("title", "Scatter Chart"),
                xaxis_title=labels.get("x", "X"),
                yaxis_title=labels.get("y", "Y"),
                **self.default_layout
            )

            return fig

        except Exception as e:
            logger.error(f"Error creating scatter chart: {str(e)}")
            raise

    def _create_heatmap(
        self,
        data: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> go.Figure:
        """
        Create a heatmap.

        Args:
            data: Data to visualize
            options: Additional chart options

        Returns:
            Plotly figure
        """
        try:
            z = data.get("z", [])
            x = data.get("x", [])
            y = data.get("y", [])
            labels = data.get("labels", {})

            fig = go.Figure(data=[
                go.Heatmap(
                    z=z,
                    x=x,
                    y=y,
                    colorscale="Viridis"
                )
            ])

            fig.update_layout(
                title=labels.get("title", "Heatmap"),
                xaxis_title=labels.get("x", "X"),
                yaxis_title=labels.get("y", "Y"),
                **self.default_layout
            )

            return fig

        except Exception as e:
            logger.error(f"Error creating heatmap: {str(e)}")
            raise

    def _create_network_graph(
        self,
        data: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> go.Figure:
        """
        Create a network graph.

        Args:
            data: Data to visualize
            options: Additional graph options

        Returns:
            Plotly figure
        """
        try:
            # Create NetworkX graph
            G = nx.Graph()
            nodes = data.get("nodes", [])
            edges = data.get("edges", [])

            # Add nodes
            for node in nodes:
                G.add_node(
                    node["id"],
                    **node.get("attributes", {})
                )

            # Add edges
            for edge in edges:
                G.add_edge(
                    edge["source"],
                    edge["target"],
                    **edge.get("attributes", {})
                )

            # Get layout
            pos = nx.spring_layout(G)

            # Create edge trace
            edge_x = []
            edge_y = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])

            edge_trace = go.Scatter(
                x=edge_x,
                y=edge_y,
                line=dict(width=0.5, color="#888"),
                hoverinfo="none",
                mode="lines"
            )

            # Create node trace
            node_x = []
            node_y = []
            node_text = []
            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                node_text.append(str(node))

            node_trace = go.Scatter(
                x=node_x,
                y=node_y,
                mode="markers+text",
                hoverinfo="text",
                text=node_text,
                textposition="top center",
                marker=dict(
                    showscale=True,
                    colorscale="YlGnBu",
                    size=10
                )
            )

            # Create figure
            fig = go.Figure(
                data=[edge_trace, node_trace],
                layout=go.Layout(
                    title="Network Graph",
                    showlegend=False,
                    hovermode="closest",
                    margin=dict(b=20, l=5, r=5, t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                )
            )

            return fig

        except Exception as e:
            logger.error(f"Error creating network graph: {str(e)}")
            raise

    def _create_tree_graph(
        self,
        data: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> go.Figure:
        """
        Create a tree graph.

        Args:
            data: Data to visualize
            options: Additional graph options

        Returns:
            Plotly figure
        """
        try:
            # Create NetworkX graph
            G = nx.DiGraph()
            nodes = data.get("nodes", [])
            edges = data.get("edges", [])

            # Add nodes
            for node in nodes:
                G.add_node(
                    node["id"],
                    **node.get("attributes", {})
                )

            # Add edges
            for edge in edges:
                G.add_edge(
                    edge["source"],
                    edge["target"],
                    **edge.get("attributes", {})
                )

            # Get layout
            pos = nx.spring_layout(G)

            # Create edge trace
            edge_x = []
            edge_y = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])

            edge_trace = go.Scatter(
                x=edge_x,
                y=edge_y,
                line=dict(width=0.5, color="#888"),
                hoverinfo="none",
                mode="lines"
            )

            # Create node trace
            node_x = []
            node_y = []
            node_text = []
            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                node_text.append(str(node))

            node_trace = go.Scatter(
                x=node_x,
                y=node_y,
                mode="markers+text",
                hoverinfo="text",
                text=node_text,
                textposition="top center",
                marker=dict(
                    showscale=True,
                    colorscale="YlGnBu",
                    size=10
                )
            )

            # Create figure
            fig = go.Figure(
                data=[edge_trace, node_trace],
                layout=go.Layout(
                    title="Tree Graph",
                    showlegend=False,
                    hovermode="closest",
                    margin=dict(b=20, l=5, r=5, t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                )
            )

            return fig

        except Exception as e:
            logger.error(f"Error creating tree graph: {str(e)}")
            raise

    def _create_sankey_diagram(
        self,
        data: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> go.Figure:
        """
        Create a Sankey diagram.

        Args:
            data: Data to visualize
            options: Additional graph options

        Returns:
            Plotly figure
        """
        try:
            nodes = data.get("nodes", [])
            links = data.get("links", [])

            fig = go.Figure(data=[
                go.Sankey(
                    node=dict(
                        pad=15,
                        thickness=20,
                        line=dict(color="black", width=0.5),
                        label=nodes,
                        color="blue"
                    ),
                    link=dict(
                        source=links["source"],
                        target=links["target"],
                        value=links["value"]
                    )
                )
            ])

            fig.update_layout(
                title="Sankey Diagram",
                font_size=10,
                **self.default_layout
            )

            return fig

        except Exception as e:
            logger.error(f"Error creating Sankey diagram: {str(e)}")
            raise 
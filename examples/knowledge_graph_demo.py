"""
Knowledge graph demo for the AI Research Assistant MCP.
This example demonstrates knowledge graph generation, visualization, and querying.
"""

from research_assistant.search.search_aggregator import SearchAggregator
from research_assistant.analysis.insight_extractor import InsightExtractor
from research_assistant.storage.knowledge_graph import KnowledgeGraph
from research_assistant.reports.visualization import GraphVisualizer
from research_assistant.utils.logger import Logger

# Initialize logger
logger = Logger.get_logger(__name__)

def build_knowledge_graph_example(topic):
    """Example of building a knowledge graph."""
    try:
        # Initialize search aggregator
        searcher = SearchAggregator()
        
        # Search for topic information
        results = searcher.search(
            query=topic,
            max_results=50,
            sources=["academic", "news", "blogs"]
        )
        
        # Initialize insight extractor
        insight_extractor = InsightExtractor()
        
        # Extract entities and relationships
        insights = insight_extractor.extract(
            content="\n".join([r["snippet"] for r in results]),
            focus_areas=["entities", "relationships", "concepts"]
        )
        
        # Initialize knowledge graph
        knowledge_graph = KnowledgeGraph()
        
        # Build graph
        graph = knowledge_graph.build(
            entities=insights["entities"],
            relationships=insights["relationships"],
            metadata={
                "topic": topic,
                "sources": [r["source"] for r in results]
            }
        )
        
        logger.info(f"Built knowledge graph for topic: {topic}")
        return {
            "graph": graph,
            "insights": insights,
            "sources": results
        }
    except Exception as e:
        logger.error(f"Error in knowledge graph building: {str(e)}")
        raise

def visualize_graph_example(graph_data):
    """Example of graph visualization."""
    try:
        # Initialize graph visualizer
        visualizer = GraphVisualizer()
        
        # Generate visualization
        visualization = visualizer.visualize(
            graph=graph_data["graph"],
            layout="force-directed",
            node_size="importance",
            edge_weight="strength",
            include_labels=True
        )
        
        logger.info("Generated graph visualization")
        return visualization
    except Exception as e:
        logger.error(f"Error in graph visualization: {str(e)}")
        raise

def query_graph_example(graph, query):
    """Example of querying the knowledge graph."""
    try:
        # Initialize knowledge graph
        knowledge_graph = KnowledgeGraph()
        
        # Query graph
        results = knowledge_graph.query(
            graph=graph,
            query=query,
            max_results=10,
            include_paths=True
        )
        
        logger.info(f"Queried graph with: {query}")
        return results
    except Exception as e:
        logger.error(f"Error in graph querying: {str(e)}")
        raise

def analyze_graph_example(graph):
    """Example of graph analysis."""
    try:
        # Initialize knowledge graph
        knowledge_graph = KnowledgeGraph()
        
        # Analyze graph
        analysis = knowledge_graph.analyze(
            graph=graph,
            metrics=[
                "centrality",
                "clustering",
                "connectivity",
                "communities"
            ]
        )
        
        logger.info("Completed graph analysis")
        return analysis
    except Exception as e:
        logger.error(f"Error in graph analysis: {str(e)}")
        raise

def main():
    """Main function demonstrating knowledge graph workflow."""
    try:
        topic = "artificial intelligence"
        
        # 1. Build knowledge graph
        graph_data = build_knowledge_graph_example(topic)
        
        # 2. Visualize graph
        visualization = visualize_graph_example(graph_data)
        
        # 3. Query graph
        queries = [
            "What are the main applications of AI?",
            "Who are the key researchers in AI?",
            "What are the ethical concerns in AI?"
        ]
        
        query_results = []
        for query in queries:
            results = query_graph_example(graph_data["graph"], query)
            query_results.append({
                "query": query,
                "results": results
            })
        
        # 4. Analyze graph
        analysis = analyze_graph_example(graph_data["graph"])
        
        logger.info("Knowledge graph demo completed successfully")
        return {
            "graph_data": graph_data,
            "visualization": visualization,
            "query_results": query_results,
            "analysis": analysis
        }
    except Exception as e:
        logger.error(f"Error in main workflow: {str(e)}")
        raise

if __name__ == "__main__":
    main() 
from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime
import uuid
import networkx as nx
import json
from pathlib import Path
import os
import pickle

from research_assistant.storage.base_storage import BaseStorage, Document, QueryResult
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class KnowledgeGraph(BaseStorage):
    """Knowledge graph implementation using NetworkX."""

    def __init__(
        self,
        graph_dir: str = "data/knowledge_graphs",
        max_nodes: int = 10000,
        max_edges: int = 50000
    ):
        """
        Initialize the knowledge graph.

        Args:
            graph_dir: Directory to store graph files
            max_nodes: Maximum number of nodes
            max_edges: Maximum number of edges
        """
        super().__init__(
            name="knowledge_graph",
            description="Knowledge graph for storing and querying relationships"
        )
        self.graph_dir = Path(graph_dir)
        self.max_nodes = max_nodes
        self.max_edges = max_edges
        self.graph = nx.DiGraph()
        self._ensure_graph_dir()

    def _ensure_graph_dir(self) -> None:
        """Ensure graph directory exists."""
        try:
            self.graph_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Error creating graph directory: {str(e)}")
            raise

    def add_node(
        self,
        node_id: str,
        node_type: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a node to the graph.

        Args:
            node_id: Node identifier
            node_type: Type of node
            properties: Optional node properties
        """
        try:
            if len(self.graph.nodes) >= self.max_nodes:
                self._enforce_node_limit()

            self.graph.add_node(
                node_id,
                type=node_type,
                properties=properties or {},
                created_at=datetime.utcnow().isoformat()
            )

        except Exception as e:
            logger.error(f"Error adding node: {str(e)}")
            raise

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        edge_type: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add an edge to the graph.

        Args:
            source_id: Source node ID
            target_id: Target node ID
            edge_type: Type of edge
            properties: Optional edge properties
        """
        try:
            if len(self.graph.edges) >= self.max_edges:
                self._enforce_edge_limit()

            self.graph.add_edge(
                source_id,
                target_id,
                type=edge_type,
                properties=properties or {},
                created_at=datetime.utcnow().isoformat()
            )

        except Exception as e:
            logger.error(f"Error adding edge: {str(e)}")
            raise

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a node by ID.

        Args:
            node_id: Node ID

        Returns:
            Node data or None if not found
        """
        try:
            if node_id not in self.graph:
                return None

            node_data = self.graph.nodes[node_id]
            return {
                "id": node_id,
                "type": node_data["type"],
                "properties": node_data["properties"],
                "created_at": node_data["created_at"]
            }

        except Exception as e:
            logger.error(f"Error getting node: {str(e)}")
            return None

    def get_edge(
        self,
        source_id: str,
        target_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get an edge by source and target IDs.

        Args:
            source_id: Source node ID
            target_id: Target node ID

        Returns:
            Edge data or None if not found
        """
        try:
            if not self.graph.has_edge(source_id, target_id):
                return None

            edge_data = self.graph.edges[source_id, target_id]
            return {
                "source": source_id,
                "target": target_id,
                "type": edge_data["type"],
                "properties": edge_data["properties"],
                "created_at": edge_data["created_at"]
            }

        except Exception as e:
            logger.error(f"Error getting edge: {str(e)}")
            return None

    def get_neighbors(
        self,
        node_id: str,
        edge_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get neighboring nodes.

        Args:
            node_id: Node ID
            edge_type: Optional edge type filter

        Returns:
            List of neighboring nodes
        """
        try:
            if node_id not in self.graph:
                return []

            neighbors = []
            for neighbor in self.graph.neighbors(node_id):
                edge = self.graph.edges[node_id, neighbor]
                if edge_type and edge["type"] != edge_type:
                    continue

                neighbors.append({
                    "node": self.get_node(neighbor),
                    "edge": self.get_edge(node_id, neighbor)
                })

            return neighbors

        except Exception as e:
            logger.error(f"Error getting neighbors: {str(e)}")
            return []

    def find_path(
        self,
        source_id: str,
        target_id: str,
        max_depth: int = 3
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Find a path between nodes.

        Args:
            source_id: Source node ID
            target_id: Target node ID
            max_depth: Maximum path depth

        Returns:
            List of nodes and edges in path or None if not found
        """
        try:
            if source_id not in self.graph or target_id not in self.graph:
                return None

            path = nx.shortest_path(
                self.graph,
                source_id,
                target_id,
                cutoff=max_depth
            )

            if not path:
                return None

            # Convert path to list of nodes and edges
            result = []
            for i in range(len(path) - 1):
                result.append({
                    "node": self.get_node(path[i]),
                    "edge": self.get_edge(path[i], path[i + 1])
                })
            result.append({"node": self.get_node(path[-1])})

            return result

        except Exception as e:
            logger.error(f"Error finding path: {str(e)}")
            return None

    def query_nodes(
        self,
        node_type: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query nodes by type and properties.

        Args:
            node_type: Optional node type filter
            properties: Optional property filters

        Returns:
            List of matching nodes
        """
        try:
            matches = []
            for node_id, node_data in self.graph.nodes(data=True):
                if node_type and node_data["type"] != node_type:
                    continue

                if properties:
                    node_props = node_data["properties"]
                    if not all(
                        node_props.get(k) == v
                        for k, v in properties.items()
                    ):
                        continue

                matches.append(self.get_node(node_id))

            return matches

        except Exception as e:
            logger.error(f"Error querying nodes: {str(e)}")
            return []

    def query_edges(
        self,
        edge_type: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query edges by type and properties.

        Args:
            edge_type: Optional edge type filter
            properties: Optional property filters

        Returns:
            List of matching edges
        """
        try:
            matches = []
            for source, target, edge_data in self.graph.edges(data=True):
                if edge_type and edge_data["type"] != edge_type:
                    continue

                if properties:
                    edge_props = edge_data["properties"]
                    if not all(
                        edge_props.get(k) == v
                        for k, v in properties.items()
                    ):
                        continue

                matches.append(self.get_edge(source, target))

            return matches

        except Exception as e:
            logger.error(f"Error querying edges: {str(e)}")
            return []

    def _enforce_node_limit(self) -> None:
        """Enforce maximum node limit."""
        try:
            if len(self.graph.nodes) > self.max_nodes:
                # Remove oldest nodes
                nodes_by_age = sorted(
                    self.graph.nodes(data=True),
                    key=lambda x: x[1]["created_at"]
                )
                for node_id, _ in nodes_by_age[:len(nodes_by_age) - self.max_nodes]:
                    self.graph.remove_node(node_id)
        except Exception as e:
            logger.error(f"Error enforcing node limit: {str(e)}")

    def _enforce_edge_limit(self) -> None:
        """Enforce maximum edge limit."""
        try:
            if len(self.graph.edges) > self.max_edges:
                # Remove oldest edges
                edges_by_age = sorted(
                    self.graph.edges(data=True),
                    key=lambda x: x[2]["created_at"]
                )
                for source, target, _ in edges_by_age[:len(edges_by_age) - self.max_edges]:
                    self.graph.remove_edge(source, target)
        except Exception as e:
            logger.error(f"Error enforcing edge limit: {str(e)}")

    def save(self, filename: str) -> None:
        """
        Save graph to file.

        Args:
            filename: Output filename
        """
        try:
            filepath = self.graph_dir / filename
            with open(filepath, "wb") as f:
                pickle.dump(self.graph, f)
        except Exception as e:
            logger.error(f"Error saving graph: {str(e)}")
            raise

    def load(self, filename: str) -> None:
        """
        Load graph from file.

        Args:
            filename: Input filename
        """
        try:
            filepath = self.graph_dir / filename
            with open(filepath, "rb") as f:
                self.graph = pickle.load(f)
        except Exception as e:
            logger.error(f"Error loading graph: {str(e)}")
            raise

    def get_stats(self) -> Dict[str, Any]:
        """
        Get graph statistics.

        Returns:
            Dictionary with graph statistics
        """
        try:
            return {
                "num_nodes": len(self.graph.nodes),
                "num_edges": len(self.graph.edges),
                "node_types": len(set(n["type"] for _, n in self.graph.nodes(data=True))),
                "edge_types": len(set(e["type"] for _, _, e in self.graph.edges(data=True))),
                "max_nodes": self.max_nodes,
                "max_edges": self.max_edges
            }
        except Exception as e:
            logger.error(f"Error getting graph stats: {str(e)}")
            return {
                "num_nodes": 0,
                "num_edges": 0,
                "node_types": 0,
                "edge_types": 0,
                "max_nodes": self.max_nodes,
                "max_edges": self.max_edges
            }

    def clear(self) -> None:
        """Clear the graph."""
        try:
            self.graph.clear()
        except Exception as e:
            logger.error(f"Error clearing graph: {str(e)}")
            raise

    def _load_graph(self):
        """Load the graph from disk if it exists."""
        try:
            graph_file = self.graph_dir / "graph.pkl"
            if graph_file.exists():
                with open(graph_file, 'rb') as f:
                    self.graph = pickle.load(f)
        except Exception as e:
            logger.error(f"Error loading graph: {str(e)}")

    def _save_graph(self):
        """Save the graph to disk."""
        try:
            graph_file = self.graph_dir / "graph.pkl"
            with open(graph_file, 'wb') as f:
                pickle.dump(self.graph, f)
        except Exception as e:
            logger.error(f"Error saving graph: {str(e)}")

    async def store(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Document:
        """
        Store content in the knowledge graph.

        Args:
            content: Content to store
            metadata: Optional metadata

        Returns:
            Stored document
        """
        try:
            # Generate document ID
            doc_id = str(uuid.uuid4())
            
            # Prepare metadata
            doc_metadata = metadata or {}
            doc_metadata.update({
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            })
            
            # Add document node
            self.add_node(
                doc_id,
                "document",
                doc_metadata
            )
            
            # Extract and add entities
            entities = self._extract_entities(content)
            for entity in entities:
                entity_id = str(uuid.uuid4())
                self.add_node(
                    entity_id,
                    "entity",
                    {"name": entity, "extracted_at": datetime.utcnow().isoformat()}
                )
                self.add_edge(
                    doc_id,
                    entity_id,
                    "contains"
                )
            
            # Save graph
            self.save("graph.pkl")
            
            return Document(
                id=doc_id,
                content=content,
                metadata=doc_metadata,
                created_at=datetime.fromisoformat(doc_metadata["created_at"]),
                updated_at=datetime.fromisoformat(doc_metadata["updated_at"])
            )

        except Exception as e:
            logger.error(f"Error storing document: {str(e)}")
            raise

    async def retrieve(
        self,
        query: str,
        options: Optional[Dict[str, Any]] = None
    ) -> List[QueryResult]:
        """
        Retrieve content from the knowledge graph.

        Args:
            query: Query string
            options: Optional query options including:
                - limit: Maximum number of results
                - min_score: Minimum similarity score
                - search_type: Type of search (keyword, entity, relationship)

        Returns:
            List of query results
        """
        try:
            options = options or {}
            limit = options.get("limit", 5)
            min_score = options.get("min_score", 0.5)
            search_type = options.get("search_type", "keyword")
            
            results = []
            
            if search_type == "keyword":
                # Search by keyword in document content
                for node, data in self.graph.nodes(data=True):
                    if data.get("type") == "document":
                        score = self._calculate_similarity(query, data["content"])
                        if score >= min_score:
                            results.append(QueryResult(
                                document=Document(
                                    id=node,
                                    content=data["content"],
                                    metadata=data["properties"],
                                    created_at=datetime.fromisoformat(data["created_at"]),
                                    updated_at=datetime.fromisoformat(data["created_at"])
                                ),
                                score=score,
                                metadata={"search_type": search_type}
                            ))
            
            elif search_type == "entity":
                # Search by entity name
                for node, data in self.graph.nodes(data=True):
                    if data.get("type") == "entity":
                        score = self._calculate_similarity(query, data["name"])
                        if score >= min_score:
                            # Get connected documents
                            for doc_node in self.graph.predecessors(node):
                                doc_data = self.graph.nodes[doc_node]
                                results.append(QueryResult(
                                    document=Document(
                                        id=doc_node,
                                        content=doc_data["content"],
                                        metadata=doc_data["properties"],
                                        created_at=datetime.fromisoformat(doc_data["created_at"]),
                                        updated_at=datetime.fromisoformat(doc_data["created_at"])
                                    ),
                                    score=score,
                                    metadata={
                                        "search_type": search_type,
                                        "entity": data["name"]
                                    }
                                ))
            
            # Sort by score and limit results
            results.sort(key=lambda x: x.score, reverse=True)
            return results[:limit]

        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            raise

    async def delete(self, document_id: str) -> bool:
        """
        Delete a document from the knowledge graph.

        Args:
            document_id: ID of document to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            if document_id in self.graph:
                # Remove document and its edges
                self.graph.remove_node(document_id)
                self.save("graph.pkl")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            return False

    async def update(
        self,
        document_id: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Document]:
        """
        Update a document in the knowledge graph.

        Args:
            document_id: ID of document to update
            content: New content
            metadata: New metadata

        Returns:
            Updated document or None if not found
        """
        try:
            if document_id not in self.graph:
                return None
            
            node_data = self.graph.nodes[document_id]
            if node_data["type"] != "document":
                return None
            
            # Update content
            if content:
                node_data["content"] = content
                # Update entities
                self._update_entities(document_id, content)
            
            # Update metadata
            if metadata:
                node_data["properties"].update(metadata)
                node_data["created_at"] = datetime.utcnow().isoformat()
            
            self.save("graph.pkl")
            
            return Document(
                id=document_id,
                content=node_data["content"],
                metadata=node_data["properties"],
                created_at=datetime.fromisoformat(node_data["created_at"]),
                updated_at=datetime.fromisoformat(node_data["created_at"])
            )

        except Exception as e:
            logger.error(f"Error updating document: {str(e)}")
            return None

    async def list_documents(
        self,
        options: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        List documents in the knowledge graph.

        Args:
            options: Optional listing options including:
                - limit: Maximum number of documents
                - offset: Offset for pagination

        Returns:
            List of documents
        """
        try:
            options = options or {}
            limit = options.get("limit", 100)
            offset = options.get("offset", 0)
            
            # Get document nodes
            documents = []
            for node, data in self.graph.nodes(data=True):
                if data.get("type") == "document":
                    documents.append(Document(
                        id=node,
                        content=data["content"],
                        metadata=data["properties"],
                        created_at=datetime.fromisoformat(data["created_at"]),
                        updated_at=datetime.fromisoformat(data["created_at"])
                    ))
            
            # Sort by creation date
            documents.sort(key=lambda x: x.created_at, reverse=True)
            
            # Apply pagination
            return documents[offset:offset + limit]

        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            raise

    async def close(self):
        """Close the knowledge graph."""
        try:
            self.save("graph.pkl")
        except Exception as e:
            logger.error(f"Error closing knowledge graph: {str(e)}")

    def _extract_entities(self, content: str) -> Set[str]:
        """
        Extract entities from content.

        Args:
            content: Content to extract entities from

        Returns:
            Set of extracted entities
        """
        # Simple entity extraction (can be enhanced with NLP)
        words = content.split()
        return {word for word in words if len(word) > 3 and word[0].isupper()}

    def _update_entities(self, document_id: str, content: str):
        """
        Update entities for a document.

        Args:
            document_id: Document ID
            content: New content
        """
        # Remove old entity edges
        for node in list(self.graph.successors(document_id)):
            if self.graph.nodes[node]["type"] == "entity":
                self.graph.remove_edge(document_id, node)
        
        # Add new entities
        entities = self._extract_entities(content)
        for entity in entities:
            entity_id = str(uuid.uuid4())
            self.add_node(
                entity_id,
                "entity",
                {"name": entity, "extracted_at": datetime.utcnow().isoformat()}
            )
            self.add_edge(
                document_id,
                entity_id,
                "contains"
            )

    def _calculate_similarity(self, query: str, text: str) -> float:
        """
        Calculate similarity between query and text.

        Args:
            query: Query string
            text: Text to compare

        Returns:
            Similarity score between 0 and 1
        """
        # Simple word overlap similarity (can be enhanced with better metrics)
        query_words = set(query.lower().split())
        text_words = set(text.lower().split())
        
        if not query_words or not text_words:
            return 0.0
        
        intersection = query_words.intersection(text_words)
        union = query_words.union(text_words)
        
        return len(intersection) / len(union) 
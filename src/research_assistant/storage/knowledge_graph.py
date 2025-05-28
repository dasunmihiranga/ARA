from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime
import uuid
import networkx as nx
import json
from pathlib import Path

from research_assistant.storage.base_storage import BaseStorage, Document, QueryResult
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class KnowledgeGraph(BaseStorage):
    """Knowledge graph implementation using NetworkX."""

    def __init__(self, persist_directory: str = "./data/graph"):
        """
        Initialize the knowledge graph.

        Args:
            persist_directory: Directory to persist the graph
        """
        super().__init__(
            name="knowledge_graph",
            description="Knowledge graph for storing and querying relationships"
        )
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        self.graph = nx.DiGraph()
        self._load_graph()

    def _load_graph(self):
        """Load the graph from disk if it exists."""
        try:
            graph_file = self.persist_directory / "graph.json"
            if graph_file.exists():
                with open(graph_file, 'r') as f:
                    data = json.load(f)
                    self.graph = nx.node_link_graph(data)
        except Exception as e:
            logger.error(f"Error loading graph: {str(e)}")

    def _save_graph(self):
        """Save the graph to disk."""
        try:
            graph_file = self.persist_directory / "graph.json"
            data = nx.node_link_data(self.graph)
            with open(graph_file, 'w') as f:
                json.dump(data, f)
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
            self.graph.add_node(
                doc_id,
                type="document",
                content=content,
                metadata=doc_metadata
            )
            
            # Extract and add entities
            entities = self._extract_entities(content)
            for entity in entities:
                entity_id = str(uuid.uuid4())
                self.graph.add_node(
                    entity_id,
                    type="entity",
                    name=entity,
                    metadata={"extracted_at": datetime.utcnow().isoformat()}
                )
                self.graph.add_edge(
                    doc_id,
                    entity_id,
                    type="contains"
                )
            
            # Save graph
            self._save_graph()
            
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
                                    metadata=data["metadata"],
                                    created_at=datetime.fromisoformat(data["metadata"]["created_at"]),
                                    updated_at=datetime.fromisoformat(data["metadata"]["updated_at"])
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
                                        metadata=doc_data["metadata"],
                                        created_at=datetime.fromisoformat(doc_data["metadata"]["created_at"]),
                                        updated_at=datetime.fromisoformat(doc_data["metadata"]["updated_at"])
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
                self._save_graph()
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
                node_data["metadata"].update(metadata)
                node_data["metadata"]["updated_at"] = datetime.utcnow().isoformat()
            
            self._save_graph()
            
            return Document(
                id=document_id,
                content=node_data["content"],
                metadata=node_data["metadata"],
                created_at=datetime.fromisoformat(node_data["metadata"]["created_at"]),
                updated_at=datetime.fromisoformat(node_data["metadata"]["updated_at"])
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
                        metadata=data["metadata"],
                        created_at=datetime.fromisoformat(data["metadata"]["created_at"]),
                        updated_at=datetime.fromisoformat(data["metadata"]["updated_at"])
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
            self._save_graph()
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
            self.graph.add_node(
                entity_id,
                type="entity",
                name=entity,
                metadata={"extracted_at": datetime.utcnow().isoformat()}
            )
            self.graph.add_edge(
                document_id,
                entity_id,
                type="contains"
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
from typing import Dict, Any, List, Optional, Union
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import numpy as np
from datetime import datetime
import json
import os

from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class VectorStore:
    """ChromaDB integration for vector storage and retrieval."""

    def __init__(
        self,
        persist_directory: str = "data/vector_store",
        collection_name: str = "research_data",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize the vector store.

        Args:
            persist_directory: Directory to persist data
            collection_name: Name of the collection
            embedding_model: Name of the embedding model
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.client = None
        self.collection = None
        self._initialize()

    def _initialize(self) -> None:
        """Initialize ChromaDB client and collection."""
        try:
            # Create persist directory if it doesn't exist
            os.makedirs(self.persist_directory, exist_ok=True)

            # Initialize client
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )

            # Initialize embedding function
            embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=self.embedding_model
            )

            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=embedding_function,
                metadata={"description": "Research data vector store"}
            )

        except Exception as e:
            logger.error(f"Error initializing vector store: {str(e)}")
            raise

    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add documents to the vector store.

        Args:
            documents: List of documents to add
            metadatas: Optional list of metadata dictionaries
            ids: Optional list of document IDs

        Returns:
            List of added document IDs
        """
        try:
            if not documents:
                return []

            # Generate IDs if not provided
            if not ids:
                ids = [f"doc_{i}_{datetime.utcnow().timestamp()}" for i in range(len(documents))]

            # Add documents
            self.collection.add(
                documents=documents,
                metadatas=metadatas or [{}] * len(documents),
                ids=ids
            )

            return ids

        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise

    def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.

        Args:
            query: Search query
            n_results: Number of results to return
            where: Optional metadata filter
            where_document: Optional document content filter

        Returns:
            List of search results with metadata
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where,
                where_document=where_document
            )

            # Format results
            formatted_results = []
            for i in range(len(results["ids"][0])):
                formatted_results.append({
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else None
                })

            return formatted_results

        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            raise

    def update_document(
        self,
        id: str,
        document: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update a document in the vector store.

        Args:
            id: Document ID
            document: New document content
            metadata: New metadata
        """
        try:
            update_data = {}
            if document is not None:
                update_data["documents"] = [document]
            if metadata is not None:
                update_data["metadatas"] = [metadata]

            if update_data:
                self.collection.update(
                    ids=[id],
                    **update_data
                )

        except Exception as e:
            logger.error(f"Error updating document: {str(e)}")
            raise

    def delete_documents(self, ids: List[str]) -> None:
        """
        Delete documents from the vector store.

        Args:
            ids: List of document IDs to delete
        """
        try:
            self.collection.delete(ids=ids)
        except Exception as e:
            logger.error(f"Error deleting documents: {str(e)}")
            raise

    def get_document(self, id: str) -> Optional[Dict[str, Any]]:
        """
        Get a document by ID.

        Args:
            id: Document ID

        Returns:
            Document data with metadata
        """
        try:
            result = self.collection.get(ids=[id])
            if not result["ids"]:
                return None

            return {
                "id": result["ids"][0],
                "document": result["documents"][0],
                "metadata": result["metadatas"][0]
            }

        except Exception as e:
            logger.error(f"Error getting document: {str(e)}")
            raise

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get collection statistics.

        Returns:
            Dictionary with collection statistics
        """
        try:
            count = self.collection.count()
            return {
                "name": self.collection_name,
                "count": count,
                "embedding_model": self.embedding_model
            }

        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            raise

    def reset_collection(self) -> None:
        """Reset the collection."""
        try:
            self.collection.delete(where={})
        except Exception as e:
            logger.error(f"Error resetting collection: {str(e)}")
            raise

    def close(self) -> None:
        """Close the vector store."""
        try:
            if self.client:
                self.client.persist()
        except Exception as e:
            logger.error(f"Error closing vector store: {str(e)}")
            raise 
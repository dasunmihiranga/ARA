from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from research_assistant.storage.base_storage import BaseStorage, Document, QueryResult
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class VectorStore(BaseStorage):
    """Vector store implementation using ChromaDB."""

    def __init__(self, persist_directory: str = "./data/chroma"):
        """
        Initialize the vector store.

        Args:
            persist_directory: Directory to persist the database
        """
        super().__init__(
            name="vector_store",
            description="Vector store for semantic search using ChromaDB"
        )
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    async def store(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Document:
        """
        Store content in the vector store.

        Args:
            content: Content to store
            metadata: Optional metadata

        Returns:
            Stored document
        """
        try:
            # Generate document ID
            doc_id = str(uuid.uuid4())
            
            # Generate embedding
            embedding = self.embedding_model.encode(content).tolist()
            
            # Prepare metadata
            doc_metadata = metadata or {}
            doc_metadata.update({
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            })
            
            # Store in ChromaDB
            self.collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[content],
                metadatas=[doc_metadata]
            )
            
            return Document(
                id=doc_id,
                content=content,
                metadata=doc_metadata,
                embedding=embedding,
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
        Retrieve content from the vector store.

        Args:
            query: Query string
            options: Optional query options including:
                - limit: Maximum number of results
                - min_score: Minimum similarity score

        Returns:
            List of query results
        """
        try:
            options = options or {}
            limit = options.get("limit", 5)
            min_score = options.get("min_score", 0.5)
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Query ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit
            )
            
            # Process results
            query_results = []
            for i, (doc_id, content, metadata, distance) in enumerate(zip(
                results["ids"][0],
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )):
                # Convert distance to similarity score
                score = 1 - distance
                
                if score >= min_score:
                    query_results.append(QueryResult(
                        document=Document(
                            id=doc_id,
                            content=content,
                            metadata=metadata,
                            created_at=datetime.fromisoformat(metadata["created_at"]),
                            updated_at=datetime.fromisoformat(metadata["updated_at"])
                        ),
                        score=score,
                        metadata={"rank": i + 1}
                    ))
            
            return query_results

        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            raise

    async def delete(self, document_id: str) -> bool:
        """
        Delete a document from the vector store.

        Args:
            document_id: ID of document to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            self.collection.delete(ids=[document_id])
            return True
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
        Update a document in the vector store.

        Args:
            document_id: ID of document to update
            content: New content
            metadata: New metadata

        Returns:
            Updated document or None if not found
        """
        try:
            # Get existing document
            results = self.collection.get(ids=[document_id])
            if not results["ids"]:
                return None
            
            # Update content and metadata
            if content:
                embedding = self.embedding_model.encode(content).tolist()
                self.collection.update(
                    ids=[document_id],
                    embeddings=[embedding],
                    documents=[content]
                )
            
            if metadata:
                metadata["updated_at"] = datetime.utcnow().isoformat()
                self.collection.update(
                    ids=[document_id],
                    metadatas=[metadata]
                )
            
            # Get updated document
            results = self.collection.get(ids=[document_id])
            return Document(
                id=document_id,
                content=results["documents"][0],
                metadata=results["metadatas"][0],
                created_at=datetime.fromisoformat(results["metadatas"][0]["created_at"]),
                updated_at=datetime.fromisoformat(results["metadatas"][0]["updated_at"])
            )

        except Exception as e:
            logger.error(f"Error updating document: {str(e)}")
            return None

    async def list_documents(
        self,
        options: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        List documents in the vector store.

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
            
            # Get documents from ChromaDB
            results = self.collection.get(
                limit=limit,
                offset=offset
            )
            
            # Convert to Document objects
            documents = []
            for doc_id, content, metadata in zip(
                results["ids"],
                results["documents"],
                results["metadatas"]
            ):
                documents.append(Document(
                    id=doc_id,
                    content=content,
                    metadata=metadata,
                    created_at=datetime.fromisoformat(metadata["created_at"]),
                    updated_at=datetime.fromisoformat(metadata["updated_at"])
                ))
            
            return documents

        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            raise

    async def close(self):
        """Close the vector store."""
        try:
            self.client.persist()
        except Exception as e:
            logger.error(f"Error closing vector store: {str(e)}") 
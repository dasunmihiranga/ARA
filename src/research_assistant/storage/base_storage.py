from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

@dataclass
class Document:
    """Class representing a document in storage."""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class QueryResult:
    """Class representing a query result."""
    document: Document
    score: float
    metadata: Dict[str, Any]

class BaseStorage(ABC):
    """Base class for storage implementations."""

    def __init__(self, name: str, description: str):
        """
        Initialize the base storage.

        Args:
            name: Name of the storage
            description: Description of the storage
        """
        self.name = name
        self.description = description
        self.logger = get_logger(f"storage.{name}")

    @abstractmethod
    async def store(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Document:
        """
        Store content in the storage.

        Args:
            content: Content to store
            metadata: Optional metadata

        Returns:
            Stored document
        """
        pass

    @abstractmethod
    async def retrieve(
        self,
        query: str,
        options: Optional[Dict[str, Any]] = None
    ) -> List[QueryResult]:
        """
        Retrieve content from storage.

        Args:
            query: Query string
            options: Optional query options

        Returns:
            List of query results
        """
        pass

    @abstractmethod
    async def delete(self, document_id: str) -> bool:
        """
        Delete a document from storage.

        Args:
            document_id: ID of document to delete

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def update(
        self,
        document_id: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Document]:
        """
        Update a document in storage.

        Args:
            document_id: ID of document to update
            content: New content
            metadata: New metadata

        Returns:
            Updated document or None if not found
        """
        pass

    @abstractmethod
    async def list_documents(
        self,
        options: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        List documents in storage.

        Args:
            options: Optional listing options

        Returns:
            List of documents
        """
        pass

    @abstractmethod
    async def close(self):
        """Close the storage and release resources."""
        pass 
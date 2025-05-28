from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from research_assistant.core.tool_registry import MCPTool
from research_assistant.storage.storage_factory import StorageFactory
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class StorageToolInput(BaseModel):
    """Input model for the storage tool."""
    operation: str = Field(
        ...,
        description="Operation to perform (store, retrieve, delete, update, list)"
    )
    storage_type: str = Field(
        default="vector_store",
        description="Type of storage to use (vector_store, knowledge_graph)"
    )
    content: Optional[str] = Field(
        default=None,
        description="Content to store or update"
    )
    query: Optional[str] = Field(
        default=None,
        description="Query string for retrieval"
    )
    document_id: Optional[str] = Field(
        default=None,
        description="Document ID for delete or update operations"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional metadata"
    )
    options: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional operation-specific options"
    )

class StorageTool(MCPTool):
    """Tool for storing and retrieving content using various storage backends."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the storage tool.

        Args:
            config_path: Path to the storage configuration file
        """
        super().__init__(
            name="storage",
            description="Store and retrieve content using various storage backends",
            version="1.0.0"
        )
        self.storage_factory = StorageFactory(config_path)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the storage tool.

        Args:
            input_data: Input data containing storage parameters

        Returns:
            Dictionary containing operation results
        """
        try:
            # Parse and validate input
            storage_input = StorageToolInput(**input_data)
            
            # Get storage instance
            storage = self.storage_factory.get_storage(storage_input.storage_type)
            if not storage:
                raise ValueError(f"Failed to create storage of type {storage_input.storage_type}")

            # Execute operation
            if storage_input.operation == "store":
                if not storage_input.content:
                    raise ValueError("Content is required for store operation")
                result = await storage.store(
                    content=storage_input.content,
                    metadata=storage_input.metadata
                )
                return {
                    "status": "success",
                    "operation": "store",
                    "document": {
                        "id": result.id,
                        "content": result.content,
                        "metadata": result.metadata,
                        "created_at": result.created_at.isoformat(),
                        "updated_at": result.updated_at.isoformat()
                    }
                }

            elif storage_input.operation == "retrieve":
                if not storage_input.query:
                    raise ValueError("Query is required for retrieve operation")
                results = await storage.retrieve(
                    query=storage_input.query,
                    options=storage_input.options
                )
                return {
                    "status": "success",
                    "operation": "retrieve",
                    "results": [
                        {
                            "document": {
                                "id": r.document.id,
                                "content": r.document.content,
                                "metadata": r.document.metadata,
                                "created_at": r.document.created_at.isoformat(),
                                "updated_at": r.document.updated_at.isoformat()
                            },
                            "score": r.score,
                            "metadata": r.metadata
                        }
                        for r in results
                    ]
                }

            elif storage_input.operation == "delete":
                if not storage_input.document_id:
                    raise ValueError("Document ID is required for delete operation")
                success = await storage.delete(storage_input.document_id)
                return {
                    "status": "success" if success else "error",
                    "operation": "delete",
                    "document_id": storage_input.document_id
                }

            elif storage_input.operation == "update":
                if not storage_input.document_id:
                    raise ValueError("Document ID is required for update operation")
                result = await storage.update(
                    document_id=storage_input.document_id,
                    content=storage_input.content,
                    metadata=storage_input.metadata
                )
                if result:
                    return {
                        "status": "success",
                        "operation": "update",
                        "document": {
                            "id": result.id,
                            "content": result.content,
                            "metadata": result.metadata,
                            "created_at": result.created_at.isoformat(),
                            "updated_at": result.updated_at.isoformat()
                        }
                    }
                return {
                    "status": "error",
                    "operation": "update",
                    "error": "Document not found"
                }

            elif storage_input.operation == "list":
                documents = await storage.list_documents(options=storage_input.options)
                return {
                    "status": "success",
                    "operation": "list",
                    "documents": [
                        {
                            "id": doc.id,
                            "content": doc.content,
                            "metadata": doc.metadata,
                            "created_at": doc.created_at.isoformat(),
                            "updated_at": doc.updated_at.isoformat()
                        }
                        for doc in documents
                    ]
                }

            else:
                raise ValueError(f"Unknown operation: {storage_input.operation}")

        except Exception as e:
            logger.error(f"Storage tool error: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def close(self):
        """Close the storage tool and its resources."""
        await self.storage_factory.close_all() 
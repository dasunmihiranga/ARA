from typing import Dict, Type, Optional
import yaml
from pathlib import Path

from research_assistant.storage.base_storage import BaseStorage
from research_assistant.storage.vector_store import VectorStore
from research_assistant.storage.knowledge_graph import KnowledgeGraph
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class StorageFactory:
    """Factory class for creating and managing storage implementations."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the storage factory.

        Args:
            config_path: Path to the storage configuration file
        """
        self.storages: Dict[str, BaseStorage] = {}
        self.config = self._load_config(config_path) if config_path else {}

    def _load_config(self, config_path: str) -> dict:
        """
        Load storage configuration from YAML file.

        Args:
            config_path: Path to the configuration file

        Returns:
            Dictionary containing storage configurations
        """
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading storage config: {str(e)}")
            return {}

    def create_storage(self, storage_type: str) -> Optional[BaseStorage]:
        """
        Create a new storage instance.

        Args:
            storage_type: Type of storage to create

        Returns:
            Storage instance or None if creation fails
        """
        try:
            if storage_type in self.storages:
                return self.storages[storage_type]

            storage = None
            config = self.config.get(storage_type, {})

            if storage_type == "vector_store":
                persist_dir = config.get("persist_directory", "./data/chroma")
                storage = VectorStore(persist_directory=persist_dir)
            elif storage_type == "knowledge_graph":
                persist_dir = config.get("persist_directory", "./data/graph")
                storage = KnowledgeGraph(persist_directory=persist_dir)
            else:
                logger.error(f"Unknown storage type: {storage_type}")
                return None

            if storage:
                self.storages[storage_type] = storage
                return storage

        except Exception as e:
            logger.error(f"Error creating storage {storage_type}: {str(e)}")
            return None

    def get_storage(self, storage_type: str) -> Optional[BaseStorage]:
        """
        Get an existing storage instance or create a new one.

        Args:
            storage_type: Type of storage to get

        Returns:
            Storage instance or None if not found/created
        """
        return self.storages.get(storage_type) or self.create_storage(storage_type)

    def list_available_storages(self) -> list:
        """
        List all available storage types.

        Returns:
            List of storage type names
        """
        return list(self.storages.keys())

    async def close_all(self):
        """Close all storage instances."""
        for storage in self.storages.values():
            try:
                await storage.close()
            except Exception as e:
                logger.error(f"Error closing storage: {str(e)}")
        self.storages.clear() 
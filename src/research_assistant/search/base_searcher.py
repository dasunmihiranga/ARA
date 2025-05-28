from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class SearchResult(BaseModel):
    """Model for search results."""
    title: str
    url: str
    snippet: str
    source: str
    metadata: Dict[str, Any] = {}

class BaseSearcher(ABC):
    """Abstract base class for search implementations."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the searcher.

        Args:
            config: Configuration dictionary for the searcher
        """
        self.config = config
        self.name = self.__class__.__name__
        self.enabled = config.get("enabled", True)
        self.max_results = config.get("max_results", 10)
        self.timeout = config.get("timeout", 30)

    @abstractmethod
    async def search(
        self,
        query: str,
        max_results: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Perform a search.

        Args:
            query: Search query string
            max_results: Maximum number of results to return
            filters: Additional search filters

        Returns:
            List of search results

        Raises:
            NotImplementedError: If the search method is not implemented
        """
        raise NotImplementedError("Search method must be implemented")

    @abstractmethod
    async def validate_connection(self) -> bool:
        """
        Validate the connection to the search service.

        Returns:
            True if connection is valid, False otherwise

        Raises:
            NotImplementedError: If the validation method is not implemented
        """
        raise NotImplementedError("Connection validation must be implemented")

    def get_config(self) -> Dict[str, Any]:
        """
        Get the searcher configuration.

        Returns:
            Configuration dictionary
        """
        return self.config

    def is_enabled(self) -> bool:
        """
        Check if the searcher is enabled.

        Returns:
            True if enabled, False otherwise
        """
        return self.enabled

    def get_name(self) -> str:
        """
        Get the searcher name.

        Returns:
            Searcher name
        """
        return self.name 
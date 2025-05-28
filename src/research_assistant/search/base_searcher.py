from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

@dataclass
class SearchResult:
    """Class representing a search result."""
    title: str
    url: str
    snippet: str
    source: str
    metadata: Dict[str, Any]

class BaseSearcher(ABC):
    """Base class for search implementations."""

    def __init__(self, name: str, description: str):
        """
        Initialize the base searcher.

        Args:
            name: Name of the searcher
            description: Description of the searcher
        """
        self.name = name
        self.description = description
        self.logger = get_logger(f"search.{name}")

    @abstractmethod
    async def search(
        self,
        query: str,
        max_results: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Perform a search.

        Args:
            query: Search query string
            max_results: Maximum number of results to return
            filters: Optional search filters

        Returns:
            List of search results
        """
        pass

    @abstractmethod
    async def validate_query(self, query: str) -> bool:
        """
        Validate a search query.

        Args:
            query: Query to validate

        Returns:
            True if query is valid, False otherwise
        """
        pass

    @abstractmethod
    async def close(self):
        """Close any resources used by the searcher."""
        pass

    def format_result(self, result: SearchResult) -> Dict[str, Any]:
        """
        Format a search result for API response.

        Args:
            result: Search result to format

        Returns:
            Formatted result dictionary
        """
        return {
            "title": result.title,
            "url": result.url,
            "snippet": result.snippet,
            "source": result.source,
            "metadata": result.metadata
        }

    async def execute(
        self,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute the search tool.

        Args:
            parameters: Search parameters
            context: Optional execution context

        Returns:
            Search results and metadata
        """
        query = parameters.get("query")
        if not query:
            raise ValueError("Search query is required")

        max_results = parameters.get("max_results", 10)
        filters = parameters.get("filters")

        # Validate query
        if not await self.validate_query(query):
            raise ValueError(f"Invalid search query: {query}")

        # Perform search
        results = await self.search(query, max_results, filters)

        # Format results
        formatted_results = [self.format_result(r) for r in results]

        return {
            "results": formatted_results,
            "total": len(results),
            "source": self.name
        } 
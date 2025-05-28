from typing import Dict, Any, List, Optional, Protocol
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field

from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class SearchResult(BaseModel):
    """Model for search results."""
    title: str = Field(..., description="Title of the result")
    url: str = Field(..., description="URL of the result")
    snippet: str = Field(..., description="Text snippet from the result")
    source: str = Field(..., description="Source of the result")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class SearchOptions(BaseModel):
    """Model for search options."""
    max_results: int = Field(default=10, description="Maximum number of results to return")
    timeout: int = Field(default=30, description="Timeout in seconds")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Search filters")
    sort_by: Optional[str] = Field(default=None, description="Sort field")
    sort_order: str = Field(default="desc", description="Sort order (asc/desc)")

class BaseSearcher(ABC):
    """Base class for all search implementations."""

    def __init__(self, name: str, description: str):
        """
        Initialize the searcher.

        Args:
            name: Name of the searcher
            description: Description of the searcher
        """
        self.name = name
        self.description = description
        self.logger = get_logger(f"searcher.{name}")

    @abstractmethod
    async def search(
        self,
        query: str,
        options: Optional[SearchOptions] = None
    ) -> List[SearchResult]:
        """
        Perform a search.

        Args:
            query: Search query
            options: Optional search options

        Returns:
            List of search results

        Raises:
            ValueError: If query is invalid
            Exception: For other search errors
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the searcher and clean up resources."""
        pass

    def validate_query(self, query: str) -> bool:
        """
        Validate a search query.

        Args:
            query: Query to validate

        Returns:
            True if query is valid, False otherwise
        """
        if not query or not isinstance(query, str):
            return False
        return len(query.strip()) > 0

    def format_result(self, result: Dict[str, Any]) -> SearchResult:
        """
        Format a raw result into a SearchResult.

        Args:
            result: Raw result data

        Returns:
            Formatted SearchResult
        """
        try:
            return SearchResult(
                title=result.get("title", ""),
                url=result.get("url", ""),
                snippet=result.get("snippet", ""),
                source=self.name,
                metadata=result.get("metadata", {})
            )
        except Exception as e:
            self.logger.error(f"Error formatting result: {str(e)}")
            raise

    def __str__(self) -> str:
        """String representation of the searcher."""
        return f"{self.name}: {self.description}"

    def __repr__(self) -> str:
        """Detailed string representation of the searcher."""
        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"description='{self.description}'"
            ")"
        )

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
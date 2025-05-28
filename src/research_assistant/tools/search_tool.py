from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from research_assistant.core.tool_registry import MCPTool
from research_assistant.search.search_factory import SearchFactory
from research_assistant.search.base_searcher import SearchResult
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class SearchToolInput(BaseModel):
    """Input model for the search tool."""
    query: str = Field(..., description="Search query string")
    searcher_type: str = Field(
        default="duckduckgo",
        description="Type of searcher to use (duckduckgo, searx, academic)"
    )
    max_results: int = Field(
        default=10,
        description="Maximum number of results to return"
    )
    filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional search filters"
    )

class SearchTool(MCPTool):
    """Tool for performing web and academic searches."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the search tool.

        Args:
            config_path: Path to the search configuration file
        """
        super().__init__(
            name="search",
            description="Search the web and academic sources",
            version="1.0.0"
        )
        self.search_factory = SearchFactory(config_path)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the search tool.

        Args:
            input_data: Input data containing search parameters

        Returns:
            Dictionary containing search results
        """
        try:
            # Parse and validate input
            search_input = SearchToolInput(**input_data)
            
            # Get searcher instance
            searcher = self.search_factory.get_searcher(search_input.searcher_type)
            if not searcher:
                raise ValueError(f"Failed to create searcher of type {search_input.searcher_type}")

            # Validate query
            if not await searcher.validate_query(search_input.query):
                raise ValueError("Invalid search query")

            # Perform search
            results = await searcher.search(
                query=search_input.query,
                max_results=search_input.max_results,
                filters=search_input.filters
            )

            # Format results
            formatted_results = [
                {
                    "title": result.title,
                    "url": result.url,
                    "snippet": result.snippet,
                    "source": result.source,
                    "metadata": result.metadata
                }
                for result in results
            ]

            return {
                "status": "success",
                "results": formatted_results,
                "total_results": len(formatted_results)
            }

        except Exception as e:
            logger.error(f"Search tool error: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def close(self):
        """Close the search tool and its resources."""
        await self.search_factory.close_all() 
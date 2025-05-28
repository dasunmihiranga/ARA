import aiohttp
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin

from research_assistant.search.base_searcher import BaseSearcher, SearchResult
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class SearXSearcher(BaseSearcher):
    """SearX search implementation."""

    def __init__(self, instance_url: str):
        """
        Initialize the SearX searcher.

        Args:
            instance_url: URL of the SearX instance
        """
        super().__init__(
            name="searx",
            description="Search using SearX metasearch engine"
        )
        self.instance_url = instance_url.rstrip('/')
        self.search_url = urljoin(self.instance_url, "/search")
        self.session = None

    async def _ensure_session(self):
        """Ensure aiohttp session exists."""
        if self.session is None:
            self.session = aiohttp.ClientSession()

    async def search(
        self,
        query: str,
        max_results: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Perform a SearX search.

        Args:
            query: Search query string
            max_results: Maximum number of results to return
            filters: Optional search filters

        Returns:
            List of search results
        """
        await self._ensure_session()

        # Prepare search parameters
        params = {
            "q": query,
            "format": "json",
            "pageno": 1,
            "engines": "google,bing,duckduckgo",
            "language": "en",
            "results_on_page": max_results
        }

        # Add filters if provided
        if filters:
            if "engines" in filters:
                params["engines"] = filters["engines"]
            if "language" in filters:
                params["language"] = filters["language"]
            if "time_range" in filters:
                params["time_range"] = filters["time_range"]

        try:
            async with self.session.get(self.search_url, params=params) as response:
                if response.status != 200:
                    raise Exception(f"SearX API error: {response.status}")

                data = await response.json()
                results = []

                # Process search results
                for result in data.get("results", [])[:max_results]:
                    results.append(SearchResult(
                        title=result.get("title", ""),
                        url=result.get("url", ""),
                        snippet=result.get("content", ""),
                        source="searx",
                        metadata={
                            "engine": result.get("engine", ""),
                            "score": result.get("score", 0),
                            "category": result.get("category", ""),
                            "img_src": result.get("img_src", "")
                        }
                    ))

                return results

        except Exception as e:
            logger.error(f"SearX search error: {str(e)}")
            raise

    async def validate_query(self, query: str) -> bool:
        """
        Validate a search query.

        Args:
            query: Query to validate

        Returns:
            True if query is valid, False otherwise
        """
        return bool(query and len(query.strip()) > 0)

    async def close(self):
        """Close the aiohttp session."""
        if self.session:
            await self.session.close()
            self.session = None 
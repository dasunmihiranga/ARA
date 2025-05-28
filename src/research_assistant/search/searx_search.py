from typing import Dict, Any, List, Optional
import aiohttp
import asyncio
from urllib.parse import urljoin

from research_assistant.search.base_searcher import BaseSearcher, SearchResult, SearchOptions
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class SearXSearcher(BaseSearcher):
    """SearX search implementation."""

    def __init__(
        self,
        instance_url: str,
        api_key: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize the SearX searcher.

        Args:
            instance_url: URL of the SearX instance
            api_key: Optional API key
            timeout: Request timeout in seconds
        """
        super().__init__(
            name="searx",
            description="Search using SearX meta-search engine"
        )
        self.instance_url = instance_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None

    async def _ensure_session(self) -> None:
        """Ensure aiohttp session exists."""
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def search(
        self,
        query: str,
        options: Optional[SearchOptions] = None
    ) -> List[SearchResult]:
        """
        Perform a SearX search.

        Args:
            query: Search query
            options: Optional search options

        Returns:
            List of search results

        Raises:
            ValueError: If query is invalid
            Exception: For other search errors
        """
        if not self.validate_query(query):
            raise ValueError("Invalid search query")

        options = options or SearchOptions()
        await self._ensure_session()

        try:
            # Prepare request parameters
            params = {
                "q": query,
                "format": "json",
                "pageno": 1,
                "engines": "google,bing,duckduckgo",
                "language": "en",
                "time_range": None,
                "category": "general"
            }

            # Add filters if specified
            if options.filters:
                params.update(options.filters)

            # Prepare headers
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            # Make request
            async with self.session.get(
                urljoin(self.instance_url, "/search"),
                params=params,
                headers=headers,
                timeout=min(options.timeout, self.timeout)
            ) as response:
                if response.status != 200:
                    raise Exception(f"SearX API error: {response.status}")

                data = await response.json()
                results = []

                # Process results
                for result in data.get("results", [])[:options.max_results]:
                    results.append(self.format_result({
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "snippet": result.get("content", ""),
                        "metadata": {
                            "engine": result.get("engine", ""),
                            "score": result.get("score", 0),
                            "category": result.get("category", ""),
                            "source": "SearX"
                        }
                    }))

                # Add suggestions if available
                if "suggestions" in data:
                    for suggestion in data["suggestions"][:options.max_results - len(results)]:
                        results.append(self.format_result({
                            "title": suggestion,
                            "url": f"search?q={suggestion}",
                            "snippet": f"Suggested search: {suggestion}",
                            "metadata": {
                                "type": "suggestion",
                                "source": "SearX"
                            }
                        }))

                return results

        except asyncio.TimeoutError:
            self.logger.error("SearX search timed out")
            raise Exception("Search timed out")
        except Exception as e:
            self.logger.error(f"SearX search error: {str(e)}")
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

    async def close(self) -> None:
        """Close the SearX searcher."""
        if self.session:
            await self.session.close()
            self.session = None 
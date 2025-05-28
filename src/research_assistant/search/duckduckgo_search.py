from typing import Dict, Any, List, Optional
import aiohttp
import asyncio
from urllib.parse import quote_plus

from research_assistant.search.base_searcher import BaseSearcher, SearchResult, SearchOptions
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class DuckDuckGoSearcher(BaseSearcher):
    """DuckDuckGo search implementation."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.duckduckgo.com/"
    ):
        """
        Initialize the DuckDuckGo searcher.

        Args:
            api_key: Optional API key
            base_url: Base URL for the DuckDuckGo API
        """
        super().__init__(
            name="duckduckgo",
            description="Search using DuckDuckGo API"
        )
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
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
        Perform a DuckDuckGo search.

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
                "no_html": 1,
                "no_redirect": 1,
                "skip_disambig": 1
            }
            if self.api_key:
                params["appid"] = self.api_key

            # Make request
            async with self.session.get(
                f"{self.base_url}/",
                params=params,
                timeout=options.timeout
            ) as response:
                if response.status != 200:
                    raise Exception(f"DuckDuckGo API error: {response.status}")

                data = await response.json()
                results = []

                # Process results
                if "Results" in data:
                    for result in data["Results"][:options.max_results]:
                        results.append(self.format_result({
                            "title": result.get("Text", ""),
                            "url": result.get("FirstURL", ""),
                            "snippet": result.get("Text", ""),
                            "metadata": {
                                "icon": result.get("Icon", {}),
                                "source": "DuckDuckGo"
                            }
                        }))

                # Add related topics
                if "RelatedTopics" in data:
                    for topic in data["RelatedTopics"][:options.max_results - len(results)]:
                        if "Text" in topic and "FirstURL" in topic:
                            results.append(self.format_result({
                                "title": topic.get("Text", ""),
                                "url": topic.get("FirstURL", ""),
                                "snippet": topic.get("Text", ""),
                                "metadata": {
                                    "type": "related_topic",
                                    "source": "DuckDuckGo"
                                }
                            }))

                return results

        except asyncio.TimeoutError:
            self.logger.error("DuckDuckGo search timed out")
            raise Exception("Search timed out")
        except Exception as e:
            self.logger.error(f"DuckDuckGo search error: {str(e)}")
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
        """Close the DuckDuckGo searcher."""
        if self.session:
            await self.session.close()
            self.session = None 
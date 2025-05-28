import aiohttp
from typing import Dict, Any, List, Optional
from urllib.parse import quote_plus

from research_assistant.search.base_searcher import BaseSearcher, SearchResult
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class DuckDuckGoSearcher(BaseSearcher):
    """DuckDuckGo search implementation."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the DuckDuckGo searcher.

        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
        self.base_url = "https://api.duckduckgo.com/"
        self.session: Optional[aiohttp.ClientSession] = None

    async def _ensure_session(self) -> None:
        """Ensure aiohttp session exists."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()

    async def search(
        self,
        query: str,
        max_results: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Perform a DuckDuckGo search.

        Args:
            query: Search query string
            max_results: Maximum number of results to return
            filters: Additional search filters

        Returns:
            List of search results

        Raises:
            Exception: If search fails
        """
        if not self.enabled:
            logger.warning("DuckDuckGo searcher is disabled")
            return []

        try:
            await self._ensure_session()
            max_results = max_results or self.max_results

            # Prepare search parameters
            params = {
                "q": query,
                "format": "json",
                "no_html": 1,
                "no_redirect": 1,
                "skip_disambig": 1
            }

            # Add filters if provided
            if filters:
                params.update(filters)

            # Perform search
            async with self.session.get(
                self.base_url,
                params=params,
                timeout=self.timeout
            ) as response:
                if response.status != 200:
                    raise Exception(f"DuckDuckGo API returned status {response.status}")

                data = await response.json()
                results = []

                # Process instant answer
                if data.get("Abstract"):
                    results.append(SearchResult(
                        title=data.get("Heading", "Instant Answer"),
                        url=data.get("AbstractURL", ""),
                        snippet=data.get("Abstract", ""),
                        source="DuckDuckGo Instant Answer",
                        metadata={"type": "instant_answer"}
                    ))

                # Process related topics
                for topic in data.get("RelatedTopics", [])[:max_results]:
                    if "Text" in topic and "FirstURL" in topic:
                        results.append(SearchResult(
                            title=topic.get("Text", "").split(" - ")[0],
                            url=topic.get("FirstURL", ""),
                            snippet=topic.get("Text", ""),
                            source="DuckDuckGo Related Topics",
                            metadata={"type": "related_topic"}
                        ))

                return results[:max_results]

        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {str(e)}")
            raise

    async def validate_connection(self) -> bool:
        """
        Validate connection to DuckDuckGo API.

        Returns:
            True if connection is valid, False otherwise
        """
        try:
            await self._ensure_session()
            async with self.session.get(
                self.base_url,
                params={"q": "test", "format": "json"},
                timeout=5
            ) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"DuckDuckGo connection validation failed: {str(e)}")
            return False

    async def close(self) -> None:
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close() 
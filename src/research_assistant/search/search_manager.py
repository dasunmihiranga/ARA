from typing import Dict, Any, List, Optional, Type
import asyncio
from concurrent.futures import ThreadPoolExecutor

from research_assistant.search.base_searcher import BaseSearcher, SearchResult, SearchOptions
from research_assistant.search.duckduckgo_search import DuckDuckGoSearcher
from research_assistant.search.searx_search import SearXSearcher
from research_assistant.search.scholar_search import ScholarSearcher
from research_assistant.search.arxiv_search import ArxivSearcher
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class SearchManager:
    """Manager for multiple search engines."""

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the search manager.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.searchers: Dict[str, BaseSearcher] = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        self._initialize_searchers()

    def _initialize_searchers(self) -> None:
        """Initialize available search engines."""
        # Initialize DuckDuckGo searcher
        if "duckduckgo" in self.config:
            self.searchers["duckduckgo"] = DuckDuckGoSearcher(
                api_key=self.config["duckduckgo"].get("api_key"),
                timeout=self.config["duckduckgo"].get("timeout", 30)
            )

        # Initialize SearX searcher
        if "searx" in self.config:
            self.searchers["searx"] = SearXSearcher(
                instance_url=self.config["searx"]["instance_url"],
                api_key=self.config["searx"].get("api_key"),
                timeout=self.config["searx"].get("timeout", 30)
            )

        # Initialize Google Scholar searcher
        if "scholar" in self.config:
            self.searchers["scholar"] = ScholarSearcher(
                base_url=self.config["scholar"].get("base_url"),
                timeout=self.config["scholar"].get("timeout", 30)
            )

        # Initialize arXiv searcher
        if "arxiv" in self.config:
            self.searchers["arxiv"] = ArxivSearcher(
                base_url=self.config["arxiv"].get("base_url"),
                timeout=self.config["arxiv"].get("timeout", 30)
            )

    async def search(
        self,
        query: str,
        engines: Optional[List[str]] = None,
        options: Optional[SearchOptions] = None
    ) -> Dict[str, List[SearchResult]]:
        """
        Perform search across multiple engines.

        Args:
            query: Search query
            engines: List of search engines to use (None for all)
            options: Optional search options

        Returns:
            Dictionary mapping engine names to their search results

        Raises:
            ValueError: If no valid search engines are specified
        """
        if not engines:
            engines = list(self.searchers.keys())
        else:
            engines = [e for e in engines if e in self.searchers]

        if not engines:
            raise ValueError("No valid search engines specified")

        options = options or SearchOptions()
        results = {}

        # Create search tasks
        tasks = []
        for engine in engines:
            searcher = self.searchers[engine]
            tasks.append(self._search_with_engine(searcher, query, options))

        # Execute searches concurrently
        try:
            engine_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for engine, result in zip(engines, engine_results):
                if isinstance(result, Exception):
                    logger.error(f"Search error in {engine}: {str(result)}")
                    results[engine] = []
                else:
                    results[engine] = result

        except Exception as e:
            logger.error(f"Search manager error: {str(e)}")
            raise

        return results

    async def _search_with_engine(
        self,
        searcher: BaseSearcher,
        query: str,
        options: SearchOptions
    ) -> List[SearchResult]:
        """
        Execute search with a specific engine.

        Args:
            searcher: Search engine instance
            query: Search query
            options: Search options

        Returns:
            List of search results
        """
        try:
            return await searcher.search(query, options)
        except Exception as e:
            logger.error(f"Error searching with {searcher.name}: {str(e)}")
            raise

    def get_available_engines(self) -> List[str]:
        """
        Get list of available search engines.

        Returns:
            List of engine names
        """
        return list(self.searchers.keys())

    def get_engine_info(self, engine: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific search engine.

        Args:
            engine: Engine name

        Returns:
            Dictionary with engine information or None if not found
        """
        if engine not in self.searchers:
            return None

        searcher = self.searchers[engine]
        return {
            "name": searcher.name,
            "description": searcher.description,
            "config": self.config.get(engine, {})
        }

    async def close(self) -> None:
        """Close all search engines."""
        for searcher in self.searchers.values():
            try:
                await searcher.close()
            except Exception as e:
                logger.error(f"Error closing {searcher.name}: {str(e)}")

        self.executor.shutdown() 
from typing import Dict, Any, List, Optional
import aiohttp
import asyncio
from urllib.parse import urljoin, quote_plus
import xml.etree.ElementTree as ET
from datetime import datetime

from research_assistant.search.base_searcher import BaseSearcher, SearchResult, SearchOptions
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class ArxivSearcher(BaseSearcher):
    """arXiv search implementation."""

    def __init__(
        self,
        base_url: str = "http://export.arxiv.org/api",
        timeout: int = 30
    ):
        """
        Initialize the arXiv searcher.

        Args:
            base_url: Base URL for arXiv API
            timeout: Request timeout in seconds
        """
        super().__init__(
            name="arxiv",
            description="Search academic papers using arXiv API"
        )
        self.base_url = base_url.rstrip("/")
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
        Perform an arXiv search.

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
                "search_query": query,
                "start": 0,
                "max_results": options.max_results,
                "sortBy": "relevance",
                "sortOrder": "descending"
            }

            # Add filters if specified
            if options.filters:
                if "category" in options.filters:
                    params["search_query"] += f" cat:{options.filters['category']}"
                if "date_range" in options.filters:
                    params["search_query"] += f" submittedDate:[{options.filters['date_range']}]"

            # Make request
            async with self.session.get(
                urljoin(self.base_url, "/query"),
                params=params,
                timeout=min(options.timeout, self.timeout)
            ) as response:
                if response.status != 200:
                    raise Exception(f"arXiv API error: {response.status}")

                xml_data = await response.text()
                results = []

                # Parse XML response
                root = ET.fromstring(xml_data)
                namespace = {"atom": "http://www.w3.org/2005/Atom"}

                for entry in root.findall(".//atom:entry", namespace):
                    # Extract paper information
                    title = entry.find("atom:title", namespace).text
                    abstract = entry.find("atom:summary", namespace).text
                    pdf_link = entry.find("atom:link[@title='pdf']", namespace).get("href")
                    arxiv_id = entry.find("atom:id", namespace).text.split("/")[-1]
                    
                    # Extract authors
                    authors = []
                    for author in entry.findall("atom:author/atom:name", namespace):
                        authors.append(author.text)

                    # Extract publication date
                    published = entry.find("atom:published", namespace).text
                    published_date = datetime.strptime(published, "%Y-%m-%dT%H:%M:%SZ")

                    # Extract categories
                    categories = []
                    for category in entry.findall("atom:category", namespace):
                        categories.append(category.get("term"))

                    results.append(self.format_result({
                        "title": title,
                        "url": pdf_link,
                        "snippet": abstract,
                        "metadata": {
                            "authors": authors,
                            "arxiv_id": arxiv_id,
                            "published_date": published_date.isoformat(),
                            "categories": categories,
                            "source": "arXiv"
                        }
                    }))

                return results

        except asyncio.TimeoutError:
            self.logger.error("arXiv search timed out")
            raise Exception("Search timed out")
        except Exception as e:
            self.logger.error(f"arXiv search error: {str(e)}")
            raise

    async def close(self) -> None:
        """Close the arXiv searcher."""
        if self.session:
            await self.session.close()
            self.session = None 
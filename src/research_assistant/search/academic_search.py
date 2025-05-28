import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime
import arxiv
from scholarly import scholarly

from research_assistant.search.base_searcher import BaseSearcher, SearchResult
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class AcademicSearcher(BaseSearcher):
    """Academic search implementation supporting arXiv and Google Scholar."""

    def __init__(self):
        """Initialize the academic searcher."""
        super().__init__(
            name="academic",
            description="Search academic papers using arXiv and Google Scholar"
        )
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
        Perform an academic search.

        Args:
            query: Search query string
            max_results: Maximum number of results to return
            filters: Optional search filters including:
                - source: "arxiv" or "scholar" (default: both)
                - categories: List of arXiv categories
                - year: Publication year
                - sort_by: "relevance" or "date"

        Returns:
            List of search results
        """
        results = []
        source = filters.get("source", "both") if filters else "both"

        try:
            if source in ["arxiv", "both"]:
                arxiv_results = await self._search_arxiv(query, max_results, filters)
                results.extend(arxiv_results)

            if source in ["scholar", "both"]:
                scholar_results = await self._search_scholar(query, max_results, filters)
                results.extend(scholar_results)

            # Sort results if specified
            if filters and filters.get("sort_by") == "date":
                results.sort(key=lambda x: x.metadata.get("date", ""), reverse=True)
            else:
                results.sort(key=lambda x: x.metadata.get("score", 0), reverse=True)

            return results[:max_results]

        except Exception as e:
            logger.error(f"Academic search error: {str(e)}")
            raise

    async def _search_arxiv(
        self,
        query: str,
        max_results: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search arXiv for papers."""
        results = []
        categories = filters.get("categories", []) if filters else []

        try:
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance,
                sort_order=arxiv.SortOrder.Descending
            )

            for paper in search.results():
                if not categories or any(cat in paper.categories for cat in categories):
                    results.append(SearchResult(
                        title=paper.title,
                        url=paper.entry_id,
                        snippet=paper.summary,
                        source="arxiv",
                        metadata={
                            "authors": [author.name for author in paper.authors],
                            "categories": paper.categories,
                            "date": paper.published.isoformat(),
                            "pdf_url": paper.pdf_url,
                            "score": 1.0  # arXiv doesn't provide relevance scores
                        }
                    ))

            return results

        except Exception as e:
            logger.error(f"arXiv search error: {str(e)}")
            return []

    async def _search_scholar(
        self,
        query: str,
        max_results: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search Google Scholar for papers."""
        results = []
        year = filters.get("year") if filters else None

        try:
            search_query = scholarly.search_pubs(query)
            count = 0

            while count < max_results:
                try:
                    paper = next(search_query)
                    
                    # Filter by year if specified
                    if year and paper.get("bib", {}).get("pub_year") != str(year):
                        continue

                    results.append(SearchResult(
                        title=paper.get("bib", {}).get("title", ""),
                        url=paper.get("pub_url", ""),
                        snippet=paper.get("bib", {}).get("abstract", ""),
                        source="scholar",
                        metadata={
                            "authors": paper.get("bib", {}).get("author", []),
                            "venue": paper.get("bib", {}).get("venue", ""),
                            "year": paper.get("bib", {}).get("pub_year", ""),
                            "citations": paper.get("num_citations", 0),
                            "score": paper.get("num_citations", 0) / 100  # Normalize citation count
                        }
                    ))
                    count += 1

                except StopIteration:
                    break

            return results

        except Exception as e:
            logger.error(f"Google Scholar search error: {str(e)}")
            return []

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
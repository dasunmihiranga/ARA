import pytest
from unittest.mock import Mock, patch
from research_assistant.search.search_manager import SearchManager
from research_assistant.search.sources.duckduckgo import DuckDuckGoSearch
from research_assistant.search.sources.searx import SearxSearch

class TestSearchManager:
    @pytest.fixture
    def search_manager(self):
        return SearchManager()

    def test_initialize_search_sources(self, search_manager):
        """Test initialization of search sources."""
        assert "duckduckgo" in search_manager.sources
        assert "searx" in search_manager.sources
        assert isinstance(search_manager.sources["duckduckgo"], DuckDuckGoSearch)
        assert isinstance(search_manager.sources["searx"], SearxSearch)

    @patch("research_assistant.search.sources.duckduckgo.DuckDuckGoSearch.search")
    @patch("research_assistant.search.sources.searx.SearxSearch.search")
    async def test_search_multiple_sources(self, mock_searx, mock_ddg, search_manager, mock_search_query):
        """Test searching across multiple sources."""
        mock_ddg.return_value = [
            {
                "title": "DDG Result",
                "url": "https://example.com/ddg",
                "snippet": "DuckDuckGo result",
                "source": "duckduckgo",
                "relevance_score": 0.9
            }
        ]
        mock_searx.return_value = [
            {
                "title": "Searx Result",
                "url": "https://example.com/searx",
                "snippet": "Searx result",
                "source": "searx",
                "relevance_score": 0.8
            }
        ]

        results = await search_manager.search(mock_search_query)
        
        assert len(results) == 2
        assert any(r["source"] == "duckduckgo" for r in results)
        assert any(r["source"] == "searx" for r in results)
        mock_ddg.assert_called_once()
        mock_searx.assert_called_once()

    @patch("research_assistant.search.sources.duckduckgo.DuckDuckGoSearch.search")
    async def test_search_single_source(self, mock_ddg, search_manager, mock_search_query):
        """Test searching with a single source."""
        mock_ddg.return_value = [
            {
                "title": "DDG Result",
                "url": "https://example.com/ddg",
                "snippet": "DuckDuckGo result",
                "source": "duckduckgo",
                "relevance_score": 0.9
            }
        ]

        mock_search_query["sources"] = ["duckduckgo"]
        results = await search_manager.search(mock_search_query)
        
        assert len(results) == 1
        assert results[0]["source"] == "duckduckgo"
        mock_ddg.assert_called_once()

    async def test_search_invalid_source(self, search_manager, mock_search_query):
        """Test searching with an invalid source."""
        mock_search_query["sources"] = ["invalid_source"]
        
        with pytest.raises(ValueError, match="Invalid search source"):
            await search_manager.search(mock_search_query)

    @patch("research_assistant.search.sources.duckduckgo.DuckDuckGoSearch.search")
    async def test_search_timeout(self, mock_ddg, search_manager, mock_search_query):
        """Test search timeout handling."""
        mock_ddg.side_effect = TimeoutError("Search timed out")
        
        with pytest.raises(TimeoutError, match="Search timed out"):
            await search_manager.search(mock_search_query)

    @patch("research_assistant.search.sources.duckduckgo.DuckDuckGoSearch.search")
    async def test_search_rate_limit(self, mock_ddg, search_manager, mock_search_query):
        """Test search rate limit handling."""
        mock_ddg.side_effect = Exception("Rate limit exceeded")
        
        with pytest.raises(Exception, match="Rate limit exceeded"):
            await search_manager.search(mock_search_query)

    def test_validate_search_query(self, search_manager, mock_search_query):
        """Test search query validation."""
        # Test valid query
        assert search_manager.validate_search_query(mock_search_query) is True

        # Test invalid query (missing required field)
        invalid_query = mock_search_query.copy()
        del invalid_query["query"]
        assert search_manager.validate_search_query(invalid_query) is False

        # Test invalid query (invalid max_results)
        invalid_query = mock_search_query.copy()
        invalid_query["max_results"] = -1
        assert search_manager.validate_search_query(invalid_query) is False

    @patch("research_assistant.search.sources.duckduckgo.DuckDuckGoSearch.search")
    async def test_search_result_deduplication(self, mock_ddg, search_manager, mock_search_query):
        """Test deduplication of search results."""
        mock_ddg.return_value = [
            {
                "title": "Duplicate Result",
                "url": "https://example.com/duplicate",
                "snippet": "This is a duplicate",
                "source": "duckduckgo",
                "relevance_score": 0.9
            },
            {
                "title": "Duplicate Result",
                "url": "https://example.com/duplicate",
                "snippet": "This is a duplicate",
                "source": "duckduckgo",
                "relevance_score": 0.9
            }
        ]

        results = await search_manager.search(mock_search_query)
        assert len(results) == 1  # Duplicate should be removed

    @patch("research_assistant.search.sources.duckduckgo.DuckDuckGoSearch.search")
    async def test_search_result_ranking(self, mock_ddg, search_manager, mock_search_query):
        """Test ranking of search results."""
        mock_ddg.return_value = [
            {
                "title": "Low Score",
                "url": "https://example.com/low",
                "snippet": "Low relevance",
                "source": "duckduckgo",
                "relevance_score": 0.3
            },
            {
                "title": "High Score",
                "url": "https://example.com/high",
                "snippet": "High relevance",
                "source": "duckduckgo",
                "relevance_score": 0.9
            }
        ]

        results = await search_manager.search(mock_search_query)
        assert results[0]["relevance_score"] > results[1]["relevance_score"] 
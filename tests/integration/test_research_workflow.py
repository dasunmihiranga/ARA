import pytest
from unittest.mock import Mock, patch
from research_assistant import ResearchAssistant
from research_assistant.search.search_manager import SearchManager
from research_assistant.extraction.extraction_manager import ExtractionManager
from research_assistant.analysis.analysis_manager import AnalysisManager
from research_assistant.knowledge_graph.graph_manager import GraphManager
from research_assistant.reports.report_manager import ReportManager

class TestResearchWorkflow:
    @pytest.fixture
    def research_assistant(self):
        return ResearchAssistant()

    @patch("research_assistant.search.search_manager.SearchManager.search")
    @patch("research_assistant.extraction.extraction_manager.ExtractionManager.extract")
    @patch("research_assistant.analysis.analysis_manager.AnalysisManager.analyze")
    async def test_complete_research_workflow(self, mock_analyze, mock_extract, mock_search, research_assistant):
        """Test complete research workflow from search to report generation."""
        # Mock search results
        mock_search.return_value = [
            {
                "title": "Test Result 1",
                "url": "https://example.com/1",
                "snippet": "Test content 1",
                "source": "duckduckgo",
                "relevance_score": 0.9
            },
            {
                "title": "Test Result 2",
                "url": "https://example.com/2",
                "snippet": "Test content 2",
                "source": "searx",
                "relevance_score": 0.8
            }
        ]

        # Mock content extraction
        mock_extract.return_value = {
            "text": "Extracted content for analysis",
            "metadata": {
                "title": "Test Content",
                "author": "Test Author",
                "date": "2024-03-15"
            }
        }

        # Mock analysis results
        mock_analyze.return_value = {
            "summary": "Test summary",
            "key_points": ["Point 1", "Point 2"],
            "confidence_score": 0.95
        }

        # Execute research workflow
        result = await research_assistant.research(
            query="test query",
            analysis_type="summarize",
            report_template="academic"
        )

        # Verify workflow execution
        assert "search_results" in result
        assert "extracted_content" in result
        assert "analysis_results" in result
        assert "report" in result

        # Verify component calls
        mock_search.assert_called_once()
        mock_extract.assert_called()
        mock_analyze.assert_called_once()

    @patch("research_assistant.search.search_manager.SearchManager.search")
    @patch("research_assistant.extraction.extraction_manager.ExtractionManager.extract")
    @patch("research_assistant.analysis.analysis_manager.AnalysisManager.analyze")
    @patch("research_assistant.knowledge_graph.graph_manager.GraphManager.build_graph")
    async def test_research_with_knowledge_graph(self, mock_graph, mock_analyze, mock_extract, mock_search, research_assistant):
        """Test research workflow with knowledge graph generation."""
        # Mock component responses
        mock_search.return_value = [{"title": "Test", "url": "https://example.com"}]
        mock_extract.return_value = {"text": "Test content", "metadata": {}}
        mock_analyze.return_value = {"summary": "Test summary", "key_points": []}
        mock_graph.return_value = {
            "nodes": [{"id": "1", "label": "Concept"}],
            "edges": []
        }

        # Execute research with knowledge graph
        result = await research_assistant.research(
            query="test query",
            analysis_type="summarize",
            generate_knowledge_graph=True
        )

        # Verify knowledge graph generation
        assert "knowledge_graph" in result
        assert "nodes" in result["knowledge_graph"]
        mock_graph.assert_called_once()

    @patch("research_assistant.search.search_manager.SearchManager.search")
    @patch("research_assistant.extraction.extraction_manager.ExtractionManager.extract")
    @patch("research_assistant.analysis.analysis_manager.AnalysisManager.analyze")
    async def test_research_with_fact_checking(self, mock_analyze, mock_extract, mock_search, research_assistant):
        """Test research workflow with fact checking."""
        # Mock component responses
        mock_search.return_value = [{"title": "Test", "url": "https://example.com"}]
        mock_extract.return_value = {"text": "Test content", "metadata": {}}
        mock_analyze.return_value = {
            "claims": [
                {
                    "text": "Test claim",
                    "verification": "verified",
                    "confidence": 0.9
                }
            ]
        }

        # Execute research with fact checking
        result = await research_assistant.research(
            query="test query",
            analysis_type="fact_check"
        )

        # Verify fact checking results
        assert "analysis_results" in result
        assert "claims" in result["analysis_results"]
        mock_analyze.assert_called_once()

    @patch("research_assistant.search.search_manager.SearchManager.search")
    @patch("research_assistant.extraction.extraction_manager.ExtractionManager.extract")
    @patch("research_assistant.analysis.analysis_manager.AnalysisManager.analyze")
    async def test_research_with_sentiment_analysis(self, mock_analyze, mock_extract, mock_search, research_assistant):
        """Test research workflow with sentiment analysis."""
        # Mock component responses
        mock_search.return_value = [{"title": "Test", "url": "https://example.com"}]
        mock_extract.return_value = {"text": "Test content", "metadata": {}}
        mock_analyze.return_value = {
            "sentiment": "positive",
            "score": 0.8,
            "aspects": [
                {"aspect": "quality", "sentiment": "positive", "score": 0.9}
            ]
        }

        # Execute research with sentiment analysis
        result = await research_assistant.research(
            query="test query",
            analysis_type="analyze_sentiment"
        )

        # Verify sentiment analysis results
        assert "analysis_results" in result
        assert "sentiment" in result["analysis_results"]
        assert "aspects" in result["analysis_results"]
        mock_analyze.assert_called_once()

    @patch("research_assistant.search.search_manager.SearchManager.search")
    @patch("research_assistant.extraction.extraction_manager.ExtractionManager.extract")
    @patch("research_assistant.analysis.analysis_manager.AnalysisManager.analyze")
    async def test_research_with_topic_modeling(self, mock_analyze, mock_extract, mock_search, research_assistant):
        """Test research workflow with topic modeling."""
        # Mock component responses
        mock_search.return_value = [{"title": "Test", "url": "https://example.com"}]
        mock_extract.return_value = {"text": "Test content", "metadata": {}}
        mock_analyze.return_value = {
            "topics": [
                {
                    "name": "Topic 1",
                    "keywords": ["word1", "word2"],
                    "weight": 0.8
                }
            ],
            "topic_distribution": [0.8, 0.2]
        }

        # Execute research with topic modeling
        result = await research_assistant.research(
            query="test query",
            analysis_type="model_topics"
        )

        # Verify topic modeling results
        assert "analysis_results" in result
        assert "topics" in result["analysis_results"]
        assert "topic_distribution" in result["analysis_results"]
        mock_analyze.assert_called_once()

    @patch("research_assistant.search.search_manager.SearchManager.search")
    async def test_research_error_handling(self, mock_search, research_assistant):
        """Test error handling in research workflow."""
        # Mock search error
        mock_search.side_effect = Exception("Search failed")

        # Execute research with error
        with pytest.raises(Exception, match="Search failed"):
            await research_assistant.research(
                query="test query",
                analysis_type="summarize"
            )

    @patch("research_assistant.search.search_manager.SearchManager.search")
    @patch("research_assistant.extraction.extraction_manager.ExtractionManager.extract")
    async def test_research_with_timeout(self, mock_extract, mock_search, research_assistant):
        """Test timeout handling in research workflow."""
        # Mock search timeout
        mock_search.side_effect = TimeoutError("Search timed out")

        # Execute research with timeout
        with pytest.raises(TimeoutError, match="Search timed out"):
            await research_assistant.research(
                query="test query",
                analysis_type="summarize"
            )

    @patch("research_assistant.search.search_manager.SearchManager.search")
    @patch("research_assistant.extraction.extraction_manager.ExtractionManager.extract")
    @patch("research_assistant.analysis.analysis_manager.AnalysisManager.analyze")
    async def test_research_with_custom_options(self, mock_analyze, mock_extract, mock_search, research_assistant):
        """Test research workflow with custom options."""
        # Mock component responses
        mock_search.return_value = [{"title": "Test", "url": "https://example.com"}]
        mock_extract.return_value = {"text": "Test content", "metadata": {}}
        mock_analyze.return_value = {"summary": "Test summary", "key_points": []}

        # Execute research with custom options
        result = await research_assistant.research(
            query="test query",
            analysis_type="summarize",
            search_options={"max_results": 5},
            extraction_options={"clean_html": True},
            analysis_options={"max_length": 200}
        )

        # Verify custom options were used
        assert "search_results" in result
        assert "extracted_content" in result
        assert "analysis_results" in result
        mock_search.assert_called_once()
        mock_extract.assert_called_once()
        mock_analyze.assert_called_once() 
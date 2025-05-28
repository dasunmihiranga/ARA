import pytest
import asyncio
from research_assistant import ResearchAssistant
from research_assistant.config import load_config
from research_assistant.utils.logger import setup_logger

class TestSystem:
    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup test environment."""
        # Load configuration
        self.config = load_config()
        
        # Setup logging
        setup_logger(self.config["logging"])
        
        # Initialize research assistant
        self.research_assistant = ResearchAssistant()
        
        # Setup test data
        self.test_queries = [
            "quantum computing applications",
            "machine learning in healthcare",
            "climate change solutions"
        ]
        
        yield
        
        # Cleanup
        await self.research_assistant.close()

    @pytest.mark.asyncio
    async def test_complete_research_workflow(self):
        """Test complete research workflow with real components."""
        # Execute research workflow
        result = await self.research_assistant.research(
            query=self.test_queries[0],
            analysis_type="summarize",
            report_template="academic",
            search_options={"max_results": 5},
            extraction_options={"clean_html": True},
            analysis_options={"max_length": 200}
        )
        
        # Verify results
        assert "search_results" in result
        assert "extracted_content" in result
        assert "analysis_results" in result
        assert "report" in result
        
        # Verify search results
        assert len(result["search_results"]) > 0
        assert all("title" in r for r in result["search_results"])
        assert all("url" in r for r in result["search_results"])
        
        # Verify extracted content
        assert "text" in result["extracted_content"]
        assert "metadata" in result["extracted_content"]
        
        # Verify analysis results
        assert "summary" in result["analysis_results"]
        assert "key_points" in result["analysis_results"]
        
        # Verify report
        assert "title" in result["report"]
        assert "content" in result["report"]
        assert "sections" in result["report"]

    @pytest.mark.asyncio
    async def test_research_with_knowledge_graph(self):
        """Test research workflow with knowledge graph generation."""
        # Execute research with knowledge graph
        result = await self.research_assistant.research(
            query=self.test_queries[1],
            analysis_type="summarize",
            generate_knowledge_graph=True
        )
        
        # Verify knowledge graph
        assert "knowledge_graph" in result
        assert "nodes" in result["knowledge_graph"]
        assert "edges" in result["knowledge_graph"]
        
        # Verify graph structure
        assert len(result["knowledge_graph"]["nodes"]) > 0
        assert all("id" in n for n in result["knowledge_graph"]["nodes"])
        assert all("label" in n for n in result["knowledge_graph"]["nodes"])

    @pytest.mark.asyncio
    async def test_research_with_fact_checking(self):
        """Test research workflow with fact checking."""
        # Execute research with fact checking
        result = await self.research_assistant.research(
            query=self.test_queries[2],
            analysis_type="fact_check"
        )
        
        # Verify fact checking results
        assert "analysis_results" in result
        assert "claims" in result["analysis_results"]
        assert "overall_veracity" in result["analysis_results"]
        
        # Verify claims
        assert len(result["analysis_results"]["claims"]) > 0
        assert all("text" in c for c in result["analysis_results"]["claims"])
        assert all("verification" in c for c in result["analysis_results"]["claims"])

    @pytest.mark.asyncio
    async def test_research_with_sentiment_analysis(self):
        """Test research workflow with sentiment analysis."""
        # Execute research with sentiment analysis
        result = await self.research_assistant.research(
            query=self.test_queries[0],
            analysis_type="analyze_sentiment"
        )
        
        # Verify sentiment analysis results
        assert "analysis_results" in result
        assert "sentiment" in result["analysis_results"]
        assert "score" in result["analysis_results"]
        assert "aspects" in result["analysis_results"]
        
        # Verify aspects
        assert len(result["analysis_results"]["aspects"]) > 0
        assert all("aspect" in a for a in result["analysis_results"]["aspects"])
        assert all("sentiment" in a for a in result["analysis_results"]["aspects"])

    @pytest.mark.asyncio
    async def test_research_with_topic_modeling(self):
        """Test research workflow with topic modeling."""
        # Execute research with topic modeling
        result = await self.research_assistant.research(
            query=self.test_queries[1],
            analysis_type="model_topics"
        )
        
        # Verify topic modeling results
        assert "analysis_results" in result
        assert "topics" in result["analysis_results"]
        assert "topic_distribution" in result["analysis_results"]
        
        # Verify topics
        assert len(result["analysis_results"]["topics"]) > 0
        assert all("name" in t for t in result["analysis_results"]["topics"])
        assert all("keywords" in t for t in result["analysis_results"]["topics"])

    @pytest.mark.asyncio
    async def test_research_with_custom_options(self):
        """Test research workflow with custom options."""
        # Execute research with custom options
        result = await self.research_assistant.research(
            query=self.test_queries[0],
            analysis_type="summarize",
            search_options={
                "max_results": 3,
                "sources": ["duckduckgo"],
                "filters": {"date_range": {"start": "2024-01-01"}}
            },
            extraction_options={
                "clean_html": True,
                "remove_ads": True,
                "extract_metadata": True
            },
            analysis_options={
                "max_length": 150,
                "focus_areas": ["key_points"],
                "confidence_threshold": 0.8
            }
        )
        
        # Verify custom options were applied
        assert len(result["search_results"]) <= 3
        assert all(r["source"] == "duckduckgo" for r in result["search_results"])
        assert "metadata" in result["extracted_content"]
        assert len(result["analysis_results"]["key_points"]) > 0

    @pytest.mark.asyncio
    async def test_research_with_multiple_queries(self):
        """Test research workflow with multiple queries."""
        # Execute research for multiple queries
        results = []
        for query in self.test_queries:
            result = await self.research_assistant.research(
                query=query,
                analysis_type="summarize"
            )
            results.append(result)
        
        # Verify results for each query
        assert len(results) == len(self.test_queries)
        for result in results:
            assert "search_results" in result
            assert "extracted_content" in result
            assert "analysis_results" in result

    @pytest.mark.asyncio
    async def test_research_with_error_handling(self):
        """Test research workflow error handling."""
        # Test with invalid query
        with pytest.raises(ValueError):
            await self.research_assistant.research(
                query="",
                analysis_type="summarize"
            )
        
        # Test with invalid analysis type
        with pytest.raises(ValueError):
            await self.research_assistant.research(
                query=self.test_queries[0],
                analysis_type="invalid_type"
            )
        
        # Test with invalid report template
        with pytest.raises(ValueError):
            await self.research_assistant.research(
                query=self.test_queries[0],
                analysis_type="summarize",
                report_template="invalid_template"
            )

    @pytest.mark.asyncio
    async def test_research_with_concurrent_requests(self):
        """Test research workflow with concurrent requests."""
        # Create multiple concurrent research requests
        tasks = [
            self.research_assistant.research(
                query=query,
                analysis_type="summarize"
            )
            for query in self.test_queries
        ]
        
        # Execute concurrent requests
        results = await asyncio.gather(*tasks)
        
        # Verify results
        assert len(results) == len(self.test_queries)
        for result in results:
            assert "search_results" in result
            assert "extracted_content" in result
            assert "analysis_results" in result 
import pytest
from unittest.mock import Mock, patch
from research_assistant.analysis.analysis_manager import AnalysisManager
from research_assistant.analysis.analyzers.summarizer import Summarizer
from research_assistant.analysis.analyzers.insight_extractor import InsightExtractor
from research_assistant.analysis.analyzers.fact_checker import FactChecker
from research_assistant.analysis.analyzers.sentiment_analyzer import SentimentAnalyzer
from research_assistant.analysis.analyzers.topic_modeler import TopicModeler

class TestAnalysisManager:
    @pytest.fixture
    def analysis_manager(self):
        return AnalysisManager()

    def test_initialize_analyzers(self, analysis_manager):
        """Test initialization of analysis components."""
        assert "summarize" in analysis_manager.analyzers
        assert "extract_insights" in analysis_manager.analyzers
        assert "fact_check" in analysis_manager.analyzers
        assert "analyze_sentiment" in analysis_manager.analyzers
        assert "model_topics" in analysis_manager.analyzers
        assert isinstance(analysis_manager.analyzers["summarize"], Summarizer)
        assert isinstance(analysis_manager.analyzers["extract_insights"], InsightExtractor)
        assert isinstance(analysis_manager.analyzers["fact_check"], FactChecker)
        assert isinstance(analysis_manager.analyzers["analyze_sentiment"], SentimentAnalyzer)
        assert isinstance(analysis_manager.analyzers["model_topics"], TopicModeler)

    @patch("research_assistant.analysis.analyzers.summarizer.Summarizer.analyze")
    async def test_summarize_content(self, mock_summarize, analysis_manager, mock_analysis_request):
        """Test content summarization."""
        mock_summarize.return_value = {
            "summary": "This is a test summary",
            "key_points": ["Point 1", "Point 2"],
            "confidence_score": 0.95
        }

        result = await analysis_manager.analyze(mock_analysis_request)
        
        assert result["summary"] == "This is a test summary"
        assert len(result["key_points"]) == 2
        assert result["confidence_score"] == 0.95
        mock_summarize.assert_called_once()

    @patch("research_assistant.analysis.analyzers.insight_extractor.InsightExtractor.analyze")
    async def test_extract_insights(self, mock_extract, analysis_manager, mock_analysis_request):
        """Test insight extraction."""
        mock_analysis_request["analysis_type"] = "extract_insights"
        mock_extract.return_value = {
            "insights": [
                {"text": "Insight 1", "confidence": 0.9},
                {"text": "Insight 2", "confidence": 0.8}
            ],
            "themes": ["Theme 1", "Theme 2"],
            "confidence_score": 0.85
        }

        result = await analysis_manager.analyze(mock_analysis_request)
        
        assert len(result["insights"]) == 2
        assert len(result["themes"]) == 2
        assert result["confidence_score"] == 0.85
        mock_extract.assert_called_once()

    @patch("research_assistant.analysis.analyzers.fact_checker.FactChecker.analyze")
    async def test_fact_checking(self, mock_check, analysis_manager, mock_analysis_request):
        """Test fact checking."""
        mock_analysis_request["analysis_type"] = "fact_check"
        mock_check.return_value = {
            "claims": [
                {
                    "text": "Claim 1",
                    "verification": "verified",
                    "confidence": 0.95,
                    "sources": ["source1", "source2"]
                }
            ],
            "overall_veracity": 0.95
        }

        result = await analysis_manager.analyze(mock_analysis_request)
        
        assert len(result["claims"]) == 1
        assert result["claims"][0]["verification"] == "verified"
        assert result["overall_veracity"] == 0.95
        mock_check.assert_called_once()

    @patch("research_assistant.analysis.analyzers.sentiment_analyzer.SentimentAnalyzer.analyze")
    async def test_sentiment_analysis(self, mock_analyze, analysis_manager, mock_analysis_request):
        """Test sentiment analysis."""
        mock_analysis_request["analysis_type"] = "analyze_sentiment"
        mock_analyze.return_value = {
            "sentiment": "positive",
            "score": 0.8,
            "aspects": [
                {"aspect": "quality", "sentiment": "positive", "score": 0.9},
                {"aspect": "price", "sentiment": "neutral", "score": 0.5}
            ]
        }

        result = await analysis_manager.analyze(mock_analysis_request)
        
        assert result["sentiment"] == "positive"
        assert result["score"] == 0.8
        assert len(result["aspects"]) == 2
        mock_analyze.assert_called_once()

    @patch("research_assistant.analysis.analyzers.topic_modeler.TopicModeler.analyze")
    async def test_topic_modeling(self, mock_model, analysis_manager, mock_analysis_request):
        """Test topic modeling."""
        mock_analysis_request["analysis_type"] = "model_topics"
        mock_model.return_value = {
            "topics": [
                {
                    "name": "Topic 1",
                    "keywords": ["word1", "word2"],
                    "weight": 0.8
                }
            ],
            "topic_distribution": [0.8, 0.2]
        }

        result = await analysis_manager.analyze(mock_analysis_request)
        
        assert len(result["topics"]) == 1
        assert len(result["topic_distribution"]) == 2
        mock_model.assert_called_once()

    async def test_analyze_invalid_type(self, analysis_manager, mock_analysis_request):
        """Test analysis with invalid type."""
        mock_analysis_request["analysis_type"] = "invalid_type"
        
        with pytest.raises(ValueError, match="Invalid analysis type"):
            await analysis_manager.analyze(mock_analysis_request)

    @patch("research_assistant.analysis.analyzers.summarizer.Summarizer.analyze")
    async def test_analyze_timeout(self, mock_summarize, analysis_manager, mock_analysis_request):
        """Test analysis timeout handling."""
        mock_summarize.side_effect = TimeoutError("Analysis timed out")
        
        with pytest.raises(TimeoutError, match="Analysis timed out"):
            await analysis_manager.analyze(mock_analysis_request)

    def test_validate_analysis_request(self, analysis_manager, mock_analysis_request):
        """Test analysis request validation."""
        # Test valid request
        assert analysis_manager.validate_analysis_request(mock_analysis_request) is True

        # Test invalid request (missing required field)
        invalid_request = mock_analysis_request.copy()
        del invalid_request["content"]
        assert analysis_manager.validate_analysis_request(invalid_request) is False

        # Test invalid request (invalid analysis type)
        invalid_request = mock_analysis_request.copy()
        invalid_request["analysis_type"] = "invalid_type"
        assert analysis_manager.validate_analysis_request(invalid_request) is False

    @patch("research_assistant.analysis.analyzers.summarizer.Summarizer.analyze")
    async def test_analyze_with_options(self, mock_summarize, analysis_manager, mock_analysis_request):
        """Test analysis with custom options."""
        mock_summarize.return_value = {
            "summary": "Custom summary",
            "key_points": ["Custom point"],
            "confidence_score": 0.9
        }

        mock_analysis_request["options"]["max_length"] = 100
        mock_analysis_request["options"]["focus_areas"] = ["key_points"]
        result = await analysis_manager.analyze(mock_analysis_request)
        
        assert result["summary"] == "Custom summary"
        assert len(result["key_points"]) == 1
        mock_summarize.assert_called_once()

    @patch("research_assistant.analysis.analyzers.summarizer.Summarizer.analyze")
    async def test_analyze_with_confidence_threshold(self, mock_summarize, analysis_manager, mock_analysis_request):
        """Test analysis with confidence threshold."""
        mock_summarize.return_value = {
            "summary": "Low confidence summary",
            "key_points": ["Point"],
            "confidence_score": 0.5
        }

        mock_analysis_request["options"]["confidence_threshold"] = 0.8
        with pytest.raises(ValueError, match="Analysis confidence below threshold"):
            await analysis_manager.analyze(mock_analysis_request) 
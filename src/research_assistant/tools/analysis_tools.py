from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

from research_assistant.tools.tool_schemas import (
    AnalysisRequest, AnalysisResult, FactCheckRequest, FactCheckResult,
    ToolResponse
)
from research_assistant.analysis.summarizer import Summarizer
from research_assistant.analysis.insight_extractor import InsightExtractor
from research_assistant.analysis.fact_checker import FactChecker
from research_assistant.analysis.sentiment_analyzer import SentimentAnalyzer
from research_assistant.analysis.topic_modeler import TopicModeler
from research_assistant.storage.cache_manager import CacheManager
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class AnalysisTools:
    """Analysis tools for the MCP server."""

    def __init__(
        self,
        cache_dir: str = "data/cache"
    ):
        """
        Initialize analysis tools.

        Args:
            cache_dir: Directory for caching results
        """
        self.cache = CacheManager(cache_dir)
        self.summarizer = Summarizer()
        self.insight_extractor = InsightExtractor()
        self.fact_checker = FactChecker()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.topic_modeler = TopicModeler()

    async def analyze_content(
        self,
        request: AnalysisRequest
    ) -> ToolResponse:
        """
        Analyze content using specified analysis type.

        Args:
            request: Analysis request parameters

        Returns:
            Analysis results
        """
        try:
            # Check cache
            cache_key = f"analysis_{request.analysis_type}_{hash(request.content)}"
            cached_results = self.cache.get(cache_key)
            if cached_results:
                return ToolResponse(
                    success=True,
                    data=cached_results,
                    metadata={"cached": True}
                )

            # Perform analysis
            if request.analysis_type == "summary":
                results = await self.summarizer.analyze(
                    request.content,
                    parameters=request.parameters
                )
            elif request.analysis_type == "insights":
                results = await self.insight_extractor.analyze(
                    request.content,
                    parameters=request.parameters
                )
            elif request.analysis_type == "sentiment":
                results = await self.sentiment_analyzer.analyze(
                    request.content,
                    parameters=request.parameters
                )
            elif request.analysis_type == "topics":
                results = await self.topic_modeler.analyze(
                    request.content,
                    parameters=request.parameters
                )
            else:
                raise ValueError(f"Unsupported analysis type: {request.analysis_type}")

            # Create response
            analysis_result = AnalysisResult(
                summary=results.get("summary", ""),
                insights=results.get("insights", []),
                confidence=results.get("confidence", 0.0),
                metadata=results.get("metadata", {})
            )

            # Cache results
            self.cache.set(cache_key, analysis_result)

            return ToolResponse(
                success=True,
                data=analysis_result,
                metadata={"cached": False}
            )

        except Exception as e:
            logger.error(f"Error analyzing content: {str(e)}")
            return ToolResponse(
                success=False,
                error=str(e)
            )

    async def fact_check(
        self,
        request: FactCheckRequest
    ) -> ToolResponse:
        """
        Verify factual claims.

        Args:
            request: Fact-checking request parameters

        Returns:
            Fact-checking results
        """
        try:
            # Check cache
            cache_key = f"factcheck_{hash(request.claim)}"
            cached_results = self.cache.get(cache_key)
            if cached_results:
                return ToolResponse(
                    success=True,
                    data=cached_results,
                    metadata={"cached": True}
                )

            # Perform fact-checking
            results = await self.fact_checker.analyze(
                request.claim,
                context=request.context,
                sources=request.sources
            )

            # Create response
            fact_check_result = FactCheckResult(
                claim=request.claim,
                verdict=results["verdict"],
                confidence=results["confidence"],
                sources=results["sources"],
                explanation=results["explanation"]
            )

            # Cache results
            self.cache.set(cache_key, fact_check_result)

            return ToolResponse(
                success=True,
                data=fact_check_result,
                metadata={"cached": False}
            )

        except Exception as e:
            logger.error(f"Error fact-checking: {str(e)}")
            return ToolResponse(
                success=False,
                error=str(e)
            )

    async def batch_analyze(
        self,
        contents: List[str],
        analysis_type: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ToolResponse:
        """
        Analyze multiple content items in batch.

        Args:
            contents: List of content to analyze
            analysis_type: Type of analysis to perform
            parameters: Optional analysis parameters

        Returns:
            Batch analysis results
        """
        try:
            results = []
            for content in contents:
                request = AnalysisRequest(
                    content=content,
                    analysis_type=analysis_type,
                    parameters=parameters
                )
                result = await self.analyze_content(request)
                if result.success:
                    results.append(result.data)
                else:
                    logger.warning(f"Failed to analyze content: {result.error}")

            return ToolResponse(
                success=True,
                data=results
            )

        except Exception as e:
            logger.error(f"Error in batch analysis: {str(e)}")
            return ToolResponse(
                success=False,
                error=str(e)
            )

    async def compare_analyses(
        self,
        content1: str,
        content2: str,
        analysis_type: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ToolResponse:
        """
        Compare analyses of two content items.

        Args:
            content1: First content item
            content2: Second content item
            analysis_type: Type of analysis to perform
            parameters: Optional analysis parameters

        Returns:
            Comparison results
        """
        try:
            # Analyze both contents
            request1 = AnalysisRequest(
                content=content1,
                analysis_type=analysis_type,
                parameters=parameters
            )
            request2 = AnalysisRequest(
                content=content2,
                analysis_type=analysis_type,
                parameters=parameters
            )

            result1 = await self.analyze_content(request1)
            result2 = await self.analyze_content(request2)

            if not result1.success or not result2.success:
                raise ValueError("Failed to analyze one or both contents")

            # Compare results
            comparison = self._compare_results(
                result1.data,
                result2.data,
                analysis_type
            )

            return ToolResponse(
                success=True,
                data=comparison
            )

        except Exception as e:
            logger.error(f"Error comparing analyses: {str(e)}")
            return ToolResponse(
                success=False,
                error=str(e)
            )

    def _compare_results(
        self,
        result1: AnalysisResult,
        result2: AnalysisResult,
        analysis_type: str
    ) -> Dict[str, Any]:
        """
        Compare two analysis results.

        Args:
            result1: First analysis result
            result2: Second analysis result
            analysis_type: Type of analysis performed

        Returns:
            Comparison results
        """
        try:
            comparison = {
                "analysis_type": analysis_type,
                "timestamp": datetime.utcnow().isoformat()
            }

            if analysis_type == "sentiment":
                # Compare sentiment scores
                comparison["sentiment_diff"] = abs(
                    result1.metadata.get("sentiment_score", 0) -
                    result2.metadata.get("sentiment_score", 0)
                )
            elif analysis_type == "topics":
                # Compare topic distributions
                topics1 = result1.metadata.get("topics", {})
                topics2 = result2.metadata.get("topics", {})
                common_topics = set(topics1.keys()) & set(topics2.keys())
                comparison["common_topics"] = list(common_topics)
                comparison["topic_similarity"] = sum(
                    min(topics1[t], topics2[t])
                    for t in common_topics
                ) / max(sum(topics1.values()), sum(topics2.values()))
            else:
                # Compare insights
                insights1 = set(result1.insights)
                insights2 = set(result2.insights)
                comparison["common_insights"] = list(insights1 & insights2)
                comparison["unique_insights_1"] = list(insights1 - insights2)
                comparison["unique_insights_2"] = list(insights2 - insights1)

            return comparison

        except Exception as e:
            logger.error(f"Error comparing results: {str(e)}")
            raise 
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
from pathlib import Path

from research_assistant.tools.tool_schemas import (
    SearchQuery, SearchResult, ContentExtractionRequest, ExtractedContent,
    ToolResponse
)
from research_assistant.search.search_aggregator import SearchAggregator
from research_assistant.extraction.base_extractor import BaseExtractor
from research_assistant.storage.cache_manager import CacheManager
from research_assistant.storage.knowledge_graph import KnowledgeGraph
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class ResearchTools:
    """Core research tools for the MCP server."""

    def __init__(
        self,
        cache_dir: str = "data/cache",
        graph_dir: str = "data/knowledge_graphs"
    ):
        """
        Initialize research tools.

        Args:
            cache_dir: Directory for caching results
            graph_dir: Directory for knowledge graphs
        """
        self.cache = CacheManager(cache_dir)
        self.graph = KnowledgeGraph(graph_dir)
        self.search_aggregator = SearchAggregator()
        self.extractors: Dict[str, BaseExtractor] = {}

    async def search(
        self,
        query: SearchQuery
    ) -> ToolResponse:
        """
        Perform multi-source web search.

        Args:
            query: Search query parameters

        Returns:
            Search results
        """
        try:
            # Check cache
            cache_key = f"search_{query.query}_{query.max_results}"
            cached_results = self.cache.get(cache_key)
            if cached_results:
                return ToolResponse(
                    success=True,
                    data=cached_results,
                    metadata={"cached": True}
                )

            # Perform search
            results = await self.search_aggregator.search(
                query.query,
                max_results=query.max_results,
                sources=query.sources,
                filters=query.filters
            )

            # Cache results
            self.cache.set(cache_key, results)

            return ToolResponse(
                success=True,
                data=results,
                metadata={"cached": False}
            )

        except Exception as e:
            logger.error(f"Error performing search: {str(e)}")
            return ToolResponse(
                success=False,
                error=str(e)
            )

    async def extract_content(
        self,
        request: ContentExtractionRequest
    ) -> ToolResponse:
        """
        Extract content from web pages or documents.

        Args:
            request: Content extraction request

        Returns:
            Extracted content
        """
        try:
            # Get appropriate extractor
            extractor = self._get_extractor(request.extraction_type)
            if not extractor:
                raise ValueError(f"No extractor found for type: {request.extraction_type}")

            # Extract content
            if request.url:
                content = await extractor.extract_from_url(
                    request.url,
                    options=request.options
                )
            elif request.file_path:
                content = await extractor.extract_from_file(
                    request.file_path,
                    options=request.options
                )
            else:
                raise ValueError("Either URL or file path must be provided")

            # Create response
            result = ExtractedContent(
                content=content["text"],
                metadata=content["metadata"],
                source=request.url or request.file_path,
                extraction_time=datetime.utcnow()
            )

            return ToolResponse(
                success=True,
                data=result
            )

        except Exception as e:
            logger.error(f"Error extracting content: {str(e)}")
            return ToolResponse(
                success=False,
                error=str(e)
            )

    async def analyze_research(
        self,
        content: str,
        analysis_type: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ToolResponse:
        """
        Analyze research content.

        Args:
            content: Content to analyze
            analysis_type: Type of analysis to perform
            parameters: Optional analysis parameters

        Returns:
            Analysis results
        """
        try:
            # Store in knowledge graph
            doc = await self.graph.store(content, {
                "analysis_type": analysis_type,
                "parameters": parameters
            })

            # Perform analysis
            analysis_results = await self._perform_analysis(
                doc.id,
                analysis_type,
                parameters
            )

            return ToolResponse(
                success=True,
                data=analysis_results
            )

        except Exception as e:
            logger.error(f"Error analyzing research: {str(e)}")
            return ToolResponse(
                success=False,
                error=str(e)
            )

    async def verify_claims(
        self,
        claims: List[str],
        context: Optional[str] = None
    ) -> ToolResponse:
        """
        Verify factual claims.

        Args:
            claims: List of claims to verify
            context: Optional context for verification

        Returns:
            Verification results
        """
        try:
            results = []
            for claim in claims:
                # Search for supporting evidence
                search_results = await self.search_aggregator.search(
                    claim,
                    max_results=5,
                    sources=["duckduckgo", "searx"]
                )

                # Analyze evidence
                verification = await self._verify_claim(
                    claim,
                    search_results,
                    context
                )

                results.append(verification)

            return ToolResponse(
                success=True,
                data=results
            )

        except Exception as e:
            logger.error(f"Error verifying claims: {str(e)}")
            return ToolResponse(
                success=False,
                error=str(e)
            )

    def _get_extractor(self, extraction_type: str) -> Optional[BaseExtractor]:
        """
        Get appropriate extractor for content type.

        Args:
            extraction_type: Type of content to extract

        Returns:
            Content extractor or None if not found
        """
        if extraction_type not in self.extractors:
            # Initialize extractor
            extractor = self._initialize_extractor(extraction_type)
            if extractor:
                self.extractors[extraction_type] = extractor

        return self.extractors.get(extraction_type)

    def _initialize_extractor(self, extraction_type: str) -> Optional[BaseExtractor]:
        """
        Initialize content extractor.

        Args:
            extraction_type: Type of content to extract

        Returns:
            Initialized extractor or None if not supported
        """
        try:
            if extraction_type == "web":
                from research_assistant.extraction.web_extractor import WebExtractor
                return WebExtractor()
            elif extraction_type == "pdf":
                from research_assistant.extraction.pdf_extractor import PDFExtractor
                return PDFExtractor()
            elif extraction_type == "document":
                from research_assistant.extraction.document_extractor import DocumentExtractor
                return DocumentExtractor()
            else:
                logger.warning(f"Unsupported extraction type: {extraction_type}")
                return None

        except Exception as e:
            logger.error(f"Error initializing extractor: {str(e)}")
            return None

    async def _perform_analysis(
        self,
        doc_id: str,
        analysis_type: str,
        parameters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Perform content analysis.

        Args:
            doc_id: Document ID
            analysis_type: Type of analysis
            parameters: Analysis parameters

        Returns:
            Analysis results
        """
        try:
            # Get document from graph
            doc = await self.graph.get_document(doc_id)
            if not doc:
                raise ValueError(f"Document not found: {doc_id}")

            # Perform analysis based on type
            if analysis_type == "summary":
                from research_assistant.analysis.summarizer import Summarizer
                analyzer = Summarizer()
            elif analysis_type == "insights":
                from research_assistant.analysis.insight_extractor import InsightExtractor
                analyzer = InsightExtractor()
            elif analysis_type == "sentiment":
                from research_assistant.analysis.sentiment_analyzer import SentimentAnalyzer
                analyzer = SentimentAnalyzer()
            elif analysis_type == "topics":
                from research_assistant.analysis.topic_modeler import TopicModeler
                analyzer = TopicModeler()
            else:
                raise ValueError(f"Unsupported analysis type: {analysis_type}")

            # Analyze content
            results = await analyzer.analyze(doc["content"], parameters)

            # Update graph with results
            await self.graph.update_document(
                doc_id,
                metadata={"analysis_results": results}
            )

            return results

        except Exception as e:
            logger.error(f"Error performing analysis: {str(e)}")
            raise

    async def _verify_claim(
        self,
        claim: str,
        evidence: List[Dict[str, Any]],
        context: Optional[str]
    ) -> Dict[str, Any]:
        """
        Verify a claim against evidence.

        Args:
            claim: Claim to verify
            evidence: Supporting evidence
            context: Optional context

        Returns:
            Verification result
        """
        try:
            from research_assistant.analysis.fact_checker import FactChecker
            checker = FactChecker()

            # Check claim
            result = await checker.analyze(
                claim,
                context=context,
                evidence=evidence
            )

            return {
                "claim": claim,
                "verdict": result["verdict"],
                "confidence": result["confidence"],
                "sources": result["sources"],
                "explanation": result["explanation"]
            }

        except Exception as e:
            logger.error(f"Error verifying claim: {str(e)}")
            raise 
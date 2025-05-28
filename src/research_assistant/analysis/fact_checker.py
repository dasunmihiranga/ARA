from typing import Dict, Any, List, Optional
from datetime import datetime

from research_assistant.analysis.base_analyzer import BaseAnalyzer, AnalysisResult
from research_assistant.search.search_factory import SearchFactory
from research_assistant.extraction.extraction_factory import ExtractionFactory
from research_assistant.llm.ollama_client import OllamaClient
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class FactChecker(BaseAnalyzer):
    """Analyzer for verifying claims across multiple sources."""

    def __init__(
        self,
        model_name: str = "mistral",
        max_sources: int = 5,
        min_confidence: float = 0.7
    ):
        """
        Initialize the fact checker.

        Args:
            model_name: Name of the Ollama model to use
            max_sources: Maximum number of sources to check
            min_confidence: Minimum confidence threshold
        """
        super().__init__(
            name="fact_checker",
            description="Verify claims across multiple sources"
        )
        self.model_name = model_name
        self.max_sources = max_sources
        self.min_confidence = min_confidence
        self.ollama = OllamaClient(model_name=model_name)
        self.search_factory = SearchFactory()
        self.extraction_factory = ExtractionFactory()

    async def analyze(
        self,
        content: str,
        options: Optional[Dict[str, Any]] = None
    ) -> AnalysisResult:
        """
        Verify claims in the given content.

        Args:
            content: Content containing claims to verify
            options: Optional verification options including:
                - max_sources: Maximum number of sources to check
                - min_confidence: Minimum confidence threshold
                - search_engines: List of search engines to use
                - verification_depth: Depth of verification (basic, detailed)

        Returns:
            Analysis result containing verification results
        """
        try:
            # Validate content
            if not await self.validate_content(content):
                raise ValueError("Invalid content for fact checking")

            # Get options
            options = options or {}
            max_sources = options.get("max_sources", self.max_sources)
            min_confidence = options.get("min_confidence", self.min_confidence)
            search_engines = options.get("search_engines", ["duckduckgo", "searx"])
            verification_depth = options.get("verification_depth", "basic")

            # Extract claims
            claims = await self._extract_claims(content)
            if not claims:
                return AnalysisResult(
                    content="No verifiable claims found in the content.",
                    metadata={"status": "no_claims"}
                )

            # Verify each claim
            verification_results = []
            for claim in claims:
                result = await self._verify_claim(
                    claim=claim,
                    max_sources=max_sources,
                    min_confidence=min_confidence,
                    search_engines=search_engines,
                    verification_depth=verification_depth
                )
                verification_results.append(result)

            # Generate verification report
            report = await self._generate_report(verification_results)
            metadata = {
                "model": self.model_name,
                "max_sources": max_sources,
                "min_confidence": min_confidence,
                "search_engines": search_engines,
                "verification_depth": verification_depth,
                "total_claims": len(claims),
                "verified_claims": sum(1 for r in verification_results if r["verified"]),
                "verification_time": datetime.utcnow().isoformat()
            }

            return AnalysisResult(
                content=report,
                metadata=metadata
            )

        except Exception as e:
            logger.error(f"Error in fact checking: {str(e)}")
            raise

    async def batch_analyze(
        self,
        contents: List[str],
        options: Optional[Dict[str, Any]] = None
    ) -> List[AnalysisResult]:
        """
        Verify claims in multiple contents.

        Args:
            contents: List of contents to verify
            options: Optional verification options

        Returns:
            List of analysis results containing verification results
        """
        try:
            results = []
            for content in contents:
                result = await self.analyze(content, options)
                results.append(result)
            return results
        except Exception as e:
            logger.error(f"Error in batch fact checking: {str(e)}")
            raise

    async def validate_content(self, content: str) -> bool:
        """
        Validate if the content can be fact checked.

        Args:
            content: Content to validate

        Returns:
            True if content is valid, False otherwise
        """
        if not content or not isinstance(content, str):
            return False
        if len(content.strip()) < 20:  # Minimum content length
            return False
        return True

    async def close(self):
        """Close the fact checker and release resources."""
        try:
            await self.ollama.close()
            await self.search_factory.close_all()
            await self.extraction_factory.close_all()
        except Exception as e:
            logger.error(f"Error closing fact checker: {str(e)}")

    async def _extract_claims(self, content: str) -> List[str]:
        """
        Extract verifiable claims from content.

        Args:
            content: Content to extract claims from

        Returns:
            List of extracted claims
        """
        prompt = f"""Extract verifiable factual claims from the following content. Each claim should be a complete statement that can be verified against external sources.

Content:
{content}

Claims:"""
        
        response = await self.ollama.generate(prompt=prompt)
        claims = [claim.strip() for claim in response.split("\n") if claim.strip()]
        return claims

    async def _verify_claim(
        self,
        claim: str,
        max_sources: int,
        min_confidence: float,
        search_engines: List[str],
        verification_depth: str
    ) -> Dict[str, Any]:
        """
        Verify a single claim against multiple sources.

        Args:
            claim: Claim to verify
            max_sources: Maximum number of sources to check
            min_confidence: Minimum confidence threshold
            search_engines: List of search engines to use
            verification_depth: Depth of verification

        Returns:
            Dictionary containing verification results
        """
        # Search for sources
        sources = []
        for engine in search_engines:
            searcher = self.search_factory.get_searcher(engine)
            if searcher:
                results = await searcher.search(claim, limit=max_sources)
                sources.extend(results)

        # Extract content from sources
        source_contents = []
        for source in sources:
            extractor = self.extraction_factory.get_extractor("web")
            if extractor:
                try:
                    content = await extractor.extract(source.url)
                    source_contents.append({
                        "url": source.url,
                        "content": content.content,
                        "metadata": content.metadata
                    })
                except Exception as e:
                    logger.error(f"Error extracting content from {source.url}: {str(e)}")

        # Verify claim against sources
        verification_prompt = f"""Verify the following claim against the provided sources. Provide a confidence score (0-1) and explain your reasoning.

Claim: {claim}

Sources:
{self._format_sources(source_contents)}

Verification:"""
        
        response = await self.ollama.generate(prompt=verification_prompt)
        
        # Parse verification result
        try:
            confidence = float(response.split("Confidence:")[1].split("\n")[0].strip())
            explanation = response.split("Explanation:")[1].strip()
        except:
            confidence = 0.0
            explanation = "Failed to parse verification result"

        return {
            "claim": claim,
            "verified": confidence >= min_confidence,
            "confidence": confidence,
            "explanation": explanation,
            "sources": source_contents
        }

    async def _generate_report(self, verification_results: List[Dict[str, Any]]) -> str:
        """
        Generate a verification report.

        Args:
            verification_results: List of verification results

        Returns:
            Formatted verification report
        """
        report = "Fact Checking Report\n\n"
        
        for i, result in enumerate(verification_results, 1):
            report += f"Claim {i}: {result['claim']}\n"
            report += f"Status: {'Verified' if result['verified'] else 'Not Verified'}\n"
            report += f"Confidence: {result['confidence']:.2f}\n"
            report += f"Explanation: {result['explanation']}\n"
            report += f"Sources: {len(result['sources'])}\n\n"

        return report

    def _format_sources(self, sources: List[Dict[str, Any]]) -> str:
        """
        Format sources for verification prompt.

        Args:
            sources: List of source contents

        Returns:
            Formatted source string
        """
        formatted = ""
        for i, source in enumerate(sources, 1):
            formatted += f"Source {i}:\n"
            formatted += f"URL: {source['url']}\n"
            formatted += f"Content: {source['content'][:500]}...\n\n"
        return formatted 
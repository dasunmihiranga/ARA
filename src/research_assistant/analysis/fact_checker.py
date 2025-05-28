from typing import Dict, Any, List, Optional
import aiohttp
import asyncio
from datetime import datetime
import re
from urllib.parse import quote_plus

from research_assistant.analysis.base_analyzer import BaseAnalyzer, AnalysisResult, AnalysisOptions
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class FactChecker(BaseAnalyzer):
    """Verifies factual claims in content using external sources."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        max_claims: int = 10,
        min_confidence: float = 0.5
    ):
        """
        Initialize the fact checker.

        Args:
            api_key: API key for fact checking service
            max_claims: Maximum number of claims to check
            min_confidence: Minimum confidence threshold for claims
        """
        super().__init__(
            name="fact_checker",
            description="Verify factual claims in content"
        )
        self.api_key = api_key
        self.max_claims = max_claims
        self.min_confidence = min_confidence
        self.session = None

    async def _ensure_session(self) -> None:
        """Ensure aiohttp session is available."""
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def analyze(
        self,
        content: str,
        options: Optional[AnalysisOptions] = None
    ) -> AnalysisResult:
        """
        Check facts in the content.

        Args:
            content: Content to analyze
            options: Optional analysis options

        Returns:
            Analysis result with fact checks

        Raises:
            ValueError: If content is invalid
            Exception: For other analysis errors
        """
        if not await self.validate_content(content):
            raise ValueError("Invalid content for fact checking")

        options = options or AnalysisOptions()

        try:
            # Extract claims from content
            claims = self._extract_claims(content)
            if not claims:
                return self.format_result({
                    "content": content,
                    "claims": [],
                    "metadata": {"num_claims": 0},
                    "confidence": 1.0
                })

            # Limit number of claims
            claims = claims[:self.max_claims]

            # Check each claim
            results = []
            for claim in claims:
                result = await self._check_claim(claim)
                if result["confidence"] >= self.min_confidence:
                    results.append(result)

            # Calculate overall confidence
            confidence = self._calculate_confidence(results)

            return self.format_result({
                "content": content,
                "claims": results,
                "metadata": {
                    "num_claims": len(results),
                    "num_verified": sum(1 for r in results if r["verified"]),
                    "num_disputed": sum(1 for r in results if not r["verified"])
                },
                "confidence": confidence
            })

        except Exception as e:
            self.logger.error(f"Error checking facts: {str(e)}")
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

        # Check minimum content length
        if len(content.split()) < 10:
            return False

        return True

    def _extract_claims(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract factual claims from content.

        Args:
            content: Content to analyze

        Returns:
            List of claims with context
        """
        claims = []
        sentences = re.split(r'[.!?]+', content)

        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue

            # Look for factual statements
            if any(pattern in sentence.lower() for pattern in [
                "is", "are", "was", "were", "has", "have", "had",
                "according to", "research shows", "studies show",
                "experts say", "scientists found"
            ]):
                # Get context (previous and next sentences)
                context = []
                if i > 0:
                    context.append(sentences[i-1].strip())
                if i < len(sentences) - 1:
                    context.append(sentences[i+1].strip())

                claims.append({
                    "text": sentence,
                    "context": context,
                    "start": content.find(sentence),
                    "end": content.find(sentence) + len(sentence)
                })

        return claims

    async def _check_claim(self, claim: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check a single claim against external sources.

        Args:
            claim: Claim to check

        Returns:
            Dictionary with verification results
        """
        try:
            await self._ensure_session()

            # Prepare search query
            query = quote_plus(claim["text"])
            url = f"https://api.factcheck.org/v1/claims?q={query}"

            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._process_verification(data, claim)
                else:
                    return self._fallback_verification(claim)

        except Exception as e:
            self.logger.error(f"Error checking claim: {str(e)}")
            return self._fallback_verification(claim)

    def _process_verification(
        self,
        data: Dict[str, Any],
        claim: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process verification results from API.

        Args:
            data: API response data
            claim: Original claim

        Returns:
            Processed verification result
        """
        if not data.get("claims"):
            return self._fallback_verification(claim)

        # Get best matching claim
        best_match = max(
            data["claims"],
            key=lambda x: self._calculate_similarity(claim["text"], x["text"])
        )

        return {
            "text": claim["text"],
            "context": claim["context"],
            "verified": best_match["rating"] in ["true", "mostly_true"],
            "rating": best_match["rating"],
            "explanation": best_match.get("explanation", ""),
            "sources": best_match.get("sources", []),
            "confidence": self._calculate_similarity(claim["text"], best_match["text"]),
            "start": claim["start"],
            "end": claim["end"]
        }

    def _fallback_verification(self, claim: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback verification when API is unavailable.

        Args:
            claim: Claim to verify

        Returns:
            Basic verification result
        """
        return {
            "text": claim["text"],
            "context": claim["context"],
            "verified": None,
            "rating": "unknown",
            "explanation": "Unable to verify claim",
            "sources": [],
            "confidence": 0.0,
            "start": claim["start"],
            "end": claim["end"]
        }

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score between 0 and 1
        """
        # Simple word overlap similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)

    def _calculate_confidence(self, results: List[Dict[str, Any]]) -> float:
        """
        Calculate overall confidence in fact checking.

        Args:
            results: List of verification results

        Returns:
            Confidence score between 0 and 1
        """
        if not results:
            return 1.0

        # Factors that increase confidence:
        # - Number of claims checked
        # - Average confidence of individual checks
        # - Proportion of verified claims
        confidence = 0.0

        # Number of claims factor
        confidence += min(len(results) / self.max_claims, 1.0) * 0.3

        # Average confidence factor
        avg_confidence = sum(r["confidence"] for r in results) / len(results)
        confidence += avg_confidence * 0.4

        # Verification rate factor
        verified_rate = sum(1 for r in results if r["verified"] is not None) / len(results)
        confidence += verified_rate * 0.3

        return min(confidence, 1.0)

    async def close(self) -> None:
        """Close the fact checker."""
        if self.session:
            await self.session.close()
            self.session = None 
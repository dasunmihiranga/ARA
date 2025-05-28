from typing import Dict, Any, Optional, List
from datetime import datetime
import re
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from research_assistant.analysis.base_analyzer import BaseAnalyzer, AnalysisResult
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class FactChecker(BaseAnalyzer):
    """Fact checking analyzer implementation."""

    def __init__(self):
        """Initialize the fact checker."""
        super().__init__(
            name="fact_checker",
            description="Verify factual claims in text content"
        )
        self.llm = Ollama(model="mistral")
        self.claim_template = PromptTemplate(
            input_variables=["text"],
            template="""
            Extract factual claims from the following text. For each claim:
            1. Identify if it's a verifiable fact
            2. Note any specific numbers, dates, or statistics
            3. Highlight any causal relationships or comparisons

            Text: {text}

            Format each claim as a JSON object with:
            - claim: The factual statement
            - type: Type of claim (statistic, date, comparison, etc.)
            - confidence: Confidence level (high, medium, low)
            """
        )
        self.verification_template = PromptTemplate(
            input_variables=["claim"],
            template="""
            Verify the following claim and provide:
            1. Whether it's likely true, false, or uncertain
            2. Reasoning for the assessment
            3. What additional information would be needed for certainty

            Claim: {claim}

            Format the response as a JSON object with:
            - verdict: true/false/uncertain
            - reasoning: Explanation
            - needed_info: Additional information needed
            """
        )

    async def analyze(
        self,
        content: str,
        options: Optional[Dict[str, Any]] = None
    ) -> AnalysisResult:
        """
        Check facts in the content.

        Args:
            content: Content to analyze
            options: Optional fact checking options including:
                - min_confidence: Minimum confidence level to include
                - max_claims: Maximum number of claims to check

        Returns:
            Analysis result containing fact checks
        """
        options = options or {}
        min_confidence = options.get("min_confidence", "medium")
        max_claims = options.get("max_claims", 5)

        try:
            # Extract claims
            claim_chain = LLMChain(llm=self.llm, prompt=self.claim_template)
            claims_response = await claim_chain.arun(text=content)
            
            # Parse claims
            claims = self._parse_claims(claims_response)
            
            # Filter claims by confidence
            confidence_levels = {"high": 3, "medium": 2, "low": 1}
            min_level = confidence_levels.get(min_confidence.lower(), 2)
            claims = [
                c for c in claims 
                if confidence_levels.get(c.get("confidence", "").lower(), 0) >= min_level
            ][:max_claims]

            # Verify claims
            verification_chain = LLMChain(llm=self.llm, prompt=self.verification_template)
            facts = []
            
            for claim in claims:
                verification = await verification_chain.arun(claim=claim["claim"])
                fact = self._parse_verification(verification)
                if fact:
                    facts.append({
                        "claim": claim["claim"],
                        "type": claim["type"],
                        "verification": fact
                    })

            return AnalysisResult(
                content=content,
                facts=facts,
                metadata={
                    "min_confidence": min_confidence,
                    "max_claims": max_claims,
                    "claims_checked": len(facts),
                    "confidence_levels": confidence_levels
                },
                analyzed_at=datetime.utcnow()
            )

        except Exception as e:
            logger.error(f"Fact checking error: {str(e)}")
            raise

    def _parse_claims(self, response: str) -> List[Dict[str, Any]]:
        """
        Parse claims from LLM response.

        Args:
            response: LLM response containing claims

        Returns:
            List of parsed claims
        """
        try:
            # Extract JSON objects from response
            json_pattern = r'\{[^{}]*\}'
            matches = re.finditer(json_pattern, response)
            
            claims = []
            for match in matches:
                try:
                    # Parse JSON-like string
                    claim_str = match.group()
                    # Convert to proper JSON format
                    claim_str = claim_str.replace("'", '"')
                    import json
                    claim = json.loads(claim_str)
                    claims.append(claim)
                except:
                    continue
                    
            return claims
        except Exception as e:
            logger.error(f"Error parsing claims: {str(e)}")
            return []

    def _parse_verification(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Parse verification result from LLM response.

        Args:
            response: LLM response containing verification

        Returns:
            Parsed verification result or None if parsing fails
        """
        try:
            # Extract JSON object from response
            json_pattern = r'\{[^{}]*\}'
            match = re.search(json_pattern, response)
            
            if match:
                # Parse JSON-like string
                verification_str = match.group()
                # Convert to proper JSON format
                verification_str = verification_str.replace("'", '"')
                import json
                return json.loads(verification_str)
                
            return None
        except Exception as e:
            logger.error(f"Error parsing verification: {str(e)}")
            return None 
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field

from research_assistant.llm.model_manager import ModelManager
from research_assistant.llm.prompt_templates import PromptTemplateManager
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class SentimentResult(BaseModel):
    """Model for sentiment analysis results."""
    sentiment: str = Field(..., description="Overall sentiment (positive, negative, neutral)")
    score: float = Field(..., description="Sentiment score (-1.0 to 1.0)")
    confidence: float = Field(..., description="Confidence score (0.0 to 1.0)")
    aspects: List[Dict[str, Any]] = Field(default_factory=list, description="Aspect-based sentiment analysis")
    emotions: Dict[str, float] = Field(default_factory=dict, description="Emotion scores")

class SentimentAnalyzer:
    """Analyzer for text sentiment."""

    def __init__(
        self,
        model_name: str = "mistral",
        config_path: Optional[str] = None
    ):
        """
        Initialize the sentiment analyzer.

        Args:
            model_name: Name of the model to use
            config_path: Path to the configuration file
        """
        self.model_name = model_name
        self.model_manager = ModelManager(config_path)
        self.template_manager = PromptTemplateManager()
        self.logger = get_logger("sentiment_analyzer")

    async def analyze(
        self,
        text: str,
        aspects: Optional[List[str]] = None,
        include_emotions: bool = True
    ) -> SentimentResult:
        """
        Analyze sentiment in text.

        Args:
            text: Text to analyze
            aspects: Optional list of aspects to analyze
            include_emotions: Whether to include emotion analysis

        Returns:
            SentimentResult object
        """
        try:
            # Load model
            model = await self.model_manager.load_model(self.model_name)
            if not model:
                raise ValueError(f"Failed to load model: {self.model_name}")

            # Prepare prompt
            prompt = self._prepare_prompt(text, aspects, include_emotions)

            # Generate analysis
            response = await model.generate(
                prompt=prompt,
                temperature=0.3,
                max_tokens=1000
            )

            # Parse response
            result = self._parse_response(response)

            return SentimentResult(**result)

        except Exception as e:
            self.logger.error(f"Error analyzing sentiment: {str(e)}")
            raise

    async def batch_analyze(
        self,
        texts: List[str],
        aspects: Optional[List[str]] = None,
        include_emotions: bool = True
    ) -> List[SentimentResult]:
        """
        Analyze sentiment in multiple texts.

        Args:
            texts: List of texts to analyze
            aspects: Optional list of aspects to analyze
            include_emotions: Whether to include emotion analysis

        Returns:
            List of SentimentResult objects
        """
        results = []
        for text in texts:
            try:
                result = await self.analyze(text, aspects, include_emotions)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error analyzing text: {str(e)}")
                results.append(None)
        return results

    def _prepare_prompt(
        self,
        text: str,
        aspects: Optional[List[str]],
        include_emotions: bool
    ) -> str:
        """
        Prepare the analysis prompt.

        Args:
            text: Text to analyze
            aspects: Optional list of aspects
            include_emotions: Whether to include emotions

        Returns:
            Formatted prompt
        """
        prompt = f"""Analyze the sentiment of the following text:

Text:
{text}

Please provide:
1. Overall sentiment (positive, negative, or neutral)
2. Sentiment score (-1.0 to 1.0)
3. Confidence score (0.0 to 1.0)
"""

        if aspects:
            prompt += "\n4. Aspect-based sentiment analysis for:\n"
            for aspect in aspects:
                prompt += f"- {aspect}\n"

        if include_emotions:
            prompt += "\n5. Emotion scores for:\n"
            prompt += "- joy\n- sadness\n- anger\n- fear\n- surprise\n- disgust\n"

        prompt += "\nFormat the response as JSON."

        return prompt

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the model response.

        Args:
            response: Model response

        Returns:
            Parsed sentiment analysis results
        """
        try:
            # Extract JSON from response
            import json
            import re

            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))

            return json.loads(response)

        except Exception as e:
            self.logger.error(f"Error parsing response: {str(e)}")
            raise

    async def close(self):
        """Close the sentiment analyzer."""
        await self.model_manager.close() 
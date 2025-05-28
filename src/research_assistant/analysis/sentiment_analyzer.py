from typing import Dict, Any, List, Optional
from transformers import pipeline
import asyncio
from datetime import datetime
import re

from research_assistant.analysis.base_analyzer import BaseAnalyzer, AnalysisResult, AnalysisOptions
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class SentimentAnalyzer(BaseAnalyzer):
    """Analyzes sentiment in content using transformer models."""

    def __init__(
        self,
        model_name: str = "finiteautomata/bertweet-base-sentiment-analysis",
        max_length: int = 512,
        batch_size: int = 32
    ):
        """
        Initialize the sentiment analyzer.

        Args:
            model_name: Name of the sentiment analysis model
            max_length: Maximum sequence length
            batch_size: Batch size for processing
        """
        super().__init__(
            name="sentiment_analyzer",
            description="Analyze sentiment in content"
        )
        self.model_name = model_name
        self.max_length = max_length
        self.batch_size = batch_size
        self.analyzer = None
        self._load_model()

    def _load_model(self) -> None:
        """Load the sentiment analysis model."""
        try:
            self.analyzer = pipeline(
                "sentiment-analysis",
                model=self.model_name,
                device=0 if asyncio.get_event_loop().is_running() else -1
            )
        except Exception as e:
            self.logger.error(f"Error loading sentiment model: {str(e)}")
            raise

    async def analyze(
        self,
        content: str,
        options: Optional[AnalysisOptions] = None
    ) -> AnalysisResult:
        """
        Analyze sentiment in the content.

        Args:
            content: Content to analyze
            options: Optional analysis options

        Returns:
            Analysis result with sentiment scores

        Raises:
            ValueError: If content is invalid
            Exception: For other analysis errors
        """
        if not await self.validate_content(content):
            raise ValueError("Invalid content for sentiment analysis")

        options = options or AnalysisOptions()

        try:
            # Split content into sentences
            sentences = self._split_sentences(content)
            if not sentences:
                return self.format_result({
                    "content": content,
                    "sentiment": {
                        "overall": {"positive": 0.5, "negative": 0.5, "neutral": 1.0},
                        "sentences": []
                    },
                    "metadata": {"num_sentences": 0},
                    "confidence": 1.0
                })

            # Analyze sentiment in batches
            results = []
            for i in range(0, len(sentences), self.batch_size):
                batch = sentences[i:i + self.batch_size]
                batch_results = self.analyzer(
                    batch,
                    truncation=True,
                    max_length=self.max_length
                )
                results.extend(batch_results)

            # Process results
            sentiment_scores = self._process_results(sentences, results)
            overall_sentiment = self._calculate_overall_sentiment(sentiment_scores)
            confidence = self._calculate_confidence(sentiment_scores)

            return self.format_result({
                "content": content,
                "sentiment": {
                    "overall": overall_sentiment,
                    "sentences": sentiment_scores
                },
                "metadata": {
                    "model": self.model_name,
                    "num_sentences": len(sentences),
                    "batch_size": self.batch_size
                },
                "confidence": confidence
            })

        except Exception as e:
            self.logger.error(f"Error analyzing sentiment: {str(e)}")
            raise

    async def validate_content(self, content: str) -> bool:
        """
        Validate if the content can be analyzed.

        Args:
            content: Content to validate

        Returns:
            True if content is valid, False otherwise
        """
        if not content or not isinstance(content, str):
            return False

        # Check minimum content length
        if len(content.split()) < 3:
            return False

        return True

    def _split_sentences(self, content: str) -> List[str]:
        """
        Split content into sentences.

        Args:
            content: Content to split

        Returns:
            List of sentences
        """
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', content)
        return [s.strip() for s in sentences if s.strip()]

    def _process_results(
        self,
        sentences: List[str],
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Process sentiment analysis results.

        Args:
            sentences: List of sentences
            results: List of analysis results

        Returns:
            List of processed sentiment scores
        """
        processed = []
        for sentence, result in zip(sentences, results):
            # Convert label to score
            label = result["label"].lower()
            score = result["score"]

            sentiment = {
                "positive": 0.0,
                "negative": 0.0,
                "neutral": 0.0
            }

            if label == "positive":
                sentiment["positive"] = score
                sentiment["neutral"] = 1 - score
            elif label == "negative":
                sentiment["negative"] = score
                sentiment["neutral"] = 1 - score
            else:  # neutral
                sentiment["neutral"] = score
                sentiment["positive"] = (1 - score) / 2
                sentiment["negative"] = (1 - score) / 2

            processed.append({
                "text": sentence,
                "sentiment": sentiment,
                "confidence": score
            })

        return processed

    def _calculate_overall_sentiment(
        self,
        sentiment_scores: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Calculate overall sentiment scores.

        Args:
            sentiment_scores: List of sentence sentiment scores

        Returns:
            Dictionary with overall sentiment scores
        """
        if not sentiment_scores:
            return {"positive": 0.5, "negative": 0.5, "neutral": 1.0}

        # Weight scores by confidence
        total_weight = 0.0
        weighted_scores = {
            "positive": 0.0,
            "negative": 0.0,
            "neutral": 0.0
        }

        for score in sentiment_scores:
            weight = score["confidence"]
            total_weight += weight
            for key in weighted_scores:
                weighted_scores[key] += score["sentiment"][key] * weight

        # Normalize scores
        if total_weight > 0:
            for key in weighted_scores:
                weighted_scores[key] /= total_weight

        return weighted_scores

    def _calculate_confidence(
        self,
        sentiment_scores: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate confidence in sentiment analysis.

        Args:
            sentiment_scores: List of sentiment scores

        Returns:
            Confidence score between 0 and 1
        """
        if not sentiment_scores:
            return 1.0

        # Factors that increase confidence:
        # - Number of sentences analyzed
        # - Average confidence of individual analyses
        # - Consistency of sentiment across sentences
        confidence = 0.0

        # Number of sentences factor
        confidence += min(len(sentiment_scores) / 10, 1.0) * 0.3

        # Average confidence factor
        avg_confidence = sum(s["confidence"] for s in sentiment_scores) / len(sentiment_scores)
        confidence += avg_confidence * 0.4

        # Consistency factor
        if len(sentiment_scores) > 1:
            sentiments = [max(s["sentiment"].items(), key=lambda x: x[1])[0] for s in sentiment_scores]
            most_common = max(set(sentiments), key=sentiments.count)
            consistency = sentiments.count(most_common) / len(sentiments)
            confidence += consistency * 0.3

        return min(confidence, 1.0)

    async def close(self) -> None:
        """Close the sentiment analyzer."""
        self.analyzer = None 
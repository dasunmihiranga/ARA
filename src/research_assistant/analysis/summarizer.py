from typing import Dict, Any, List, Optional
import asyncio
from transformers import pipeline
import nltk
from nltk.tokenize import sent_tokenize
import langdetect
from datetime import datetime

from research_assistant.analysis.base_analyzer import BaseAnalyzer, AnalysisResult, AnalysisOptions
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class Summarizer(BaseAnalyzer):
    """Content summarization implementation."""

    def __init__(
        self,
        model_name: str = "facebook/bart-large-cnn",
        max_length: int = 130,
        min_length: int = 30,
        num_beams: int = 4
    ):
        """
        Initialize the summarizer.

        Args:
            model_name: Name of the summarization model
            max_length: Maximum summary length
            min_length: Minimum summary length
            num_beams: Number of beams for beam search
        """
        super().__init__(
            name="summarizer",
            description="Generate concise summaries of content"
        )
        self.model_name = model_name
        self.max_length = max_length
        self.min_length = min_length
        self.num_beams = num_beams
        self.summarizer = None
        self._ensure_nltk()

    def _ensure_nltk(self) -> None:
        """Ensure NLTK resources are downloaded."""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')

    async def _load_model(self) -> None:
        """Load the summarization model."""
        if not self.summarizer:
            try:
                self.summarizer = pipeline(
                    "summarization",
                    model=self.model_name,
                    device=0 if asyncio.get_event_loop().is_running() else -1
                )
            except Exception as e:
                self.logger.error(f"Error loading summarization model: {str(e)}")
                raise

    async def analyze(
        self,
        content: str,
        options: Optional[AnalysisOptions] = None
    ) -> AnalysisResult:
        """
        Generate a summary of the content.

        Args:
            content: Content to summarize
            options: Optional analysis options

        Returns:
            Analysis result with summary

        Raises:
            ValueError: If content is invalid
            Exception: For other analysis errors
        """
        if not await self.validate_content(content):
            raise ValueError("Invalid content for summarization")

        options = options or AnalysisOptions()

        try:
            # Load model if needed
            await self._load_model()

            # Detect language
            try:
                language = langdetect.detect(content)
            except:
                language = None

            # Split content into chunks if needed
            chunks = self._split_content(content, options.max_tokens)
            summaries = []

            # Generate summary for each chunk
            for chunk in chunks:
                summary = self.summarizer(
                    chunk,
                    max_length=min(self.max_length, len(chunk.split())),
                    min_length=self.min_length,
                    num_beams=self.num_beams,
                    do_sample=False
                )[0]['summary_text']
                summaries.append(summary)

            # Combine summaries
            final_summary = " ".join(summaries)

            # Extract key insights
            insights = self._extract_insights(content, final_summary)

            return self.format_result({
                "content": content,
                "summary": final_summary,
                "insights": insights,
                "metadata": {
                    "model": self.model_name,
                    "num_chunks": len(chunks),
                    "language": language
                },
                "confidence": self._calculate_confidence(content, final_summary),
                "language": language
            })

        except Exception as e:
            self.logger.error(f"Error summarizing content: {str(e)}")
            raise

    async def validate_content(self, content: str) -> bool:
        """
        Validate if the content can be summarized.

        Args:
            content: Content to validate

        Returns:
            True if content is valid, False otherwise
        """
        if not content or not isinstance(content, str):
            return False

        # Check minimum content length
        if len(content.split()) < self.min_length:
            return False

        return True

    def _split_content(self, content: str, max_tokens: Optional[int] = None) -> List[str]:
        """
        Split content into chunks.

        Args:
            content: Content to split
            max_tokens: Maximum tokens per chunk

        Returns:
            List of content chunks
        """
        if not max_tokens:
            return [content]

        sentences = sent_tokenize(content)
        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence.split())
            if current_length + sentence_length > max_tokens:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def _extract_insights(self, content: str, summary: str) -> List[str]:
        """
        Extract key insights from content and summary.

        Args:
            content: Original content
            summary: Generated summary

        Returns:
            List of key insights
        """
        insights = []
        sentences = sent_tokenize(content)

        # Extract sentences that appear in summary
        summary_sentences = set(summary.lower().split())
        for sentence in sentences:
            words = set(sentence.lower().split())
            if len(words.intersection(summary_sentences)) / len(words) > 0.5:
                insights.append(sentence)

        return insights

    def _calculate_confidence(self, content: str, summary: str) -> float:
        """
        Calculate confidence score for the summary.

        Args:
            content: Original content
            summary: Generated summary

        Returns:
            Confidence score (0-1)
        """
        # Calculate compression ratio
        content_words = len(content.split())
        summary_words = len(summary.split())
        compression_ratio = summary_words / content_words

        # Calculate word overlap
        content_words = set(content.lower().split())
        summary_words = set(summary.lower().split())
        word_overlap = len(content_words.intersection(summary_words)) / len(content_words)

        # Combine scores
        confidence = (compression_ratio + word_overlap) / 2
        return min(max(confidence, 0.0), 1.0)

    async def close(self) -> None:
        """Close the summarizer."""
        self.summarizer = None 
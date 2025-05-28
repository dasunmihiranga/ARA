from typing import Dict, Any, List, Optional
import spacy
from collections import Counter
import networkx as nx
from datetime import datetime
import re

from research_assistant.analysis.base_analyzer import BaseAnalyzer, AnalysisResult, AnalysisOptions
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class InsightExtractor(BaseAnalyzer):
    """Extracts key insights and patterns from content."""

    def __init__(
        self,
        model_name: str = "en_core_web_sm",
        min_confidence: float = 0.5,
        max_insights: int = 10
    ):
        """
        Initialize the insight extractor.

        Args:
            model_name: Name of the spaCy model to use
            min_confidence: Minimum confidence threshold for insights
            max_insights: Maximum number of insights to extract
        """
        super().__init__(
            name="insight_extractor",
            description="Extract key insights and patterns from content"
        )
        self.model_name = model_name
        self.min_confidence = min_confidence
        self.max_insights = max_insights
        self.nlp = None
        self._load_model()

    def _load_model(self) -> None:
        """Load the spaCy model."""
        try:
            self.nlp = spacy.load(self.model_name)
        except OSError:
            self.logger.info(f"Downloading spaCy model: {self.model_name}")
            spacy.cli.download(self.model_name)
            self.nlp = spacy.load(self.model_name)

    async def analyze(
        self,
        content: str,
        options: Optional[AnalysisOptions] = None
    ) -> AnalysisResult:
        """
        Extract insights from the content.

        Args:
            content: Content to analyze
            options: Optional analysis options

        Returns:
            Analysis result with insights

        Raises:
            ValueError: If content is invalid
            Exception: For other analysis errors
        """
        if not await self.validate_content(content):
            raise ValueError("Invalid content for insight extraction")

        options = options or AnalysisOptions()

        try:
            # Process content with spaCy
            doc = self.nlp(content)

            # Extract various insights
            entities = self._extract_entities(doc)
            key_phrases = self._extract_key_phrases(doc)
            topics = self._extract_topics(doc)
            relationships = self._extract_relationships(doc)
            sentiment = self._analyze_sentiment(doc)

            # Calculate confidence scores
            confidence = self._calculate_confidence(doc, entities, key_phrases)

            return self.format_result({
                "content": content,
                "insights": {
                    "entities": entities,
                    "key_phrases": key_phrases,
                    "topics": topics,
                    "relationships": relationships,
                    "sentiment": sentiment
                },
                "metadata": {
                    "model": self.model_name,
                    "num_entities": len(entities),
                    "num_phrases": len(key_phrases),
                    "num_topics": len(topics)
                },
                "confidence": confidence
            })

        except Exception as e:
            self.logger.error(f"Error extracting insights: {str(e)}")
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
        if len(content.split()) < 10:
            return False

        return True

    def _extract_entities(self, doc) -> List[Dict[str, Any]]:
        """
        Extract named entities from the document.

        Args:
            doc: spaCy document

        Returns:
            List of entities with their types and counts
        """
        entities = []
        for ent in doc.ents:
            if ent.label_ not in ['DATE', 'TIME', 'PERCENT', 'MONEY', 'QUANTITY']:
                entities.append({
                    "text": ent.text,
                    "type": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "confidence": ent._.confidence if hasattr(ent._, 'confidence') else 1.0
                })
        return entities

    def _extract_key_phrases(self, doc) -> List[Dict[str, Any]]:
        """
        Extract key phrases from the document.

        Args:
            doc: spaCy document

        Returns:
            List of key phrases with their scores
        """
        phrases = []
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) > 1:
                phrases.append({
                    "text": chunk.text,
                    "root": chunk.root.text,
                    "dependency": chunk.root.dep_,
                    "score": self._calculate_phrase_score(chunk)
                })
        return sorted(phrases, key=lambda x: x["score"], reverse=True)[:self.max_insights]

    def _extract_topics(self, doc) -> List[Dict[str, Any]]:
        """
        Extract main topics from the document.

        Args:
            doc: spaCy document

        Returns:
            List of topics with their frequencies
        """
        # Count noun frequencies
        noun_freq = Counter()
        for token in doc:
            if token.pos_ in ['NOUN', 'PROPN'] and not token.is_stop:
                noun_freq[token.lemma_] += 1

        # Get top topics
        topics = []
        for topic, freq in noun_freq.most_common(self.max_insights):
            topics.append({
                "text": topic,
                "frequency": freq,
                "score": freq / len(doc)
            })
        return topics

    def _extract_relationships(self, doc) -> List[Dict[str, Any]]:
        """
        Extract relationships between entities.

        Args:
            doc: spaCy document

        Returns:
            List of relationships between entities
        """
        relationships = []
        for token in doc:
            if token.dep_ in ['nsubj', 'dobj'] and token.head.pos_ == 'VERB':
                relationships.append({
                    "subject": token.text,
                    "verb": token.head.text,
                    "object": next((t.text for t in token.head.children if t.dep_ == 'dobj'), None)
                })
        return relationships

    def _analyze_sentiment(self, doc) -> Dict[str, float]:
        """
        Analyze sentiment of the document.

        Args:
            doc: spaCy document

        Returns:
            Dictionary with sentiment scores
        """
        # Simple sentiment analysis based on positive/negative words
        positive_words = {'good', 'great', 'excellent', 'positive', 'happy', 'best'}
        negative_words = {'bad', 'poor', 'negative', 'unhappy', 'worst', 'terrible'}

        positive_count = sum(1 for token in doc if token.text.lower() in positive_words)
        negative_count = sum(1 for token in doc if token.text.lower() in negative_words)
        total = positive_count + negative_count

        if total == 0:
            return {"positive": 0.5, "negative": 0.5, "neutral": 1.0}

        return {
            "positive": positive_count / total,
            "negative": negative_count / total,
            "neutral": 1 - (positive_count + negative_count) / len(doc)
        }

    def _calculate_phrase_score(self, chunk) -> float:
        """
        Calculate importance score for a phrase.

        Args:
            chunk: spaCy noun chunk

        Returns:
            Score between 0 and 1
        """
        # Factors that increase score:
        # - Length of phrase
        # - Presence of proper nouns
        # - Position in sentence
        score = 0.0

        # Length factor
        score += min(len(chunk.text.split()) / 5, 1.0) * 0.3

        # Proper noun factor
        proper_nouns = sum(1 for token in chunk if token.pos_ == 'PROPN')
        score += (proper_nouns / len(chunk)) * 0.3

        # Position factor
        if chunk.start == 0:  # Start of sentence
            score += 0.4

        return min(score, 1.0)

    def _calculate_confidence(
        self,
        doc,
        entities: List[Dict[str, Any]],
        key_phrases: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate confidence score for the analysis.

        Args:
            doc: spaCy document
            entities: Extracted entities
            key_phrases: Extracted key phrases

        Returns:
            Confidence score between 0 and 1
        """
        # Factors that increase confidence:
        # - Number of entities found
        # - Quality of key phrases
        # - Document length
        confidence = 0.0

        # Entity factor
        if entities:
            confidence += min(len(entities) / 10, 1.0) * 0.4

        # Key phrase factor
        if key_phrases:
            avg_phrase_score = sum(p["score"] for p in key_phrases) / len(key_phrases)
            confidence += avg_phrase_score * 0.3

        # Length factor
        confidence += min(len(doc) / 1000, 1.0) * 0.3

        return min(confidence, 1.0)

    async def close(self) -> None:
        """Close the insight extractor."""
        self.nlp = None 
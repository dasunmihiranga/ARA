from typing import Dict, Any, List, Optional
import spacy
from gensim import corpora, models
import numpy as np
from datetime import datetime
import re
from collections import Counter

from research_assistant.analysis.base_analyzer import BaseAnalyzer, AnalysisResult, AnalysisOptions
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class TopicModeler(BaseAnalyzer):
    """Identifies and analyzes topics in content using LDA."""

    def __init__(
        self,
        model_name: str = "en_core_web_sm",
        num_topics: int = 5,
        passes: int = 10,
        min_topic_size: int = 3
    ):
        """
        Initialize the topic modeler.

        Args:
            model_name: Name of the spaCy model to use
            num_topics: Number of topics to extract
            passes: Number of passes for LDA training
            min_topic_size: Minimum number of words per topic
        """
        super().__init__(
            name="topic_modeler",
            description="Identify and analyze topics in content"
        )
        self.model_name = model_name
        self.num_topics = num_topics
        self.passes = passes
        self.min_topic_size = min_topic_size
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
        Identify topics in the content.

        Args:
            content: Content to analyze
            options: Optional analysis options

        Returns:
            Analysis result with topics

        Raises:
            ValueError: If content is invalid
            Exception: For other analysis errors
        """
        if not await self.validate_content(content):
            raise ValueError("Invalid content for topic modeling")

        options = options or AnalysisOptions()

        try:
            # Process content with spaCy
            doc = self.nlp(content)

            # Extract and preprocess text
            sentences = [sent.text.strip() for sent in doc.sents]
            if not sentences:
                return self.format_result({
                    "content": content,
                    "topics": [],
                    "metadata": {"num_sentences": 0},
                    "confidence": 1.0
                })

            # Prepare documents for LDA
            processed_docs = self._preprocess_documents(sentences)
            if not processed_docs:
                return self.format_result({
                    "content": content,
                    "topics": [],
                    "metadata": {"num_sentences": len(sentences)},
                    "confidence": 1.0
                })

            # Create dictionary and corpus
            dictionary = corpora.Dictionary(processed_docs)
            corpus = [dictionary.doc2bow(doc) for doc in processed_docs]

            # Train LDA model
            lda_model = models.LdaModel(
                corpus=corpus,
                num_topics=self.num_topics,
                id2word=dictionary,
                passes=self.passes
            )

            # Extract topics
            topics = self._extract_topics(lda_model, dictionary)
            topic_distribution = self._calculate_topic_distribution(lda_model, corpus)
            coherence = self._calculate_coherence(lda_model, corpus, dictionary)

            return self.format_result({
                "content": content,
                "topics": topics,
                "distribution": topic_distribution,
                "metadata": {
                    "model": "LDA",
                    "num_topics": len(topics),
                    "num_sentences": len(sentences),
                    "coherence": coherence
                },
                "confidence": coherence
            })

        except Exception as e:
            self.logger.error(f"Error modeling topics: {str(e)}")
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
        if len(content.split()) < 20:
            return False

        return True

    def _preprocess_documents(self, sentences: List[str]) -> List[List[str]]:
        """
        Preprocess documents for topic modeling.

        Args:
            sentences: List of sentences

        Returns:
            List of preprocessed documents
        """
        processed_docs = []
        for sentence in sentences:
            # Process with spaCy
            doc = self.nlp(sentence)

            # Extract tokens
            tokens = [
                token.lemma_.lower()
                for token in doc
                if not token.is_stop
                and not token.is_punct
                and not token.is_space
                and len(token.text) > 2
            ]

            if len(tokens) >= self.min_topic_size:
                processed_docs.append(tokens)

        return processed_docs

    def _extract_topics(
        self,
        lda_model: models.LdaModel,
        dictionary: corpora.Dictionary
    ) -> List[Dict[str, Any]]:
        """
        Extract topics from the LDA model.

        Args:
            lda_model: Trained LDA model
            dictionary: Gensim dictionary

        Returns:
            List of topics with their words and scores
        """
        topics = []
        for topic_id in range(lda_model.num_topics):
            # Get topic words
            topic_words = lda_model.show_topic(topic_id, topn=10)
            
            # Calculate topic coherence
            words = [word for word, _ in topic_words]
            coherence = self._calculate_topic_coherence(words)

            topics.append({
                "id": topic_id,
                "words": [
                    {
                        "word": word,
                        "score": float(score)
                    }
                    for word, score in topic_words
                ],
                "coherence": coherence
            })

        return topics

    def _calculate_topic_distribution(
        self,
        lda_model: models.LdaModel,
        corpus: List[List[tuple]]
    ) -> List[Dict[str, Any]]:
        """
        Calculate topic distribution across documents.

        Args:
            lda_model: Trained LDA model
            corpus: Document corpus

        Returns:
            List of topic distributions
        """
        distributions = []
        for doc in corpus:
            # Get document topics
            doc_topics = lda_model.get_document_topics(doc)
            
            # Convert to dictionary
            topic_dist = {
                topic_id: float(score)
                for topic_id, score in doc_topics
            }
            
            distributions.append(topic_dist)

        return distributions

    def _calculate_coherence(
        self,
        lda_model: models.LdaModel,
        corpus: List[List[tuple]],
        dictionary: corpora.Dictionary
    ) -> float:
        """
        Calculate model coherence score.

        Args:
            lda_model: Trained LDA model
            corpus: Document corpus
            dictionary: Gensim dictionary

        Returns:
            Coherence score between 0 and 1
        """
        try:
            # Calculate topic coherence
            coherence_model = models.CoherenceModel(
                model=lda_model,
                texts=corpus,
                dictionary=dictionary,
                coherence='c_v'
            )
            coherence = coherence_model.get_coherence()
            return min(max(coherence, 0.0), 1.0)
        except:
            return 0.0

    def _calculate_topic_coherence(self, words: List[str]) -> float:
        """
        Calculate coherence for a single topic.

        Args:
            words: List of topic words

        Returns:
            Coherence score between 0 and 1
        """
        if not words:
            return 0.0

        # Simple word co-occurrence based coherence
        co_occurrences = 0
        total_pairs = 0

        for i in range(len(words)):
            for j in range(i + 1, len(words)):
                total_pairs += 1
                # Check if words appear together in any sentence
                if any(
                    words[i] in sent.lower() and words[j] in sent.lower()
                    for sent in self.nlp.vocab.strings
                ):
                    co_occurrences += 1

        return co_occurrences / total_pairs if total_pairs > 0 else 0.0

    async def close(self) -> None:
        """Close the topic modeler."""
        self.nlp = None 
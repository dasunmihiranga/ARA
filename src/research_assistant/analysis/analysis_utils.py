from typing import Dict, Any, List, Optional, Union
import re
import json
from datetime import datetime
import numpy as np
from collections import Counter
import spacy
from textblob import TextBlob
import networkx as nx

from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class AnalysisUtils:
    """Utility functions for content analysis."""

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text.

        Args:
            text: Text to clean

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())

        # Remove special characters
        text = re.sub(r'[^\w\s.,!?-]', '', text)

        return text

    @staticmethod
    def extract_keywords(
        text: str,
        nlp: Optional[spacy.Language] = None,
        max_keywords: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Extract keywords from text.

        Args:
            text: Text to analyze
            nlp: Optional spaCy model
            max_keywords: Maximum number of keywords

        Returns:
            List of keywords with scores
        """
        if not text:
            return []

        try:
            # Use provided model or create a simple one
            if not nlp:
                nlp = spacy.load("en_core_web_sm")

            # Process text
            doc = nlp(text)

            # Count word frequencies
            word_freq = Counter()
            for token in doc:
                if not token.is_stop and not token.is_punct and len(token.text) > 2:
                    word_freq[token.lemma_.lower()] += 1

            # Calculate scores
            total_words = sum(word_freq.values())
            keywords = []
            for word, freq in word_freq.most_common(max_keywords):
                score = freq / total_words
                keywords.append({
                    "word": word,
                    "frequency": freq,
                    "score": score
                })

            return keywords

        except Exception as e:
            logger.error(f"Error extracting keywords: {str(e)}")
            return []

    @staticmethod
    def calculate_readability(text: str) -> Dict[str, float]:
        """
        Calculate readability metrics.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with readability scores
        """
        if not text:
            return {
                "flesch_kincaid": 0.0,
                "gunning_fog": 0.0,
                "smog": 0.0
            }

        try:
            # Calculate basic metrics
            sentences = text.split('.')
            words = text.split()
            syllables = sum(AnalysisUtils._count_syllables(word) for word in words)

            # Flesch-Kincaid Grade Level
            flesch_kincaid = 0.39 * (len(words) / len(sentences)) + 11.8 * (syllables / len(words)) - 15.59

            # Gunning Fog Index
            complex_words = sum(1 for word in words if AnalysisUtils._count_syllables(word) > 2)
            gunning_fog = 0.4 * ((len(words) / len(sentences)) + 100 * (complex_words / len(words)))

            # SMOG Index
            smog = 1.043 * np.sqrt(complex_words * (30 / len(sentences))) + 3.1291

            return {
                "flesch_kincaid": max(0.0, min(20.0, flesch_kincaid)),
                "gunning_fog": max(0.0, min(20.0, gunning_fog)),
                "smog": max(0.0, min(20.0, smog))
            }

        except Exception as e:
            logger.error(f"Error calculating readability: {str(e)}")
            return {
                "flesch_kincaid": 0.0,
                "gunning_fog": 0.0,
                "smog": 0.0
            }

    @staticmethod
    def extract_entities(
        text: str,
        nlp: Optional[spacy.Language] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract named entities from text.

        Args:
            text: Text to analyze
            nlp: Optional spaCy model

        Returns:
            List of entities with types
        """
        if not text:
            return []

        try:
            # Use provided model or create a simple one
            if not nlp:
                nlp = spacy.load("en_core_web_sm")

            # Process text
            doc = nlp(text)

            # Extract entities
            entities = []
            for ent in doc.ents:
                entities.append({
                    "text": ent.text,
                    "type": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char
                })

            return entities

        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")
            return []

    @staticmethod
    def analyze_sentiment(text: str) -> Dict[str, float]:
        """
        Analyze sentiment of text.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with sentiment scores
        """
        if not text:
            return {
                "polarity": 0.0,
                "subjectivity": 0.0
            }

        try:
            # Use TextBlob for sentiment analysis
            blob = TextBlob(text)
            return {
                "polarity": (blob.sentiment.polarity + 1) / 2,  # Convert to 0-1 range
                "subjectivity": blob.sentiment.subjectivity
            }

        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return {
                "polarity": 0.5,
                "subjectivity": 0.5
            }

    @staticmethod
    def extract_relationships(
        text: str,
        nlp: Optional[spacy.Language] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract relationships between entities.

        Args:
            text: Text to analyze
            nlp: Optional spaCy model

        Returns:
            List of relationships
        """
        if not text:
            return []

        try:
            # Use provided model or create a simple one
            if not nlp:
                nlp = spacy.load("en_core_web_sm")

            # Process text
            doc = nlp(text)

            # Extract relationships
            relationships = []
            for token in doc:
                if token.dep_ in ['nsubj', 'dobj'] and token.head.pos_ == 'VERB':
                    relationships.append({
                        "subject": token.text,
                        "verb": token.head.text,
                        "object": next((t.text for t in token.head.children if t.dep_ == 'dobj'), None)
                    })

            return relationships

        except Exception as e:
            logger.error(f"Error extracting relationships: {str(e)}")
            return []

    @staticmethod
    def build_entity_graph(
        entities: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]]
    ) -> nx.Graph:
        """
        Build a graph of entities and relationships.

        Args:
            entities: List of entities
            relationships: List of relationships

        Returns:
            NetworkX graph
        """
        try:
            # Create graph
            G = nx.Graph()

            # Add entities as nodes
            for entity in entities:
                G.add_node(
                    entity["text"],
                    type=entity["type"]
                )

            # Add relationships as edges
            for rel in relationships:
                if rel["subject"] and rel["object"]:
                    G.add_edge(
                        rel["subject"],
                        rel["object"],
                        verb=rel["verb"]
                    )

            return G

        except Exception as e:
            logger.error(f"Error building entity graph: {str(e)}")
            return nx.Graph()

    @staticmethod
    def _count_syllables(word: str) -> int:
        """
        Count syllables in a word.

        Args:
            word: Word to analyze

        Returns:
            Number of syllables
        """
        word = word.lower()
        count = 0
        vowels = "aeiouy"
        previous_is_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_is_vowel:
                count += 1
            previous_is_vowel = is_vowel

        if word.endswith("e"):
            count -= 1

        return max(1, count)

    @staticmethod
    def format_analysis_result(
        content: str,
        analysis: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Format analysis results.

        Args:
            content: Original content
            analysis: Analysis results
            metadata: Optional metadata

        Returns:
            Formatted result
        """
        return {
            "content": content,
            "analysis": analysis,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        }

    @staticmethod
    def merge_analysis_results(
        results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Merge multiple analysis results.

        Args:
            results: List of analysis results

        Returns:
            Merged result
        """
        if not results:
            return {}

        try:
            # Initialize merged result
            merged = {
                "content": results[0]["content"],
                "analysis": {},
                "metadata": {
                    "num_analyses": len(results),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

            # Merge analyses
            for result in results:
                for key, value in result["analysis"].items():
                    if key not in merged["analysis"]:
                        merged["analysis"][key] = value
                    elif isinstance(value, (int, float)):
                        merged["analysis"][key] = (merged["analysis"][key] + value) / 2
                    elif isinstance(value, list):
                        merged["analysis"][key].extend(value)
                    elif isinstance(value, dict):
                        merged["analysis"][key].update(value)

            # Merge metadata
            for result in results:
                if "metadata" in result:
                    merged["metadata"].update(result["metadata"])

            return merged

        except Exception as e:
            logger.error(f"Error merging analysis results: {str(e)}")
            return {} 
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
import numpy as np
from collections import Counter

from research_assistant.llm.model_manager import ModelManager
from research_assistant.llm.prompt_templates import PromptTemplateManager
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class Topic(BaseModel):
    """Model for topic analysis results."""
    name: str = Field(..., description="Topic name")
    keywords: List[str] = Field(..., description="Key terms associated with the topic")
    score: float = Field(..., description="Topic relevance score (0.0 to 1.0)")
    examples: List[str] = Field(default_factory=list, description="Example phrases for the topic")

class TopicModelResult(BaseModel):
    """Model for topic modeling results."""
    topics: List[Topic] = Field(..., description="Identified topics")
    document_topics: List[Dict[str, float]] = Field(..., description="Topic distribution for each document")
    coherence_score: float = Field(..., description="Topic coherence score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class TopicModeler:
    """Modeler for text topics."""

    def __init__(
        self,
        model_name: str = "mistral",
        config_path: Optional[str] = None,
        num_topics: int = 5,
        min_topic_size: int = 3
    ):
        """
        Initialize the topic modeler.

        Args:
            model_name: Name of the model to use
            config_path: Path to the configuration file
            num_topics: Number of topics to identify
            min_topic_size: Minimum number of documents per topic
        """
        self.model_name = model_name
        self.model_manager = ModelManager(config_path)
        self.template_manager = PromptTemplateManager()
        self.num_topics = num_topics
        self.min_topic_size = min_topic_size
        self.logger = get_logger("topic_modeler")

    async def analyze(
        self,
        documents: List[str],
        num_topics: Optional[int] = None,
        min_topic_size: Optional[int] = None
    ) -> TopicModelResult:
        """
        Analyze topics in documents.

        Args:
            documents: List of documents to analyze
            num_topics: Optional number of topics to identify
            min_topic_size: Optional minimum topic size

        Returns:
            TopicModelResult object
        """
        try:
            # Load model
            model = await self.model_manager.load_model(self.model_name)
            if not model:
                raise ValueError(f"Failed to load model: {self.model_name}")

            # Set parameters
            num_topics = num_topics or self.num_topics
            min_topic_size = min_topic_size or self.min_topic_size

            # Prepare prompt
            prompt = self._prepare_prompt(documents, num_topics, min_topic_size)

            # Generate analysis
            response = await model.generate(
                prompt=prompt,
                temperature=0.3,
                max_tokens=2000
            )

            # Parse response
            result = self._parse_response(response)

            # Calculate document-topic distribution
            doc_topics = self._calculate_document_topics(documents, result["topics"])

            # Calculate coherence score
            coherence = self._calculate_coherence(result["topics"])

            return TopicModelResult(
                topics=[Topic(**topic) for topic in result["topics"]],
                document_topics=doc_topics,
                coherence_score=coherence,
                metadata=result.get("metadata", {})
            )

        except Exception as e:
            self.logger.error(f"Error analyzing topics: {str(e)}")
            raise

    def _prepare_prompt(
        self,
        documents: List[str],
        num_topics: int,
        min_topic_size: int
    ) -> str:
        """
        Prepare the analysis prompt.

        Args:
            documents: List of documents
            num_topics: Number of topics
            min_topic_size: Minimum topic size

        Returns:
            Formatted prompt
        """
        prompt = f"""Analyze the following documents and identify {num_topics} main topics.
Each topic should have at least {min_topic_size} documents.

Documents:
{self._format_documents(documents)}

For each topic, provide:
1. Topic name
2. Key terms (at least 5)
3. Relevance score (0.0 to 1.0)
4. Example phrases (at least 3)

Format the response as JSON with the following structure:
{{
    "topics": [
        {{
            "name": "topic name",
            "keywords": ["term1", "term2", ...],
            "score": 0.8,
            "examples": ["example1", "example2", ...]
        }},
        ...
    ],
    "metadata": {{
        "num_documents": {len(documents)},
        "num_topics": {num_topics}
    }}
}}"""

        return prompt

    def _format_documents(self, documents: List[str]) -> str:
        """
        Format documents for the prompt.

        Args:
            documents: List of documents

        Returns:
            Formatted documents string
        """
        formatted = []
        for i, doc in enumerate(documents, 1):
            formatted.append(f"Document {i}:\n{doc}\n")
        return "\n".join(formatted)

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the model response.

        Args:
            response: Model response

        Returns:
            Parsed topic modeling results
        """
        try:
            import json
            import re

            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))

            return json.loads(response)

        except Exception as e:
            self.logger.error(f"Error parsing response: {str(e)}")
            raise

    def _calculate_document_topics(
        self,
        documents: List[str],
        topics: List[Dict[str, Any]]
    ) -> List[Dict[str, float]]:
        """
        Calculate topic distribution for each document.

        Args:
            documents: List of documents
            topics: List of topics

        Returns:
            List of topic distributions
        """
        distributions = []
        for doc in documents:
            doc_dist = {}
            for topic in topics:
                # Calculate similarity based on keyword overlap
                keywords = set(topic["keywords"])
                doc_words = set(doc.lower().split())
                overlap = len(keywords.intersection(doc_words))
                score = overlap / len(keywords) if keywords else 0.0
                doc_dist[topic["name"]] = score
            distributions.append(doc_dist)
        return distributions

    def _calculate_coherence(self, topics: List[Dict[str, Any]]) -> float:
        """
        Calculate topic coherence score.

        Args:
            topics: List of topics

        Returns:
            Coherence score
        """
        try:
            # Simple coherence based on keyword overlap
            total_overlap = 0
            total_pairs = 0

            for i, topic1 in enumerate(topics):
                for topic2 in topics[i+1:]:
                    keywords1 = set(topic1["keywords"])
                    keywords2 = set(topic2["keywords"])
                    overlap = len(keywords1.intersection(keywords2))
                    total_overlap += overlap
                    total_pairs += 1

            return 1.0 - (total_overlap / (total_pairs * 5)) if total_pairs > 0 else 0.0

        except Exception as e:
            self.logger.error(f"Error calculating coherence: {str(e)}")
            return 0.0

    async def close(self):
        """Close the topic modeler."""
        await self.model_manager.close() 
from typing import Dict, Any, List, Optional, Protocol
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from datetime import datetime

from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class AnalysisResult(BaseModel):
    """Model for analysis results."""
    content: str = Field(..., description="Analyzed content")
    summary: Optional[str] = Field(default=None, description="Analysis summary")
    insights: List[str] = Field(default_factory=list, description="Key insights")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Analysis metadata")
    confidence: float = Field(default=1.0, description="Confidence score (0-1)")
    analysis_date: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")
    language: Optional[str] = Field(default=None, description="Content language")
    sentiment: Optional[Dict[str, float]] = Field(default=None, description="Sentiment scores")
    topics: Optional[List[Dict[str, Any]]] = Field(default=None, description="Identified topics")
    facts: Optional[List[Dict[str, Any]]] = Field(default=None, description="Verified facts")

class AnalysisOptions(BaseModel):
    """Model for analysis options."""
    timeout: int = Field(default=30, description="Timeout in seconds")
    max_tokens: Optional[int] = Field(default=None, description="Maximum tokens to process")
    min_confidence: float = Field(default=0.7, description="Minimum confidence threshold")
    language: Optional[str] = Field(default=None, description="Target language")
    include_summary: bool = Field(default=True, description="Whether to include summary")
    include_insights: bool = Field(default=True, description="Whether to include insights")
    include_sentiment: bool = Field(default=False, description="Whether to include sentiment")
    include_topics: bool = Field(default=False, description="Whether to include topics")
    include_facts: bool = Field(default=False, description="Whether to include facts")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")

class BaseAnalyzer(ABC):
    """Base class for all content analyzers."""

    def __init__(self, name: str, description: str):
        """
        Initialize the analyzer.

        Args:
            name: Name of the analyzer
            description: Description of the analyzer
        """
        self.name = name
        self.description = description
        self.logger = get_logger(f"analyzer.{name}")

    @abstractmethod
    async def analyze(
        self,
        content: str,
        options: Optional[AnalysisOptions] = None
    ) -> AnalysisResult:
        """
        Analyze content.

        Args:
            content: Content to analyze
            options: Optional analysis options

        Returns:
            Analysis result

        Raises:
            ValueError: If content is invalid
            Exception: For other analysis errors
        """
        pass

    @abstractmethod
    async def validate_content(self, content: str) -> bool:
        """
        Validate if the content can be processed by this analyzer.

        Args:
            content: Content to validate

        Returns:
            True if content is valid, False otherwise
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the analyzer and clean up resources."""
        pass

    def format_result(self, result: Dict[str, Any]) -> AnalysisResult:
        """
        Format raw result into an AnalysisResult object.

        Args:
            result: Raw result data

        Returns:
            Formatted AnalysisResult
        """
        try:
            return AnalysisResult(
                content=result.get("content", ""),
                summary=result.get("summary"),
                insights=result.get("insights", []),
                metadata=result.get("metadata", {}),
                confidence=result.get("confidence", 1.0),
                language=result.get("language"),
                sentiment=result.get("sentiment"),
                topics=result.get("topics"),
                facts=result.get("facts")
            )
        except Exception as e:
            self.logger.error(f"Error formatting result: {str(e)}")
            raise

    def __str__(self) -> str:
        """String representation of the analyzer."""
        return f"{self.name}: {self.description}"

    def __repr__(self) -> str:
        """Detailed string representation of the analyzer."""
        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"description='{self.description}'"
            ")"
        )

    async def execute(
        self,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute the analysis tool.

        Args:
            parameters: Analysis parameters
            context: Optional execution context

        Returns:
            Analysis result and metadata
        """
        content = parameters.get("content")
        if not content:
            raise ValueError("Content is required")

        options = parameters.get("options", {})

        # Validate content
        if not await self.validate_content(content):
            raise ValueError(f"Invalid content for {self.name}")

        # Analyze content
        result = await self.analyze(content, options)

        # Format result
        formatted_result = self.format_result(result)

        return {
            "result": formatted_result,
            "analyzer": self.name
        } 
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime

from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class AnalysisResult:
    """Class representing the result of an analysis operation."""
    def __init__(
        self,
        content: str,
        metadata: Dict[str, Any],
        created_at: Optional[datetime] = None
    ):
        self.content = content
        self.metadata = metadata
        self.created_at = created_at or datetime.utcnow()

class BaseAnalyzer(ABC):
    """Base class for all analyzers."""

    def __init__(self, name: str, description: str):
        """
        Initialize the base analyzer.

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
        options: Optional[Dict[str, Any]] = None
    ) -> AnalysisResult:
        """
        Analyze the given content.

        Args:
            content: Content to analyze
            options: Optional analysis options

        Returns:
            Analysis result
        """
        pass

    @abstractmethod
    async def batch_analyze(
        self,
        contents: List[str],
        options: Optional[Dict[str, Any]] = None
    ) -> List[AnalysisResult]:
        """
        Analyze multiple contents in batch.

        Args:
            contents: List of contents to analyze
            options: Optional analysis options

        Returns:
            List of analysis results
        """
        pass

    @abstractmethod
    async def validate_content(self, content: str) -> bool:
        """
        Validate if the content can be analyzed.

        Args:
            content: Content to validate

        Returns:
            True if content is valid, False otherwise
        """
        pass

    @abstractmethod
    async def close(self):
        """Close the analyzer and release resources."""
        pass 
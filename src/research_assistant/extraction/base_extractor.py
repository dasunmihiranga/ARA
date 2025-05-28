from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime

from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

@dataclass
class ExtractedContent:
    """Class representing extracted content."""
    title: str
    text: str
    source: str
    url: Optional[str] = None
    metadata: Dict[str, Any] = None
    extracted_at: datetime = None

class BaseExtractor(ABC):
    """Base class for content extractors."""

    def __init__(self, name: str, description: str):
        """
        Initialize the base extractor.

        Args:
            name: Name of the extractor
            description: Description of the extractor
        """
        self.name = name
        self.description = description
        self.logger = get_logger(f"extraction.{name}")

    @abstractmethod
    async def extract(
        self,
        source: str,
        options: Optional[Dict[str, Any]] = None
    ) -> ExtractedContent:
        """
        Extract content from a source.

        Args:
            source: Source to extract from (URL, file path, etc.)
            options: Optional extraction options

        Returns:
            Extracted content
        """
        pass

    @abstractmethod
    async def validate_source(self, source: str) -> bool:
        """
        Validate if the source can be processed.

        Args:
            source: Source to validate

        Returns:
            True if source is valid, False otherwise
        """
        pass

    @abstractmethod
    async def close(self):
        """Close any resources used by the extractor."""
        pass

    def format_content(self, content: ExtractedContent) -> Dict[str, Any]:
        """
        Format extracted content for API response.

        Args:
            content: Content to format

        Returns:
            Formatted content dictionary
        """
        return {
            "title": content.title,
            "text": content.text,
            "source": content.source,
            "url": content.url,
            "metadata": content.metadata or {},
            "extracted_at": content.extracted_at.isoformat() if content.extracted_at else None
        }

    async def execute(
        self,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute the extraction tool.

        Args:
            parameters: Extraction parameters
            context: Optional execution context

        Returns:
            Extracted content and metadata
        """
        source = parameters.get("source")
        if not source:
            raise ValueError("Source is required")

        options = parameters.get("options", {})

        # Validate source
        if not await self.validate_source(source):
            raise ValueError(f"Invalid source: {source}")

        # Extract content
        content = await self.extract(source, options)

        # Format content
        formatted_content = self.format_content(content)

        return {
            "content": formatted_content,
            "extractor": self.name
        } 
from typing import Dict, Any, List, Optional, Protocol
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from datetime import datetime

from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class ExtractedContent(BaseModel):
    """Model for extracted content."""
    title: str = Field(..., description="Title of the content")
    text: str = Field(..., description="Main text content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Content metadata")
    source: str = Field(..., description="Source of the content")
    extraction_date: datetime = Field(default_factory=datetime.utcnow, description="Extraction timestamp")
    language: Optional[str] = Field(default=None, description="Content language")
    word_count: Optional[int] = Field(default=None, description="Word count")
    char_count: Optional[int] = Field(default=None, description="Character count")

class ExtractionOptions(BaseModel):
    """Model for extraction options."""
    timeout: int = Field(default=30, description="Timeout in seconds")
    max_size: Optional[int] = Field(default=None, description="Maximum content size in bytes")
    include_images: bool = Field(default=False, description="Whether to include images")
    include_links: bool = Field(default=True, description="Whether to include links")
    include_metadata: bool = Field(default=True, description="Whether to include metadata")
    language: Optional[str] = Field(default=None, description="Target language")
    clean_html: bool = Field(default=True, description="Whether to clean HTML")
    extract_tables: bool = Field(default=False, description="Whether to extract tables")
    extract_figures: bool = Field(default=False, description="Whether to extract figures")

class BaseExtractor(ABC):
    """Base class for all content extractors."""

    def __init__(self, name: str, description: str):
        """
        Initialize the extractor.

        Args:
            name: Name of the extractor
            description: Description of the extractor
        """
        self.name = name
        self.description = description
        self.logger = get_logger(f"extractor.{name}")

    @abstractmethod
    async def extract(
        self,
        source: str,
        options: Optional[ExtractionOptions] = None
    ) -> ExtractedContent:
        """
        Extract content from a source.

        Args:
            source: Source to extract from (URL, file path, etc.)
            options: Optional extraction options

        Returns:
            Extracted content

        Raises:
            ValueError: If source is invalid
            Exception: For other extraction errors
        """
        pass

    @abstractmethod
    async def validate_source(self, source: str) -> bool:
        """
        Validate if the source can be processed by this extractor.

        Args:
            source: Source to validate

        Returns:
            True if source is valid, False otherwise
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the extractor and clean up resources."""
        pass

    def format_content(self, content: Dict[str, Any]) -> ExtractedContent:
        """
        Format raw content into an ExtractedContent object.

        Args:
            content: Raw content data

        Returns:
            Formatted ExtractedContent
        """
        try:
            return ExtractedContent(
                title=content.get("title", ""),
                text=content.get("text", ""),
                metadata=content.get("metadata", {}),
                source=self.name,
                language=content.get("language"),
                word_count=content.get("word_count"),
                char_count=content.get("char_count")
            )
        except Exception as e:
            self.logger.error(f"Error formatting content: {str(e)}")
            raise

    def __str__(self) -> str:
        """String representation of the extractor."""
        return f"{self.name}: {self.description}"

    def __repr__(self) -> str:
        """Detailed string representation of the extractor."""
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
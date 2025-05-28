from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from research_assistant.core.tool_registry import MCPTool
from research_assistant.extraction.extraction_factory import ExtractionFactory
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class ExtractionToolInput(BaseModel):
    """Input model for the extraction tool."""
    source: str = Field(..., description="Source to extract from (URL or file path)")
    extractor_type: str = Field(
        default="web",
        description="Type of extractor to use (web, pdf, document)"
    )
    options: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional extraction options"
    )

class ExtractionTool(MCPTool):
    """Tool for extracting content from various sources."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the extraction tool.

        Args:
            config_path: Path to the extraction configuration file
        """
        super().__init__(
            name="extract",
            description="Extract content from web pages, PDFs, and documents",
            version="1.0.0"
        )
        self.extraction_factory = ExtractionFactory(config_path)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the extraction tool.

        Args:
            input_data: Input data containing extraction parameters

        Returns:
            Dictionary containing extracted content
        """
        try:
            # Parse and validate input
            extraction_input = ExtractionToolInput(**input_data)
            
            # Get extractor instance
            extractor = self.extraction_factory.get_extractor(extraction_input.extractor_type)
            if not extractor:
                raise ValueError(f"Failed to create extractor of type {extraction_input.extractor_type}")

            # Validate source
            if not await extractor.validate_source(extraction_input.source):
                raise ValueError(f"Invalid source for {extraction_input.extractor_type} extractor")

            # Extract content
            content = await extractor.extract(
                source=extraction_input.source,
                options=extraction_input.options
            )

            # Format content
            formatted_content = extractor.format_content(content)

            return {
                "status": "success",
                "content": formatted_content,
                "extractor": extraction_input.extractor_type
            }

        except Exception as e:
            logger.error(f"Extraction tool error: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def close(self):
        """Close the extraction tool and its resources."""
        await self.extraction_factory.close_all() 
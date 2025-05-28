import PyPDF2
import pdfplumber
from typing import Dict, Any, Optional, List
from datetime import datetime
import os
from pathlib import Path

from research_assistant.extraction.base_extractor import BaseExtractor, ExtractedContent
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class PDFExtractor(BaseExtractor):
    """PDF content extractor implementation."""

    def __init__(self):
        """Initialize the PDF extractor."""
        super().__init__(
            name="pdf",
            description="Extract content from PDF files"
        )

    async def extract(
        self,
        source: str,
        options: Optional[Dict[str, Any]] = None
    ) -> ExtractedContent:
        """
        Extract content from a PDF file.

        Args:
            source: Path to the PDF file
            options: Optional extraction options including:
                - max_pages: Maximum number of pages to extract
                - extract_images: Whether to extract image information
                - extract_tables: Whether to extract tables
                - password: PDF password if encrypted

        Returns:
            Extracted content
        """
        options = options or {}
        max_pages = options.get("max_pages", 100)
        extract_images = options.get("extract_images", False)
        extract_tables = options.get("extract_tables", True)
        password = options.get("password")

        try:
            # Get basic PDF info
            with open(source, 'rb') as file:
                pdf = PyPDF2.PdfReader(file)
                if pdf.is_encrypted:
                    if not password:
                        raise ValueError("PDF is encrypted but no password provided")
                    pdf.decrypt(password)

                # Extract metadata
                info = pdf.metadata
                title = info.get('/Title', '') if info else os.path.basename(source)
                num_pages = len(pdf.pages)

            # Extract text content
            text_content = []
            tables = []
            images = []

            with pdfplumber.open(source, password=password) as pdf:
                for i, page in enumerate(pdf.pages[:max_pages]):
                    # Extract text
                    text = page.extract_text()
                    if text:
                        text_content.append(text)

                    # Extract tables if requested
                    if extract_tables:
                        page_tables = page.extract_tables()
                        if page_tables:
                            tables.extend(page_tables)

                    # Extract image information if requested
                    if extract_images:
                        page_images = page.images
                        if page_images:
                            images.extend(page_images)

            # Combine extracted content
            full_text = "\n\n".join(text_content)

            return ExtractedContent(
                title=title,
                text=full_text,
                source="pdf",
                url=source,
                metadata={
                    "num_pages": num_pages,
                    "pages_extracted": min(num_pages, max_pages),
                    "has_tables": bool(tables),
                    "num_tables": len(tables),
                    "has_images": bool(images),
                    "num_images": len(images),
                    "extraction_options": options
                },
                extracted_at=datetime.utcnow()
            )

        except Exception as e:
            logger.error(f"PDF extraction error: {str(e)}")
            raise

    async def validate_source(self, source: str) -> bool:
        """
        Validate if the source is a valid PDF file.

        Args:
            source: Source to validate

        Returns:
            True if source is valid, False otherwise
        """
        try:
            path = Path(source)
            return path.exists() and path.suffix.lower() == '.pdf'
        except Exception:
            return False

    async def close(self):
        """No resources to close."""
        pass 
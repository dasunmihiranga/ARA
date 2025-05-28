import docx
from typing import Dict, Any, Optional, List
from datetime import datetime
import os
from pathlib import Path
import mimetypes

from research_assistant.extraction.base_extractor import BaseExtractor, ExtractedContent
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class DocumentExtractor(BaseExtractor):
    """Document content extractor implementation."""

    def __init__(self):
        """Initialize the document extractor."""
        super().__init__(
            name="document",
            description="Extract content from various document formats"
        )
        self.supported_formats = {
            '.docx': self._extract_docx,
            '.doc': self._extract_doc,
            '.txt': self._extract_txt,
            '.rtf': self._extract_rtf
        }

    async def extract(
        self,
        source: str,
        options: Optional[Dict[str, Any]] = None
    ) -> ExtractedContent:
        """
        Extract content from a document file.

        Args:
            source: Path to the document file
            options: Optional extraction options including:
                - max_size_mb: Maximum file size in MB
                - extract_images: Whether to extract image information
                - extract_tables: Whether to extract tables

        Returns:
            Extracted content
        """
        options = options or {}
        max_size = options.get("max_size_mb", 10) * 1024 * 1024  # Convert to bytes

        try:
            # Validate file size
            file_size = os.path.getsize(source)
            if file_size > max_size:
                raise ValueError(f"File size exceeds maximum limit of {max_size/1024/1024}MB")

            # Get file extension
            ext = Path(source).suffix.lower()
            if ext not in self.supported_formats:
                raise ValueError(f"Unsupported file format: {ext}")

            # Extract content based on file type
            extractor = self.supported_formats[ext]
            title, text, metadata = await extractor(source, options)

            return ExtractedContent(
                title=title,
                text=text,
                source="document",
                url=source,
                metadata=metadata,
                extracted_at=datetime.utcnow()
            )

        except Exception as e:
            logger.error(f"Document extraction error: {str(e)}")
            raise

    async def _extract_docx(
        self,
        source: str,
        options: Dict[str, Any]
    ) -> tuple[str, str, Dict[str, Any]]:
        """Extract content from DOCX files."""
        try:
            doc = docx.Document(source)
            
            # Extract title from first paragraph or filename
            title = doc.paragraphs[0].text if doc.paragraphs else os.path.basename(source)
            
            # Extract text content
            text_content = []
            tables = []
            images = []

            # Extract paragraphs
            for para in doc.paragraphs:
                if para.text.strip():
                    text_content.append(para.text)

            # Extract tables if requested
            if options.get("extract_tables", True):
                for table in doc.tables:
                    table_data = []
                    for row in table.rows:
                        table_data.append([cell.text for cell in row.cells])
                    tables.append(table_data)

            # Extract image information if requested
            if options.get("extract_images", False):
                for rel in doc.part.rels.values():
                    if "image" in rel.target_ref:
                        images.append({
                            "type": rel.target_ref.split('.')[-1],
                            "path": rel.target_ref
                        })

            # Combine text content
            text = "\n\n".join(text_content)

            metadata = {
                "format": "docx",
                "num_paragraphs": len(text_content),
                "has_tables": bool(tables),
                "num_tables": len(tables),
                "has_images": bool(images),
                "num_images": len(images),
                "extraction_options": options
            }

            return title, text, metadata

        except Exception as e:
            logger.error(f"DOCX extraction error: {str(e)}")
            raise

    async def _extract_doc(
        self,
        source: str,
        options: Dict[str, Any]
    ) -> tuple[str, str, Dict[str, Any]]:
        """Extract content from DOC files."""
        # Note: DOC extraction requires additional libraries like antiword or textract
        # For now, we'll raise an error
        raise NotImplementedError("DOC extraction not implemented yet")

    async def _extract_txt(
        self,
        source: str,
        options: Dict[str, Any]
    ) -> tuple[str, str, Dict[str, Any]]:
        """Extract content from TXT files."""
        try:
            with open(source, 'r', encoding='utf-8') as file:
                text = file.read()
                title = os.path.basename(source)
                
                metadata = {
                    "format": "txt",
                    "encoding": file.encoding,
                    "extraction_options": options
                }

                return title, text, metadata

        except Exception as e:
            logger.error(f"TXT extraction error: {str(e)}")
            raise

    async def _extract_rtf(
        self,
        source: str,
        options: Dict[str, Any]
    ) -> tuple[str, str, Dict[str, Any]]:
        """Extract content from RTF files."""
        # Note: RTF extraction requires additional libraries like striprtf
        # For now, we'll raise an error
        raise NotImplementedError("RTF extraction not implemented yet")

    async def validate_source(self, source: str) -> bool:
        """
        Validate if the source is a supported document file.

        Args:
            source: Source to validate

        Returns:
            True if source is valid, False otherwise
        """
        try:
            path = Path(source)
            return path.exists() and path.suffix.lower() in self.supported_formats
        except Exception:
            return False

    async def close(self):
        """No resources to close."""
        pass 
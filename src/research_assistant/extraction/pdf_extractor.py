from typing import Dict, Any, List, Optional
import asyncio
import fitz  # PyMuPDF
import re
from pathlib import Path
import langdetect
from datetime import datetime

from research_assistant.extraction.base_extractor import BaseExtractor, ExtractedContent, ExtractionOptions
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class PDFExtractor(BaseExtractor):
    """PDF content extractor implementation."""

    def __init__(self, max_pages: int = 1000):
        """
        Initialize the PDF extractor.

        Args:
            max_pages: Maximum number of pages to process
        """
        super().__init__(
            name="pdf",
            description="Extract content from PDF files"
        )
        self.max_pages = max_pages

    async def extract(
        self,
        source: str,
        options: Optional[ExtractionOptions] = None
    ) -> ExtractedContent:
        """
        Extract content from a PDF file.

        Args:
            source: Path to the PDF file
            options: Optional extraction options

        Returns:
            Extracted content

        Raises:
            ValueError: If file is invalid
            Exception: For other extraction errors
        """
        if not await self.validate_source(source):
            raise ValueError(f"Invalid PDF file: {source}")

        options = options or ExtractionOptions()

        try:
            # Open PDF file
            doc = fitz.open(source)
            
            # Check file size
            if options.max_size and Path(source).stat().st_size > options.max_size:
                raise ValueError(f"File size exceeds maximum limit: {Path(source).stat().st_size} bytes")

            # Extract text from each page
            text_parts = []
            metadata = self._extract_metadata(doc)
            
            # Process pages
            for page_num in range(min(len(doc), self.max_pages)):
                page = doc[page_num]
                
                # Extract text
                text = page.get_text()
                if text.strip():
                    text_parts.append(text)

                # Extract tables if requested
                if options.extract_tables:
                    tables = self._extract_tables(page)
                    if tables:
                        text_parts.extend(tables)

                # Extract images if requested
                if options.include_images:
                    images = self._extract_images(page)
                    if images:
                        metadata["images"] = metadata.get("images", []) + images

            # Combine text parts
            content = "\n\n".join(text_parts)
            
            # Clean content
            content = self._clean_content(content)

            # Detect language
            try:
                language = langdetect.detect(content)
            except:
                language = None

            # Count words and characters
            word_count = len(content.split())
            char_count = len(content)

            # Close the document
            doc.close()

            return self.format_content({
                "title": metadata.get("title", Path(source).stem),
                "text": content,
                "metadata": metadata,
                "language": language,
                "word_count": word_count,
                "char_count": char_count
            })

        except Exception as e:
            self.logger.error(f"Error extracting from {source}: {str(e)}")
            raise

    async def validate_source(self, source: str) -> bool:
        """
        Validate if the source is a valid PDF file.

        Args:
            source: File path to validate

        Returns:
            True if file is valid, False otherwise
        """
        try:
            path = Path(source)
            return path.exists() and path.is_file() and path.suffix.lower() == '.pdf'
        except:
            return False

    def _extract_metadata(self, doc: fitz.Document) -> Dict[str, Any]:
        """
        Extract metadata from PDF.

        Args:
            doc: PyMuPDF document

        Returns:
            Dictionary of metadata
        """
        metadata = {
            "title": "",
            "author": "",
            "subject": "",
            "keywords": [],
            "creator": "",
            "producer": "",
            "creation_date": None,
            "modification_date": None,
            "page_count": len(doc),
            "file_size": doc.filesize,
            "encrypted": doc.is_encrypted,
            "images": []
        }

        # Extract document metadata
        for key, value in doc.metadata.items():
            if key == "title":
                metadata["title"] = value
            elif key == "author":
                metadata["author"] = value
            elif key == "subject":
                metadata["subject"] = value
            elif key == "keywords":
                metadata["keywords"] = [k.strip() for k in value.split(',')]
            elif key == "creator":
                metadata["creator"] = value
            elif key == "producer":
                metadata["producer"] = value
            elif key == "creationDate":
                try:
                    metadata["creation_date"] = datetime.strptime(value, "D:%Y%m%d%H%M%S")
                except:
                    pass
            elif key == "modDate":
                try:
                    metadata["modification_date"] = datetime.strptime(value, "D:%Y%m%d%H%M%S")
                except:
                    pass

        return metadata

    def _extract_tables(self, page: fitz.Page) -> List[str]:
        """
        Extract tables from a page.

        Args:
            page: PyMuPDF page

        Returns:
            List of table contents as text
        """
        tables = []
        try:
            # Get table boundaries
            table_rects = page.find_tables()
            
            for table in table_rects:
                # Extract table content
                table_text = []
                for row in table.extract():
                    row_text = [cell.strip() for cell in row if cell.strip()]
                    if row_text:
                        table_text.append(" | ".join(row_text))
                
                if table_text:
                    tables.append("\n".join(table_text))
        except Exception as e:
            self.logger.warning(f"Error extracting tables: {str(e)}")

        return tables

    def _extract_images(self, page: fitz.Page) -> List[Dict[str, Any]]:
        """
        Extract images from a page.

        Args:
            page: PyMuPDF page

        Returns:
            List of image information
        """
        images = []
        try:
            for img_index, img in enumerate(page.get_images()):
                xref = img[0]
                base_image = page.parent.extract_image(xref)
                
                if base_image:
                    images.append({
                        "index": img_index,
                        "width": base_image["width"],
                        "height": base_image["height"],
                        "format": base_image["ext"],
                        "size": len(base_image["image"])
                    })
        except Exception as e:
            self.logger.warning(f"Error extracting images: {str(e)}")

        return images

    def _clean_content(self, content: str) -> str:
        """
        Clean extracted content.

        Args:
            content: Raw content to clean

        Returns:
            Cleaned content
        """
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove empty lines
        content = re.sub(r'\n\s*\n', '\n', content)
        
        # Remove special characters
        content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', content)
        
        return content.strip()

    async def close(self) -> None:
        """Close the PDF extractor."""
        pass  # No resources to clean up 
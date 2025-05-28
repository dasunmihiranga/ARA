import pytest
from unittest.mock import Mock, patch
from research_assistant.extraction.extraction_manager import ExtractionManager
from research_assistant.extraction.extractors.web import WebExtractor
from research_assistant.extraction.extractors.pdf import PDFExtractor
from research_assistant.extraction.extractors.document import DocumentExtractor

class TestExtractionManager:
    @pytest.fixture
    def extraction_manager(self):
        return ExtractionManager()

    def test_initialize_extractors(self, extraction_manager):
        """Test initialization of content extractors."""
        assert "web" in extraction_manager.extractors
        assert "pdf" in extraction_manager.extractors
        assert "document" in extraction_manager.extractors
        assert isinstance(extraction_manager.extractors["web"], WebExtractor)
        assert isinstance(extraction_manager.extractors["pdf"], PDFExtractor)
        assert isinstance(extraction_manager.extractors["document"], DocumentExtractor)

    @patch("research_assistant.extraction.extractors.web.WebExtractor.extract")
    async def test_extract_web_content(self, mock_web_extract, extraction_manager, mock_extraction_request):
        """Test web content extraction."""
        mock_web_extract.return_value = {
            "text": "Extracted web content",
            "metadata": {
                "title": "Test Page",
                "author": "Test Author",
                "date": "2024-03-15"
            }
        }

        result = await extraction_manager.extract(mock_extraction_request)
        
        assert result["text"] == "Extracted web content"
        assert "metadata" in result
        mock_web_extract.assert_called_once()

    @patch("research_assistant.extraction.extractors.pdf.PDFExtractor.extract")
    async def test_extract_pdf_content(self, mock_pdf_extract, extraction_manager, mock_extraction_request):
        """Test PDF content extraction."""
        mock_extraction_request["type"] = "pdf"
        mock_pdf_extract.return_value = {
            "text": "Extracted PDF content",
            "metadata": {
                "title": "Test PDF",
                "author": "Test Author",
                "page_count": 10
            }
        }

        result = await extraction_manager.extract(mock_extraction_request)
        
        assert result["text"] == "Extracted PDF content"
        assert result["metadata"]["page_count"] == 10
        mock_pdf_extract.assert_called_once()

    @patch("research_assistant.extraction.extractors.document.DocumentExtractor.extract")
    async def test_extract_document_content(self, mock_doc_extract, extraction_manager, mock_extraction_request):
        """Test document content extraction."""
        mock_extraction_request["type"] = "document"
        mock_doc_extract.return_value = {
            "text": "Extracted document content",
            "metadata": {
                "title": "Test Document",
                "author": "Test Author",
                "format": "docx"
            }
        }

        result = await extraction_manager.extract(mock_extraction_request)
        
        assert result["text"] == "Extracted document content"
        assert result["metadata"]["format"] == "docx"
        mock_doc_extract.assert_called_once()

    async def test_extract_invalid_type(self, extraction_manager, mock_extraction_request):
        """Test extraction with invalid content type."""
        mock_extraction_request["type"] = "invalid_type"
        
        with pytest.raises(ValueError, match="Invalid content type"):
            await extraction_manager.extract(mock_extraction_request)

    @patch("research_assistant.extraction.extractors.web.WebExtractor.extract")
    async def test_extract_timeout(self, mock_web_extract, extraction_manager, mock_extraction_request):
        """Test extraction timeout handling."""
        mock_web_extract.side_effect = TimeoutError("Extraction timed out")
        
        with pytest.raises(TimeoutError, match="Extraction timed out"):
            await extraction_manager.extract(mock_extraction_request)

    @patch("research_assistant.extraction.extractors.web.WebExtractor.extract")
    async def test_extract_encoding_error(self, mock_web_extract, extraction_manager, mock_extraction_request):
        """Test extraction encoding error handling."""
        mock_web_extract.side_effect = UnicodeDecodeError("utf-8", b"", 0, 1, "Invalid encoding")
        
        with pytest.raises(UnicodeDecodeError):
            await extraction_manager.extract(mock_extraction_request)

    def test_validate_extraction_request(self, extraction_manager, mock_extraction_request):
        """Test extraction request validation."""
        # Test valid request
        assert extraction_manager.validate_extraction_request(mock_extraction_request) is True

        # Test invalid request (missing required field)
        invalid_request = mock_extraction_request.copy()
        del invalid_request["url"]
        assert extraction_manager.validate_extraction_request(invalid_request) is False

        # Test invalid request (invalid type)
        invalid_request = mock_extraction_request.copy()
        invalid_request["type"] = "invalid_type"
        assert extraction_manager.validate_extraction_request(invalid_request) is False

    @patch("research_assistant.extraction.extractors.web.WebExtractor.extract")
    async def test_extract_with_metadata(self, mock_web_extract, extraction_manager, mock_extraction_request):
        """Test extraction with metadata options."""
        mock_web_extract.return_value = {
            "text": "Extracted content",
            "metadata": {
                "title": "Test Page",
                "author": "Test Author",
                "date": "2024-03-15",
                "keywords": ["test", "example"],
                "description": "Test description"
            }
        }

        mock_extraction_request["options"]["extract_metadata"] = True
        result = await extraction_manager.extract(mock_extraction_request)
        
        assert "metadata" in result
        assert "keywords" in result["metadata"]
        assert "description" in result["metadata"]

    @patch("research_assistant.extraction.extractors.web.WebExtractor.extract")
    async def test_extract_with_cleaning(self, mock_web_extract, extraction_manager, mock_extraction_request):
        """Test extraction with content cleaning options."""
        mock_web_extract.return_value = {
            "text": "<div>Extracted content with <script>ads</script> and <style>styles</style></div>",
            "metadata": {}
        }

        mock_extraction_request["options"]["clean_html"] = True
        mock_extraction_request["options"]["remove_ads"] = True
        result = await extraction_manager.extract(mock_extraction_request)
        
        assert "<script>" not in result["text"]
        assert "<style>" not in result["text"]
        assert "Extracted content" in result["text"] 
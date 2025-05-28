import pytest
from unittest.mock import Mock, patch
from research_assistant.reports.report_manager import ReportManager
from research_assistant.reports.generators.academic import AcademicReportGenerator
from research_assistant.reports.generators.business import BusinessReportGenerator
from research_assistant.reports.generators.technical import TechnicalReportGenerator

class TestReportManager:
    @pytest.fixture
    def report_manager(self):
        return ReportManager()

    def test_initialize_generators(self, report_manager):
        """Test initialization of report generators."""
        assert "academic" in report_manager.generators
        assert "business" in report_manager.generators
        assert "technical" in report_manager.generators
        assert isinstance(report_manager.generators["academic"], AcademicReportGenerator)
        assert isinstance(report_manager.generators["business"], BusinessReportGenerator)
        assert isinstance(report_manager.generators["technical"], TechnicalReportGenerator)

    @patch("research_assistant.reports.generators.academic.AcademicReportGenerator.generate")
    async def test_generate_academic_report(self, mock_generate, report_manager, mock_report_request):
        """Test academic report generation."""
        mock_generate.return_value = {
            "title": "Academic Report",
            "content": "This is an academic report",
            "sections": [
                {"title": "Introduction", "content": "Introduction content"},
                {"title": "Methodology", "content": "Methodology content"}
            ],
            "metadata": {
                "generated_at": "2024-03-15",
                "page_count": 2,
                "citations": ["citation1", "citation2"]
            }
        }

        result = await report_manager.generate_report(mock_report_request)
        
        assert result["title"] == "Academic Report"
        assert len(result["sections"]) == 2
        assert "citations" in result["metadata"]
        mock_generate.assert_called_once()

    @patch("research_assistant.reports.generators.business.BusinessReportGenerator.generate")
    async def test_generate_business_report(self, mock_generate, report_manager, mock_report_request):
        """Test business report generation."""
        mock_report_request["template"] = "business"
        mock_generate.return_value = {
            "title": "Business Report",
            "content": "This is a business report",
            "sections": [
                {"title": "Executive Summary", "content": "Summary content"},
                {"title": "Market Analysis", "content": "Analysis content"}
            ],
            "metadata": {
                "generated_at": "2024-03-15",
                "page_count": 2,
                "visualizations": ["chart1", "chart2"]
            }
        }

        result = await report_manager.generate_report(mock_report_request)
        
        assert result["title"] == "Business Report"
        assert len(result["sections"]) == 2
        assert "visualizations" in result["metadata"]
        mock_generate.assert_called_once()

    @patch("research_assistant.reports.generators.technical.TechnicalReportGenerator.generate")
    async def test_generate_technical_report(self, mock_generate, report_manager, mock_report_request):
        """Test technical report generation."""
        mock_report_request["template"] = "technical"
        mock_generate.return_value = {
            "title": "Technical Report",
            "content": "This is a technical report",
            "sections": [
                {"title": "System Overview", "content": "Overview content"},
                {"title": "Technical Details", "content": "Details content"}
            ],
            "metadata": {
                "generated_at": "2024-03-15",
                "page_count": 2,
                "code_snippets": ["code1", "code2"]
            }
        }

        result = await report_manager.generate_report(mock_report_request)
        
        assert result["title"] == "Technical Report"
        assert len(result["sections"]) == 2
        assert "code_snippets" in result["metadata"]
        mock_generate.assert_called_once()

    async def test_generate_report_invalid_template(self, report_manager, mock_report_request):
        """Test report generation with invalid template."""
        mock_report_request["template"] = "invalid_template"
        
        with pytest.raises(ValueError, match="Invalid report template"):
            await report_manager.generate_report(mock_report_request)

    @patch("research_assistant.reports.generators.academic.AcademicReportGenerator.generate")
    async def test_generate_report_timeout(self, mock_generate, report_manager, mock_report_request):
        """Test report generation timeout handling."""
        mock_generate.side_effect = TimeoutError("Report generation timed out")
        
        with pytest.raises(TimeoutError, match="Report generation timed out"):
            await report_manager.generate_report(mock_report_request)

    def test_validate_report_request(self, report_manager, mock_report_request):
        """Test report request validation."""
        # Test valid request
        assert report_manager.validate_report_request(mock_report_request) is True

        # Test invalid request (missing required field)
        invalid_request = mock_report_request.copy()
        del invalid_request["research_data"]
        assert report_manager.validate_report_request(invalid_request) is False

        # Test invalid request (invalid template)
        invalid_request = mock_report_request.copy()
        invalid_request["template"] = "invalid_template"
        assert report_manager.validate_report_request(invalid_request) is False

    @patch("research_assistant.reports.generators.academic.AcademicReportGenerator.generate")
    async def test_generate_report_with_visualizations(self, mock_generate, report_manager, mock_report_request):
        """Test report generation with visualizations."""
        mock_generate.return_value = {
            "title": "Report with Visualizations",
            "content": "Report content",
            "sections": [{"title": "Section", "content": "Content"}],
            "metadata": {
                "visualizations": ["chart1", "chart2"]
            }
        }

        mock_report_request["options"]["include_visualizations"] = True
        result = await report_manager.generate_report(mock_report_request)
        
        assert "visualizations" in result["metadata"]
        assert len(result["metadata"]["visualizations"]) == 2
        mock_generate.assert_called_once()

    @patch("research_assistant.reports.generators.academic.AcademicReportGenerator.generate")
    async def test_generate_report_with_citations(self, mock_generate, report_manager, mock_report_request):
        """Test report generation with citations."""
        mock_generate.return_value = {
            "title": "Report with Citations",
            "content": "Report content",
            "sections": [{"title": "Section", "content": "Content"}],
            "metadata": {
                "citations": ["citation1", "citation2"]
            }
        }

        mock_report_request["options"]["include_citations"] = True
        result = await report_manager.generate_report(mock_report_request)
        
        assert "citations" in result["metadata"]
        assert len(result["metadata"]["citations"]) == 2
        mock_generate.assert_called_once()

    @patch("research_assistant.reports.generators.academic.AcademicReportGenerator.generate")
    async def test_generate_report_with_custom_format(self, mock_generate, report_manager, mock_report_request):
        """Test report generation with custom format."""
        mock_generate.return_value = {
            "title": "Custom Format Report",
            "content": "Report content",
            "sections": [{"title": "Section", "content": "Content"}],
            "metadata": {
                "format": "pdf"
            }
        }

        mock_report_request["format"] = "pdf"
        result = await report_manager.generate_report(mock_report_request)
        
        assert result["metadata"]["format"] == "pdf"
        mock_generate.assert_called_once() 
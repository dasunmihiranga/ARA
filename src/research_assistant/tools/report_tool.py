from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from research_assistant.tools.base_tool import MCPTool
from research_assistant.reports.report_generator import ReportGenerator
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class ReportToolInput(BaseModel):
    """Input model for the report tool."""
    template_name: str = Field(..., description="Name of the report template to use")
    research_data: Dict[str, Any] = Field(..., description="Research data to include in the report")
    format: str = Field(default="markdown", description="Output format (markdown, html, pdf)")
    options: Optional[Dict[str, Any]] = Field(default=None, description="Additional report options")

class ReportTool(MCPTool):
    """Tool for generating research reports."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the report tool.

        Args:
            config_path: Path to the report configuration file
        """
        super().__init__(
            name="report",
            description="Generate research reports from analysis results",
            input_model=ReportToolInput
        )
        self.report_generator = ReportGenerator(config_path=config_path)
        self.logger = get_logger("report_tool")

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the report generation.

        Args:
            input_data: Input data for report generation

        Returns:
            Dictionary containing the generated report
        """
        try:
            # Validate input
            input_model = ReportToolInput(**input_data)

            # Generate report
            report = await self.report_generator.generate_report(
                research_data=input_model.research_data,
                template_name=input_model.template_name,
                format=input_model.format,
                options=input_model.options
            )

            return {
                "status": "success",
                "report": report
            }

        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def close(self):
        """Close the report tool."""
        await self.report_generator.close() 
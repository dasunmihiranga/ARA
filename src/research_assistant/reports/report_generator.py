from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import yaml
from pathlib import Path

from research_assistant.llm.model_manager import ModelManager
from research_assistant.llm.prompt_templates import PromptTemplateManager
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class ReportGenerator:
    """Generator for research reports."""

    def __init__(
        self,
        model_name: str = "mistral",
        templates_dir: Optional[str] = None,
        config_path: Optional[str] = None
    ):
        """
        Initialize the report generator.

        Args:
            model_name: Name of the model to use
            templates_dir: Directory containing report templates
            config_path: Path to the report configuration file
        """
        self.model_name = model_name
        self.model_manager = ModelManager(config_path)
        self.template_manager = PromptTemplateManager(templates_dir)
        self.logger = get_logger("report_generator")

    async def generate_report(
        self,
        research_data: Dict[str, Any],
        template_name: str,
        format: str = "markdown",
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a research report.

        Args:
            research_data: Research findings and metadata
            template_name: Name of the report template
            format: Output format (markdown, html, pdf)
            options: Additional report options

        Returns:
            Dictionary containing the generated report
        """
        try:
            # Load model
            model = await self.model_manager.load_model(self.model_name)
            if not model:
                raise ValueError(f"Failed to load model: {self.model_name}")

            # Get template
            template = self.template_manager.get_template(template_name)
            if not template:
                raise ValueError(f"Template not found: {template_name}")

            # Prepare report data
            report_data = self._prepare_report_data(research_data, options)

            # Generate report content
            content = await self._generate_content(model, template, report_data)

            # Format report
            formatted_report = await self._format_report(content, format)

            return {
                "content": formatted_report,
                "metadata": {
                    "template": template_name,
                    "format": format,
                    "generated_at": datetime.utcnow().isoformat(),
                    "model": self.model_name,
                    "options": options
                }
            }

        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            raise

    def _prepare_report_data(
        self,
        research_data: Dict[str, Any],
        options: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Prepare data for report generation.

        Args:
            research_data: Research findings and metadata
            options: Additional report options

        Returns:
            Prepared report data
        """
        data = {
            "title": research_data.get("title", "Research Report"),
            "summary": research_data.get("summary", ""),
            "findings": research_data.get("findings", []),
            "sources": research_data.get("sources", []),
            "metadata": research_data.get("metadata", {}),
            "options": options or {}
        }

        # Add timestamps
        data["generated_at"] = datetime.utcnow().isoformat()
        if "created_at" not in data["metadata"]:
            data["metadata"]["created_at"] = data["generated_at"]

        return data

    async def _generate_content(
        self,
        model: Any,
        template: Any,
        data: Dict[str, Any]
    ) -> str:
        """
        Generate report content using the model.

        Args:
            model: Model instance
            template: Report template
            data: Report data

        Returns:
            Generated report content
        """
        try:
            # Render template
            prompt = template.render(**data)

            # Generate content
            response = await model.generate(
                prompt=prompt,
                temperature=0.7,
                max_tokens=2000
            )

            return response.strip()

        except Exception as e:
            self.logger.error(f"Error generating content: {str(e)}")
            raise

    async def _format_report(
        self,
        content: str,
        format: str
    ) -> str:
        """
        Format the report in the specified format.

        Args:
            content: Report content
            format: Output format

        Returns:
            Formatted report
        """
        try:
            if format == "markdown":
                return content
            elif format == "html":
                return self._convert_to_html(content)
            elif format == "pdf":
                return await self._convert_to_pdf(content)
            else:
                raise ValueError(f"Unsupported format: {format}")

        except Exception as e:
            self.logger.error(f"Error formatting report: {str(e)}")
            raise

    def _convert_to_html(self, content: str) -> str:
        """
        Convert markdown content to HTML.

        Args:
            content: Markdown content

        Returns:
            HTML content
        """
        # TODO: Implement markdown to HTML conversion
        return f"<html><body>{content}</body></html>"

    async def _convert_to_pdf(self, content: str) -> str:
        """
        Convert content to PDF.

        Args:
            content: Report content

        Returns:
            PDF content as base64 string
        """
        # TODO: Implement PDF conversion
        raise NotImplementedError("PDF conversion not implemented")

    async def close(self):
        """Close the report generator."""
        await self.model_manager.close() 
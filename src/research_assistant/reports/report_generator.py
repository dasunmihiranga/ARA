from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pathlib import Path
import json
import yaml

from research_assistant.reports.template_manager import TemplateManager
from research_assistant.reports.export_formats import ExportFormats
from research_assistant.reports.visualization import Visualization
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class ReportGenerator:
    """Report generation and compilation."""

    def __init__(
        self,
        template_dir: str = "templates",
        export_dir: str = "data/exports"
    ):
        """
        Initialize report generator.

        Args:
            template_dir: Directory containing report templates
            export_dir: Directory for exported reports
        """
        self.template_manager = TemplateManager(template_dir)
        self.export_formats = ExportFormats()
        self.visualization = Visualization()
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    async def generate_report(
        self,
        content: Dict[str, Any],
        template_name: str,
        format: str = "pdf",
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a research report.

        Args:
            content: Report content
            template_name: Name of template to use
            format: Output format (pdf, html, markdown, json)
            options: Additional generation options

        Returns:
            Generated report data
        """
        try:
            # Load template
            template = await self.template_manager.get_template(template_name)
            if not template:
                raise ValueError(f"Template not found: {template_name}")

            # Process content
            processed_content = await self._process_content(content, template)

            # Generate visualizations
            if "visualizations" in template.get("sections", []):
                processed_content = await self._add_visualizations(
                    processed_content,
                    template["sections"]["visualizations"]
                )

            # Format report
            formatted_report = await self.export_formats.format_report(
                processed_content,
                format,
                options
            )

            # Save report
            filename = self._generate_filename(template_name, format)
            filepath = self.export_dir / filename
            await self.export_formats.save_report(formatted_report, filepath, format)

            return {
                "report_id": filename,
                "content": formatted_report,
                "format": format,
                "metadata": {
                    "template": template_name,
                    "timestamp": datetime.utcnow().isoformat(),
                    "filepath": str(filepath)
                }
            }

        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            raise

    async def _process_content(
        self,
        content: Dict[str, Any],
        template: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process content according to template structure.

        Args:
            content: Raw content
            template: Template structure

        Returns:
            Processed content
        """
        try:
            processed = {
                "title": content.get("title", "Research Report"),
                "timestamp": datetime.utcnow().isoformat(),
                "sections": []
            }

            # Process each section
            for section in template.get("sections", []):
                section_name = section["name"]
                if section_name in content:
                    processed_section = await self._process_section(
                        content[section_name],
                        section
                    )
                    processed["sections"].append(processed_section)

            # Add metadata
            processed["metadata"] = {
                "template": template.get("name", ""),
                "version": template.get("version", "1.0"),
                "generated_by": "AI Research Assistant"
            }

            return processed

        except Exception as e:
            logger.error(f"Error processing content: {str(e)}")
            raise

    async def _process_section(
        self,
        content: Any,
        section: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a single section.

        Args:
            content: Section content
            section: Section template

        Returns:
            Processed section
        """
        try:
            processed = {
                "name": section["name"],
                "type": section.get("type", "text"),
                "content": content
            }

            # Apply section-specific processing
            if section.get("type") == "table":
                processed["content"] = self._format_table(content)
            elif section.get("type") == "list":
                processed["content"] = self._format_list(content)
            elif section.get("type") == "code":
                processed["content"] = self._format_code(content)

            return processed

        except Exception as e:
            logger.error(f"Error processing section: {str(e)}")
            raise

    async def _add_visualizations(
        self,
        content: Dict[str, Any],
        visualization_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add visualizations to report.

        Args:
            content: Report content
            visualization_config: Visualization configuration

        Returns:
            Content with visualizations
        """
        try:
            for viz_type, config in visualization_config.items():
                if viz_type == "charts":
                    charts = await self.visualization.generate_charts(
                        content,
                        config
                    )
                    content["visualizations"] = charts
                elif viz_type == "graphs":
                    graphs = await self.visualization.generate_graphs(
                        content,
                        config
                    )
                    content["visualizations"] = graphs

            return content

        except Exception as e:
            logger.error(f"Error adding visualizations: {str(e)}")
            raise

    def _format_table(self, content: List[Dict[str, Any]]) -> str:
        """Format content as table."""
        try:
            if not content:
                return ""

            # Get headers
            headers = list(content[0].keys())
            
            # Create table
            table = "| " + " | ".join(headers) + " |\n"
            table += "| " + " | ".join(["---"] * len(headers)) + " |\n"
            
            for row in content:
                table += "| " + " | ".join(str(row[h]) for h in headers) + " |\n"
            
            return table

        except Exception as e:
            logger.error(f"Error formatting table: {str(e)}")
            raise

    def _format_list(self, content: List[str]) -> str:
        """Format content as list."""
        try:
            return "\n".join(f"- {item}" for item in content)
        except Exception as e:
            logger.error(f"Error formatting list: {str(e)}")
            raise

    def _format_code(self, content: str) -> str:
        """Format content as code block."""
        try:
            return f"```\n{content}\n```"
        except Exception as e:
            logger.error(f"Error formatting code: {str(e)}")
            raise

    def _generate_filename(
        self,
        template_name: str,
        format: str
    ) -> str:
        """Generate unique filename for report."""
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            return f"report_{template_name}_{timestamp}.{format}"
        except Exception as e:
            logger.error(f"Error generating filename: {str(e)}")
            raise 
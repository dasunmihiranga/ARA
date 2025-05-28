from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import json
import csv
import yaml
import markdown
import pdfkit
from pathlib import Path

from research_assistant.tools.tool_schemas import (
    ReportRequest, ReportResult, ToolResponse
)
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class ExportTools:
    """Export tools for the MCP server."""

    def __init__(
        self,
        export_dir: str = "data/exports"
    ):
        """
        Initialize export tools.

        Args:
            export_dir: Directory for exported files
        """
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    async def generate_report(
        self,
        request: ReportRequest
    ) -> ToolResponse:
        """
        Generate a research report.

        Args:
            request: Report generation parameters

        Returns:
            Generated report
        """
        try:
            # Generate report content
            content = self._generate_content(
                request.content,
                request.template,
                request.options
            )

            # Convert to requested format
            if request.format == "markdown":
                report_content = self._to_markdown(content)
                file_extension = "md"
            elif request.format == "html":
                report_content = self._to_html(content)
                file_extension = "html"
            elif request.format == "pdf":
                report_content = self._to_pdf(content)
                file_extension = "pdf"
            elif request.format == "json":
                report_content = self._to_json(content)
                file_extension = "json"
            else:
                raise ValueError(f"Unsupported format: {request.format}")

            # Generate unique filename
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{timestamp}.{file_extension}"
            filepath = self.export_dir / filename

            # Save report
            self._save_report(report_content, filepath, request.format)

            # Create response
            report_result = ReportResult(
                report_id=filename,
                content=report_content,
                format=request.format,
                metadata={
                    "filename": filename,
                    "filepath": str(filepath),
                    "timestamp": timestamp
                }
            )

            return ToolResponse(
                success=True,
                data=report_result
            )

        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return ToolResponse(
                success=False,
                error=str(e)
            )

    def _generate_content(
        self,
        content: Dict[str, Any],
        template: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate report content from template.

        Args:
            content: Report content
            template: Optional template to use
            options: Optional generation options

        Returns:
            Generated content
        """
        try:
            if template:
                # Load template
                template_path = Path("templates") / f"{template}.yaml"
                if not template_path.exists():
                    raise ValueError(f"Template not found: {template}")

                with open(template_path) as f:
                    template_data = yaml.safe_load(f)

                # Apply template
                report_content = self._apply_template(
                    content,
                    template_data,
                    options
                )
            else:
                # Use default structure
                report_content = {
                    "title": content.get("title", "Research Report"),
                    "timestamp": datetime.utcnow().isoformat(),
                    "sections": content.get("sections", []),
                    "metadata": content.get("metadata", {})
                }

            return report_content

        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            raise

    def _apply_template(
        self,
        content: Dict[str, Any],
        template: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Apply template to content.

        Args:
            content: Report content
            template: Template structure
            options: Optional template options

        Returns:
            Templated content
        """
        try:
            result = template.copy()
            options = options or {}

            # Apply template sections
            for section in template.get("sections", []):
                section_name = section["name"]
                if section_name in content:
                    result["sections"].append({
                        "name": section_name,
                        "content": content[section_name],
                        "options": section.get("options", {})
                    })

            # Apply template options
            for key, value in options.items():
                if key in result:
                    result[key] = value

            return result

        except Exception as e:
            logger.error(f"Error applying template: {str(e)}")
            raise

    def _to_markdown(self, content: Dict[str, Any]) -> str:
        """
        Convert content to Markdown.

        Args:
            content: Report content

        Returns:
            Markdown string
        """
        try:
            md = f"# {content['title']}\n\n"
            md += f"Generated: {content['timestamp']}\n\n"

            for section in content.get("sections", []):
                md += f"## {section['name']}\n\n"
                md += f"{section['content']}\n\n"

            return md

        except Exception as e:
            logger.error(f"Error converting to Markdown: {str(e)}")
            raise

    def _to_html(self, content: Dict[str, Any]) -> str:
        """
        Convert content to HTML.

        Args:
            content: Report content

        Returns:
            HTML string
        """
        try:
            # Convert to Markdown first
            md = self._to_markdown(content)
            
            # Convert Markdown to HTML
            html = markdown.markdown(
                md,
                extensions=['tables', 'fenced_code']
            )

            # Add basic styling
            styled_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; }}
                    h1 {{ color: #2c3e50; }}
                    h2 {{ color: #34495e; margin-top: 30px; }}
                    pre {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f8f9fa; }}
                </style>
            </head>
            <body>
                {html}
            </body>
            </html>
            """

            return styled_html

        except Exception as e:
            logger.error(f"Error converting to HTML: {str(e)}")
            raise

    def _to_pdf(self, content: Dict[str, Any]) -> bytes:
        """
        Convert content to PDF.

        Args:
            content: Report content

        Returns:
            PDF bytes
        """
        try:
            # Convert to HTML first
            html = self._to_html(content)
            
            # Convert HTML to PDF
            pdf = pdfkit.from_string(
                html,
                False,
                options={
                    'page-size': 'A4',
                    'margin-top': '20mm',
                    'margin-right': '20mm',
                    'margin-bottom': '20mm',
                    'margin-left': '20mm',
                    'encoding': 'UTF-8'
                }
            )

            return pdf

        except Exception as e:
            logger.error(f"Error converting to PDF: {str(e)}")
            raise

    def _to_json(self, content: Dict[str, Any]) -> str:
        """
        Convert content to JSON.

        Args:
            content: Report content

        Returns:
            JSON string
        """
        try:
            return json.dumps(content, indent=2)

        except Exception as e:
            logger.error(f"Error converting to JSON: {str(e)}")
            raise

    def _save_report(
        self,
        content: Union[str, bytes],
        filepath: Path,
        format: str
    ) -> None:
        """
        Save report to file.

        Args:
            content: Report content
            filepath: Path to save file
            format: Report format
        """
        try:
            if format == "pdf":
                with open(filepath, "wb") as f:
                    f.write(content)
            else:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)

        except Exception as e:
            logger.error(f"Error saving report: {str(e)}")
            raise 
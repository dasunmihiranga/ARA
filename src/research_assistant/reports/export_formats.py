from typing import Dict, Any, Optional, Union
from pathlib import Path
import json
import yaml
import markdown
import pdfkit
from jinja2 import Template
import plotly.graph_objects as go
import plotly.io as pio

from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class ExportFormats:
    """Handler for different export formats."""

    def __init__(self):
        """Initialize export formats handler."""
        self.html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{{ title }}</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 40px;
                }
                h1, h2, h3 {
                    color: #333;
                }
                table {
                    border-collapse: collapse;
                    width: 100%;
                    margin: 20px 0;
                }
                th, td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }
                th {
                    background-color: #f5f5f5;
                }
                pre {
                    background-color: #f5f5f5;
                    padding: 10px;
                    border-radius: 5px;
                }
                .chart {
                    margin: 20px 0;
                }
            </style>
        </head>
        <body>
            {{ content }}
        </body>
        </html>
        """

    def to_markdown(
        self,
        content: Dict[str, Any]
    ) -> Optional[str]:
        """
        Convert content to Markdown format.

        Args:
            content: Content to convert

        Returns:
            Markdown string or None if failed
        """
        try:
            markdown_content = []

            # Add title
            if "title" in content:
                markdown_content.append(f"# {content['title']}\n")

            # Add sections
            if "sections" in content:
                for section in content["sections"]:
                    # Add section title
                    if "name" in section:
                        markdown_content.append(f"## {section['name']}\n")

                    # Add section content
                    if "content" in section:
                        if section.get("type") == "table":
                            markdown_content.append(self._table_to_markdown(section["content"]))
                        elif section.get("type") == "list":
                            markdown_content.append(self._list_to_markdown(section["content"]))
                        elif section.get("type") == "code":
                            markdown_content.append(self._code_to_markdown(section["content"]))
                        else:
                            markdown_content.append(f"{section['content']}\n")

            return "\n".join(markdown_content)

        except Exception as e:
            logger.error(f"Error converting to Markdown: {str(e)}")
            return None

    def to_html(
        self,
        content: Dict[str, Any]
    ) -> Optional[str]:
        """
        Convert content to HTML format.

        Args:
            content: Content to convert

        Returns:
            HTML string or None if failed
        """
        try:
            # First convert to Markdown
            markdown_content = self.to_markdown(content)
            if not markdown_content:
                return None

            # Convert Markdown to HTML
            html_content = markdown.markdown(
                markdown_content,
                extensions=["tables", "fenced_code"]
            )

            # Apply template
            template = Template(self.html_template)
            return template.render(
                title=content.get("title", "Report"),
                content=html_content
            )

        except Exception as e:
            logger.error(f"Error converting to HTML: {str(e)}")
            return None

    def to_pdf(
        self,
        content: Dict[str, Any],
        output_path: Optional[Path] = None
    ) -> Optional[bytes]:
        """
        Convert content to PDF format.

        Args:
            content: Content to convert
            output_path: Optional path to save PDF

        Returns:
            PDF bytes or None if failed
        """
        try:
            # First convert to HTML
            html_content = self.to_html(content)
            if not html_content:
                return None

            # Convert HTML to PDF
            pdf_options = {
                "page-size": "A4",
                "margin-top": "20mm",
                "margin-right": "20mm",
                "margin-bottom": "20mm",
                "margin-left": "20mm",
                "encoding": "UTF-8",
                "no-outline": None
            }

            pdf_bytes = pdfkit.from_string(
                html_content,
                False,
                options=pdf_options
            )

            # Save if output path provided
            if output_path:
                with open(output_path, "wb") as f:
                    f.write(pdf_bytes)

            return pdf_bytes

        except Exception as e:
            logger.error(f"Error converting to PDF: {str(e)}")
            return None

    def to_json(
        self,
        content: Dict[str, Any]
    ) -> Optional[str]:
        """
        Convert content to JSON format.

        Args:
            content: Content to convert

        Returns:
            JSON string or None if failed
        """
        try:
            return json.dumps(content, indent=2)

        except Exception as e:
            logger.error(f"Error converting to JSON: {str(e)}")
            return None

    def to_yaml(
        self,
        content: Dict[str, Any]
    ) -> Optional[str]:
        """
        Convert content to YAML format.

        Args:
            content: Content to convert

        Returns:
            YAML string or None if failed
        """
        try:
            return yaml.dump(content, default_flow_style=False)

        except Exception as e:
            logger.error(f"Error converting to YAML: {str(e)}")
            return None

    def _table_to_markdown(
        self,
        table_data: Union[Dict[str, Any], List[Dict[str, Any]]]
    ) -> str:
        """
        Convert table data to Markdown format.

        Args:
            table_data: Table data to convert

        Returns:
            Markdown table string
        """
        try:
            if isinstance(table_data, dict):
                # Single table
                headers = list(table_data.keys())
                rows = [list(table_data.values())]
            else:
                # List of tables
                headers = list(table_data[0].keys())
                rows = [list(row.values()) for row in table_data]

            # Create table
            markdown_table = []
            markdown_table.append("| " + " | ".join(headers) + " |")
            markdown_table.append("| " + " | ".join(["---"] * len(headers)) + " |")
            for row in rows:
                markdown_table.append("| " + " | ".join(str(cell) for cell in row) + " |")

            return "\n".join(markdown_table)

        except Exception as e:
            logger.error(f"Error converting table to Markdown: {str(e)}")
            return ""

    def _list_to_markdown(
        self,
        list_data: List[Any]
    ) -> str:
        """
        Convert list data to Markdown format.

        Args:
            list_data: List data to convert

        Returns:
            Markdown list string
        """
        try:
            return "\n".join(f"- {item}" for item in list_data)

        except Exception as e:
            logger.error(f"Error converting list to Markdown: {str(e)}")
            return ""

    def _code_to_markdown(
        self,
        code_data: str
    ) -> str:
        """
        Convert code data to Markdown format.

        Args:
            code_data: Code data to convert

        Returns:
            Markdown code block string
        """
        try:
            return f"```\n{code_data}\n```"

        except Exception as e:
            logger.error(f"Error converting code to Markdown: {str(e)}")
            return "" 
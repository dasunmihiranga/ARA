from typing import Dict, Any, Optional
import yaml
from pathlib import Path
from jinja2 import Template

from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class PromptTemplateManager:
    """Manager for prompt templates."""

    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize the prompt template manager.

        Args:
            templates_dir: Directory containing prompt template files
        """
        self.templates_dir = templates_dir or str(Path(__file__).parent / "templates")
        self.templates: Dict[str, Template] = {}
        self.logger = get_logger("prompt_templates")

    def load_templates(self) -> None:
        """Load all prompt templates from the templates directory."""
        try:
            templates_path = Path(self.templates_dir)
            if not templates_path.exists():
                self.logger.warning(f"Templates directory not found: {self.templates_dir}")
                return

            for template_file in templates_path.glob("*.yaml"):
                self._load_template_file(template_file)

        except Exception as e:
            self.logger.error(f"Error loading templates: {str(e)}")
            raise

    def _load_template_file(self, template_file: Path) -> None:
        """
        Load a single template file.

        Args:
            template_file: Path to the template file
        """
        try:
            with open(template_file, 'r') as f:
                template_data = yaml.safe_load(f)

            for template_name, template_info in template_data.items():
                template_str = template_info.get("template", "")
                self.templates[template_name] = Template(template_str)

        except Exception as e:
            self.logger.error(f"Error loading template file {template_file}: {str(e)}")
            raise

    def get_template(self, template_name: str) -> Optional[Template]:
        """
        Get a template by name.

        Args:
            template_name: Name of the template

        Returns:
            Jinja2 Template object or None if not found
        """
        return self.templates.get(template_name)

    def render_template(
        self,
        template_name: str,
        **kwargs: Any
    ) -> Optional[str]:
        """
        Render a template with the given variables.

        Args:
            template_name: Name of the template
            **kwargs: Variables to render in the template

        Returns:
            Rendered template string or None if template not found
        """
        template = self.get_template(template_name)
        if template is None:
            self.logger.warning(f"Template not found: {template_name}")
            return None

        try:
            return template.render(**kwargs)
        except Exception as e:
            self.logger.error(f"Error rendering template {template_name}: {str(e)}")
            raise

    def add_template(self, template_name: str, template_str: str) -> None:
        """
        Add a new template.

        Args:
            template_name: Name of the template
            template_str: Template string
        """
        try:
            self.templates[template_name] = Template(template_str)
        except Exception as e:
            self.logger.error(f"Error adding template {template_name}: {str(e)}")
            raise

    def remove_template(self, template_name: str) -> None:
        """
        Remove a template.

        Args:
            template_name: Name of the template to remove
        """
        self.templates.pop(template_name, None)

    def list_templates(self) -> list:
        """
        List all available templates.

        Returns:
            List of template names
        """
        return list(self.templates.keys()) 
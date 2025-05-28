from typing import Dict, Type, Optional
import yaml
from pathlib import Path

from research_assistant.extraction.base_extractor import BaseExtractor
from research_assistant.extraction.web_extractor import WebExtractor
from research_assistant.extraction.pdf_extractor import PDFExtractor
from research_assistant.extraction.document_extractor import DocumentExtractor
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class ExtractionFactory:
    """Factory class for creating and managing content extractors."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the extraction factory.

        Args:
            config_path: Path to the extraction configuration file
        """
        self.extractors: Dict[str, BaseExtractor] = {}
        self.config = self._load_config(config_path) if config_path else {}

    def _load_config(self, config_path: str) -> dict:
        """
        Load extraction configuration from YAML file.

        Args:
            config_path: Path to the configuration file

        Returns:
            Dictionary containing extraction configurations
        """
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading extraction config: {str(e)}")
            return {}

    def create_extractor(self, extractor_type: str) -> Optional[BaseExtractor]:
        """
        Create a new extractor instance.

        Args:
            extractor_type: Type of extractor to create

        Returns:
            Extractor instance or None if creation fails
        """
        try:
            if extractor_type in self.extractors:
                return self.extractors[extractor_type]

            extractor = None
            config = self.config.get(extractor_type, {})

            if extractor_type == "web":
                extractor = WebExtractor()
            elif extractor_type == "pdf":
                extractor = PDFExtractor()
            elif extractor_type == "document":
                extractor = DocumentExtractor()
            else:
                logger.error(f"Unknown extractor type: {extractor_type}")
                return None

            if extractor:
                self.extractors[extractor_type] = extractor
                return extractor

        except Exception as e:
            logger.error(f"Error creating extractor {extractor_type}: {str(e)}")
            return None

    def get_extractor(self, extractor_type: str) -> Optional[BaseExtractor]:
        """
        Get an existing extractor instance or create a new one.

        Args:
            extractor_type: Type of extractor to get

        Returns:
            Extractor instance or None if not found/created
        """
        return self.extractors.get(extractor_type) or self.create_extractor(extractor_type)

    def list_available_extractors(self) -> list:
        """
        List all available extractor types.

        Returns:
            List of extractor type names
        """
        return list(self.extractors.keys())

    async def close_all(self):
        """Close all extractor instances."""
        for extractor in self.extractors.values():
            try:
                await extractor.close()
            except Exception as e:
                logger.error(f"Error closing extractor: {str(e)}")
        self.extractors.clear() 
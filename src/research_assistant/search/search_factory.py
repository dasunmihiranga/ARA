from typing import Dict, Type, Optional
import yaml
from pathlib import Path

from research_assistant.search.base_searcher import BaseSearcher
from research_assistant.search.duckduckgo_search import DuckDuckGoSearcher
from research_assistant.search.searx_search import SearXSearcher
from research_assistant.search.academic_search import AcademicSearcher
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class SearchFactory:
    """Factory class for creating and managing search implementations."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the search factory.

        Args:
            config_path: Path to the search configuration file
        """
        self.searchers: Dict[str, BaseSearcher] = {}
        self.config = self._load_config(config_path) if config_path else {}

    def _load_config(self, config_path: str) -> dict:
        """
        Load search configuration from YAML file.

        Args:
            config_path: Path to the configuration file

        Returns:
            Dictionary containing search configurations
        """
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading search config: {str(e)}")
            return {}

    def create_searcher(self, searcher_type: str) -> Optional[BaseSearcher]:
        """
        Create a new searcher instance.

        Args:
            searcher_type: Type of searcher to create

        Returns:
            Searcher instance or None if creation fails
        """
        try:
            if searcher_type in self.searchers:
                return self.searchers[searcher_type]

            searcher = None
            config = self.config.get(searcher_type, {})

            if searcher_type == "duckduckgo":
                searcher = DuckDuckGoSearcher()
            elif searcher_type == "searx":
                if "instance_url" in config:
                    searcher = SearXSearcher(config["instance_url"])
                else:
                    logger.error("SearX instance URL not configured")
            elif searcher_type == "academic":
                searcher = AcademicSearcher()
            else:
                logger.error(f"Unknown searcher type: {searcher_type}")
                return None

            if searcher:
                self.searchers[searcher_type] = searcher
                return searcher

        except Exception as e:
            logger.error(f"Error creating searcher {searcher_type}: {str(e)}")
            return None

    def get_searcher(self, searcher_type: str) -> Optional[BaseSearcher]:
        """
        Get an existing searcher instance or create a new one.

        Args:
            searcher_type: Type of searcher to get

        Returns:
            Searcher instance or None if not found/created
        """
        return self.searchers.get(searcher_type) or self.create_searcher(searcher_type)

    def list_available_searchers(self) -> list:
        """
        List all available searcher types.

        Returns:
            List of searcher type names
        """
        return list(self.searchers.keys())

    async def close_all(self):
        """Close all searcher instances."""
        for searcher in self.searchers.values():
            try:
                await searcher.close()
            except Exception as e:
                logger.error(f"Error closing searcher: {str(e)}")
        self.searchers.clear() 
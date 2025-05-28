from typing import Dict, Type, Optional
import yaml
from pathlib import Path

from research_assistant.analysis.base_analyzer import BaseAnalyzer
from research_assistant.analysis.summarizer import Summarizer
from research_assistant.analysis.fact_checker import FactChecker
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class AnalysisFactory:
    """Factory class for creating and managing content analyzers."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the analysis factory.

        Args:
            config_path: Path to the analysis configuration file
        """
        self.analyzers: Dict[str, BaseAnalyzer] = {}
        self.config = self._load_config(config_path) if config_path else {}

    def _load_config(self, config_path: str) -> dict:
        """
        Load analysis configuration from YAML file.

        Args:
            config_path: Path to the configuration file

        Returns:
            Dictionary containing analysis configurations
        """
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading analysis config: {str(e)}")
            return {}

    def create_analyzer(self, analyzer_type: str) -> Optional[BaseAnalyzer]:
        """
        Create a new analyzer instance.

        Args:
            analyzer_type: Type of analyzer to create

        Returns:
            Analyzer instance or None if creation fails
        """
        try:
            if analyzer_type in self.analyzers:
                return self.analyzers[analyzer_type]

            analyzer = None
            config = self.config.get(analyzer_type, {})

            if analyzer_type == "summarizer":
                analyzer = Summarizer()
            elif analyzer_type == "fact_checker":
                analyzer = FactChecker()
            else:
                logger.error(f"Unknown analyzer type: {analyzer_type}")
                return None

            if analyzer:
                self.analyzers[analyzer_type] = analyzer
                return analyzer

        except Exception as e:
            logger.error(f"Error creating analyzer {analyzer_type}: {str(e)}")
            return None

    def get_analyzer(self, analyzer_type: str) -> Optional[BaseAnalyzer]:
        """
        Get an existing analyzer instance or create a new one.

        Args:
            analyzer_type: Type of analyzer to get

        Returns:
            Analyzer instance or None if not found/created
        """
        return self.analyzers.get(analyzer_type) or self.create_analyzer(analyzer_type)

    def list_available_analyzers(self) -> list:
        """
        List all available analyzer types.

        Returns:
            List of analyzer type names
        """
        return list(self.analyzers.keys())

    async def close_all(self):
        """Close all analyzer instances."""
        for analyzer in self.analyzers.values():
            try:
                await analyzer.close()
            except Exception as e:
                logger.error(f"Error closing analyzer: {str(e)}")
        self.analyzers.clear() 
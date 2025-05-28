from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from research_assistant.core.tool_registry import MCPTool
from research_assistant.analysis.analysis_factory import AnalysisFactory
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class AnalysisToolInput(BaseModel):
    """Input model for the analysis tool."""
    analyzer_type: str = Field(
        ...,
        description="Type of analyzer to use (summarizer, fact_checker)"
    )
    content: str = Field(
        ...,
        description="Content to analyze"
    )
    options: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional analysis options"
    )

class AnalysisTool(MCPTool):
    """Tool for analyzing content using various analyzers."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the analysis tool.

        Args:
            config_path: Path to the analysis configuration file
        """
        super().__init__(
            name="analysis",
            description="Analyze content using various analyzers",
            version="1.0.0"
        )
        self.analysis_factory = AnalysisFactory(config_path)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the analysis tool.

        Args:
            input_data: Input data containing analysis parameters

        Returns:
            Dictionary containing analysis results
        """
        try:
            # Parse and validate input
            analysis_input = AnalysisToolInput(**input_data)
            
            # Get analyzer instance
            analyzer = self.analysis_factory.get_analyzer(analysis_input.analyzer_type)
            if not analyzer:
                raise ValueError(f"Failed to create analyzer of type {analysis_input.analyzer_type}")

            # Execute analysis
            result = await analyzer.analyze(
                content=analysis_input.content,
                options=analysis_input.options
            )

            return {
                "status": "success",
                "analyzer_type": analysis_input.analyzer_type,
                "result": {
                    "content": result.content,
                    "metadata": result.metadata,
                    "created_at": result.created_at.isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Analysis tool error: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def close(self):
        """Close the analysis tool and its resources."""
        await self.analysis_factory.close_all() 
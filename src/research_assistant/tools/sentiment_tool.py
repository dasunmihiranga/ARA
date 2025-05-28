from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from research_assistant.tools.base_tool import MCPTool
from research_assistant.analysis.sentiment_analyzer import SentimentAnalyzer
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class SentimentToolInput(BaseModel):
    """Input model for the sentiment analysis tool."""
    text: str = Field(..., description="Text to analyze")
    aspects: Optional[List[str]] = Field(default=None, description="Optional aspects to analyze")
    include_emotions: bool = Field(default=True, description="Whether to include emotion analysis")

class SentimentTool(MCPTool):
    """Tool for sentiment analysis."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the sentiment analysis tool.

        Args:
            config_path: Path to the configuration file
        """
        super().__init__(
            name="sentiment",
            description="Analyze sentiment in text",
            input_model=SentimentToolInput
        )
        self.analyzer = SentimentAnalyzer(config_path=config_path)
        self.logger = get_logger("sentiment_tool")

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the sentiment analysis.

        Args:
            input_data: Input data for sentiment analysis

        Returns:
            Dictionary containing the analysis results
        """
        try:
            # Validate input
            input_model = SentimentToolInput(**input_data)

            # Analyze sentiment
            result = await self.analyzer.analyze(
                text=input_model.text,
                aspects=input_model.aspects,
                include_emotions=input_model.include_emotions
            )

            return {
                "status": "success",
                "result": result.dict()
            }

        except Exception as e:
            self.logger.error(f"Error analyzing sentiment: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def close(self):
        """Close the sentiment analysis tool."""
        await self.analyzer.close() 
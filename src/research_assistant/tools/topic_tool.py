from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from research_assistant.tools.base_tool import MCPTool
from research_assistant.analysis.topic_modeler import TopicModeler
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class TopicToolInput(BaseModel):
    """Input model for the topic modeling tool."""
    documents: List[str] = Field(..., description="List of documents to analyze")
    num_topics: Optional[int] = Field(default=None, description="Optional number of topics to identify")
    min_topic_size: Optional[int] = Field(default=None, description="Optional minimum topic size")

class TopicTool(MCPTool):
    """Tool for topic modeling."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the topic modeling tool.

        Args:
            config_path: Path to the configuration file
        """
        super().__init__(
            name="topic",
            description="Analyze topics in documents",
            input_model=TopicToolInput
        )
        self.modeler = TopicModeler(config_path=config_path)
        self.logger = get_logger("topic_tool")

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the topic modeling.

        Args:
            input_data: Input data for topic modeling

        Returns:
            Dictionary containing the analysis results
        """
        try:
            # Validate input
            input_model = TopicToolInput(**input_data)

            # Analyze topics
            result = await self.modeler.analyze(
                documents=input_model.documents,
                num_topics=input_model.num_topics,
                min_topic_size=input_model.min_topic_size
            )

            return {
                "status": "success",
                "result": result.dict()
            }

        except Exception as e:
            self.logger.error(f"Error analyzing topics: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def close(self):
        """Close the topic modeling tool."""
        await self.modeler.close() 
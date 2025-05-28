from typing import Dict, Any, Optional, Type
from abc import ABC, abstractmethod
from pydantic import BaseModel

from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class MCPTool(ABC):
    """Base class for all MCP tools."""

    def __init__(
        self,
        name: str,
        description: str,
        input_model: Optional[Type[BaseModel]] = None
    ):
        """
        Initialize the MCP tool.

        Args:
            name: Name of the tool
            description: Description of the tool's functionality
            input_model: Optional Pydantic model for input validation
        """
        self.name = name
        self.description = description
        self.input_model = input_model
        self.logger = get_logger(f"tool.{name}")

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool with the given input data.

        Args:
            input_data: Input data for the tool

        Returns:
            Dictionary containing the execution results

        Raises:
            ValueError: If input data is invalid
            Exception: For other execution errors
        """
        pass

    async def close(self) -> None:
        """Close the tool and clean up resources."""
        pass

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input data against the input model.

        Args:
            input_data: Input data to validate

        Returns:
            True if input is valid, False otherwise
        """
        if not self.input_model:
            return True

        try:
            self.input_model(**input_data)
            return True
        except Exception as e:
            self.logger.error(f"Input validation failed: {str(e)}")
            return False

    def get_schema(self) -> Optional[Dict[str, Any]]:
        """
        Get the input schema for the tool.

        Returns:
            Tool input schema or None if no input model
        """
        if not self.input_model:
            return None
        return self.input_model.schema()

    def __str__(self) -> str:
        """String representation of the tool."""
        return f"{self.name}: {self.description}"

    def __repr__(self) -> str:
        """Detailed string representation of the tool."""
        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"description='{self.description}', "
            f"input_model={self.input_model.__name__ if self.input_model else None}"
            ")"
        ) 
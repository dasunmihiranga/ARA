from typing import Dict, Any, List, Optional, Protocol
from pydantic import BaseModel

from research_assistant.tools.base_tool import MCPTool
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class MCPTool(Protocol):
    """Protocol defining the interface for MCP tools."""
    
    name: str
    description: str
    version: str
    
    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Any:
        """Execute the tool with given parameters and context."""
        ...

class ToolRegistry:
    """Registry for managing MCP tools."""

    def __init__(self):
        """Initialize the tool registry."""
        self._tools: Dict[str, MCPTool] = {}
        self.logger = get_logger("tool_registry")

    def register_tool(self, tool: MCPTool) -> None:
        """
        Register a new tool.

        Args:
            tool: Tool instance to register
        """
        if not isinstance(tool, MCPTool):
            raise ValueError("Tool must be an instance of MCPTool")

        tool_name = tool.name
        if tool_name in self._tools:
            self.logger.warning(f"Tool {tool_name} already registered. Overwriting.")

        self._tools[tool_name] = tool
        self.logger.info(f"Registered tool: {tool_name}")

    def register_tools(self, tools: list[MCPTool]) -> None:
        """
        Register multiple tools.

        Args:
            tools: List of tool instances to register
        """
        for tool in tools:
            self.register_tool(tool)

    def get_tool(self, name: str) -> Optional[MCPTool]:
        """
        Get a tool by name.

        Args:
            name: Name of the tool

        Returns:
            Tool instance or None if not found
        """
        tool = self._tools.get(name)
        if not tool:
            self.logger.warning(f"Tool not found: {name}")
        return tool

    def list_tools(self) -> Dict[str, Dict[str, Any]]:
        """
        List all registered tools.

        Returns:
            Dictionary of tool information
        """
        return {
            name: {
                "description": tool.description,
                "input_model": tool.input_model.__name__ if tool.input_model else None
            }
            for name, tool in self._tools.items()
        }

    def unregister_tool(self, name: str) -> bool:
        """
        Unregister a tool.

        Args:
            name: Name of the tool to unregister

        Returns:
            True if tool was unregistered, False if not found
        """
        if name in self._tools:
            del self._tools[name]
            self.logger.info(f"Unregistered tool: {name}")
            return True
        return False

    def clear_tools(self) -> None:
        """Clear all registered tools."""
        self._tools.clear()
        self.logger.info("Cleared all tools")

    async def close(self) -> None:
        """Close all registered tools."""
        for name, tool in self._tools.items():
            try:
                await tool.close()
                self.logger.info(f"Closed tool: {name}")
            except Exception as e:
                self.logger.error(f"Error closing tool {name}: {str(e)}")

    def validate_tool_input(self, name: str, input_data: Dict[str, Any]) -> bool:
        """
        Validate tool input data.

        Args:
            name: Name of the tool
            input_data: Input data to validate

        Returns:
            True if input is valid, False otherwise
        """
        tool = self.get_tool(name)
        if not tool or not tool.input_model:
            return False

        try:
            tool.input_model(**input_data)
            return True
        except Exception as e:
            self.logger.error(f"Invalid input for tool {name}: {str(e)}")
            return False

    def get_tool_schema(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get the input schema for a tool.

        Args:
            name: Name of the tool

        Returns:
            Tool input schema or None if not found
        """
        tool = self.get_tool(name)
        if not tool or not tool.input_model:
            return None

        return tool.input_model.schema() 
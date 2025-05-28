from typing import Dict, Any, List, Optional, Protocol
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

    def register_tool(self, tool: MCPTool) -> None:
        """
        Register a new MCP tool.

        Args:
            tool: The tool to register

        Raises:
            ValueError: If tool with same name is already registered
        """
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")
        
        logger.info(f"Registering tool: {tool.name}")
        self._tools[tool.name] = tool

    def unregister_tool(self, tool_name: str) -> bool:
        """
        Unregister an MCP tool.

        Args:
            tool_name: Name of the tool to unregister

        Returns:
            True if tool was unregistered, False if not found
        """
        if tool_name in self._tools:
            logger.info(f"Unregistering tool: {tool_name}")
            del self._tools[tool_name]
            return True
        return False

    def get_tool(self, tool_name: str) -> Optional[MCPTool]:
        """
        Get a registered tool by name.

        Args:
            tool_name: Name of the tool to get

        Returns:
            The tool if found, None otherwise
        """
        return self._tools.get(tool_name)

    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List all registered tools with their descriptions.

        Returns:
            List of tool descriptions
        """
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "version": tool.version
            }
            for tool in self._tools.values()
        ]

    def get_tool_count(self) -> int:
        """
        Get the number of registered tools.

        Returns:
            Number of registered tools
        """
        return len(self._tools) 
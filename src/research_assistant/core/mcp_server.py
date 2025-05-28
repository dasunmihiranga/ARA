from typing import Dict, Any, Optional
from research_assistant.utils.logging import get_logger
from research_assistant.core.tool_registry import ToolRegistry
from research_assistant.core.error_handler import ErrorHandler

logger = get_logger(__name__)

class MCPServer:
    """Core MCP server implementation for handling tool execution and context management."""

    def __init__(self, tool_registry: ToolRegistry, error_handler: ErrorHandler):
        """
        Initialize the MCP server.

        Args:
            tool_registry: Registry of available MCP tools
            error_handler: Error handling component
        """
        self.tool_registry = tool_registry
        self.error_handler = error_handler
        self._active_contexts: Dict[str, Dict[str, Any]] = {}

    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        context_id: Optional[str] = None
    ) -> Any:
        """
        Execute an MCP tool with the given parameters and context.

        Args:
            tool_name: Name of the tool to execute
            parameters: Tool-specific parameters
            context_id: Optional context ID for maintaining state

        Returns:
            Tool execution result

        Raises:
            ValueError: If tool is not found
            Exception: For other execution errors
        """
        try:
            # Get tool from registry
            tool = self.tool_registry.get_tool(tool_name)
            if not tool:
                raise ValueError(f"Tool not found: {tool_name}")

            # Get context if provided
            context = self._active_contexts.get(context_id) if context_id else None

            # Execute tool
            logger.info(f"Executing tool: {tool_name}")
            result = await tool.execute(parameters, context)

            # Update context if provided
            if context_id and hasattr(tool, 'update_context'):
                self._active_contexts[context_id] = tool.update_context(context, result)

            return result

        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            raise self.error_handler.handle_error(e)

    def create_context(self, initial_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new context for tool execution.

        Args:
            initial_data: Optional initial context data

        Returns:
            Context ID
        """
        import uuid
        context_id = str(uuid.uuid4())
        self._active_contexts[context_id] = initial_data or {}
        return context_id

    def get_context(self, context_id: str) -> Optional[Dict[str, Any]]:
        """
        Get context data by ID.

        Args:
            context_id: Context identifier

        Returns:
            Context data or None if not found
        """
        return self._active_contexts.get(context_id)

    def clear_context(self, context_id: str) -> bool:
        """
        Clear a specific context.

        Args:
            context_id: Context identifier

        Returns:
            True if context was cleared, False if not found
        """
        if context_id in self._active_contexts:
            del self._active_contexts[context_id]
            return True
        return False

    def clear_all_contexts(self) -> None:
        """Clear all active contexts."""
        self._active_contexts.clear() 
from typing import Dict, Any, Optional, List, Callable, Awaitable
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from research_assistant.core.tool_registry import ToolRegistry
from research_assistant.core.error_handler import ErrorHandler
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class MCPRequest(BaseModel):
    """Model for MCP request messages."""
    tool: str = Field(..., description="Name of the tool to execute")
    input: Dict[str, Any] = Field(..., description="Input data for the tool")
    session_id: Optional[str] = Field(default=None, description="Optional session ID")

class MCPResponse(BaseModel):
    """Model for MCP response messages."""
    status: str = Field(..., description="Status of the response (success/error)")
    result: Optional[Dict[str, Any]] = Field(default=None, description="Result data if successful")
    error: Optional[str] = Field(default=None, description="Error message if failed")

class MCPServer:
    """MCP server implementation."""

    def __init__(
        self,
        tool_registry: ToolRegistry,
        error_handler: ErrorHandler,
        host: str = "0.0.0.0",
        port: int = 8000
    ):
        """
        Initialize the MCP server.

        Args:
            tool_registry: Tool registry instance
            error_handler: Error handler instance
            host: Server host address
            port: Server port number
        """
        self.tool_registry = tool_registry
        self.error_handler = error_handler
        self.host = host
        self.port = port
        self.app = FastAPI()
        self.active_connections: List[WebSocket] = []
        self.logger = get_logger("mcp_server")

        # Register WebSocket endpoint
        self.app.websocket("/ws")(self.websocket_endpoint)

    async def connect(self, websocket: WebSocket):
        """Connect a new WebSocket client."""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.logger.info(f"New client connected. Total connections: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket):
        """Disconnect a WebSocket client."""
        self.active_connections.remove(websocket)
        self.logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all connected clients."""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                self.logger.error(f"Error broadcasting message: {str(e)}")

    async def websocket_endpoint(self, websocket: WebSocket):
        """Handle WebSocket connections and messages."""
        await self.connect(websocket)
        try:
            while True:
                # Receive message
                message = await websocket.receive_text()
                self.logger.debug(f"Received message: {message}")

                try:
                    # Parse request
                    request_data = json.loads(message)
                    request = MCPRequest(**request_data)

                    # Execute tool
                    result = await self.execute_tool(request)

                    # Send response
                    await websocket.send_json(result.dict())

                except json.JSONDecodeError:
                    error_response = MCPResponse(
                        status="error",
                        error="Invalid JSON message"
                    )
                    await websocket.send_json(error_response.dict())

                except Exception as e:
                    error_response = MCPResponse(
                        status="error",
                        error=str(e)
                    )
                    await websocket.send_json(error_response.dict())

        except WebSocketDisconnect:
            await self.disconnect(websocket)

    async def execute_tool(self, request: MCPRequest) -> MCPResponse:
        """
        Execute a tool request.

        Args:
            request: MCP request object

        Returns:
            MCPResponse object
        """
        try:
            # Get tool
            tool = self.tool_registry.get_tool(request.tool)
            if not tool:
                raise ValueError(f"Tool not found: {request.tool}")

            # Execute tool
            result = await tool.execute(request.input)

            return MCPResponse(
                status="success",
                result=result
            )

        except Exception as e:
            # Handle error
            error_message = self.error_handler.handle_error(e)
            return MCPResponse(
                status="error",
                error=error_message
            )

    async def start(self):
        """Start the MCP server."""
        import uvicorn
        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()

    async def stop(self):
        """Stop the MCP server."""
        # Close all active connections
        for connection in self.active_connections:
            try:
                await connection.close()
            except Exception as e:
                self.logger.error(f"Error closing connection: {str(e)}")
        self.active_connections.clear()

        # Close tool registry
        await self.tool_registry.close() 
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any

from research_assistant.core.mcp_server import MCPServer
from research_assistant.core.tool_registry import ToolRegistry
from research_assistant.core.error_handler import ErrorHandler
from research_assistant.utils.logging import setup_logging, get_logger

# Set up logging
setup_logging()
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Research Assistant MCP Server",
    description="A powerful research assistant using Machine Conversation Protocol",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core components
tool_registry = ToolRegistry()
error_handler = ErrorHandler()
mcp_server = MCPServer(tool_registry, error_handler)

class MCPRequest(BaseModel):
    """Model for MCP protocol requests."""
    tool: str
    parameters: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None

class MCPResponse(BaseModel):
    """Model for MCP protocol responses."""
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None

@app.post("/mcp", response_model=MCPResponse)
async def handle_mcp_request(request: MCPRequest) -> MCPResponse:
    """
    Handle MCP protocol requests.
    
    Args:
        request: The MCP request containing tool name and parameters
        
    Returns:
        MCPResponse: The response from the MCP server
    """
    try:
        logger.info(f"Received MCP request for tool: {request.tool}")
        result = await mcp_server.execute_tool(
            request.tool,
            request.parameters,
            request.context
        )
        return MCPResponse(status="success", result=result)
    except Exception as e:
        error_msg = error_handler.handle_error(e)
        logger.error(f"Error processing MCP request: {error_msg}")
        return MCPResponse(status="error", error=error_msg)

@app.get("/tools", response_model=List[Dict[str, Any]])
async def list_available_tools() -> List[Dict[str, Any]]:
    """
    List all available MCP tools.
    
    Returns:
        List of tool descriptions
    """
    try:
        return tool_registry.list_tools()
    except Exception as e:
        error_msg = error_handler.handle_error(e)
        logger.error(f"Error listing tools: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.
    
    Returns:
        Status of the server
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
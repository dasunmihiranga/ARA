from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl

class SearchQuery(BaseModel):
    """Search query model."""
    query: str = Field(..., description="Search query string")
    max_results: int = Field(10, description="Maximum number of results to return")
    sources: List[str] = Field(["duckduckgo", "searx"], description="Search sources to use")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional search filters")

class SearchResult(BaseModel):
    """Search result model."""
    title: str = Field(..., description="Result title")
    url: HttpUrl = Field(..., description="Result URL")
    snippet: str = Field(..., description="Result snippet/description")
    source: str = Field(..., description="Source of the result")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class ResearchSession(BaseModel):
    """Research session model."""
    session_id: str = Field(..., description="Unique session identifier")
    query: SearchQuery = Field(..., description="Initial search query")
    results: List[SearchResult] = Field(default_factory=list, description="Search results")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Session creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Session metadata")

class ResearchContext(BaseModel):
    """Research context model."""
    session_id: str = Field(..., description="Associated session ID")
    current_focus: str = Field(..., description="Current research focus")
    history: List[Dict[str, Any]] = Field(default_factory=list, description="Research history")
    active_sources: List[str] = Field(default_factory=list, description="Active research sources")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Active filters")

class ResearchTask(BaseModel):
    """Research task model."""
    task_id: str = Field(..., description="Unique task identifier")
    session_id: str = Field(..., description="Associated session ID")
    type: str = Field(..., description="Task type (search, analysis, etc.)")
    parameters: Dict[str, Any] = Field(..., description="Task parameters")
    status: str = Field("pending", description="Task status")
    result: Optional[Dict[str, Any]] = Field(None, description="Task result")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Task creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Task completion timestamp")

class ResearchSource(BaseModel):
    """Research source model."""
    source_id: str = Field(..., description="Unique source identifier")
    name: str = Field(..., description="Source name")
    type: str = Field(..., description="Source type (web, academic, etc.)")
    url: Optional[HttpUrl] = Field(None, description="Source URL")
    api_key: Optional[str] = Field(None, description="API key if required")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Source parameters")
    is_active: bool = Field(True, description="Whether source is active")

class ResearchFilter(BaseModel):
    """Research filter model."""
    filter_id: str = Field(..., description="Unique filter identifier")
    name: str = Field(..., description="Filter name")
    type: str = Field(..., description="Filter type")
    parameters: Dict[str, Any] = Field(..., description="Filter parameters")
    is_active: bool = Field(True, description="Whether filter is active")

class ResearchMetadata(BaseModel):
    """Research metadata model."""
    session_id: str = Field(..., description="Associated session ID")
    query_count: int = Field(0, description="Number of queries executed")
    result_count: int = Field(0, description="Total number of results")
    source_usage: Dict[str, int] = Field(default_factory=dict, description="Usage statistics by source")
    filter_usage: Dict[str, int] = Field(default_factory=dict, description="Usage statistics by filter")
    start_time: datetime = Field(default_factory=datetime.utcnow, description="Research start time")
    end_time: Optional[datetime] = Field(None, description="Research end time")
    duration: Optional[float] = Field(None, description="Research duration in seconds") 
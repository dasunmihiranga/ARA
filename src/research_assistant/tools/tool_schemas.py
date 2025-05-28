from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime

class SearchQuery(BaseModel):
    """Schema for search queries."""
    query: str = Field(..., description="Search query string")
    max_results: int = Field(10, description="Maximum number of results to return")
    sources: List[str] = Field(["duckduckgo", "searx"], description="Search sources to use")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional search filters")

class SearchResult(BaseModel):
    """Schema for search results."""
    title: str = Field(..., description="Result title")
    url: str = Field(..., description="Result URL")
    snippet: str = Field(..., description="Result snippet")
    source: str = Field(..., description="Source of the result")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class ContentExtractionRequest(BaseModel):
    """Schema for content extraction requests."""
    url: Optional[str] = Field(None, description="URL to extract content from")
    file_path: Optional[str] = Field(None, description="File path to extract content from")
    extraction_type: str = Field(..., description="Type of content to extract")
    options: Optional[Dict[str, Any]] = Field(None, description="Extraction options")

class ExtractedContent(BaseModel):
    """Schema for extracted content."""
    content: str = Field(..., description="Extracted text content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Content metadata")
    source: str = Field(..., description="Source of the content")
    extraction_time: datetime = Field(default_factory=datetime.utcnow)

class AnalysisRequest(BaseModel):
    """Schema for analysis requests."""
    content: str = Field(..., description="Content to analyze")
    analysis_type: str = Field(..., description="Type of analysis to perform")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Analysis parameters")

class AnalysisResult(BaseModel):
    """Schema for analysis results."""
    summary: str = Field(..., description="Analysis summary")
    insights: List[str] = Field(..., description="Key insights")
    confidence: float = Field(..., description="Confidence score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Analysis metadata")

class FactCheckRequest(BaseModel):
    """Schema for fact-checking requests."""
    claim: str = Field(..., description="Claim to verify")
    context: Optional[str] = Field(None, description="Additional context")
    sources: Optional[List[str]] = Field(None, description="Sources to check against")

class FactCheckResult(BaseModel):
    """Schema for fact-checking results."""
    claim: str = Field(..., description="Original claim")
    verdict: str = Field(..., description="Verification verdict")
    confidence: float = Field(..., description="Confidence score")
    sources: List[Dict[str, Any]] = Field(..., description="Supporting sources")
    explanation: str = Field(..., description="Explanation of the verdict")

class ReportRequest(BaseModel):
    """Schema for report generation requests."""
    content: Dict[str, Any] = Field(..., description="Content to include in report")
    template: str = Field(..., description="Report template to use")
    format: str = Field("pdf", description="Output format")
    options: Optional[Dict[str, Any]] = Field(None, description="Report options")

class ReportResult(BaseModel):
    """Schema for report generation results."""
    report_id: str = Field(..., description="Unique report identifier")
    content: bytes = Field(..., description="Report content")
    format: str = Field(..., description="Report format")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Report metadata")

class KnowledgeGraphRequest(BaseModel):
    """Schema for knowledge graph requests."""
    content: Dict[str, Any] = Field(..., description="Content to graph")
    graph_type: str = Field(..., description="Type of graph to generate")
    options: Optional[Dict[str, Any]] = Field(None, description="Graph options")

class KnowledgeGraphResult(BaseModel):
    """Schema for knowledge graph results."""
    nodes: List[Dict[str, Any]] = Field(..., description="Graph nodes")
    edges: List[Dict[str, Any]] = Field(..., description="Graph edges")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Graph metadata")

class SessionRequest(BaseModel):
    """Schema for session management requests."""
    action: str = Field(..., description="Session action to perform")
    session_id: Optional[str] = Field(None, description="Session identifier")
    data: Optional[Dict[str, Any]] = Field(None, description="Session data")

class SessionResult(BaseModel):
    """Schema for session management results."""
    session_id: str = Field(..., description="Session identifier")
    status: str = Field(..., description="Session status")
    data: Optional[Dict[str, Any]] = Field(None, description="Session data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Session metadata")

class ToolResponse(BaseModel):
    """Schema for tool responses."""
    success: bool = Field(..., description="Whether the operation was successful")
    data: Optional[Any] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if any")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Response metadata") 
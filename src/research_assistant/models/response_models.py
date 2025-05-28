from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field

class BaseResponse(BaseModel):
    """Base API response model."""
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

class ErrorResponse(BaseResponse):
    """Error response model."""
    error_code: str = Field(..., description="Error code")
    error_details: Dict[str, Any] = Field(default_factory=dict, description="Error details")
    stack_trace: Optional[str] = Field(None, description="Stack trace if available")

class SearchResponse(BaseResponse):
    """Search response model."""
    query: str = Field(..., description="Search query")
    results: List[Dict[str, Any]] = Field(default_factory=list, description="Search results")
    total_results: int = Field(0, description="Total number of results")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(10, description="Results per page")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Response metadata")

class AnalysisResponse(BaseResponse):
    """Analysis response model."""
    content_id: str = Field(..., description="Analyzed content ID")
    analysis_type: str = Field(..., description="Type of analysis performed")
    results: Dict[str, Any] = Field(..., description="Analysis results")
    confidence: float = Field(..., description="Confidence score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Response metadata")

class ReportResponse(BaseResponse):
    """Report response model."""
    report_id: str = Field(..., description="Generated report ID")
    report_type: str = Field(..., description="Type of report")
    content: Dict[str, Any] = Field(..., description="Report content")
    format: str = Field(..., description="Report format")
    download_url: Optional[str] = Field(None, description="Report download URL")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Response metadata")

class SessionResponse(BaseResponse):
    """Session response model."""
    session_id: str = Field(..., description="Session ID")
    status: str = Field(..., description="Session status")
    data: Dict[str, Any] = Field(..., description="Session data")
    expires_at: Optional[datetime] = Field(None, description="Session expiration timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Response metadata")

class ProgressResponse(BaseResponse):
    """Progress response model."""
    task_id: str = Field(..., description="Task ID")
    progress: float = Field(..., description="Progress percentage")
    status: str = Field(..., description="Current status")
    current_step: str = Field(..., description="Current processing step")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Response metadata")

class ValidationResponse(BaseResponse):
    """Validation response model."""
    is_valid: bool = Field(..., description="Whether the input is valid")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="Validation errors")
    warnings: List[Dict[str, Any]] = Field(default_factory=list, description="Validation warnings")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Response metadata")

class HealthResponse(BaseResponse):
    """Health check response model."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    uptime: float = Field(..., description="Service uptime in seconds")
    components: Dict[str, str] = Field(default_factory=dict, description="Component statuses")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Response metadata")

class MetricsResponse(BaseResponse):
    """Metrics response model."""
    metrics: Dict[str, Any] = Field(..., description="Service metrics")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Metrics timestamp")
    interval: str = Field(..., description="Metrics collection interval")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Response metadata") 
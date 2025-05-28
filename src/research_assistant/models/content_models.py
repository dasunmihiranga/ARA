from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl

class ContentSource(BaseModel):
    """Content source model."""
    url: Optional[HttpUrl] = Field(None, description="Source URL")
    file_path: Optional[str] = Field(None, description="Local file path")
    source_type: str = Field(..., description="Type of source (web, pdf, doc, etc.)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Source metadata")

class ExtractedContent(BaseModel):
    """Extracted content model."""
    content_id: str = Field(..., description="Unique content identifier")
    source: ContentSource = Field(..., description="Content source")
    title: str = Field(..., description="Content title")
    text: str = Field(..., description="Extracted text content")
    html: Optional[str] = Field(None, description="Extracted HTML content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Content metadata")
    extracted_at: datetime = Field(default_factory=datetime.utcnow, description="Extraction timestamp")

class ContentSection(BaseModel):
    """Content section model."""
    section_id: str = Field(..., description="Unique section identifier")
    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Section content")
    type: str = Field("text", description="Section type (text, table, list, etc.)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Section metadata")

class ContentStructure(BaseModel):
    """Content structure model."""
    content_id: str = Field(..., description="Associated content ID")
    sections: List[ContentSection] = Field(default_factory=list, description="Content sections")
    hierarchy: Dict[str, Any] = Field(default_factory=dict, description="Content hierarchy")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Structure metadata")

class ContentMetadata(BaseModel):
    """Content metadata model."""
    content_id: str = Field(..., description="Associated content ID")
    language: str = Field("en", description="Content language")
    word_count: int = Field(0, description="Word count")
    char_count: int = Field(0, description="Character count")
    section_count: int = Field(0, description="Number of sections")
    created_at: Optional[datetime] = Field(None, description="Content creation timestamp")
    modified_at: Optional[datetime] = Field(None, description="Content modification timestamp")
    author: Optional[str] = Field(None, description="Content author")
    tags: List[str] = Field(default_factory=list, description="Content tags")

class ContentReference(BaseModel):
    """Content reference model."""
    reference_id: str = Field(..., description="Unique reference identifier")
    content_id: str = Field(..., description="Associated content ID")
    reference_type: str = Field(..., description="Reference type (citation, link, etc.)")
    reference_data: Dict[str, Any] = Field(..., description="Reference data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Reference metadata")

class ContentVersion(BaseModel):
    """Content version model."""
    version_id: str = Field(..., description="Unique version identifier")
    content_id: str = Field(..., description="Associated content ID")
    version_number: int = Field(..., description="Version number")
    content: str = Field(..., description="Version content")
    changes: Dict[str, Any] = Field(default_factory=dict, description="Version changes")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Version creation timestamp")
    created_by: Optional[str] = Field(None, description="Version creator")

class ContentRelationship(BaseModel):
    """Content relationship model."""
    relationship_id: str = Field(..., description="Unique relationship identifier")
    source_content_id: str = Field(..., description="Source content ID")
    target_content_id: str = Field(..., description="Target content ID")
    relationship_type: str = Field(..., description="Relationship type")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Relationship metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Relationship creation timestamp") 
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field

class AnalysisResult(BaseModel):
    """Base analysis result model."""
    result_id: str = Field(..., description="Unique result identifier")
    content_id: str = Field(..., description="Associated content ID")
    analysis_type: str = Field(..., description="Type of analysis")
    result: Dict[str, Any] = Field(..., description="Analysis result")
    confidence: float = Field(..., description="Confidence score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Result metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Result creation timestamp")

class SummaryResult(AnalysisResult):
    """Summary analysis result model."""
    summary: str = Field(..., description="Content summary")
    key_points: List[str] = Field(default_factory=list, description="Key points")
    length: int = Field(..., description="Summary length in words")
    focus_areas: List[str] = Field(default_factory=list, description="Focus areas")

class SentimentResult(AnalysisResult):
    """Sentiment analysis result model."""
    overall_sentiment: str = Field(..., description="Overall sentiment")
    sentiment_score: float = Field(..., description="Sentiment score")
    sentiment_by_section: Dict[str, float] = Field(default_factory=dict, description="Sentiment by section")
    emotion_scores: Dict[str, float] = Field(default_factory=dict, description="Emotion scores")

class TopicResult(AnalysisResult):
    """Topic analysis result model."""
    topics: List[Dict[str, Any]] = Field(default_factory=list, description="Identified topics")
    topic_distribution: Dict[str, float] = Field(default_factory=dict, description="Topic distribution")
    key_terms: List[str] = Field(default_factory=list, description="Key terms")
    topic_relationships: Dict[str, List[str]] = Field(default_factory=dict, description="Topic relationships")

class InsightResult(AnalysisResult):
    """Insight analysis result model."""
    insights: List[Dict[str, Any]] = Field(default_factory=list, description="Key insights")
    categories: List[str] = Field(default_factory=list, description="Insight categories")
    importance_scores: Dict[str, float] = Field(default_factory=dict, description="Importance scores")
    supporting_evidence: Dict[str, List[str]] = Field(default_factory=dict, description="Supporting evidence")

class FactCheckResult(AnalysisResult):
    """Fact-checking result model."""
    claim: str = Field(..., description="Claim being checked")
    verdict: str = Field(..., description="Fact-check verdict")
    confidence: float = Field(..., description="Confidence in verdict")
    supporting_sources: List[Dict[str, Any]] = Field(default_factory=list, description="Supporting sources")
    explanation: str = Field(..., description="Explanation of verdict")

class ComparisonResult(AnalysisResult):
    """Content comparison result model."""
    comparison_type: str = Field(..., description="Type of comparison")
    similarity_score: float = Field(..., description="Similarity score")
    differences: List[Dict[str, Any]] = Field(default_factory=list, description="Key differences")
    common_elements: List[Dict[str, Any]] = Field(default_factory=list, description="Common elements")
    comparison_metrics: Dict[str, float] = Field(default_factory=dict, description="Comparison metrics")

class TrendResult(AnalysisResult):
    """Trend analysis result model."""
    trends: List[Dict[str, Any]] = Field(default_factory=list, description="Identified trends")
    trend_direction: str = Field(..., description="Overall trend direction")
    significance_score: float = Field(..., description="Trend significance score")
    supporting_data: Dict[str, Any] = Field(default_factory=dict, description="Supporting data")

class AnalysisMetadata(BaseModel):
    """Analysis metadata model."""
    analysis_id: str = Field(..., description="Associated analysis ID")
    model_used: str = Field(..., description="Model used for analysis")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Analysis parameters")
    performance_metrics: Dict[str, float] = Field(default_factory=dict, description="Performance metrics")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Analysis creation timestamp")
    duration: float = Field(..., description="Analysis duration in seconds") 
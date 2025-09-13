"""
Analysis Schemas

This module defines Pydantic models for request/response schemas
related to content analysis in ScholarIQ.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class AnalysisStatus(str, Enum):
    """Status of an analysis task."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisRequest(BaseModel):
    """Request schema for content analysis."""
    text: Optional[str] = Field(
        None,
        description="Text content to analyze (for text analysis)"
    )
    content: Optional[Union[bytes, str]] = Field(
        None,
        description="Raw content (for file uploads)"
    )
    content_type: Optional[str] = Field(
        None,
        description="MIME type of the content"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        {},
        description="Additional metadata about the content"
    )
    options: Optional[Dict[str, Any]] = Field(
        {},
        description="Analysis options specific to the content type"
    )

    class Config:
        schema_extra = {
            "example": {
                "text": "Machine learning is a subset of artificial intelligence...",
                "content_type": "text/plain",
                "metadata": {
                    "title": "Introduction to Machine Learning",
                    "author": "AI Research Team"
                },
                "options": {
                    "extract_key_phrases": True,
                    "analyze_sentiment": True
                }
            }
        }


class AnalysisResponse(BaseModel):
    """Response schema for content analysis."""
    task_id: str = Field(
        ...,
        description="Unique identifier for the analysis task"
    )
    status: AnalysisStatus = Field(
        ...,
        description="Current status of the analysis"
    )
    content_type: Optional[str] = Field(
        None,
        description="MIME type of the analyzed content"
    )
    results: Optional[Dict[str, Any]] = Field(
        None,
        description="Analysis results (available when status is 'completed')"
    )
    error: Optional[str] = Field(
        None,
        description="Error message (if status is 'failed')"
    )
    metadata: Dict[str, Any] = Field(
        {},
        description="Additional metadata about the analysis"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the analysis was created"
    )
    updated_at: Optional[datetime] = Field(
        None,
        description="Timestamp when the analysis was last updated"
    )

    class Config:
        schema_extra = {
            "example": {
                "task_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "completed",
                "content_type": "text/plain",
                "results": {
                    "key_phrases": [
                        {"phrase": "machine learning", "score": 0.95},
                        {"phrase": "artificial intelligence", "score": 0.87}
                    ],
                    "sentiment": {
                        "positive": 0.8,
                        "neutral": 0.15,
                        "negative": 0.05,
                        "compound": 0.9
                    },
                    "word_count": 245,
                    "reading_time_minutes": 1.2
                },
                "metadata": {
                    "model": "en_core_web_lg",
                    "version": "1.0.0"
                },
                "created_at": "2023-09-13T12:00:00Z",
                "updated_at": "2023-09-13T12:00:05Z"
            }
        }


class BatchAnalysisRequest(BaseModel):
    """Request schema for batch content analysis."""
    items: List[AnalysisRequest] = Field(
        ...,
        description="List of content items to analyze"
    )
    options: Optional[Dict[str, Any]] = Field(
        {},
        description="Global options to apply to all items in the batch"
    )

    class Config:
        schema_extra = {
            "example": {
                "items": [
                    {
                        "text": "First document content...",
                        "content_type": "text/plain"
                    },
                    {
                        "text": "Second document content...",
                        "content_type": "text/plain"
                    }
                ],
                "options": {
                    "extract_key_phrases": True
                }
            }
        }


class BatchAnalysisResponse(BaseModel):
    """Response schema for batch content analysis."""
    task_id: str = Field(
        ...,
        description="Unique identifier for the batch analysis task"
    )
    status: AnalysisStatus = Field(
        ...,
        description="Overall status of the batch analysis"
    )
    items: List[AnalysisResponse] = Field(
        ...,
        description="List of individual analysis responses"
    )
    metadata: Dict[str, Any] = Field(
        {},
        description="Additional metadata about the batch analysis"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the batch analysis was created"
    )
    completed_at: Optional[datetime] = Field(
        None,
        description="Timestamp when the batch analysis was completed"
    )

    class Config:
        schema_extra = {
            "example": {
                "task_id": "660e8400-e29b-41d4-a716-446655440001",
                "status": "completed",
                "items": [
                    {
                        "task_id": "550e8400-e29b-41d4-a716-446655440000",
                        "status": "completed",
                        "content_type": "text/plain",
                        "results": {"word_count": 120},
                        "created_at": "2023-09-13T12:00:00Z"
                    },
                    {
                        "task_id": "550e8400-e29b-41d4-a716-446655440001",
                        "status": "completed",
                        "content_type": "text/plain",
                        "results": {"word_count": 85},
                        "created_at": "2023-09-13T12:00:01Z"
                    }
                ],
                "metadata": {
                    "total_items": 2,
                    "successful_items": 2,
                    "failed_items": 0
                },
                "created_at": "2023-09-13T12:00:00Z",
                "completed_at": "2023-09-13T12:00:05Z"
            }
        }

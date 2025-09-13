"""
Demo endpoints for the ScholarIQ API.

This module provides demo and testing endpoints that return sample data
for development and demonstration purposes.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/demo", tags=["demo"])

class DemoResponse(BaseModel):
    """Response model for demo endpoints."""
    message: str
    data: Dict[str, Any] = {}

@router.get("/sample-text", response_model=DemoResponse)
async def get_sample_text() -> DemoResponse:
    """
    Get sample educational text for demonstration purposes.
    
    Returns:
        DemoResponse: Sample educational text with metadata.
    """
    return DemoResponse(
        message="Sample educational text retrieved successfully",
        data={
            "title": "Introduction to Machine Learning",
            "content": "Machine learning is a subset of artificial intelligence that focuses on building systems that learn from data...",
            "language": "en",
            "difficulty": "intermediate"
        }
    )

@router.get("/sample-analysis", response_model=DemoResponse)
async def get_sample_analysis() -> DemoResponse:
    """
    Get sample analysis results for demonstration purposes.
    
    Returns:
        DemoResponse: Sample analysis results with metadata.
    """
    return DemoResponse(
        message="Sample analysis results retrieved successfully",
        data={
            "analysis_id": "demo_12345",
            "status": "completed",
            "results": {
                "key_concepts": ["machine learning", "neural networks", "training data"],
                "difficulty_level": "intermediate",
                "reading_time_minutes": 8,
                "vocabulary_complexity": 0.75
            },
            "timestamp": "2023-09-13T10:00:00Z"
        }
    )

@router.get("/sample-questions", response_model=DemoResponse)
async def get_sample_questions() -> DemoResponse:
    """
    Get sample questions based on educational content.
    
    Returns:
        DemoResponse: Sample questions with answers.
    """
    return DemoResponse(
        message="Sample questions generated successfully",
        data={
            "questions": [
                {
                    "question": "What is the difference between supervised and unsupervised learning?",
                    "type": "short_answer",
                    "difficulty": "medium"
                },
                {
                    "question": "Which of the following is not a machine learning algorithm?",
                    "type": "multiple_choice",
                    "options": ["Random Forest", "Linear Regression", "Binary Search", "Neural Network"],
                    "correct_answer": 2,
                    "explanation": "Binary Search is a search algorithm, not a machine learning algorithm.",
                    "difficulty": "easy"
                }
            ]
        }
    )

@router.get("/sample-feedback", response_model=DemoResponse)
async def get_sample_feedback() -> DemoResponse:
    """
    Get sample feedback on a student's response.
    
    Returns:
        DemoResponse: Sample feedback with suggestions.
    """
    return DemoResponse(
        message="Sample feedback generated successfully",
        data={
            "original_answer": "Machine learning is when computers learn from data.",
            "feedback": {
                "score": 0.6,
                "strengths": ["Correctly identifies the core concept of learning from data"],
                "areas_for_improvement": [
                    "Could be more specific about how the learning process works",
                    "Mention the role of algorithms in machine learning"
                ],
                "suggested_resources": [
                    {"title": "Introduction to Machine Learning", "url": "#"},
                    {"title": "Types of Machine Learning Algorithms", "url": "#"}
                ]
            }
        }
    )

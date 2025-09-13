"""
Analysis endpoints for the ScholarIQ API.

This module provides endpoints for analyzing educational content including text,
images, audio, and video files.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from pydantic import BaseModel

from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.services.analysis_service import AnalysisService

router = APIRouter(prefix="/analyze", tags=["analysis"])

@router.post("/text", response_model=AnalysisResponse)
async def analyze_text(
    request: AnalysisRequest,
    analysis_service: AnalysisService = Depends()
) -> AnalysisResponse:
    """
    Analyze text content.
    
    Args:
        request: The analysis request containing the text to analyze.
        analysis_service: The analysis service dependency.
        
    Returns:
        AnalysisResponse: The analysis results.
    """
    try:
        return await analysis_service.analyze_text(request.text)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing text: {str(e)}"
        )

@router.post("/file", response_model=AnalysisResponse)
async def analyze_file(
    file: UploadFile = File(...),
    analysis_service: AnalysisService = Depends()
) -> AnalysisResponse:
    """
    Analyze a file (text, image, audio, or video).
    
    Args:
        file: The file to analyze.
        analysis_service: The analysis service dependency.
        
    Returns:
        AnalysisResponse: The analysis results.
    """
    try:
        content = await file.read()
        return await analysis_service.analyze_file(
            content=content,
            filename=file.filename,
            content_type=file.content_type
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing file: {str(e)}"
        )

@router.get("/status/{task_id}", response_model=AnalysisResponse)
async def get_analysis_status(
    task_id: str,
    analysis_service: AnalysisService = Depends()
) -> AnalysisResponse:
    """
    Get the status of a previously submitted analysis task.
    
    Args:
        task_id: The ID of the analysis task.
        analysis_service: The analysis service dependency.
        
    Returns:
        AnalysisResponse: The current status and results (if available) of the analysis.
    """
    try:
        return await analysis_service.get_analysis_status(task_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting analysis status: {str(e)}"
        )

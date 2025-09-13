"""
Analysis Service Module

This module provides the main analysis service for ScholarIQ, coordinating
between different analyzers and handling the analysis workflow.
"""

import logging
import os
import uuid
from typing import Any, Dict, List, Optional, Union, Type
from datetime import datetime
import mimetypes

from app.models.ai import (
    BaseAnalyzer,
    TextAnalyzer,
    AudioAnalyzer,
    VideoAnalyzer
)
from app.schemas.analysis import AnalysisRequest, AnalysisResponse, AnalysisStatus

logger = logging.getLogger(__name__)

class AnalysisService:
    """
    Service for coordinating content analysis across different modalities.
    
    This service handles the analysis of various content types (text, audio, video)
    by delegating to the appropriate analyzer implementations.
    """
    
    def __init__(self):
        """Initialize the analysis service with default analyzers."""
        self.analyzers = {
            "text": TextAnalyzer(),
            "audio": AudioAnalyzer(),
            "video": VideoAnalyzer(),
        }
        
        # Map of MIME types to analyzer types
        self.mime_type_map = {
            # Text types
            "text/plain": "text",
            "text/markdown": "text",
            "text/html": "text",
            "application/json": "text",
            
            # Audio types
            "audio/wav": "audio",
            "audio/mp3": "audio",
            "audio/mpeg": "audio",
            "audio/ogg": "audio",
            "audio/webm": "audio",
            
            # Video types
            "video/mp4": "video",
            "video/quicktime": "video",
            "video/x-msvideo": "video",  # AVI
            "video/x-ms-wmv": "video",   # WMV
            "video/webm": "video",
        }
        
        # In-memory storage for analysis tasks (in production, use a database)
        self.tasks = {}
    
    def _get_analyzer_for_content(
        self,
        content_type: Optional[str] = None,
        filename: Optional[str] = None
    ) -> Type[BaseAnalyzer]:
        """
        Determine the appropriate analyzer for the given content type or filename.
        
        Args:
            content_type: The MIME type of the content.
            filename: Optional filename to help determine content type.
            
        Returns:
            The appropriate analyzer class for the content.
            
        Raises:
            ValueError: If no suitable analyzer is found for the content type.
        """
        # Try to determine content type from filename if not provided
        if not content_type and filename:
            content_type, _ = mimetypes.guess_type(filename)
        
        if not content_type:
            content_type = "application/octet-stream"
        
        # Find the analyzer type for the content type
        analyzer_type = self.mime_type_map.get(content_type.lower())
        
        if not analyzer_type:
            # Try to determine from file extension if content type is unknown
            if filename:
                _, ext = os.path.splitext(filename.lower())
                if ext in ['.txt', '.md', '.html', '.json']:
                    analyzer_type = "text"
                elif ext in ['.wav', '.mp3', '.ogg', '.webm']:
                    analyzer_type = "audio"
                elif ext in ['.mp4', '.mov', '.avi', '.wmv', '.webm']:
                    analyzer_type = "video"
        
        if not analyzer_type:
            raise ValueError(f"Unsupported content type: {content_type}")
        
        return self.analyzers[analyzer_type]
    
    async def analyze_text(
        self,
        text: str,
        **kwargs
    ) -> AnalysisResponse:
        """
        Analyze text content.
        
        Args:
            text: The text content to analyze.
            **kwargs: Additional analysis parameters.
            
        Returns:
            AnalysisResponse containing the analysis results.
        """
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = {
            "status": AnalysisStatus.PROCESSING,
            "start_time": datetime.utcnow(),
            "content_type": "text/plain",
            "analyzer_type": "text",
        }
        
        try:
            analyzer = self.analyzers["text"]
            results = await analyzer.analyze(text, **kwargs)
            
            response = AnalysisResponse(
                task_id=task_id,
                status=AnalysisStatus.COMPLETED,
                content_type="text/plain",
                results=results,
                metadata={
                    "analyzer": analyzer.__class__.__name__,
                    "model": getattr(analyzer, "model_name", "default"),
                }
            )
            
            self.tasks[task_id].update({
                "status": AnalysisStatus.COMPLETED,
                "end_time": datetime.utcnow(),
                "response": response.dict()
            })
            
            return response
            
        except Exception as e:
            logger.exception("Error analyzing text")
            self.tasks[task_id].update({
                "status": AnalysisStatus.FAILED,
                "end_time": datetime.utcnow(),
                "error": str(e)
            })
            
            return AnalysisResponse(
                task_id=task_id,
                status=AnalysisStatus.FAILED,
                error=str(e)
            )
    
    async def analyze_file(
        self,
        content: bytes,
        filename: Optional[str] = None,
        content_type: Optional[str] = None,
        **kwargs
    ) -> AnalysisResponse:
        """
        Analyze a file (text, audio, or video).
        
        Args:
            content: The file content as bytes.
            filename: The original filename (used to determine content type).
            content_type: The MIME type of the content.
            **kwargs: Additional analysis parameters.
            
        Returns:
            AnalysisResponse containing the analysis results.
        """
        task_id = str(uuid.uuid4())
        
        try:
            # Determine the appropriate analyzer
            analyzer = self._get_analyzer_for_content(content_type, filename)
            
            self.tasks[task_id] = {
                "status": AnalysisStatus.PROCESSING,
                "start_time": datetime.utcnow(),
                "content_type": content_type or "application/octet-stream",
                "analyzer_type": analyzer.__class__.__name__,
                "filename": filename
            }
            
            # Perform the analysis
            results = await analyzer.analyze(content, **kwargs)
            
            # Prepare the response
            response = AnalysisResponse(
                task_id=task_id,
                status=AnalysisStatus.COMPLETED,
                content_type=content_type,
                results=results,
                metadata={
                    "filename": filename,
                    "analyzer": analyzer.__class__.__name__,
                    "model": getattr(analyzer, "model_name", "default"),
                }
            )
            
            # Update task status
            self.tasks[task_id].update({
                "status": AnalysisStatus.COMPLETED,
                "end_time": datetime.utcnow(),
                "response": response.dict()
            })
            
            return response
            
        except Exception as e:
            logger.exception(f"Error analyzing file {filename}")
            
            if task_id in self.tasks:
                self.tasks[task_id].update({
                    "status": AnalysisStatus.FAILED,
                    "end_time": datetime.utcnow(),
                    "error": str(e)
                })
            
            return AnalysisResponse(
                task_id=task_id,
                status=AnalysisStatus.FAILED,
                error=str(e)
            )
    
    async def get_analysis_status(self, task_id: str) -> AnalysisResponse:
        """
        Get the status of a previously submitted analysis task.
        
        Args:
            task_id: The ID of the analysis task.
            
        Returns:
            AnalysisResponse with the current status and results (if available).
            
        Raises:
            ValueError: If the task ID is not found.
        """
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        if task["status"] == AnalysisStatus.COMPLETED:
            return AnalysisResponse(**task["response"])
        elif task["status"] == AnalysisStatus.FAILED:
            return AnalysisResponse(
                task_id=task_id,
                status=AnalysisStatus.FAILED,
                error=task.get("error", "Unknown error")
            )
        else:
            return AnalysisResponse(
                task_id=task_id,
                status=task["status"],
                metadata={
                    "start_time": task["start_time"].isoformat(),
                    "content_type": task.get("content_type"),
                    "analyzer_type": task.get("analyzer_type")
                }
            )
    
    async def get_available_analyzers(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about available analyzers and their capabilities.
        
        Returns:
            Dictionary mapping analyzer types to their capabilities.
        """
        return {
            name: analyzer.get_capabilities()
            for name, analyzer in self.analyzers.items()
        }

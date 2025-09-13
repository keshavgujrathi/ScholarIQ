"""
Base Analyzer Module

This module defines the abstract base class for all analyzer implementations in ScholarIQ.
All specific analyzers should inherit from this base class and implement its abstract methods.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
import logging

logger = logging.getLogger(__name__)

class BaseAnalyzer(ABC):
    """
    Abstract base class for all analyzers in ScholarIQ.
    
    This class defines the common interface that all analyzers must implement,
    regardless of the type of content they analyze (text, audio, video, etc.).
    """
    
    def __init__(self, model_name: Optional[str] = None, **kwargs):
        """
        Initialize the analyzer with optional model configuration.
        
        Args:
            model_name: Name or identifier of the model to use.
            **kwargs: Additional model-specific configuration parameters.
        """
        self.model_name = model_name
        self.model = self._load_model(**kwargs)
        logger.info(f"Initialized {self.__class__.__name__} with model: {model_name or 'default'}")
    
    @abstractmethod
    def _load_model(self, **kwargs) -> Any:
        """
        Load and initialize the underlying model.
        
        This method should be implemented by subclasses to load the specific
        model or models needed for analysis.
        
        Args:
            **kwargs: Additional model-specific configuration parameters.
            
        Returns:
            The loaded model object(s).
        """
        pass
    
    @abstractmethod
    async def analyze(self, content: Any, **kwargs) -> Dict[str, Any]:
        """
        Perform analysis on the provided content.
        
        This is the main method that performs the analysis. It should be implemented
        by subclasses to handle the specific type of content they're designed for.
        
        Args:
            content: The content to analyze. The type depends on the analyzer
                   (e.g., str for text, bytes for binary files).
            **kwargs: Additional analysis parameters.
            
        Returns:
            A dictionary containing the analysis results.
        """
        pass
    
    async def batch_analyze(self, contents: List[Any], **kwargs) -> List[Dict[str, Any]]:
        """
        Perform analysis on multiple content items.
        
        This method provides a default implementation that processes items sequentially.
        Subclasses may override this to implement more efficient batch processing.
        
        Args:
            contents: A list of content items to analyze.
            **kwargs: Additional analysis parameters.
            
        Returns:
            A list of analysis result dictionaries.
        """
        return [await self.analyze(content, **kwargs) for content in contents]
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get information about the analyzer's capabilities.
        
        Returns:
            A dictionary describing what types of analysis this analyzer can perform.
        """
        return {
            "analyzer_type": self.__class__.__name__,
            "model": self.model_name,
            "supports_batch": True,
            "content_types": []
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check the health/readiness of the analyzer.
        
        Returns:
            A dictionary containing health check information.
        """
        return {
            "status": "healthy",
            "analyzer": self.__class__.__name__,
            "model_loaded": self.model is not None,
            "model_name": self.model_name or "default"
        }

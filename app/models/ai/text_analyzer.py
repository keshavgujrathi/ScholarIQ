"""
Text Analyzer Module

This module provides text analysis capabilities for ScholarIQ, including
content analysis, key concept extraction, and difficulty assessment.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
import spacy
from .base_analyzer import BaseAnalyzer

logger = logging.getLogger(__name__)

class TextAnalyzer(BaseAnalyzer):
    """
    Text analysis implementation for ScholarIQ.
    
    This analyzer processes text content to extract educational insights,
    including key concepts, difficulty level, and other relevant metrics.
    """
    
    def __init__(self, model_name: Optional[str] = "en_core_web_sm", **kwargs):
        """
        Initialize the text analyzer with a spaCy language model.
        
        Args:
            model_name: Name of the spaCy language model to use.
            **kwargs: Additional model configuration parameters.
        """
        super().__init__(model_name=model_name, **kwargs)
        self.nlp = None  # Will be initialized in _load_model
    
    def _load_model(self, **kwargs) -> Any:
        """
        Load the spaCy language model.
        
        Args:
            **kwargs: Additional model configuration parameters.
            
        Returns:
            The loaded spaCy language model.
        """
        try:
            self.nlp = spacy.load(self.model_name)
            logger.info(f"Loaded spaCy model: {self.model_name}")
            return self.nlp
        except OSError:
            logger.warning(f"spaCy model {self.model_name} not found. Downloading...")
            import spacy.cli
            spacy.cli.download(self.model_name)
            self.nlp = spacy.load(self.model_name)
            return self.nlp
    
    async def analyze(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        Analyze the provided text content.
        
        Args:
            text: The text content to analyze.
            **kwargs: Additional analysis parameters.
                - extract_key_phrases: Whether to extract key phrases (default: True)
                - analyze_sentiment: Whether to perform sentiment analysis (default: False)
                - detect_language: Whether to detect the language (default: True)
                
        Returns:
            A dictionary containing the analysis results.
        """
        if not text.strip():
            raise ValueError("Empty text provided for analysis")
            
        doc = self.nlp(text)
        
        # Extract basic statistics
        stats = self._extract_basic_stats(doc)
        
        # Extract key phrases if requested
        extract_key_phrases = kwargs.get("extract_key_phrases", True)
        if extract_key_phrases:
            key_phrases = self._extract_key_phrases(doc)
            stats["key_phrases"] = key_phrases
        
        # Perform sentiment analysis if requested
        analyze_sentiment = kwargs.get("analyze_sentiment", False)
        if analyze_sentiment:
            sentiment = self._analyze_sentiment(doc)
            stats["sentiment"] = sentiment
        
        # Detect language if requested
        detect_language = kwargs.get("detect_language", True)
        if detect_language:
            language = self._detect_language(text)
            stats["language"] = language
        
        return stats
    
    def _extract_basic_stats(self, doc) -> Dict[str, Any]:
        """Extract basic statistics from the document."""
        sentences = list(doc.sents)
        words = [token for token in doc if not token.is_punct and not token.is_space]
        
        return {
            "char_count": len(doc.text),
            "word_count": len(words),
            "sentence_count": len(sentences),
            "avg_word_length": sum(len(token) for token in words) / len(words) if words else 0,
            "avg_sentence_length": len(words) / len(sentences) if sentences else 0,
            "vocab_size": len(set(token.text.lower() for token in words)),
            "reading_time_minutes": len(words) / 200,  # Average reading speed: 200 wpm
        }
    
    def _extract_key_phrases(self, doc, top_n: int = 10) -> List[Dict[str, Any]]:
        """Extract key phrases from the document."""
        # Simple implementation using noun chunks
        # In a production environment, consider using more sophisticated algorithms
        # like TextRank, YAKE!, or BERT-based approaches
        key_phrases = []
        seen = set()
        
        for chunk in doc.noun_chunks:
            phrase = chunk.text.lower().strip()
            if len(phrase.split()) > 1 and phrase not in seen:
                seen.add(phrase)
                key_phrases.append({
                    "phrase": phrase,
                    "count": 1,
                    "importance": 0.0  # Placeholder for actual importance score
                })
        
        # Sort by phrase length as a simple proxy for importance
        key_phrases.sort(key=lambda x: len(x["phrase"]), reverse=True)
        
        return key_phrases[:top_n]
    
    def _analyze_sentiment(self, doc) -> Dict[str, float]:
        """
        Perform basic sentiment analysis on the document.
        
        Note: This is a simple implementation. For production use, consider
        using a dedicated sentiment analysis model.
        """
        positive_words = {"good", "great", "excellent", "amazing", "wonderful"}
        negative_words = {"bad", "terrible", "awful", "poor", "worst"}
        
        pos_count = sum(1 for token in doc if token.text.lower() in positive_words)
        neg_count = sum(1 for token in doc if token.text.lower() in negative_words)
        total = len(doc)
        
        return {
            "positive": pos_count / total if total > 0 else 0,
            "negative": neg_count / total if total > 0 else 0,
            "neutral": 1 - (pos_count + neg_count) / total if total > 0 else 1,
        }
    
    def _detect_language(self, text: str, default: str = "en") -> str:
        """
        Detect the language of the text.
        
        Args:
            text: The text to analyze.
            default: Default language code to return if detection fails.
            
        Returns:
            ISO 639-1 language code (e.g., 'en', 'es', 'fr').
        """
        # This is a placeholder. In production, use a dedicated language detection library
        # like langdetect or fastText for more accurate results.
        try:
            # Simple heuristic: check for common words in different languages
            english_words = {"the", "be", "to", "of", "and", "a", "in", "that", "have", "I"}
            spanish_words = {"el", "la", "de", "que", "y", "a", "en", "un", "ser", "se"}
            
            words = set(text.lower().split())
            
            en_score = len(english_words.intersection(words))
            es_score = len(spanish_words.intersection(words))
            
            if en_score > es_score and en_score > 1:
                return "en"
            elif es_score > en_score and es_score > 1:
                return "es"
            else:
                return default
        except Exception as e:
            logger.warning(f"Language detection failed: {str(e)}")
            return default
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get information about the text analyzer's capabilities."""
        capabilities = super().get_capabilities()
        capabilities.update({
            "content_types": ["text/plain", "text/markdown", "text/html"],
            "features": [
                "basic_stats",
                "key_phrase_extraction",
                "sentiment_analysis",
                "language_detection"
            ]
        })
        return capabilities

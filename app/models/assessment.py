from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
from datetime import datetime
import enum

class AssessmentType(enum.Enum):
    QUIZ = "quiz"
    EXAM = "exam" 
    ASSIGNMENT = "assignment"
    PRACTICE = "practice"

class DifficultyLevel(enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class Assessment(BaseModel):
    __tablename__ = "assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Assessment metadata
    assessment_type = Column(Enum(AssessmentType), nullable=False)
    difficulty_level = Column(Enum(DifficultyLevel), default=DifficultyLevel.INTERMEDIATE)
    subject = Column(String(100), nullable=False, index=True)
    topic = Column(String(150), nullable=True, index=True)
    
    # Timing and constraints
    duration_minutes = Column(Integer, nullable=True)  # Time limit in minutes
    max_attempts = Column(Integer, default=1)
    passing_score = Column(Float, nullable=True)  # Percentage needed to pass
    
    # Question configuration
    total_questions = Column(Integer, default=0)
    randomize_questions = Column(Boolean, default=False)
    show_results_immediately = Column(Boolean, default=True)
    
    # Status and visibility
    is_active = Column(Boolean, default=True)
    is_published = Column(Boolean, default=False)
    
    # Relationships (if you have instructor/creator model)
    # created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    # creator = relationship("User", back_populates="created_assessments")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    
    # Optional: Start and end dates for availability
    available_from = Column(DateTime, nullable=True)
    available_until = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Assessment(id={self.id}, title='{self.title}', type='{self.assessment_type}')>"
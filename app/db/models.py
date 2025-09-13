"""
Database Models

This module defines the SQLAlchemy models for the ScholarIQ application.
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, 
    ForeignKey, Text, JSON, Table, func
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, declarative_base

from app.db.database import Base

# Association tables for many-to-many relationships
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True)
)

class User(Base):
    """User account model."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    analyses = relationship("Analysis", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.username}>"


class Role(Base):
    """User role model for authorization."""
    __tablename__ = "roles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    permissions = Column(JSONB, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")
    
    def __repr__(self):
        return f"<Role {self.name}>"


class Analysis(Base):
    """Analysis job model."""
    __tablename__ = "analyses"
    
    class Status(str):
        PENDING = "pending"
        PROCESSING = "processing"
        COMPLETED = "completed"
        FAILED = "failed"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String(20), default=Status.PENDING, nullable=False)
    content_type = Column(String(100), nullable=False)  # e.g., 'text/plain', 'audio/mp3'
    file_path = Column(String(512), nullable=True)  # Path to stored file if any
    file_size = Column(Integer, nullable=True)  # File size in bytes
    file_hash = Column(String(64), nullable=True)  # SHA-256 hash of file
    metadata_ = Column("metadata", JSONB, default=dict)  # Additional metadata
    results = Column(JSONB, nullable=True)  # Analysis results
    error = Column(Text, nullable=True)  # Error message if failed
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="analyses")
    
    @property
    def duration(self) -> Optional[float]:
        """Return the duration of the analysis in seconds."""
        if not self.started_at or not self.completed_at:
            return None
        return (self.completed_at - self.started_at).total_seconds()
    
    def __repr__(self):
        return f"<Analysis {self.id} - {self.status}>"


class Content(Base):
    """Content model for storing analyzed content."""
    __tablename__ = "contents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    content_type = Column(String(50), nullable=False)  # 'text', 'audio', 'video', etc.
    source_url = Column(String(512), nullable=True)
    source_type = Column(String(50), nullable=True)  # 'upload', 'url', 'api', etc.
    metadata_ = Column("metadata", JSONB, default=dict)  # Additional metadata
    is_public = Column(Boolean, default=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    analysis = relationship("Analysis", back_populates="content", uselist=False)
    
    def __repr__(self):
        return f"<Content {self.title} ({self.content_type})>"


class AnalysisResult(Base):
    """Detailed analysis results for content."""
    __tablename__ = "analysis_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analyses.id"), nullable=False)
    content_id = Column(UUID(as_uuid=True), ForeignKey("contents.id"), nullable=False)
    result_type = Column(String(50), nullable=False)  # 'summary', 'transcript', 'entities', etc.
    data = Column(JSONB, nullable=False)  # The actual result data
    confidence = Column(Float, nullable=True)  # Confidence score if applicable
    metadata_ = Column("metadata", JSONB, default=dict)  # Additional metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    analysis = relationship("Analysis", back_populates="results")
    content = relationship("Content", back_populates="results")
    
    def __repr__(self):
        return f"<AnalysisResult {self.result_type} for {self.analysis_id}>"


# Add back-references for relationships
Analysis.content = relationship("Content", back_populates="analysis", uselist=False)
Content.results = relationship("AnalysisResult", back_populates="content")
Analysis.results = relationship("AnalysisResult", back_populates="analysis")


class APIKey(Base):
    """API key model for authentication."""
    __tablename__ = "api_keys"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    scopes = Column(JSONB, default=list)  # List of permission scopes
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<APIKey {self.name} ({'active' if self.is_active else 'inactive'})>"


class AuditLog(Base):
    """Audit log for tracking important actions and events."""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)  # e.g., 'user.login', 'analysis.create'
    resource_type = Column(String(50), nullable=True)  # e.g., 'user', 'analysis'
    resource_id = Column(String(50), nullable=True)  # ID of the affected resource
    status = Column(String(20), nullable=False)  # 'success', 'failure'
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(255), nullable=True)
    metadata_ = Column("metadata", JSONB, default=dict)  # Additional context
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<AuditLog {self.action} ({self.status})>"


class SystemSetting(Base):
    """System configuration settings."""
    __tablename__ = "system_settings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(JSONB, nullable=False)
    description = Column(Text, nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<SystemSetting {self.key}>"


# Add indexes for better query performance
from sqlalchemy import Index

Index('idx_analyses_user_status', Analysis.user_id, Analysis.status)
Index('idx_analyses_created_at', Analysis.created_at.desc())
Index('idx_contents_created_by', Content.created_by)
Index('idx_audit_logs_created_at', AuditLog.created_at.desc())

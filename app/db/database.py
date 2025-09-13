"""
Database Configuration

This module configures the SQLAlchemy database connection and session management
for the ScholarIQ application.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import settings

# Create SQLAlchemy engine
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for models
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.
    
    Yields:
        SQLAlchemy database session.
        
    Example:
        def some_endpoint(db: Session = Depends(get_db)):
            # Use the database session
            db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    """Initialize the database by creating all tables."""
    from app.db import models  # noqa: F401 Import models to ensure they are registered with SQLAlchemy
    
    print("Initializing database...")
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")

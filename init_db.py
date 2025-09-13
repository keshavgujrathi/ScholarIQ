#!/usr/bin/env python3
"""
Initialize the database and create tables.
"""
import logging
from app.core.database import init_db, drop_db
from app.core.logging import setup_logging
from app.core.config import settings

def main():
    """Initialize the database."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Drop all tables (use with caution in production)
        if settings.APP_ENV != "production":
            logger.info("Dropping all database tables...")
            drop_db()
        
        # Create all tables
        logger.info("Creating database tables...")
        init_db()
        logger.info("Database initialized successfully!")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

if __name__ == "__main__":
    main()

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
import logging

from .config import settings

# Configure logger
logger = logging.getLogger(__name__)

# Create database engine
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    # SQLite specific configuration
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a scoped session factory
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

# Base class for all models
Base = declarative_base()

def get_db():
    """
    Dependency function to get DB session.
    Use this in FastAPI dependencies.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_session():
    """
    Context manager for database sessions.
    Use this for non-FastAPI contexts.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        session.close()

def init_db():
    """
    Initialize the database by creating all tables.
    """
    try:
        # Import models here to ensure they are registered with SQLAlchemy
        from app.models.user import User  # noqa: F401
        from app.models.student import Student  # noqa: F401
        from app.models.assessment import Assessment  # noqa: F401
        
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

def drop_db():
    """
    Drop all database tables.
    Use with caution - only for testing and development!
    """
    try:
        Base.metadata.drop_all(bind=engine)
        logger.warning("Dropped all database tables")
    except Exception as e:
        logger.error(f"Error dropping database: {str(e)}")
        raise

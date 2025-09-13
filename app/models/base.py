from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declared_attr
import logging

from app.core.database import Base

logger = logging.getLogger(__name__)

class BaseModel(Base):
    """
    Base model class that all database models should inherit from.
    Provides common fields and methods.
    """
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    @declared_attr
    def __tablename__(cls):
        """
        Generate table name from class name.
        Converts CamelCase class names to snake_case table names.
        """
        import re
        # Convert CamelCase to snake_case
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
        return name
    
    def to_dict(self):
        """
        Convert model instance to dictionary.
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            
            # Convert datetime objects to ISO format strings
            if hasattr(value, 'isoformat'):
                value = value.isoformat()
                
            result[column.name] = value
            
        return result
    
    def update(self, **kwargs):
        """
        Update model attributes.
        
        Args:
            **kwargs: Dictionary of attributes to update
        """
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['id', 'created_at', 'updated_at']:
                setattr(self, key, value)
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"

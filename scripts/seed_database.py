#!/usr/bin/env python3
"""
Database Seeding Script

This script populates the database with initial data for development and testing.
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal, engine, init_db
from app.core.security import get_password_hash
from app.db.models import (
    User, Role, APIKey, SystemSetting, Analysis, Content, AnalysisResult, AuditLog
)
from app.core.logging import setup_logging

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

def create_initial_roles(db: Session) -> Dict[str, Role]:
    """Create initial user roles."""
    logger.info("Creating initial roles...")
    
    roles = [
        {
            "name": "admin",
            "description": "Administrator with full access",
            "permissions": {
                "*": ["read", "create", "update", "delete"]
            }
        },
        {
            "name": "educator",
            "description": "Educator with content creation and management access",
            "permissions": {
                "content": ["read", "create", "update"],
                "analysis": ["read", "create"],
                "user": ["read_own"]
            }
        },
        {
            "name": "student",
            "description": "Student with basic access",
            "permissions": {
                "content": ["read"],
                "analysis": ["read_own", "create"],
                "user": ["read_own"]
            }
        },
        {
            "name": "researcher",
            "description": "Researcher with advanced analysis capabilities",
            "permissions": {
                "content": ["read", "create", "update"],
                "analysis": ["read", "create", "update"],
                "user": ["read_own"]
            }
        }
    ]
    
    role_objects = {}
    for role_data in roles:
        role = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not role:
            role = Role(
                id=role_data.get("id"),
                name=role_data["name"],
                description=role_data["description"],
                permissions=role_data["permissions"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(role)
            logger.info(f"Created role: {role.name}")
        else:
            logger.info(f"Role already exists: {role.name}")
        role_objects[role_data["name"]] = role
    
    db.commit()
    return role_objects

def create_initial_users(db: Session, roles: Dict[str, Role]) -> Dict[str, User]:
    """Create initial users."""
    logger.info("Creating initial users...")
    
    users = [
        {
            "email": "admin@scholariq.edu",
            "username": "admin",
            "password": "admin123",  # In production, use a secure password
            "full_name": "System Administrator",
            "is_active": True,
            "is_verified": True,
            "roles": ["admin"]
        },
        {
            "email": "prof.smith@university.edu",
            "username": "profsmith",
            "password": "professor123",
            "full_name": "Professor John Smith",
            "is_active": True,
            "is_verified": True,
            "roles": ["educator", "researcher"]
        },
        {
            "email": "student1@university.edu",
            "username": "student1",
            "password": "student123",
            "full_name": "Alice Johnson",
            "is_active": True,
            "is_verified": True,
            "roles": ["student"]
        }
    ]
    
    user_objects = {}
    for user_data in users:
        user = db.query(User).filter(User.email == user_data["email"]).first()
        if not user:
            user = User(
                email=user_data["email"],
                username=user_data["username"],
                hashed_password=get_password_hash(user_data["password"]),
                full_name=user_data["full_name"],
                is_active=user_data["is_active"],
                is_verified=user_data["is_verified"],
                last_login=datetime.utcnow(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Assign roles
            for role_name in user_data["roles"]:
                if role_name in roles:
                    user.roles.append(roles[role_name])
            
            db.add(user)
            logger.info(f"Created user: {user.username}")
        else:
            logger.info(f"User already exists: {user.username}")
        
        user_objects[user_data["username"]] = user
    
    db.commit()
    return user_objects

def create_initial_api_keys(db: Session, users: Dict[str, User]) -> None:
    """Create initial API keys for users."""
    logger.info("Creating initial API keys...")
    
    # In production, use secure random strings
    api_keys = [
        {
            "username": "admin",
            "name": "Admin CLI",
            "key": "sk_admin_1234567890abcdef1234567890abcdef",
            "expires_in_days": 365,  # 1 year
            "scopes": ["*"]
        },
        {
            "username": "profsmith",
            "name": "Research Script",
            "key": "sk_research_1234567890abcdef1234567890abcd",
            "expires_in_days": 90,  # 3 months
            "scopes": ["content:read", "content:write", "analysis:read", "analysis:write"]
        }
    ]
    
    for key_data in api_keys:
        username = key_data["username"]
        if username not in users:
            logger.warning(f"User {username} not found for API key creation")
            continue
            
        user = users[username]
        
        # Check if key already exists
        existing_key = db.query(APIKey).filter(APIKey.key == key_data["key"]).first()
        if existing_key:
            logger.info(f"API key already exists for {username}")
            continue
            
        # Create new API key
        expires_at = datetime.utcnow() + timedelta(days=key_data["expires_in_days"]) if key_data["expires_in_days"] else None
        
        api_key = APIKey(
            key=key_data["key"],
            name=key_data["name"],
            user_id=user.id,
            expires_at=expires_at,
            is_active=True,
            scopes=key_data["scopes"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(api_key)
        logger.info(f"Created API key for {username}: {key_data['name']}")
    
    db.commit()

def create_initial_system_settings(db: Session) -> None:
    """Create initial system settings."""
    logger.info("Creating initial system settings...")
    
    settings = [
        {
            "key": "app.name",
            "value": "ScholarIQ",
            "description": "Application name",
            "is_public": True
        },
        {
            "key": "app.version",
            "value": "1.0.0",
            "description": "Application version",
            "is_public": True
        },
        {
            "key": "app.maintenance_mode",
            "value": False,
            "description": "Whether the application is in maintenance mode",
            "is_public": True
        },
        {
            "key": "storage.max_upload_size_mb",
            "value": 100,
            "description": "Maximum file upload size in MB",
            "is_public": True
        },
        {
            "key": "ai.default_model",
            "value": "gpt-4",
            "description": "Default AI model to use for analysis",
            "is_public": False
        }
    ]
    
    for setting_data in settings:
        setting = db.query(SystemSetting).filter(SystemSetting.key == setting_data["key"]).first()
        if not setting:
            setting = SystemSetting(
                key=setting_data["key"],
                value=setting_data["value"],
                description=setting_data["description"],
                is_public=setting_data["is_public"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(setting)
            logger.info(f"Created system setting: {setting.key}")
        else:
            logger.info(f"System setting already exists: {setting.key}")
    
    db.commit()

def create_sample_analyses(db: Session, users: Dict[str, User]) -> None:
    """Create sample analysis data."""
    logger.info("Creating sample analyses...")
    
    if not users:
        logger.warning("No users found for creating sample analyses")
        return
    
    # Get the professor user
    professor = users.get("profsmith")
    if not professor:
        professor = list(users.values())[0]  # Fallback to first user
    
    sample_analyses = [
        {
            "title": "Research Paper: Machine Learning in Education",
            "description": "Analysis of the impact of machine learning in modern education systems.",
            "content_type": "text/plain",
            "status": "completed",
            "results": {
                "summary": "The paper discusses various applications of machine learning in education...",
                "key_topics": ["machine learning", "education technology", "personalized learning"],
                "sentiment": {"positive": 0.8, "neutral": 0.15, "negative": 0.05},
                "word_count": 2450
            },
            "metadata": {
                "source": "research_paper.txt",
                "language": "en",
                "model": "gpt-4"
            },
            "started_at": datetime.utcnow() - timedelta(hours=2),
            "completed_at": datetime.utcnow() - timedelta(hours=1, minutes=55)
        },
        {
            "title": "Lecture Recording: Introduction to AI",
            "description": "Transcription and analysis of the first lecture on AI fundamentals.",
            "content_type": "audio/mp3",
            "status": "completed",
            "results": {
                "transcript": "Welcome to Introduction to Artificial Intelligence...",
                "duration_seconds": 3540,
                "speaker_count": 1,
                "topics": ["artificial intelligence", "machine learning", "neural networks"]
            },
            "metadata": {
                "source": "lecture_ai_intro.mp3",
                "duration_seconds": 3540,
                "language": "en",
                "model": "whisper-large"
            },
            "started_at": datetime.utcnow() - timedelta(days=1, hours=3),
            "completed_at": datetime.utcnow() - timedelta(days=1, hours=1)
        },
        {
            "title": "Student Essay: The Future of Education",
            "description": "Analysis of a student's essay on the future of education.",
            "content_type": "text/plain",
            "status": "processing",
            "metadata": {
                "source": "student_essay.txt",
                "language": "en",
                "model": "gpt-4"
            },
            "started_at": datetime.utcnow() - timedelta(minutes=15)
        }
    ]
    
    for analysis_data in sample_analyses:
        analysis = Analysis(
            user_id=professor.id,
            title=analysis_data["title"],
            description=analysis_data["description"],
            content_type=analysis_data["content_type"],
            status=analysis_data["status"],
            results=analysis_data.get("results"),
            metadata=analysis_data.get("metadata", {}),
            started_at=analysis_data.get("started_at"),
            completed_at=analysis_data.get("completed_at"),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(analysis)
        logger.info(f"Created sample analysis: {analysis.title}")
    
    db.commit()

def main():
    """Main function to seed the database."""
    logger.info("Starting database seeding...")
    
    # Initialize the database (create tables)
    init_db()
    
    # Create a database session
    db = SessionLocal()
    
    try:
        # Create initial data
        roles = create_initial_roles(db)
        users = create_initial_users(db, roles)
        create_initial_api_keys(db, users)
        create_initial_system_settings(db)
        create_sample_analyses(db, users)
        
        logger.info("Database seeding completed successfully!")
        
        # Print admin API key for easy access
        admin_key = db.query(APIKey).filter(APIKey.name == "Admin CLI").first()
        if admin_key:
            print("\nAdmin API Key:")
            print(f"Key: {admin_key.key}")
            print(f"Expires: {admin_key.expires_at}")
            print("\nUse this key for authenticating API requests.")
            
    except Exception as e:
        logger.error(f"Error seeding database: {e}", exc_info=True)
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()

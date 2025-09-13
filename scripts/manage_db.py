#!/usr/bin/env python3
"""
Database Management Script

This script provides commands to manage the database, including:
- Initializing the database
- Dropping all tables (for development)
- Seeding the database with initial data
- Running migrations
"""

import argparse
import logging
import os
import sys
from typing import Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database, drop_database

from app.core.config import settings
from app.core.database import Base, engine, init_db, drop_db
from app.core.logging import setup_logging

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

def create_database_if_not_exists() -> None:
    """Create the database if it doesn't exist."""
    if not database_exists(settings.DATABASE_URL):
        logger.info(f"Creating database: {settings.DATABASE_URL}")
        create_database(settings.DATABASE_URL)
        logger.info("Database created successfully")
    else:
        logger.info("Database already exists")

def drop_database_if_exists() -> None:
    """Drop the database if it exists."""
    if database_exists(settings.DATABASE_URL):
        confirm = input("Are you sure you want to drop the database? This will delete all data. (y/n): ")
        if confirm.lower() == 'y':
            logger.warning(f"Dropping database: {settings.DATABASE_URL}")
            drop_database(settings.DATABASE_URL)
            logger.info("Database dropped successfully")
        else:
            logger.info("Database drop cancelled")
    else:
        logger.info("Database does not exist")

def run_migrations() -> None:
    """Run database migrations using Alembic."""
    logger.info("Running database migrations...")
    
    # Get the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Get the project root directory (one level up from scripts/)
    project_root = os.path.dirname(script_dir)
    
    # Path to the alembic.ini file and migrations directory
    alembic_cfg = Config(os.path.join(project_root, "alembic.ini"))
    alembic_cfg.set_main_option("script_location", os.path.join(project_root, "alembic"))
    
    # Run the upgrade command
    command.upgrade(alembic_cfg, "head")
    logger.info("Migrations completed successfully")

def seed_database() -> None:
    """Seed the database with initial data."""
    logger.info("Seeding database with initial data...")
    
    # Import and run the seed script
    from scripts.seed_database import main as seed_main
    seed_main()

def reset_database() -> None:
    """Reset the database by dropping and recreating it, then running migrations and seeding."""
    logger.warning("Resetting database...")
    
    # Drop and recreate the database
    drop_db()
    init_db()
    
    # Run migrations
    run_migrations()
    
    # Seed the database
    seed_database()
    
    logger.info("Database reset completed successfully")

def main():
    """Main entry point for the database management script."""
    parser = argparse.ArgumentParser(description="Manage the ScholarIQ database")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Create database command
    subparsers.add_parser("create", help="Create the database if it doesn't exist")
    
    # Drop database command
    subparsers.add_parser("drop", help="Drop the database (DANGER: deletes all data)")
    
    # Initialize database command
    subparsers.add_parser("init", help="Initialize the database (create tables)")
    
    # Migrate command
    subparsers.add_parser("migrate", help="Run database migrations")
    
    # Seed command
    subparsers.add_parser("seed", help="Seed the database with initial data")
    
    # Reset command
    subparsers.add_parser("reset", help="Reset the database (drop, create, migrate, seed)")
    
    # Parse command line arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute the appropriate command
    if args.command == "create":
        create_database_if_not_exists()
    elif args.command == "drop":
        drop_database_if_exists()
    elif args.command == "init":
        init_db()
        logger.info("Database initialized successfully")
    elif args.command == "migrate":
        run_migrations()
    elif args.command == "seed":
        seed_database()
    elif args.command == "reset":
        reset_database()
    else:
        logger.error(f"Unknown command: {args.command}")
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()

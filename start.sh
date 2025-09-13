#!/bin/bash

# Set environment variables
export APP_ENV=development

# Create and activate virtual environment
echo "Creating virtual environment..."
python -m venv venv
source venv/bin/activate  # On Windows, use: .\venv\Scripts\activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Set up environment variables
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please update the .env file with your configuration and press Enter to continue..."
    read -r
fi

# Initialize the database
echo "Initializing database..."
python init_db.py

# Start the application
echo "Starting ScholarIQ API server..."
uvicorn app.main:app --reload

# Deactivate virtual environment on exit
deactivate

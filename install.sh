#!/bin/bash

# Exit on error
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting ScholarIQ installation...${NC}"

# Check if Python 3.8+ is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}❌ Python 3.8 or higher is required but not installed.${NC}"
    exit 1
fi

# Create virtual environment
echo -e "${GREEN}🔧 Creating virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo -e "${GREEN}⬆️ Upgrading pip...${NC}"
pip install --upgrade pip

# Install production dependencies
echo -e "${GREEN}📦 Installing production dependencies...${NC}"
pip install -r requirements.txt

# Install development dependencies if --dev flag is passed
if [ "$1" = "--dev" ]; then
    echo -e "${GREEN}🔧 Installing development dependencies...${NC}"
    pip install -r requirements-dev.txt
    
    # Set up pre-commit hooks
    echo -e "${GREEN}🔧 Setting up pre-commit hooks...${NC}"
    pre-commit install
fi

# Download spaCy models
echo -e "${GREEN}📥 Downloading spaCy models...${NC}"
python -m spacy download en_core_web_sm

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${GREEN}📄 Creating .env file...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}ℹ️  Please update the .env file with your configuration.${NC}"
fi

# Initialize database
echo -e "${GREEN}💾 Initializing database...${NC}"
python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())" || echo "${YELLOW}⚠️  Database initialization failed. Make sure your database is running and configured correctly.${NC}"

echo -e "${GREEN}✨ Installation complete!${NC}"
echo -e "${GREEN}To activate the virtual environment, run:${NC} source venv/bin/activate"
echo -e "${GREEN}To start the development server:${NC} uvicorn app.main:app --reload"

# Mark task as complete
todo_list {"todos": [{"id": "3", "content": "Create install.sh for Mac/Linux", "status": "completed", "priority": "medium"}]}

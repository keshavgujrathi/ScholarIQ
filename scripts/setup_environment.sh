#!/bin/bash

# Exit on error
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
VENV_PATH="../.venv"
REQUIREMENTS_FILE="../requirements.txt"
DEV_REQUIREMENTS_FILE="../requirements-dev.txt"
ENV_EXAMPLE_FILE="../.env.example"
ENV_FILE="../.env"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}Warning: Running as root is not recommended. Consider running as a regular user.${NC}"
fi

echo -e "${CYAN}=== Setting up ScholarIQ Development Environment ===${NC}"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "Python is not installed. Please install Python 3.8 or higher and try again."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d '.' -f 1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d '.' -f 2)

if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]; }; then
    echo "Python 3.8 or higher is required. Found Python $PYTHON_VERSION"
    exit 1
fi

echo -e "${GREEN}✓ Using Python $PYTHON_VERSION${NC}"

# Create virtual environment
if [ -d "$VENV_PATH" ]; then
    if [ "$1" = "--force" ] || [ "$1" = "-f" ]; then
        echo -e "${YELLOW}Removing existing virtual environment...${NC}"
        rm -rf "$VENV_PATH"
    else
        echo -e "${YELLOW}Virtual environment already exists at $VENV_PATH${NC}"
        read -p "Recreate virtual environment? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Using existing virtual environment."
        else
            rm -rf "$VENV_PATH"
        fi
    fi
fi

if [ ! -d "$VENV_PATH" ]; then
    echo -e "${CYAN}Creating virtual environment at $VENV_PATH...${NC}"
    python3 -m venv "$VENV_PATH"
    
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${CYAN}Activating virtual environment...${NC}"
source "$VENV_PATH/bin/activate"

# Upgrade pip
echo -e "${CYAN}Upgrading pip...${NC}"
pip install --upgrade pip

if [ $? -ne 0 ]; then
    echo "Failed to upgrade pip"
    exit 1
fi

# Install requirements
echo -e "${CYAN}Installing requirements...${NC}"
pip install -r "$REQUIREMENTS_FILE"

if [ $? -ne 0 ]; then
    echo "Failed to install requirements"
    exit 1
fi

# Install dev requirements if requested
if [ "$1" = "--dev" ] || [ "$2" = "--dev" ]; then
    echo -e "${CYAN}Installing development requirements...${NC}"
    pip install -r "$DEV_REQUIREMENTS_FILE"
    
    if [ $? -ne 0 ]; then
        echo "Failed to install development requirements"
        exit 1
    fi
    
    # Install pre-commit hooks if available
    if command -v pre-commit &> /dev/null; then
        echo -e "${CYAN}Installing pre-commit hooks...${NC}"
        pre-commit install
        
        if [ $? -ne 0 ]; then
            echo -e "${YELLOW}Failed to install pre-commit hooks${NC}"
        else
            echo -e "${GREEN}✓ Pre-commit hooks installed${NC}"
        fi
    fi
fi

# Create .env file if it doesn't exist
if [ ! -f "$ENV_FILE" ] && [ -f "$ENV_EXAMPLE_FILE" ]; then
    echo -e "${CYAN}Creating .env file from example...${NC}"
    cp "$ENV_EXAMPLE_FILE" "$ENV_FILE"
    echo -e "${GREEN}✓ .env file created. Please update it with your configuration.${NC}"
fi

echo -e "\n${CYAN}=== Setup Complete ===${NC}"
echo -e "To activate the virtual environment, run:"
echo -e "  source $VENV_PATH/bin/activate${NC}"
echo -e "\nTo deactivate the virtual environment, run:"
echo -e "  deactivate${NC}"

echo -e "\n${CYAN}Next steps:${NC}"
echo -e "1. Update the .env file with your configuration"
echo -e "2. Run 'python -m scripts.manage_db reset' to initialize the database"
echo -e "3. Run 'uvicorn app.main:app --reload' to start the development server"

# Make the script executable
chmod +x "$0"

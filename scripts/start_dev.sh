#!/bin/bash

# Exit on error
set -e

# Default configuration
HOST="0.0.0.0"
PORT=8000
WORKERS=1
RELOAD=true
DEBUG=false
VENV_PATH="../.venv"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --workers)
            WORKERS="$2"
            shift 2
            ;;
        --no-reload)
            RELOAD=false
            shift
            ;;
        --debug)
            DEBUG=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${YELLOW}Virtual environment not found at $VENV_PATH${NC}"
    echo -e "${CYAN}Running setup script...${NC}"
    
    # Run the setup script
    setup_script="$(dirname "$0")/setup_environment.sh"
    if [ ! -f "$setup_script" ]; then
        echo -e "${YELLOW}Setup script not found at $setup_script${NC}"
        exit 1
    fi
    
    bash "$setup_script" --dev
    
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}Failed to set up the development environment${NC}"
        exit 1
    fi
fi

# Activate virtual environment
echo -e "${CYAN}Activating virtual environment...${NC}"
source "$VENV_PATH/bin/activate"

# Install dependencies if needed
if ! pip show uvicorn > /dev/null 2>&1; then
    echo -e "${CYAN}Installing dependencies...${NC}"
    pip install -r "$(dirname "$0")/../requirements.txt"
    
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}Failed to install dependencies${NC}"
        exit 1
    fi
fi

# Set environment variables
export APP_ENV="development"
if [ "$DEBUG" = true ]; then
    export DEBUG="true"
    export LOG_LEVEL="DEBUG"
else
    export DEBUG="false"
    export LOG_LEVEL="INFO"
fi

# Build Uvicorn command
UVICORN_CMD="uvicorn app.main:app --host $HOST --port $PORT --workers $WORKERS"

if [ "$RELOAD" = true ]; then
    UVICORN_CMD+=" --reload"
fi

if [ "$DEBUG" = true ]; then
    UVICORN_CMD+=" --log-level debug"
fi

# Start the server
echo -e "${CYAN}Starting development server on http://${HOST}:${PORT}${NC}"
echo -e "${CYAN}Press Ctrl+C to stop${NC}"
echo

eval $UVICORN_CMD

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Failed to start the development server${NC}"
    exit 1
fi

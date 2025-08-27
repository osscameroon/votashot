#!/bin/bash

# Script to start the MCP server
# This script activates the virtual environment and runs the codetools-mcp.py script

set -e  # Exit on any error

# Get the project root directory (directory containing this script)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$PROJECT_ROOT/.venv"
SRC_PATH="$PROJECT_ROOT/src"

echo "Starting MCP server..."

# Check if virtual environment exists
if [[ ! -d "$VENV_PATH" ]]; then
    echo "Error: Virtual environment not found at $VENV_PATH"
    echo "Please run the setup script first: ./install/setup_project.sh"
    exit 1
fi

# Check if src directory exists
if [[ ! -d "$SRC_PATH" ]]; then
    echo "Error: Source directory not found at $SRC_PATH"
    exit 1
fi

# Check if codetools-mcp.py exists
if [[ ! -f "$SRC_PATH/codetools-mcp.py" ]]; then
    echo "Error: codetools-mcp.py not found at $SRC_PATH/codetools-mcp.py"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_PATH/bin/activate"

# Go to src directory
cd "$SRC_PATH" || exit 1

# Run the migrations
echo "Running migrations"
python manage.py makemigrations
python manage.py migrate

# Start the server
echo "Starting the server"
python manage.py runserver

#!/bin/bash

# Script to start the MCP server
# This script activates the virtual environment and runs the manage.py script

set -e  # Exit on any error

# Get the project root directory (directory containing this script)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$PROJECT_ROOT/.venv"
SRC_PATH="$PROJECT_ROOT"

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

# Check if manage.py exists
if [[ ! -f "$SRC_PATH/manage.py" ]]; then
    echo "Error: manage.py not found at $SRC_PATH/manage.py"
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

#!/bin/bash

# Brightness Toggle Service Wrapper
# This script activates the conda environment and runs the brightness toggle app

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

# Set environment variables for X11 display
export DISPLAY="${DISPLAY:-:0}"

# Activate conda environment
if [ -d "$PROJECT_DIR/.conda" ]; then
    # Use project-local conda environment
    export CONDA_PREFIX="$PROJECT_DIR/.conda"
    export PATH="$CONDA_PREFIX/bin:$PATH"
    echo "Using conda environment at: $CONDA_PREFIX"
else
    echo "Error: Conda environment not found at $PROJECT_DIR/.conda"
    exit 1
fi

# Change to project directory
cd "$PROJECT_DIR"

# Log startup
echo "$(date): Starting brightness toggle service..."
echo "Display: $DISPLAY"
echo "Python: $(which python)"
echo "Working directory: $(pwd)"

# Run the brightness toggle app
exec python brightness_toggle.py

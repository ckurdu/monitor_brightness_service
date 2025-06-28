#!/bin/bash

# Brightness GUI Launcher
# This script activates the conda environment and runs the GUI application

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

# Set environment variables for X11 display
export DISPLAY="${DISPLAY:-:0}"

# Activate appropriate environment
if [ -d "$PROJECT_DIR/.conda" ]; then
    # Use project-local conda environment
    export CONDA_PREFIX="$PROJECT_DIR/.conda"
    export PATH="$CONDA_PREFIX/bin:$PATH"
    echo "Using conda environment at: $CONDA_PREFIX"
elif [ -d "$PROJECT_DIR/.venv" ]; then
    # Use virtual environment
    source "$PROJECT_DIR/.venv/bin/activate"
    echo "Using virtual environment at: $PROJECT_DIR/.venv"
else
    echo "Using system Python environment"
    echo "Make sure PySide6 and psutil are installed system-wide"
fi

# Change to project directory
cd "$PROJECT_DIR"

# Log startup
echo "$(date): Starting brightness GUI..."
echo "Display: $DISPLAY"
echo "Python: $(which python)"
echo "Working directory: $(pwd)"

# Run the brightness GUI
exec python brightness_gui.py

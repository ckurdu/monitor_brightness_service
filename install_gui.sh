#!/bin/bash

# GUI Installation script for Monitor Brightness Toggle

echo "Monitor Brightness Toggle - GUI Installation Script"
echo "=================================================="
echo

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check for conda environment first
if [ -d "$PROJECT_DIR/.conda" ]; then
    echo "Installing GUI dependencies in conda environment..."
    source "$PROJECT_DIR/.conda/bin/activate"
    pip install PySide6>=6.5.0 psutil>=5.9.0
    echo "✓ GUI dependencies installed in conda environment"
elif [ -d "$PROJECT_DIR/.venv" ]; then
    echo "Installing GUI dependencies in virtual environment..."
    source "$PROJECT_DIR/.venv/bin/activate"
    pip install PySide6>=6.5.0 psutil>=5.9.0
    echo "✓ GUI dependencies installed in virtual environment"
else
    echo "No conda or virtual environment found."
    echo "Attempting to install system packages..."
    
    # Try to install system packages
    if command -v apt &> /dev/null; then
        echo "Installing system packages with apt..."
        sudo apt update
        sudo apt install -y python3-pyside6.qtwidgets python3-pyside6.qtcore python3-pyside6.qtgui python3-psutil
        echo "✓ System packages installed"
    else
        echo "Error: Cannot install dependencies automatically."
        echo "Please install PySide6 and psutil manually:"
        echo "  Option 1: Create virtual environment:"
        echo "    sudo apt install python3.11-venv"
        echo "    python3 -m venv .venv"
        echo "    source .venv/bin/activate"
        echo "    pip install PySide6>=6.5.0 psutil>=5.9.0"
        echo "  Option 2: Install system packages:"
        echo "    sudo apt install python3-pyside6.qtwidgets python3-pyside6.qtcore python3-pyside6.qtgui python3-psutil"
        exit 1
    fi
fi

# Make GUI script executable
chmod +x "$PROJECT_DIR/brightness_gui.sh"
echo "✓ GUI script made executable"

# Install desktop entry
DESKTOP_DIR="$HOME/.local/share/applications"
mkdir -p "$DESKTOP_DIR"

# Update desktop entry with correct path
sed "s|/home/ckurdu/projects/my/monitor_brightness_on_off|$PROJECT_DIR|g" \
    "$PROJECT_DIR/brightness-control.desktop" > "$DESKTOP_DIR/brightness-control.desktop"

echo "✓ Desktop entry installed"

echo
echo "Installation complete!"
echo
echo "You can now:"
echo "  1. Run 'make gui' to start the GUI"
echo "  2. Search for 'Brightness Control' in your application menu"
echo "  3. Run './brightness_gui.sh' directly"
echo
echo "The GUI will appear in your system tray when started."

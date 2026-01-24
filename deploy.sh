#!/bin/bash

# Deployment script for Monitor Brightness Toggle Service
# This script sets up the application as a systemd user service with conda environment

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
SERVICE_NAME="brightness-toggle"

echo "Monitor Brightness Toggle - Deployment Script"
echo "============================================="
echo "Project directory: $PROJECT_DIR"
echo

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
echo "Checking system dependencies..."

if ! command_exists conda; then
    echo "Error: conda is not installed or not in PATH"
    echo "Please install conda/miniconda first: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

if ! command_exists xrandr; then
    echo "Installing xrandr..."
    if command_exists apt; then
        sudo apt update && sudo apt install -y x11-xserver-utils
    elif command_exists dnf; then
        sudo dnf install -y xorg-x11-server-utils
    elif command_exists pacman; then
        sudo pacman -S xorg-xrandr
    else
        echo "Error: Could not install xrandr. Please install x11-xserver-utils manually."
        exit 1
    fi
fi

if ! command_exists notify-send; then
    echo "Installing notify-send..."
    if command_exists apt; then
        sudo apt install -y libnotify-bin
    elif command_exists dnf; then
        sudo dnf install -y libnotify
    elif command_exists pacman; then
        sudo pacman -S libnotify
    else
        echo "Warning: Could not install notify-send. Notifications may not work."
    fi
fi

if ! command_exists qdbus; then
    echo "Installing qdbus (for Night Color support)..."
    if command_exists apt; then
        sudo apt install -y qdbus-qt5
    elif command_exists dnf; then
        sudo dnf install -y qt5-qttools
    elif command_exists pacman; then
        sudo pacman -S qt5-tools
    else
        echo "Warning: Could not install qdbus. Night Color mode may not work."
    fi
fi

# Create or update conda environment
echo "Setting up conda environment..."
if [ -f "$PROJECT_DIR/environment.yml" ]; then
    echo "Creating conda environment from environment.yml..."
    if [ -d "$PROJECT_DIR/.conda" ]; then
        echo "Removing existing environment..."
        rm -rf "$PROJECT_DIR/.conda"
    fi
    conda env create -f "$PROJECT_DIR/environment.yml" -p "$PROJECT_DIR/.conda"
else
    echo "Creating conda environment manually..."
    conda create -p "$PROJECT_DIR/.conda" python=3.11 -y
    conda run -p "$PROJECT_DIR/.conda" pip install -r "$PROJECT_DIR/requirements.txt"
fi

# Test the conda environment
echo "Testing conda environment..."
if conda run -p "$PROJECT_DIR/.conda" python -c "import sys; print(f'Python {sys.version}')"; then
    echo "✓ Python working"
else
    echo "✗ Python test failed"
    exit 1
fi

if conda run -p "$PROJECT_DIR/.conda" python -c "import pynput; print('pynput imported successfully')"; then
    echo "✓ pynput working"
else
    echo "✗ pynput test failed"
    exit 1
fi

# Test brightness control
echo "Testing brightness control..."
if conda run -p "$PROJECT_DIR/.conda" python -c "
import subprocess
try:
    result = subprocess.run(['xrandr', '--query'], capture_output=True, text=True, check=True)
    displays = [line.split()[0] for line in result.stdout.split('\n') if ' connected' in line and 'disconnected' not in line]
    print(f'Found displays: {displays}')
    if displays:
        print('✓ Brightness control should work')
    else:
        print('✗ No displays found')
except Exception as e:
    print(f'✗ Brightness control test failed: {e}')
"; then
    echo "Brightness control test completed"
else
    echo "Warning: Brightness control test had issues"
fi

# Install systemd service
echo "Installing systemd user service..."

# Create systemd user directory if it doesn't exist
mkdir -p "$HOME/.config/systemd/user"

# Copy service file
cp "$PROJECT_DIR/${SERVICE_NAME}.service" "$HOME/.config/systemd/user/"

# Reload systemd and enable service
systemctl --user daemon-reload
systemctl --user enable "$SERVICE_NAME.service"

echo "Service installed successfully!"
echo

# Provide usage instructions
echo "Usage Instructions:"
echo "=================="
echo
echo "Start the service:"
echo "  systemctl --user start $SERVICE_NAME"
echo
echo "Stop the service:"
echo "  systemctl --user stop $SERVICE_NAME"
echo
echo "Check service status:"
echo "  systemctl --user status $SERVICE_NAME"
echo
echo "View service logs:"
echo "  journalctl --user -u $SERVICE_NAME -f"
echo
echo "Enable auto-start on login:"
echo "  systemctl --user enable $SERVICE_NAME"
echo "  loginctl enable-linger \$USER"
echo
echo "Disable auto-start:"
echo "  systemctl --user disable $SERVICE_NAME"
echo
echo "Manual test (without service):"
echo "  $PROJECT_DIR/brightness_service.sh"
echo
echo "The service uses Ctrl+Alt+B to toggle brightness."
echo "Configuration is saved to ~/.brightness_toggle_config.json"
echo

# Ask if user wants to start the service now
read -p "Would you like to start the service now? [y/N]: " -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Starting service..."
    systemctl --user start "$SERVICE_NAME"
    sleep 2
    echo "Service status:"
    systemctl --user status "$SERVICE_NAME" --no-pager -l
    echo
    echo "Service started! Press Ctrl+Alt+B to test brightness toggle."
    echo "Use 'journalctl --user -u $SERVICE_NAME -f' to view logs."
else
    echo "Service is installed but not started."
    echo "Start it manually with: systemctl --user start $SERVICE_NAME"
fi

echo
echo "Deployment completed successfully!"

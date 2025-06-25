#!/bin/bash

# Installation script for Monitor Brightness Toggle
# For Debian Linux with KDE

echo "Monitor Brightness Toggle - Installation Script"
echo "=============================================="
echo

# Check if running on Debian/Ubuntu
if ! command -v apt &> /dev/null; then
    echo "Error: This script is designed for Debian/Ubuntu systems with apt package manager."
    exit 1
fi

# Install system dependencies
echo "Installing system dependencies..."
sudo apt update
sudo apt install -y python3 python3-pip x11-xserver-utils libnotify-bin

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Make script executable
echo "Making script executable..."
chmod +x brightness_toggle.py

echo
echo "Installation complete!"
echo
echo "Usage:"
echo "  python3 brightness_toggle.py"
echo
echo "Hotkey: Ctrl+Alt+B to toggle brightness"
echo "Press Ctrl+C to exit the program"
echo
echo "For auto-start on login, add this to KDE Autostart:"
echo "  Command: python3 $(pwd)/brightness_toggle.py"

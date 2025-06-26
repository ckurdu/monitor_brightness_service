#!/bin/bash

# Uninstall script for Monitor Brightness Toggle Service

set -e

SERVICE_NAME="brightness-toggle"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Monitor Brightness Toggle - Uninstall Script"
echo "==========================================="
echo

# Stop and disable service if running
echo "Stopping and disabling service..."
if systemctl --user is-active --quiet "$SERVICE_NAME"; then
    systemctl --user stop "$SERVICE_NAME"
    echo "✓ Service stopped"
fi

if systemctl --user is-enabled --quiet "$SERVICE_NAME"; then
    systemctl --user disable "$SERVICE_NAME"
    echo "✓ Service disabled"
fi

# Remove service file
if [ -f "$HOME/.config/systemd/user/${SERVICE_NAME}.service" ]; then
    rm "$HOME/.config/systemd/user/${SERVICE_NAME}.service"
    echo "✓ Service file removed"
fi

# Reload systemd
systemctl --user daemon-reload
echo "✓ Systemd reloaded"

# Ask about removing conda environment
read -p "Remove conda environment (.conda/)? [y/N]: " -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -d "$PROJECT_DIR/.conda" ]; then
        rm -rf "$PROJECT_DIR/.conda"
        echo "✓ Conda environment removed"
    fi
fi

# Ask about removing config file
read -p "Remove user configuration file (~/.brightness_toggle_config.json)? [y/N]: " -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f "$HOME/.brightness_toggle_config.json" ]; then
        rm "$HOME/.brightness_toggle_config.json"
        echo "✓ Configuration file removed"
    fi
fi

echo
echo "Uninstall completed!"
echo "Project files remain in: $PROJECT_DIR"

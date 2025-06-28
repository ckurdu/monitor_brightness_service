# Monitor Brightness Toggle

A Python service for toggling monitor brightness between 0% and normal levels using a keyboard shortcut (Ctrl+Alt+B) on Debian Linux with KDE. Includes both command-line service and GUI system tray application.

## Features

- 🔆 Toggle brightness between 0% and saved normal level
- ⌨️ Global keyboard shortcut (Ctrl+Alt+B)
- 🔧 Systemd service integration
- 🐍 Conda environment for dependency isolation
- 📱 KDE notifications
- 💾 Persistent configuration storage
- 🖥️ Multi-monitor support
- 🖥️ GUI system tray application for easy management

## Quick Start

### 1. Deploy as Service

```bash
./deploy.sh
```

This script will:
- Install system dependencies (xrandr, notify-send)
- Create a conda environment with Python dependencies
- Install and enable the systemd user service
- Test the setup

### 2. GUI Application

```bash
# Install GUI dependencies and desktop integration
./install_gui.sh

# Start the GUI system tray application
make gui
# or
./brightness_gui.sh
```

### 3. Manual Usage

```bash
# Test the application directly
./dev.sh test

# Check service status
./dev.sh service-status

# View service logs
./dev.sh service-logs
```

## System Requirements

- **OS**: Debian/Ubuntu Linux with X11
- **Desktop**: KDE Plasma (for notifications)
- **Dependencies**: conda/miniconda, xrandr, notify-send
- **Python**: 3.11+ (managed by conda)

## Project Structure

```
├── brightness_toggle.py       # Main application
├── brightness_gui.py          # GUI system tray application
├── brightness_gui.sh          # GUI launcher script
├── brightness_service.sh      # Service wrapper script
├── brightness-toggle.service  # Systemd service file
├── brightness-control.desktop # Desktop entry for GUI
├── environment.yml           # Conda environment specification
├── requirements.txt          # Python dependencies
├── deploy.sh                # Deployment script
├── install_gui.sh           # GUI installation script
├── uninstall.sh             # Uninstall script
├── dev.sh                   # Development/testing script
├── GUI_README.md            # GUI-specific documentation
└── .gitignore               # Git ignore rules
```

## Usage

### GUI Application

The GUI provides a user-friendly system tray interface for managing the brightness service:

```bash
# Start GUI (after running ./install_gui.sh)
make gui

# Or search for "Brightness Control" in your application menu
```

**GUI Features:**
- System tray icon with context menu
- Service management (start/stop/enable/disable)
- Manual brightness control with configurable levels
- Settings dialog for brightness configuration
- Real-time service status monitoring
- Desktop notifications

See [GUI_README.md](GUI_README.md) for detailed GUI documentation.

### Service Management

```bash
# Start service
systemctl --user start brightness-toggle

# Stop service
systemctl --user stop brightness-toggle

# Enable auto-start on login
systemctl --user enable brightness-toggle
loginctl enable-linger $USER

# Check status
systemctl --user status brightness-toggle

# View logs
journalctl --user -u brightness-toggle -f
```

### Development Commands

```bash
# Run all available commands
./dev.sh help

# Test application directly
./dev.sh test

# Check display information
./dev.sh check-displays

# View environment info
./dev.sh env-info

# Service management
./dev.sh service-start
./dev.sh service-stop
./dev.sh service-status
./dev.sh service-logs
```

## Configuration

The application stores its configuration in `~/.brightness_toggle_config.json`:

```json
{
  "normal_brightness": 1.0,
  "low_brightness": 0.0,
  "is_dimmed": false
}
```

- `normal_brightness`: High brightness level (0.1-1.0, default 1.0)
- `low_brightness`: Low brightness level (0.0-0.5, default 0.0)
- `is_dimmed`: Current brightness state

## Keyboard Shortcut

- **Ctrl+Alt+B**: Toggle brightness between 0% and normal level

## Conda Environment

The application uses a local conda environment (`.conda/`) with the following dependencies:

- Python 3.11
- pynput (for keyboard shortcuts)
- PySide6 (for GUI, optional)
- psutil (for process monitoring, optional)

### Environment Management

```bash
# Recreate environment
conda env create -f environment.yml -p .conda --force

# Install additional packages
conda run -p .conda pip install <package>

# Activate environment manually
export CONDA_PREFIX="$(pwd)/.conda"
export PATH="$CONDA_PREFIX/bin:$PATH"
```

## Deployment Options

### 1. User Service (Recommended)

The service runs as a user service, which provides:
- Automatic X11 display access
- User-specific configuration
- No root privileges required
- Auto-start on user login (optional)

### 2. Manual Execution

For testing or one-time use:

```bash
# Using conda environment
./brightness_service.sh

# Direct execution (requires system Python with pynput)
python brightness_toggle.py
```

## Troubleshooting

### Service Not Starting

```bash
# Check service logs
journalctl --user -u brightness-toggle

# Test wrapper script directly
./brightness_service.sh

# Check conda environment
./dev.sh env-info
```

### Display Issues

```bash
# Check connected displays
./dev.sh check-displays

# Test xrandr manually
xrandr --query
```

### Permission Issues

```bash
# Ensure X11 access
echo $DISPLAY
xrandr --query

# Check systemd user services are enabled
systemctl --user status
```

## Uninstallation

```bash
./uninstall.sh
```

This will:
- Stop and disable the service
- Remove systemd service files
- Optionally remove conda environment and config files

## License

[Your License Here]

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test with `./dev.sh test`
4. Submit a pull request

## Support

- Check service logs: `./dev.sh service-logs`
- Test setup: `./dev.sh check-displays`
- Environment info: `./dev.sh env-info`

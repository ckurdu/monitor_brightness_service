# Monitor Brightness Toggle

A Python service for toggling monitor brightness between 0% and normal levels using a keyboard shortcut (Ctrl+Alt+B) on Debian Linux with KDE. Includes both command-line service and GUI system tray application.

## Quick Start

### 1. Deploy as Service
```bash
./deploy.sh
```

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
```

## Features

- 🔆 **Dual Mode Support**: Toggle brightness OR KDE Night Color
- ⌨️ Global keyboard shortcut (Ctrl+Alt+B)
- 🌙 **Night Color Integration**: Control KDE Plasma Night Color via D-Bus
- 🔧 Systemd service integration
- 🖥️ GUI system tray application for easy management
- 🐍 Conda environment for dependency isolation
- 📱 KDE notifications
- 💾 Persistent configuration storage with mode selection
- 🖥️ Multi-monitor support

## Documentation

For detailed documentation, see the [docs](docs/) folder:

- **[Complete Documentation](docs/README.md)** - Full project documentation
- **[Night Color Mode Guide](docs/NIGHT_COLOR_MODE.md)** - KDE Night Color integration and mode selection
- **[GUI Guide](docs/GUI_README.md)** - GUI application documentation
- **[Implementation Summary](docs/IMPLEMENTATION_SUMMARY.md)** - Technical implementation details

## System Requirements

- **OS**: Debian/Ubuntu Linux with X11
- **Desktop**: KDE Plasma (for notifications and Night Color)
- **Dependencies**: conda/miniconda, xrandr, notify-send, qdbus (for Night Color)
- **Python**: 3.11+ (managed by conda)

## Mode Selection

The application supports two modes that can be toggled:

### 🔆 Brightness Mode (Default)
- Toggles monitor brightness between 0% and normal level
- Uses xrandr for hardware brightness control
- Works with all monitors

### 🌙 Night Color Mode
- Toggles KDE Plasma Night Color on/off
- Uses D-Bus to communicate with KDE's color correction
- Shows current color temperature in notifications
- Requires KDE Plasma desktop environment

To switch modes:
1. **GUI**: Use the mode selector in the system tray application
2. **Manual Mode**: Use the `m` or `mode` command
3. **Config File**: Edit `~/.brightness_toggle_config.json` and set `"mode": "nightcolor"` or `"mode": "brightness"`

The selected mode is persistent across restarts.

## License

[Your License Here]

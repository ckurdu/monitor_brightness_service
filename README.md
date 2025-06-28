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

- 🔆 Toggle brightness between 0% and saved normal level
- ⌨️ Global keyboard shortcut (Ctrl+Alt+B)
- 🔧 Systemd service integration
- 🖥️ GUI system tray application for easy management
- 🐍 Conda environment for dependency isolation
- 📱 KDE notifications
- 💾 Persistent configuration storage
- 🖥️ Multi-monitor support

## Documentation

For detailed documentation, see the [docs](docs/) folder:

- **[Complete Documentation](docs/README.md)** - Full project documentation
- **[GUI Guide](docs/GUI_README.md)** - GUI application documentation
- **[Implementation Summary](docs/IMPLEMENTATION_SUMMARY.md)** - Technical implementation details

## System Requirements

- **OS**: Debian/Ubuntu Linux with X11
- **Desktop**: KDE Plasma (for notifications)
- **Dependencies**: conda/miniconda, xrandr, notify-send
- **Python**: 3.11+ (managed by conda)

## License

[Your License Here]

# Brightness Control GUI

A PySide6-based system tray application for managing the monitor brightness toggle service.

## Features

- **System Tray Integration**: Runs persistently in the system tray
- **Service Management**: Start, stop, enable, and disable the systemd service
- **Brightness Control**: Manual brightness adjustment with configurable high/low values
- **Settings Dialog**: Configure brightness levels through a user-friendly interface
- **Real-time Status**: Live monitoring of service status
- **Notifications**: Visual feedback for all operations

## Installation

### Option 1: System Packages (Recommended)

```bash
# Install system dependencies
sudo apt update
sudo apt install python3-pyside6.qtwidgets python3-pyside6.qtcore python3-pyside6.qtgui python3-psutil

# Run the GUI installer
./install_gui.sh
```

### Option 2: Virtual Environment

```bash
# Install venv support
sudo apt install python3.11-venv

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install PySide6>=6.5.0 psutil>=5.9.0

# Run the GUI installer
./install_gui.sh
```

### Option 3: Conda Environment

If you have the conda environment set up from the main project:

```bash
# Activate conda environment
source .conda/bin/activate

# Install GUI dependencies
pip install PySide6>=6.5.0 psutil>=5.9.0

# Run the GUI installer
./install_gui.sh
```

## Usage

### Starting the GUI

```bash
# Method 1: Using make
make gui

# Method 2: Direct script
./brightness_gui.sh

# Method 3: Python directly
python3 brightness_gui.py
```

### GUI Features

#### System Tray Menu

- **Status**: Shows current service status (Running/Stopped)
- **Brightness Control**:
  - Toggle Brightness: Switch between high and low brightness
  - Set High Brightness: Apply the configured high brightness value
  - Set Low Brightness: Apply the configured low brightness value
- **Service Management**:
  - Start/Stop Service: Control the systemd service
  - Enable/Disable Auto-start: Control service auto-start on boot
- **Settings**: Configure brightness levels
- **Exit**: Close the GUI application

#### Settings Dialog

- **Higher Brightness**: Set the normal/high brightness level (10-100%)
- **Lower Brightness**: Set the dimmed/low brightness level (0-50%)
- Settings are automatically saved to `~/.brightness_toggle_config.json`

## Integration with Existing Service

The GUI integrates seamlessly with the existing brightness toggle service:

- **Shared Configuration**: Uses the same config file as the command-line version
- **Service Management**: Can start/stop the background service that provides keyboard shortcuts
- **Independent Operation**: Can control brightness even when the service is not running
- **Status Monitoring**: Real-time monitoring of service status

## Keyboard Shortcuts

When the background service is running, you can still use:
- **Ctrl+Alt+B**: Toggle brightness (works system-wide)

## Troubleshooting

### GUI Won't Start

1. **Check Dependencies**:
   ```bash
   python3 -c "import PySide6.QtWidgets; print('PySide6 OK')"
   python3 -c "import psutil; print('psutil OK')"
   ```

2. **Check Display**:
   ```bash
   echo $DISPLAY
   # Should show something like :0
   ```

3. **Check System Tray**:
   - Ensure your desktop environment supports system tray
   - Some minimal window managers may not have system tray support

### Service Management Issues

1. **Permission Errors**: Make sure you can run systemctl commands:
   ```bash
   systemctl --user status brightness-toggle
   ```

2. **Service Not Found**: Ensure the service is installed:
   ```bash
   ls ~/.config/systemd/user/brightness-toggle.service
   ```

### Brightness Control Issues

1. **No Displays Found**: Check if xrandr works:
   ```bash
   xrandr --query
   ```

2. **Permission Issues**: Ensure you can control display brightness:
   ```bash
   xrandr --output $(xrandr | grep " connected" | cut -d" " -f1 | head -1) --brightness 0.8
   ```

## Desktop Integration

After running `./install_gui.sh`, the application will be available in your application menu as "Brightness Control". You can:

1. **Add to Startup**: Add "Brightness Control" to your desktop environment's startup applications
2. **Create Shortcut**: Pin the application to your taskbar or desktop
3. **Auto-start**: The desktop entry includes auto-start configuration

## Files Created

- `brightness_gui.py`: Main GUI application
- `brightness_gui.sh`: Launcher script
- `brightness-control.desktop`: Desktop entry file
- `~/.local/share/applications/brightness-control.desktop`: Installed desktop entry

## Uninstallation

To remove the GUI components:

```bash
# Remove desktop entry
rm ~/.local/share/applications/brightness-control.desktop

# Remove GUI files (optional)
rm brightness_gui.py brightness_gui.sh brightness-control.desktop
```

The main service and configuration files are managed by the main project's uninstall script.

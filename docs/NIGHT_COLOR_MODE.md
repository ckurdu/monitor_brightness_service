# Night Color Mode Feature

## Overview

The brightness toggle application now supports two operational modes:
1. **Brightness Mode** (default): Controls monitor brightness via xrandr
2. **Night Color Mode**: Toggles KDE Plasma Night Color on/off

## Features

### Night Color Mode
- Toggle KDE Plasma's Night Color feature with the same Ctrl+Alt+B hotkey
- View current Night Color status and temperature
- Notifications show color temperature when enabled
- Persistent mode selection across restarts

### Mode Selection
The application remembers your preferred mode and saves it to the configuration file.

## Usage

### Via Manual Mode

Start the application in manual mode:
```bash
./dev.sh test
# or
conda run -p .conda python brightness_toggle.py
```

Commands:
- `t` or `toggle` - Toggle brightness/Night Color based on current mode
- `m` or `mode` - Switch between brightness and nightcolor modes
- `s` or `status` - Show current mode and status
- `n` or `nightinfo` - Show Night Color information
- `q` or `quit` - Exit

### Via Service

The service automatically uses the mode saved in your configuration:

```bash
# Check current service status
systemctl --user status brightness-toggle

# The hotkey Ctrl+Alt+B will toggle based on the saved mode
```

### Via Configuration File

Edit `~/.brightness_toggle_config.json`:

```json
{
  "mode": "nightcolor",
  "normal_brightness": 1.0,
  "low_brightness": 0.0,
  "is_dimmed": false,
  "night_color_enabled": true
}
```

Set `"mode"` to either:
- `"brightness"` - For monitor brightness control
- `"nightcolor"` - For Night Color toggle

## Example Workflow

### Switch to Night Color Mode

1. **Stop the service** (if running):
   ```bash
   systemctl --user stop brightness-toggle
   ```

2. **Run in manual mode**:
   ```bash
   ./dev.sh test
   ```

3. **Switch mode**:
   ```
   brightness> m
   Switched to Night Color mode
   ```

4. **Test the toggle**:
   ```
   brightness> t
   Night Color enabled (4500K)
   ```

5. **Verify status**:
   ```
   brightness> s
   Current mode: nightcolor
   Night Color: enabled
   Temperature: 4500K
   ```

6. **Exit and restart service**:
   ```
   brightness> q
   systemctl --user start brightness-toggle
   ```

Now pressing Ctrl+Alt+B will toggle Night Color instead of brightness!

### Switch Back to Brightness Mode

Repeat the process but use `m` command to switch back to brightness mode.

## Technical Details

### D-Bus Integration

Night Color is controlled via KDE's D-Bus interface:
- **Service**: `org.kde.KWin`
- **Path**: `/ColorCorrect`
- **Interface**: `org.kde.kwin.ColorCorrect`

Methods used:
- `enabled` - Get/set Night Color enabled state
- `currentTemperature` - Get current color temperature

### Requirements

- KDE Plasma desktop environment
- `qdbus` or `qdbus-qt5` package installed
- Night Color configured in KDE System Settings

### Installation

The deploy script automatically installs qdbus:

```bash
./deploy.sh
```

Or manually install:
```bash
# Debian/Ubuntu
sudo apt install qdbus-qt5

# Fedora
sudo dnf install qt5-qttools

# Arch Linux
sudo pacman -S qt5-tools
```

## Configuration Schema

The configuration file now includes mode selection:

```json
{
  "normal_brightness": 1.0,        // Normal brightness level (0.0-1.0)
  "low_brightness": 0.0,           // Dimmed brightness level (0.0-1.0)
  "is_dimmed": false,              // Current brightness state
  "mode": "brightness",            // Active mode: "brightness" or "nightcolor"
  "night_color_enabled": false     // Last known Night Color state
}
```

## Troubleshooting

### Night Color Commands Not Working

1. **Check if qdbus is installed**:
   ```bash
   which qdbus
   ```

2. **Test D-Bus connection**:
   ```bash
   qdbus org.kde.KWin /ColorCorrect org.kde.kwin.ColorCorrect.enabled
   ```

3. **Verify KDE Plasma is running**:
   ```bash
   echo $DESKTOP_SESSION
   # Should show "plasma" or similar
   ```

### Mode Not Persisting

Check configuration file permissions:
```bash
ls -la ~/.brightness_toggle_config.json
cat ~/.brightness_toggle_config.json
```

### Service Using Wrong Mode

1. Stop the service
2. Edit the config file to set desired mode
3. Restart the service

```bash
systemctl --user stop brightness-toggle
nano ~/.brightness_toggle_config.json
# Change "mode": "brightness" or "mode": "nightcolor"
systemctl --user start brightness-toggle
```

## Future Enhancements

Potential future features:
- Set specific Night Color temperature values
- Schedule automatic mode switching
- GUI mode selector in system tray
- Custom color temperature presets
- Integration with time-based triggers

#!/bin/bash

# Setup KDE keyboard shortcut for brightness toggle
# This creates a system-level shortcut that works reliably

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOGGLE_SCRIPT="$SCRIPT_DIR/brightness_toggle_simple.py"

echo "Setting up KDE keyboard shortcut for brightness toggle"
echo "====================================================="

# Create the simple toggle script
cat > "$TOGGLE_SCRIPT" << 'EOF'
#!/usr/bin/env python3
"""
Simple brightness toggle script for KDE shortcut
This script just toggles brightness and exits
"""

import subprocess
import json
from pathlib import Path

class BrightnessController:
    def __init__(self):
        self.config_file = Path.home() / '.brightness_toggle_config.json'
        self.normal_brightness = 1.0
        self.is_dimmed = False
        self.load_config()

    def load_config(self):
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.normal_brightness = config.get('normal_brightness', 1.0)
                    self.is_dimmed = config.get('is_dimmed', False)
        except Exception:
            pass

    def save_config(self):
        try:
            config = {
                'normal_brightness': self.normal_brightness,
                'is_dimmed': self.is_dimmed
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except Exception:
            pass

    def get_displays(self):
        try:
            result = subprocess.run(['xrandr', '--query'],
                                    capture_output=True, text=True, check=True)
            displays = []
            for line in result.stdout.split('\n'):
                if ' connected' in line and 'disconnected' not in line:
                    display_name = line.split()[0]
                    displays.append(display_name)
            return displays
        except:
            return []

    def get_current_brightness(self, display):
        try:
            result = subprocess.run(['xrandr', '--verbose'], 
                                    capture_output=True, text=True, check=True)
            lines = result.stdout.split('\n')
            for i, line in enumerate(lines):
                if display in line and ' connected' in line:
                    for j in range(i+1, min(i+10, len(lines))):
                        if 'Brightness:' in lines[j]:
                            brightness_str = lines[j].split('Brightness:')[1].strip()
                            return float(brightness_str)
            return 1.0
        except:
            return 1.0

    def set_brightness(self, brightness):
        displays = self.get_displays()
        if not displays:
            return False

        for display in displays:
            try:
                cmd = ['xrandr', '--output', display, '--brightness', str(brightness)]
                subprocess.run(cmd, check=True, capture_output=True)
            except:
                pass
        return True

    def show_notification(self, message):
        try:
            subprocess.run(['notify-send', 'Brightness Toggle', message],
                           check=False, capture_output=True)
        except:
            pass

    def toggle_brightness(self):
        try:
            if self.is_dimmed:
                # Restore to normal brightness
                self.set_brightness(self.normal_brightness)
                self.is_dimmed = False
                brightness_pct = self.normal_brightness * 100
                message = f"Brightness restored to {brightness_pct:.0f}%"
                self.show_notification(message)
            else:
                # Save current brightness before dimming
                displays = self.get_displays()
                if displays:
                    current_brightness = self.get_current_brightness(displays[0])
                    if current_brightness > 0.1:
                        self.normal_brightness = current_brightness
                
                # Dim to 0% brightness
                self.set_brightness(0.0)
                self.is_dimmed = True
                self.show_notification("Brightness set to 0%")

            self.save_config()
        except Exception as e:
            self.show_notification(f"Error: {e}")

if __name__ == "__main__":
    controller = BrightnessController()
    controller.toggle_brightness()
EOF

chmod +x "$TOGGLE_SCRIPT"

echo "Created toggle script: $TOGGLE_SCRIPT"
echo ""
echo "Now setting up KDE keyboard shortcut..."
echo ""
echo "Please follow these steps to set up the keyboard shortcut:"
echo ""
echo "1. Open System Settings (systemsettings5)"
echo "2. Go to Shortcuts → Custom Shortcuts"
echo "3. Click 'Edit' → 'New' → 'Global Shortcut' → 'Command/URL'"
echo "4. Set the name to: 'Brightness Toggle'"
echo "5. In the 'Trigger' tab, set the shortcut to: Ctrl+Alt+B"
echo "6. In the 'Action' tab, set the command to:"
echo "   $TOGGLE_SCRIPT"
echo "7. Click 'Apply'"
echo ""
echo "Alternative: Run this command to open System Settings directly:"
echo "systemsettings5 kcm_keys"
echo ""
echo "After setup, press Ctrl+Alt+B to toggle brightness!"

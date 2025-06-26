#!/usr/bin/env python3
"""
Monitor Brightness Toggle for Debian Linux with KDE
A Python script that toggles monitor brightness between 0% and normal with a hotkey.
Optimized for Debian Linux with KDE Plasma desktop environment.
"""

import subprocess
import json
from pathlib import Path
try:
    from pynput import keyboard
    from pynput.keyboard import Key, KeyCode, Listener
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False


class BrightnessController:
    def __init__(self):
        self.config_file = Path.home() / '.brightness_toggle_config.json'
        self.normal_brightness = 1.0  # Default normal brightness (100%)
        self.is_dimmed = False

        # Load saved configuration
        self.load_config()

    def load_config(self):
        """Load saved brightness configuration"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.normal_brightness = config.get(
                        'normal_brightness', 1.0)
                    self.is_dimmed = config.get('is_dimmed', False)
        except Exception as e:
            print(f"Warning: Could not load config: {e}")

    def save_config(self):
        """Save current brightness configuration"""
        try:
            config = {
                'normal_brightness': self.normal_brightness,
                'is_dimmed': self.is_dimmed
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Warning: Could not save config: {e}")

    def get_displays(self):
        """Get list of connected displays using xrandr"""
        try:
            result = subprocess.run(['xrandr', '--query'],
                                    capture_output=True, text=True, check=True)
            displays = []
            for line in result.stdout.split('\n'):
                if ' connected' in line and 'disconnected' not in line:
                    display_name = line.split()[0]
                    displays.append(display_name)
            return displays
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Error: xrandr not found. "
                  "Install with: sudo apt install x11-xserver-utils")
            return []

    def get_current_brightness(self, display):
        """Get current brightness for a display"""
        try:
            result = subprocess.run(['xrandr', '--verbose'],
                                    capture_output=True, text=True, check=True)
            lines = result.stdout.split('\n')
            for i, line in enumerate(lines):
                if display in line and ' connected' in line:
                    # Look for brightness line in the next few lines
                    for j in range(i+1, min(i+10, len(lines))):
                        if 'Brightness:' in lines[j]:
                            brightness_str = lines[j].split('Brightness:')[1].strip()
                            return float(brightness_str)
            return 1.0  # Default brightness
        except Exception:
            return 1.0

    def set_brightness(self, brightness):
        """Set brightness using xrandr --brightness"""
        displays = self.get_displays()
        if not displays:
            return False

        success = True
        for display in displays:
            try:
                cmd = ['xrandr', '--output', display, '--brightness', str(brightness)]
                subprocess.run(cmd, check=True, capture_output=True)
                brightness_pct = brightness * 100
                print(f"Set brightness to {brightness_pct:.0f}% for {display}")
            except subprocess.CalledProcessError as e:
                print(f"Failed to set brightness for display {display}: {e}")
                success = False
        return success

    def show_kde_notification(self, message):
        """Show a KDE notification"""
        try:
            subprocess.run(['notify-send', 'Brightness Toggle', message],
                           check=False, capture_output=True)
        except FileNotFoundError:
            # notify-send not available, just print
            pass

    def save_current_brightness_as_normal(self):
        """Save current brightness as the normal brightness"""
        displays = self.get_displays()
        if displays:
            # Get current brightness from first display as reference
            current_brightness = self.get_current_brightness(displays[0])
            if current_brightness > 0.1:  # Only save if not currently dimmed
                self.normal_brightness = current_brightness
                brightness_pct = current_brightness * 100
                print(f"Saved current brightness ({brightness_pct:.0f}%) as normal")

    def toggle_brightness(self):
        """Toggle between normal brightness and zero brightness"""
        try:
            if self.is_dimmed:
                # Restore to normal brightness
                success = self.set_brightness(self.normal_brightness)
                if success:
                    self.is_dimmed = False
                    brightness_pct = self.normal_brightness * 100
                    message = f"Brightness restored to {brightness_pct:.0f}%"
                    print(message)
                    self.show_kde_notification(message)
            else:
                # Save current brightness before dimming
                self.save_current_brightness_as_normal()

                # Dim to 0% brightness
                success = self.set_brightness(0.0)
                if success:
                    self.is_dimmed = True
                    message = "Brightness set to 0%"
                    print(message)
                    self.show_kde_notification(message)

            if success:
                self.save_config()

        except Exception as e:
            error_msg = f"Error toggling brightness: {e}"
            print(error_msg)
            self.show_kde_notification(error_msg)


class KeyboardShortcutHandler:
    def __init__(self, controller):
        self.controller = controller
        self.ctrl_pressed = False
        self.alt_pressed = False

    def on_press(self, key):
        try:
            if key == Key.ctrl_l or key == Key.ctrl_r:
                self.ctrl_pressed = True
            elif key == Key.alt_l or key == Key.alt_r:
                self.alt_pressed = True
            elif hasattr(key, 'char') and key.char == 'b':
                if self.ctrl_pressed and self.alt_pressed:
                    print("Ctrl+Alt+B pressed - toggling brightness...")
                    self.controller.toggle_brightness()
        except AttributeError:
            pass

    def on_release(self, key):
        try:
            if key == Key.ctrl_l or key == Key.ctrl_r:
                self.ctrl_pressed = False
            elif key == Key.alt_l or key == Key.alt_r:
                self.alt_pressed = False
            elif key == Key.esc:
                print("Escape pressed - exiting...")
                return False
        except AttributeError:
            pass

    def start_listening(self):
        print("Keyboard shortcut listener started!")
        print("Press Ctrl+Alt+B to toggle brightness")
        print("Press Escape to exit")
        print()

        with Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()


def run_with_keyboard_shortcut(controller):
    """Run with pynput keyboard shortcut support"""
    try:
        handler = KeyboardShortcutHandler(controller)
        handler.start_listening()
        return True
    except Exception as e:
        print(f"Keyboard shortcut error: {e}")
        return False


def run_manual_mode(controller):
    """Run with manual command input"""
    print("Manual command mode")
    print("Commands:")
    print("  t or toggle - Toggle brightness between 0% and normal")
    print("  s or status - Show current status")
    print("  q or quit   - Exit the program")
    print()

    try:
        while True:
            try:
                command = input("brightness> ").strip().lower()

                if command in ['t', 'toggle']:
                    controller.toggle_brightness()
                elif command in ['s', 'status']:
                    if controller.is_dimmed:
                        status = "dimmed (0%)"
                    else:
                        brightness_pct = controller.normal_brightness * 100
                        status = f"normal ({brightness_pct:.0f}%)"
                    print(f"Current brightness: {status}")
                elif command in ['q', 'quit', 'exit']:
                    print("Exiting...")
                    break
                elif command == '':
                    continue
                else:
                    print("Unknown command. Use 't' to toggle, 's' for status, "
                          "'q' to quit.")

            except EOFError:
                print("\nExiting...")
                break

    except KeyboardInterrupt:
        print("\nExiting...")


def main():
    import sys
    import os
    
    print("Monitor Brightness Toggle for Debian Linux with KDE")
    print("==================================================")

    controller = BrightnessController()

    # Test if brightness control works
    print("Testing brightness control...")
    displays = controller.get_displays()
    if displays:
        print(f"Found displays: {', '.join(displays)}")
    else:
        print("No displays found or xrandr not available")
        return

    # Check if running in non-interactive mode (service)
    is_service = not sys.stdin.isatty() or os.getenv('SYSTEMD_EXEC_PID') is not None

    # Choose mode based on pynput availability and environment
    if PYNPUT_AVAILABLE:
        if is_service:
            # Running as service - automatically use keyboard shortcut mode
            print("\nRunning as service - starting keyboard shortcut mode...")
            print("Press Ctrl+Alt+B to toggle brightness")
            if not run_with_keyboard_shortcut(controller):
                print("Keyboard shortcut mode failed!")
                return
        else:
            # Interactive mode - ask user for preference
            print("\nChoose mode:")
            print("1. Keyboard shortcut mode (Ctrl+Alt+B)")
            print("2. Manual command mode")
            print()

            try:
                choice = input("Enter choice (1 or 2, default=1): ").strip()
                if choice == '2':
                    run_manual_mode(controller)
                else:
                    print("\nStarting keyboard shortcut mode...")
                    if not run_with_keyboard_shortcut(controller):
                        print("Falling back to manual mode...")
                        run_manual_mode(controller)
            except (EOFError, KeyboardInterrupt):
                print("\nExiting...")
    else:
        if is_service:
            print("\nError: pynput not available - cannot run as service")
            print("Install pynput: pip install pynput")
            return
        else:
            print("\npynput not available - using manual mode")
            print("To enable keyboard shortcuts, install: pip install pynput")
            print()
            run_manual_mode(controller)


if __name__ == "__main__":
    main()

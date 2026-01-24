#!/usr/bin/env python3
"""
Monitor Brightness Toggle for Debian Linux with KDE
A Python script that toggles monitor brightness between 0% and normal with a hotkey.
Optimized for Debian Linux with KDE Plasma desktop environment.
"""

import subprocess
import json
import os
import signal
from pathlib import Path
try:
    from pynput import keyboard
    from pynput.keyboard import Key, KeyCode, Listener
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class BrightnessController:
    def __init__(self):
        self.config_file = Path.home() / '.brightness_toggle_config.json'
        self.normal_brightness = 1.0  # Default normal brightness (100%)
        self.low_brightness = 0.0  # Default low brightness (0%)
        self.is_dimmed = False
        self.mode = 'brightness'  # Default mode: 'brightness' or 'nightcolor'
        self.night_color_enabled = False

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
                    self.low_brightness = config.get(
                        'low_brightness', 0.0)
                    self.is_dimmed = config.get('is_dimmed', False)
                    self.mode = config.get('mode', 'brightness')
                    self.night_color_enabled = config.get('night_color_enabled', False)
        except Exception as e:
            print(f"Warning: Could not load config: {e}")

    def save_config(self):
        """Save current brightness configuration"""
        try:
            config = {
                'normal_brightness': self.normal_brightness,
                'low_brightness': self.low_brightness,
                'is_dimmed': self.is_dimmed,
                'mode': self.mode,
                'night_color_enabled': self.night_color_enabled
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

    def get_night_color_status(self):
        """Get Night Color status via D-Bus"""
        try:
            result = subprocess.run(
                ['qdbus', 'org.kde.KWin', '/ColorCorrect',
                 'org.kde.kwin.ColorCorrect.enabled'],
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip().lower() == 'true'
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Warning: Could not get Night Color status. Is KDE Plasma running?")
            return False

    def set_night_color(self, enabled):
        """Enable or disable Night Color via D-Bus"""
        try:
            value = 'true' if enabled else 'false'
            subprocess.run(
                ['qdbus', 'org.kde.KWin', '/ColorCorrect',
                 'org.kde.kwin.ColorCorrect.enabled', value],
                check=True, capture_output=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Failed to set Night Color: {e}")
            print("Make sure qdbus is installed: sudo apt install qdbus-qt5")
            return False

    def get_night_color_temperature(self):
        """Get current Night Color temperature"""
        try:
            result = subprocess.run(
                ['qdbus', 'org.kde.KWin', '/ColorCorrect',
                 'org.kde.kwin.ColorCorrect.currentTemperature'],
                capture_output=True, text=True, check=True
            )
            return int(result.stdout.strip())
        except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
            return None

    def toggle_night_color(self):
        """Toggle Night Color on/off"""
        try:
            current_status = self.get_night_color_status()
            new_status = not current_status
            
            success = self.set_night_color(new_status)
            if success:
                self.night_color_enabled = new_status
                temp = self.get_night_color_temperature()
                
                if new_status:
                    message = f"Night Color enabled"
                    if temp:
                        message += f" ({temp}K)"
                    print(message)
                    self.show_kde_notification(message)
                else:
                    message = "Night Color disabled"
                    print(message)
                    self.show_kde_notification(message)
                
                self.save_config()
            return success
        except Exception as e:
            error_msg = f"Error toggling Night Color: {e}"
            print(error_msg)
            self.show_kde_notification(error_msg)
            return False

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
        """Toggle between brightness modes or Night Color based on selected mode"""
        try:
            if self.mode == 'nightcolor':
                # Toggle Night Color mode
                self.toggle_night_color()
            else:
                # Toggle brightness mode (default)
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
                    # Dim to low brightness
                    success = self.set_brightness(self.low_brightness)
                    if success:
                        self.is_dimmed = True
                        message = "Brightness set to 0%"
                        print(message)
                        self.show_kde_notification(message)

                if success:
                    self.save_config()

        except Exception as e:
            error_msg = f"Error toggling: {e}"
            print(error_msg)
            self.show_kde_notification(error_msg)

    def get_service_status(self):
        """Get systemd service status"""
        try:
            result = subprocess.run(['systemctl', '--user', 'is-active', 'brightness-toggle'],
                                    capture_output=True, text=True)
            is_active = result.returncode == 0 and result.stdout.strip() == 'active'
            
            result = subprocess.run(['systemctl', '--user', 'is-enabled', 'brightness-toggle'],
                                    capture_output=True, text=True)
            is_enabled = result.returncode == 0 and result.stdout.strip() == 'enabled'
            
            return {
                'active': is_active,
                'enabled': is_enabled,
                'status': 'running' if is_active else 'stopped'
            }
        except Exception as e:
            print(f"Error getting service status: {e}")
            return {'active': False, 'enabled': False, 'status': 'unknown'}

    def start_service(self):
        """Start the systemd service"""
        try:
            result = subprocess.run(['systemctl', '--user', 'start', 'brightness-toggle'],
                                    capture_output=True, text=True, check=True)
            return True, "Service started successfully"
        except subprocess.CalledProcessError as e:
            return False, f"Failed to start service: {e.stderr}"

    def stop_service(self):
        """Stop the systemd service"""
        try:
            result = subprocess.run(['systemctl', '--user', 'stop', 'brightness-toggle'],
                                    capture_output=True, text=True, check=True)
            return True, "Service stopped successfully"
        except subprocess.CalledProcessError as e:
            return False, f"Failed to stop service: {e.stderr}"

    def enable_service(self):
        """Enable the systemd service for auto-start"""
        try:
            result = subprocess.run(['systemctl', '--user', 'enable', 'brightness-toggle'],
                                    capture_output=True, text=True, check=True)
            return True, "Service enabled for auto-start"
        except subprocess.CalledProcessError as e:
            return False, f"Failed to enable service: {e.stderr}"

    def disable_service(self):
        """Disable the systemd service auto-start"""
        try:
            result = subprocess.run(['systemctl', '--user', 'disable', 'brightness-toggle'],
                                    capture_output=True, text=True, check=True)
            return True, "Service disabled from auto-start"
        except subprocess.CalledProcessError as e:
            return False, f"Failed to disable service: {e.stderr}"

    def is_service_process_running(self):
        """Check if brightness service process is running using psutil"""
        if not PSUTIL_AVAILABLE:
            return False
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info['cmdline']
                    if cmdline and len(cmdline) >= 2:
                        if 'python' in cmdline[0] and 'brightness_toggle.py' in ' '.join(cmdline):
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return False
        except Exception:
            return False


class KeyboardShortcutHandler:
    def __init__(self, controller, is_service=False):
        self.controller = controller
        self.ctrl_pressed = False
        self.alt_pressed = False
        self.is_service = is_service

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
            elif key == Key.esc and not self.is_service:
                print("Escape pressed - exiting...")
                return False
        except AttributeError:
            pass

    def start_listening(self):
        print("Keyboard shortcut listener started!")
        print("Press Ctrl+Alt+B to toggle brightness")
        if not self.is_service:
            print("Press Escape to exit")
        print()

        with Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()


def run_with_keyboard_shortcut(controller, is_service=False):
    """Run with pynput keyboard shortcut support"""
    try:
        handler = KeyboardShortcutHandler(controller, is_service)
        handler.start_listening()
        return True
    except Exception as e:
        print(f"Keyboard shortcut error: {e}")
        return False


def run_manual_mode(controller):
    """Run with manual command input"""
    print("Manual command mode")
    print("Commands:")
    print("  t or toggle    - Toggle based on current mode")
    print("  s or status    - Show current status")
    print("  m or mode      - Switch between brightness/nightcolor mode")
    print("  n or nightinfo - Show Night Color information")
    print("  q or quit      - Exit the program")
    print()

    try:
        while True:
            try:
                command = input("brightness> ").strip().lower()

                if command in ['t', 'toggle']:
                    controller.toggle_brightness()
                elif command in ['s', 'status']:
                    print(f"Current mode: {controller.mode}")
                    if controller.mode == 'nightcolor':
                        nc_status = controller.get_night_color_status()
                        temp = controller.get_night_color_temperature()
                        print(f"Night Color: {'enabled' if nc_status else 'disabled'}")
                        if temp:
                            print(f"Temperature: {temp}K")
                    else:
                        if controller.is_dimmed:
                            status = "dimmed (0%)"
                        else:
                            brightness_pct = controller.normal_brightness * 100
                            status = f"normal ({brightness_pct:.0f}%)"
                        print(f"Current brightness: {status}")
                elif command in ['m', 'mode']:
                    if controller.mode == 'brightness':
                        controller.mode = 'nightcolor'
                        print("Switched to Night Color mode")
                    else:
                        controller.mode = 'brightness'
                        print("Switched to brightness mode")
                    controller.save_config()
                elif command in ['n', 'nightinfo']:
                    nc_status = controller.get_night_color_status()
                    temp = controller.get_night_color_temperature()
                    print(f"Night Color status: {'enabled' if nc_status else 'disabled'}")
                    if temp:
                        print(f"Current temperature: {temp}K")
                elif command in ['q', 'quit', 'exit']:
                    print("Exiting...")
                    break
                elif command == '':
                    continue
                else:
                    print("Unknown command. Type 't' to toggle, 's' for status,")
                    print("'m' to change mode, 'n' for night info, 'q' to quit.")

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
            if not run_with_keyboard_shortcut(controller, is_service):
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
                    if not run_with_keyboard_shortcut(controller, False):
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

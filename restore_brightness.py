#!/usr/bin/env python3
"""
Restore normal brightness/gamma settings
Use this if your brightness got stuck or you want to reset to normal
"""

import subprocess

def get_displays():
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
        print("Error: xrandr not found.")
        return []

def restore_normal_brightness():
    """Restore normal brightness/gamma for all displays"""
    displays = get_displays()
    if not displays:
        print("No displays found")
        return False
    
    success = True
    for display in displays:
        try:
            # Reset to normal gamma (1.0:1.0:1.0) and normal brightness
            subprocess.run(['xrandr', '--output', display, '--gamma', '1.0:1.0:1.0', 
                           '--brightness', '1.0'], check=True, capture_output=True)
            print(f"Restored normal brightness for {display}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to restore brightness for {display}: {e}")
            success = False
    
    return success

if __name__ == "__main__":
    print("Brightness Restore Tool")
    print("======================")
    print("This will restore normal brightness/gamma for all displays")
    print()
    
    if restore_normal_brightness():
        print("\nBrightness restored successfully!")
    else:
        print("\nSome displays could not be restored.")
    
    print("\nYou can now run the brightness toggle script normally.")

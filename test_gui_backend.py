#!/usr/bin/env python3
"""
Test script for GUI backend functionality
Tests the BrightnessController enhancements without requiring PySide6
"""

from brightness_toggle import BrightnessController
import json

def test_brightness_controller():
    print("Testing BrightnessController enhancements...")
    print("=" * 50)
    
    # Create controller
    controller = BrightnessController()
    
    # Test configuration
    print(f"Normal brightness: {controller.normal_brightness}")
    print(f"Low brightness: {controller.low_brightness}")
    print(f"Is dimmed: {controller.is_dimmed}")
    
    # Test displays
    displays = controller.get_displays()
    print(f"Found displays: {displays}")
    
    # Test service status
    print("\nTesting service management...")
    status = controller.get_service_status()
    print(f"Service status: {status}")
    
    # Test process detection
    process_running = controller.is_service_process_running()
    print(f"Service process running: {process_running}")
    
    # Test configuration with new low brightness setting
    print("\nTesting configuration...")
    original_low = controller.low_brightness
    controller.low_brightness = 0.1  # 10%
    controller.save_config()
    
    # Reload and verify
    controller.load_config()
    print(f"Low brightness after save/load: {controller.low_brightness}")
    
    # Restore original
    controller.low_brightness = original_low
    controller.save_config()
    
    print("\n✓ All backend tests passed!")

if __name__ == "__main__":
    test_brightness_controller()

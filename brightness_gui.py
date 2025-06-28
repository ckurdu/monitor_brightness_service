#!/usr/bin/env python3
"""
Monitor Brightness Toggle - GUI Application
A PySide6 system tray application to manage the brightness toggle service.
"""

import sys
import os
import json
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QSystemTrayIcon, QMenu, QDialog, 
                               QVBoxLayout, QHBoxLayout, QLabel, QSlider, 
                               QPushButton, QCheckBox, QSpinBox, QDoubleSpinBox,
                               QGroupBox, QMessageBox, QProgressBar)
from PySide6.QtCore import Qt, QTimer, Signal, QThread
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QAction

# Import our brightness controller
from brightness_toggle import BrightnessController


class ServiceStatusThread(QThread):
    """Thread to check service status without blocking UI"""
    status_updated = Signal(dict)
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.running = True
    
    def run(self):
        while self.running:
            try:
                status = self.controller.get_service_status()
                self.status_updated.emit(status)
                self.msleep(2000)  # Check every 2 seconds
            except Exception as e:
                print(f"Status thread error: {e}")
                self.msleep(5000)
    
    def stop(self):
        self.running = False
        self.quit()
        self.wait()


class SettingsDialog(QDialog):
    """Settings dialog for brightness configuration"""
    
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Brightness Settings")
        self.setFixedSize(400, 300)
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Brightness settings group
        brightness_group = QGroupBox("Brightness Levels")
        brightness_layout = QVBoxLayout(brightness_group)
        
        # Normal brightness
        normal_layout = QHBoxLayout()
        normal_layout.addWidget(QLabel("Higher Brightness:"))
        self.normal_slider = QSlider(Qt.Horizontal)
        self.normal_slider.setRange(10, 100)
        self.normal_slider.setValue(100)
        self.normal_slider.setTickPosition(QSlider.TicksBelow)
        self.normal_slider.setTickInterval(10)
        self.normal_label = QLabel("100%")
        self.normal_slider.valueChanged.connect(
            lambda v: self.normal_label.setText(f"{v}%"))
        normal_layout.addWidget(self.normal_slider)
        normal_layout.addWidget(self.normal_label)
        brightness_layout.addLayout(normal_layout)
        
        # Low brightness
        low_layout = QHBoxLayout()
        low_layout.addWidget(QLabel("Lower Brightness:"))
        self.low_slider = QSlider(Qt.Horizontal)
        self.low_slider.setRange(0, 50)
        self.low_slider.setValue(0)
        self.low_slider.setTickPosition(QSlider.TicksBelow)
        self.low_slider.setTickInterval(5)
        self.low_label = QLabel("0%")
        self.low_slider.valueChanged.connect(
            lambda v: self.low_label.setText(f"{v}%"))
        low_layout.addWidget(self.low_slider)
        low_layout.addWidget(self.low_label)
        brightness_layout.addLayout(low_layout)
        
        layout.addWidget(brightness_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        self.save_button.clicked.connect(self.save_settings)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
    
    def load_settings(self):
        """Load current settings into the dialog"""
        normal_pct = int(self.controller.normal_brightness * 100)
        low_pct = int(self.controller.low_brightness * 100)
        
        self.normal_slider.setValue(normal_pct)
        self.low_slider.setValue(low_pct)
        self.normal_label.setText(f"{normal_pct}%")
        self.low_label.setText(f"{low_pct}%")
    
    def save_settings(self):
        """Save settings and close dialog"""
        self.controller.normal_brightness = self.normal_slider.value() / 100.0
        self.controller.low_brightness = self.low_slider.value() / 100.0
        self.controller.save_config()
        self.accept()


class BrightnessSystemTray(QSystemTrayIcon):
    """Main system tray application"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = BrightnessController()
        self.status_thread = None
        self.setup_icon()
        self.setup_menu()
        self.setup_status_monitoring()
        
        # Show initial notification
        self.showMessage("Brightness Control", 
                        "Brightness control is now running in system tray",
                        QSystemTrayIcon.Information, 3000)
    
    def setup_icon(self):
        """Create and set the system tray icon"""
        # Create a simple icon programmatically
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw a brightness icon (sun-like)
        painter.setBrush(QColor(255, 215, 0))  # Gold color
        painter.setPen(QColor(255, 165, 0))    # Orange outline
        painter.drawEllipse(8, 8, 16, 16)
        
        # Draw simple rays
        painter.setPen(QColor(255, 215, 0))
        painter.drawLine(16, 2, 16, 6)    # Top
        painter.drawLine(16, 26, 16, 30)  # Bottom
        painter.drawLine(2, 16, 6, 16)    # Left
        painter.drawLine(26, 16, 30, 16)  # Right
        painter.drawLine(6, 6, 10, 10)    # Top-left
        painter.drawLine(22, 22, 26, 26)  # Bottom-right
        painter.drawLine(26, 6, 22, 10)   # Top-right
        painter.drawLine(10, 22, 6, 26)   # Bottom-left
        
        painter.end()
        
        icon = QIcon(pixmap)
        self.setIcon(icon)
    
    def setup_menu(self):
        """Setup the context menu"""
        self.menu = QMenu()
        
        # Status section
        self.status_action = QAction("Status: Checking...", self)
        self.status_action.setEnabled(False)
        self.menu.addAction(self.status_action)
        self.menu.addSeparator()
        
        # Brightness controls
        brightness_menu = self.menu.addMenu("Brightness Control")
        
        self.toggle_action = QAction("Toggle Brightness", self)
        self.toggle_action.triggered.connect(self.toggle_brightness)
        brightness_menu.addAction(self.toggle_action)
        
        self.set_high_action = QAction("Set High Brightness", self)
        self.set_high_action.triggered.connect(self.set_high_brightness)
        brightness_menu.addAction(self.set_high_action)
        
        self.set_low_action = QAction("Set Low Brightness", self)
        self.set_low_action.triggered.connect(self.set_low_brightness)
        brightness_menu.addAction(self.set_low_action)
        
        self.menu.addSeparator()
        
        # Service management
        service_menu = self.menu.addMenu("Service Management")
        
        self.start_service_action = QAction("Start Service", self)
        self.start_service_action.triggered.connect(self.start_service)
        service_menu.addAction(self.start_service_action)
        
        self.stop_service_action = QAction("Stop Service", self)
        self.stop_service_action.triggered.connect(self.stop_service)
        service_menu.addAction(self.stop_service_action)
        
        service_menu.addSeparator()
        
        self.enable_service_action = QAction("Enable Auto-start", self)
        self.enable_service_action.triggered.connect(self.enable_service)
        service_menu.addAction(self.enable_service_action)
        
        self.disable_service_action = QAction("Disable Auto-start", self)
        self.disable_service_action.triggered.connect(self.disable_service)
        service_menu.addAction(self.disable_service_action)
        
        self.menu.addSeparator()
        
        # Settings
        self.settings_action = QAction("Settings...", self)
        self.settings_action.triggered.connect(self.show_settings)
        self.menu.addAction(self.settings_action)
        
        self.menu.addSeparator()
        
        # Exit
        self.exit_action = QAction("Exit", self)
        self.exit_action.triggered.connect(self.exit_application)
        self.menu.addAction(self.exit_action)
        
        self.setContextMenu(self.menu)
    
    def setup_status_monitoring(self):
        """Setup background status monitoring"""
        self.status_thread = ServiceStatusThread(self.controller)
        self.status_thread.status_updated.connect(self.update_status)
        self.status_thread.start()
    
    def update_status(self, status):
        """Update UI based on service status"""
        if status['active']:
            self.status_action.setText("Status: Service Running")
            self.start_service_action.setEnabled(False)
            self.stop_service_action.setEnabled(True)
        else:
            self.status_action.setText("Status: Service Stopped")
            self.start_service_action.setEnabled(True)
            self.stop_service_action.setEnabled(False)
        
        if status['enabled']:
            self.enable_service_action.setEnabled(False)
            self.disable_service_action.setEnabled(True)
        else:
            self.enable_service_action.setEnabled(True)
            self.disable_service_action.setEnabled(False)
    
    def toggle_brightness(self):
        """Toggle brightness between high and low"""
        try:
            self.controller.toggle_brightness()
            state = "Low" if self.controller.is_dimmed else "High"
            self.showMessage("Brightness Toggle", 
                           f"Brightness set to {state}",
                           QSystemTrayIcon.Information, 2000)
        except Exception as e:
            self.showMessage("Error", f"Failed to toggle brightness: {e}",
                           QSystemTrayIcon.Critical, 3000)
    
    def set_high_brightness(self):
        """Set brightness to high value"""
        try:
            self.controller.set_brightness(self.controller.normal_brightness)
            self.controller.is_dimmed = False
            self.controller.save_config()
            pct = int(self.controller.normal_brightness * 100)
            self.showMessage("Brightness Control", 
                           f"Brightness set to {pct}%",
                           QSystemTrayIcon.Information, 2000)
        except Exception as e:
            self.showMessage("Error", f"Failed to set brightness: {e}",
                           QSystemTrayIcon.Critical, 3000)
    
    def set_low_brightness(self):
        """Set brightness to low value"""
        try:
            self.controller.set_brightness(self.controller.low_brightness)
            self.controller.is_dimmed = True
            self.controller.save_config()
            pct = int(self.controller.low_brightness * 100)
            self.showMessage("Brightness Control", 
                           f"Brightness set to {pct}%",
                           QSystemTrayIcon.Information, 2000)
        except Exception as e:
            self.showMessage("Error", f"Failed to set brightness: {e}",
                           QSystemTrayIcon.Critical, 3000)
    
    def start_service(self):
        """Start the systemd service"""
        success, message = self.controller.start_service()
        icon_type = QSystemTrayIcon.Information if success else QSystemTrayIcon.Critical
        self.showMessage("Service Management", message, icon_type, 3000)
    
    def stop_service(self):
        """Stop the systemd service"""
        success, message = self.controller.stop_service()
        icon_type = QSystemTrayIcon.Information if success else QSystemTrayIcon.Critical
        self.showMessage("Service Management", message, icon_type, 3000)
    
    def enable_service(self):
        """Enable service auto-start"""
        success, message = self.controller.enable_service()
        icon_type = QSystemTrayIcon.Information if success else QSystemTrayIcon.Critical
        self.showMessage("Service Management", message, icon_type, 3000)
    
    def disable_service(self):
        """Disable service auto-start"""
        success, message = self.controller.disable_service()
        icon_type = QSystemTrayIcon.Information if success else QSystemTrayIcon.Critical
        self.showMessage("Service Management", message, icon_type, 3000)
    
    def show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self.controller)
        if dialog.exec() == QDialog.Accepted:
            self.showMessage("Settings", "Settings saved successfully",
                           QSystemTrayIcon.Information, 2000)
    
    def exit_application(self):
        """Exit the application"""
        if self.status_thread:
            self.status_thread.stop()
        QApplication.quit()


def main():
    app = QApplication(sys.argv)
    
    # Check if system tray is available
    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, "System Tray",
                           "System tray is not available on this system.")
        sys.exit(1)
    
    # Prevent application from quitting when last window is closed
    app.setQuitOnLastWindowClosed(False)
    
    # Create and show system tray
    tray = BrightnessSystemTray()
    tray.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

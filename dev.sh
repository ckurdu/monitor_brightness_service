#!/bin/bash

# Development and testing script for Monitor Brightness Toggle

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

echo "Monitor Brightness Toggle - Development Script"
echo "============================================="
echo

# Function to run with conda environment
run_with_conda() {
    if [ -d "$PROJECT_DIR/.conda" ]; then
        export CONDA_PREFIX="$PROJECT_DIR/.conda"
        export PATH="$CONDA_PREFIX/bin:$PATH"
        cd "$PROJECT_DIR"
        "$@"
    else
        echo "Error: Conda environment not found. Run ./deploy.sh first."
        exit 1
    fi
}

# Parse command line arguments
case "${1:-help}" in
    "test")
        echo "Testing application..."
        run_with_conda python brightness_toggle.py
        ;;
    "env-info")
        echo "Environment Information:"
        echo "======================="
        run_with_conda python -c "
import sys
print(f'Python: {sys.executable}')
print(f'Version: {sys.version}')
print('Packages:')
try:
    import pynput
    print(f'  pynput: {pynput.__version__}')
except ImportError:
    print('  pynput: NOT INSTALLED')
"
        ;;
    "check-displays")
        echo "Checking displays..."
        run_with_conda python -c "
import subprocess
try:
    result = subprocess.run(['xrandr', '--query'], capture_output=True, text=True, check=True)
    displays = []
    for line in result.stdout.split('\n'):
        if ' connected' in line and 'disconnected' not in line:
            displays.append(line.split()[0])
    print(f'Connected displays: {displays}')
    
    if displays:
        for display in displays:
            result = subprocess.run(['xrandr', '--verbose'], capture_output=True, text=True, check=True)
            lines = result.stdout.split('\n')
            for i, line in enumerate(lines):
                if display in line and ' connected' in line:
                    for j in range(i+1, min(i+10, len(lines))):
                        if 'Brightness:' in lines[j]:
                            brightness = lines[j].split('Brightness:')[1].strip()
                            print(f'  {display}: brightness = {brightness}')
                            break
except Exception as e:
    print(f'Error: {e}')
"
        ;;
    "service-status")
        echo "Service Status:"
        echo "=============="
        systemctl --user status brightness-toggle --no-pager -l || echo "Service not found/running"
        ;;
    "service-logs")
        echo "Service Logs:"
        echo "============"
        journalctl --user -u brightness-toggle --no-pager -n 20
        ;;
    "service-start")
        echo "Starting service..."
        systemctl --user start brightness-toggle
        ;;
    "service-stop")
        echo "Stopping service..."
        systemctl --user stop brightness-toggle
        ;;
    "service-restart")
        echo "Restarting service..."
        systemctl --user restart brightness-toggle
        ;;
    "install-deps")
        echo "Installing development dependencies..."
        run_with_conda pip install -r requirements.txt
        ;;
    "clean")
        echo "Cleaning up..."
        find "$PROJECT_DIR" -name "*.pyc" -delete
        find "$PROJECT_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
        echo "✓ Python cache cleaned"
        ;;
    "help"|*)
        echo "Usage: $0 <command>"
        echo
        echo "Commands:"
        echo "  test           - Run the application directly"
        echo "  env-info       - Show environment information"
        echo "  check-displays - Check connected displays and brightness"
        echo "  service-status - Show systemd service status"
        echo "  service-logs   - Show recent service logs"
        echo "  service-start  - Start the systemd service"
        echo "  service-stop   - Stop the systemd service"
        echo "  service-restart- Restart the systemd service"
        echo "  install-deps   - Install/update Python dependencies"
        echo "  clean          - Clean Python cache files"
        echo "  help           - Show this help message"
        echo
        echo "Examples:"
        echo "  $0 test                    # Test the app directly"
        echo "  $0 check-displays          # Check display setup"
        echo "  $0 service-status          # Check if service is running"
        echo "  $0 service-logs            # View recent logs"
        ;;
esac

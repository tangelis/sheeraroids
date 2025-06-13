#!/bin/bash
echo "Building Sheeraroids for macOS..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Build with PyInstaller
echo "Building executable with PyInstaller..."
pyinstaller --name Sheeraroids --windowed --onefile \
    --add-data "assets:assets" \
    --icon=assets/GS1.png \
    --clean \
    linux_asteroids.py

echo "Build complete! Executable is in the dist folder."
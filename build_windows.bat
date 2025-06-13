@echo off
echo Building Sheeraroids for Windows...

rem Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

rem Activate virtual environment
call venv\Scripts\activate.bat

rem Install requirements
echo Installing requirements...
pip install -r requirements.txt

rem Build with PyInstaller
echo Building executable with PyInstaller...
pyinstaller --name Sheeraroids --windowed --onefile ^
    --add-data "assets;assets" ^
    --icon=assets\GS1.png ^
    --clean ^
    linux_asteroids.py

echo Build complete! Executable is in the dist folder.
pause
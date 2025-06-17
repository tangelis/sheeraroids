@echo off
echo Installing cx_Freeze if not already installed...
pip install cx_Freeze

echo Building executable...
python setup.py build

echo Done! Executable created in the build directory.
pause
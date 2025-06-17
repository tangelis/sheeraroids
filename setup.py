import sys
from cx_Freeze import setup, Executable

# Dependencies
build_exe_options = {
    "packages": ["pygame", "numpy"],
    "include_files": [
        "assets/",  # Include all game assets
        "constants.py",
        "game.py",
        "ui.py",
        "sprites.py",
        "effects.py",
        "audio.py",
        "screens.py",
        "highscores.py",
        "utils.py"
    ],
    "excludes": ["tkinter", "unittest"],
    "optimize": 2,
}

# Base for the executable
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Use this to hide console window on Windows

setup(
    name="Sheera vs Iguanas",
    version="1.0.0",
    description="A game where Sheera uses sound waves to defend against Iguanas",
    author="Sheera Fan",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "main.py",
            base=base,
            target_name="SheeraVsIguanas.exe",
            icon="assets/iguana.png",  # You can create and use a proper .ico file here
        )
    ],
)
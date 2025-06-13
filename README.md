# Sheeraroids

A game where Sheera uses sound waves to defend against Iguanas.

## Controls

- Arrow keys: Move and rotate
- Space: Shoot sound waves
- S: Activate shield
- P: Pause game
- M: Toggle background music (internet radio stream)
- ESC: Exit game
- ENTER: Restart game (when game over)

## Building Executables

### Windows

1. Make sure you have Python installed
2. Run `build_windows.bat`
3. Find the executable in the `dist` folder

### macOS

1. Make sure you have Python installed
2. Run `chmod +x build_macos.sh` to make the script executable
3. Run `./build_macos.sh`
4. Find the application in the `dist` folder

### Manual Build

You can also build manually using PyInstaller:

```
pip install -r requirements.txt
pyinstaller sheeraroids.spec
```

## Features

- Asteroid-style gameplay with Sheera vs Iguanas theme
- Sound wave shooting mechanics
- Shield system
- Heat management for rapid firing
- Background music streaming from internet radio
- Particle effects and explosions
- Progressive difficulty

## Dependencies

- pygame
- numpy
- requests (for internet radio streaming)
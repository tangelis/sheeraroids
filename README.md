# 🐕 SHEERAROIDS - German Shepherd vs Iguanas! 🦎

## The Epic Battle of Bark vs Lizard!

https://github.com/user-attachments/assets/00788496-fc11-4803-9ad3-8ff6b046015c


## 🎮 What is this madness?

Ever wondered what would happen if a sound-blasting German Shepherd named Sheera took on an army of invading iguanas? **Sheeraroids** is an exciting twist on the classic Asteroids game where you control Sheera, a heroic German Shepherd with the ability to emit devastating sound waves to defend against the iguana invasion!

## 🚀 Features

### Dual Game Modes
- 🏃‍♂️ **Accelerated Mode**: Everything moves faster for intense action
- 🐌 **Slowed Mode**: Relaxed gameplay for strategic planning

### Epic Visual Effects
- 💥 **Spectacular Explosions**: Watch enemies shatter into speed-based fragments
- 🎆 **80s-Style Game Over**: Retro neon graphics with scrolling high scores
- 🌟 **Particle Effects**: Beautiful firework explosions and visual trails
- 🎯 **Dynamic Fragment Scaling**: Fast fragments grow dramatically (up to 4x size)

### Advanced Gameplay
- 🐕 Control Sheera with fine-tuned movement (3x tighter turning)
- 🔊 Shoot powerful sound waves (spacebar for rapid fire)
- 🛡️ Dynamic shield system with reflection mechanics
- 🔥 Heat buildup system with visual glow effects
- 🎯 Smart collision detection and enemy splitting
- 📊 Complete high score system with 3-character initial entry
- 🧩 Math riddle challenge to continue after high scores
- 💥 Epic two-burst final death explosion sequence

### Audio Experience
- 🎵 Procedurally generated 80s-style music for every screen
- 💥 Multiple explosion sounds with unique player death effects
- 🔊 Bark shooting sounds with volume control
- 🎼 Complete sound design: typing beeps, transition sweeps, victory fanfares
- 🎹 Looping background music for all end screens

## 🎯 How to Play

### Controls
- **Move**: Arrow keys (↑ ← →)
- **Shoot**: Spacebar (hold for rapid fire)
- **Shield**: S key (hold to activate shield)
- **Pause**: P
- **Quit**: ESC

### Game Modes
1. **Choose Your Mode**: Select Accelerated or Slowed gameplay at startup
2. **Battle Iguanas**: Shoot sound waves to destroy iguana enemies
3. **Watch Fragments**: Enjoy speed-based fragment scaling - faster pieces get larger!
4. **Survive**: Avoid collisions and clear all enemies to advance levels
5. **Set Records**: Enter your initials when you achieve a high score

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.6+ (for running from source)
- Virtual environment (required on modern macOS)

### Windows Executable
```
# Download the latest release ZIP file
# Extract the ZIP file to any location
# Run SheeraVsIguanas.exe to play
```

### Quick Start (From Source)
```bash
# Clone this repository
git clone https://github.com/your-repo/sheeraroids.git

# Navigate to the game directory
cd sheeraroids

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py
```

### Alternative Installation
```bash
# Install dependencies manually
pip install pygame numpy

# Run directly
python main.py
```

### Building the Windows Executable
```bash
# Install cx_Freeze
pip install cx_Freeze

# Build the executable
python setup.py build

# The executable will be in the build/exe.win-amd64-x.x/ directory
# (where x.x is your Python version)
```

## 🏗️ Project Structure

The game is built with a clean, modular architecture:

```
sheeraroids/
├── main.py              # Main entry point (39 lines)
├── game.py              # Core game logic (530 lines)
├── sprites.py           # Player, enemies, projectiles (400 lines)
├── effects.py           # Visual effects & explosions (320 lines)
├── audio.py             # Sound generation & loading (680 lines)
├── screens.py           # Game over, high scores, riddle screens (660 lines)
├── ui.py                # UI components & mode selection (196 lines)
├── highscores.py        # Score management (280 lines)
├── utils.py             # Asset loading utilities (64 lines)
├── constants.py         # Game constants (25 lines)
├── setup.py             # cx_Freeze build configuration
├── build_exe.bat        # Windows executable build script
├── requirements.txt     # Dependencies
├── CLAUDE.md            # Developer documentation
└── assets/              # Game assets (images, sounds)
```

**All files are under 800 lines** - perfectly modular and maintainable!

## 🎮 Game Features Deep Dive

### Speed-Based Fragment Scaling
- Explosion fragments scale based on their velocity (1x to 4x size)
- Middle speed fragments (50% velocity) = 2.5x size
- Maximum speed fragments (100% velocity) = 4x size  
- Fixed dramatic scaling system for consistent visual impact
- Creates spectacular visual feedback without UI complexity

### 80s Retro Experience
- Neon color palette with pulsing effects
- Geometric shapes and digital rain transitions
- Procedurally generated synth music
- Scrolling high score display with retro fonts

### Advanced Physics
- Realistic momentum and friction
- Collision detection with proper splitting mechanics
- Heat buildup system affecting weapon performance
- Shield reflection with particle effects

## 🧠 Pro Tips

- **Fragment Scaling**: Enjoy the automatic speed-based scaling - faster fragments grow bigger!
- **Mode Selection**: Try both Accelerated and Slowed modes for different experiences  
- **Heat Management**: Watch Sheera's heat buildup - rapid firing creates visual glow
- **Strategic Shooting**: Target larger iguanas first as they split into smaller, faster enemies
- **Shield Tactics**: Hold S to activate shields that can reflect bullets back at enemies. Shield strength recharges when not in use
- **High Scores**: After game over, watch the scrolling high scores
- **Riddle Challenge**: Answer "seven" or "7" to continue playing
- **Controls**: Only ENTER key works on final screens for clean user experience
- **Final Death**: Enjoy the epic two-burst explosion with particle effects

## 🔧 Development

### For Developers
- See `CLAUDE.md` for detailed architecture documentation
- All code follows the 800-line-per-file limit
- Modular design makes features easy to modify
- Clean separation of concerns between modules

### Testing
```bash
# Activate virtual environment
source venv/bin/activate

# Test imports
python -c "import main; print('All imports successful')"

# Run the game
python main.py
```

## 🙏 Credits

- **Sheera**: The brave German Shepherd protagonist
- **Pygame Community**: For the excellent game framework
- **NumPy**: For procedural audio generation
- **80s Aesthetic**: Inspired by classic arcade games
- **Original Asteroids**: The timeless gameplay foundation

## 📜 License

This game is released under the MIT License - feel free to modify and share!

## 🐛 Troubleshooting

### Common Issues
1. **"No module named pygame"**: Ensure virtual environment is activated
2. **Audio not working**: Check numpy installation for procedural sounds
3. **Missing images**: Game will auto-generate placeholder images if assets are missing
4. **Performance issues**: Fragment scaling is automatic (no slider needed)

### System Requirements
- **macOS**: Requires virtual environment due to PEP 668
- **Windows/Linux**: Virtual environment recommended but not required
- **Memory**: Minimal - game uses efficient sprite management
- **Graphics**: Any system capable of running pygame

---

*"In the battle between bark and lizard, may the best species win!"* 🐕⚔️🦎

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

### Audio Experience
- 🎵 Procedurally generated 80s-style music and sound effects
- 💥 Custom explosion sounds using numpy synthesis
- 🔊 Bark shooting sounds with volume control

## 🎯 How to Play

### Controls
- **Move**: Arrow keys (↑ ← →)
- **Shoot**: Spacebar (hold for rapid fire)
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
- Python 3.6+
- Virtual environment (required on modern macOS)

### Quick Start
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

## 🏗️ Project Structure

The game is built with a clean, modular architecture:

```
sheeraroids/
├── main.py              # Main entry point (39 lines)
├── game.py              # Core game logic (458 lines)
├── sprites.py           # Player, enemies, projectiles (367 lines)
├── effects.py           # Visual effects & explosions (219 lines)
├── audio.py             # Sound generation & loading (230 lines)
├── screens.py           # 80s game over screen (200 lines)
├── ui.py                # UI components & mode selection (184 lines)
├── highscores.py        # Score management (121 lines)
├── utils.py             # Asset loading utilities (64 lines)
├── constants.py         # Game constants (25 lines)
├── requirements.txt     # Dependencies
├── CLAUDE.md           # Developer documentation
└── assets/             # Game assets (images, sounds)
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
- **Shield Tactics**: Shields can reflect bullets back at enemies
- **High Scores**: After 2 seconds on the game over screen, you'll auto-enter initials
- **Controls**: Only ENTER key works on final screens for clean user experience

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
4. **Performance issues**: Try adjusting the fragment scaling slider

### System Requirements
- **macOS**: Requires virtual environment due to PEP 668
- **Windows/Linux**: Virtual environment recommended but not required
- **Memory**: Minimal - game uses efficient sprite management
- **Graphics**: Any system capable of running pygame

---

*"In the battle between bark and lizard, may the best species win!"* 🐕⚔️🦎

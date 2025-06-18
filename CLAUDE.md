# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Sheeraroids** is a complete Python/pygame arcade game where a German Shepherd named Sheera battles iguana enemies. The game features dual gameplay modes, spectacular visual effects, 80s-style aesthetics, advanced physics with automatic speed-based fragment scaling, and a complete high score system with local file persistence.

## Architecture - Modular Design

The codebase is organized into **10 modular files**, each under 800 lines, following clean separation of concerns:

### Core Files Structure
```
main.py              (39 lines)   - Entry point and main game loop
game.py              (530 lines)  - Core Game class with main logic
sprites.py           (400 lines)  - All sprite classes (Player, Enemies, Projectiles)
effects.py           (320 lines)  - Visual effects and explosion systems
audio.py             (680 lines)  - Sound generation and audio loading
screens.py           (660 lines)  - 80s retro game over screen, high scores, riddle
ui.py                (196 lines)  - UI components and mode selection
highscores.py        (280 lines)  - High score management system
utils.py             (64 lines)   - Asset loading and utility functions
constants.py         (25 lines)   - Game constants and pygame init
setup.py             (21 lines)   - Package setup configuration
```

**Total modular code: ~3,215 lines** (was previously 2,006 lines in single file)

## Development Commands

### Setup and Running
```bash
# Create virtual environment (required on modern macOS due to PEP 668)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (use pip3 on macOS/Linux)
pip3 install -r requirements.txt
# OR manually: pip3 install pygame numpy

# Run the game
python main.py
```

### Building Executable (NEW)
```bash
# Windows users can use the batch file
build_exe.bat

# OR manually install cx_Freeze and build
pip install cx_Freeze
python setup.py build

# Executable will be created in build/ directory
```

### Development Tasks
```bash
# Test imports work correctly
python -c "import main; print('All imports successful')"

# Check line counts of all files
wc -l *.py | sort -nr

# Run from specific module (if needed)
python -m main
```

### Code Quality
- **No test suite exists** - Consider adding pytest if tests are needed
- **No linting configuration** - Consider adding ruff or flake8 if code quality checks are needed
- **No build process** - The game runs directly from source
- **800-line limit enforced** - All files must stay under 800 lines

## Detailed Module Documentation

### main.py (Entry Point)
- Contains main game loop and mode selection flow
- Handles game restart logic
- Minimal file - just coordinates other modules

### game.py (Core Logic)
**Key Classes:**
- `Game`: Main game controller with state management
- Game states: "playing", "death_pause", "game_over_80s", "entering_initials", "showing_high_scores", "correct_animation"
- Handles collision detection, scoring, and level progression
- Manages sprite groups and game physics
- Updates explosions and particles during death pause for proper animation

### sprites.py (Game Entities)
**Key Classes:**
- `Sheera`: Player character (German Shepherd) with mode-based sprites
- `Asteroid`: Iguana enemies with splitting mechanics
- `SoundWave`: Player projectiles with pulse effects
- `FireworkParticle`: Explosion particles
- `MotionTrail`: Visual trails for movement

### effects.py (Visual Effects)
**Key Classes:**
- `ImageFragment`: Speed-based scaling fragments for explosions
- `PlayerExplosion`: Spectacular player death explosion with shockwave
- `Explosion`: Traditional particle explosions with visible rings
- `FinalDeathExplosion`: Two-burst particle explosion for epic final death

### audio.py (Sound System)
**Functions:**
- `create_explosion_sound()`: Sharp, punchy first explosion (0.3s)
- `create_explosion_sound_2()`: Deeper, bigger second explosion (0.5s)
- `create_player_death_sound()`: Unique sound for non-final deaths (0.8s)
- `create_particle_shrinking_sound()`: 3-second particle fade effect
- `create_final_death_sound_80s()`: Short explosive death blast (0.5s)
- `create_80s_death_sound()`: Retro-style death sound
- `create_80s_transition_music()`: 5-second transition music
- `create_game_over_music()`: Dramatic game over screen music
- `create_typing_sound()`: 80s computer beep for initial entry
- `create_high_scores_music()`: Upbeat music for high scores screen
- `create_transition_sweep()`: Screen transition sound effect
- `create_victory_fanfare()`: Triumphant sound for riddle completion
- `create_wrong_answer_sound()`: Buzzer for incorrect riddle answers
- **NEW** `create_shield_bounce_sound()`: High-frequency ping for shield deflections (0.2s)
- `load_all_sounds()`: Sound loading coordination (now returns 15 sounds)

### screens.py (Visual Screens)
**Key Classes:**
- `RetroGameOverScreen`: 80s-style game over with neon effects
- `ModernHighScoresScreen`: Scrolling high scores with riddle challenge
- `CorrectAnswerAnimation`: Victory animation after solving riddle
- Features: scrolling high scores, geometric shapes, starfield background, math riddle

### ui.py (User Interface)
**Key Classes:**
- `show_mode_selection()`: Mode selection screen function with dual game mode options
- Clean, simple UI design focused on core gameplay

### highscores.py (Score Management)
**Key Classes:**
- `HighScoreManager`: Local JSON file storage with 20 default scores (1000-50)
- `HighScoreEntry`: 3-character initial entry with modern UI and cursor
- Auto-saves to `high_scores.json` in game directory immediately after entry
- Supabase-ready structure with timestamps and device IDs

### utils.py (Utilities)
**Functions:**
- `load_image()`: Image loading with fallbacks
- `create_placeholder_image()`: Asset generation for missing files
- `load_game_assets()`: Centralized asset loading

### constants.py (Configuration)
- Game constants: WIDTH, HEIGHT, FPS, colors
- Pygame initialization
- Screen and clock setup

## Game Features

### Dual Gameplay Modes
- **Accelerated**: 1.5x speed multiplier for all elements
- **Slowed**: 0.5x speed multiplier for relaxed gameplay
- Mode affects player movement, enemy speed, and projectile velocity

### Advanced Visual Effects
- **Speed-Based Fragment Scaling**: Automatic scaling from 1x to 4x based on fragment velocity
- **Fixed Dramatic Scaling**: Middle speed = 2.5x size, maximum speed = 4x size
- **80s Aesthetic**: Neon colors, geometric shapes, digital rain effects, scrolling starfields
- **Particle Systems**: Fireworks, trails, shockwave effects, and reflection particles
- **Player Death Effects**: Immediate sprite hiding, 80s death sound, direct transition to retro screen
- **Enhanced Shield Effects**: Multi-layer pulsating shield with color-coded strength indicator

### Physics Engine
- Realistic momentum and friction
- Collision detection with proper sprite splitting
- Heat buildup system affecting weapon performance
- **NEW Shield Mechanics**: 
  - Shields deflect asteroids with bounce physics
  - Asteroids split into 3 pieces on shield impact
  - Shield strength depletes on hits and active use
  - Auto-recharge when shield is inactive

### Executable Build System (NEW)
- **cx_Freeze Integration**: Create standalone Windows executables
- **build_exe.bat**: One-click build script for Windows
- **Asset Bundling**: All game assets included in executable
- **No Console Window**: Clean GUI experience on Windows

### Audio Experience
- Procedurally generated sounds using numpy
- 80s-style synthesized music and effects
- Volume-controlled sound layers

## Asset Management

### Directory Structure
```
assets/
├── GS1.png                              # German Shepherd sprite
├── iguana2.png                          # Iguana enemy sprite
├── ChatGPT Image Jun 12, 2025...png     # Accelerated mode sprite
├── Generated Image June 12, 2025...png  # Slowed mode sprite
├── bark_shoot_converted.wav             # Shooting sound
└── [auto-generated placeholders]        # Created if missing
```

### Fallback System
- Automatic placeholder generation for missing assets
- Procedural sound generation if audio files missing
- Game continues to work even with no asset files

## Development Guidelines

### Code Organization Principles
1. **Single Responsibility**: Each module has one clear purpose
2. **800-Line Limit**: Enforced on all files for maintainability
3. **Clean Dependencies**: Minimal imports between modules
4. **Separation of Concerns**: Game logic, rendering, audio, and UI are separated

### When Adding Features
1. Identify which module the feature belongs to
2. Ensure the module won't exceed 800 lines
3. If it would exceed, consider creating a new module
4. Update this CLAUDE.md file with changes

### Import Dependencies
```python
# Core modules depend on constants
from constants import WIDTH, HEIGHT, WHITE, BLACK, screen, clock

# Game uses sprites, effects, ui, audio
from sprites import Sheera, Asteroid, SoundWave
from effects import PlayerExplosion, Explosion
from ui import show_mode_selection  # Note: SpeedScaleSlider was removed
from audio import load_all_sounds

# Clean dependency chain prevents circular imports
```

## Performance Considerations

- **Sprite Groups**: Efficient collision detection using pygame groups
- **Fragment Management**: Automatic cleanup of off-screen fragments
- **Audio Generation**: Cached procedural sounds to avoid regeneration
- **Asset Loading**: One-time loading with fallback placeholders

## Future Integration Notes

- **Supabase Integration**: HighScoreManager prepared for database connection
- **Additional Modes**: Easy to add new game modes via mode selection
- **New Effects**: Effects system designed for easy expansion
- **Sound Packs**: Audio system supports both files and procedural generation

## Critical Implementation Details

### Game State Management
- States: "playing" → "death_pause" → "game_over_80s" → "showing_high_scores" → "correct_animation" → restart
- **Death Pause**: Allows explosions to animate before transitioning
- **High Scores Flow**: Always shows scrolling high scores after game over
- **Riddle System**: Must answer "seven" or "7" to "What is the sum of three and four?"
- **IMPORTANT**: Only ENTER key works on end screens (all other keys ignored)
- Auto-transition from game over to high scores after 2 seconds (120 frames at 60fps)
- Player sprite hidden after 10 frames to show explosion first

### Controls and User Experience
- **Rotation Speed**: Set to 1.5 for fine movement control ("like a clock, resolution down to the second")
- **Lives System**: Player has 3 lives with proper respawn mechanics
- **Heat Management**: Visual glow effects when rapid firing
- **Shield System**: 
  - **NEW: Shield vs Asteroids**: Shield now deflects asteroids, splitting them and bouncing them away
  - **Shield Controls**: Press and hold 'S' key to activate shield
  - **Shield Strength**: Starts at 50%, depletes when active or hit, recharges when inactive
  - **Visual Feedback**: Enhanced multi-layer shield with pulsating effect and color-coded strength
  - **Shield Bar**: Visual indicator with color-coded health (cyan→blue→purple)
  - **Shield Bounce**: Asteroids split into 3 pieces when hitting shield, even size 1 asteroids

### Fragment Scaling System
- **Velocity Range**: 1-15 for dramatic scaling differences
- **Scale Formula**: `base_scale_multiplier = 1.0 + (normalized_speed * 3.0)`
- **NO SLIDER**: Fixed scaling system only - slider was removed as "did not work at all"
- **Permanent Scaling**: Fragments maintain their speed-based size throughout lifetime

### Audio System
- **Final Death Sequence**: 
  - Immediate: First explosion sound (0.3s)
  - 333ms: Second explosion sound (0.5s)
  - 500ms: Particle shrinking sound (3s)
- **Screen Music**:
  - Game Over: Dramatic minor chord progression
  - High Scores: Upbeat 80s synth with fast bass
  - Victory: Triumphant fanfare
- **Sound Effects**:
  - Player death: Descending sweep with warble
  - Wrong answer: Harsh buzzer
  - Typing: 880Hz beep
  - Transitions: Frequency sweep
  - **NEW Shield bounce**: High-frequency ping with harmonics (1200Hz base)
- Procedural generation using numpy synthesis
- All music loops continuously until screen change
- Shield bounce sound at 60% volume for balance

### File Persistence
- High scores save to `high_scores.json` in game directory
- Automatic saving immediately after initial entry
- JSON format: `[{"initials": "ABC", "score": 12345}, ...]`

## Important Notes

- **Virtual Environment Required**: macOS requires venv due to PEP 668
- **Python 3.6+ Required**: Uses f-strings and modern pygame features
- **Pygame 2.1.0+ Required**: For advanced sprite and audio features
- **NumPy Dependency**: Required for procedural audio generation
- **cx_Freeze Optional**: Only needed for building standalone executables
- **pip3 vs pip**: Use `pip3` on macOS/Linux systems to ensure Python 3 compatibility
- **All Files Under 800 Lines**: Maintain this limit when making changes
- **Speed Slider Removed**: Previous debug slider system was completely removed
- **Shield Controls**: Press 'S' key to activate shield (hint shown on screen)

## Testing the Refactored Code

```bash
# 1. Verify line counts
wc -l *.py | grep -v "total"

# 2. Test imports
python -c "import main; print('Success')"

# 3. Run the game
source venv/bin/activate
python main.py

# 4. Verify all features work:
#    - Mode selection screen appears
#    - Both game modes work (accelerated/slowed)
#    - Automatic fragment scaling based on speed (no slider)
#    - Explosions show dramatic speed-based scaling (1x to 4x)
#    - Player disappears immediately on death
#    - 80s game over screen displays with 2-second timer
#    - High score entry works with arrow keys
#    - Only ENTER key advances final screens
#    - Scores save to high_scores.json locally
#    - NEW: Shield activates with 'S' key
#    - NEW: Shield deflects asteroids and splits them
#    - NEW: Shield strength bar shows color-coded health
#    - NEW: Shield bounce sound plays on asteroid deflection

# 5. Build executable (Windows):
build_exe.bat
```

## Session History & Key Learnings

### Major Development Session (User Feedback & Iterations)

This section documents critical user feedback and implementation decisions that future Claude instances must understand:

#### User Preferences & Requirements
1. **Movement Controls**: "I want resolution down to the second" - User wanted SLOWER, finer movement control, not faster. Rotation speed reduced to 1.5 (from initial incorrect increase to 15).

2. **Visual Effects**: User wanted dramatic, immediately visible effects:
   - Fragment scaling was "barely noticeable" initially
   - Required velocity range expansion (1-15) and permanent scaling
   - Final system: 1x to 4x scaling with middle speed = 2.5x, max speed = 4x

3. **User Experience**: User values clean, simple interactions:
   - "Only ENTER will move it to another screen" - strict control requirements
   - Removed all transition animations that felt "weird" 
   - 2-second auto-timer for initials entry
   - Direct transitions without unnecessary delays

4. **Failed Features**: User explicitly rejected features that "did not work at all":
   - **Speed slider removal**: "Can you remove the speed scale from the side. That did not work at all."
   - User prefers fixed, automatic systems over manual controls

#### Critical Implementation Fixes

1. **Player Death Sequence**:
   - Player sprite must disappear immediately: `player.hidden = True`
   - Direct transition to 80s screen (no animation)
   - 80s death sound plays on explosion
   - Lives system must work for all 3 lives

2. **Game State Logic**:
   - Fixed ordering issue where 80s sequence wasn't appearing
   - Proper state transitions: playing → game_over_80s → entering_initials
   - Timer-based auto-progression (120 frames = 2 seconds)

3. **Fragment Scaling System**:
   - **Removed SpeedScaleSlider completely** - all references eliminated
   - Fixed scaling formula for consistent dramatic effect
   - Velocity range: 1-15 for maximum visual differentiation
   - Permanent scaling throughout fragment lifetime

4. **Controls & Navigation**:
   - Only ENTER key responds on final screens
   - Arrow keys for initial entry navigation
   - No other keys work to prevent accidental advancement

#### Code Architecture Decisions

1. **800-Line Limit Enforcement**:
   - User requirement: "I don't want any document with more than 800 lines of code"
   - Successfully refactored 2006-line monolith into 10 modular files
   - All files verified under 800 lines

2. **Modular Design Benefits**:
   - Clean separation allowed easy feature removal (slider)
   - Independent testing of components
   - Maintainable codebase for future development

3. **Local File Persistence**:
   - High scores save to `high_scores.json` in game directory
   - Immediate saving on initial entry completion
   - Supabase integration prepared but not implemented

### Testing & Validation

The game has been thoroughly tested with:
- ✅ Virtual environment setup on macOS
- ✅ All imports working correctly
- ✅ Both game modes functional
- ✅ Fragment scaling system working without slider
- ✅ 80s game over sequence with proper timing
- ✅ High score system with local file persistence
- ✅ ENTER-only controls on end screens
- ✅ Player death effects and respawn system
- ✅ Epic final death with two-burst explosions
- ✅ Full sound design for all screens and transitions
- ✅ High scores scrolling with riddle challenge

### Future Development Guidelines

1. **Always test user feedback carefully** - initial implementations may miss the mark
2. **Prefer automatic systems over manual controls** - user rejected slider in favor of fixed scaling
3. **Keep interactions simple and clean** - only essential keys should work
4. **Maintain 800-line limit** - critical for maintainability
5. **Document ALL changes** - this session history is essential for continuity

## Additional Project Context

### Web Version
- The repository also contains an HTML5/JavaScript version in the `web/` directory
- Web version mirrors the core gameplay of the Python version
- Deployed for browser-based play

### Project Status
- **License**: MIT License
- **Active Development**: Modular refactor completed, all features functional, shield mechanics enhanced
- **Code Quality**: ✅ All files under 800 lines | ✅ Modular architecture | ✅ Clean dependencies | ✅ Speed slider removed | ✅ Fixed dramatic scaling | ✅ Local high score persistence | ✅ Complete sound design | ✅ Epic final death sequence | ✅ Enhanced shield system | ✅ Executable build support
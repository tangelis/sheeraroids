# CLAUDE.md

This file provides comprehensive guidance to Claude Code instances when working with the Sheeraroids game repository.

## Project Overview

**Sheeraroids** is a complete Python/pygame arcade game where a German Shepherd named Sheera battles iguana enemies. The game features dual gameplay modes, spectacular visual effects, 80s-style aesthetics, advanced physics with automatic speed-based fragment scaling, and a complete high score system with local file persistence.

## Architecture - Modular Design

The codebase is organized into **10 modular files**, each under 800 lines, following clean separation of concerns:

### Core Files Structure
```
main.py              (39 lines)   - Entry point and main game loop
game.py              (458 lines)  - Core Game class with main logic
sprites.py           (367 lines)  - All sprite classes (Player, Enemies, Projectiles)
effects.py           (219 lines)  - Visual effects and explosion systems
audio.py             (230 lines)  - Sound generation and audio loading
screens.py           (200 lines)  - 80s retro game over screen
ui.py                (184 lines)  - UI components and mode selection
highscores.py        (121 lines)  - High score management system
utils.py             (64 lines)   - Asset loading and utility functions
constants.py         (25 lines)   - Game constants and pygame init
```

**Total modular code: 1,928 lines** (was previously 2,006 lines in single file)

## Development Commands

### Setup and Running
```bash
# Create virtual environment (required on modern macOS due to PEP 668)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
# OR manually: pip install pygame numpy

# Run the game
python main.py
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
- Game states: "playing", "transition", "game_over_80s", "entering_initials"
- Handles collision detection, scoring, and level progression
- Manages sprite groups and game physics

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
- `Explosion`: Traditional particle explosions

### audio.py (Sound System)
**Functions:**
- `create_explosion_sound()`: Procedural explosion effects
- `create_80s_death_sound()`: Retro-style death sound
- `create_80s_transition_music()`: 5-second transition music
- `load_all_sounds()`: Sound loading coordination

### screens.py (Visual Screens)
**Key Classes:**
- `RetroGameOverScreen`: 80s-style game over with neon effects
- Features: scrolling high scores, geometric shapes, starfield background

### ui.py (User Interface)
**Key Classes:**
- `show_mode_selection()`: Mode selection screen function with dual game mode options
- Clean, simple UI design focused on core gameplay

### highscores.py (Score Management)
**Key Classes:**
- `HighScoreManager`: Local JSON file storage and management with Supabase preparation
- `HighScoreEntry`: 3-character initial entry with arrow key navigation
- Auto-saves to `high_scores.json` in game directory immediately after entry

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

### Physics Engine
- Realistic momentum and friction
- Collision detection with proper sprite splitting
- Heat buildup system affecting weapon performance
- Shield reflection mechanics

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
from ui import SpeedScaleSlider, show_mode_selection
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
- States: "playing" → "game_over_80s" → "entering_initials" → restart
- **IMPORTANT**: Only ENTER key works on end screens (all other keys ignored)
- Auto-transition to initials entry after 2 seconds (120 frames at 60fps)
- Player sprite must be hidden immediately on death: `player.hidden = True`

### Controls and User Experience
- **Rotation Speed**: Set to 1.5 for fine movement control ("like a clock, resolution down to the second")
- **Lives System**: Player has 3 lives with proper respawn mechanics
- **Heat Management**: Visual glow effects when rapid firing
- **Shield System**: Reflects projectiles with particle effects

### Fragment Scaling System
- **Velocity Range**: 1-15 for dramatic scaling differences
- **Scale Formula**: `base_scale_multiplier = 1.0 + (normalized_speed * 3.0)`
- **NO SLIDER**: Fixed scaling system only - slider was removed as "did not work at all"
- **Permanent Scaling**: Fragments maintain their speed-based size throughout lifetime

### Audio System
- Procedural 80s-style death sound using numpy synthesis
- Shooting sounds with volume control
- Background music during transitions

### File Persistence
- High scores save to `high_scores.json` in game directory
- Automatic saving immediately after initial entry
- JSON format: `[{"initials": "ABC", "score": 12345}, ...]`

## Important Notes

- **Virtual Environment Required**: macOS requires venv due to PEP 668
- **Python 3.6+ Required**: Uses f-strings and modern pygame features
- **Pygame 2.1.0+ Required**: For advanced sprite and audio features
- **NumPy Dependency**: Required for procedural audio generation
- **All Files Under 800 Lines**: Maintain this limit when making changes
- **Speed Slider Removed**: Previous debug slider system was completely removed

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

### Future Development Guidelines

1. **Always test user feedback carefully** - initial implementations may miss the mark
2. **Prefer automatic systems over manual controls** - user rejected slider in favor of fixed scaling
3. **Keep interactions simple and clean** - only essential keys should work
4. **Maintain 800-line limit** - critical for maintainability
5. **Document ALL changes** - this session history is essential for continuity

---

**Code Quality Status**: ✅ All files under 800 lines | ✅ Modular architecture | ✅ Clean dependencies | ✅ Speed slider removed | ✅ Fixed dramatic scaling | ✅ Local high score persistence
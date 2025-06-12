# Error Documentation

## Project: Sheeraroids
**Date Started:** January 6, 2025
**Environment:** macOS with zsh terminal

### Errors Encountered and Solutions

#### 1. Python Command Not Found
**Error:** `(eval):1: command not found: python`
**Context:** Attempted to run `python linux_asteroids.py`
**Solution:** Use `python3` instead of `python` on macOS systems
**Learning:** macOS typically has `python3` as the default Python command

#### 2. Pip Command Not Found  
**Error:** `(eval):1: command not found: pip`
**Context:** Attempted to install pygame with `pip install pygame`
**Solution:** Use `pip3` instead of `pip` on macOS systems
**Learning:** macOS uses `pip3` for Python 3 package management

#### 3. Externally Managed Environment
**Error:** `error: externally-managed-environment`
**Context:** Attempted to install pygame system-wide with `pip3 install pygame`
**Solution:** Create a virtual environment first:
```bash
python3 -m venv venv
source venv/bin/activate
pip install pygame
```
**Learning:** Modern macOS/Homebrew Python installations require virtual environments to prevent system package conflicts (PEP 668)

#### 4. Missing numpy Module
**Error:** `ModuleNotFoundError: No module named 'numpy'`
**Context:** Attempted to use numpy for sound generation in pygame without installing it first
**Solution:** Install numpy in the virtual environment: `pip install numpy`
**Learning:** Always check and install required dependencies when adding new imports

### Key Takeaways
- Always check Python version availability with `python3` first on macOS
- Use virtual environments for Python projects to avoid system conflicts
- macOS with Homebrew manages Python packages differently than other systems
- Install all required dependencies (including numpy) when adding new imports
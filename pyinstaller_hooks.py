"""
PyInstaller hooks for Sheeraroids game
This file helps PyInstaller correctly package all dependencies
"""

def get_pygame_hidden_imports():
    """Return a list of hidden pygame modules that PyInstaller might miss"""
    return [
        'pygame.mixer',
        'pygame.mixer_music',
        'pygame.font',
        'pygame.transform',
        'pygame.draw',
        'pygame.image',
        'pygame.math',
        'pygame.locals',
    ]

def get_audio_streamer_imports():
    """Return a list of imports needed for audio streaming"""
    return [
        'requests',
        'tempfile',
        'threading',
    ]
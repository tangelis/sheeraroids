"""
Utility functions for image loading and asset management
"""
import pygame
import os
import numpy as np
from constants import assets_dir, WIDTH, HEIGHT, BLACK, RED

def load_image(name, size=None, convert_alpha=True):
    """Load an image with optional scaling"""
    try:
        image = pygame.image.load(name)
        if convert_alpha:
            image = image.convert_alpha()
        else:
            image = image.convert()
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except pygame.error:
        print(f"Cannot load image: {name}")
        return pygame.Surface((30, 30))

def create_placeholder_image(filename, color, size):
    """Create a placeholder image if asset doesn't exist"""
    filepath = os.path.join(assets_dir, filename)
    if not os.path.exists(filepath):
        surface = pygame.Surface(size, pygame.SRCALPHA)
        surface.fill(color)
        pygame.image.save(surface, filepath)

def ensure_assets_directory():
    """Create assets directory if it doesn't exist"""
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)

def load_game_assets():
    """Load all game assets"""
    ensure_assets_directory()
    
    # Create placeholder images if they don't exist
    create_placeholder_image("ship.png", (255, 255, 255), (30, 30))
    create_placeholder_image("bullet.png", (255, 255, 0), (5, 10))
    create_placeholder_image("explosion.png", RED, (50, 50))

    # Load game assets
    ship_img = load_image(os.path.join(assets_dir, "GS1.png"), (120, 90))
    bullet_img = load_image(os.path.join(assets_dir, "bullet.png"))
    explosion_img = load_image(os.path.join(assets_dir, "explosion.png"))

    # Load iguana image and create different sizes
    iguana_original = load_image(os.path.join(assets_dir, "iguana2.png"))
    if iguana_original.get_width() == 30:  # Default surface when image not found
        # Create a placeholder iguana image if not found
        iguana_surface = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.polygon(iguana_surface, (0, 200, 0), [(10, 30), (50, 10), (50, 50)])
        iguana_original = iguana_surface

    asteroid_images = [
        pygame.transform.scale(iguana_original, (90, 90)),  # Large
        pygame.transform.scale(iguana_original, (70, 70)),  # Medium
        pygame.transform.scale(iguana_original, (50, 50))   # Small
    ]
    
    return ship_img, bullet_img, explosion_img, asteroid_images
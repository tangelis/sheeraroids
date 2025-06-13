"""
Game constants and configuration
"""
import pygame
import os

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Game constants
WIDTH, HEIGHT = 1024, 768
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sheera vs Iguanas")
clock = pygame.time.Clock()

# Assets directory
assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
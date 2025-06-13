import pygame
import os

def create_title_image(assets_dir, width=800, height=200):
    """Create a title image if one doesn't exist"""
    filepath = os.path.join(assets_dir, "SHEERAROIDS.png")
    
    # Check if file already exists
    if os.path.exists(filepath):
        return
    
    # Create a surface for the title
    title_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Create gradient background
    for y in range(height):
        # Calculate gradient color (blue to purple)
        r = int(100 + (y / height) * 155)
        g = int(50 + (y / height) * 50)
        b = int(200 - (y / height) * 50)
        
        # Draw horizontal line with this color
        pygame.draw.line(title_surface, (r, g, b), (0, y), (width, y))
    
    # Add text
    font_size = height // 2
    try:
        font = pygame.font.Font(None, font_size)
    except:
        # If default font fails, try system font
        font = pygame.font.SysFont("Arial", font_size)
    
    # Render text with outline
    text = "SHEERAROIDS"
    
    # Draw outline
    outline_size = font_size // 15
    outline_color = (255, 255, 0)  # Yellow outline
    text_color = (255, 255, 255)   # White text
    
    # Main text
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=(width//2, height//2))
    
    # Draw outline by offsetting the text in different directions
    for dx in [-outline_size, 0, outline_size]:
        for dy in [-outline_size, 0, outline_size]:
            if dx != 0 or dy != 0:  # Skip the center position
                outline_rect = text_rect.copy()
                outline_rect.x += dx
                outline_rect.y += dy
                outline_surf = font.render(text, True, outline_color)
                title_surface.blit(outline_surf, outline_rect)
    
    # Draw main text on top
    title_surface.blit(text_surface, text_rect)
    
    # Add some stars
    for _ in range(50):
        import random
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.randint(1, 3)
        brightness = random.randint(150, 255)
        pygame.draw.circle(title_surface, (brightness, brightness, brightness), (x, y), size)
    
    # Save the image
    pygame.image.save(title_surface, filepath)
    
    return filepath
import pygame
import math
import random
import os
from pygame.locals import *

class IntroAnimation:
    def __init__(self, screen, assets_dir, ship_img, asteroid_images):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.assets_dir = assets_dir
        self.ship_img = ship_img
        self.asteroid_images = asteroid_images
        self.done = False
        self.start_time = pygame.time.get_ticks()
        self.duration = 6000  # 6 seconds total
        
        # Load title image
        try:
            self.title_img = pygame.image.load(os.path.join(assets_dir, "SHEERAROIDS.png"))
            self.title_img = pygame.transform.scale(self.title_img, (int(self.width * 0.8), int(self.height * 0.3)))
        except:
            # Create a text title if image not available
            font = pygame.font.Font(None, 120)
            self.title_img = font.render("SHEERAROIDS", True, (255, 255, 255))
        
        self.title_rect = self.title_img.get_rect(center=(self.width // 2, self.height // 3))
        
        # Setup animation elements
        self.sheera = {
            'img': pygame.transform.scale(ship_img, (int(ship_img.get_width() * 1.5), int(ship_img.get_height() * 1.5))),
            'pos': [-100, self.height // 2],
            'angle': 0,
            'speed': 5
        }
        
        # Create iguanas
        self.iguanas = []
        for i in range(5):
            iguana = {
                'img': random.choice(asteroid_images),
                'pos': [self.width + random.randint(50, 300), random.randint(100, self.height - 100)],
                'speed': random.uniform(2, 4),
                'angle': random.randint(0, 360),
                'rotation_speed': random.uniform(-3, 3)
            }
            self.iguanas.append(iguana)
        
        # Firework particles
        self.particles = []
        
        # Press any key text
        self.font = pygame.font.Font(None, 36)
        self.press_key_text = self.font.render("Press Any Key to Start", True, (255, 255, 255))
        self.press_key_rect = self.press_key_text.get_rect(center=(self.width // 2, self.height * 0.8))
        self.blink_timer = 0
        self.show_text = True
        
    def create_firework(self, pos):
        colors = [
            (255, 0, 0),    # Red
            (255, 165, 0),  # Orange
            (255, 255, 0),  # Yellow
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (75, 0, 130),   # Indigo
            (148, 0, 211),  # Violet
            (255, 192, 203), # Pink
            (255, 255, 255), # White
            (255, 215, 0)    # Gold
        ]
        
        for _ in range(50):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 5)
            color = random.choice(colors)
            particle = {
                'pos': list(pos),
                'vel': [math.cos(angle) * speed, math.sin(angle) * speed],
                'color': color,
                'size': random.randint(2, 4),
                'lifetime': random.randint(30, 60),
                'alpha': 255
            }
            self.particles.append(particle)
    
    def update(self):
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time
        progress = min(1.0, elapsed / self.duration)
        
        # Update Sheera position
        if progress < 0.5:  # First half of animation
            self.sheera['pos'][0] += self.sheera['speed']
            if self.sheera['pos'][0] > self.width // 2:
                self.sheera['pos'][0] = self.width // 2
        
        # Update iguanas
        for iguana in self.iguanas:
            iguana['pos'][0] -= iguana['speed']
            iguana['angle'] = (iguana['angle'] + iguana['rotation_speed']) % 360
            
            # Reset iguana if it goes off screen
            if iguana['pos'][0] < -100:
                iguana['pos'][0] = self.width + random.randint(50, 300)
                iguana['pos'][1] = random.randint(100, self.height - 100)
        
        # Create random fireworks
        if random.random() < 0.03:  # 3% chance each frame
            self.create_firework([
                random.randint(100, self.width - 100),
                random.randint(100, self.height - 100)
            ])
        
        # Update particles
        for particle in self.particles[:]:
            particle['pos'][0] += particle['vel'][0]
            particle['pos'][1] += particle['vel'][1]
            particle['vel'][1] += 0.05  # Gravity
            particle['lifetime'] -= 1
            particle['alpha'] = int(255 * (particle['lifetime'] / 60))
            
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
        
        # Update blinking text
        self.blink_timer += 1
        if self.blink_timer >= 30:  # Toggle every 30 frames (0.5 seconds at 60 FPS)
            self.blink_timer = 0
            self.show_text = not self.show_text
        
        # Check for key press to end intro
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            elif event.type == KEYDOWN:
                self.done = True
                return True
        
        return True
    
    def draw(self):
        # Fill background
        self.screen.fill((0, 0, 0))
        
        # Draw particles
        for particle in self.particles:
            color_with_alpha = (*particle['color'], particle['alpha'])
            surf = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, color_with_alpha, (particle['size'], particle['size']), particle['size'])
            self.screen.blit(surf, (particle['pos'][0] - particle['size'], particle['pos'][1] - particle['size']))
        
        # Draw iguanas
        for iguana in self.iguanas:
            rotated = pygame.transform.rotate(iguana['img'], iguana['angle'])
            rect = rotated.get_rect(center=iguana['pos'])
            self.screen.blit(rotated, rect.topleft)
        
        # Draw Sheera
        rotated_sheera = pygame.transform.rotate(self.sheera['img'], self.sheera['angle'])
        sheera_rect = rotated_sheera.get_rect(center=self.sheera['pos'])
        self.screen.blit(rotated_sheera, sheera_rect.topleft)
        
        # Draw title with glow effect
        glow_colors = [
            (255, 0, 0, 50),    # Red
            (0, 255, 0, 50),    # Green
            (0, 0, 255, 50),    # Blue
        ]
        
        # Draw glow layers
        for i, color in enumerate(glow_colors):
            offset = math.sin(pygame.time.get_ticks() * 0.005 + i) * 3
            glow_rect = self.title_rect.copy()
            glow_rect.x += offset
            glow_rect.y += offset
            
            # Create a surface for the glow
            glow_surf = pygame.Surface((self.title_rect.width + 20, self.title_rect.height + 20), pygame.SRCALPHA)
            glow_rect_local = pygame.Rect(10, 10, self.title_rect.width, self.title_rect.height)
            pygame.draw.rect(glow_surf, color, glow_rect_local, border_radius=10)
            
            # Apply blur effect by scaling down and up
            scale_factor = 0.5
            small_surf = pygame.transform.scale(glow_surf, 
                                              (int(glow_surf.get_width() * scale_factor),
                                               int(glow_surf.get_height() * scale_factor)))
            blurred = pygame.transform.scale(small_surf, (glow_surf.get_width(), glow_surf.get_height()))
            
            # Blit the glow
            self.screen.blit(blurred, (glow_rect.x - 10, glow_rect.y - 10))
        
        # Draw title
        self.screen.blit(self.title_img, self.title_rect)
        
        # Draw "Press any key" text if it should be shown
        if self.show_text:
            self.screen.blit(self.press_key_text, self.press_key_rect)
        
        # Update display
        pygame.display.flip()
        
    def run(self):
        while not self.done:
            if not self.update():
                return False
            self.draw()
            pygame.time.Clock().tick(60)
        return True
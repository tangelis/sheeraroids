#!/usr/bin/env python3
"""
Sheera vs Iguanas
A game where Sheera uses sound waves to defend against Iguanas.
"""
import pygame
import sys
import math
import random
import os
import numpy as np
import json
from pygame.locals import *
from disintegration_effect import DisintegrationEffect
from intro_animation import IntroAnimation

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Game constants
#WIDTH, HEIGHT = 800, 600

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

# Load images
def load_image(name, size=None, convert_alpha=True):
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

# Create directory for assets if it doesn't exist
assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(assets_dir, exist_ok=True)

# Create placeholder images if they don't exist
def create_placeholder_image(filename, color, size):
    filepath = os.path.join(assets_dir, filename)
    if not os.path.exists(filepath):
        surface = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.circle(surface, color, (size[0]//2, size[1]//2), min(size)//2)
        pygame.image.save(surface, filepath)

# Create placeholder images
# No need for placeholder since we're using the actual image

def create_soundwave_placeholder():
    filepath = os.path.join(assets_dir, "bullet.png")
    if not os.path.exists(filepath):
        # Create a sound wave effect
        size = (15, 10)
        surface = pygame.Surface(size, pygame.SRCALPHA)
        # Draw sound wave lines
        wave_color = (0, 191, 255)  # Deep sky blue
        for i in range(3):
            y_pos = 5
            x_start = i * 5
            pygame.draw.line(surface, wave_color, (x_start, y_pos-3), (x_start, y_pos+3), 2)
        pygame.image.save(surface, filepath)

# Create custom game assets
create_soundwave_placeholder()
create_placeholder_image("explosion.png", RED, (50, 50))

# Create title image if needed
from assets.title_text import create_title_image
create_title_image(assets_dir, WIDTH, int(HEIGHT * 0.3))

# Load game assets
ship_img = load_image(os.path.join(assets_dir, "GS1.png"), (120, 90))  # Load German Shepherd head
bullet_img = load_image(os.path.join(assets_dir, "bullet.png"))
explosion_img = load_image(os.path.join(assets_dir, "explosion.png"))

# Load iguana image and create different sizes
iguana_original = load_image(os.path.join(assets_dir, "iguana2.png"))
if iguana_original.get_width() == 30:  # Default surface when image not found
    # Create a placeholder iguana image if not found
    iguana_surface = pygame.Surface((60, 60), pygame.SRCALPHA)
    pygame.draw.polygon(iguana_surface, (0, 200, 0), [(10, 30), (50, 10), (50, 50)])  # Simple triangle
    iguana_original = iguana_surface

asteroid_images = [
    pygame.transform.scale(iguana_original, (90, 90)),  # Large
    pygame.transform.scale(iguana_original, (70, 70)),  # Medium
    pygame.transform.scale(iguana_original, (50, 50))   # Small
]

# Load shooting sound
try:
    # Load the converted wav bark sound file
    shoot_sound = pygame.mixer.Sound(os.path.join(assets_dir, "bark_shoot_converted.wav"))
    shoot_sound.set_volume(0.5)  # Adjust volume to not be too loud
except:
    print("Could not load bark shoot converted.wav")
    shoot_sound = None

# Motion trail class
class MotionTrail(pygame.sprite.Sprite):
    def __init__(self, image, position, alpha=150):
        pygame.sprite.Sprite.__init__(self)
        self.image = image.copy()
        self.image.set_alpha(alpha)
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.lifetime = 15  # frames
        
    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
        else:
            # Fade out
            alpha = int((self.lifetime / 15) * 150)
            self.image.set_alpha(alpha)

# Game classes
class Sheera(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = ship_img  # Now using the sheera.jpg image
        self.original_image = self.image
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.position = pygame.math.Vector2(self.rect.center)
        self.velocity = pygame.math.Vector2(0, 0)
        self.angle = 0
        self.rotation_speed = 5
        self.acceleration = 0.2
        self.max_speed = 7
        self.friction = 0.98
        self.shoot_delay = 250  # Bark delay
        self.min_shoot_delay = 100  # Minimum delay between shots when fully charged
        self.fire_rate_boost = 0  # Increases as fire button is held
        self.max_fire_rate_boost = 150  # Maximum reduction in shoot delay
        self.last_shot = pygame.time.get_ticks()
        self.fire_button_held_time = 0  # Time fire button has been held
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.respawn_delay = 3000  # 3 seconds respawn delay
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.trail_timer = 0
        
        # Glow effect properties
        self.heat = 0
        self.max_heat = 100
        self.heat_increase = 20
        self.heat_cooldown = 1
        self.glow_colors = [
            (255, 255, 0),    # Yellow
            (255, 165, 0),    # Orange
            (255, 69, 0),     # Red-Orange
            (255, 0, 0)       # Red
        ]
        
        # Shield properties
        self.shield_active = False
        self.shield_strength = 0
        self.max_shield = 100
        self.shield_increase = 2
        self.shield_decrease = 5
        self.shield_colors = [
            (0, 100, 255),    # Light Blue
            (0, 50, 255),     # Medium Blue
            (0, 0, 255),      # Blue
            (75, 0, 130)      # Indigo
        ]

    def update(self):
        # Handle invulnerability
        if self.invulnerable:
            if pygame.time.get_ticks() - self.invulnerable_timer > 3000:
                self.invulnerable = False
        
        # Handle hidden state (after death)
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > self.respawn_delay and not game.game_over:
            self.hidden = False
            self.rect.center = (WIDTH // 2, HEIGHT // 2)
            self.position = pygame.math.Vector2(self.rect.center)
            self.velocity = pygame.math.Vector2(0, 0)
            self.invulnerable = True
            self.invulnerable_timer = pygame.time.get_ticks()
            
        # Create motion trail based on velocity
        now = pygame.time.get_ticks()
        if not self.hidden and self.velocity.length() > 1.0 and now - self.trail_timer > 50:
            self.trail_timer = now
            # Create a trail sprite at current position
            trail = MotionTrail(self.image, self.position)
            game.all_sprites.add(trail)
            game.trails.add(trail)
            
        # Update fire rate boost based on space key
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            # Increase fire rate boost while space is held
            self.fire_rate_boost = min(self.max_fire_rate_boost, 
                                      self.fire_rate_boost + 0.5)
        else:
            # Reset fire rate boost when space is released
            self.fire_rate_boost = 0

        # Get key presses
        keys = pygame.key.get_pressed()
        
        # Only process controls if not disabled in the game
        if not hasattr(game, 'controls_disabled') or not game.controls_disabled:
            # Rotation
            if keys[pygame.K_LEFT]:
                self.angle += self.rotation_speed
            if keys[pygame.K_RIGHT]:
                self.angle -= self.rotation_speed
                
            # Thrust
            if keys[pygame.K_UP]:
                # Calculate thrust vector based on 3 o'clock direction (90 degrees to the right)
                thrust_angle = self.angle - 90
                thrust_x = -math.sin(math.radians(thrust_angle)) * self.acceleration
                thrust_y = -math.cos(math.radians(thrust_angle)) * self.acceleration
                self.velocity += pygame.math.Vector2(thrust_x, thrust_y)
                
                # Limit speed
                if self.velocity.length() > self.max_speed:
                    self.velocity.scale_to_length(self.max_speed)
            
            # Shield control
            if keys[pygame.K_s]:
                # Increase shield strength while S is held
                self.shield_strength = min(self.max_shield, self.shield_strength + self.shield_increase)
                self.shield_active = self.shield_strength > 0
            else:
                # Decrease shield strength when S is released
                self.shield_strength = max(0, self.shield_strength - self.shield_decrease)
                self.shield_active = self.shield_strength > 0
        
        # Apply friction
        self.velocity *= self.friction
        
        # Update position
        self.position += self.velocity
        
        # Wrap around screen
        if self.position.x < 0:
            self.position.x = WIDTH
        if self.position.x > WIDTH:
            self.position.x = 0
        if self.position.y < 0:
            self.position.y = HEIGHT
        if self.position.y > HEIGHT:
            self.position.y = 0
            
        # Update rect position
        self.rect.center = self.position
        
        # Cool down heat
        self.heat = max(0, self.heat - self.heat_cooldown)
        
        # Rotate ship image
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        
        # Shield and glow effects are now handled in the Game.draw() method
    
    def shoot(self):
        now = pygame.time.get_ticks()
        # Calculate current shoot delay based on fire rate boost
        current_delay = max(self.min_shoot_delay, self.shoot_delay - self.fire_rate_boost)
        
        if now - self.last_shot > current_delay and not self.hidden:
            self.last_shot = now
            # Increase heat when shooting (dog barking heats up)
            self.heat = min(self.max_heat, self.heat + self.heat_increase)
            
            # Calculate position and direction at 3 o'clock (right side)
            # This is 90 degrees to the right of the current angle
            right_angle = self.angle - 90
            
            # Calculate shooting direction (3 o'clock direction)
            direction_x = -math.sin(math.radians(right_angle))
            direction_y = -math.cos(math.radians(right_angle))
            
            # Calculate spawn position at the right side of the head
            offset_x = direction_x * (self.rect.width * 0.5)
            offset_y = direction_y * (self.rect.height * 0.5)
            
            # Position sound wave at the right side of the German Shepherd head
            pos_x = self.position.x + offset_x
            pos_y = self.position.y + offset_y
            
            # Create a sound wave bullet shooting to the right
            return SoundWave(pos_x, pos_y, direction_x, direction_y)
        return None
        
    def draw_glow(self):
        # Calculate bark intensity parameters based on heat
        heat_percent = self.heat / self.max_heat
        glow_size = int(self.rect.width * (1 + heat_percent * 0.8))
        
        # Choose color based on bark intensity level
        color_index = min(len(self.glow_colors) - 1, int(heat_percent * len(self.glow_colors)))
        color = self.glow_colors[color_index]
        
        # Create bark visualization surface
        glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        
        # Draw sound waves emanating from dog's mouth
        for radius in range(glow_size, 0, -5):
            alpha = int(100 * (radius / glow_size) * heat_percent)
            wave_color = (*color, alpha)
            # Draw semi-circular sound waves in front of the dog
            angle_start = self.angle - 30
            angle_end = self.angle + 30
            rect = pygame.Rect(glow_size - radius, glow_size - radius, radius * 2, radius * 2)
            pygame.draw.arc(glow_surf, wave_color, rect, 
                           math.radians(angle_start), math.radians(angle_end), 3)
        
        # Draw the bark visualization on the screen
        glow_rect = glow_surf.get_rect(center=self.rect.center)
        screen.blit(glow_surf, glow_rect.topleft)
        
    def draw_shield(self):
        # Calculate shield parameters based on strength
        shield_percent = self.shield_strength / self.max_shield
        shield_size = int(self.rect.width * (1.5 + shield_percent * 1.0))
        
        # Choose color based on shield level
        color_index = min(len(self.shield_colors) - 1, int(shield_percent * len(self.shield_colors)))
        color = self.shield_colors[color_index]
        
        # Create shield surface
        shield_surf = pygame.Surface((shield_size * 2, shield_size * 2), pygame.SRCALPHA)
        
        # Draw shield as a circle with pulsating effect
        pulse = math.sin(pygame.time.get_ticks() * 0.01) * 0.1 + 0.9
        for radius in range(shield_size, shield_size - 5, -1):
            adjusted_radius = int(radius * pulse)
            alpha = int(150 * shield_percent)
            shield_color = (*color, alpha)
            pygame.draw.circle(shield_surf, shield_color, (shield_size, shield_size), adjusted_radius, 2)
        
        # Draw the shield on the screen
        shield_rect = shield_surf.get_rect(center=self.rect.center)
        screen.blit(shield_surf, shield_rect.topleft)
    
    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH + 200, HEIGHT + 200)  # Move off screen
        # Set respawn time to 3 seconds
        self.respawn_delay = 3000

class Asteroid(pygame.sprite.Sprite):
    def __init__(self, size=3, level_modifier=1.0, color_shift=0):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        # Use appropriate iguana image based on size (index 0=large, 1=medium, 2=small)
        self.image = asteroid_images[3 - self.size]
        # Scale image based on size and level modifier
        scale = self.size * 0.3 * level_modifier
        self.image = pygame.transform.scale(self.image, 
                                           (int(self.image.get_width() * scale),
                                            int(self.image.get_height() * scale)))
        
        # Apply color shift based on level
        if color_shift > 0:
            # Create a copy to avoid modifying the original
            self.image = self.image.copy()
            # Create a color overlay surface
            overlay = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            
            # Generate a color based on level
            hue = (color_shift * 30) % 360  # Shift hue by 30 degrees per level
            # Convert HSV to RGB (hue: 0-360, saturation: 0-100, value: 0-100)
            h = hue / 360
            s = 0.7  # 70% saturation
            v = 0.9  # 90% value
            
            # HSV to RGB conversion
            i = int(h * 6)
            f = h * 6 - i
            p = v * (1 - s)
            q = v * (1 - f * s)
            t = v * (1 - (1 - f) * s)
            
            if i % 6 == 0:
                r, g, b = v, t, p
            elif i % 6 == 1:
                r, g, b = q, v, p
            elif i % 6 == 2:
                r, g, b = p, v, t
            elif i % 6 == 3:
                r, g, b = p, q, v
            elif i % 6 == 4:
                r, g, b = t, p, v
            else:
                r, g, b = v, p, q
                
            color = (int(r * 255), int(g * 255), int(b * 255), 100)
            overlay.fill(color)
            self.image.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
        self.rect = self.image.get_rect()
        
        # Spawn at edge of screen
        side = random.randint(1, 4)
        if side == 1:  # top
            self.rect.x = random.randint(0, WIDTH)
            self.rect.y = -self.rect.height
        elif side == 2:  # right
            self.rect.x = WIDTH
            self.rect.y = random.randint(0, HEIGHT)
        elif side == 3:  # bottom
            self.rect.x = random.randint(0, WIDTH)
            self.rect.y = HEIGHT
        else:  # left
            self.rect.x = -self.rect.width
            self.rect.y = random.randint(0, HEIGHT)
            
        self.position = pygame.math.Vector2(self.rect.center)
        
        # Random velocity
        speed = random.uniform(0.5, 2.0) * (4 - self.size)
        angle = random.uniform(0, 2 * math.pi)
        self.velocity = pygame.math.Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
        
        # Random rotation
        self.rotation = 0
        self.rotation_speed = random.uniform(-3, 3)
        self.original_image = self.image
        self.trail_timer = 0
    
    def update(self):
        # Rotate asteroid
        self.rotation = (self.rotation + self.rotation_speed) % 360
        self.image = pygame.transform.rotate(self.original_image, self.rotation)
        self.rect = self.image.get_rect(center=self.rect.center)
        
        # Update position
        self.position += self.velocity
        self.rect.center = self.position
        
        # Create motion trail based on velocity
        now = pygame.time.get_ticks()
        if self.velocity.length() > 2.0 and now - self.trail_timer > 100:
            self.trail_timer = now
            # Create a trail sprite at current position with lower alpha
            trail = MotionTrail(self.image, self.position, alpha=80)
            game.all_sprites.add(trail)
            game.trails.add(trail)
        
        # Wrap around screen
        if self.position.x < -self.rect.width:
            self.position.x = WIDTH + self.rect.width
        if self.position.x > WIDTH + self.rect.width:
            self.position.x = -self.rect.width
        if self.position.y < -self.rect.height:
            self.position.y = HEIGHT + self.rect.height
        if self.position.y > HEIGHT + self.rect.height:
            self.position.y = -self.rect.height

    def split(self):
        if self.size > 1:
            # Get the current level from the game instance
            level_modifier = 1.0
            color_shift = 0
            if game:
                level_modifier = 1.0 + (game.level - 1) * 0.5
                color_shift = game.level - 1
            
            # Create smaller asteroids with the same level modifiers
            return [Asteroid(self.size - 1, level_modifier, color_shift) for _ in range(2)]
        return []

class SoundWave(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.position = pygame.math.Vector2(self.rect.center)
        self.velocity = pygame.math.Vector2(dx, dy) * 15
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 3000
        self.original_image = self.image
        self.angle = math.degrees(math.atan2(-dy, dx)) - 90
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.pulse_timer = 0
        self.pulse_rate = 100  # milliseconds
        self.trail_timer = 0
    
    def update(self):
        # Update position
        self.position += self.velocity
        self.rect.center = self.position
        
        # Pulse effect for sound wave
        now = pygame.time.get_ticks()
        if now - self.pulse_timer > self.pulse_rate:
            self.pulse_timer = now
            # Alternate between original and slightly larger image
            if self.rect.width == self.original_image.get_width():
                scale = 1.2
                self.image = pygame.transform.scale(self.original_image, 
                                                  (int(self.original_image.get_width() * scale),
                                                   int(self.original_image.get_height() * scale)))
            else:
                self.image = self.original_image
            # Maintain rotation
            self.image = pygame.transform.rotate(self.image, self.angle)
            self.rect = self.image.get_rect(center=self.position)
            
        # Create motion trail for sound waves
        if now - self.trail_timer > 30:  # More frequent trails for bullets
            self.trail_timer = now
            trail = MotionTrail(self.image, self.position, alpha=100)
            trail.lifetime = 8  # Shorter lifetime for bullet trails
            game.all_sprites.add(trail)
            game.trails.add(trail)
        
        # Check if sound wave is off screen or expired
        if (now - self.spawn_time > self.lifetime or
            self.rect.right < 0 or self.rect.left > WIDTH or
            self.rect.bottom < 0 or self.rect.top > HEIGHT):
            self.kill()

class FireworkParticle(pygame.sprite.Sprite):
    def __init__(self, pos, velocity, color, size=3, lifetime_range=(30, 60), particle_type="normal"):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.particle_type = particle_type
        
        if particle_type == "smoke":
            # Smoke particles are gray/white with blur effect
            gray_value = random.randint(180, 230)
            self.color = (gray_value, gray_value, gray_value)
            # Smoke particles are larger and more transparent
            pygame.draw.circle(self.image, self.color, (self.size//2, self.size//2), self.size//2)
            self.alpha = 150
        else:
            # Normal firework particles
            self.color = color
            pygame.draw.circle(self.image, color, (self.size//2, self.size//2), self.size//2)
            self.alpha = 255
            
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.position = pygame.math.Vector2(pos)
        self.velocity = velocity
        self.gravity = pygame.math.Vector2(0, 0.05) if particle_type != "smoke" else pygame.math.Vector2(0, -0.02)
        self.lifetime = random.randint(lifetime_range[0], lifetime_range[1])  # frames
        self.fade_rate = self.alpha / self.lifetime
        self.original_size = size
        self.grow_rate = 0.05 if particle_type == "smoke" else 0
        
    def update(self):
        self.velocity += self.gravity
        self.position += self.velocity
        self.rect.center = self.position
        self.lifetime -= 1
        
        if self.lifetime <= 0:
            self.kill()
        else:
            self.alpha = max(0, self.alpha - self.fade_rate)
            
            if self.particle_type == "smoke":
                # Smoke particles grow over time
                self.size += self.grow_rate
                new_size = int(self.original_size + self.size)
                self.image = pygame.Surface((new_size, new_size), pygame.SRCALPHA)
                pygame.draw.circle(self.image, self.color, (new_size//2, new_size//2), new_size//2)
                self.image.set_alpha(int(self.alpha))
                self.rect = self.image.get_rect(center=self.rect.center)
                
                # Add some random drift to smoke
                self.velocity.x += random.uniform(-0.1, 0.1)
            else:
                # Add sparkle effect to normal particles
                if random.random() < 0.1:  # 10% chance each frame
                    # Temporarily increase brightness
                    bright_color = tuple(min(255, c + 50) for c in self.color[:3])
                    bright_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
                    pygame.draw.circle(bright_surface, bright_color, (self.size//2, self.size//2), self.size//2)
                    bright_surface.set_alpha(int(self.alpha))
                    self.image = bright_surface
                else:
                    # Normal appearance
                    self.image.set_alpha(int(self.alpha))

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.center = center
        self.size = size
        self.particles = []
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_duration = 20  # milliseconds
        self.colors = [
            (255, 0, 0),    # Red
            (255, 165, 0),  # Orange
            (255, 255, 0),  # Yellow
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (128, 0, 128),  # Purple
            (255, 255, 255) # White
        ]
        # Create a dummy image for the sprite
        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center)
        
    def create_particles(self, game, particle_count=None, special_colors=False):
        # Create firework particles
        num_particles = particle_count if particle_count else self.size * 15
        
        # Special colors for player explosion
        special_color_list = [
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
        
        for _ in range(num_particles):
            # Random direction
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3 + self.size)
            velocity = pygame.math.Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
            
            if special_colors:
                color = random.choice(special_color_list)
                # Create larger, longer-lasting particles for player explosion
                particle = FireworkParticle(self.center, velocity, color, size=4, lifetime_range=(45, 90))
            else:
                color = random.choice(self.colors)
                particle = FireworkParticle(self.center, velocity, color)
                
            game.all_sprites.add(particle)
            self.particles.append(particle)
        
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_duration:
            self.last_update = now
            self.frame += 1
            if self.frame >= 1:  # Just need one frame to create particles
                self.kill()

class Game:
    def __init__(self):
        self.score = 0
        self.level = 1
        self.game_over = False
        self.paused = False
        self.controls_disabled = False
        self.explosion_created = False
        self.entering_initials = False
        self.current_initials = ""
        self.initials_cursor = 0
        self.disintegration_effect = None
        self.level_timer = pygame.time.get_ticks()
        self.level_duration = 10000  # 10 seconds per level
        self.show_intro = False  # Flag to show intro again from game over
        
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        self.trails = pygame.sprite.Group()  # New group for motion trails
        
        # Create player (Sheera)
        self.player = Sheera()
        self.all_sprites.add(self.player)
        
        # Initialize audio streamer for background music
        try:
            from audio_streamer import AudioStreamer
            self.audio_streamer = AudioStreamer()
        except ImportError:
            print("AudioStreamer module not available")
            self.audio_streamer = None
            
        # Initialize high score manager
        from highscores import HighScoreManager
        self.high_score_manager = HighScoreManager()
        self.show_high_scores = False
        
        # Spawn initial asteroids
        self.spawn_asteroids(self.level + 2)
        
        # Load font
        self.font = pygame.font.Font(None, 36)
    
    def spawn_asteroids(self, count):
        # Calculate level-based modifiers
        level_size_modifier = 1.0 + (self.level - 1) * 0.5  # 50% size increase per level
        
        # Double the count for each level beyond the first
        adjusted_count = count * (2 ** (self.level - 1))
        
        # Cap the maximum number of asteroids to prevent overwhelming the player
        max_asteroids = 30
        adjusted_count = min(adjusted_count, max_asteroids)
        
        for _ in range(adjusted_count):
            asteroid = Asteroid(3, level_size_modifier, self.level - 1)  # Start with large asteroids
            # Make sure asteroids don't spawn too close to the player
            while (asteroid.position - self.player.position).length() < 150:
                asteroid.position = pygame.math.Vector2(
                    random.randint(0, WIDTH),
                    random.randint(0, HEIGHT)
                )
            self.asteroids.add(asteroid)
            self.all_sprites.add(asteroid)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                # Handle initials input
                if self.game_over and self.entering_initials:
                    if event.key == pygame.K_BACKSPACE:
                        if len(self.current_initials) > 0:
                            self.current_initials = self.current_initials[:-1]
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        pass  # Handled elsewhere
                    elif len(self.current_initials) < 3:
                        if event.unicode.isalpha():
                            self.current_initials += event.unicode.upper()
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_SPACE and not self.controls_disabled:
                    bullet = self.player.shoot()
                    if bullet:
                        self.bullets.add(bullet)
                        self.all_sprites.add(bullet)
                        if shoot_sound:
                            shoot_sound.play()
                if event.key == pygame.K_p and not self.controls_disabled:
                    self.paused = not self.paused
                if event.key == pygame.K_m and hasattr(self, 'audio_streamer') and self.audio_streamer:
                    # Toggle music streaming
                    if self.audio_streamer.is_playing:
                        self.audio_streamer.stop_streaming()
                        print("Background music stopped")
                    else:
                        self.audio_streamer.start_streaming()
                        print("Background music started")
                if event.key == pygame.K_RETURN and self.game_over:
                    if self.entering_initials:
                        # Save high score and show high score table
                        if len(self.current_initials) > 0:
                            self.high_score_manager.add_score(
                                self.current_initials.ljust(3, 'A'), 
                                self.score, 
                                self.level
                            )
                        self.entering_initials = False
                        self.show_high_scores = True
                    elif self.show_high_scores:
                        # Show intro again before starting new game
                        self.show_intro = True
                        return False
                    else:
                        # Show intro again before starting new game
                        self.show_intro = True
                        return False
            
        return True
    
    def update(self):
        if self.paused:
            return
        
        # Check if it's time to increase the level
        current_time = pygame.time.get_ticks()
        if not self.game_over and current_time - self.level_timer > self.level_duration:
            self.level += 1
            self.level_timer = current_time
            
            # Spawn new asteroids for the new level
            self.spawn_asteroids(self.level + 2)
            
            # Display level up message
            print(f"Level up! Now at level {self.level}")
        
        # Update disintegration effect if active
        if self.disintegration_effect and not self.disintegration_effect.is_complete():
            self.disintegration_effect.update()
        
        # If game is over but explosion hasn't been created yet, create it
        if self.game_over and not self.explosion_created:
            # Create a large explosion at the player's position
            explosion = Explosion(self.player.rect.center, 4)  # Size 4 for a big explosion
            self.explosions.add(explosion)
            self.all_sprites.add(explosion)
            explosion.create_particles(self, particle_count=50, special_colors=True)
            
            # Create multiple smaller explosions around the player for dramatic effect
            for _ in range(5):
                offset = pygame.math.Vector2(random.uniform(-30, 30), random.uniform(-30, 30))
                pos = self.player.rect.center + offset
                small_explosion = Explosion(pos, 2)
                self.explosions.add(small_explosion)
                self.all_sprites.add(small_explosion)
                small_explosion.create_particles(self, particle_count=15, special_colors=True)
            
            # Create smoke particles from the player sprite
            for _ in range(30):
                pos = pygame.math.Vector2(self.player.rect.center)
                # Add slight offset for more natural look
                pos += pygame.math.Vector2(random.uniform(-20, 20), random.uniform(-20, 20))
                # Smoke particles move upward and outward
                vel = pygame.math.Vector2(random.uniform(-0.5, 0.5), random.uniform(-1.5, -0.5))
                # Create gray smoke particles with longer lifetime
                smoke = FireworkParticle(pos, vel, (200, 200, 200), size=5, lifetime_range=(60, 120), particle_type="smoke")
                self.all_sprites.add(smoke)
                self.particles.add(smoke)
                
            self.explosion_created = True
            self.controls_disabled = True
            # Hide the player sprite
            self.player.hidden = True
            
        # Check for spacebar held down (rapid fire) - only if controls aren't disabled
        if not self.controls_disabled:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                bullet = self.player.shoot()
                if bullet:
                    self.bullets.add(bullet)
                    self.all_sprites.add(bullet)
                    shoot_sound.play()
            
        # Update all sprites
        self.all_sprites.update()
        
        # Check for shield-bullet collisions (reflect bullets)
        if self.player.shield_active:
            shield_radius = int(self.player.rect.width * (1.5 + self.player.shield_strength / self.player.max_shield))
            for bullet in self.bullets:
                # Calculate distance between bullet and player center
                distance = pygame.math.Vector2(bullet.rect.center).distance_to(self.player.position)
                if distance < shield_radius:
                    # Reflect the bullet by reversing its velocity and slightly randomizing direction
                    bullet.velocity = -bullet.velocity.rotate(random.uniform(-20, 20))
                    # Reset bullet lifetime
                    bullet.spawn_time = pygame.time.get_ticks()
                    # Add some visual effect for reflection
                    self.create_reflection_effect(bullet.rect.center)
        
        # Check for bullet-asteroid collisions
        hits = pygame.sprite.groupcollide(self.asteroids, self.bullets, True, True)
        for asteroid in hits:
            # Score based on asteroid size
            self.score += (4 - asteroid.size) * 100
            
            # Create firework explosion
            explosion = Explosion(asteroid.rect.center, asteroid.size)
            self.explosions.add(explosion)
            self.all_sprites.add(explosion)
            explosion.create_particles(self)
            
            # Split asteroid
            new_asteroids = asteroid.split()
            for new_asteroid in new_asteroids:
                new_asteroid.rect.center = asteroid.rect.center
                new_asteroid.position = pygame.math.Vector2(asteroid.rect.center)
                self.asteroids.add(new_asteroid)
                self.all_sprites.add(new_asteroid)
        
        # Check for ship-asteroid collisions if player is not invulnerable or shielded
        if not self.player.invulnerable and not self.player.hidden and not self.player.shield_active:
            hits = pygame.sprite.spritecollide(self.player, self.asteroids, True, 
                                              pygame.sprite.collide_circle)
            for asteroid in hits:
                self.player.lives -= 1
                
                # Create firework explosion at asteroid position
                explosion = Explosion(asteroid.rect.center, asteroid.size)
                self.explosions.add(explosion)
                self.all_sprites.add(explosion)
                explosion.create_particles(self)
                
                # Create colorful explosion at player position
                player_explosion = Explosion(self.player.rect.center, 3)
                self.explosions.add(player_explosion)
                self.all_sprites.add(player_explosion)
                player_explosion.create_particles(self, particle_count=30, special_colors=True)
                
                # Add smoke effect when player is hit
                for _ in range(15):
                    pos = pygame.math.Vector2(self.player.rect.center)
                    # Add slight offset
                    pos += pygame.math.Vector2(random.uniform(-10, 10), random.uniform(-10, 10))
                    # Smoke particles move upward
                    vel = pygame.math.Vector2(random.uniform(-0.3, 0.3), random.uniform(-1.0, -0.2))
                    # Create gray smoke particles
                    smoke = FireworkParticle(pos, vel, (180, 180, 180), size=4, lifetime_range=(30, 60), particle_type="smoke")
                    self.all_sprites.add(smoke)
                    self.particles.add(smoke)
                
                # Split asteroid
                new_asteroids = asteroid.split()
                for new_asteroid in new_asteroids:
                    new_asteroid.rect.center = asteroid.rect.center
                    new_asteroid.position = pygame.math.Vector2(asteroid.rect.center)
                    self.asteroids.add(new_asteroid)
                    self.all_sprites.add(new_asteroid)
                
                if self.player.lives <= 0:
                    # Game over
                    self.game_over = True
                    # Create disintegration effect from player sprite
                    self.disintegration_effect = DisintegrationEffect(
                        self.player.image, 
                        self.player.rect.center,
                        particle_count=150
                    )
                    # Check if this is a high score
                    if self.high_score_manager.is_high_score(self.score):
                        self.entering_initials = True
                        self.current_initials = ""
                else:
                    # Hide player temporarily
                    self.player.hide()
        
        # Check if all asteroids are destroyed
        if len(self.asteroids) == 0:
            self.level += 1
            self.spawn_asteroids(self.level + 2)
    
    def draw(self):
        # Draw background
        screen.fill(BLACK)
        
        # Draw sprites in layers to handle glow effects
        # First draw trails
        for sprite in self.trails:
            screen.blit(sprite.image, sprite.rect)
            
        # Then draw other non-player sprites
        for sprite in self.all_sprites:
            if sprite != self.player and sprite not in self.trails:
                screen.blit(sprite.image, sprite.rect)
        
        # Draw disintegration effect if active
        if self.disintegration_effect and not self.disintegration_effect.is_complete():
            self.disintegration_effect.draw(screen)
            # Don't draw the player if disintegrating
        elif not self.game_over and not self.player.hidden:
            # Draw player with shield or glow
            if self.player.shield_active:
                self.player.draw_shield()
            elif self.player.heat > 0:
                self.player.draw_glow()
            screen.blit(self.player.image, self.player.rect)
            
        # Draw level up notification
        time_since_level = pygame.time.get_ticks() - self.level_timer
        if time_since_level < 2000:  # Show for 2 seconds
            # Flash the text
            if (time_since_level // 200) % 2 == 0:  # Flash every 200ms
                level_text = f"LEVEL {self.level}"
                self.draw_text(level_text, WIDTH // 2 - 60, HEIGHT // 2 - 100, size=48, color=(255, 255, 0))
        
        # Draw HUD
        self.draw_text(f"Score: {self.score}", 10, 10)
        self.draw_text(f"Level: {self.level}", 10, 50)
        self.draw_text(f"Lives: {self.player.lives}", WIDTH - 100, 10)
        
        # Show heat level
        heat_percent = int((self.player.heat / self.player.max_heat) * 100)
        if heat_percent > 0:
            self.draw_text(f"Heat: {heat_percent}%", WIDTH - 100, 50)
            
        # Show shield level
        shield_percent = int((self.player.shield_strength / self.player.max_shield) * 100)
        if shield_percent > 0:
            self.draw_text(f"Shield: {shield_percent}%", WIDTH - 100, 90)
            
        # Show fire rate boost
        fire_boost_percent = int((self.player.fire_rate_boost / self.player.max_fire_rate_boost) * 100)
        if fire_boost_percent > 0:
            boost_color = (255, 255 - fire_boost_percent * 2, 0)  # Yellow to red
            self.draw_text(f"Fire Rate: +{fire_boost_percent}%", WIDTH - 150, 130, color=boost_color)
        
        if self.game_over:
            if self.entering_initials:
                self.draw_text("NEW HIGH SCORE!", WIDTH // 2 - 120, HEIGHT // 2 - 60)
                self.draw_text("Enter your initials:", WIDTH // 2 - 120, HEIGHT // 2 - 20)
                
                # Draw initials with blinking cursor
                for i in range(3):
                    char = self.current_initials[i] if i < len(self.current_initials) else "_"
                    # Make cursor blink
                    if i == len(self.current_initials) and pygame.time.get_ticks() % 1000 < 500:
                        char = "|"
                    self.draw_text(char, WIDTH // 2 - 40 + i * 30, HEIGHT // 2 + 20, size=48)
                
                self.draw_text("Press ENTER when done", WIDTH // 2 - 140, HEIGHT // 2 + 80)
            elif self.show_high_scores:
                self.draw_text("HIGH SCORES", WIDTH // 2 - 100, HEIGHT // 2 - 150)
                
                for i, entry in enumerate(self.high_score_manager.high_scores[:10]):
                    y_pos = HEIGHT // 2 - 100 + i * 30
                    self.draw_text(f"{i+1}. {entry['initials']} {entry['score']:06d} L{entry['level']}", 
                                  WIDTH // 2 - 100, y_pos)
                
                self.draw_text("Press ENTER to start over", WIDTH // 2 - 125, HEIGHT // 2 + 200)
            else:
                self.draw_text("GAME OVER", WIDTH // 2 - 100, HEIGHT // 2 - 30)
                self.draw_text(f"Final Score: {self.score}", WIDTH // 2 - 100, HEIGHT // 2 + 10)
                self.draw_text("Press ESC to exit", WIDTH // 2 - 100, HEIGHT // 2 + 50)
                self.draw_text("Press ENTER to start over", WIDTH // 2 - 125, HEIGHT // 2 + 90)
        
        if self.paused:
            self.draw_text("PAUSED", WIDTH // 2 - 50, HEIGHT // 2)
            self.draw_text("Press P to continue", WIDTH // 2 - 100, HEIGHT // 2 + 40)
        
        # Update display
        pygame.display.flip()
    
    def draw_text(self, text, x, y, size=None, color=WHITE):
        if size:
            font = pygame.font.Font(None, size)
        else:
            font = self.font
        text_surface = font.render(text, True, color)
        screen.blit(text_surface, (x, y))
        
    def create_reflection_effect(self, position):
        # Create a small flash effect when bullets reflect off shield
        for _ in range(5):
            # Random direction
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            velocity = pygame.math.Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
            # Use shield color for reflection particles
            color_index = min(len(self.player.shield_colors) - 1, 
                             int((self.player.shield_strength / self.player.max_shield) * len(self.player.shield_colors)))
            color = self.player.shield_colors[color_index]
            # Create particle
            particle = FireworkParticle(position, velocity, color)
            particle.lifetime = 10  # Short lifetime
            self.all_sprites.add(particle)
            self.particles.add(particle)

# Create a global game instance that can be accessed by other classes
game = None

# Main game loop
def main():
    global game
    show_intro = True
    
    while True:
        # Show intro animation
        if show_intro:
            intro = IntroAnimation(screen, assets_dir, ship_img, asteroid_images)
            if not intro.run():
                pygame.quit()
                sys.exit()
            show_intro = False
        
        # Start the game
        game = Game()
        running = True
        
        while running:
            clock.tick(FPS)
            
            # Handle events
            running = game.handle_events()
            
            # Update game state
            game.update()
            
            # Draw everything
            game.draw()
            
            # Check if we should show intro again
            if not running and game.show_intro:
                show_intro = True
                break
        
        # If we're not showing intro again, exit
        if not show_intro:
            break
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
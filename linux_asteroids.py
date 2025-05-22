#!/usr/bin/env python3
"""
Sheera vs Tux
A game where Sheera uses sound waves to defend against Tux penguins.
"""
import pygame
import sys
import math
import random
import os
from pygame.locals import *
import collections

# Initialize pygame
pygame.init()
try:
    pygame.mixer.init()
    print("Pygame mixer initialized successfully.")
except pygame.error as e:
    print(f"Error initializing pygame mixer: {e}. Game will run without sound.")
    pygame.mixer = None # type: ignore

# Game constants
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sheera vs Tux")
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

# Load game assets
ship_img = load_image(os.path.join(assets_dir, "sheera.jpg"), (120, 90))  # Load Sheera image at twice the size
bullet_img = load_image(os.path.join(assets_dir, "bullet.png"))
explosion_img = load_image(os.path.join(assets_dir, "explosion.png"))

# Sound File Placeholders
shoot_sound_file = os.path.join(assets_dir, "shoot.wav")
explosion_sound_file = os.path.join(assets_dir, "explosion.wav")
thrust_sound_file = os.path.join(assets_dir, "thrust.wav")
player_hit_sound_file = os.path.join(assets_dir, "player_hit.wav")
shield_activate_sound_file = os.path.join(assets_dir, "shield_on.wav")
shield_deactivate_sound_file = os.path.join(assets_dir, "shield_off.wav")

# Tux Asteroid Animation Setup
tux_anim_filenames = [os.path.join(assets_dir, f"tux_anim_{i}.png") for i in range(2)] # Expecting tux_anim_0.png and tux_anim_1.png
tux_animations_available = all(os.path.exists(f) for f in tux_anim_filenames)
processed_asteroid_frames = []
tux_sizes = [(60, 60), (45, 45), (30, 30)] # L, M, S sizes for asteroids

if tux_animations_available:
    print("Tux animation frames found. Implementing animations.")
    base_tux_frames = [load_image(f) for f in tux_anim_filenames]
    for target_size in tux_sizes:
        frames_for_size = [pygame.transform.scale(frame.copy(), target_size) for frame in base_tux_frames]
        processed_asteroid_frames.append(frames_for_size)
else:
    print("Tux animation frames not found or incomplete. Using static Tux image.")
    tux_original_static = load_image(os.path.join(assets_dir, "tux_original.png")) # Renamed to avoid conflict
    if tux_original_static.get_width() < 10: # Basic check if placeholder was loaded
        print("Warning: tux_original.png might be a placeholder or failed to load correctly.")
    for target_size in tux_sizes:
        processed_asteroid_frames.append([pygame.transform.scale(tux_original_static.copy(), target_size)])

# Game classes
class Sheera(pygame.sprite.Sprite):
    def __init__(self, game): # Added game argument
        pygame.sprite.Sprite.__init__(self)
        self.game = game # Store game instance
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
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.is_hit_flashing = False
        self.hit_flash_timer = 0
        self.hit_flash_duration = 1000  # 1 second
        self.invulnerability_duration_on_hit = 2000  # 2 seconds
        self.current_invulnerability_window = 0 # Stores the duration for current invulnerability
        
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
        self.prev_shield_active = False # For tracking shield state change

    def update(self):
        # Handle invulnerability
        if self.invulnerable:
            if pygame.time.get_ticks() - self.invulnerable_timer > self.current_invulnerability_window:
                self.invulnerable = False
        
        # Handle hidden state (after death) - Player Respawn
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.center = (WIDTH // 2, HEIGHT // 2)
            self.position = pygame.math.Vector2(self.rect.center)
            self.velocity = pygame.math.Vector2(0, 0)
            self.invulnerable = True
            self.invulnerable_timer = pygame.time.get_ticks()
            self.current_invulnerability_window = 3000 # Standard respawn invulnerability

        # Handle hit flashing timer
        if self.is_hit_flashing:
            if pygame.time.get_ticks() - self.hit_flash_timer > self.hit_flash_duration:
                self.is_hit_flashing = False

        # Get key presses
        keys = pygame.key.get_pressed()
        
        # Rotation
        if keys[pygame.K_LEFT]:
            self.angle += self.rotation_speed
        if keys[pygame.K_RIGHT]:
            self.angle -= self.rotation_speed
            
        # Thrust
        if keys[pygame.K_UP]:
            # Calculate thrust vector based on angle
            thrust_x = -math.sin(math.radians(self.angle)) * self.acceleration
            thrust_y = -math.cos(math.radians(self.angle)) * self.acceleration
            self.velocity += pygame.math.Vector2(thrust_x, thrust_y)
            
            # Limit speed
            if self.velocity.length() > self.max_speed:
                self.velocity.scale_to_length(self.max_speed)
            # Play thrust sound
            if pygame.mixer and self.game.thrust_sound and not pygame.mixer.Channel(0).get_busy():
                pygame.mixer.Channel(0).play(self.game.thrust_sound, loops=-1)
        else:
            # Stop thrust sound
            if pygame.mixer:
                pygame.mixer.Channel(0).stop()
        
        # Shield control
        current_shield_key_pressed = keys[pygame.K_s]
        if current_shield_key_pressed:
            # Increase shield strength while S is held
            self.shield_strength = min(self.max_shield, self.shield_strength + self.shield_increase)
        else:
            # Decrease shield strength when S is released
            self.shield_strength = max(0, self.shield_strength - self.shield_decrease)
        
        self.shield_active = self.shield_strength > 0

        # Shield sound effects
        if pygame.mixer:
            if self.shield_active and not self.prev_shield_active:
                if self.game.shield_activate_sound:
                    self.game.shield_activate_sound.play()
            elif not self.shield_active and self.prev_shield_active:
                if self.game.shield_deactivate_sound:
                    self.game.shield_deactivate_sound.play()
        self.prev_shield_active = self.shield_active
        
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
        rotated_image = pygame.transform.rotate(self.original_image, self.angle)
        
        # Apply alpha effects for flashing or invulnerability
        if self.is_hit_flashing:
            if (pygame.time.get_ticks() // 100) % 2 == 0:  # Flash every 100ms
                rotated_image.set_alpha(64)  # Dimmer
            else:
                rotated_image.set_alpha(192)  # Brighter
        elif self.invulnerable:
            rotated_image.set_alpha(128)  # General invulnerability alpha
        else:
            rotated_image.set_alpha(255) # Ensure full alpha if no effects

        self.image = rotated_image
        self.rect = self.image.get_rect(center=self.rect.center)
        
        # Shield and glow effects are now handled in the Game.draw() method
    
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay and not self.hidden:
            self.last_shot = now
            # Increase heat when shooting (dog barking heats up)
            self.heat = min(self.max_heat, self.heat + self.heat_increase)

            if pygame.mixer and self.game.shoot_sound:
                self.game.shoot_sound.play()
            
            # Calculate sound wave direction based on dog angle
            direction_x = -math.sin(math.radians(self.angle))
            direction_y = -math.cos(math.radians(self.angle))
            # Position sound wave at the front of the dog (mouth)
            pos_x = self.position.x + direction_x * self.rect.width / 2
            pos_y = self.position.y + direction_y * self.rect.height / 2
            
            # Create a sound wave bullet
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
        if self.shield_strength <= 0: # No need to draw if shield is off
            return

        shield_percent = self.shield_strength / self.max_shield
        base_shield_radius = int(self.rect.width * 0.75 + (self.rect.width * 0.50 * shield_percent)) # Scale from 0.75x to 1.25x ship width

        # Choose color based on shield level
        color_index = min(len(self.shield_colors) - 1, int(shield_percent * len(self.shield_colors)))
        base_color = self.shield_colors[color_index]

        # Create shield surface, ensure it's large enough for the biggest pulse
        # Max radius will be base_shield_radius * (pulse_amplitude_max, e.g., 1.15 or 1.2)
        # Let's make surface 2.5x base_shield_radius
        surface_size = int(base_shield_radius * 2.5) 
        # Ensure surface_size is at least 1 to avoid pygame.error: Surfaceissiing
        surface_size = max(1, surface_size)
        shield_surf = pygame.Surface((surface_size, surface_size), pygame.SRCALPHA)
        surface_center = surface_size // 2

        # 1. Outer pulsating boundary (more subtle pulse, stronger alpha)
        outer_pulse_factor = math.sin(pygame.time.get_ticks() * 0.015) * 0.05 + 0.97  # Small size pulse: 0.97 to 1.02
        outer_radius = int(base_shield_radius * outer_pulse_factor)
        outer_alpha = int(120 + 135 * shield_percent) # Range from 120 to 255
        outer_alpha = max(0, min(255, outer_alpha)) # Clamp alpha
        if outer_radius > 0: # Ensure radius is positive
            pygame.draw.circle(shield_surf, (*base_color, outer_alpha), 
                               (surface_center, surface_center), outer_radius, 3) # Thickness 3

        # 2. Inner energy shimmer/pulse (more rapid or different visual pulse)
        inner_pulse_factor = math.sin(pygame.time.get_ticks() * 0.05) * 0.1 + 0.85 # Size pulse: 0.85 to 0.95 of base_radius
        inner_radius = int(base_shield_radius * inner_pulse_factor)
        # Alpha pulse for inner shimmer
        inner_alpha_pulse = math.sin(pygame.time.get_ticks() * 0.07) * 50 + 100 # Alpha from 50 to 150
        inner_alpha = int(inner_alpha_pulse * shield_percent) # Modulated by shield strength
        inner_alpha = max(0, min(255, inner_alpha)) # Clamp alpha
        
        # Optional: Inner shimmer as a slightly different color or thinner line
        # For example, a lighter shade of the base_color
        light_color = tuple(min(255, c + 50) for c in base_color) 
        if inner_radius > 0: # Ensure radius is positive
            pygame.draw.circle(shield_surf, (*light_color, inner_alpha),
                               (surface_center, surface_center), inner_radius, 2) # Thickness 2
        
        # Blit the shield surface
        shield_rect = shield_surf.get_rect(center=self.rect.center)
        screen.blit(shield_surf, shield_rect.topleft)
    
    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH + 200, HEIGHT + 200)  # Move off screen

class Asteroid(pygame.sprite.Sprite):
    def __init__(self, size=3):
        pygame.sprite.Sprite.__init__(self)
        self.size = size # size 3=Large, 2=Medium, 1=Small
        
        # Assign frames based on size (index 0=L, 1=M, 2=S)
        # Size 3 maps to index 0, Size 2 to 1, Size 1 to 2.
        self.frames = processed_asteroid_frames[3 - self.size]
        self.current_frame_index = 0
        self.image = self.frames[self.current_frame_index]
        self.original_image = self.image # For rotation
        self.rect = self.image.get_rect()

        self.animation_last_update = pygame.time.get_ticks()
        self.animation_speed = 200  # milliseconds per frame
        
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
        # self.original_image is already set to the current animation frame
    
    def update(self):
        # Animation
        if tux_animations_available and len(self.frames) > 1:
            now = pygame.time.get_ticks()
            if now - self.animation_last_update > self.animation_speed:
                self.animation_last_update = now
                self.current_frame_index = (self.current_frame_index + 1) % len(self.frames)
                self.original_image = self.frames[self.current_frame_index] # Update original_image for rotation

        # Rotate asteroid
        self.rotation = (self.rotation + self.rotation_speed) % 360
        self.image = pygame.transform.rotate(self.original_image, self.rotation)
        self.rect = self.image.get_rect(center=self.rect.center)
        
        # Update position
        self.position += self.velocity
        self.rect.center = self.position
        
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
            return [Asteroid(self.size - 1) for _ in range(2)]
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
        
        # Check if sound wave is off screen or expired
        if (now - self.spawn_time > self.lifetime or
            self.rect.right < 0 or self.rect.left > WIDTH or
            self.rect.bottom < 0 or self.rect.top > HEIGHT):
            self.kill()

class FireworkParticle(pygame.sprite.Sprite):
    def __init__(self, pos, velocity, color):
        pygame.sprite.Sprite.__init__(self)
        self.size = 3
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (self.size//2, self.size//2), self.size//2)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.position = pygame.math.Vector2(pos)
        self.velocity = velocity
        self.gravity = pygame.math.Vector2(0, 0.05)
        self.lifetime = random.randint(30, 60)  # frames
        self.alpha = 255
        self.fade_rate = 255 / self.lifetime
        
    def update(self):
        self.velocity += self.gravity
        self.position += self.velocity
        self.rect.center = self.position
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
        else:
            self.alpha = max(0, self.alpha - self.fade_rate)
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
        
    def create_particles(self, game):
        # Create firework particles
        num_particles = self.size * 15
        for _ in range(num_particles):
            # Random direction
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3 + self.size)
            velocity = pygame.math.Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
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
        
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        
        # Create player (Sheera)
        self.player = Sheera(self) # Pass game instance to Sheera
        self.all_sprites.add(self.player)
        
        # Spawn initial asteroids
        self.spawn_asteroids(self.level + 2)
        
        # Load font
        self.font = pygame.font.Font(None, 36)

        # Load Sounds
        if pygame.mixer:
            self.shoot_sound = None
            if os.path.exists(shoot_sound_file):
                self.shoot_sound = pygame.mixer.Sound(shoot_sound_file)
            else:
                print(f"Warning: Sound file not found: {shoot_sound_file}. Game will run without this sound.")

            self.explosion_sound = None
            if os.path.exists(explosion_sound_file):
                self.explosion_sound = pygame.mixer.Sound(explosion_sound_file)
            else:
                print(f"Warning: Sound file not found: {explosion_sound_file}. Game will run without this sound.")

            self.thrust_sound = None
            if os.path.exists(thrust_sound_file):
                self.thrust_sound = pygame.mixer.Sound(thrust_sound_file)
                self.thrust_sound.set_volume(0.5) # Set volume for looping thrust
            else:
                print(f"Warning: Sound file not found: {thrust_sound_file}. Game will run without this sound.")

            self.player_hit_sound = None
            if os.path.exists(player_hit_sound_file):
                self.player_hit_sound = pygame.mixer.Sound(player_hit_sound_file)
            else:
                print(f"Warning: Sound file not found: {player_hit_sound_file}. Game will run without this sound.")
            
            self.shield_activate_sound = None
            if os.path.exists(shield_activate_sound_file):
                self.shield_activate_sound = pygame.mixer.Sound(shield_activate_sound_file)
            else:
                print(f"Warning: Sound file not found: {shield_activate_sound_file}. Game will run without this sound.")

            self.shield_deactivate_sound = None
            if os.path.exists(shield_deactivate_sound_file):
                self.shield_deactivate_sound = pygame.mixer.Sound(shield_deactivate_sound_file)
            else:
                print(f"Warning: Sound file not found: {shield_deactivate_sound_file}. Game will run without this sound.")
        else: # Mixer not available
            self.shoot_sound = None
            self.explosion_sound = None
            self.thrust_sound = None
            self.player_hit_sound = None
            self.shield_activate_sound = None
            self.shield_deactivate_sound = None
            print("Mixer not initialized, all sounds disabled.")


        # Starfield
        self.Star = collections.namedtuple("Star", ["x", "y", "speed", "radius", "color"])
        self.stars = []
        for _ in range(150): # Generate 150 stars
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            radius = random.choice([1, 2, 3])
            speed = radius * 0.5
            color_value = 50 + radius * 50
            # Ensure color_value is within 0-255
            color_value = max(0, min(255, color_value)) 
            color = (color_value, color_value, color_value)
            self.stars.append(self.Star(x, y, speed, radius, color))
    
    def spawn_asteroids(self, count):
        for _ in range(count):
            asteroid = Asteroid(3)  # Start with large asteroids
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
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_SPACE:
                    bullet = self.player.shoot()
                    if bullet:
                        self.bullets.add(bullet)
                        self.all_sprites.add(bullet)
                if event.key == pygame.K_p:
                    self.paused = not self.paused
            
        return True
    
    def update(self):
        if self.paused:
            return
        
        self.update_stars()
            
        # Check for spacebar held down (rapid fire)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            bullet = self.player.shoot()
            if bullet:
                self.bullets.add(bullet)
                self.all_sprites.add(bullet)
            
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

            if pygame.mixer and self.explosion_sound:
                self.explosion_sound.play()
            
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
                # Activate hit feedback
                self.player.is_hit_flashing = True
                self.player.hit_flash_timer = pygame.time.get_ticks()
                self.player.invulnerable = True
                self.player.invulnerable_timer = pygame.time.get_ticks()
                self.player.current_invulnerability_window = self.player.invulnerability_duration_on_hit

                self.player.lives -= 1

                if pygame.mixer and self.player_hit_sound:
                    self.player_hit_sound.play()
                
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
                
                if self.player.lives <= 0:
                    # Game over
                    self.game_over = True
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

        # Draw stars
        for star in self.stars:
            pygame.draw.circle(screen, star.color, (star.x, int(star.y)), star.radius)
        
        # Draw sprites in layers to handle glow effects
        # First draw non-player sprites
        for sprite in self.all_sprites:
            if sprite != self.player:
                screen.blit(sprite.image, sprite.rect)
        
        # Draw player with shield or glow
        if self.player.shield_active:
            self.player.draw_shield()
        elif self.player.heat > 0:
            self.player.draw_glow()
        screen.blit(self.player.image, self.player.rect)
        
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
        
        if self.game_over:
            self.draw_text("GAME OVER", WIDTH // 2 - 100, HEIGHT // 2 - 30)
            self.draw_text(f"Final Score: {self.score}", WIDTH // 2 - 100, HEIGHT // 2 + 10)
            self.draw_text("Press ESC to exit", WIDTH // 2 - 100, HEIGHT // 2 + 50)
        
        if self.paused:
            self.draw_text("PAUSED", WIDTH // 2 - 50, HEIGHT // 2)
            self.draw_text("Press P to continue", WIDTH // 2 - 100, HEIGHT // 2 + 40)
        
        # Update display
        pygame.display.flip()

    def update_stars(self):
        for i, star in enumerate(self.stars):
            new_y = star.y + star.speed
            if new_y > HEIGHT:
                new_y = 0
                new_x = random.randint(0, WIDTH)
                self.stars[i] = star._replace(y=new_y, x=new_x)
            else:
                self.stars[i] = star._replace(y=new_y)
    
    def draw_text(self, text, x, y):
        text_surface = self.font.render(text, True, WHITE)
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

# Main game loop
def main():
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
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
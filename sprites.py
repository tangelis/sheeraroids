"""
Game sprite classes: Player, Enemies, Projectiles, Effects
"""
import pygame
import math
import random
from constants import WIDTH, HEIGHT, WHITE, BLACK
from utils import load_game_assets

# Load assets for sprites
ship_img, bullet_img, explosion_img, asteroid_images = load_game_assets()

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

class Sheera(pygame.sprite.Sprite):
    def __init__(self, game_mode="normal"):
        pygame.sprite.Sprite.__init__(self)
        # Load different image based on game mode
        if game_mode == "accelerated":
            try:
                import os
                from constants import assets_dir
                mode_img = pygame.image.load(os.path.join(assets_dir, "ChatGPT Image Jun 12, 2025, 07_17_20 PM.png"))
                scaled_img = pygame.transform.scale(mode_img, (60, 60))
                self.image = pygame.transform.rotate(scaled_img, 90)
            except:
                self.image = ship_img
        elif game_mode == "slowed":
            try:
                import os
                from constants import assets_dir
                mode_img = pygame.image.load(os.path.join(assets_dir, "Generated Image June 12, 2025 - 7_16PM.png"))
                scaled_img = pygame.transform.scale(mode_img, (60, 60))
                self.image = pygame.transform.rotate(scaled_img, 90)
            except:
                self.image = ship_img
        else:
            self.image = ship_img
        self.original_image = self.image
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.position = pygame.math.Vector2(self.rect.center)
        self.velocity = pygame.math.Vector2(0, 0)
        self.angle = 0
        self.rotation_speed = 1.5
        self.acceleration = 0.2
        self.max_speed = 7
        self.friction = 0.98
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.trail_timer = 0
        
        # Glow effect properties
        self.heat = 0
        self.max_heat = 100
        self.heat_increase = 20
        self.heat_cooldown = 1
        self.glow_colors = [
            (255, 255, 0), (255, 165, 0), (255, 69, 0), (255, 0, 0)
        ]
        
        # Shield properties
        self.shield_active = False
        self.shield_strength = 0
        self.max_shield = 100
        self.shield_increase = 2
        self.shield_decrease = 5
        self.shield_colors = [
            (0, 100, 255), (0, 50, 255), (0, 0, 255), (75, 0, 130)
        ]

    def update(self):
        # Handle invulnerability
        if self.invulnerable:
            if pygame.time.get_ticks() - self.invulnerable_timer > 2000:
                self.invulnerable = False
        
        if self.hidden:
            # Check if it's time to respawn (after 3 seconds)
            if pygame.time.get_ticks() - self.hide_timer > 3000:
                self.respawn()
            return
        
        # Handle input
        keys = pygame.key.get_pressed()
        
        # Rotation
        if keys[pygame.K_LEFT]:
            self.angle += self.rotation_speed
        if keys[pygame.K_RIGHT]:
            self.angle -= self.rotation_speed
        
        # Thrust
        if keys[pygame.K_UP]:
            thrust_x = math.cos(math.radians(self.angle)) * self.acceleration
            thrust_y = -math.sin(math.radians(self.angle)) * self.acceleration
            self.velocity.x += thrust_x
            self.velocity.y += thrust_y
            
            # Limit speed
            if self.velocity.length() > self.max_speed:
                self.velocity.scale_to_length(self.max_speed)
        
        # Apply friction
        self.velocity *= self.friction
        
        # Update position
        self.position += self.velocity
        
        # Wrap around screen
        if self.position.x < 0:
            self.position.x = WIDTH
        elif self.position.x > WIDTH:
            self.position.x = 0
        if self.position.y < 0:
            self.position.y = HEIGHT
        elif self.position.y > HEIGHT:
            self.position.y = 0
            
        # Update rect position
        self.rect.center = self.position
        
        # Cool down heat
        self.heat = max(0, self.heat - self.heat_cooldown)
        
        # Rotate ship image
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
    
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay and not self.hidden:
            self.last_shot = now
            self.heat = min(self.max_heat, self.heat + self.heat_increase)
            
            # Calculate shooting direction (3 o'clock direction)
            right_angle = self.angle - 90
            direction_x = -math.sin(math.radians(right_angle))
            direction_y = -math.cos(math.radians(right_angle))
            
            # Calculate spawn position at the right side of the head
            offset_x = direction_x * (self.rect.width * 0.5)
            offset_y = direction_y * (self.rect.height * 0.5)
            
            pos_x = self.position.x + offset_x
            pos_y = self.position.y + offset_y
            
            return SoundWave(pos_x, pos_y, direction_x, direction_y)
        return None
        
    def draw_glow(self):
        from constants import screen
        # Calculate bark intensity parameters based on heat
        heat_percent = self.heat / self.max_heat
        glow_size = int(self.rect.width * (1 + heat_percent * 0.8))
        
        # Choose color based on bark intensity level
        color_index = min(len(self.glow_colors) - 1, int(heat_percent * len(self.glow_colors)))
        color = self.glow_colors[color_index]
        
        # Create bark visualization surface
        glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        
        # Draw multiple glow circles for intensity effect
        for radius in range(glow_size, glow_size - 10, -1):
            alpha = int(100 * heat_percent * (radius / glow_size))
            glow_color = (*color, alpha)
            pygame.draw.circle(glow_surface, glow_color, (glow_size, glow_size), radius, 2)
        
        # Draw the glow on the screen
        glow_rect = glow_surface.get_rect(center=self.rect.center)
        screen.blit(glow_surface, glow_rect.topleft)
    
    def draw_shield(self):
        from constants import screen
        if not self.shield_active:
            return
            
        shield_percent = self.shield_strength / self.max_shield
        shield_size = int(self.rect.width * (1.5 + shield_percent))
        
        # Choose color based on shield strength
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
        self.rect.center = (WIDTH + 200, HEIGHT + 200)
    
    def respawn(self):
        """Respawn the player in the center with invulnerability"""
        if self.lives > 0:  # Only respawn if still have lives
            self.hidden = False
            self.position = pygame.math.Vector2(WIDTH // 2, HEIGHT // 2)
            self.rect.center = self.position
            self.velocity = pygame.math.Vector2(0, 0)
            self.angle = 0
            # Make invulnerable for 2 seconds after respawn
            self.invulnerable = True
            self.invulnerable_timer = pygame.time.get_ticks()
            # Reset heat and other stats
            self.heat = 0

class Asteroid(pygame.sprite.Sprite):
    def __init__(self, size=3):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = asteroid_images[3 - self.size]
        scale = self.size * 0.3
        self.image = pygame.transform.scale(self.image, 
                                           (int(self.image.get_width() * scale),
                                            int(self.image.get_height() * scale)))
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
        
        # Wrap around screen
        if self.position.x < -50:
            self.position.x = WIDTH + 50
        elif self.position.x > WIDTH + 50:
            self.position.x = -50
        if self.position.y < -50:
            self.position.y = HEIGHT + 50
        elif self.position.y > HEIGHT + 50:
            self.position.y = -50
        
        self.rect.center = self.position
    
    def split(self):
        """Split asteroid into smaller pieces"""
        new_asteroids = []
        if self.size > 1:
            for _ in range(2):
                new_asteroid = Asteroid(self.size - 1)
                # Random velocity for new pieces
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(1, 3)
                new_asteroid.velocity = pygame.math.Vector2(
                    math.cos(angle) * speed, math.sin(angle) * speed
                )
                new_asteroids.append(new_asteroid)
        return new_asteroids

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
        self.pulse_rate = 100
        self.trail_timer = 0
    
    def update(self):
        # Update position
        self.position += self.velocity
        self.rect.center = self.position
        
        # Pulse effect
        now = pygame.time.get_ticks()
        if now - self.pulse_timer > self.pulse_rate:
            self.pulse_timer = now
            # Scale bullet for sound wave effect
            if self.lifetime > 2000:
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
        self.lifetime = random.randint(30, 60)
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
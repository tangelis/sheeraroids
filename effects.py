"""
Visual effects: Explosions, Fragments, Particles
"""
import pygame
import math
import random
from constants import WIDTH, HEIGHT

class ImageFragment(pygame.sprite.Sprite):
    def __init__(self, surface, position, velocity, rotation_speed, game):
        pygame.sprite.Sprite.__init__(self)
        self.original_surface = surface
        self.image = surface
        self.rect = self.image.get_rect()
        self.position = pygame.math.Vector2(position)
        self.rect.center = self.position
        self.velocity = velocity
        self.rotation = 0
        self.rotation_speed = rotation_speed
        self.game = game  # Reference to game for slider access
        
        # Store initial speed for scaling calculation
        self.initial_speed = velocity.length()
        
        self.base_scale = 1.0  # Time-based shrinking scale
        self.alpha = 255
        self.lifetime = 120  # frames
        self.gravity = pygame.math.Vector2(0, 0.3)
        
    def update(self):
        # Update physics
        self.velocity += self.gravity
        self.position += self.velocity
        self.rect.center = self.position
        
        # Update rotation
        self.rotation += self.rotation_speed
        
        # Calculate speed-based scale with fixed multiplier
        # Normalize speed based on range (1-15) with aggressive scaling
        normalized_speed = min(1.0, self.initial_speed / 15.0)
        
        # FIXED DRAMATIC SCALING SYSTEM:
        # - Middle speed (7.5/15 = 0.5) gives 2.5x size
        # - Full speed (15/15 = 1.0) gives 4x size  
        # - Fixed multiplier for consistent dramatic effect
        
        if normalized_speed > 0.1:  # Scale almost all moving fragments
            # DRAMATIC SCALING: Linear interpolation from 1x to 4x
            # 0.0 speed = 1x, 0.5 speed = 2.5x, 1.0 speed = 4x
            base_scale_multiplier = 1.0 + (normalized_speed * 3.0)  # Linear 1x to 4x
            
            # Use fixed multiplier of 1.0 for good balance
            speed_scale_factor = base_scale_multiplier
        else:
            speed_scale_factor = 1.0  # Keep very slow fragments normal size
        
        # Apply time-based shrinking while preserving speed-based scale
        self.base_scale *= 0.98  # Time-based shrinkage
        # Final scale combines speed scaling with time-based shrinking
        self.scale = self.base_scale * speed_scale_factor
        
        # Fade out
        self.alpha = max(0, self.alpha - 2)
        self.lifetime -= 1
        
        # Apply transformations
        if self.scale > 0.1 and self.lifetime > 0:
            # Scale the image
            scaled_size = (int(self.original_surface.get_width() * self.scale),
                          int(self.original_surface.get_height() * self.scale))
            if scaled_size[0] > 0 and scaled_size[1] > 0:
                scaled_image = pygame.transform.scale(self.original_surface, scaled_size)
                # Rotate the image
                self.image = pygame.transform.rotate(scaled_image, self.rotation)
                self.image.set_alpha(self.alpha)
                self.rect = self.image.get_rect(center=self.position)
        else:
            self.kill()
            
        # Apply drag
        self.velocity *= 0.98
        
        # Kill if off screen
        if (self.rect.right < 0 or self.rect.left > WIDTH or 
            self.rect.bottom < 0 or self.rect.top > HEIGHT):
            self.kill()

class PlayerExplosion(pygame.sprite.Sprite):
    def __init__(self, player_image, position, game):
        pygame.sprite.Sprite.__init__(self)
        self.position = position
        self.game = game
        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=position)
        self.fragments = []
        self.shockwave_radius = 0
        self.max_shockwave_radius = 200
        self.frame = 0
        self.flash_alpha = 255
        
        # Create fragments from player image
        self.create_fragments(player_image)
        
    def create_fragments(self, image):
        """Break the player image into fragments"""
        width, height = image.get_size()
        
        # Create a 4x4 grid of fragments
        cols = rows = 4
        frag_width = width // cols
        frag_height = height // rows
        
        for row in range(rows):
            for col in range(cols):
                # Create fragment surface
                frag_surface = pygame.Surface((frag_width, frag_height), pygame.SRCALPHA)
                
                # Copy portion of original image
                src_rect = pygame.Rect(col * frag_width, row * frag_height, 
                                      frag_width, frag_height)
                frag_surface.blit(image, (0, 0), src_rect)
                
                # Calculate fragment center position
                frag_x = self.position[0] - width//2 + col * frag_width + frag_width//2
                frag_y = self.position[1] - height//2 + row * frag_height + frag_height//2
                
                # Calculate velocity away from center
                dx = frag_x - self.position[0]
                dy = frag_y - self.position[1]
                distance = math.sqrt(dx**2 + dy**2) or 1
                
                # Much wider speed range for more dramatic scaling differences
                base_speed = random.uniform(1, 15)  # Much wider range: 1-15 instead of 3-8
                velocity = pygame.math.Vector2(
                    (dx/distance) * base_speed + random.uniform(-3, 3),
                    (dy/distance) * base_speed + random.uniform(-3, 3)
                )
                
                # Random rotation speed
                rotation_speed = random.uniform(-15, 15)
                
                # Create fragment sprite
                fragment = ImageFragment(frag_surface, (frag_x, frag_y), velocity, rotation_speed, self.game)
                self.fragments.append(fragment)
    
    def update(self):
        self.frame += 1
        
        # Update shockwave
        if self.shockwave_radius < self.max_shockwave_radius:
            self.shockwave_radius += 8
            
        # Update flash
        self.flash_alpha = max(0, self.flash_alpha - 15)
        
        # Kill after shockwave completes
        if self.shockwave_radius >= self.max_shockwave_radius and self.flash_alpha <= 0:
            self.kill()
    
    def draw_effects(self, surface):
        # Draw white flash
        if self.flash_alpha > 0:
            flash_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash_surface.fill((255, 255, 255, self.flash_alpha))
            surface.blit(flash_surface, (0, 0))
            
        # Draw shockwave
        if self.shockwave_radius < self.max_shockwave_radius:
            # Calculate alpha based on radius
            alpha = int(255 * (1 - self.shockwave_radius / self.max_shockwave_radius))
            
            # Draw multiple rings for thickness
            for i in range(3):
                ring_alpha = alpha // (i + 1)
                if ring_alpha > 0:
                    # Create a surface for the ring
                    ring_surface = pygame.Surface((self.shockwave_radius * 2 + 10, 
                                                 self.shockwave_radius * 2 + 10), pygame.SRCALPHA)
                    pygame.draw.circle(ring_surface, (255, 255, 255, ring_alpha),
                                     (self.shockwave_radius + 5, self.shockwave_radius + 5),
                                     self.shockwave_radius - i, 3)
                    
                    # Blit with additive blending for glow
                    surface.blit(ring_surface, 
                               (self.position[0] - self.shockwave_radius - 5,
                                self.position[1] - self.shockwave_radius - 5),
                               special_flags=pygame.BLEND_ADD)

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
            (255, 0, 0), (255, 165, 0), (255, 255, 0),
            (0, 255, 0), (0, 0, 255), (128, 0, 128), (255, 255, 255)
        ]
        # Create a dummy image for the sprite
        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center)
        
    def create_particles(self, game):
        from sprites import FireworkParticle
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
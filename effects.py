"""
Visual effects: Explosions, Fragments, Particles
"""
import pygame
import math
import random
from constants import WIDTH, HEIGHT

class FinalDeathExplosion(pygame.sprite.Sprite):
    """Simple but cool two-burst particle explosion for final death"""
    def __init__(self, center, game, sound1=None, sound2=None, particle_sound=None):
        pygame.sprite.Sprite.__init__(self)
        self.center = center
        self.game = game
        self.frame = 0
        self.burst_triggered = [False, False, False]  # Two bursts + particle sound
        self.sound1 = sound1
        self.sound2 = sound2
        self.particle_sound = particle_sound
        
        # Dummy sprite requirements
        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center)
        
    def update(self):
        self.frame += 1
        
        # First burst - immediate with sound
        if self.frame == 1 and not self.burst_triggered[0]:
            self.create_particle_burst(self.center, 100, 8, [(255, 255, 0), (255, 200, 0), (255, 150, 0)])
            if self.sound1:
                self.sound1.play()
            self.burst_triggered[0] = True
        
        # Second burst - delayed for impact with different sound
        if self.frame == 20 and not self.burst_triggered[1]:
            self.create_particle_burst(self.center, 150, 12, [(255, 0, 0), (255, 100, 0), (255, 255, 255)])
            if self.sound2:
                self.sound2.play()
            self.burst_triggered[1] = True
        
        # Particle shrinking sound - slightly after second burst
        if self.frame == 30 and not self.burst_triggered[2]:
            if self.particle_sound:
                self.particle_sound.play()
            self.burst_triggered[2] = True
        
        # Kill after all effects are done
        if self.frame > 200:  # Let particles live longer
            self.kill()
    
    def create_particle_burst(self, center, count, max_speed, colors):
        """Create a burst of particles"""
        from sprites import FireworkParticle
        
        for i in range(count):
            angle = (i / count) * 2 * math.pi + random.uniform(-0.2, 0.2)
            speed = random.uniform(max_speed * 0.8, max_speed * 1.5)  # Faster particles
            velocity = pygame.math.Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
            color = random.choice(colors)
            
            particle = FireworkParticle(center, velocity, color)
            particle.lifetime = random.randint(120, 180)  # Much longer lifetime for shrinking effect
            # Recreate image with new size
            new_size = random.randint(4, 8)
            particle.size = new_size
            particle.image = pygame.Surface((new_size * 2, new_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle.image, color, (new_size, new_size), new_size)
            particle.rect = particle.image.get_rect(center=center)
            
            self.game.all_sprites.add(particle)
            self.game.particles.add(particle)

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
        # Create visible explosion sprite
        self.radius = size * 20
        self.max_radius = size * 60
        self.image = pygame.Surface((self.max_radius * 2, self.max_radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center)
        self.alpha = 255
        
    def create_particles(self, game):
        from sprites import FireworkParticle
        # Create firework particles
        num_particles = self.size * 15
        for _ in range(num_particles):
            # Random direction
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5 + self.size)  # Increased speed
            velocity = pygame.math.Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
            color = random.choice(self.colors)
            particle = FireworkParticle(self.center, velocity, color)
            game.all_sprites.add(particle)
            game.particles.add(particle)  # Add to particles group too!
            self.particles.append(particle)
        
    def update(self):
        # Expand explosion radius
        if self.radius < self.max_radius:
            self.radius += self.size * 3
        
        # Fade out
        self.alpha = max(0, self.alpha - 8)
        
        # Clear image
        self.image.fill((0, 0, 0, 0))
        
        # Draw explosion circles
        if self.alpha > 0:
            # Draw multiple colored rings for dramatic effect
            for i in range(3):
                ring_radius = self.radius - i * 10
                if ring_radius > 0:
                    color_idx = (self.frame + i) % len(self.colors)
                    color = self.colors[color_idx]
                    ring_alpha = self.alpha // (i + 1)
                    pygame.draw.circle(self.image, (*color, ring_alpha),
                                     (self.max_radius, self.max_radius),
                                     int(ring_radius), max(2, 5 - i))
            
            # Draw bright center flash
            if self.radius < self.max_radius // 2:
                flash_radius = int(self.radius * 1.5)
                pygame.draw.circle(self.image, (255, 255, 255, min(255, self.alpha * 2)),
                                 (self.max_radius, self.max_radius),
                                 flash_radius)
        
        self.frame += 1
        
        # Kill after fully expanded and faded
        if self.radius >= self.max_radius and self.alpha <= 0:
            self.kill()
import pygame
import random
import math

class DisintegrationEffect:
    """Creates a disintegration effect from a sprite image"""
    
    def __init__(self, sprite_image, position, particle_count=100):
        self.particles = []
        self.position = position
        self.create_particles(sprite_image, particle_count)
        self.complete = False
        
    def create_particles(self, sprite_image, particle_count):
        # Get sprite dimensions
        width = sprite_image.get_width()
        height = sprite_image.get_height()
        
        # Sample pixels from the sprite image
        for _ in range(particle_count):
            # Random position within the sprite
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            
            # Get color at this position (if not transparent)
            try:
                color = sprite_image.get_at((x, y))
                if color.a > 0:  # Only create particles for non-transparent pixels
                    # Calculate world position
                    world_x = self.position[0] - width/2 + x
                    world_y = self.position[1] - height/2 + y
                    
                    # Create particle with random velocity
                    angle = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(0.5, 2.0)
                    velocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                    
                    # Add some upward drift for smoke-like effect
                    velocity[1] -= random.uniform(0.5, 1.0)
                    
                    particle = {
                        'pos': [world_x, world_y],
                        'vel': velocity,
                        'color': (color.r, color.g, color.b),
                        'size': random.randint(1, 3),
                        'alpha': 255,
                        'fade_rate': random.uniform(2, 5)
                    }
                    self.particles.append(particle)
            except:
                # Skip any pixels that cause issues
                pass
    
    def update(self):
        # Update all particles
        for particle in self.particles[:]:
            # Move particle
            particle['pos'][0] += particle['vel'][0]
            particle['pos'][1] += particle['vel'][1]
            
            # Add gravity effect
            particle['vel'][1] += 0.03
            
            # Fade out
            particle['alpha'] -= particle['fade_rate']
            
            # Remove faded particles
            if particle['alpha'] <= 0:
                self.particles.remove(particle)
        
        # Check if effect is complete
        if len(self.particles) == 0:
            self.complete = True
    
    def draw(self, surface):
        # Draw all particles
        for particle in self.particles:
            # Create a surface for this particle
            size = particle['size']
            particle_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            
            # Draw the particle
            pygame.draw.circle(
                particle_surf, 
                (*particle['color'], int(particle['alpha'])), 
                (size, size), 
                size
            )
            
            # Blit to main surface
            surface.blit(particle_surf, (particle['pos'][0] - size, particle['pos'][1] - size))
    
    def is_complete(self):
        return self.complete
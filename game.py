"""
Main game class and logic
"""
import pygame
import math
import random
from constants import WIDTH, HEIGHT, WHITE, BLACK, screen, clock
from sprites import Sheera, Asteroid, SoundWave, FireworkParticle
from effects import Explosion
from highscores import HighScoreManager, HighScoreEntry
from screens import RetroGameOverScreen
from audio import load_all_sounds

# Load all sounds at module level
shoot_sound, explosion_sound, death_sound_80s, transition_music_80s = load_all_sounds()

class Game:
    def __init__(self, game_mode="normal"):
        self.score = 0
        self.level = 1
        self.game_over = False
        self.paused = False
        self.controls_disabled = False
        self.explosion_created = False
        self.game_mode = game_mode
        
        # High score system
        self.high_score_manager = HighScoreManager()
        self.high_score_entry = None
        self.retro_game_over = None
        self.game_state = "playing"  # "playing", "transition", "game_over_80s", "entering_initials"
        self.transition_timer = 0
        self.transition_duration = 300  # 5 seconds at 60fps
        self.music_started = False
        
        
        # Speed multipliers based on game mode
        if game_mode == "accelerated":
            self.speed_multiplier = 1.5
            self.rotation_multiplier = 1.5
        elif game_mode == "slowed":
            self.speed_multiplier = 0.5
            self.rotation_multiplier = 0.5
        else:
            self.speed_multiplier = 1.0
            self.rotation_multiplier = 1.0
        
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        self.trails = pygame.sprite.Group()  # New group for motion trails
        
        # Create player (Sheera) with the selected game mode
        self.player = Sheera(game_mode)
        # Apply game mode modifiers to player
        self.player.rotation_speed *= self.rotation_multiplier
        self.player.acceleration *= self.speed_multiplier
        self.player.max_speed *= self.speed_multiplier
        self.all_sprites.add(self.player)
        
        # Spawn initial asteroids
        self.spawn_asteroids(self.level + 2)
        
        # Load font
        self.font = pygame.font.Font(None, 36)
    
    def spawn_asteroids(self, count):
        for _ in range(count):
            asteroid = Asteroid(3)  # Start with large asteroids
            # Apply speed multiplier to asteroid
            asteroid.velocity *= self.speed_multiplier
            asteroid.rotation_speed *= self.rotation_multiplier
            # Make sure asteroids don't spawn too close to the player
            while (asteroid.position - self.player.position).length() < 150:
                asteroid.position = pygame.math.Vector2(
                    random.randint(0, WIDTH),
                    random.randint(0, HEIGHT)
                )
            self.asteroids.add(asteroid)
            self.all_sprites.add(asteroid)
    
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                
                # UNIVERSAL RESTART: ENTER key restarts game from any death-related state
                if event.key == pygame.K_RETURN and self.game_over:
                    return "restart"
                
                # Handle different game states
                if self.game_state == "playing":
                    if event.key == pygame.K_SPACE and not self.controls_disabled:
                        bullet = self.player.shoot()
                        if bullet:
                            bullet.velocity *= self.speed_multiplier
                            self.bullets.add(bullet)
                            self.all_sprites.add(bullet)
                            if shoot_sound:
                                shoot_sound.play()
                    if event.key == pygame.K_p and not self.controls_disabled:
                        self.paused = not self.paused
                
                
                elif self.game_state == "game_over_80s":
                    # ONLY ENTER key starts a new game - all other keys ignored
                    if event.key == pygame.K_RETURN:
                        return "restart"
                    # All other keys are completely ignored
                
                elif self.game_state == "entering_initials":
                    # Handle initial entry
                    self.high_score_entry.handle_input(event)
                    if self.high_score_entry.done:
                        # After entering initials, save and restart
                        return "restart"
                
            
        return True
    
    def update(self):
        # FIRST: Check if game just ended - go directly to 80s screen
        if self.game_over and not self.explosion_created:
            self.explosion_created = True
            self.controls_disabled = True
            # Hide the player sprite completely
            self.player.hidden = True
            # Remove player from all sprite groups so it won't be drawn
            self.all_sprites.remove(self.player)
            
            # Play 80s style death sound
            if death_sound_80s:
                death_sound_80s.play()
            
            # Go DIRECTLY to 80s screen - skip transition animation
            self.game_state = "game_over_80s"
            self.retro_game_over = RetroGameOverScreen(self.score, self.high_score_manager.get_high_scores())
        
        # Handle paused or 80s screen states
        if self.paused or self.game_state != "playing":
            # Update 80s screen if active
            if self.game_state == "game_over_80s" and self.retro_game_over:
                self.retro_game_over.update()
                # After 2 seconds, automatically show initials entry
                if self.retro_game_over.should_show_initials():
                    self.game_state = "entering_initials"
                    self.high_score_entry = HighScoreEntry(self.score, self.high_score_manager)
            return
            
        # Check for spacebar held down (rapid fire) - only if controls aren't disabled
        if not self.controls_disabled:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                bullet = self.player.shoot()
                if bullet:
                    bullet.velocity *= self.speed_multiplier
                    self.bullets.add(bullet)
                    self.all_sprites.add(bullet)
                    if shoot_sound:
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
                # Apply speed multiplier to split asteroids
                new_asteroid.velocity *= self.speed_multiplier
                new_asteroid.rotation_speed *= self.rotation_multiplier
                self.asteroids.add(new_asteroid)
                self.all_sprites.add(new_asteroid)
        
        # Check for ship-asteroid collisions if player is not invulnerable or shielded
        if not self.player.invulnerable and not self.player.hidden and not self.player.shield_active:
            hits = pygame.sprite.spritecollide(self.player, self.asteroids, True, 
                                              pygame.sprite.collide_circle)
            for asteroid in hits:
                self.player.lives -= 1
                
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
                    # Apply speed multiplier to split asteroids
                    new_asteroid.velocity *= self.speed_multiplier
                    new_asteroid.rotation_speed *= self.rotation_multiplier
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
        # Handle different game states
        if self.game_state == "game_over_80s":
            if self.retro_game_over:
                self.retro_game_over.draw(screen)
            pygame.display.flip()
            return
        elif self.game_state == "entering_initials":
            if self.high_score_entry:
                self.high_score_entry.draw(screen)
            pygame.display.flip()
            return
        
        # Normal gameplay drawing
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
        
        # Draw player with shield or glow (only if not exploding)
        if not self.player.hidden:
            # Blink during invulnerability
            should_draw = True
            if self.player.invulnerable:
                # Blink every 100ms during invulnerability
                blink_time = pygame.time.get_ticks() % 200
                should_draw = blink_time < 100
            
            if should_draw:
                if self.player.shield_active:
                    self.player.draw_shield()
                elif self.player.heat > 0:
                    self.player.draw_glow()
                screen.blit(self.player.image, self.player.rect)
        
        # Draw HUD
        self.draw_text(f"Score: {self.score}", 10, 10)
        self.draw_text(f"Level: {self.level}", 10, 50)
        
        # Only show player-related HUD if player exists and isn't exploded
        if self.player and not self.player.hidden:
            self.draw_text(f"Lives: {self.player.lives}", WIDTH - 100, 10)
            
            # Show heat level
            heat_percent = int((self.player.heat / self.player.max_heat) * 100)
            if heat_percent > 0:
                self.draw_text(f"Heat: {heat_percent}%", WIDTH - 100, 50)
                
            # Show shield level
            shield_percent = int((self.player.shield_strength / self.player.max_shield) * 100)
            if shield_percent > 0:
                self.draw_text(f"Shield: {shield_percent}%", WIDTH - 100, 90)
        elif self.game_over:
            # Show lives as 0 when game over
            self.draw_text(f"Lives: 0", WIDTH - 100, 10)
        
        # Show game mode
        mode_text = "ACCELERATED" if self.game_mode == "accelerated" else "SLOWED" if self.game_mode == "slowed" else "NORMAL"
        mode_color = (255, 200, 100) if self.game_mode == "accelerated" else (100, 200, 255) if self.game_mode == "slowed" else WHITE
        mode_surface = self.font.render(f"Mode: {mode_text}", True, mode_color)
        screen.blit(mode_surface, (WIDTH // 2 - 100, 10))
        
        if self.game_over and self.game_state != "transition":
            self.draw_text("GAME OVER", WIDTH // 2 - 100, HEIGHT // 2 - 30)
            self.draw_text(f"Final Score: {self.score}", WIDTH // 2 - 100, HEIGHT // 2 + 10)
            self.draw_text("Press ESC to exit", WIDTH // 2 - 100, HEIGHT // 2 + 50)
            self.draw_text("Press ENTER to start over", WIDTH // 2 - 125, HEIGHT // 2 + 90)
        
        # Transition effect
        if self.game_state == "transition":
            # Fade to black effect
            progress = self.transition_timer / self.transition_duration
            alpha = min(255, int(progress * 255))
            
            # Create fade overlay
            fade_surface = pygame.Surface((WIDTH, HEIGHT))
            fade_surface.set_alpha(alpha)
            fade_surface.fill((0, 0, 0))
            screen.blit(fade_surface, (0, 0))
            
            # Show restart instruction during transition
            self.draw_text("Press ENTER to restart", WIDTH // 2 - 120, HEIGHT - 50)
            
            # Show creative transition effects
            if progress > 0.2:  # Start effects after 20% of transition
                
                # Pulsing energy orbs
                num_orbs = 8
                orb_radius = 20 + int(progress * 30)
                
                for i in range(num_orbs):
                    angle = (i * 2 * math.pi / num_orbs) + (self.transition_timer * 0.1)
                    distance = 80 + math.sin(self.transition_timer * 0.05) * 20
                    
                    orb_x = WIDTH//2 + math.cos(angle) * distance
                    orb_y = HEIGHT//2 + math.sin(angle) * distance
                    
                    # Cycling neon colors
                    color_cycle = (self.transition_timer + i * 30) % 180
                    if color_cycle < 60:
                        color = (255, int(255 * (color_cycle / 60)), 255)  # Pink to white
                    elif color_cycle < 120:
                        color = (int(255 * ((120 - color_cycle) / 60)), 255, 255)  # White to cyan
                    else:
                        color = (255, 255, int(255 * ((color_cycle - 120) / 60)))  # Cyan to pink
                    
                    # Draw orb with glow effect
                    pygame.draw.circle(screen, color, (int(orb_x), int(orb_y)), orb_radius, 3)
                    pygame.draw.circle(screen, (*color[:3], 100), (int(orb_x), int(orb_y)), orb_radius + 10, 1)
                
                # Digital rain effect (Matrix-style but with 80s colors)
                if progress > 0.4:
                    for x in range(0, WIDTH, 20):
                        rain_height = int((progress - 0.4) * HEIGHT * 2)
                        for y in range(0, min(rain_height, HEIGHT), 15):
                            # Random characters
                            char = chr(random.randint(33, 126))
                            char_alpha = max(0, 255 - (y * 3))
                            
                            # Neon green like classic matrix
                            char_color = (0, 255, 100, char_alpha)
                            char_surf = pygame.font.Font(None, 24).render(char, True, char_color[:3])
                            char_surf.set_alpha(char_alpha)
                            screen.blit(char_surf, (x + random.randint(-5, 5), y))
                
                # Central growing hexagon
                if progress > 0.6:
                    hex_size = int((progress - 0.6) * 100)
                    hex_points = []
                    for i in range(6):
                        angle = i * math.pi / 3
                        hex_x = WIDTH//2 + math.cos(angle) * hex_size
                        hex_y = HEIGHT//2 + math.sin(angle) * hex_size
                        hex_points.append((hex_x, hex_y))
                    
                    # Draw hexagon with pulsing neon outline
                    pulse_width = 3 + int(math.sin(self.transition_timer * 0.3) * 2)
                    pygame.draw.polygon(screen, (255, 0, 255), hex_points, pulse_width)
        
        if self.paused:
            self.draw_text("PAUSED", WIDTH // 2 - 50, HEIGHT // 2)
            self.draw_text("Press P to continue", WIDTH // 2 - 100, HEIGHT // 2 + 40)
        
        
        
        # Update display
        pygame.display.flip()
    
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
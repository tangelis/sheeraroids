"""
Game screens: 80s Game Over screen and other visual effects
"""
import pygame
import math
import random
from constants import WIDTH, HEIGHT, WHITE, BLACK, screen, clock

class RetroGameOverScreen:
    def __init__(self, score, high_scores):
        self.score = score
        self.high_scores = high_scores
        self.frame = 0
        self.scroll_offset = 0
        self.scroll_speed = 1
        self.timer = 0  # Timer for 2-second auto-transition
        
        # 80s color palette
        self.neon_pink = (255, 20, 147)
        self.neon_cyan = (0, 255, 255)
        self.neon_purple = (138, 43, 226)
        self.neon_green = (50, 205, 50)
        self.neon_orange = (255, 165, 0)
        
        # Background elements
        self.stars = []
        for _ in range(100):
            self.stars.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(0, HEIGHT),
                'speed': random.uniform(0.5, 2.0),
                'brightness': random.randint(100, 255)
            })
        
        # Grid lines for 80s aesthetic
        self.grid_lines = []
        for i in range(0, WIDTH, 40):
            self.grid_lines.append(i)
    
    def update(self):
        self.frame += 1
        self.timer += 1  # Increment timer (60fps = 120 frames for 2 seconds)
        
        # Update scrolling high scores
        self.scroll_offset += self.scroll_speed
        if self.scroll_offset > len(self.high_scores) * 40 + HEIGHT:
            self.scroll_offset = 0
        
        # Update stars
        for star in self.stars:
            star['y'] += star['speed']
            if star['y'] > HEIGHT:
                star['y'] = 0
                star['x'] = random.randint(0, WIDTH)
    
    def should_show_initials(self):
        """Check if 2 seconds have passed (120 frames at 60fps)"""
        return self.timer >= 120
    
    def draw_grid_background(self, surface):
        """Draw 80s style grid background"""
        # Draw perspective grid
        grid_color = (40, 40, 80)
        
        # Horizontal lines (perspective)
        for y in range(HEIGHT//2, HEIGHT, 20):
            # Calculate perspective scaling
            distance = y - HEIGHT//2
            scale = 1 + (distance / HEIGHT)
            line_width = max(1, int(3 / scale))
            
            start_x = WIDTH//2 - (WIDTH * scale)//2
            end_x = WIDTH//2 + (WIDTH * scale)//2
            
            if start_x > -WIDTH and end_x < WIDTH * 2:
                pygame.draw.line(surface, grid_color, (start_x, y), (end_x, y), line_width)
        
        # Vertical lines (perspective)
        for i, x in enumerate(self.grid_lines):
            # Calculate perspective
            center_offset = x - WIDTH//2
            for y in range(HEIGHT//2, HEIGHT, 5):
                distance = y - HEIGHT//2
                scale = 1 + (distance / HEIGHT)
                perspective_x = WIDTH//2 + (center_offset * scale)
                
                if 0 <= perspective_x <= WIDTH:
                    pygame.draw.circle(surface, grid_color, (int(perspective_x), y), 1)
    
    def draw_stars(self, surface):
        """Draw moving starfield"""
        for star in self.stars:
            alpha = star['brightness']
            star_color = (alpha, alpha, alpha)
            pygame.draw.circle(surface, star_color, (int(star['x']), int(star['y'])), 1)
    
    def draw_neon_text(self, surface, text, size, color, x, y, glow=True):
        """Draw text with neon glow effect"""
        font = pygame.font.Font(None, size)
        
        if glow:
            # Draw glow effect
            for offset in range(5, 0, -1):
                glow_color = tuple(min(255, c + offset * 10) for c in color)
                glow_alpha = 100 - offset * 15
                
                # Create glow surface
                glow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                glow_text = font.render(text, True, (*glow_color, glow_alpha))
                
                # Draw glow in multiple positions
                for dx in range(-offset, offset + 1):
                    for dy in range(-offset, offset + 1):
                        if dx != 0 or dy != 0:
                            glow_rect = glow_text.get_rect(center=(x + dx, y + dy))
                            glow_surface.blit(glow_text, glow_rect)
                
                surface.blit(glow_surface, (0, 0))
        
        # Draw main text
        main_text = font.render(text, True, color)
        text_rect = main_text.get_rect(center=(x, y))
        surface.blit(main_text, text_rect)
    
    def draw_geometric_shapes(self, surface):
        """Draw 80s geometric shapes"""
        # Pulsating triangles
        pulse = math.sin(self.frame * 0.1) * 0.3 + 0.7
        
        # Left triangle
        triangle_size = int(50 * pulse)
        triangle_points = [
            (100, 200),
            (100 - triangle_size, 200 + triangle_size),
            (100 + triangle_size, 200 + triangle_size)
        ]
        pygame.draw.polygon(surface, self.neon_cyan, triangle_points, 3)
        
        # Right triangle
        triangle_points = [
            (WIDTH - 100, 200),
            (WIDTH - 100 - triangle_size, 200 + triangle_size),
            (WIDTH - 100 + triangle_size, 200 + triangle_size)
        ]
        pygame.draw.polygon(surface, self.neon_pink, triangle_points, 3)
        
        # Rotating diamonds
        rotation = self.frame * 2
        diamond_size = 30
        
        for i, color in enumerate([self.neon_purple, self.neon_green, self.neon_orange]):
            x = 150 + i * 100
            y = 100
            
            # Calculate diamond points with rotation
            angle_rad = math.radians(rotation + i * 45)
            cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
            
            points = []
            for dx, dy in [(0, -diamond_size), (diamond_size, 0), (0, diamond_size), (-diamond_size, 0)]:
                rx = dx * cos_a - dy * sin_a + x
                ry = dx * sin_a + dy * cos_a + y
                points.append((rx, ry))
            
            pygame.draw.polygon(surface, color, points, 2)
    
    def draw_scrolling_scores(self, surface):
        """Draw scrolling high scores"""
        font = pygame.font.Font(None, 36)
        
        # Current score highlight
        self.draw_neon_text(surface, f"YOUR SCORE: {self.score}", 48, self.neon_cyan, WIDTH//2, 400)
        
        # Scrolling high scores
        for i, entry in enumerate(self.high_scores):
            y_pos = 500 + i * 40 - self.scroll_offset
            
            if -50 < y_pos < HEIGHT + 50:
                score_text = f"{i+1:2d}. {entry['initials']} - {entry['score']:,}"
                color = self.neon_pink if i % 2 == 0 else self.neon_green
                self.draw_neon_text(surface, score_text, 32, color, WIDTH//2, y_pos, glow=False)
    
    def draw(self, surface):
        """Draw the complete 80s game over screen"""
        # Clear screen with dark background
        surface.fill((10, 10, 30))
        
        # Draw background elements
        self.draw_grid_background(surface)
        self.draw_stars(surface)
        
        # Draw geometric shapes
        self.draw_geometric_shapes(surface)
        
        # Main "GAME OVER" text with pulsing effect
        pulse = math.sin(self.frame * 0.15) * 0.2 + 1.0
        game_over_size = int(96 * pulse)
        self.draw_neon_text(surface, "GAME OVER", game_over_size, self.neon_pink, WIDTH//2, 200)
        
        # Add subtitle
        self.draw_neon_text(surface, "SHEERA'S MISSION COMPLETE", 36, self.neon_cyan, WIDTH//2, 280)
        
        # Draw scrolling scores
        self.draw_scrolling_scores(surface)
        
        # Show different message based on timer
        if self.timer < 120:  # Before 2 seconds
            remaining = int((120 - self.timer) / 60) + 1  # Convert frames to seconds
            self.draw_neon_text(surface, f"Enter initials in {remaining}...", 28, self.neon_orange, WIDTH//2, HEIGHT - 60, glow=False)
        else:
            self.draw_neon_text(surface, "PRESS ENTER TO RESTART", 28, self.neon_orange, WIDTH//2, HEIGHT - 60, glow=False)
        
        # Update frame counter
        self.update()
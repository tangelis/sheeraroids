"""
Game screens: Purple initials entry and clean high scores display
"""
import pygame
import math
import random
from constants import WIDTH, HEIGHT, WHITE, BLACK, screen, clock


class PurpleInitialsScreen:
    """Purple-themed dashboard for entering initials"""
    def __init__(self, score, typing_sound=None):
        self.score = score
        self.typing_sound = typing_sound
        self.initials = ""
        self.done = False
        self.animation_time = 0
        self.cursor_blink_timer = 0
        self.cursor_visible = True
        
        # Purple color palette
        self.purple_dark = (40, 20, 60)
        self.purple_mid = (80, 40, 120)
        self.purple_light = (120, 60, 180)
        self.purple_bright = (160, 80, 220)
        self.accent_pink = (255, 100, 200)
        self.accent_cyan = (100, 255, 255)
        self.white = (255, 255, 255)
        
        # Design elements
        self.particles = []
        for _ in range(30):
            self.particles.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(0, HEIGHT),
                'size': random.uniform(2, 5),
                'speed': random.uniform(0.5, 2),
                'angle': random.uniform(0, 2 * math.pi),
                'rotation_speed': random.uniform(-0.05, 0.05)
            })
        
        # Geometric shapes for decoration
        self.shapes = []
        for _ in range(10):
            self.shapes.append({
                'type': random.choice(['triangle', 'square', 'hexagon']),
                'x': random.randint(0, WIDTH),
                'y': random.randint(0, HEIGHT),
                'size': random.uniform(20, 50),
                'rotation': random.uniform(0, 2 * math.pi),
                'rotation_speed': random.uniform(-0.02, 0.02),
                'color': random.choice([self.purple_light, self.purple_mid, self.accent_pink])
            })
    
    def handle_input(self, event):
        """Handle keyboard input for initials entry"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if len(self.initials) > 0:
                    self.initials = self.initials[:-1]
                    if self.typing_sound:
                        self.typing_sound.play()
            elif event.key == pygame.K_RETURN:
                if len(self.initials) == 3:
                    self.done = True
            else:
                # Add character if it's a letter and we have less than 3 initials
                if event.unicode.isalpha() and len(self.initials) < 3:
                    self.initials += event.unicode.upper()
                    if self.typing_sound:
                        self.typing_sound.play()
    
    def update(self):
        """Update animation elements"""
        self.animation_time += 1
        self.cursor_blink_timer += 1
        
        # Blink cursor
        if self.cursor_blink_timer >= 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_blink_timer = 0
        
        # Update particles
        for particle in self.particles:
            particle['y'] -= particle['speed']
            particle['angle'] += particle['rotation_speed']
            
            # Wrap around
            if particle['y'] < -10:
                particle['y'] = HEIGHT + 10
                particle['x'] = random.randint(0, WIDTH)
        
        # Update shapes
        for shape in self.shapes:
            shape['rotation'] += shape['rotation_speed']
    
    def draw_shape(self, surface, shape_type, x, y, size, rotation, color):
        """Draw a geometric shape"""
        points = []
        
        if shape_type == 'triangle':
            for i in range(3):
                angle = rotation + (i * 2 * math.pi / 3)
                px = x + size * math.cos(angle)
                py = y + size * math.sin(angle)
                points.append((px, py))
        elif shape_type == 'square':
            for i in range(4):
                angle = rotation + (i * math.pi / 2)
                px = x + size * math.cos(angle)
                py = y + size * math.sin(angle)
                points.append((px, py))
        elif shape_type == 'hexagon':
            for i in range(6):
                angle = rotation + (i * math.pi / 3)
                px = x + size * math.cos(angle) * 0.8
                py = y + size * math.sin(angle) * 0.8
                points.append((px, py))
        
        if len(points) >= 3:
            pygame.draw.polygon(surface, color, points, 2)
    
    def draw_gradient_background(self, surface):
        """Draw purple gradient background"""
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            # Interpolate between dark purple at top and mid purple at bottom
            r = int(self.purple_dark[0] * (1 - ratio) + self.purple_mid[0] * ratio)
            g = int(self.purple_dark[1] * (1 - ratio) + self.purple_mid[1] * ratio)
            b = int(self.purple_dark[2] * (1 - ratio) + self.purple_mid[2] * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))
    
    def draw_dashboard_frame(self, surface):
        """Draw the dashboard frame with purple theme"""
        # Outer frame
        pygame.draw.rect(surface, self.purple_bright, (50, 50, WIDTH - 100, HEIGHT - 100), 3)
        
        # Inner decorative frame
        pygame.draw.rect(surface, self.purple_light, (70, 70, WIDTH - 140, HEIGHT - 140), 2)
        
        # Corner decorations
        corner_size = 30
        corners = [
            (70, 70),  # Top left
            (WIDTH - 70 - corner_size, 70),  # Top right
            (70, HEIGHT - 70 - corner_size),  # Bottom left
            (WIDTH - 70 - corner_size, HEIGHT - 70 - corner_size)  # Bottom right
        ]
        
        for cx, cy in corners:
            # Draw corner accent
            pygame.draw.lines(surface, self.accent_pink, False, 
                            [(cx, cy + corner_size), (cx, cy), (cx + corner_size, cy)], 3)
    
    def draw_particles(self, surface):
        """Draw floating particles"""
        for particle in self.particles:
            # Create glowing effect
            glow_surf = pygame.Surface((particle['size'] * 4, particle['size'] * 4), pygame.SRCALPHA)
            glow_color = (*self.accent_cyan, 100)
            pygame.draw.circle(glow_surf, glow_color, 
                             (int(particle['size'] * 2), int(particle['size'] * 2)), 
                             int(particle['size'] * 2))
            surface.blit(glow_surf, (particle['x'] - particle['size'] * 2, particle['y'] - particle['size'] * 2))
            
            # Draw core
            pygame.draw.circle(surface, self.accent_cyan, 
                             (int(particle['x']), int(particle['y'])), 
                             int(particle['size']))
    
    def draw_shapes(self, surface):
        """Draw background geometric shapes"""
        for shape in self.shapes:
            self.draw_shape(surface, shape['type'], shape['x'], shape['y'], 
                          shape['size'], shape['rotation'], shape['color'])
    
    def draw_title(self, surface):
        """Draw the title text"""
        font_large = pygame.font.Font(None, 72)
        font_medium = pygame.font.Font(None, 36)
        
        # Main title with glow
        title_text = "ENTER YOUR INITIALS"
        title_surf = font_large.render(title_text, True, self.white)
        title_rect = title_surf.get_rect(center=(WIDTH // 2, 150))
        
        # Draw glow
        for offset in range(5, 0, -1):
            glow_surf = font_large.render(title_text, True, self.purple_bright)
            glow_rect = glow_surf.get_rect(center=(WIDTH // 2, 150))
            glow_surface = pygame.Surface((glow_surf.get_width() + offset*4, 
                                         glow_surf.get_height() + offset*4), pygame.SRCALPHA)
            glow_surface.fill((*self.purple_bright, 50 // offset))
            surface.blit(glow_surface, (glow_rect.x - offset*2, glow_rect.y - offset*2), 
                        special_flags=pygame.BLEND_ADD)
        
        surface.blit(title_surf, title_rect)
        
        # Score display
        score_text = f"FINAL SCORE: {self.score:,}"
        score_surf = font_medium.render(score_text, True, self.accent_pink)
        score_rect = score_surf.get_rect(center=(WIDTH // 2, 220))
        surface.blit(score_surf, score_rect)
    
    def draw_input_box(self, surface):
        """Draw the initials input box"""
        box_width = 300
        box_height = 80
        box_x = WIDTH // 2 - box_width // 2
        box_y = HEIGHT // 2 - box_height // 2
        
        # Draw box background
        box_surf = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        pygame.draw.rect(box_surf, (*self.purple_dark, 180), (0, 0, box_width, box_height))
        pygame.draw.rect(box_surf, self.purple_bright, (0, 0, box_width, box_height), 3)
        surface.blit(box_surf, (box_x, box_y))
        
        # Draw initials
        font_huge = pygame.font.Font(None, 64)
        display_text = self.initials + ('_' if self.cursor_visible and len(self.initials) < 3 else '')
        text_surf = font_huge.render(display_text, True, self.white)
        text_rect = text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        surface.blit(text_surf, text_rect)
        
        # Draw character slots
        slot_y = box_y + box_height + 20
        slot_size = 60
        slot_spacing = 80
        start_x = WIDTH // 2 - (3 * slot_spacing - (slot_spacing - slot_size)) // 2
        
        for i in range(3):
            slot_x = start_x + i * slot_spacing
            color = self.accent_pink if i < len(self.initials) else self.purple_light
            pygame.draw.rect(surface, color, (slot_x, slot_y, slot_size, 5))
    
    def draw_instructions(self, surface):
        """Draw instructions at the bottom"""
        font_small = pygame.font.Font(None, 28)
        
        instructions = [
            "Type 3 letters for your initials",
            "Press ENTER when done"
        ]
        
        y_start = HEIGHT - 150
        for i, instruction in enumerate(instructions):
            text_surf = font_small.render(instruction, True, self.purple_light)
            text_rect = text_surf.get_rect(center=(WIDTH // 2, y_start + i * 30))
            surface.blit(text_surf, text_rect)
    
    def draw(self, surface):
        """Draw the complete purple initials screen"""
        self.update()
        
        # Draw background
        self.draw_gradient_background(surface)
        
        # Draw decorative elements
        self.draw_shapes(surface)
        self.draw_particles(surface)
        
        # Draw dashboard frame
        self.draw_dashboard_frame(surface)
        
        # Draw content
        self.draw_title(surface)
        self.draw_input_box(surface)
        self.draw_instructions(surface)


class CleanHighScoresScreen:
    """Clean high scores display screen"""
    def __init__(self, score, high_scores):
        self.score = score
        self.high_scores = high_scores
        self.frame = 0
        self.timer = 0  # Timer to track 10 seconds
        self.can_continue = False  # Can press ENTER after 10 seconds
        
        # Color palette
        self.bg_color = (20, 10, 40)  # Dark purple background
        self.title_color = (255, 200, 100)  # Gold for title
        self.score_color = (100, 255, 255)  # Cyan for scores
        self.highlight_color = (255, 100, 200)  # Pink for player's score
        self.text_color = (200, 200, 255)  # Light purple for text
        
        # Starfield background
        self.stars = []
        for _ in range(200):
            self.stars.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(0, HEIGHT),
                'brightness': random.randint(50, 255),
                'twinkle_speed': random.uniform(0.02, 0.05)
            })
    
    def update(self):
        """Update animations and timer"""
        self.frame += 1
        self.timer += 1
        
        # After 10 seconds (600 frames at 60fps), allow continuing
        if self.timer >= 600:
            self.can_continue = True
        
        # Update star twinkle
        for star in self.stars:
            star['brightness'] = 128 + 127 * math.sin(self.frame * star['twinkle_speed'])
    
    def draw_stars(self, surface):
        """Draw twinkling starfield"""
        for star in self.stars:
            brightness = int(star['brightness'])
            color = (brightness, brightness, brightness)
            pygame.draw.circle(surface, color, (star['x'], star['y']), 1)
    
    def draw_title(self, surface):
        """Draw the HIGH SCORES title"""
        font_title = pygame.font.Font(None, 96)
        
        # Draw title with glow effect
        title_text = "HIGH SCORES"
        
        # Glow layers
        for offset in range(10, 0, -2):
            glow_alpha = 30 // (offset // 2)
            glow_surf = font_title.render(title_text, True, self.title_color)
            glow_rect = glow_surf.get_rect(center=(WIDTH // 2, 100))
            
            glow_surface = pygame.Surface((glow_surf.get_width() + offset*4, 
                                         glow_surf.get_height() + offset*4), pygame.SRCALPHA)
            glow_surface.fill((*self.title_color, glow_alpha))
            surface.blit(glow_surface, (glow_rect.x - offset*2, glow_rect.y - offset*2), 
                        special_flags=pygame.BLEND_ADD)
        
        # Main title
        title_surf = font_title.render(title_text, True, self.title_color)
        title_rect = title_surf.get_rect(center=(WIDTH // 2, 100))
        surface.blit(title_surf, title_rect)
    
    def draw_scores(self, surface):
        """Draw the high scores list"""
        font_score = pygame.font.Font(None, 48)
        font_rank = pygame.font.Font(None, 36)
        
        # Starting position for scores
        y_start = 200
        line_height = 45
        
        # Draw top 10 scores
        for i, entry in enumerate(self.high_scores[:10]):
            y_pos = y_start + i * line_height
            
            # Check if this is the player's score
            is_player_score = entry.get('score') == self.score and i < 10
            
            # Choose color
            if i == 0:
                color = (255, 215, 0)  # Gold for 1st
            elif i == 1:
                color = (192, 192, 192)  # Silver for 2nd
            elif i == 2:
                color = (205, 127, 50)  # Bronze for 3rd
            elif is_player_score:
                color = self.highlight_color  # Highlight player's score
            else:
                color = self.score_color
            
            # Draw rank
            rank_text = f"{i + 1}."
            rank_surf = font_rank.render(rank_text, True, color)
            surface.blit(rank_surf, (200, y_pos))
            
            # Draw initials
            initials_text = entry.get('initials', '???')
            initials_surf = font_score.render(initials_text, True, color)
            surface.blit(initials_surf, (280, y_pos - 5))
            
            # Draw score
            score_text = f"{entry.get('score', 0):,}"
            score_surf = font_score.render(score_text, True, color)
            score_rect = score_surf.get_rect(right=WIDTH - 200)
            score_rect.y = y_pos - 5
            surface.blit(score_surf, score_rect)
            
            # Add pulsing effect for player's score
            if is_player_score:
                pulse = math.sin(self.frame * 0.1) * 0.3 + 0.7
                overlay = pygame.Surface((WIDTH - 400, line_height), pygame.SRCALPHA)
                overlay.fill((*self.highlight_color, int(30 * pulse)))
                surface.blit(overlay, (200, y_pos - 5), special_flags=pygame.BLEND_ADD)
    
    def draw_continue_prompt(self, surface):
        """Draw the continue prompt"""
        font_prompt = pygame.font.Font(None, 36)
        
        if self.can_continue:
            # Pulsing effect for prompt
            pulse = math.sin(self.frame * 0.05) * 0.3 + 0.7
            prompt_color = tuple(int(c * pulse) for c in self.text_color)
            
            prompt_text = "Press ENTER to play again"
            prompt_surf = font_prompt.render(prompt_text, True, prompt_color)
            prompt_rect = prompt_surf.get_rect(center=(WIDTH // 2, HEIGHT - 80))
            surface.blit(prompt_surf, prompt_rect)
        else:
            # Show countdown
            seconds_left = max(0, 10 - self.timer // 60)
            countdown_text = f"Continue in {seconds_left}..."
            countdown_surf = font_prompt.render(countdown_text, True, self.text_color)
            countdown_rect = countdown_surf.get_rect(center=(WIDTH // 2, HEIGHT - 80))
            surface.blit(countdown_surf, countdown_rect)
    
    def draw(self, surface):
        """Draw the complete high scores screen"""
        # Clear screen
        surface.fill(self.bg_color)
        
        # Draw background
        self.draw_stars(surface)
        
        # Draw content
        self.draw_title(surface)
        self.draw_scores(surface)
        self.draw_continue_prompt(surface)
        
        # Update animations
        self.update()

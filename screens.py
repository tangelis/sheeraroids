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
            self.draw_neon_text(surface, f"Continue in {remaining}...", 28, self.neon_orange, WIDTH//2, HEIGHT - 60, glow=False)
        else:
            self.draw_neon_text(surface, "PRESS ENTER TO CONTINUE", 28, self.neon_orange, WIDTH//2, HEIGHT - 60, glow=False)
        
        # Update frame counter
        self.update()


class ModernHighScoresScreen:
    """Modern high scores display screen with riddle system"""
    def __init__(self, high_score_manager, player_score, wrong_answer_sound=None):
        self.high_score_manager = high_score_manager
        self.player_score = player_score
        self.wrong_answer_sound = wrong_answer_sound
        self.animation_time = 0
        self.particles = []
        self.done = False  # ONLY set to True when riddle is solved correctly
        self.scroll_offset = 0
        self.scroll_speed = 2
        self.auto_scroll = True
        self.total_height = 0  # Will calculate based on scores
        self.visible_start = 200  # Where scores start being visible
        self.visible_end = HEIGHT - 100  # Where scores stop being visible
        
        # Riddle system
        self.riddle_active = False
        self.riddle_timer = 0
        self.riddle_answer = ""
        self.riddle_correct = False
        self.wrong_answer_shake = 0
        self.cursor_visible = True
        self.cursor_timer = 0
        
        # Modern color palette
        self.primary_color = (100, 200, 255)  # Soft blue
        self.accent_color = (255, 100, 150)   # Soft pink
        self.gold_color = (255, 215, 0)       # Gold for top 3
        self.silver_color = (192, 192, 192)   # Silver
        self.bronze_color = (205, 127, 50)    # Bronze
        self.bg_gradient_top = (20, 25, 40)   # Dark blue
        self.bg_gradient_bottom = (40, 20, 60) # Dark purple
        
        # Generate floating particles
        for _ in range(20):
            self.particles.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(0, HEIGHT),
                'size': random.randint(1, 3),
                'speed': random.uniform(0.5, 1.5),
                'opacity': random.randint(50, 150)
            })
    
    def handle_input(self, event):
        """Handle input - riddle system"""
        if event.type == pygame.KEYDOWN:
            # First check if we need to activate riddle
            if not self.riddle_active and self.auto_scroll:
                if event.key == pygame.K_RETURN:
                    # ENTER activates the riddle
                    self.riddle_active = True
                    self.auto_scroll = False
                # Ignore all other keys while scrolling
                return
            
            # Only handle input if riddle is active
            elif self.riddle_active:
                # Handle riddle input
                if event.key == pygame.K_BACKSPACE:
                    if len(self.riddle_answer) > 0:
                        self.riddle_answer = self.riddle_answer[:-1]
                elif event.key == pygame.K_RETURN:
                    # Only process if there's an answer
                    if self.riddle_answer.strip():  # Check for non-empty answer
                        # Check answer - ONLY accept "seven" or "7"
                        if self.riddle_answer.lower().strip() == "seven" or self.riddle_answer.strip() == "7":
                            self.riddle_correct = True
                            self.done = True
                        else:
                            # Wrong answer - shake and reset
                            self.wrong_answer_shake = 30
                            self.riddle_answer = ""
                            # Explicitly ensure we're not done
                            self.done = False
                            self.riddle_correct = False
                            # Play wrong answer sound
                            if self.wrong_answer_sound:
                                self.wrong_answer_sound.play()
                else:
                    # Add typed character
                    if event.unicode and len(self.riddle_answer) < 10:
                        self.riddle_answer += event.unicode
    
    def draw_gradient_background(self, surface):
        """Draw gradient background"""
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(self.bg_gradient_top[0] * (1 - ratio) + self.bg_gradient_bottom[0] * ratio)
            g = int(self.bg_gradient_top[1] * (1 - ratio) + self.bg_gradient_bottom[1] * ratio)
            b = int(self.bg_gradient_top[2] * (1 - ratio) + self.bg_gradient_bottom[2] * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))
    
    def draw_floating_particles(self, surface):
        """Draw floating particles"""
        for particle in self.particles:
            particle['y'] -= particle['speed']
            if particle['y'] < -10:
                particle['y'] = HEIGHT + 10
                particle['x'] = random.randint(0, WIDTH)
            
            # Draw particle
            alpha_surface = pygame.Surface((particle['size'] * 4, particle['size'] * 4), pygame.SRCALPHA)
            pygame.draw.circle(alpha_surface, (*self.primary_color, particle['opacity']//2), 
                             (particle['size'] * 2, particle['size'] * 2), particle['size'] * 2)
            surface.blit(alpha_surface, (particle['x'] - particle['size'] * 2, particle['y'] - particle['size'] * 2))
    
    def get_rank_color(self, rank):
        """Get color based on rank"""
        if rank == 1:
            return self.gold_color
        elif rank == 2:
            return self.silver_color
        elif rank == 3:
            return self.bronze_color
        else:
            return WHITE
    
    def draw(self, surface):
        """Draw the high scores screen"""
        self.animation_time += 1
        self.cursor_timer += 1
        
        # Toggle cursor visibility every 30 frames
        if self.cursor_timer >= 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
        
        # Calculate total height needed for all scores (20 scores * 40 pixels each)
        scores = self.high_score_manager.get_high_scores()
        self.total_height = len(scores[:20]) * 40 + 100  # Extra padding
        
        # Update scrolling
        if self.auto_scroll:
            self.scroll_offset += self.scroll_speed
            
            # Loop scrolling - when we've scrolled through all scores, start over
            if self.scroll_offset > self.total_height:
                self.scroll_offset = -200  # Start from below visible area
        
        # Update wrong answer shake
        if self.wrong_answer_shake > 0:
            self.wrong_answer_shake -= 1
        
        # Draw background
        self.draw_gradient_background(surface)
        self.draw_floating_particles(surface)
        
        # Fonts
        title_font = pygame.font.Font(None, 64)
        header_font = pygame.font.Font(None, 36)
        score_font = pygame.font.Font(None, 32)
        instruction_font = pygame.font.Font(None, 28)
        
        # Title
        title_text = title_font.render("HIGH SCORES", True, WHITE)
        title_rect = title_text.get_rect(center=(WIDTH//2, 80))
        
        # Title glow effect
        for offset in [(2, 2), (-2, 2), (2, -2), (-2, -2)]:
            glow_surface = title_font.render("HIGH SCORES", True, self.accent_color)
            glow_rect = glow_surface.get_rect(center=(WIDTH//2 + offset[0], 80 + offset[1]))
            glow_surface.set_alpha(50)
            surface.blit(glow_surface, glow_rect)
        
        surface.blit(title_text, title_rect)
        
        # Score table background
        table_surface = pygame.Surface((600, 450), pygame.SRCALPHA)
        pygame.draw.rect(table_surface, (255, 255, 255, 20), (0, 0, 600, 450), border_radius=20)
        pygame.draw.rect(table_surface, (255, 255, 255, 40), (0, 0, 600, 450), 3, border_radius=20)
        table_rect = table_surface.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))
        surface.blit(table_surface, table_rect)
        
        # Table headers (draw before clipping)
        headers = ["RANK", "NAME", "SCORE"]
        header_x_positions = [WIDTH//2 - 200, WIDTH//2, WIDTH//2 + 200]
        
        for i, (header, x) in enumerate(zip(headers, header_x_positions)):
            header_text = header_font.render(header, True, self.primary_color)
            header_rect = header_text.get_rect(center=(x, 170))
            surface.blit(header_text, header_rect)
        
        # Create clipping area for scrolling scores
        clip_rect = pygame.Rect(WIDTH//2 - 300, 200, 600, 360)
        surface.set_clip(clip_rect)
        
        # Draw scores with scrolling
        scores = self.high_score_manager.get_high_scores()
        start_y = 220 - int(self.scroll_offset)
        
        # Draw all 20 scores (draw twice for seamless looping)
        all_scores = scores[:20] + scores[:20]  # Duplicate for continuous scroll
        
        for i, score_entry in enumerate(all_scores):
            y = start_y + i * 40
            # Use modulo to get correct rank for duplicated scores
            rank = (i % 20) + 1
            color = self.get_rank_color(rank)
            
            # Highlight player's score with pulse effect
            if score_entry['score'] == self.player_score:
                pulse = abs(math.sin(self.animation_time * 0.05))
                highlight_surface = pygame.Surface((550, 35), pygame.SRCALPHA)
                pygame.draw.rect(highlight_surface, (*self.accent_color, int(100 * pulse)), 
                               (0, 0, 550, 35), border_radius=10)
                highlight_rect = highlight_surface.get_rect(center=(WIDTH//2, y))
                surface.blit(highlight_surface, highlight_rect)
            
            # Rank
            rank_text = score_font.render(str(rank), True, color)
            rank_rect = rank_text.get_rect(center=(header_x_positions[0], y))
            surface.blit(rank_text, rank_rect)
            
            # Add medal icon for top 3
            if rank <= 3:
                medal_radius = 12
                medal_x = header_x_positions[0] - 40
                pygame.draw.circle(surface, color, (medal_x, y), medal_radius)
                pygame.draw.circle(surface, (255, 255, 255, 100), (medal_x, y), medal_radius, 2)
            
            # Name
            name_text = score_font.render(score_entry['initials'], True, color)
            name_rect = name_text.get_rect(center=(header_x_positions[1], y))
            surface.blit(name_text, name_rect)
            
            # Score
            score_text = score_font.render(f"{score_entry['score']:,}", True, color)
            score_rect = score_text.get_rect(center=(header_x_positions[2], y))
            surface.blit(score_text, score_rect)
        
        # Reset clipping
        surface.set_clip(None)
        
        # Draw riddle overlay if active
        if self.riddle_active:
            # Darken background
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, 0))
            
            # Riddle box
            riddle_width = 600
            riddle_height = 300
            riddle_x = WIDTH//2 - riddle_width//2
            riddle_y = HEIGHT//2 - riddle_height//2
            
            # Apply shake effect if wrong answer
            if self.wrong_answer_shake > 0:
                shake_x = random.randint(-5, 5) * (self.wrong_answer_shake // 5)
                riddle_x += shake_x
            
            # Draw riddle background
            riddle_surface = pygame.Surface((riddle_width, riddle_height), pygame.SRCALPHA)
            pygame.draw.rect(riddle_surface, (20, 20, 40, 240), (0, 0, riddle_width, riddle_height), border_radius=20)
            pygame.draw.rect(riddle_surface, self.accent_color, (0, 0, riddle_width, riddle_height), 3, border_radius=20)
            surface.blit(riddle_surface, (riddle_x, riddle_y))
            
            # Riddle title
            riddle_title = title_font.render("SOLVE TO CONTINUE", True, self.accent_color)
            title_rect = riddle_title.get_rect(center=(WIDTH//2, riddle_y + 60))
            surface.blit(riddle_title, title_rect)
            
            # Riddle question
            question_font = pygame.font.Font(None, 42)
            question = question_font.render("What is the sum of three and four?", True, WHITE)
            question_rect = question.get_rect(center=(WIDTH//2, riddle_y + 120))
            surface.blit(question, question_rect)
            
            # Answer input field
            input_width = 300
            input_height = 50
            input_x = WIDTH//2 - input_width//2
            input_y = riddle_y + 180
            
            # Make input field more visible with solid background
            pygame.draw.rect(surface, (40, 40, 60), (input_x, input_y, input_width, input_height), border_radius=10)
            pygame.draw.rect(surface, self.primary_color, (input_x, input_y, input_width, input_height), 3, border_radius=10)
            
            # Draw answer text or placeholder
            answer_font = pygame.font.Font(None, 36)
            if self.riddle_answer:
                answer_text = answer_font.render(self.riddle_answer, True, WHITE)
                answer_rect = answer_text.get_rect(midleft=(input_x + 15, input_y + input_height//2))
                surface.blit(answer_text, answer_rect)
                cursor_x = answer_rect.right + 5
            else:
                # Show placeholder text
                placeholder = answer_font.render("Type answer...", True, (100, 100, 100))
                placeholder_rect = placeholder.get_rect(midleft=(input_x + 15, input_y + input_height//2))
                surface.blit(placeholder, placeholder_rect)
                cursor_x = input_x + 15
            
            # Draw blinking cursor
            if self.cursor_visible:
                cursor_rect = pygame.Rect(cursor_x, input_y + 10, 3, input_height - 20)
                pygame.draw.rect(surface, WHITE, cursor_rect)
            
            # Instructions
            hint_font = pygame.font.Font(None, 28)
            hint = hint_font.render("Type your answer and press ENTER", True, (200, 200, 200))
            hint_rect = hint.get_rect(center=(WIDTH//2, riddle_y + 250))
            surface.blit(hint, hint_rect)
            
            # Show wrong answer feedback
            if self.wrong_answer_shake > 0:
                error_text = hint_font.render("Wrong! Try again!", True, (255, 100, 100))
                error_rect = error_text.get_rect(center=(WIDTH//2, riddle_y + 280))
                surface.blit(error_text, error_rect)
                
            # Debug: Show what answers are accepted
            debug_font = pygame.font.Font(None, 20)
            debug_text = debug_font.render("(Type 'seven' or '7')", True, (150, 150, 150))
            debug_rect = debug_text.get_rect(center=(WIDTH//2, riddle_y + 310))
            surface.blit(debug_text, debug_rect)
        else:
            # Normal instructions at bottom
            instruction = instruction_font.render("Press ENTER to continue", True, self.accent_color)
            instruction_rect = instruction.get_rect(center=(WIDTH//2, HEIGHT - 40))
            surface.blit(instruction, instruction_rect)
            
            # Add pulsing effect to make it more visible
            if self.animation_time % 60 < 30:
                glow = instruction_font.render("Press ENTER to continue", True, WHITE)
                glow_rect = glow.get_rect(center=(WIDTH//2, HEIGHT - 40))
                glow.set_alpha(100)
                surface.blit(glow, glow_rect)


class CorrectAnswerAnimation:
    """Cool animation screen shown after correct riddle answer"""
    def __init__(self):
        self.animation_time = 0
        self.done = False
        self.particles = []
        self.rings = []
        self.text_scale = 0
        
        # Colors
        self.gold = (255, 215, 0)
        self.bright_green = (0, 255, 100)
        self.electric_blue = (0, 150, 255)
        self.purple = (150, 0, 255)
        
        # Create celebration particles
        for _ in range(100):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(5, 15)
            self.particles.append({
                'x': WIDTH // 2,
                'y': HEIGHT // 2,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'color': random.choice([self.gold, self.bright_green, self.electric_blue, self.purple]),
                'size': random.randint(3, 8),
                'lifetime': random.randint(60, 120)
            })
    
    def update(self):
        """Update animation"""
        self.animation_time += 1
        
        # Update particles
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.3  # Gravity
            particle['lifetime'] -= 1
            particle['size'] = max(1, particle['size'] - 0.1)
            
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
        
        # Create expanding rings
        if self.animation_time % 20 == 0 and self.animation_time < 100:
            self.rings.append({
                'radius': 10,
                'alpha': 255,
                'color': random.choice([self.gold, self.bright_green, self.electric_blue])
            })
        
        # Update rings
        for ring in self.rings[:]:
            ring['radius'] += 8
            ring['alpha'] -= 5
            if ring['alpha'] <= 0:
                self.rings.remove(ring)
        
        # Update text scale
        if self.text_scale < 1:
            self.text_scale += 0.05
        
        # End animation after 3 seconds
        if self.animation_time > 180:
            self.done = True
    
    def draw(self, surface):
        """Draw the celebration animation"""
        self.update()
        
        # Animated gradient background
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            offset = math.sin(self.animation_time * 0.02 + y * 0.01) * 20
            r = int(20 + offset + ratio * 40)
            g = int(25 + offset + ratio * 45)
            b = int(40 + offset + ratio * 60)
            pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))
        
        # Draw expanding rings
        for ring in self.rings:
            ring_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(ring_surface, (*ring['color'], ring['alpha']), 
                             (WIDTH//2, HEIGHT//2), ring['radius'], 3)
            surface.blit(ring_surface, (0, 0))
        
        # Draw particles
        for particle in self.particles:
            glow_surface = pygame.Surface((particle['size'] * 4, particle['size'] * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*particle['color'], 100), 
                             (particle['size'] * 2, particle['size'] * 2), particle['size'] * 2)
            pygame.draw.circle(glow_surface, particle['color'], 
                             (particle['size'] * 2, particle['size'] * 2), particle['size'])
            surface.blit(glow_surface, (particle['x'] - particle['size'] * 2, particle['y'] - particle['size'] * 2))
        
        # Draw success text with scaling animation
        font_size = int(72 * self.text_scale)
        if font_size > 0:
            success_font = pygame.font.Font(None, font_size)
            
            # Main text with glow
            texts = ["CORRECT!", "GET READY!"]
            y_positions = [HEIGHT//2 - 50, HEIGHT//2 + 20]
            
            for text, y in zip(texts, y_positions):
                # Glow effect
                for offset in [(3, 3), (-3, 3), (3, -3), (-3, -3)]:
                    glow_text = success_font.render(text, True, self.gold)
                    glow_rect = glow_text.get_rect(center=(WIDTH//2 + offset[0], y + offset[1]))
                    glow_surface = pygame.Surface(glow_text.get_size(), pygame.SRCALPHA)
                    glow_surface.blit(glow_text, (0, 0))
                    glow_surface.set_alpha(100)
                    surface.blit(glow_surface, glow_rect)
                
                # Main text
                main_text = success_font.render(text, True, WHITE)
                main_rect = main_text.get_rect(center=(WIDTH//2, y))
                surface.blit(main_text, main_rect)
        
        # Countdown text
        if self.animation_time > 60:
            countdown = max(0, 3 - (self.animation_time - 60) // 60)
            if countdown > 0:
                countdown_font = pygame.font.Font(None, 48)
                countdown_text = countdown_font.render(f"Starting in {countdown}...", True, (200, 200, 200))
                countdown_rect = countdown_text.get_rect(center=(WIDTH//2, HEIGHT - 100))
                surface.blit(countdown_text, countdown_rect)
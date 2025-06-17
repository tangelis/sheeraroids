"""
High score management system with local storage and Supabase-ready structure
"""
import pygame
import math
import json
import os
from datetime import datetime
from constants import WIDTH, HEIGHT, WHITE, BLACK, GREEN, screen

class HighScoreManager:
    def __init__(self):
        self.scores_file = "high_scores.json"
        self.backup_file = "high_scores_backup.json"
        self.high_scores = self.load_scores()
        
        # Supabase-ready configuration (for future integration)
        self.supabase_config = {
            "table_name": "high_scores",
            "columns": ["id", "name", "score", "game_mode", "created_at", "device_id"]
        }
    
    def load_scores(self):
        """Load high scores from local file with Supabase-ready structure"""
        try:
            if os.path.exists(self.scores_file):
                with open(self.scores_file, 'r') as f:
                    data = json.load(f)
                    # Handle both old and new formats
                    if isinstance(data, list) and len(data) > 0:
                        if "created_at" in data[0]:
                            # New format
                            return data
                        else:
                            # Convert old format to new
                            return self._convert_to_new_format(data)
            else:
                # Default high scores with new structure
                return self._create_default_scores()
        except Exception as e:
            print(f"Error loading high scores: {e}")
            # Try backup file
            if os.path.exists(self.backup_file):
                try:
                    with open(self.backup_file, 'r') as f:
                        return json.load(f)
                except:
                    pass
            return self._create_default_scores()
    
    def _convert_to_new_format(self, old_scores):
        """Convert old format to Supabase-ready format"""
        new_scores = []
        for i, score in enumerate(old_scores):
            new_scores.append({
                "id": i + 1,
                "name": score.get("initials", "???"),
                "score": score.get("score", 0),
                "game_mode": "normal",
                "created_at": datetime.now().isoformat(),
                "device_id": "legacy"
            })
        return new_scores
    
    def _create_default_scores(self):
        """Create default high scores with new structure"""
        defaults = [
            ("ACE", 1000), ("MAX", 950), ("ZAP", 900), ("BOB", 850),
            ("JOE", 800), ("SUE", 750), ("TOM", 700), ("ANN", 650),
            ("DAN", 600), ("KIM", 550), ("REX", 500), ("LEO", 450),
            ("SAM", 400), ("EVE", 350), ("JAX", 300), ("LIZ", 250),
            ("RAY", 200), ("MEG", 150), ("BEN", 100), ("ZOE", 50)
        ]
        return [
            {
                "id": i + 1,
                "name": name,
                "score": score,
                "game_mode": "normal",
                "created_at": datetime.now().isoformat(),
                "device_id": "default"
            }
            for i, (name, score) in enumerate(defaults)
        ]
    
    def save_scores(self):
        """Save high scores to local file with backup"""
        try:
            # Create backup first
            if os.path.exists(self.scores_file):
                with open(self.scores_file, 'r') as f:
                    backup_data = f.read()
                with open(self.backup_file, 'w') as f:
                    f.write(backup_data)
            
            # Save new scores
            with open(self.scores_file, 'w') as f:
                json.dump(self.high_scores, f, indent=2)
            print(f"High scores saved to {self.scores_file}")
            
            # Log for future Supabase sync
            self._log_for_sync()
        except Exception as e:
            print(f"Error saving high scores: {e}")
    
    def _log_for_sync(self):
        """Create a log file for future Supabase synchronization"""
        sync_file = "high_scores_sync.json"
        try:
            sync_data = {
                "last_local_update": datetime.now().isoformat(),
                "pending_sync": True,
                "scores_count": len(self.high_scores)
            }
            with open(sync_file, 'w') as f:
                json.dump(sync_data, f, indent=2)
        except:
            pass
    
    def is_high_score(self, score):
        """Check if score qualifies for high score table"""
        return len(self.high_scores) < 20 or score > self.high_scores[-1]["score"]
    
    def add_score(self, name, score, game_mode="normal"):
        """Add new score with Supabase-ready structure"""
        # Generate unique ID (timestamp-based for local storage)
        new_id = int(datetime.now().timestamp() * 1000)
        
        new_entry = {
            "id": new_id,
            "name": name.strip()[:3],  # Ensure 3 characters
            "score": score,
            "game_mode": game_mode,
            "created_at": datetime.now().isoformat(),
            "device_id": self._get_device_id()
        }
        
        self.high_scores.append(new_entry)
        self.high_scores.sort(key=lambda x: x["score"], reverse=True)
        self.high_scores = self.high_scores[:20]  # Keep top 20
        self.save_scores()  # Save to file immediately
    
    def _get_device_id(self):
        """Generate a unique device ID for this installation"""
        device_file = ".device_id"
        if os.path.exists(device_file):
            with open(device_file, 'r') as f:
                return f.read().strip()
        else:
            # Generate new device ID
            import uuid
            device_id = str(uuid.uuid4())
            with open(device_file, 'w') as f:
                f.write(device_id)
            return device_id
    
    def get_high_scores(self):
        """Get sorted high scores (compatible with old format)"""
        # Return in old format for compatibility
        return [
            {
                "initials": score["name"],
                "score": score["score"]
            }
            for score in self.high_scores
        ]
    
    def get_full_high_scores(self):
        """Get high scores with full Supabase-ready data"""
        return self.high_scores

class HighScoreEntry:
    def __init__(self, score, high_score_manager, game_mode="normal"):
        self.score = score
        self.high_score_manager = high_score_manager
        self.game_mode = game_mode
        self.name = ""  # Changed from initials array to string
        self.max_length = 3  # Exactly 3 characters
        self.done = False
        self.animation_time = 0
        self.particles = []
        self.cursor_visible = True
        self.cursor_timer = 0
        
        # Modern color palette
        self.primary_color = (100, 200, 255)  # Soft blue
        self.accent_color = (255, 100, 150)   # Soft pink
        self.bg_gradient_top = (20, 25, 40)   # Dark blue
        self.bg_gradient_bottom = (40, 20, 60) # Dark purple
        
        # Generate floating particles for background
        for _ in range(30):
            self.particles.append({
                'x': pygame.time.get_ticks() % WIDTH,
                'y': pygame.time.get_ticks() % HEIGHT,
                'size': pygame.time.get_ticks() % 3 + 1,
                'speed': (pygame.time.get_ticks() % 10 + 5) / 10,
                'opacity': pygame.time.get_ticks() % 128 + 50
            })
    
    def handle_input(self, event):
        """Handle modern text input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # Submit name (require exactly 3 characters)
                if len(self.name) == 3:
                    initials = self.name.upper()
                    self.high_score_manager.add_score(initials, self.score, self.game_mode)
                    self.done = True
            elif event.key == pygame.K_BACKSPACE:
                # Delete last character
                if len(self.name) > 0:
                    self.name = self.name[:-1]
            else:
                # Add typed character if it's a letter or space
                if event.unicode and len(self.name) < self.max_length:
                    char = event.unicode
                    if char.isalpha() or char == ' ':
                        self.name += char.upper()
    
    def draw_gradient_background(self, surface):
        """Draw a modern gradient background"""
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(self.bg_gradient_top[0] * (1 - ratio) + self.bg_gradient_bottom[0] * ratio)
            g = int(self.bg_gradient_top[1] * (1 - ratio) + self.bg_gradient_bottom[1] * ratio)
            b = int(self.bg_gradient_top[2] * (1 - ratio) + self.bg_gradient_bottom[2] * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))
    
    def draw_floating_particles(self, surface):
        """Draw subtle floating particles in background"""
        for particle in self.particles:
            particle['y'] -= particle['speed']
            if particle['y'] < -10:
                particle['y'] = HEIGHT + 10
                particle['x'] = pygame.time.get_ticks() % WIDTH
            
            # Draw particle with glow effect
            alpha_surface = pygame.Surface((particle['size'] * 4, particle['size'] * 4), pygame.SRCALPHA)
            pygame.draw.circle(alpha_surface, (*self.primary_color, particle['opacity']//2), 
                             (particle['size'] * 2, particle['size'] * 2), particle['size'] * 2)
            pygame.draw.circle(alpha_surface, (*self.primary_color, particle['opacity']), 
                             (particle['size'] * 2, particle['size'] * 2), particle['size'])
            surface.blit(alpha_surface, (particle['x'] - particle['size'] * 2, particle['y'] - particle['size'] * 2))
    
    def draw(self, surface):
        """Draw the modern initial entry screen"""
        self.animation_time += 1
        self.cursor_timer += 1
        
        # Toggle cursor visibility every 30 frames
        if self.cursor_timer >= 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
        
        # Draw gradient background
        self.draw_gradient_background(surface)
        
        # Draw floating particles
        self.draw_floating_particles(surface)
        
        # Create fonts with better sizing
        title_font = pygame.font.Font(None, 72)
        score_font = pygame.font.Font(None, 56)
        instruction_font = pygame.font.Font(None, 36)
        input_font = pygame.font.Font(None, 48)
        control_font = pygame.font.Font(None, 28)
        
        # Draw semi-transparent card background
        card_rect = pygame.Rect(WIDTH//2 - 300, 100, 600, 500)
        card_surface = pygame.Surface((600, 500), pygame.SRCALPHA)
        pygame.draw.rect(card_surface, (255, 255, 255, 20), (0, 0, 600, 500), border_radius=20)
        pygame.draw.rect(card_surface, (255, 255, 255, 40), (0, 0, 600, 500), 3, border_radius=20)
        surface.blit(card_surface, card_rect)
        
        # Title with glow effect
        title_glow = title_font.render("NEW HIGH SCORE", True, self.accent_color)
        for offset in [(2, 2), (-2, 2), (2, -2), (-2, -2)]:
            title_rect = title_glow.get_rect(center=(WIDTH//2 + offset[0], 180 + offset[1]))
            title_surface = pygame.Surface(title_glow.get_size(), pygame.SRCALPHA)
            title_surface.blit(title_glow, (0, 0))
            title_surface.set_alpha(50)
            surface.blit(title_surface, title_rect)
        
        title_text = title_font.render("NEW HIGH SCORE", True, WHITE)
        title_rect = title_text.get_rect(center=(WIDTH//2, 180))
        surface.blit(title_text, title_rect)
        
        # Score with animated pulse
        pulse = math.sin(self.animation_time * 0.05) * 0.1 + 1
        score_surface = pygame.Surface((400, 100), pygame.SRCALPHA)
        score_text = score_font.render(f"{self.score:,}", True, self.primary_color)
        score_rect = score_text.get_rect(center=(200, 50))
        score_surface.blit(score_text, score_rect)
        
        scaled_size = (int(400 * pulse), int(100 * pulse))
        scaled_surface = pygame.transform.smoothscale(score_surface, scaled_size)
        scaled_rect = scaled_surface.get_rect(center=(WIDTH//2, 260))
        surface.blit(scaled_surface, scaled_rect)
        
        # Modern instruction text
        inst_text = instruction_font.render("Enter 3 characters", True, (200, 200, 200))
        inst_rect = inst_text.get_rect(center=(WIDTH//2, 340))
        surface.blit(inst_text, inst_rect)
        
        # Text input field
        input_width = 400
        input_height = 60
        input_x = WIDTH//2 - input_width//2
        input_y = 380
        
        # Draw input field background
        input_rect = pygame.Rect(input_x, input_y, input_width, input_height)
        input_surface = pygame.Surface((input_width, input_height), pygame.SRCALPHA)
        pygame.draw.rect(input_surface, (255, 255, 255, 30), (0, 0, input_width, input_height), border_radius=10)
        pygame.draw.rect(input_surface, self.primary_color, (0, 0, input_width, input_height), 2, border_radius=10)
        surface.blit(input_surface, input_rect)
        
        # Draw typed text
        if self.name:
            text_surface = input_font.render(self.name, True, WHITE)
            text_rect = text_surface.get_rect(midleft=(input_x + 20, input_y + input_height//2))
            surface.blit(text_surface, text_rect)
            cursor_x = text_rect.right + 5
        else:
            # Show placeholder text
            placeholder = input_font.render("Enter name...", True, (150, 150, 150))
            placeholder_rect = placeholder.get_rect(midleft=(input_x + 20, input_y + input_height//2))
            surface.blit(placeholder, placeholder_rect)
            cursor_x = input_x + 20
        
        # Draw blinking cursor
        if self.cursor_visible and len(self.name) < self.max_length:
            cursor_rect = pygame.Rect(cursor_x, input_y + 15, 2, input_height - 30)
            pygame.draw.rect(surface, WHITE, cursor_rect)
        
        # Character limit indicator
        limit_text = control_font.render(f"{len(self.name)}/3", True, (150, 150, 150))
        limit_rect = limit_text.get_rect(topright=(input_x + input_width - 10, input_y + input_height + 5))
        surface.blit(limit_text, limit_rect)
        
        # Modern control hints at bottom
        control_bg = pygame.Surface((WIDTH, 80), pygame.SRCALPHA)
        pygame.draw.rect(control_bg, (0, 0, 0, 100), (0, 0, WIDTH, 80))
        surface.blit(control_bg, (0, HEIGHT - 80))
        
        # Simple instructions
        if len(self.name) < 3:
            instruction = control_font.render("Type 3 characters for your name", True, (200, 200, 200))
        else:
            instruction = control_font.render("Press ENTER to confirm", True, (100, 255, 100))
        instruction_rect = instruction.get_rect(center=(WIDTH//2, HEIGHT - 40))
        surface.blit(instruction, instruction_rect)
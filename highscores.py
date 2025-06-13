"""
High score management system
"""
import pygame
import math
import json
import os
from constants import WIDTH, HEIGHT, WHITE, BLACK, GREEN, screen

class HighScoreManager:
    def __init__(self):
        self.scores_file = "high_scores.json"
        self.high_scores = self.load_scores()
    
    def load_scores(self):
        """Load high scores from local file"""
        try:
            if os.path.exists(self.scores_file):
                with open(self.scores_file, 'r') as f:
                    return json.load(f)
            else:
                # Default high scores if file doesn't exist
                return [
                    {"initials": "ACE", "score": 15000},
                    {"initials": "MAX", "score": 12500},
                    {"initials": "ZAP", "score": 11200},
                    {"initials": "BOB", "score": 9800},
                    {"initials": "JOE", "score": 8900},
                    {"initials": "SUE", "score": 7500},
                    {"initials": "TOM", "score": 6200},
                    {"initials": "ANN", "score": 5100},
                    {"initials": "DAN", "score": 4000},
                    {"initials": "KIM", "score": 3200}
                ]
        except Exception as e:
            print(f"Error loading high scores: {e}")
            # Return default scores if there's an error
            return [{"initials": "ERR", "score": 0}]
    
    def save_scores(self):
        """Save high scores to local file"""
        try:
            with open(self.scores_file, 'w') as f:
                json.dump(self.high_scores, f, indent=2)
            print(f"High scores saved to {self.scores_file}")
        except Exception as e:
            print(f"Error saving high scores: {e}")
    
    def is_high_score(self, score):
        """Check if score qualifies for high score table"""
        return len(self.high_scores) < 10 or score > self.high_scores[-1]["score"]
    
    def add_score(self, initials, score):
        """Add new score to high score table and save to file"""
        new_entry = {"initials": initials, "score": score}
        self.high_scores.append(new_entry)
        self.high_scores.sort(key=lambda x: x["score"], reverse=True)
        self.high_scores = self.high_scores[:10]  # Keep only top 10
        self.save_scores()  # Save to file immediately
    
    def get_high_scores(self):
        """Get sorted high scores"""
        return self.high_scores

class HighScoreEntry:
    def __init__(self, score, high_score_manager):
        self.score = score
        self.high_score_manager = high_score_manager
        self.initials = ["A", "A", "A"]
        self.current_letter = 0
        self.done = False
    
    def handle_input(self, event):
        """Handle input for entering initials"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                # Move to next letter
                self.initials[self.current_letter] = chr((ord(self.initials[self.current_letter]) - ord('A') + 1) % 26 + ord('A'))
            elif event.key == pygame.K_DOWN:
                # Move to previous letter  
                self.initials[self.current_letter] = chr((ord(self.initials[self.current_letter]) - ord('A') - 1) % 26 + ord('A'))
            elif event.key == pygame.K_RIGHT and self.current_letter < 2:
                # Move to next position
                self.current_letter += 1
            elif event.key == pygame.K_LEFT and self.current_letter > 0:
                # Move to previous position
                self.current_letter -= 1
            elif event.key == pygame.K_RETURN:
                # Submit initials
                initials_string = "".join(self.initials)
                self.high_score_manager.add_score(initials_string, self.score)
                self.done = True
    
    def draw(self, surface):
        """Draw the initial entry screen"""
        # Background
        surface.fill(BLACK)
        
        # Fonts
        title_font = pygame.font.Font(None, 64)
        subtitle_font = pygame.font.Font(None, 48)
        instruction_font = pygame.font.Font(None, 32)
        letter_font = pygame.font.Font(None, 96)
        
        # Title
        title_text = title_font.render("NEW HIGH SCORE!", True, WHITE)
        title_rect = title_text.get_rect(center=(WIDTH//2, 150))
        surface.blit(title_text, title_rect)
        
        # Score
        score_text = subtitle_font.render(f"Score: {self.score}", True, GREEN)
        score_rect = score_text.get_rect(center=(WIDTH//2, 220))
        surface.blit(score_text, score_rect)
        
        # Instructions
        inst_text = instruction_font.render("Enter your initials:", True, WHITE)
        inst_rect = inst_text.get_rect(center=(WIDTH//2, 300))
        surface.blit(inst_text, inst_rect)
        
        # Letter entry
        letter_spacing = 80
        start_x = WIDTH//2 - letter_spacing
        
        for i, letter in enumerate(self.initials):
            x = start_x + i * letter_spacing
            y = 400
            
            # Highlight current letter
            if i == self.current_letter:
                highlight_rect = pygame.Rect(x - 30, y - 40, 60, 80)
                pygame.draw.rect(surface, WHITE, highlight_rect, 3)
            
            # Draw letter
            letter_text = letter_font.render(letter, True, WHITE)
            letter_rect = letter_text.get_rect(center=(x, y))
            surface.blit(letter_text, letter_rect)
        
        # Controls
        control_texts = [
            "UP/DOWN: Change letter",
            "LEFT/RIGHT: Move cursor", 
            "ENTER: Submit"
        ]
        
        for i, text in enumerate(control_texts):
            control_surface = instruction_font.render(text, True, WHITE)
            control_rect = control_surface.get_rect(center=(WIDTH//2, 550 + i * 30))
            surface.blit(control_surface, control_rect)
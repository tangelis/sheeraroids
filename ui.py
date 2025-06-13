"""
User interface components: Sliders, High Score screens, Mode Selection
"""
import pygame
import math
import random
from constants import WIDTH, HEIGHT, WHITE, BLACK, screen

class SpeedScaleSlider:
    def __init__(self):
        self.x = 20
        self.y = 200
        self.width = 30
        self.height = 300
        self.slider_pos = 0.5  # 0.0 to 1.0, starts at middle
        self.dragging = False
        self.knob_radius = 15
        
    def handle_mouse_event(self, event, mouse_pos):
        """Handle mouse events for the slider"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                knob_y = self.y + self.height - (self.slider_pos * self.height)
                knob_rect = pygame.Rect(self.x - self.knob_radius, knob_y - self.knob_radius, 
                                       self.knob_radius * 2, self.knob_radius * 2)
                if knob_rect.collidepoint(mouse_pos):
                    self.dragging = True
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
                
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                # Update slider position based on mouse Y
                relative_y = mouse_pos[1] - self.y
                self.slider_pos = 1.0 - (relative_y / self.height)  # Invert so top = 1.0
                self.slider_pos = max(0.0, min(1.0, self.slider_pos))  # Clamp
    
    def get_scale_multiplier(self):
        """Convert slider position to exponential scale multiplier"""
        # Exponential scale: 0.1x to 100x (much more dramatic!)
        # slider_pos 0.0 -> 0.1x, slider_pos 0.5 -> 1.0x, slider_pos 1.0 -> 100x
        if self.slider_pos <= 0.5:
            # Bottom half: 0.1 to 1.0 (exponential)
            normalized = self.slider_pos * 2  # 0.0 to 1.0
            return 0.1 * (10 ** normalized)  # 0.1 to 1.0
        else:
            # Top half: 1.0 to 100.0 (exponential)
            normalized = (self.slider_pos - 0.5) * 2  # 0.0 to 1.0
            return 1.0 * (100 ** normalized)  # 1.0 to 100.0
    
    def draw(self, surface):
        """Draw the slider"""
        # Draw slider track
        track_color = (100, 100, 100)
        track_rect = pygame.Rect(self.x - 5, self.y, self.width + 10, self.height)
        pygame.draw.rect(surface, track_color, track_rect, 2)
        
        # Draw slider background
        bg_color = (50, 50, 50)
        bg_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, bg_color, bg_rect)
        
        # Draw slider knob
        knob_y = self.y + self.height - (self.slider_pos * self.height)
        knob_color = (0, 255, 255) if self.dragging else (255, 255, 255)
        pygame.draw.circle(surface, knob_color, (self.x + self.width // 2, int(knob_y)), self.knob_radius)
        
        # Draw scale value text
        scale_value = self.get_scale_multiplier()
        font = pygame.font.Font(None, 24)
        
        # Title
        title_text = font.render("Speed Scale", True, (255, 255, 255))
        surface.blit(title_text, (self.x - 10, self.y - 30))
        
        # Current value
        value_text = font.render(f"{scale_value:.1f}x", True, (0, 255, 255))
        surface.blit(value_text, (self.x - 5, self.y + self.height + 10))
        
        # Show what this means for fragment scaling
        small_font = pygame.font.Font(None, 18)
        # Calculate what medium speed fragments will be
        medium_scale = 1.0 + ((1.0 + (0.5 * 3.0) - 1.0) * scale_value)  # 0.5 normalized speed
        fast_scale = 1.0 + ((1.0 + (1.0 * 3.0) - 1.0) * scale_value)     # 1.0 normalized speed
        
        medium_text = small_font.render(f"Med: {medium_scale:.1f}x", True, (255, 255, 100))
        surface.blit(medium_text, (self.x - 5, self.y + self.height + 35))
        
        fast_text = small_font.render(f"Fast: {fast_scale:.1f}x", True, (255, 100, 100))
        surface.blit(fast_text, (self.x - 5, self.y + self.height + 55))
        
        # Scale markers
        small_font = pygame.font.Font(None, 20)
        # Top (100x)
        top_text = small_font.render("100x", True, (150, 150, 150))
        surface.blit(top_text, (self.x + self.width + 5, self.y - 5))
        
        # Middle (1x)
        mid_text = small_font.render("1x", True, (150, 150, 150))
        surface.blit(mid_text, (self.x + self.width + 5, self.y + self.height // 2 - 5))
        
        # Bottom (0.1x)
        bottom_text = small_font.render("0.1x", True, (150, 150, 150))
        surface.blit(bottom_text, (self.x + self.width + 5, self.y + self.height - 10))

def show_mode_selection():
    """Display mode selection screen and return the selected mode"""
    from constants import clock
    import os
    from constants import assets_dir
    
    # Load mode selection images
    try:
        mode1_img = pygame.image.load(os.path.join(assets_dir, "ChatGPT Image Jun 12, 2025, 07_17_20 PM.png"))
        mode2_img = pygame.image.load(os.path.join(assets_dir, "Generated Image June 12, 2025 - 7_16PM.png"))
        # Scale images to reasonable size
        mode1_img = pygame.transform.scale(mode1_img, (300, 300))
        mode2_img = pygame.transform.scale(mode2_img, (300, 300))
    except:
        # Fallback if images can't be loaded
        mode1_img = pygame.Surface((300, 300))
        mode1_img.fill((255, 100, 100))
        mode2_img = pygame.Surface((300, 300))
        mode2_img.fill((100, 100, 255))
    
    font_title = pygame.font.Font(None, 64)
    font_subtitle = pygame.font.Font(None, 36)
    font_instruction = pygame.font.Font(None, 24)
    
    selecting = True
    selected_mode = None
    
    while selecting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                import sys
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    selected_mode = "accelerated"
                    selecting = False
                elif event.key == pygame.K_2:
                    selected_mode = "slowed"
                    selecting = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    import sys
                    sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                # Check if clicked on mode 1
                if 50 <= mouse_x <= 350 and 200 <= mouse_y <= 500:
                    selected_mode = "accelerated"
                    selecting = False
                # Check if clicked on mode 2
                elif 450 <= mouse_x <= 750 and 200 <= mouse_y <= 500:
                    selected_mode = "slowed"
                    selecting = False
        
        # Draw selection screen
        screen.fill(BLACK)
        
        # Title
        title_text = font_title.render("CHOOSE YOUR MODE", True, WHITE)
        title_rect = title_text.get_rect(center=(WIDTH//2, 100))
        screen.blit(title_text, title_rect)
        
        # Mode 1 - Accelerated
        screen.blit(mode1_img, (50, 200))
        mode1_text = font_subtitle.render("ACCELERATED", True, (255, 200, 100))
        mode1_rect = mode1_text.get_rect(center=(200, 520))
        screen.blit(mode1_text, mode1_rect)
        mode1_desc = font_instruction.render("Press 1 or Click", True, WHITE)
        mode1_desc_rect = mode1_desc.get_rect(center=(200, 550))
        screen.blit(mode1_desc, mode1_desc_rect)
        
        # Mode 2 - Slowed
        screen.blit(mode2_img, (450, 200))
        mode2_text = font_subtitle.render("SLOWED", True, (100, 200, 255))
        mode2_rect = mode2_text.get_rect(center=(600, 520))
        screen.blit(mode2_text, mode2_rect)
        mode2_desc = font_instruction.render("Press 2 or Click", True, WHITE)
        mode2_desc_rect = mode2_desc.get_rect(center=(600, 550))
        screen.blit(mode2_desc, mode2_desc_rect)
        
        # Instruction
        inst_text = font_instruction.render("Choose your gameplay speed mode", True, WHITE)
        inst_rect = inst_text.get_rect(center=(WIDTH//2, 150))
        screen.blit(inst_text, inst_rect)
        
        pygame.display.flip()
        clock.tick(30)
    
    return selected_mode
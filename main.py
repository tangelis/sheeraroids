#!/usr/bin/env python3
"""
Sheera vs Iguanas
A game where Sheera uses sound waves to defend against Iguanas.
Main entry point for the game.
"""
import pygame
import sys
from constants import clock, FPS
from game import Game
from ui import show_mode_selection

def main():
    while True:
        # Show mode selection screen
        selected_mode = show_mode_selection()
        
        # Create game with selected mode
        game = Game(selected_mode)
        running = True
        
        while running:
            clock.tick(FPS)
            
            # Handle events
            result = game.handle_events()
            if result == "restart":
                running = False  # Break out to restart
            elif result == False:
                pygame.quit()
                sys.exit()
            
            # Update game state
            game.update()
            
            # Draw everything
            game.draw()

if __name__ == "__main__":
    main()
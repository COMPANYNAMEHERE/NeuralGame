import sys
import os
import pygame

# Add src to Python path
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

# Game imports
from game.game import Game

def main():
    try:
        # Initialize pygame
        pygame.init()
        
        # Create and run game
        game = Game()
        game.run()
    except Exception as e:
        print(f"Error during game execution: {e}")
    finally:
        # Clean up
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
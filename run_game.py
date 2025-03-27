#!/usr/bin/env python3
import sys
import os

# Make sure we can import our game modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from game import Game
except ImportError as e:
    print(f"Error importing game modules: {e}")
    sys.exit(1)

def main():
    """
    Main entry point for the game.
    This function can be wrapped for web deployment using tools like Pyodide/Pygame Web.
    """
    game = Game()
    game.run()
    
if __name__ == "__main__":
    main() 
import pygame
import os

class AssetLoader:
    def __init__(self):
        self.assets = {}
        
    def load_image(self, path):
        """Load an image, returning None if the file doesn't exist."""
        if path in self.assets:
            return self.assets[path]
            
        if os.path.exists(path):
            try:
                image = pygame.image.load(path).convert_alpha()
                self.assets[path] = image
                return image
            except pygame.error:
                print(f"Failed to load image: {path}")
                return None
        return None
    
    def get_character_sprite(self, path="assets/character/player.png"):
        """Try to load character sprite, return None if it doesn't exist."""
        return self.load_image(path)
    
    def get_tool_sprite(self, tool_name):
        """Try to load a tool sprite, return None if it doesn't exist."""
        path = f"assets/tools/{tool_name}.png"
        return self.load_image(path)
    
    def get_world_sprite(self, element_name):
        """Try to load a world element sprite, return None if it doesn't exist."""
        path = f"assets/world/{element_name}.png"
        return self.load_image(path)

# Create a global instance
asset_loader = AssetLoader() 
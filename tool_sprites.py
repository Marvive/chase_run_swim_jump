import pygame
import math

class ToolSprite:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.inventory_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
    def draw(self, screen, x, y, angle, facing_right=True, is_swinging=False):
        if not facing_right:
            angle = -angle
            
        # Create a copy of the surface for animation
        anim_surface = self.surface.copy()
        
        if is_swinging:
            # Add a trail effect when swinging
            trail_length = 8
            trail_width = 2
            trail_color = (255, 255, 255, 100)
            
            # Calculate trail points
            handle_x = 16
            handle_y = 16
            head_x = 24 + math.cos(math.radians(angle)) * 8
            head_y = 24 + math.sin(math.radians(angle)) * 8
            
            # Draw trail
            for i in range(trail_length):
                alpha = 100 - (i * 100 // trail_length)
                trail_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                trail_x = handle_x + (head_x - handle_x) * i / trail_length
                trail_y = handle_y + (head_y - handle_y) * i / trail_length
                pygame.draw.circle(trail_surface, (*trail_color[:3], alpha), 
                                 (int(trail_x), int(trail_y)), trail_width)
                anim_surface.blit(trail_surface, (0, 0))
        
        rotated = pygame.transform.rotate(anim_surface, angle)
        screen.blit(rotated, (x - rotated.get_width()//2, y - rotated.get_height()//2))
        
    def draw_inventory(self, screen, x, y):
        screen.blit(self.inventory_surface, (x, y))

class AxeSprite(ToolSprite):
    def __init__(self):
        super().__init__(32, 32)
        # Draw handle
        pygame.draw.line(self.surface, (139, 69, 19), (16, 16), (24, 24), 4)
        # Draw axe head
        pygame.draw.polygon(self.surface, (192, 192, 192), 
                          [(24, 16), (28, 12), (28, 20)])
        
        # Draw inventory version (top-down view)
        pygame.draw.line(self.inventory_surface, (139, 69, 19), (8, 16), (24, 16), 4)
        pygame.draw.polygon(self.inventory_surface, (192, 192, 192), 
                          [(24, 16), (28, 12), (28, 20)])

class PickaxeSprite(ToolSprite):
    def __init__(self):
        super().__init__(32, 32)
        # Draw handle
        pygame.draw.line(self.surface, (139, 69, 19), (16, 16), (24, 24), 4)
        # Draw pickaxe head
        pygame.draw.polygon(self.surface, (192, 192, 192), 
                          [(24, 16), (28, 12), (28, 20)])
        pygame.draw.polygon(self.surface, (192, 192, 192), 
                          [(24, 16), (28, 16), (28, 24)])
        
        # Draw inventory version (top-down view)
        pygame.draw.line(self.inventory_surface, (139, 69, 19), (8, 16), (24, 16), 4)
        pygame.draw.polygon(self.inventory_surface, (192, 192, 192), 
                          [(24, 16), (28, 12), (28, 20)])
        pygame.draw.polygon(self.inventory_surface, (192, 192, 192), 
                          [(24, 16), (28, 16), (28, 24)])

class HammerSprite(ToolSprite):
    def __init__(self):
        super().__init__(32, 32)
        # Draw handle
        pygame.draw.line(self.surface, (139, 69, 19), (16, 16), (24, 24), 4)
        # Draw hammer head
        pygame.draw.rect(self.surface, (192, 192, 192), (24, 12, 8, 8))
        pygame.draw.rect(self.surface, (192, 192, 192), (24, 20, 8, 4))
        
        # Draw inventory version (top-down view)
        pygame.draw.line(self.inventory_surface, (139, 69, 19), (8, 16), (24, 16), 4)
        pygame.draw.rect(self.inventory_surface, (192, 192, 192), (24, 12, 8, 8))
        pygame.draw.rect(self.inventory_surface, (192, 192, 192), (24, 20, 8, 4)) 
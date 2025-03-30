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
            # Add a trail effect when swinging (more pixelated for 16-bit style)
            trail_length = 4  # Reduced for more pixelated look
            pixel_size = 2    # Size of trail "pixels"
            trail_color = (255, 255, 255, 150)
            
            # Calculate trail points
            handle_x = 16
            handle_y = 16
            head_x = 24 + math.cos(math.radians(angle)) * 8
            head_y = 24 + math.sin(math.radians(angle)) * 8
            
            # Draw pixelated trail
            for i in range(trail_length):
                alpha = 150 - (i * 150 // trail_length)
                trail_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                trail_x = handle_x + (head_x - handle_x) * i / trail_length
                trail_y = handle_y + (head_y - handle_y) * i / trail_length
                
                # Draw a square "pixel" instead of a circle for 16-bit look
                pixel_rect = pygame.Rect(
                    int(trail_x - pixel_size/2), 
                    int(trail_y - pixel_size/2),
                    pixel_size, pixel_size
                )
                pygame.draw.rect(trail_surface, (*trail_color[:3], alpha), pixel_rect)
                anim_surface.blit(trail_surface, (0, 0))
        
        rotated = pygame.transform.rotate(anim_surface, angle)
        screen.blit(rotated, (x - rotated.get_width()//2, y - rotated.get_height()//2))
        
    def draw_inventory(self, screen, x, y):
        screen.blit(self.inventory_surface, (x, y))

class AxeSprite(ToolSprite):
    def __init__(self):
        super().__init__(32, 32)
        # Define pixel size for 16-bit look
        pixel_size = 2
        
        # Draw handle (pixelated)
        for i in range(8):
            px = 16 + i // 2
            py = 16 + i // 2
            pygame.draw.rect(self.surface, (139, 69, 19), 
                           (px, py, pixel_size, pixel_size))
            
        # Draw axe head (pixelated)
        axe_head_color = (160, 160, 160)
        edge_color = (200, 200, 200)
        
        # Blade right side
        for i in range(5):
            pygame.draw.rect(self.surface, axe_head_color, 
                          (24 + i, 16 - i, pixel_size, pixel_size))
            pygame.draw.rect(self.surface, axe_head_color, 
                          (24 + i, 16 + i, pixel_size, pixel_size))
                          
        # Blade edge highlight
        pygame.draw.rect(self.surface, edge_color, 
                      (28, 12, pixel_size, pixel_size))
        pygame.draw.rect(self.surface, edge_color, 
                      (28, 20, pixel_size, pixel_size))
        
        # Draw inventory version (pixelated top-down view)
        # Handle
        for i in range(8):
            pygame.draw.rect(self.inventory_surface, (139, 69, 19), 
                          (8 + i * 2, 16, pixel_size, pixel_size))
            
        # Axe head
        for i in range(4):
            pygame.draw.rect(self.inventory_surface, axe_head_color, 
                          (24, 12 + i * 2, pixel_size, pixel_size))
            pygame.draw.rect(self.inventory_surface, axe_head_color, 
                          (26, 12 + i * 2, pixel_size, pixel_size))
            pygame.draw.rect(self.inventory_surface, edge_color, 
                          (28, 12 + i * 2, pixel_size, pixel_size))

class PickaxeSprite(ToolSprite):
    def __init__(self):
        super().__init__(32, 32)
        # Define pixel size for 16-bit look
        pixel_size = 2
        
        # Draw handle (pixelated)
        for i in range(8):
            px = 16 + i // 2
            py = 16 + i // 2
            pygame.draw.rect(self.surface, (139, 69, 19), 
                           (px, py, pixel_size, pixel_size))
            
        # Draw pickaxe head (pixelated)
        pick_color = (160, 160, 160)
        edge_color = (200, 200, 200)
        
        # Top prong
        for i in range(4):
            pygame.draw.rect(self.surface, pick_color, 
                          (24 + i, 16 - i, pixel_size, pixel_size))
                          
        # Bottom prong
        for i in range(4):
            pygame.draw.rect(self.surface, pick_color, 
                          (24 + i, 16 + i, pixel_size, pixel_size))
                          
        # Prong tips (highlight)
        pygame.draw.rect(self.surface, edge_color, 
                      (28, 12, pixel_size, pixel_size))
        pygame.draw.rect(self.surface, edge_color, 
                      (28, 20, pixel_size, pixel_size))
        
        # Draw inventory version (pixelated top-down view)
        # Handle
        for i in range(8):
            pygame.draw.rect(self.inventory_surface, (139, 69, 19), 
                          (8 + i * 2, 16, pixel_size, pixel_size))
            
        # Pickaxe head
        for i in range(3):
            pygame.draw.rect(self.inventory_surface, pick_color, 
                          (24, 12 + i * 4, pixel_size, pixel_size))
            pygame.draw.rect(self.inventory_surface, pick_color, 
                          (26, 12 + i * 4, pixel_size, pixel_size))
            pygame.draw.rect(self.inventory_surface, edge_color, 
                          (28, 12 + i * 4, pixel_size, pixel_size))

class SwordSprite:
    def __init__(self):
        self.width = 32
        self.height = 32
        
    def draw(self, screen, x, y, angle=0, facing_right=True, is_swinging=False):
        # Create surface for sword
        sword_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Define colors for sword
        blade_color = (200, 200, 220)  # Silver blade
        handle_color = (139, 69, 19)   # Brown handle
        guard_color = (218, 165, 32)   # Gold guard
        
        # Draw handle
        pygame.draw.rect(sword_surface, handle_color, (13, 16, 6, 12))
        
        # Draw guard (cross piece)
        pygame.draw.rect(sword_surface, guard_color, (7, 14, 18, 4))
        
        # Draw blade
        if facing_right:
            # Draw blade pointing right
            points = [(15, 2), (17, 2), (17, 14), (15, 14)]
        else:
            # Draw blade pointing left
            points = [(15, 2), (17, 2), (17, 14), (15, 14)]
            
        pygame.draw.polygon(sword_surface, blade_color, points)
        
        # Draw blade edge/highlight
        if facing_right:
            pygame.draw.line(sword_surface, (255, 255, 255), (17, 2), (17, 14), 1)
        else:
            pygame.draw.line(sword_surface, (255, 255, 255), (15, 2), (15, 14), 1)
        
        # Apply rotation for swing animation
        if is_swinging:
            # Rotate based on angle for swing animation
            offset = 30 if facing_right else -30
            rotation_angle = offset - angle * (1 if facing_right else -1)
            sword_surface = pygame.transform.rotate(sword_surface, rotation_angle)
        
        # Flip if facing left
        if not facing_right:
            sword_surface = pygame.transform.flip(sword_surface, True, False)
        
        # Draw to screen
        screen.blit(sword_surface, (x, y))
    
    def draw_inventory(self, screen, x, y):
        # Create a simpler version for inventory display
        inventory_surface = pygame.Surface((24, 24), pygame.SRCALPHA)
        
        # Define colors
        blade_color = (200, 200, 220)  # Silver blade
        handle_color = (139, 69, 19)   # Brown handle
        guard_color = (218, 165, 32)   # Gold guard
        
        # Draw handle
        pygame.draw.rect(inventory_surface, handle_color, (10, 12, 4, 10))
        
        # Draw guard
        pygame.draw.rect(inventory_surface, guard_color, (6, 10, 12, 3))
        
        # Draw blade
        pygame.draw.rect(inventory_surface, blade_color, (10, 2, 4, 9))
        
        # Draw to screen
        screen.blit(inventory_surface, (x, y))

class HammerSprite(ToolSprite):
    def __init__(self):
        super().__init__(32, 32)
        # Define pixel size for 16-bit look
        pixel_size = 2
        
        # Draw handle (pixelated)
        for i in range(8):
            px = 16 + i // 2
            py = 16 + i // 2
            pygame.draw.rect(self.surface, (139, 69, 19), 
                           (px, py, pixel_size, pixel_size))
            
        # Draw hammer head (pixelated)
        hammer_color = (160, 160, 160)
        edge_color = (200, 200, 200)
        
        # Hammer head block
        for y in range(4):
            for x in range(4):
                pygame.draw.rect(self.surface, hammer_color, 
                              (24 + x * pixel_size, 12 + y * pixel_size, 
                               pixel_size, pixel_size))
                               
        # Hammer edge (at bottom)
        for x in range(4):
            pygame.draw.rect(self.surface, hammer_color, 
                          (24 + x * pixel_size, 20, pixel_size, pixel_size))
                          
        # Edge highlight
        pygame.draw.rect(self.surface, edge_color, 
                      (24, 12, pixel_size, pixel_size))
        pygame.draw.rect(self.surface, edge_color, 
                      (30, 12, pixel_size, pixel_size))
        
        # Draw inventory version (pixelated top-down view)
        # Handle
        for i in range(8):
            pygame.draw.rect(self.inventory_surface, (139, 69, 19), 
                          (8 + i * 2, 16, pixel_size, pixel_size))
            
        # Hammer head
        for y in range(4):
            for x in range(4):
                pygame.draw.rect(self.inventory_surface, hammer_color, 
                              (24 + x * pixel_size, 12 + y * pixel_size, 
                               pixel_size, pixel_size))
                               
        # Bottom part
        for x in range(4):
            pygame.draw.rect(self.inventory_surface, hammer_color, 
                          (24 + x * pixel_size, 20, pixel_size, pixel_size)) 
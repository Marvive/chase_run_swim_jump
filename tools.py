import pygame
import math

class Tool:
    def __init__(self, name, damage, cooldown):
        self.name = name
        self.damage = damage
        self.cooldown = cooldown
        self.current_cooldown = 0
        self.animation_frame = 0
        self.is_swinging = False
        
    def update(self):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1
            
    def can_use(self):
        return self.current_cooldown == 0
        
    def use(self):
        if self.can_use():
            self.current_cooldown = self.cooldown
            self.is_swinging = True
            self.animation_frame = 0
            return True
        return False
        
    def draw(self, screen, x, y, facing_right):
        # Draw tool animation
        if self.is_swinging:
            angle = math.sin(self.animation_frame * 0.5) * 45
            if not facing_right:
                angle = -angle
                
            # Draw tool handle
            handle_length = 20
            handle_width = 4
            handle_x = x + (20 if facing_right else -20)
            handle_y = y + 20
            
            # Draw tool head
            head_size = 16
            head_x = handle_x + math.cos(math.radians(angle)) * handle_length
            head_y = handle_y + math.sin(math.radians(angle)) * handle_length
            
            # Draw handle
            pygame.draw.line(screen, (139, 69, 19), 
                           (handle_x, handle_y),
                           (head_x, head_y),
                           handle_width)
            
            # Draw tool head
            pygame.draw.rect(screen, (192, 192, 192),
                           (head_x - head_size//2,
                            head_y - head_size//2,
                            head_size, head_size))
            
            self.animation_frame += 1
            if self.animation_frame >= 20:
                self.is_swinging = False

class Axe(Tool):
    def __init__(self):
        super().__init__("axe", 2, 20)
        
class Pickaxe(Tool):
    def __init__(self):
        super().__init__("pickaxe", 2, 20)
        
class Hammer(Tool):
    def __init__(self):
        super().__init__("hammer", 1, 15)

class BuildingSystem:
    def __init__(self):
        self.blueprints = {
            "house": {
                "wood": 50,
                "stone": 30,
                "ore": 10
            },
            "toy_robot": {
                "wood": 20,
                "stone": 10,
                "ore": 30
            }
        }
        self.current_blueprint = None
        self.building_mode = False
        
    def can_build(self, inventory, blueprint_name):
        if blueprint_name not in self.blueprints:
            return False
            
        requirements = self.blueprints[blueprint_name]
        for material, amount in requirements.items():
            if inventory[material] < amount:
                return False
        return True
        
    def build(self, inventory, blueprint_name):
        if not self.can_build(inventory, blueprint_name):
            return False
            
        requirements = self.blueprints[blueprint_name]
        for material, amount in requirements.items():
            inventory[material] -= amount
        return True 
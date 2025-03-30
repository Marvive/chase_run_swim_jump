import pygame
import random
import sys
from tools import Axe, Pickaxe, Hammer, BuildingSystem
from sprites import Character
from tool_sprites import AxeSprite, PickaxeSprite, HammerSprite
from particles import ParticleSystem
from sound_manager import SoundManager

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 32
GRAVITY = 0.8
JUMP_FORCE = -15
PLAYER_SPEED = 5

# Colors
SKY_BLUE = (135, 206, 235)
GRASS_GREEN = (34, 139, 34)
DIRT_BROWN = (139, 69, 19)
STONE_GRAY = (128, 128, 128)
INVENTORY_BG = (50, 50, 50, 180)
SELECTED_ITEM = (255, 255, 255, 100)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Chase Run Swim Jump")
clock = pygame.time.Clock()

class Player:
    def __init__(self):
        self.character = Character()
        self.width = self.character.width
        self.height = self.character.height
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 200
        self.vel_y = 0
        self.jumping = False
        self.facing_right = True
        self.tools = {
            "axe": Axe(),
            "pickaxe": Pickaxe(),
            "hammer": Hammer()
        }
        self.tool_sprites = {
            "axe": AxeSprite(),
            "pickaxe": PickaxeSprite(),
            "hammer": HammerSprite()
        }
        self.current_tool = "axe"
        self.inventory = {
            "wood": 0,
            "stone": 0,
            "ore": 0
        }
        self.building_system = BuildingSystem()
        self.show_inventory = False
        self.selected_slot = 0
        self.inventory_slots = [
            {"name": "axe", "icon": "🪓"},
            {"name": "pickaxe", "icon": "⛏️"}
        ]
        self.sound_manager = SoundManager()
        self.is_swinging = False
        self.swing_timer = 0
        
    def move(self, dx):
        self.x += dx
        if dx > 0:
            self.facing_right = True
        elif dx < 0:
            self.facing_right = False
            
    def jump(self):
        if not self.jumping:
            self.vel_y = JUMP_FORCE
            self.jumping = True
            
    def update(self):
        # Apply gravity
        self.vel_y += GRAVITY
        self.y += self.vel_y
        
        # Ground collision
        if self.y > SCREEN_HEIGHT - self.height:
            self.y = SCREEN_HEIGHT - self.height
            self.vel_y = 0
            self.jumping = False
            
        # Screen boundaries
        if self.x < 0:
            self.x = 0
        if self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
            
        # Update current tool
        self.tools[self.current_tool].update()
        
        # Update swing animation
        if self.is_swinging:
            self.swing_timer += 1
            if self.swing_timer >= 10:  # Swing animation duration
                self.is_swinging = False
                self.swing_timer = 0
            
    def draw(self, screen):
        # Draw character
        self.character.draw(screen, self.x, self.y, self.facing_right)
        
        # Draw current tool or hammer if building
        if self.building_system.building_mode:
            self.tool_sprites["hammer"].draw(screen, 
                                          self.x + (40 if self.facing_right else -40),
                                          self.y + 20,
                                          self.tools["hammer"].animation_frame * 5,
                                          self.facing_right,
                                          self.is_swinging)
        else:
            self.tool_sprites[self.current_tool].draw(screen,
                                                    self.x + (40 if self.facing_right else -40),
                                                    self.y + 20,
                                                    self.tools[self.current_tool].animation_frame * 5,
                                                    self.facing_right,
                                                    self.is_swinging)
        
        # Draw resource inventory
        self.draw_resource_inventory(screen)
        
        # Draw tool inventory if open
        if self.show_inventory:
            self.draw_tool_inventory(screen)
        
    def draw_resource_inventory(self, screen):
        # Draw inventory background
        inventory_y = 10
        for i, (item, count) in enumerate(self.inventory.items()):
            pygame.draw.rect(screen, (200, 200, 200), 
                           (10 + i * 100, inventory_y, 90, 30))
            font = pygame.font.Font(None, 24)
            text = font.render(f"{item}: {count}", True, (0, 0, 0))
            screen.blit(text, (15 + i * 100, inventory_y + 5))
            
    def draw_tool_inventory(self, screen):
        # Create semi-transparent background
        inventory_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        inventory_surface.fill(INVENTORY_BG)
        screen.blit(inventory_surface, (0, 0))
        
        # Draw inventory slots
        slot_size = 64
        start_x = SCREEN_WIDTH // 2 - (len(self.inventory_slots) * slot_size) // 2
        start_y = SCREEN_HEIGHT // 2 - slot_size // 2
        
        for i, slot in enumerate(self.inventory_slots):
            x = start_x + i * slot_size
            y = start_y
            
            # Draw slot background
            pygame.draw.rect(screen, (100, 100, 100), (x, y, slot_size, slot_size))
            pygame.draw.rect(screen, (0, 0, 0), (x, y, slot_size, slot_size), 2)
            
            # Draw selected highlight
            if i == self.selected_slot:
                pygame.draw.rect(screen, SELECTED_ITEM, (x, y, slot_size, slot_size))
            
            # Draw tool sprite
            tool_name = slot["name"]
            if tool_name in self.tool_sprites:
                self.tool_sprites[tool_name].draw_inventory(screen, 
                                                          x + (slot_size - 32)//2,
                                                          y + (slot_size - 32)//2)
            
            # Draw tool name
            name_font = pygame.font.Font(None, 24)
            name_text = name_font.render(slot["name"], True, (0, 0, 0))
            name_rect = name_text.get_rect(center=(x + slot_size//2, y + slot_size + 20))
            screen.blit(name_text, name_rect)
            
    def switch_tool(self, tool_name):
        if tool_name in self.tools:
            self.current_tool = tool_name
            
    def use_tool(self, world):
        if self.building_system.building_mode:
            if self.tools["hammer"].use():
                self.sound_manager.play("hammer_swing")
                self.is_swinging = True
                self.swing_timer = 0
                mouse_pos = pygame.mouse.get_pos()
                if self.building_system.build(self.inventory, self.building_system.current_blueprint):
                    world.add_building(mouse_pos[0], mouse_pos[1], 
                                    self.building_system.current_blueprint)
        else:
            if self.tools[self.current_tool].use():
                # Play tool sound
                self.sound_manager.play(f"{self.current_tool}_swing")
                self.is_swinging = True
                self.swing_timer = 0
                
                # Check for resource collection
                mouse_pos = pygame.mouse.get_pos()
                for tile in world.tiles:
                    if tile["rect"].collidepoint(mouse_pos):
                        if self.current_tool == "axe" and tile["type"] == "tree":
                            self.inventory["wood"] += 1
                            world.remove_tile(tile)
                            world.particle_system.create_block_break(
                                tile["rect"].centerx, tile["rect"].centery, 
                                (34, 139, 34))  # Tree color
                            self.sound_manager.play("block_break")
                        elif self.current_tool == "pickaxe" and tile["type"] == "stone":
                            self.inventory["stone"] += 1
                            world.remove_tile(tile)
                            world.particle_system.create_block_break(
                                tile["rect"].centerx, tile["rect"].centery, 
                                STONE_GRAY)
                            self.sound_manager.play("block_break")

class World:
    def __init__(self):
        self.tiles = []
        self.buildings = []
        self.particle_system = ParticleSystem()
        self.generate_world()
        
    def generate_world(self):
        # Generate ground
        ground_height = SCREEN_HEIGHT - 100
        for x in range(0, SCREEN_WIDTH, TILE_SIZE):
            # Grass layer
            self.tiles.append({"rect": pygame.Rect(x, ground_height, TILE_SIZE, TILE_SIZE), "type": "grass"})
            # Dirt layer
            for y in range(ground_height + TILE_SIZE, SCREEN_HEIGHT, TILE_SIZE):
                self.tiles.append({"rect": pygame.Rect(x, y, TILE_SIZE, TILE_SIZE), "type": "dirt"})
                
        # Generate some trees
        for _ in range(5):
            tree_x = random.randint(0, SCREEN_WIDTH - TILE_SIZE)
            tree_y = ground_height - TILE_SIZE * 3
            self.tiles.append({"rect": pygame.Rect(tree_x, tree_y, TILE_SIZE, TILE_SIZE * 3), "type": "tree"})
            
        # Generate some stones
        for _ in range(3):
            stone_x = random.randint(0, SCREEN_WIDTH - TILE_SIZE)
            stone_y = ground_height - TILE_SIZE * 2
            self.tiles.append({"rect": pygame.Rect(stone_x, stone_y, TILE_SIZE * 2, TILE_SIZE * 2), "type": "stone"})
            
    def remove_tile(self, tile):
        if tile in self.tiles:
            self.tiles.remove(tile)
            
    def add_building(self, x, y, blueprint_name):
        building = pygame.Rect(x - 32, y - 32, 64, 64)
        self.buildings.append((building, blueprint_name))
            
    def draw(self, screen):
        # Draw ground and trees
        for tile in self.tiles:
            if tile["type"] == "grass":
                color = GRASS_GREEN
                pygame.draw.rect(screen, color, tile["rect"])
                pygame.draw.rect(screen, (0, 0, 0), tile["rect"], 1)
            elif tile["type"] == "dirt":
                color = DIRT_BROWN
                pygame.draw.rect(screen, color, tile["rect"])
                pygame.draw.rect(screen, (0, 0, 0), tile["rect"], 1)
            elif tile["type"] == "tree":
                # Draw trunk
                trunk_color = (139, 69, 19)
                trunk_rect = pygame.Rect(tile["rect"].x + 8, tile["rect"].y + tile["rect"].height - 16, 16, 16)
                pygame.draw.rect(screen, trunk_color, trunk_rect)
                pygame.draw.rect(screen, (0, 0, 0), trunk_rect, 1)
                
                # Draw leaves (triangle shape)
                leaves_color = (34, 139, 34)
                leaves_points = [
                    (tile["rect"].x, tile["rect"].y + tile["rect"].height - 16),
                    (tile["rect"].x + tile["rect"].width, tile["rect"].y + tile["rect"].height - 16),
                    (tile["rect"].x + tile["rect"].width//2, tile["rect"].y)
                ]
                pygame.draw.polygon(screen, leaves_color, leaves_points)
                pygame.draw.polygon(screen, (0, 0, 0), leaves_points, 1)
            elif tile["type"] == "stone":
                # Draw stone with shading
                color = STONE_GRAY
                pygame.draw.rect(screen, color, tile["rect"])
                # Add highlights
                highlight_color = (150, 150, 150)
                pygame.draw.line(screen, highlight_color, 
                               (tile["rect"].x, tile["rect"].y),
                               (tile["rect"].x + tile["rect"].width, tile["rect"].y), 2)
                pygame.draw.line(screen, highlight_color,
                               (tile["rect"].x, tile["rect"].y),
                               (tile["rect"].x, tile["rect"].y + tile["rect"].height), 2)
                # Add shadows
                shadow_color = (100, 100, 100)
                pygame.draw.line(screen, shadow_color,
                               (tile["rect"].x + tile["rect"].width, tile["rect"].y),
                               (tile["rect"].x + tile["rect"].width, tile["rect"].y + tile["rect"].height), 2)
                pygame.draw.line(screen, shadow_color,
                               (tile["rect"].x, tile["rect"].y + tile["rect"].height),
                               (tile["rect"].x + tile["rect"].width, tile["rect"].y + tile["rect"].height), 2)
                pygame.draw.rect(screen, (0, 0, 0), tile["rect"], 1)
            
        # Draw buildings
        for building, blueprint_name in self.buildings:
            if blueprint_name == "house":
                # Draw house with more detail
                pygame.draw.rect(screen, (100, 100, 100), building)
                # Draw roof
                roof_points = [
                    (building.x, building.y),
                    (building.x + building.width, building.y),
                    (building.x + building.width//2, building.y - 20)
                ]
                pygame.draw.polygon(screen, (139, 69, 19), roof_points)
                # Draw door
                door_rect = pygame.Rect(building.x + building.width//2 - 8,
                                      building.y + building.height - 20,
                                      16, 20)
                pygame.draw.rect(screen, (139, 69, 19), door_rect)
                # Draw window
                window_rect = pygame.Rect(building.x + 8, building.y + 8, 8, 8)
                pygame.draw.rect(screen, (255, 255, 255), window_rect)
            else:
                color = (200, 200, 200)
                pygame.draw.rect(screen, color, building)
            pygame.draw.rect(screen, (0, 0, 0), building, 1)
            
        # Draw particles
        self.particle_system.draw(screen)
        
    def update(self):
        self.particle_system.update()

def main():
    player = Player()
    world = World()
    
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()
                elif event.key == pygame.K_e:
                    player.show_inventory = not player.show_inventory
                elif event.key == pygame.K_b:
                    player.building_system.building_mode = not player.building_system.building_mode
                    if player.building_system.building_mode:
                        player.building_system.current_blueprint = "house"
                    else:
                        player.building_system.current_blueprint = None
                elif player.show_inventory:
                    if event.key in [pygame.K_LEFT, pygame.K_a]:
                        player.selected_slot = (player.selected_slot - 1) % len(player.inventory_slots)
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        player.selected_slot = (player.selected_slot + 1) % len(player.inventory_slots)
                    elif event.key == pygame.K_RETURN:
                        player.switch_tool(player.inventory_slots[player.selected_slot]["name"])
                        player.show_inventory = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    player.use_tool(world)
                    
        # Get keyboard state
        keys = pygame.key.get_pressed()
        if not player.show_inventory:  # Only allow movement when inventory is closed
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                player.move(-PLAYER_SPEED)
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                player.move(PLAYER_SPEED)
            
        # Update
        player.update()
        world.update()
        
        # Draw
        screen.fill(SKY_BLUE)
        world.draw(screen)
        player.draw(screen)
        
        # Update display
        pygame.display.flip()
        clock.tick(60)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 
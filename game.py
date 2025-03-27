import pygame
import random
import sys
import math
from tools import Axe, Pickaxe, Hammer, BuildingSystem
from sprites import Character
from tool_sprites import AxeSprite, PickaxeSprite, HammerSprite
from particles import ParticleSystem
from sound_manager import SoundManager
from ui import Tooltip, NotificationSystem

class Game:
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        pygame.mixer.init()
        
        # Constants
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600
        self.TILE_SIZE = 32
        self.GRAVITY = 0.8
        self.JUMP_FORCE = -15
        self.PLAYER_SPEED = 5
        self.INTERACTION_DISTANCE = 60  # Distance for interacting with objects
        
        # Colors
        self.SKY_BLUE = (135, 206, 235)
        self.GRASS_GREEN = (34, 139, 34)
        self.DIRT_BROWN = (139, 69, 19)
        self.STONE_GRAY = (128, 128, 128)
        self.INVENTORY_BG = (50, 50, 50, 180)
        self.SELECTED_ITEM = (255, 255, 255, 100)
        
        # Set up display
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Chase Run Swim Jump")
        self.clock = pygame.time.Clock()
        
        # Initialize game components
        self.player = Player(self)
        self.world = World(self)
        self.tooltip = Tooltip()
        self.notification_system = NotificationSystem()
        
        # Show initial notification
        self.notification_system.add_notification("Use F to interact with objects", 180)
        
        # Game state
        self.running = True
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.player.show_inventory:
                        # If inventory is open, select the current tool
                        self.player.switch_tool(self.player.inventory_slots[self.player.selected_slot]["name"])
                        self.player.show_inventory = False
                    else:
                        # Otherwise jump
                        self.player.jump()
                elif event.key == pygame.K_e:
                    self.player.show_inventory = not self.player.show_inventory
                elif event.key == pygame.K_b:
                    self.player.building_system.building_mode = not self.player.building_system.building_mode
                    if self.player.building_system.building_mode:
                        self.player.building_system.current_blueprint = "house"
                        self.notification_system.add_notification("Building Mode Activated")
                    else:
                        self.player.building_system.current_blueprint = None
                        self.notification_system.add_notification("Building Mode Deactivated")
                elif event.key == pygame.K_f:
                    self.player.interact(self.world)
                elif event.key == pygame.K_h:
                    self.tooltip.toggle_help()
                elif event.key == pygame.K_1:
                    self.player.quick_select(0)
                elif event.key == pygame.K_2:
                    self.player.quick_select(1)
                elif self.player.show_inventory:
                    if event.key in [pygame.K_LEFT, pygame.K_a]:
                        self.player.selected_slot = (self.player.selected_slot - 1) % len(self.player.inventory_slots)
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        self.player.selected_slot = (self.player.selected_slot + 1) % len(self.player.inventory_slots)
                    elif event.key == pygame.K_RETURN:
                        self.player.switch_tool(self.player.inventory_slots[self.player.selected_slot]["name"])
                        self.player.show_inventory = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Only process mouse clicks when not in inventory mode
                if not self.player.show_inventory:
                    if event.button == 1:  # Left click
                        # Instead of directly using the tool, trigger an interaction if close enough
                        self.player.interact(self.world)
                        
        # Get keyboard state for movement
        keys = pygame.key.get_pressed()
        if not self.player.show_inventory:  # Only allow movement when inventory is closed
            dx = 0
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                dx -= self.PLAYER_SPEED
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                dx += self.PLAYER_SPEED
            if dx != 0:
                self.player.move(dx)
    
    def update(self):
        self.player.update()
        self.world.update()
        self.tooltip.update()
        self.notification_system.update()
        
    def draw(self):
        self.screen.fill(self.SKY_BLUE)
        self.world.draw(self.screen)
        self.player.draw(self.screen)
        self.tooltip.draw(self.screen)
        self.notification_system.draw(self.screen)
        
        # Draw interaction indicators
        closest_object = self.player.get_closest_interactive_object(self.world)
        if closest_object:
            pygame.draw.circle(self.screen, (255, 255, 255, 100), 
                            (closest_object["rect"].centerx, closest_object["rect"].centery), 
                            5, 1)
        
        pygame.display.flip()
        
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()

class Player:
    def __init__(self, game):
        self.game = game
        self.character = Character()
        self.width = self.character.width
        self.height = self.character.height
        self.x = game.SCREEN_WIDTH // 2
        self.y = game.SCREEN_HEIGHT - 200
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
        
        # Ensure we don't go off-screen
        if self.x < 0:
            self.x = 0
        if self.x > self.game.SCREEN_WIDTH - self.width:
            self.x = self.game.SCREEN_WIDTH - self.width
            
    def jump(self):
        if not self.jumping:
            self.vel_y = self.game.JUMP_FORCE
            self.jumping = True
            
    def update(self):
        # Apply gravity
        self.vel_y += self.game.GRAVITY
        self.y += self.vel_y
        
        # Ground collision
        if self.y > self.game.SCREEN_HEIGHT - self.height:
            self.y = self.game.SCREEN_HEIGHT - self.height
            self.vel_y = 0
            self.jumping = False
            
        # Update current tool
        self.tools[self.current_tool].update()
        
        # Update swing animation
        if self.is_swinging:
            self.swing_timer += 1
            if self.swing_timer >= 10:  # Swing animation duration
                self.is_swinging = False
                self.swing_timer = 0
                
    def quick_select(self, slot_index):
        if slot_index < len(self.inventory_slots):
            self.switch_tool(self.inventory_slots[slot_index]["name"])
            self.game.notification_system.add_notification(f"Selected {self.inventory_slots[slot_index]['name'].capitalize()}")
            
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
            
    def get_closest_interactive_object(self, world):
        player_center_x = self.x + self.width // 2
        player_center_y = self.y + self.height // 2
        
        closest_object = None
        closest_distance = float('inf')
        
        for tile in world.tiles:
            if tile["type"] in ["tree", "stone"]:  # Only these are interactive
                tile_center_x = tile["rect"].centerx
                tile_center_y = tile["rect"].centery
                
                distance = math.sqrt((player_center_x - tile_center_x) ** 2 + 
                                    (player_center_y - tile_center_y) ** 2)
                
                if distance < self.game.INTERACTION_DISTANCE and distance < closest_distance:
                    closest_distance = distance
                    closest_object = tile
                    
        return closest_object
        
    def interact(self, world):
        closest_object = self.get_closest_interactive_object(world)
        
        if not closest_object:
            self.game.notification_system.add_notification("Nothing to interact with nearby")
            return
            
        if self.building_system.building_mode:
            if self.tools["hammer"].use():
                self.sound_manager.play("hammer_swing")
                self.is_swinging = True
                self.swing_timer = 0
                
                if self.building_system.build(self.inventory, self.building_system.current_blueprint):
                    # Create building near the player
                    world.add_building(self.x + self.width, self.y + self.height, 
                                     self.building_system.current_blueprint)
                    self.game.notification_system.add_notification(f"Built {self.building_system.current_blueprint}")
                else:
                    self.game.notification_system.add_notification("Not enough resources!")
        else:
            if self.tools[self.current_tool].use():
                # Play tool sound
                self.sound_manager.play(f"{self.current_tool}_swing")
                self.is_swinging = True
                self.swing_timer = 0
                
                if self.current_tool == "axe" and closest_object["type"] == "tree":
                    self.inventory["wood"] += 1
                    world.remove_tile(closest_object)
                    world.particle_system.create_block_break(
                        closest_object["rect"].centerx, closest_object["rect"].centery, 
                        (34, 139, 34))  # Tree color
                    self.sound_manager.play("block_break")
                    self.game.notification_system.add_notification("Collected wood")
                elif self.current_tool == "pickaxe" and closest_object["type"] == "stone":
                    self.inventory["stone"] += 1
                    world.remove_tile(closest_object)
                    world.particle_system.create_block_break(
                        closest_object["rect"].centerx, closest_object["rect"].centery, 
                        self.game.STONE_GRAY)
                    self.sound_manager.play("block_break")
                    self.game.notification_system.add_notification("Collected stone")
                else:
                    self.game.notification_system.add_notification(f"Can't use {self.current_tool} on that")
        
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
        inventory_surface = pygame.Surface((self.game.SCREEN_WIDTH, self.game.SCREEN_HEIGHT), pygame.SRCALPHA)
        inventory_surface.fill(self.game.INVENTORY_BG)
        screen.blit(inventory_surface, (0, 0))
        
        # Draw inventory slots
        slot_size = 64
        start_x = self.game.SCREEN_WIDTH // 2 - (len(self.inventory_slots) * slot_size) // 2
        start_y = self.game.SCREEN_HEIGHT // 2 - slot_size // 2
        
        for i, slot in enumerate(self.inventory_slots):
            x = start_x + i * slot_size
            y = start_y
            
            # Draw slot background
            pygame.draw.rect(screen, (100, 100, 100), (x, y, slot_size, slot_size))
            pygame.draw.rect(screen, (0, 0, 0), (x, y, slot_size, slot_size), 2)
            
            # Draw selected highlight
            if i == self.selected_slot:
                pygame.draw.rect(screen, self.game.SELECTED_ITEM, (x, y, slot_size, slot_size))
            
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

class World:
    def __init__(self, game):
        self.game = game
        self.tiles = []
        self.buildings = []
        self.particle_system = ParticleSystem()
        self.generate_world()
        
    def generate_world(self):
        # Generate ground
        ground_height = self.game.SCREEN_HEIGHT - 100
        for x in range(0, self.game.SCREEN_WIDTH, self.game.TILE_SIZE):
            # Grass layer
            self.tiles.append({"rect": pygame.Rect(x, ground_height, self.game.TILE_SIZE, self.game.TILE_SIZE), "type": "grass"})
            # Dirt layer
            for y in range(ground_height + self.game.TILE_SIZE, self.game.SCREEN_HEIGHT, self.game.TILE_SIZE):
                self.tiles.append({"rect": pygame.Rect(x, y, self.game.TILE_SIZE, self.game.TILE_SIZE), "type": "dirt"})
                
        # Generate some trees
        for _ in range(5):
            tree_x = random.randint(0, self.game.SCREEN_WIDTH - self.game.TILE_SIZE)
            tree_y = ground_height - self.game.TILE_SIZE * 3
            self.tiles.append({"rect": pygame.Rect(tree_x, tree_y, self.game.TILE_SIZE, self.game.TILE_SIZE * 3), "type": "tree"})
            
        # Generate some stones
        for _ in range(3):
            stone_x = random.randint(0, self.game.SCREEN_WIDTH - self.game.TILE_SIZE)
            stone_y = ground_height - self.game.TILE_SIZE * 2
            self.tiles.append({"rect": pygame.Rect(stone_x, stone_y, self.game.TILE_SIZE * 2, self.game.TILE_SIZE * 2), "type": "stone"})
            
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
                color = self.game.GRASS_GREEN
                pygame.draw.rect(screen, color, tile["rect"])
                pygame.draw.rect(screen, (0, 0, 0), tile["rect"], 1)
            elif tile["type"] == "dirt":
                color = self.game.DIRT_BROWN
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
                color = self.game.STONE_GRAY
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

if __name__ == "__main__":
    game = Game()
    game.run() 
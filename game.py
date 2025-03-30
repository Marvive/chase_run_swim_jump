import pygame
import random
import sys
import math
from tools import Axe, Pickaxe, Hammer, Sword, BuildingSystem
from sprites import Character, Princess, Food, Crab, KingCrab
from tool_sprites import AxeSprite, PickaxeSprite, HammerSprite, SwordSprite
from particles import ParticleSystem
from sound_manager import SoundManager
from ui import Tooltip, NotificationSystem
from assets.environment.cloud import create_cloud_variations

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
        self.SWORD_ATTACK_RANGE = 70   # Distance for sword attack
        self.WORLD_WIDTH = 1600  # Wider world for scrolling
        
        # Camera/Scrolling
        self.camera_x = 0
        
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
        
        # Initialize princess NPC
        self.princess = PrincessNPC(self)
        
        # Show initial notification
        self.notification_system.add_notification("Use F to interact with objects", 180)
        self.notification_system.add_notification("Eat food with E to regain health", 180)
        self.notification_system.add_notification("Watch out for crabs when breaking rocks/trees!", 180)
        
        # Game state
        self.running = True
        
        # Death and respawn related
        self.death_screen_active = False
        self.respawn_timer = 0
        self.respawn_delay = 180  # 3 seconds at 60fps
        
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
                    if self.player.show_inventory:
                        self.player.show_inventory = False
                    else:
                        # Try to eat food if health is not full
                        if self.player.health < self.player.max_health:
                            self.player.eat_food()
                        else:
                            self.notification_system.add_notification("Health is already full!")
                elif event.key == pygame.K_i:
                    # Use i key to toggle inventory instead
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
                    if self.player.current_tool == "sword":
                        # Use sword attack when F is pressed with sword equipped
                        self.player.perform_attack(self.world)
                    else:
                        # Otherwise use normal interaction
                        closest_object = self.player.get_closest_interactive_object(self.world)
                        if closest_object:
                            self.player.interact(self.world, closest_object)
                        else:
                            self.notification_system.add_notification("Nothing to interact with nearby")
                elif event.key == pygame.K_h:
                    self.tooltip.toggle_help()
                elif event.key == pygame.K_1:
                    self.player.quick_select(0)
                elif event.key == pygame.K_2:
                    self.player.quick_select(1)
                elif event.key == pygame.K_3:
                    self.player.quick_select(2)
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
                        # NEW LOGIC: Check for sword first
                        if self.player.current_tool == "sword":
                            self.player.perform_attack(self.world)
                        # OLD LOGIC (now in else block):
                        else:
                            # Get the object under the mouse (using world coordinates)
                            mouse_pos = pygame.mouse.get_pos()
                            world_mouse_x = mouse_pos[0] + int(self.camera_x)
                            world_mouse_y = mouse_pos[1]
                            clicked_object = None
                            
                            for tile in self.world.tiles:
                                if tile["type"] in ["tree", "stone"] and tile["rect"].collidepoint(world_mouse_x, world_mouse_y):
                                    clicked_object = tile
                                    break
                                    
                            # Check distance ONLY if an object was clicked
                            if clicked_object:
                                player_center_x = self.player.x + self.player.width // 2
                                player_center_y = self.player.y + self.player.height // 2
                                tile_center_x = clicked_object["rect"].centerx
                                tile_center_y = clicked_object["rect"].centery
                                distance = math.sqrt((player_center_x - tile_center_x) ** 2 + 
                                                    (player_center_y - tile_center_y) ** 2)
                                
                                if distance < self.INTERACTION_DISTANCE:
                                    self.player.interact(self.world, clicked_object)
                                else:
                                    self.notification_system.add_notification("Too far away to interact")
                            # Check for building mode if no object was clicked
                            elif self.player.building_system.building_mode:
                                self.player.interact(self.world)
                            # If not sword, not building, and no object clicked, then nothing happens
                            # (Removed the unnecessary notification here)
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
        # Check if player died
        if self.player.health <= 0 and not self.death_screen_active:
            self.handle_player_death()
            
        # Handle respawn timer if death screen is active
        if self.death_screen_active:
            self.respawn_timer += 1
            if self.respawn_timer >= self.respawn_delay:
                self.respawn_player()
        else:
            # Only update game if player is alive
            self.player.update()
            self.world.update()
            self.tooltip.update()
            self.notification_system.update()
            self.princess.update(self.world)
            
            # Check for player collision with enemies
            self.player.check_enemy_collisions(self.world)
            
            # Update camera position based on player position
            player_center_x = self.player.x + self.player.width // 2
            
            # Set camera to keep player in center of screen
            target_camera_x = player_center_x - self.SCREEN_WIDTH // 2
            
            # Apply camera boundaries
            target_camera_x = max(0, min(target_camera_x, self.WORLD_WIDTH - self.SCREEN_WIDTH))
            
            # Smooth camera movement
            self.camera_x += (target_camera_x - self.camera_x) * 0.1
        
    def draw(self):
        self.screen.fill(self.SKY_BLUE)
        self.world.draw(self.screen, int(self.camera_x))
        self.princess.draw(self.screen, int(self.camera_x))
        
        # Draw player if not in death screen
        if not self.death_screen_active:
            self.player.draw(self.screen, int(self.camera_x))
            
        self.tooltip.draw(self.screen)
        self.notification_system.draw(self.screen)
        
        # Draw player experience bar
        self.player.draw_experience_bar(self.screen)
        
        # Draw death screen if active
        if self.death_screen_active:
            self.draw_death_screen()
        
        # Draw tool help text (varies depending on selected tool)
        if not self.player.show_inventory:
            font = pygame.font.Font(None, 20)
            tool_info = ""
            if self.player.current_tool == "axe":
                tool_info = "Axe: Left-click trees to gather wood"
            elif self.player.current_tool == "pickaxe":
                tool_info = "Pickaxe: Left-click stones to gather stone"
            elif self.player.current_tool == "sword":
                tool_info = "Sword: Left-click or press F to attack nearby crabs"
            elif self.player.building_system.building_mode:
                tool_info = "Building Mode: Left-click to place building"
                
            if tool_info:
                text = font.render(tool_info, True, (255, 255, 255))
                text_bg = pygame.Surface((text.get_width() + 10, text.get_height() + 6), pygame.SRCALPHA)
                text_bg.fill((0, 0, 0, 180))
                self.screen.blit(text_bg, (10, self.SCREEN_HEIGHT - 30))
                self.screen.blit(text, (15, self.SCREEN_HEIGHT - 27))
                
            # Additional controls reminder
            controls = "WASD: Move | SPACE: Jump | E: Eat | I: Inventory | 1-3: Tools | F: Interact"
            controls_text = font.render(controls, True, (255, 255, 255))
            controls_bg = pygame.Surface((controls_text.get_width() + 10, controls_text.get_height() + 6), pygame.SRCALPHA)
            controls_bg.fill((0, 0, 0, 120))
            self.screen.blit(controls_bg, (10, self.SCREEN_HEIGHT - 60))
            self.screen.blit(controls_text, (15, self.SCREEN_HEIGHT - 57))
        
        # Draw interaction indicators
        closest_object = self.player.get_closest_interactive_object(self.world)
        if closest_object:
            pygame.draw.circle(self.screen, (255, 255, 255, 100), 
                            (closest_object["rect"].centerx - int(self.camera_x), closest_object["rect"].centery), 
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

    def handle_player_death(self):
        # Set death screen active
        self.death_screen_active = True
        self.respawn_timer = 0
        
        # Reduce player experience (lose 30% of current experience)
        exp_loss = int(self.player.experience * 0.3)
        self.player.experience = max(0, self.player.experience - exp_loss)
        
        # Show notification
        self.notification_system.add_notification(f"You died! Lost {exp_loss} XP", 180)
        
    def respawn_player(self):
        # Reset death screen
        self.death_screen_active = False
        
        # Restore player health
        self.player.health = self.player.max_health
        
        # Reset player position to center of screen
        self.player.x = self.SCREEN_WIDTH // 2
        ground_height = self.SCREEN_HEIGHT - 100
        self.player.y = ground_height - self.player.height
        
        # Reset camera
        self.camera_x = self.player.x - self.SCREEN_WIDTH // 2
        
        # Show notification
        self.notification_system.add_notification("Respawned!")
        
    def draw_death_screen(self):
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((200, 0, 0, 100))  # Red tint
        self.screen.blit(overlay, (0, 0))
        
        # Draw death message
        font = pygame.font.Font(None, 64)
        text = font.render("YOU DIED!", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(text, text_rect)
        
        # Draw respawn countdown
        seconds_left = (self.respawn_delay - self.respawn_timer) // 60 + 1
        respawn_font = pygame.font.Font(None, 36)
        respawn_text = respawn_font.render(f"Respawning in {seconds_left}...", True, (255, 255, 255))
        respawn_rect = respawn_text.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(respawn_text, respawn_rect)

class Player:
    def __init__(self, game):
        self.game = game
        self.character = Character()
        self.width = self.character.width
        self.height = self.character.height
        self.x = game.SCREEN_WIDTH // 2
        
        # Correct ground level position - ensure player is properly on ground level like trees and rocks
        ground_height = game.SCREEN_HEIGHT - 100  # This is where grass blocks are
        self.y = ground_height - self.height  # Position character so feet touch the ground
        
        self.vel_y = 0
        self.jumping = False
        self.facing_right = True
        self.is_moving = False
        
        # Tools initialization
        self.tools = {
            "axe": Axe(),
            "pickaxe": Pickaxe(),
            "sword": Sword(),
            "hammer": Hammer()
        }
        self.tool_sprites = {
            "axe": AxeSprite(),
            "pickaxe": PickaxeSprite(),
            "sword": SwordSprite(),
            "hammer": HammerSprite()
        }
        self.current_tool = "axe"
        self.inventory = {
            "wood": 0,
            "stone": 0,
            "ore": 0,
            "food": []  # List to store food items
        }
        self.building_system = BuildingSystem()
        self.show_inventory = False
        self.selected_slot = 0
        self.inventory_slots = [
            {"name": "axe", "icon": "🪓"},
            {"name": "pickaxe", "icon": "⛏️"},
            {"name": "sword", "icon": "🗡️"}
        ]
        self.sound_manager = SoundManager()
        self.is_swinging = False
        self.swing_timer = 0
        
        # Health system
        self.max_health = 100
        self.health = self.max_health
        
        # Experience and level system
        self.experience = 0
        self.level = 1
        self.exp_to_next_level = 100  # Base XP needed for level 2
        self.invincibility_frames = 0 # Initialize invincibility frames
        
    def move(self, dx):
        self.x += dx
        
        # Set movement state
        self.is_moving = dx != 0
        
        if dx > 0:
            self.facing_right = True
        elif dx < 0:
            self.facing_right = False
        
        # Allow player to move beyond screen boundaries but within world limits
        if self.x < 0:
            self.x = 0
        if self.x > self.game.WORLD_WIDTH - self.width:
            self.x = self.game.WORLD_WIDTH - self.width
            
    def jump(self):
        if not self.jumping:
            self.vel_y = self.game.JUMP_FORCE
            self.jumping = True
            
    def update(self):
        # Apply gravity
        self.vel_y += self.game.GRAVITY
        self.y += self.vel_y
        
        # Ground collision - ensure player stands on the ground level
        ground_height = self.game.SCREEN_HEIGHT - 100  # This is where grass blocks are
        
        if self.y + self.height > ground_height:
            self.y = ground_height - self.height
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
                
        # Update invincibility frames if player was hit
        if hasattr(self, 'invincibility_frames') and self.invincibility_frames > 0:
            self.invincibility_frames -= 1
        
    def quick_select(self, slot_index):
        if slot_index < len(self.inventory_slots):
            self.switch_tool(self.inventory_slots[slot_index]["name"])
            self.game.notification_system.add_notification(f"Selected {self.inventory_slots[slot_index]['name'].capitalize()}")
            
    def draw(self, screen, camera_x):
        # Draw character with camera offset
        screen_x = self.x - camera_x
        self.character.draw(screen, screen_x, self.y, self.facing_right, self.is_moving)
        
        # Draw current tool or hammer if building
        if self.building_system.building_mode:
            self.tool_sprites["hammer"].draw(screen, 
                                          screen_x + (40 if self.facing_right else -40),
                                          self.y + 20,
                                          self.tools["hammer"].animation_frame * 5,
                                          self.facing_right,
                                          self.is_swinging)
        else:
            self.tool_sprites[self.current_tool].draw(screen,
                                                    screen_x + (40 if self.facing_right else -40),
                                                    self.y + 20,
                                                    self.tools[self.current_tool].animation_frame * 5,
                                                    self.facing_right,
                                                    self.is_swinging)
        
        # Draw resource inventory (fixed position on screen, not affected by camera)
        self.draw_resource_inventory(screen)
        
        # Draw health bar
        self.draw_health_bar(screen)
        
        # Draw experience bar
        self.draw_experience_bar(screen)
        
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
        
    def interact(self, world, clicked_object=None):
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
            if not clicked_object:
                self.game.notification_system.add_notification("Nothing to interact with nearby")
                return
                
            if self.tools[self.current_tool].use():
                # Play tool sound
                self.sound_manager.play(f"{self.current_tool}_swing")
                self.is_swinging = True
                self.swing_timer = 0
                
                if self.current_tool == "axe" and clicked_object["type"] == "tree":
                    self.inventory["wood"] += 1
                    world.remove_tile(clicked_object)
                    world.particle_system.create_block_break(
                        clicked_object["rect"].centerx, clicked_object["rect"].centery, 
                        (34, 139, 34))  # Tree color
                    self.sound_manager.play("block_break")
                    self.game.notification_system.add_notification("Collected wood")
                    
                    # Chance to spawn a crab
                    if random.random() < 0.3:  # 30% chance
                        world.spawn_crab(clicked_object["rect"].centerx, clicked_object["rect"].centery)
                        self.game.notification_system.add_notification("A crab appeared!")
                        
                elif self.current_tool == "pickaxe" and clicked_object["type"] == "stone":
                    self.inventory["stone"] += 1
                    world.remove_tile(clicked_object)
                    world.particle_system.create_block_break(
                        clicked_object["rect"].centerx, clicked_object["rect"].centery, 
                        self.game.STONE_GRAY)
                    self.sound_manager.play("block_break")
                    self.game.notification_system.add_notification("Collected stone")
                    
                    # Chance to spawn a crab
                    if random.random() < 0.4:  # 40% chance
                        world.spawn_crab(clicked_object["rect"].centerx, clicked_object["rect"].centery)
                        self.game.notification_system.add_notification("A crab appeared!")
                        
                else:
                    self.game.notification_system.add_notification(f"Can't use {self.current_tool} on that")
        
    def draw_resource_inventory(self, screen):
        # Draw inventory background
        inventory_y = 10
        for i, (item, count) in enumerate(self.inventory.items()):
            if item != "food":  # Handle regular resources
                pygame.draw.rect(screen, (200, 200, 200), 
                               (10 + i * 100, inventory_y, 90, 30))
                font = pygame.font.Font(None, 24)
                text = font.render(f"{item}: {count}", True, (0, 0, 0))
                screen.blit(text, (15 + i * 100, inventory_y + 5))
        
        # Draw food inventory separately
        food_y = inventory_y + 35
        food_count = len(self.inventory["food"])
        pygame.draw.rect(screen, (200, 200, 200), 
                       (10, food_y, 90, 30))
        font = pygame.font.Font(None, 24)
        text = font.render(f"Food: {food_count}", True, (0, 0, 0))
        screen.blit(text, (15, food_y + 5))
        
        # Draw food icons if any
        if food_count > 0:
            for i, food_item in enumerate(self.inventory["food"][:3]):  # Show up to 3 food items
                food_item.draw(screen, 110 + i * 20, food_y + 7)
    
    def draw_health_bar(self, screen):
        # Draw health bar at the top right corner
        bar_width = 150
        bar_height = 20
        border_width = 2
        x = self.game.SCREEN_WIDTH - bar_width - 10
        y = 10
        
        # Draw border
        pygame.draw.rect(screen, (0, 0, 0), 
                       (x - border_width, y - border_width, 
                        bar_width + border_width * 2, bar_height + border_width * 2))
        
        # Draw background
        pygame.draw.rect(screen, (200, 0, 0), 
                       (x, y, bar_width, bar_height))
        
        # Draw health (green portion)
        health_width = int((self.health / self.max_health) * bar_width)
        pygame.draw.rect(screen, (0, 200, 0), 
                       (x, y, health_width, bar_height))
        
        # Draw health text
        font = pygame.font.Font(None, 20)
        text = font.render(f"{self.health}/{self.max_health}", True, (255, 255, 255))
        text_rect = text.get_rect(center=(x + bar_width//2, y + bar_height//2))
        screen.blit(text, text_rect)
        
    def draw_experience_bar(self, screen):
        # Draw experience bar below health bar
        bar_width = 150
        bar_height = 10
        border_width = 2
        x = self.game.SCREEN_WIDTH - bar_width - 10
        y = 35  # Just below health bar
        
        # Draw border
        pygame.draw.rect(screen, (0, 0, 0), 
                       (x - border_width, y - border_width, 
                        bar_width + border_width * 2, bar_height + border_width * 2))
        
        # Draw background
        pygame.draw.rect(screen, (100, 100, 100), 
                       (x, y, bar_width, bar_height))
        
        # Draw experience (blue portion)
        exp_width = int((self.experience / self.exp_to_next_level) * bar_width)
        pygame.draw.rect(screen, (50, 100, 255), 
                       (x, y, exp_width, bar_height))
        
        # Draw level text above the bar
        font = pygame.font.Font(None, 20)
        text = font.render(f"Level {self.level}", True, (255, 255, 255))
        text_rect = text.get_rect(bottomright=(x + bar_width, y - 2))
        screen.blit(text, text_rect)
        
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

    def eat_food(self):
        # Check if player has food
        if len(self.inventory["food"]) > 0:
            # Get the first food item
            food = self.inventory["food"].pop(0)
            
            # Add health
            self.health = min(self.max_health, self.health + food.healing)
            
            # Show notification
            self.game.notification_system.add_notification(f"Ate {food.type} (+{food.healing} health)")
            
            # Play eating sound
            self.sound_manager.play("block_break")  # Reuse existing sound for now
            
            return True
        else:
            self.game.notification_system.add_notification("No food to eat!")
            return False

    def add_experience(self, amount):
        # Add experience points to player
        self.experience += amount
        
        # Check if player should level up
        if self.experience >= self.exp_to_next_level:
            self.level_up()
            
        # Show notification
        self.game.notification_system.add_notification(f"+{amount} XP")
    
    def level_up(self):
        # Increase player level
        self.level += 1
        
        # Reset experience and increase next level requirement (increasing difficulty)
        self.experience = self.experience - self.exp_to_next_level
        self.exp_to_next_level = int(self.exp_to_next_level * 1.5)  # Each level requires 50% more XP
        
        # Increase max health as bonus
        old_max_health = self.max_health
        self.max_health += 10  # +10 health per level
        self.health += 10  # Also heal player when leveling up
        
        # Play sound effect
        self.sound_manager.play("block_break")  # Reuse sound for now
        
        # Show level up notification
        self.game.notification_system.add_notification(f"Level Up! You are now level {self.level}")
        self.game.notification_system.add_notification(f"Max Health +10 ({old_max_health} → {self.max_health})")
        self.game.notification_system.add_notification(f"Sword Damage +2")
            
    def check_enemy_collisions(self, world):
        # Check if player collides with any enemies - USE WORLD COORDINATES
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        for enemy in world.enemies[:]: # Iterate over a copy
            enemy_obj = enemy["enemy_obj"] # Get the actual enemy object
            # Use enemy's world coordinates for collision check
            enemy_rect = pygame.Rect(enemy["x"], enemy["y"],
                                   enemy_obj.width, enemy_obj.height)

            # Check for simple rectangle collision first
            if player_rect.colliderect(enemy_rect):
                 # Take damage unless player is in invincibility frames
                 if self.invincibility_frames <= 0:
                    damage = enemy_obj.damage # Use enemy's specific damage
                    self.health -= damage
                    
                    if self.health < 0:
                        self.health = 0
                        
                    enemy_name = "King Crab" if isinstance(enemy_obj, KingCrab) else "Crab"
                    self.game.notification_system.add_notification(f"Ouch! {enemy_name} attacked you for {damage} damage!")
                    
                    self.invincibility_frames = 30 
                    self.sound_manager.play("block_break") 
            
    def perform_attack(self, world):
        """Swings the equipped tool (currently only sword logic implemented) 
           and damages enemies in range."""
        # Check cooldown and tool type
        if self.current_tool == "sword" and self.tools["sword"].use():
            self.sound_manager.play("sword_swing")
            self.is_swinging = True
            self.swing_timer = 0

            player_center_x = self.x + self.width // 2
            player_center_y = self.y + self.height // 2
            attack_hit = False # Flag to check if any enemy was hit

            # Check for enemies within sword range and in front of the player
            for enemy in world.enemies[:]: # Iterate over a copy for safe removal
                enemy_obj = enemy["enemy_obj"]
                enemy_center_x = enemy["x"] + enemy_obj.width // 2
                enemy_center_y = enemy["y"] + enemy_obj.height // 2

                distance = math.sqrt((player_center_x - enemy_center_x) ** 2 +
                                   (player_center_y - enemy_center_y) ** 2)

                # Check if enemy is within sword attack range (defined in Game class)
                if distance < self.game.SWORD_ATTACK_RANGE: # Use SWORD_ATTACK_RANGE
                    # Check if enemy is generally in front of the player
                    is_in_front = ((self.facing_right and enemy_center_x >= player_center_x) or
                                   (not self.facing_right and enemy_center_x <= player_center_x))
                    
                    if is_in_front:
                        self.deal_damage_to_enemy(world, enemy) 
                        attack_hit = True
                        # Optional: break here if sword should only hit one target per swing
            
            # If the swing hit nothing, maybe provide feedback?
            if not attack_hit:
                # Attack missed all enemies
                pass
        
        elif self.current_tool == "sword": # Sword was selected but on cooldown
             self.game.notification_system.add_notification("Sword not ready!")
    
    def deal_damage_to_enemy(self, world, enemy):
        """Calculates and applies damage to a specific enemy."""
        enemy_obj = enemy["enemy_obj"]
        
        # Calculate damage based on tool
        damage = 10  # Default damage for non-sword tools
        
        if self.current_tool == "sword":
            # Get sword directly from tools dictionary
            sword = self.tools["sword"]
            # Calculate sword damage based on player level
            damage = sword.get_damage(self.level)
            self.game.notification_system.add_notification(f"Sword attack! {damage} damage")
        
        # Deal damage to enemy
        if enemy_obj.take_damage(damage):
            # Enemy defeated - gain experience
            xp_gain = 150 if isinstance(enemy_obj, KingCrab) else 30  # More XP for King Crab
            self.add_experience(xp_gain)
            
            # Show particles and notification
            enemy_center_x = enemy["x"] + enemy_obj.width // 2
            enemy_center_y = enemy["y"] + enemy_obj.height // 2
            
            enemy_name = "King Crab" if isinstance(enemy_obj, KingCrab) else "Crab"
            world.remove_enemy(enemy)
            world.particle_system.create_block_break(
                enemy_center_x, enemy_center_y, (200, 0, 0))  # Red crab particles
            self.game.notification_system.add_notification(f"Defeated the {enemy_name}!")
            
            # Add special victory message for King Crab
            if isinstance(enemy_obj, KingCrab):
                self.game.notification_system.add_notification("Victory! You defeated the King Crab!", 300)
        else:
            # Enemy hit but not defeated
            enemy_name = "King Crab" if isinstance(enemy_obj, KingCrab) else "Crab"
            self.game.notification_system.add_notification(f"Hit {enemy_name}! {enemy_obj.health} HP left")

class World:
    def __init__(self, game):
        self.game = game
        self.tiles = []
        self.buildings = []
        self.particle_system = ParticleSystem()
        self.clouds = []
        self.enemies = []  # List to store enemy crabs
        
        # Load cloud sprites
        try:
            self.cloud_sprites = create_cloud_variations(self.game.WORLD_WIDTH, self.game.SCREEN_HEIGHT)
        except Exception as e:
            print(f"Error loading cloud sprites: {e}")
            self.cloud_sprites = None
            
        self.initial_resource_count = 0 # Track initial trees/rocks
        self.king_crab_spawned = False # Flag to prevent multiple spawns
        self.generate_world()
        
    def generate_world(self):
        # Generate ground - now wider for scrolling
        ground_height = self.game.SCREEN_HEIGHT - 100
        for x in range(0, self.game.WORLD_WIDTH, self.game.TILE_SIZE):
            # Grass layer
            self.tiles.append({"rect": pygame.Rect(x, ground_height, self.game.TILE_SIZE, self.game.TILE_SIZE), "type": "grass"})
            # Dirt layer
            for y in range(ground_height + self.game.TILE_SIZE, self.game.SCREEN_HEIGHT, self.game.TILE_SIZE):
                self.tiles.append({"rect": pygame.Rect(x, y, self.game.TILE_SIZE, self.game.TILE_SIZE), "type": "dirt"})
                
        # Generate some trees across the wider world - now positioned ABOVE green blocks
        resource_count = 0 # Initialize counter here
        num_trees = 15 # Define number of trees
        for _ in range(num_trees):  
            tree_x = random.randint(0, self.game.WORLD_WIDTH - self.game.TILE_SIZE)
            
            # Place trees on top of the ground rather than partially embedded
            tree_height = random.randint(2, 4) * self.game.TILE_SIZE  # Variable height
            tree_width = random.randint(self.game.TILE_SIZE - 8, self.game.TILE_SIZE + 8)  # Variable width
            tree_y = ground_height - tree_height  # Place on top of ground
            
            self.tiles.append({
                "rect": pygame.Rect(tree_x, tree_y, tree_width, tree_height), 
                "type": "tree",
                "variant": random.randint(0, 2)  # Variation for different tree appearances
            })
            resource_count += 1 # Increment count
            
        # Generate some stones across the wider world - now positioned ABOVE green blocks
        num_stones = 10 # Define number of stones
        for _ in range(num_stones):
            stone_x = random.randint(0, self.game.WORLD_WIDTH - self.game.TILE_SIZE)
            
            # Place stones on top of the ground
            stone_width = random.randint(self.game.TILE_SIZE, self.game.TILE_SIZE * 2)  # Variable width
            stone_height = random.randint(self.game.TILE_SIZE, int(self.game.TILE_SIZE * 1.5))  # Variable height
            stone_y = ground_height - stone_height  # Place on top of ground
            
            self.tiles.append({
                "rect": pygame.Rect(stone_x, stone_y, stone_width, stone_height), 
                "type": "stone",
                "variant": random.randint(0, 2)  # Variation for different stone appearances
            })
            resource_count += 1 # Increment count
            
        self.initial_resource_count = resource_count # Set the total initial count
        print(f"Initial resource count: {self.initial_resource_count}") # Debug print
        
        # Generate static clouds using sprites with more variation
        # Now self.cloud_sprites is guaranteed to be initialized
        if self.cloud_sprites: # Check if sprites were loaded successfully
            for _ in range(8):  # More clouds for the wider world
                cloud_x = random.randint(0, self.game.WORLD_WIDTH)
                cloud_y = random.randint(20, 150)  # More vertical variation
                
                # Choose a random cloud variation
                cloud_sprite = random.choice(self.cloud_sprites)
                
                # Add rotation and flipping for more variety
                flip_x = random.choice([True, False])
                flip_y = random.choice([True, False])
                
                self.clouds.append({
                    "rect": pygame.Rect(cloud_x, cloud_y, cloud_sprite.get_width(), cloud_sprite.get_height()), 
                    "sprite_index": self.cloud_sprites.index(cloud_sprite),
                    "flip_x": flip_x,
                    "flip_y": flip_y
                })
        else:
            # Fallback to simple cloud rects if sprites failed to load
            print("Warning: Cloud sprites not loaded, using fallback rectangles.")
            for _ in range(8):
                cloud_x = random.randint(0, self.game.WORLD_WIDTH)
                cloud_y = random.randint(20, 150)
                cloud_width = random.randint(80, 160)
                cloud_height = random.randint(30, 60)
                self.clouds.append({"rect": pygame.Rect(cloud_x, cloud_y, cloud_width, cloud_height)})
        
    def remove_tile(self, tile):
        if tile in self.tiles:
            tile_type = tile["type"]
            self.tiles.remove(tile)
            # Decrement resource count only if it was a tree or stone
            if tile_type in ["tree", "stone"]:
                self.initial_resource_count -= 1
                print(f"Resource removed. Remaining: {self.initial_resource_count}") # Debug print
                # Check if all resources are cleared and king crab hasn't spawned
                if self.initial_resource_count <= 0 and not self.king_crab_spawned:
                    self.spawn_king_crab()

    def spawn_king_crab(self):
        if not self.king_crab_spawned:
            self.king_crab_spawned = True
            king_crab = KingCrab()
            
            # Spawn near center of the world, on the ground
            spawn_x = self.game.WORLD_WIDTH // 2 - king_crab.width // 2
            ground_height = self.game.SCREEN_HEIGHT - 100
            spawn_y = ground_height - king_crab.height
            
            self.enemies.append({
                "enemy_obj": king_crab, # Use "enemy_obj" key for consistency
                "x": spawn_x,
                "y": spawn_y,
                "vel_x": 0,
                "vel_y": 0,
                "facing_right": random.choice([True, False])
            })
            self.game.notification_system.add_notification("The KING CRAB has appeared!", 300)
            # Maybe play a boss sound? self.game.sound_manager.play("boss_spawn")

    def add_building(self, x, y, blueprint_name):
        building = pygame.Rect(x - 32, y - 32, 64, 64)
        self.buildings.append((building, blueprint_name))
            
    def draw(self, screen, camera_x):
        # Draw clouds with camera offset
        for cloud in self.clouds:
            # Adjust position based on camera
            screen_x = cloud["rect"].x - camera_x
            
            # Early culling - don't draw clouds outside the screen
            if screen_x + cloud["rect"].width < 0 or screen_x > self.game.SCREEN_WIDTH:
                continue
            
            # Draw cloud sprite if available
            if self.cloud_sprites and "sprite_index" in cloud:
                cloud_sprite = self.cloud_sprites[cloud["sprite_index"]]
                
                # Apply flipping for more variety if specified
                if cloud.get("flip_x", False) or cloud.get("flip_y", False):
                    cloud_sprite = pygame.transform.flip(cloud_sprite, cloud.get("flip_x", False), cloud.get("flip_y", False))
                
                screen.blit(cloud_sprite, (screen_x, cloud["rect"].y))
            else:
                # Fallback to basic cloud drawing
                cloud_color = (255, 100, 100)  # Red clouds
                y = cloud["rect"].y
                width = cloud["rect"].width
                height = cloud["rect"].height
                
                # Draw a simple cloud shape
                pygame.draw.ellipse(screen, cloud_color, 
                                  (screen_x, y, width, height))
                pygame.draw.ellipse(screen, (255, 150, 150), 
                                  (screen_x + width//4, y - height//4, width//2, height//2))
        
        # Draw ground and trees with camera offset
        for tile in self.tiles:
            # Create a copy of the rect for drawing with camera offset
            screen_rect = pygame.Rect(tile["rect"].x - camera_x, tile["rect"].y, 
                                    tile["rect"].width, tile["rect"].height)
            
            # Early culling - don't draw tiles outside the screen
            if screen_rect.right < 0 or screen_rect.left > self.game.SCREEN_WIDTH:
                continue
                
            if tile["type"] == "grass":
                color = self.game.GRASS_GREEN
                pygame.draw.rect(screen, color, screen_rect)
                pygame.draw.rect(screen, (0, 0, 0), screen_rect, 1)
            elif tile["type"] == "dirt":
                color = self.game.DIRT_BROWN
                pygame.draw.rect(screen, color, screen_rect)
                pygame.draw.rect(screen, (0, 0, 0), screen_rect, 1)
            elif tile["type"] == "tree":
                # Get variation for tree appearance
                variant = tile.get("variant", 0)
                
                # Define consistent tree parts based on variant
                # All trees have a trunk and foliage
                
                # Common trunk features - all trunks are brown and positioned at bottom of tree rect
                trunk_colors = [(139, 69, 19), (120, 60, 20), (160, 82, 45)]  # Different browns
                trunk_color = trunk_colors[variant]
                
                # Different trunk widths and heights for variants
                trunk_widths = [12, 14, 10]  # Width for each variant
                trunk_width = trunk_widths[variant]
                
                # Trunk always takes bottom portion of tree
                trunk_height = screen_rect.height // 3
                trunk_rect = pygame.Rect(
                    screen_rect.x + (screen_rect.width - trunk_width) // 2,
                    screen_rect.y + screen_rect.height - trunk_height,
                    trunk_width, trunk_height
                )
                
                # Draw trunk
                pygame.draw.rect(screen, trunk_color, trunk_rect)
                pygame.draw.rect(screen, (0, 0, 0), trunk_rect, 1)  # Black outline
                
                # Draw foliage - different styles for each variant
                # Define foliage colors - different green shades
                leaf_colors = [(34, 139, 34), (45, 150, 45), (25, 120, 25)]
                leaves_color = leaf_colors[variant]
                
                # Leaf area is always above trunk
                leaf_area_height = screen_rect.height - trunk_height
                leaf_area_y = screen_rect.y
                
                if variant == 0:
                    # Pine tree style - triangular shape
                    # Draw triangular leaf section
                    leaf_points = [
                        (screen_rect.x + screen_rect.width // 2, leaf_area_y),  # Top point
                        (screen_rect.x + screen_rect.width // 5, leaf_area_y + leaf_area_height),  # Bottom left
                        (screen_rect.x + screen_rect.width * 4 // 5, leaf_area_y + leaf_area_height)  # Bottom right
                    ]
                    pygame.draw.polygon(screen, leaves_color, leaf_points)
                    pygame.draw.polygon(screen, (0, 0, 0), leaf_points, 1)  # Black outline
                    
                    # Add some detail to the pine tree
                    # Secondary triangle for texture
                    second_points = [
                        (screen_rect.x + screen_rect.width // 2, leaf_area_y + leaf_area_height // 3),  # Top point
                        (screen_rect.x + screen_rect.width // 4, leaf_area_y + leaf_area_height),  # Bottom left
                        (screen_rect.x + screen_rect.width * 3 // 4, leaf_area_y + leaf_area_height)  # Bottom right
                    ]
                    pygame.draw.polygon(screen, (leaves_color[0] - 10, leaves_color[1] - 10, leaves_color[2] - 10), second_points)
                    
                elif variant == 1:
                    # Oak tree style - round bushy top
                    # Draw circular leaf section
                    leaf_radius = min(screen_rect.width // 2, leaf_area_height)
                    center_x = screen_rect.x + screen_rect.width // 2
                    center_y = leaf_area_y + leaf_area_height // 2 - leaf_radius // 3  # Moved up slightly
                    
                    # Draw main foliage circle
                    pygame.draw.circle(screen, leaves_color, (center_x, center_y), leaf_radius)
                    pygame.draw.circle(screen, (0, 0, 0), (center_x, center_y), leaf_radius, 1)  # Black outline
                    
                    # Add some smaller circles around the main one for a bushy look
                    smaller_radius = leaf_radius * 2 // 3
                    offsets = [(leaf_radius // 2, -leaf_radius // 3), (-leaf_radius // 2, -leaf_radius // 3),
                              (0, -leaf_radius // 2), (leaf_radius // 3, leaf_radius // 3)]
                    
                    for offset_x, offset_y in offsets:
                        pygame.draw.circle(screen, leaves_color, (center_x + offset_x, center_y + offset_y), smaller_radius)
                
                else:
                    # Maple tree style - layered foliage
                    # Draw a series of progressively smaller rectangles
                    layer_height = leaf_area_height // 3
                    
                    # Bottom layer (widest)
                    bottom_layer = pygame.Rect(
                        screen_rect.x, 
                        leaf_area_y + leaf_area_height - layer_height,
                        screen_rect.width,
                        layer_height
                    )
                    
                    # Middle layer
                    middle_layer = pygame.Rect(
                        screen_rect.x + screen_rect.width // 6,
                        leaf_area_y + leaf_area_height - layer_height * 2,
                        screen_rect.width * 2 // 3,
                        layer_height
                    )
                    
                    # Top layer (narrowest)
                    top_layer = pygame.Rect(
                        screen_rect.x + screen_rect.width // 3,
                        leaf_area_y,
                        screen_rect.width // 3,
                        layer_height
                    )
                    
                    # Draw all layers
                    pygame.draw.rect(screen, leaves_color, bottom_layer)
                    pygame.draw.rect(screen, leaves_color, middle_layer)
                    pygame.draw.rect(screen, leaves_color, top_layer)
                    
                    # Draw outlines
                    pygame.draw.rect(screen, (0, 0, 0), bottom_layer, 1)
                    pygame.draw.rect(screen, (0, 0, 0), middle_layer, 1)
                    pygame.draw.rect(screen, (0, 0, 0), top_layer, 1)
            elif tile["type"] == "stone":
                # Get variation for stone appearance
                variant = tile.get("variant", 0)
                
                # Different base colors based on variant
                base_colors = [
                    self.game.STONE_GRAY,  # Standard gray
                    (140, 140, 140),       # Lighter gray
                    (110, 110, 110)        # Darker gray
                ]
                base_color = base_colors[variant]
                
                # Draw main stone block
                pygame.draw.rect(screen, base_color, screen_rect)
                
                # Static, non-random patterns for each stone type
                if variant == 0:
                    # Boulder-like stone with cracks
                    # Main outline
                    pygame.draw.rect(screen, (0, 0, 0), screen_rect, 1)
                    
                    # Add cracks
                    crack_color = (100, 100, 100)
                    
                    # Horizontal crack across middle
                    mid_y = screen_rect.y + screen_rect.height // 2
                    start_x = screen_rect.x + screen_rect.width // 4
                    pygame.draw.line(screen, crack_color, 
                                   (start_x, mid_y),
                                   (start_x + screen_rect.width // 2, mid_y + screen_rect.height // 6), 2)
                    
                    # Vertical crack
                    mid_x = screen_rect.x + screen_rect.width // 2
                    start_y = screen_rect.y + screen_rect.height // 3
                    pygame.draw.line(screen, crack_color, 
                                   (mid_x, start_y),
                                   (mid_x - screen_rect.width // 5, start_y + screen_rect.height // 2), 2)
                    
                    # Add highlights at top edges
                    highlight_color = (170, 170, 170)
                    pygame.draw.line(screen, highlight_color, 
                                   (screen_rect.x, screen_rect.y),
                                   (screen_rect.x + screen_rect.width // 2, screen_rect.y), 2)
                    pygame.draw.line(screen, highlight_color, 
                                   (screen_rect.x, screen_rect.y),
                                   (screen_rect.x, screen_rect.y + screen_rect.height // 3), 2)
                
                elif variant == 1:
                    # Ore-like stone with embedded crystals
                    pygame.draw.rect(screen, (0, 0, 0), screen_rect, 1)
                    
                    # Draw embedded "crystals" or ore deposits
                    crystal_color = (180, 180, 190)  # Silvery
                    
                    # Fixed pattern of crystal locations
                    crystal_spots = [
                        (0.2, 0.3, 0.1),  # x, y, size as proportions of the stone
                        (0.5, 0.2, 0.15),
                        (0.7, 0.6, 0.12),
                        (0.3, 0.7, 0.08)
                    ]
                    
                    for spot_x, spot_y, spot_size in crystal_spots:
                        x = screen_rect.x + int(screen_rect.width * spot_x)
                        y = screen_rect.y + int(screen_rect.height * spot_y)
                        size = int(min(screen_rect.width, screen_rect.height) * spot_size)
                        
                        # Draw irregular crystal shape
                        points = [
                            (x, y),
                            (x + size, y + size//2),
                            (x + size//2, y + size),
                            (x - size//3, y + size//2)
                        ]
                        pygame.draw.polygon(screen, crystal_color, points)
                        pygame.draw.polygon(screen, (100, 100, 100), points, 1)
                
                else:
                    # Smooth river stone with gradient
                    # Draw as an ellipse rather than rectangle
                    pygame.draw.ellipse(screen, base_color, screen_rect)
                    pygame.draw.ellipse(screen, (0, 0, 0), screen_rect, 1)
                    
                    # Add smooth gradient effect
                    # Top-left half is lighter
                    light_rect = pygame.Rect(
                        screen_rect.x,
                        screen_rect.y,
                        screen_rect.width // 2,
                        screen_rect.height // 2
                    )
                    
                    highlight_color = (min(base_color[0] + 30, 255), 
                                      min(base_color[1] + 30, 255), 
                                      min(base_color[2] + 30, 255))
                    
                    # Draw lighter section with transparency for gradient effect
                    highlight_surface = pygame.Surface((light_rect.width, light_rect.height), pygame.SRCALPHA)
                    highlight_surface.fill((highlight_color[0], highlight_color[1], highlight_color[2], 100))
                    screen.blit(highlight_surface, light_rect)
            
        # Draw buildings with camera offset
        for building, blueprint_name in self.buildings:
            screen_building = pygame.Rect(building.x - camera_x, building.y, 
                                        building.width, building.height)
                                        
            # Early culling
            if screen_building.right < 0 or screen_building.left > self.game.SCREEN_WIDTH:
                continue
                
            if blueprint_name == "house":
                # Draw house with more detail
                pygame.draw.rect(screen, (100, 100, 100), screen_building)
                # Draw roof
                roof_points = [
                    (screen_building.x, screen_building.y),
                    (screen_building.x + screen_building.width, screen_building.y),
                    (screen_building.x + screen_building.width//2, screen_building.y - 20)
                ]
                pygame.draw.polygon(screen, (139, 69, 19), roof_points)
                # Draw door
                door_rect = pygame.Rect(screen_building.x + screen_building.width//2 - 8,
                                      screen_building.y + screen_building.height - 20,
                                      16, 20)
                pygame.draw.rect(screen, (139, 69, 19), door_rect)
                # Draw window
                window_rect = pygame.Rect(screen_building.x + 8, screen_building.y + 8, 8, 8)
                pygame.draw.rect(screen, (255, 255, 255), window_rect)
            else:
                color = (200, 200, 200)
                pygame.draw.rect(screen, color, screen_building)
            pygame.draw.rect(screen, (0, 0, 0), screen_building, 1)
            
        # Draw particles with camera offset
        self.particle_system.draw(screen, camera_x)
        
        # Draw enemies with camera offset
        for enemy in self.enemies:
            # Calculate screen position
            screen_x = enemy["x"] - camera_x
            
            # Only draw if on screen
            if (screen_x + enemy["enemy_obj"].width > 0 and 
                screen_x < self.game.SCREEN_WIDTH):
                enemy["enemy_obj"].draw(screen, screen_x, enemy["y"], enemy["facing_right"])
                
                # Fix health bar to correctly use enemy's max_health
                enemy_obj = enemy["enemy_obj"]
                
                # Get max health based on enemy type
                max_health = 150 if isinstance(enemy_obj, KingCrab) else 30
                
                health_pct = enemy_obj.health / max_health
                bar_width = enemy_obj.width
                bar_height = 3
                
                # Background (red)
                pygame.draw.rect(screen, (200, 0, 0), 
                               (screen_x, enemy["y"] - bar_height - 2, 
                                bar_width, bar_height))
                
                # Health remaining (green)
                pygame.draw.rect(screen, (0, 200, 0), 
                               (screen_x, enemy["y"] - bar_height - 2, 
                                int(bar_width * health_pct), bar_height))

    def update(self):
        self.particle_system.update()
        
        # Update enemies
        for enemy in self.enemies:
            # Update crab enemy
            enemy["enemy_obj"].update()
            
            # Simple movement AI
            if random.random() < 0.02:  # 2% chance to change direction
                enemy["vel_x"] = random.choice([-1, 0, 1])
                
            # Update position
            enemy["x"] += enemy["vel_x"]
            
            # Update facing direction
            if enemy["vel_x"] > 0:
                enemy["facing_right"] = True
            elif enemy["vel_x"] < 0:
                enemy["facing_right"] = False
                
            # Apply world boundaries
            if enemy["x"] < 0:
                enemy["x"] = 0
                enemy["vel_x"] = abs(enemy["vel_x"])  # Bounce off edge
            elif enemy["x"] > self.game.WORLD_WIDTH - enemy["enemy_obj"].width:
                enemy["x"] = self.game.WORLD_WIDTH - enemy["enemy_obj"].width
                enemy["vel_x"] = -abs(enemy["vel_x"])  # Bounce off edge
                
            # Apply gravity
            enemy["vel_y"] += self.game.GRAVITY * 0.5  # Half gravity effect
            enemy["y"] += enemy["vel_y"]
            
            # Ground collision
            ground_height = self.game.SCREEN_HEIGHT - 100
            if enemy["y"] + enemy["enemy_obj"].height > ground_height:
                enemy["y"] = ground_height - enemy["enemy_obj"].height
                enemy["vel_y"] = 0

    def spawn_crab(self, x, y):
        # Create new crab enemy
        crab = Crab()
        
        # Position the crab at the given location
        crab_x = x - crab.width // 2
        crab_y = y - crab.height // 2
        
        # Randomize initial direction
        facing_right = random.choice([True, False])
        
        # Add to enemies list
        self.enemies.append({
            "enemy_obj": crab,
            "x": crab_x,
            "y": crab_y,
            "vel_x": random.choice([-1, 1]),  # Random initial direction
            "vel_y": 0,
            "facing_right": facing_right
        })
        
    def remove_enemy(self, enemy):
        if enemy in self.enemies:
            self.enemies.remove(enemy)

class PrincessNPC:
    def __init__(self, game):
        self.game = game
        self.princess = Princess()
        self.width = self.princess.width
        self.height = self.princess.height
        
        # Place princess at random position on ground
        ground_height = game.SCREEN_HEIGHT - 100
        self.x = random.randint(0, game.WORLD_WIDTH - self.width)
        self.y = ground_height - self.height
        
        # Movement properties
        self.speed = 1  # Slower than player
        self.facing_right = random.choice([True, False])
        self.move_timer = 0
        self.move_duration = random.randint(120, 300)  # 2-5 seconds at 60fps
        self.rest_timer = 0
        self.rest_duration = random.randint(120, 240)  # 2-4 seconds
        self.is_moving = False
        
        # Food creation properties
        self.food_timer = 0
        self.food_cooldown = 600  # 10 seconds at 60fps
        self.is_cooking = False
        self.cooking_timer = 0
        self.cooking_duration = 180  # 3 seconds
        
        # Food items that can be created
        self.food_types = ["apple", "cake", "cookie"]
        
    def update(self, world):
        # Handle princess movement
        if self.is_moving:
            # Move princess
            if self.facing_right:
                self.x += self.speed
                # Check if reached world boundary
                if self.x > self.game.WORLD_WIDTH - self.width:
                    self.x = self.game.WORLD_WIDTH - self.width
                    self.facing_right = False
            else:
                self.x -= self.speed
                # Check if reached world boundary
                if self.x < 0:
                    self.x = 0
                    self.facing_right = True
                    
            # Update move timer
            self.move_timer += 1
            if self.move_timer >= self.move_duration:
                self.move_timer = 0
                self.is_moving = False
                self.rest_timer = 0
        else:
            # Princess is resting, possibly cooking
            self.rest_timer += 1
            
            # Check if should start cooking
            if not self.is_cooking and random.random() < 0.01:  # 1% chance each frame
                self.is_cooking = True
                self.cooking_timer = 0
                
            # Handle cooking
            if self.is_cooking:
                self.cooking_timer += 1
                if self.cooking_timer >= self.cooking_duration:
                    self.cook_food()
                    self.is_cooking = False
            
            # Check if rest period is over
            if self.rest_timer >= self.rest_duration:
                self.is_moving = True
                self.move_timer = 0
                self.move_duration = random.randint(120, 300)
                # 50% chance to change direction
                if random.random() < 0.5:
                    self.facing_right = not self.facing_right
                    
        # Food timer
        self.food_timer += 1
        if self.food_timer >= self.food_cooldown:
            self.food_timer = 0
            # Create food if not cooking already
            if not self.is_cooking and random.random() < 0.5:  # 50% chance
                self.is_cooking = True
                self.cooking_timer = 0
        
    def draw(self, screen, camera_x):
        # Calculate screen position
        screen_x = self.x - camera_x
        
        # Only draw if on screen
        if screen_x + self.width > 0 and screen_x < self.game.SCREEN_WIDTH:
            # Draw princess - pass is_moving to princess draw method
            self.princess.draw(screen, screen_x, self.y, self.facing_right, self.is_moving)
            
            # If cooking, draw a cooking indicator
            if self.is_cooking:
                # Draw cooking bubble
                bubble_radius = 8
                bubble_x = screen_x + (self.width if self.facing_right else 0)
                bubble_y = self.y - bubble_radius * 2
                
                # Draw white bubble
                pygame.draw.circle(screen, (255, 255, 255), (bubble_x, bubble_y), bubble_radius)
                pygame.draw.circle(screen, (0, 0, 0), (bubble_x, bubble_y), bubble_radius, 1)
                
                # Draw food icon inside bubble
                # For simplicity, just draw a small colored circle representing food
                food_color = (255, 0, 0)  # Red for food
                pygame.draw.circle(screen, food_color, (bubble_x, bubble_y), bubble_radius // 2)
    
    def cook_food(self):
        # Create a random food item
        food_type = random.choice(self.food_types)
        food = Food(food_type)
        
        # Add food to player's inventory
        self.game.player.inventory["food"].append(food)
        
        # Show notification
        self.game.notification_system.add_notification(f"Princess made {food_type} for you!")

if __name__ == "__main__":
    game = Game()
    game.run() 
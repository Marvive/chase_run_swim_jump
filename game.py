import pygame
import random
import sys
import math
from tools import Axe, Pickaxe, Hammer, Sword, BuildingSystem
from sprites import Character, Princess, Food, Crab, KingCrab, Fish, Dinosaur
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
        self.SWIM_SPEED = 3  # Swimming speed in water
        
        # Level system
        self.current_level = 1
        self.level_transition_active = False
        self.transition_timer = 0
        self.transition_delay = 180  # 3 seconds at 60fps
        
        # Camera/Scrolling
        self.camera_x = 0
        
        # Colors
        self.SKY_BLUE = (135, 206, 235)
        self.GRASS_GREEN = (34, 139, 34)
        self.DIRT_BROWN = (139, 69, 19)
        self.STONE_GRAY = (128, 128, 128)
        self.WATER_BLUE = (64, 164, 223)
        self.INVENTORY_BG = (50, 50, 50, 180)
        self.SELECTED_ITEM = (255, 255, 255, 100)
        
        # Set up display
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Chase Run Swim Jump")
        self.clock = pygame.time.Clock()
        
        # Initialize game components
        self.player = Player(self)
        self.world = World(self, self.current_level)
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
                            # Only show notification if cooldown has expired
                            if self.player.last_interaction_notification <= 0:
                                self.notification_system.add_notification("Nothing to interact with nearby")
                                self.player.last_interaction_notification = self.player.notification_cooldown
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
        # Handle level transition if active
        elif self.level_transition_active:
            self.transition_timer += 1
            if self.transition_timer >= self.transition_delay:
                self.load_next_level()
        else:
            # Only update game if player is alive and not transitioning
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
            
            # Check if all enemies are defeated (and we have at least 1 enemy spawned)
            if len(self.world.enemies) == 0 and self.world.enemies_spawned > 0:
                if self.current_level == 1 and self.world.king_crab_spawned and self.world.king_crab_defeated:
                    # Start level transition to dinosaur level
                    self.start_level_transition()
                    
    def start_level_transition(self):
        """Start transition to the next level"""
        self.level_transition_active = True
        self.transition_timer = 0
        self.notification_system.add_notification("Level Complete! Loading next level...", 180)
                    
    def load_next_level(self):
        """Load the next level when transition completes"""
        self.current_level += 1
        self.level_transition_active = False
        
        # Reset camera
        self.camera_x = 0
        
        # Reset player position (but keep stats)
        self.player.x = 100
        ground_height = self.SCREEN_HEIGHT - 100
        self.player.y = ground_height - self.player.height
        
        # Create a new world for this level
        self.world = World(self, self.current_level)
        
        # Show level notification
        if self.current_level == 2:
            self.notification_system.add_notification("Level 2: Dinosaur Jungle", 180)
            self.notification_system.add_notification("Find the lake to swim and catch fish!", 180)
        
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
        
        # Draw level transition screen if active
        if self.level_transition_active:
            self.draw_transition_screen()
        
        # Draw tool help text (varies depending on selected tool)
        if not self.player.show_inventory and not self.level_transition_active:
            font = pygame.font.Font(None, 20)
            tool_info = ""
            if self.player.current_tool == "axe":
                tool_info = "Axe: Left-click trees to gather wood"
            elif self.player.current_tool == "pickaxe":
                tool_info = "Pickaxe: Left-click stones to gather stone"
            elif self.player.current_tool == "sword":
                tool_info = "Sword: Left-click or press F to attack nearby enemies"
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
            
            # Display current level
            level_text = font.render(f"Level {self.current_level}", True, (255, 255, 255))
            level_bg = pygame.Surface((level_text.get_width() + 10, level_text.get_height() + 6), pygame.SRCALPHA)
            level_bg.fill((0, 0, 0, 180))
            self.screen.blit(level_bg, (self.SCREEN_WIDTH - level_text.get_width() - 20, 10))
            self.screen.blit(level_text, (self.SCREEN_WIDTH - level_text.get_width() - 15, 13))
        
        # Draw interaction indicators
        closest_object = self.player.get_closest_interactive_object(self.world)
        if closest_object:
            pygame.draw.circle(self.screen, (255, 255, 255, 100), 
                            (closest_object["rect"].centerx - int(self.camera_x), closest_object["rect"].centery), 
                            5, 1)
        
        pygame.display.flip()
        
    def draw_transition_screen(self):
        """Draw the level transition screen"""
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # Dark overlay
        self.screen.blit(overlay, (0, 0))
        
        # Draw level complete message
        font = pygame.font.Font(None, 64)
        text = font.render(f"Level {self.current_level} Complete!", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(text, text_rect)
        
        # Draw next level message
        next_level_font = pygame.font.Font(None, 36)
        next_level_text = next_level_font.render(f"Loading Level {self.current_level + 1}...", True, (255, 255, 255))
        next_level_rect = next_level_text.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(next_level_text, next_level_rect)
        
        # Draw loading bar
        bar_width = 300
        bar_height = 20
        border = 2
        progress = min(1.0, self.transition_timer / self.transition_delay)
        
        # Border
        pygame.draw.rect(self.screen, (255, 255, 255), 
                      (self.SCREEN_WIDTH // 2 - bar_width // 2 - border, 
                       self.SCREEN_HEIGHT // 2 + 80 - border,
                       bar_width + border * 2, bar_height + border * 2))
        
        # Progress
        pygame.draw.rect(self.screen, (0, 255, 0), 
                      (self.SCREEN_WIDTH // 2 - bar_width // 2, 
                       self.SCREEN_HEIGHT // 2 + 80,
                       int(bar_width * progress), bar_height))
        
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
        self.swimming = False  # Track if player is swimming
        
        # Add notification cooldown timer
        self.last_interaction_notification = 0  # Frame counter for notification cooldown
        self.notification_cooldown = 120  # 2 seconds at 60fps
        
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
        # Movement speed depends on if swimming or not
        if self.swimming:
            dx *= 0.7  # Slower movement in water
            
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
            if self.swimming:
                # Gentler "jump" in water - more like swimming upward
                self.vel_y = self.game.JUMP_FORCE * 0.5
            else:
                # Normal jump on land
                self.vel_y = self.game.JUMP_FORCE
                
            self.jumping = True
            
    def update(self):
        # Check if player is in water (only for level 2+)
        self.check_water_collision()
        
        # Apply different physics based on swimming state
        if self.swimming:
            # Lighter gravity when swimming
            self.vel_y += self.game.GRAVITY * 0.3
            
            # Cap falling speed in water
            self.vel_y = min(self.vel_y, 2.0)
            
            # Apply water drag - slow down vertical movement
            if abs(self.vel_y) > 0.1:
                self.vel_y *= 0.95
        else:
            # Regular gravity on land
            self.vel_y += self.game.GRAVITY
            
        # Update position
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
        if self.invincibility_frames > 0:
            self.invincibility_frames -= 1
            
        # Update notification cooldown
        if self.last_interaction_notification > 0:
            self.last_interaction_notification -= 1
    
    def check_water_collision(self):
        """Check if player is in water and update swimming state"""
        # Only check for water in level 2+
        if self.game.current_level < 2:
            self.swimming = False
            return
            
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Check if player collides with any water tiles
        for water in self.game.world.water_tiles:
            water_rect = pygame.Rect(water["rect"])
            
            if player_rect.colliderect(water_rect):
                if not self.swimming:
                    # Just entered water - show notification
                    self.game.notification_system.add_notification("Swimming! Use WASD to swim and catch fish", 120)
                self.swimming = True
                return
                
        # Not in water
        self.swimming = False
        
    def quick_select(self, slot_index):
        if slot_index < len(self.inventory_slots):
            self.switch_tool(self.inventory_slots[slot_index]["name"])
            self.game.notification_system.add_notification(f"Selected {self.inventory_slots[slot_index]['name'].capitalize()}")
            
    def draw(self, screen, camera_x):
        # Draw character with camera offset
        screen_x = self.x - camera_x
        
        # Use swimming state for character animation
        self.character.draw(screen, screen_x, self.y, self.facing_right, self.is_moving, self.swimming)
        
        # If swimming, don't show tools
        if not self.swimming:
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
                # Only show notification if cooldown has expired
                if self.last_interaction_notification <= 0:
                    self.game.notification_system.add_notification("Nothing to interact with nearby")
                    self.last_interaction_notification = self.notification_cooldown
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
            # Update the health in the dictionary to match the object's health
            enemy["health"] = enemy_obj.health
            
            enemy_name = "King Crab" if isinstance(enemy_obj, KingCrab) else "Crab"
            self.game.notification_system.add_notification(f"Hit {enemy_name}! {enemy_obj.health} HP left")

class World:
    def __init__(self, game, level=1):
        self.game = game
        self.tiles = []
        self.trees = []
        self.clouds = []
        self.crabs = []  # List to store crabs (level 1)
        self.dinosaurs = []  # List to store dinosaurs (level 2+)
        self.water_tiles = []  # List to store water tiles (level 2+)
        self.grass_tiles = []
        self.dirt_tiles = []
        self.stone_tiles = []
        self.tree_tiles = []
        self.resources = []
        self.fish = []  # List to store fish (level 2+)
        self.special_areas = []
        self.enemies = []  # General enemies list
        self.buildings = []  # Buildings and structures
        self.particle_system = ParticleSystem()
        
        # Load cloud sprites
        self.cloud_sprites = []
        cloud_img1 = pygame.Surface((60, 30), pygame.SRCALPHA)
        pygame.draw.ellipse(cloud_img1, (255, 255, 255, 180), (0, 0, 60, 30))
        self.cloud_sprites.append(cloud_img1)
        
        cloud_img2 = pygame.Surface((80, 40), pygame.SRCALPHA)
        pygame.draw.ellipse(cloud_img2, (255, 255, 255, 150), (0, 0, 80, 40))
        self.cloud_sprites.append(cloud_img2)
        
        cloud_img3 = pygame.Surface((100, 50), pygame.SRCALPHA)
        pygame.draw.ellipse(cloud_img3, (255, 255, 255, 130), (0, 0, 100, 50))
        self.cloud_sprites.append(cloud_img3)
        
        self.enemies_spawned = 0  # Track how many enemies we've spawned
        self.king_crab_spawned = False  # Flag to prevent multiple king crab spawns
        self.king_crab_defeated = False  # Flag to track if king crab was defeated
        
        self.generate_world(level)
    
    def generate_world(self, level):
        """Generate world based on current level"""
        if level == 1:
            self.generate_crab_beach()
        else:
            self.generate_dinosaur_jungle()
    
    def generate_crab_beach(self):
        """Generate level 1: Crab Beach"""
        # Generate ground - now wider for scrolling
        ground_height = self.game.SCREEN_HEIGHT - 100
        for x in range(0, self.game.WORLD_WIDTH, self.game.TILE_SIZE):
            # Grass layer
            self.tiles.append({"rect": pygame.Rect(x, ground_height, self.game.TILE_SIZE, self.game.TILE_SIZE), "type": "grass"})
            # Dirt layer
            for y in range(ground_height + self.game.TILE_SIZE, self.game.SCREEN_HEIGHT, self.game.TILE_SIZE):
                self.tiles.append({"rect": pygame.Rect(x, y, self.game.TILE_SIZE, self.game.TILE_SIZE), "type": "dirt"})
                
        # Generate trees and stones as before
        resource_count = 0
        num_trees = 15
        for _ in range(num_trees):  
            tree_x = random.randint(0, self.game.WORLD_WIDTH - self.game.TILE_SIZE)
            tree_height = random.randint(2, 4) * self.game.TILE_SIZE
            tree_width = random.randint(self.game.TILE_SIZE - 8, self.game.TILE_SIZE + 8)
            tree_y = ground_height - tree_height
            
            self.tiles.append({
                "rect": pygame.Rect(tree_x, tree_y, tree_width, tree_height), 
                "type": "tree",
                "variant": random.randint(0, 2)
            })
            resource_count += 1
            
        num_stones = 10
        for _ in range(num_stones):
            stone_x = random.randint(0, self.game.WORLD_WIDTH - self.game.TILE_SIZE)
            stone_width = random.randint(self.game.TILE_SIZE, self.game.TILE_SIZE * 2)
            stone_height = random.randint(self.game.TILE_SIZE, int(self.game.TILE_SIZE * 1.5))
            stone_y = ground_height - stone_height
            
            self.tiles.append({
                "rect": pygame.Rect(stone_x, stone_y, stone_width, stone_height), 
                "type": "stone",
                "variant": random.randint(0, 2)
            })
            resource_count += 1
            
        self.initial_resource_count = resource_count
        print(f"Initial resource count: {self.initial_resource_count}")
        
        # Generate clouds as in original code
        self.generate_clouds()
    
    def generate_dinosaur_jungle(self):
        """Generate a jungle world with dinosaurs"""
        # World dimensions
        world_width = 100
        world_height = 30
        
        # Generate ground terrain with more variation
        ground_height = 15
        
        # Generate terrain with various heights
        terrain_heights = [ground_height] * world_width
        
        # Create some hills and valleys
        for i in range(5, world_width - 5, 10):
            # Random hill or valley height
            hill_height = random.randint(2, 4)
            hill_width = random.randint(5, 10)
            
            # 50% chance for hill, 50% for valley
            if random.random() > 0.5:
                # Create hill
                for j in range(hill_width):
                    if i + j < world_width:
                        # Smoother hill using sine wave
                        height_mod = hill_height * math.sin(j * math.pi / hill_width)
                        terrain_heights[i + j] = ground_height - round(height_mod)
            else:
                # Create valley
                for j in range(hill_width):
                    if i + j < world_width:
                        # Smoother valley using sine wave
                        height_mod = hill_height * math.sin(j * math.pi / hill_width)
                        terrain_heights[i + j] = ground_height + round(height_mod)
        
        # Generate ground tiles based on terrain heights
        for x in range(world_width):
            for y in range(world_height):
                # Determine tile type based on depth and position
                if y == terrain_heights[x]:
                    # Surface layer - grass
                    rect = pygame.Rect(x * self.game.TILE_SIZE, y * self.game.TILE_SIZE, self.game.TILE_SIZE, self.game.TILE_SIZE)
                    tile = {
                        "rect": rect,
                        "type": "grass",
                        "x": x * self.game.TILE_SIZE,
                        "y": y * self.game.TILE_SIZE
                    }
                    self.tiles.append(tile)
                elif y > terrain_heights[x] and y < terrain_heights[x] + 3:
                    # Subsurface layer - dirt
                    rect = pygame.Rect(x * self.game.TILE_SIZE, y * self.game.TILE_SIZE, self.game.TILE_SIZE, self.game.TILE_SIZE)
                    tile = {
                        "rect": rect,
                        "type": "dirt",
                        "x": x * self.game.TILE_SIZE,
                        "y": y * self.game.TILE_SIZE
                    }
                    self.tiles.append(tile)
                elif y >= terrain_heights[x] + 3:
                    # Deep layer - stone
                    rect = pygame.Rect(x * self.game.TILE_SIZE, y * self.game.TILE_SIZE, self.game.TILE_SIZE, self.game.TILE_SIZE)
                    tile = {
                        "type": "stone",
                        "rect": rect,
                        "x": x * self.game.TILE_SIZE,
                        "y": y * self.game.TILE_SIZE
                    }
                    self.tiles.append(tile)
        
        # Level 2+ has a lake/water area
        # Create a lake area in the middle of the map
        lake_x = world_width // 3
        lake_width = world_width // 3
        lake_y = ground_height - 1
        lake_depth = 4
        
        # Create water tiles with proper collision rectangles
        for x in range(lake_x, lake_x + lake_width):
            for y in range(lake_y, lake_y + lake_depth):
                rect = pygame.Rect(x * self.game.TILE_SIZE, y * self.game.TILE_SIZE, self.game.TILE_SIZE, self.game.TILE_SIZE)
                self.water_tiles.append({
                    "rect": rect,
                    "x": x * self.game.TILE_SIZE,
                    "y": y * self.game.TILE_SIZE
                })
                # Remove any existing tiles at this position
                self.tiles = [tile for tile in self.tiles if not 
                             (tile["x"] == x * self.game.TILE_SIZE and tile["y"] == y * self.game.TILE_SIZE)]
        
        # Add solid ground under the lake
        for x in range(lake_x, lake_x + lake_width):
            y = lake_y + lake_depth
            rect = pygame.Rect(x * self.game.TILE_SIZE, y * self.game.TILE_SIZE, self.game.TILE_SIZE, self.game.TILE_SIZE)
            tile = {
                "rect": rect,
                "type": "stone",
                "x": x * self.game.TILE_SIZE,
                "y": y * self.game.TILE_SIZE
            }
            self.tiles.append(tile)
        
        # Add some fish to the water
        for _ in range(8):
            fish_x = random.randint(lake_x, lake_x + lake_width - 1) * self.game.TILE_SIZE + random.randint(0, self.game.TILE_SIZE)
            fish_y = random.randint(lake_y, lake_y + lake_depth - 1) * self.game.TILE_SIZE + random.randint(0, self.game.TILE_SIZE)
            
            # Use the Fish class from this file (game.py)
            fish = Fish(self.game, fish_x, fish_y)
            self.resources.append(fish)
        
        # Initialize resource count
        resource_count = 0
        
        # Add jungle trees (more than on the beach)
        for _ in range(20):
            x = random.randint(5, world_width - 5)
            # Don't place trees in the lake
            if not (lake_x <= x < lake_x + lake_width):
                # Find the ground height at this position
                y = terrain_heights[x]
                tree_height = random.randint(3, 5) * self.game.TILE_SIZE
                tree_width = random.randint(self.game.TILE_SIZE - 8, self.game.TILE_SIZE + 8)
                
                # Place tree on top of the ground
                tree_x = x * self.game.TILE_SIZE
                tree_y = y * self.game.TILE_SIZE - tree_height
                
                # Add tree as a tile (same format as level 1 trees)
                self.tiles.append({
                    "rect": pygame.Rect(tree_x, tree_y, tree_width, tree_height),
                    "type": "tree",
                    "variant": random.randint(0, 2),
                    "x": tree_x,
                    "y": tree_y
                })
                resource_count += 1
        
        # Add dinosaurs
        for _ in range(5):
            x = random.randint(10, world_width - 10) * self.game.TILE_SIZE
            y = 0  # Will be placed on ground in the Dinosaur class
            dinosaur_obj = Dinosaur()  # Create the dinosaur sprite
            
            # Add dinosaur with the same structure as other enemies
            self.enemies.append({
                "enemy_obj": dinosaur_obj,
                "x": x,
                "y": y,
                "width": 48,
                "height": 48,
                "vel_x": random.choice([-1, 1]),
                "vel_y": 0,
                "facing_right": random.choice([True, False]),
                "health": dinosaur_obj.health,
                "max_health": dinosaur_obj.max_health
            })
            
            # Increment enemy counter
            self.enemies_spawned += 1
        
        # Add resource nodes
        for _ in range(15):
            x = random.randint(5, world_width - 5)
            # Don't place resources in the lake
            if not (lake_x <= x < lake_x + lake_width):
                y = terrain_heights[x] - 1  # Place on top of ground
                resource_type = random.choice(["wood", "stone", "gold"])
                # Create a resource dictionary instead of class
                
                # Instead of placing resources as tiles, add them as resources with proper visibility
                resource_height = self.game.TILE_SIZE
                resource_width = self.game.TILE_SIZE
                resource_x = x * self.game.TILE_SIZE
                resource_y = y * self.game.TILE_SIZE - resource_height
                
                resource = {
                    "x": resource_x,
                    "y": resource_y,
                    "type": resource_type,
                    "health": 30,
                    "rect": pygame.Rect(resource_x, resource_y, resource_width, resource_height)
                }
                self.resources.append(resource)
                if resource_type in ["stone", "wood"]:
                    resource_count += 1
        
        # Set initial resource count
        self.initial_resource_count = resource_count
        print(f"Initial resource count: {self.initial_resource_count}")
    
    def generate_clouds(self):
        """Generate clouds for any level"""
        if self.cloud_sprites:
            for _ in range(8):
                cloud_x = random.randint(0, self.game.WORLD_WIDTH)
                cloud_y = random.randint(20, 150)
                
                cloud_sprite = random.choice(self.cloud_sprites)
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
                
    def spawn_fish(self, x, y):
        """Spawn a fish in the lake"""
        fish = Fish()  # We'll need to create this class
        
        # Position the fish
        fish_x = x - fish.width // 2
        fish_y = y - fish.height // 2
        
        # Randomize initial direction
        facing_right = random.choice([True, False])
        
        # Add to fish list
        self.fish.append({
            "fish_obj": fish,
            "x": fish_x,
            "y": fish_y,
            "vel_x": random.choice([-0.5, 0.5]) * 2,  # Slower movement
            "vel_y": random.choice([-0.3, 0.3]),  # Some vertical movement
            "facing_right": facing_right
        })
        
    def spawn_dinosaur(self, x, y):
        """Spawn a dinosaur enemy"""
        dinosaur = Dinosaur()  # We'll need to create this class
        
        # Position the dinosaur
        dino_x = x - dinosaur.width // 2
        dino_y = y - dinosaur.height // 2
        
        # Randomize initial direction
        facing_right = random.choice([True, False])
        
        # Add to enemies list directly with consistent format
        self.enemies.append({
            "enemy_obj": dinosaur,
            "x": dino_x,
            "y": dino_y,
            "vel_x": random.choice([-1, 1]),
            "vel_y": 0,
            "facing_right": facing_right,
            "health": dinosaur.health,
            "max_health": dinosaur.max_health
        })
        
        # Increment enemy counter
        self.enemies_spawned += 1

    def draw(self, screen, camera_x, camera_y=0):
        # Draw tiles with camera offset
        for tile in self.tiles:
            # Handle both old-style rect tiles and new-style x,y tiles
            if "x" in tile:
                screen_x = tile["x"] - camera_x
                screen_y = tile["y"] - camera_y
                tile_width = self.game.TILE_SIZE
                tile_height = self.game.TILE_SIZE
            else:
                screen_x = tile["rect"].x - camera_x
                screen_y = tile["rect"].y
                tile_width = tile["rect"].width
                tile_height = tile["rect"].height
            
            # Only draw if on screen
            if (screen_x > -tile_width and screen_x < self.game.SCREEN_WIDTH and
                screen_y > -tile_height and screen_y < self.game.SCREEN_HEIGHT):
                if tile["type"] == "grass":
                    pygame.draw.rect(screen, (100, 200, 100), (screen_x, screen_y, tile_width, tile_height))
                elif tile["type"] == "dirt":
                    pygame.draw.rect(screen, (139, 69, 19), (screen_x, screen_y, tile_width, tile_height))
                elif tile["type"] == "stone":
                    pygame.draw.rect(screen, (128, 128, 128), (screen_x, screen_y, tile_width, tile_height))
                elif tile["type"] == "tree":
                    # Draw tree trunk
                    trunk_width = 16
                    trunk_height = tile_height * 0.6
                    trunk_x = screen_x + (tile_width - trunk_width) // 2
                    trunk_y = screen_y + tile_height - trunk_height
                    pygame.draw.rect(screen, (139, 69, 19), (trunk_x, trunk_y, trunk_width, trunk_height))
                    
                    # Draw tree leaves
                    leaf_radius = tile_width * 0.6
                    leaf_x = screen_x + tile_width // 2
                    leaf_y = screen_y + tile_height // 3
                    pygame.draw.circle(screen, (34, 139, 34), (leaf_x, leaf_y), leaf_radius)
        
        # Draw water tiles with blue color and transparency
        for water in self.water_tiles:
            if "x" in water:
                screen_x = water["x"] - camera_x
                screen_y = water["y"] - camera_y
            else:
                screen_x = water["rect"].x - camera_x
                screen_y = water["rect"].y
            
            if (screen_x > -self.game.TILE_SIZE and screen_x < self.game.SCREEN_WIDTH and
                screen_y > -self.game.TILE_SIZE and screen_y < self.game.SCREEN_HEIGHT):
                # Draw water with transparency and wave effect
                water_surface = pygame.Surface((self.game.TILE_SIZE, self.game.TILE_SIZE), pygame.SRCALPHA)
                # Animate water color slightly based on time
                blue_val = 164 + int(10 * math.sin(pygame.time.get_ticks() / 500))
                water_surface.fill((64, blue_val, 223, 180))  # Blue with alpha
                screen.blit(water_surface, (screen_x, screen_y))
        
        # Draw all resources
        for resource in self.resources:
            # Check if resource is an object or a dictionary
            if isinstance(resource, dict):
                # Draw dictionary-type resources
                screen_x = resource["x"] - camera_x
                screen_y = resource["y"] - camera_y
                
                # Only draw if on screen
                if (screen_x > -self.game.TILE_SIZE and screen_x < self.game.SCREEN_WIDTH and
                    screen_y > -self.game.TILE_SIZE and screen_y < self.game.SCREEN_HEIGHT):
                    if resource["type"] == "wood":
                        pygame.draw.rect(screen, (139, 69, 19), (screen_x, screen_y, self.game.TILE_SIZE, self.game.TILE_SIZE))
                    elif resource["type"] == "stone":
                        pygame.draw.rect(screen, (128, 128, 128), (screen_x, screen_y, self.game.TILE_SIZE, self.game.TILE_SIZE))
                    elif resource["type"] == "gold":
                        pygame.draw.rect(screen, (255, 215, 0), (screen_x, screen_y, self.game.TILE_SIZE, self.game.TILE_SIZE))
            else:
                # Draw object resources - this path is likely never used now
                screen_x = resource.x - camera_x
                screen_y = resource.y - camera_y
                
                # Only draw if on screen
                if (screen_x > -resource.width and screen_x < self.game.SCREEN_WIDTH and
                    screen_y > -resource.height and screen_y < self.game.SCREEN_HEIGHT):
                    # Call the object's draw method with the correct parameters
                    resource.draw(screen, screen_x, screen_y)
                    
        # Draw all enemies with camera offset
        for enemy in self.enemies:
            # Calculate screen position
            screen_x = enemy["x"] - camera_x
            
            # Get enemy size based on the type
            width = 0
            if "width" in enemy:
                width = enemy["width"]
            else:
                # Use enemy_obj if available
                width = enemy["enemy_obj"].width
            
            # Only draw if on screen
            if screen_x + width > 0 and screen_x < self.game.SCREEN_WIDTH:
                # Draw the enemy
                enemy["enemy_obj"].draw(screen, screen_x, enemy["y"], enemy["facing_right"])
                
                # Display health bar for enemy
                if "health" in enemy and "max_health" in enemy:
                    health = enemy["health"]
                    max_health = enemy["max_health"]
                    # Draw health bar
                    health_width = 30
                    health_height = 4
                    health_x = screen_x + (width / 2) - (health_width / 2)
                    health_y = enemy["y"] - 10
                    
                    # Background (red)
                    pygame.draw.rect(screen, (255, 0, 0), (health_x, health_y, health_width, health_height))
                    
                    # Foreground (green) - scaled by health percentage
                    health_percent = health / max_health
                    pygame.draw.rect(screen, (0, 255, 0), 
                                    (health_x, health_y, health_width * health_percent, health_height))
        
        # Draw clouds
        for cloud in self.clouds:
            # Cloud follows screen, not world (parallax effect)
            # Handle x in rect or directly in cloud
            if "x" in cloud:
                cloud_x = cloud["x"] - (camera_x * 0.1)  # Clouds move at 1/10 the speed
                cloud_y = cloud["y"]
            else:
                cloud_x = cloud["rect"].x - (camera_x * 0.1)
                cloud_y = cloud["rect"].y
                
            # Draw the cloud sprite
            sprite_index = cloud.get("sprite_index", 0)
            if self.cloud_sprites and sprite_index < len(self.cloud_sprites):
                screen.blit(self.cloud_sprites[sprite_index], (cloud_x, cloud_y))
        
    def update(self):
        self.particle_system.update()
        
        # Update fish movement if in level 2+
        if self.game.current_level >= 2:
            for fish in self.resources[:]:  # Use copy for safe removal
                if isinstance(fish, Fish):  # Only process Fish objects
                    fish.update()
                    
                    # Check if fish has been eaten by player
                    if self.game.player.swimming and self.check_fish_collision(fish):
                        # Give player health and remove fish
                        self.game.player.health = min(self.game.player.max_health, 
                                                self.game.player.health + fish.healing)
                        self.game.notification_system.add_notification(f"Ate fish! +{fish.healing} Health")
                        self.resources.remove(fish)
                        
                        # Spawn a new fish to replace it
                        lake_start_x = 100
                        lake_width = self.game.WORLD_WIDTH // 4
                        fish_x = lake_start_x + random.randint(0, lake_width - 20)
                        fish_y = self.game.SCREEN_HEIGHT - 100 + random.randint(10, 70)
                        new_fish = Fish(self.game, fish_x, fish_y)
                        self.resources.append(new_fish)
        
        # Update enemies (crabs or dinosaurs)
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
            "vel_x": 0,
            "vel_y": 0,
            "facing_right": facing_right,
            "health": crab.health,
            "max_health": crab.max_health
        })
        
    def remove_enemy(self, enemy):
        if enemy in self.enemies:
            # Check if it was the King Crab
            if isinstance(enemy["enemy_obj"], KingCrab):
                self.king_crab_defeated = True
                
            self.enemies.remove(enemy)

    def check_fish_collision(self, fish):
        """Check if player has collided with a fish while swimming"""
        player = self.game.player
        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
        fish_rect = pygame.Rect(fish.x, fish.y, fish.width, fish.height)
        
        return player_rect.colliderect(fish_rect)

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
                "facing_right": random.choice([True, False]),
                "health": king_crab.health,
                "max_health": king_crab.max_health
            })
            
            # Increment enemy counter
            self.enemies_spawned += 1
            
            self.game.notification_system.add_notification("The KING CRAB has appeared!", 300)
            # Maybe play a boss sound? self.game.sound_manager.play("boss_spawn")

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

class Fish:
    """Fish resource that can be caught for health recovery"""
    def __init__(self, game, x, y):
        self.game = game
        self.x = x
        self.y = y
        self.width = 16
        self.height = 12
        self.type = "fish"
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Fish sprite
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Fish colors
        self.body_color = (230, 150, 90)  # Orange fish body
        self.tail_color = (240, 180, 100)  # Tail color
        self.eye_color = (0, 0, 0)  # Black eye
        
        # Fish stats
        self.healing = 10  # Health gained when eaten
        
        # Create simple fish sprite
        # Body
        for x in range(4, 12):
            for y in range(2, 10):
                if ((x-8)**2 + (y-6)**2 < 16):  # Oval shape
                    pygame.draw.rect(self.surface, self.body_color, (x, y, 1, 1))
        
        # Tail
        for x in range(1, 5):
            for y in range(3, 9):
                if abs(y-6) < (x+2):  # Triangle shape
                    pygame.draw.rect(self.surface, self.tail_color, (x, y, 1, 1))
        
        # Eye
        pygame.draw.rect(self.surface, self.eye_color, (10, 5, 2, 2))
        
        # Animation
        self.facing_right = random.choice([True, False])
        self.speed = random.uniform(0.2, 0.5)
        self.movement_timer = 0
        self.movement_change = random.randint(60, 120)
        
    def update(self):
        # Simple fish movement - back and forth in water
        self.movement_timer += 1
        if self.movement_timer >= self.movement_change:
            self.movement_timer = 0
            self.movement_change = random.randint(60, 120)
            self.facing_right = not self.facing_right
            
        # Move fish
        if self.facing_right:
            self.x += self.speed
        else:
            self.x -= self.speed
            
        # Update rect
        self.rect.x = self.x
        self.rect.y = self.y
        
    def draw(self, screen, x, y):
        # Only draw if on screen
        if (x > -self.width and x < self.game.SCREEN_WIDTH and
            y > -self.height and y < self.game.SCREEN_HEIGHT):
            
            # Flip surface if facing left
            if self.facing_right:
                screen.blit(self.surface, (x, y))
            else:
                flipped = pygame.transform.flip(self.surface, True, False)
                screen.blit(flipped, (x, y))
                
    def collect(self, player):
        # Heal player when fish is collected
        player.health = min(player.health + 20, player.max_health)
        self.game.notification_system.add_notification("+20 Health from Fish!", 60)
        return True  # Return True to indicate it was collected

if __name__ == "__main__":
    game = Game()
    game.run() 
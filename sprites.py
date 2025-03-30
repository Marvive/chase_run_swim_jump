import pygame
import os
import math
import random

class SpriteSheet:
    def __init__(self, image, frame_width, frame_height, frames, animation_speed):
        self.sheet = image
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.frames = frames
        self.animation_speed = animation_speed
        self.current_frame = 0
        self.animation_timer = 0
        
    def get_frame(self):
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % self.frames
            
        x = self.current_frame * self.frame_width
        y = 0
        return pygame.Rect(x, y, self.frame_width, self.frame_height)
        
    def draw(self, screen, x, y, facing_right=True):
        frame = self.get_frame()
        if facing_right:
            screen.blit(self.sheet, (x, y), frame)
        else:
            flipped = pygame.transform.flip(self.sheet.subsurface(frame), True, False)
            screen.blit(flipped, (x, y))

class Character:
    def __init__(self):
        # Create a 32-bit style character sprite with more detail
        self.width = 32
        self.height = 48
        
        # Create base surface
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Define our pixel size for 32-bit style (smaller pixels)
        pixel_size = 2  # Reduced from 4 for more detail
        
        # Enhanced color palette for 32-bit style
        skin_color = (255, 200, 150)
        skin_shadow = (220, 170, 130)
        hair_color = (80, 50, 20)
        hair_highlight = (110, 70, 30)
        shirt_color = (40, 60, 150)
        shirt_highlight = (60, 80, 180)
        shirt_shadow = (30, 45, 120)
        pants_color = (60, 40, 90)
        pants_highlight = (80, 55, 120)
        pants_shadow = (45, 30, 70)
        
        # Draw character with more detail
        
        # Draw head with shading
        for x in range(5, 11):
            for y in range(2, 8):
                # Base skin
                color = skin_color
                # Add shading/highlight based on position
                if x < 7:  # Left side shadow
                    color = skin_shadow
                pygame.draw.rect(self.surface, color, 
                               (x * pixel_size, y * pixel_size, 
                                pixel_size, pixel_size))
        
        # Hair with highlights
        for x in range(5, 11):
            for y in range(1, 3):
                color = hair_color
                if x % 3 == 0:  # Occasional highlight streaks
                    color = hair_highlight
                pygame.draw.rect(self.surface, color, 
                               (x * pixel_size, y * pixel_size, pixel_size, pixel_size))
        
        # Side hair
        for y in range(2, 6):
            # Left side hair
            pygame.draw.rect(self.surface, hair_color, 
                           (4 * pixel_size, y * pixel_size, pixel_size, pixel_size))
            # Right side hair
            pygame.draw.rect(self.surface, hair_color, 
                           (11 * pixel_size, y * pixel_size, pixel_size, pixel_size))
        
        # Eyes with more detail
        # Left eye
        pygame.draw.rect(self.surface, (255, 255, 255), 
                       (6 * pixel_size, 4 * pixel_size, 2 * pixel_size, pixel_size))
        pygame.draw.rect(self.surface, (0, 0, 0), 
                       (7 * pixel_size, 4 * pixel_size, pixel_size, pixel_size))
        
        # Right eye
        pygame.draw.rect(self.surface, (255, 255, 255), 
                       (9 * pixel_size, 4 * pixel_size, 2 * pixel_size, pixel_size))
        pygame.draw.rect(self.surface, (0, 0, 0), 
                       (9 * pixel_size, 4 * pixel_size, pixel_size, pixel_size))
        
        # Mouth
        pygame.draw.rect(self.surface, (200, 100, 100), 
                       (8 * pixel_size, 6 * pixel_size, pixel_size, pixel_size))
        
        # Draw body with shading
        # Torso with shading
        for x in range(4, 12):
            for y in range(8, 16):
                color = shirt_color
                if x < 6:  # Left side shadow
                    color = shirt_shadow
                elif x > 9:  # Right side highlight
                    color = shirt_highlight
                pygame.draw.rect(self.surface, color, 
                               (x * pixel_size, y * pixel_size, 
                                pixel_size, pixel_size))
        
        # Add shirt details - collar
        for x in range(7, 9):
            pygame.draw.rect(self.surface, shirt_highlight, 
                           (x * pixel_size, 8 * pixel_size, pixel_size, pixel_size))
        
        # Draw arms with shading
        # Left arm
        for y in range(8, 16):
            color = skin_color
            if y > 12:  # Shadow at bottom
                color = skin_shadow
            pygame.draw.rect(self.surface, color, 
                           (2 * pixel_size, y * pixel_size, 2 * pixel_size, pixel_size))
        
        # Right arm
        for y in range(8, 16):
            color = skin_color
            if y < 11:  # Highlight at top
                color = skin_shadow
            pygame.draw.rect(self.surface, color, 
                           (12 * pixel_size, y * pixel_size, 2 * pixel_size, pixel_size))
        
        # Draw legs with shading
        # Left leg
        for x in range(4, 8):
            for y in range(16, 24):
                color = pants_color
                if x < 6:  # Left side shadow
                    color = pants_shadow
                pygame.draw.rect(self.surface, color, 
                               (x * pixel_size, y * pixel_size, 
                                pixel_size, pixel_size))
        
        # Right leg
        for x in range(8, 12):
            for y in range(16, 24):
                color = pants_color
                if x > 9:  # Right side highlight
                    color = pants_highlight
                pygame.draw.rect(self.surface, color, 
                               (x * pixel_size, y * pixel_size, 
                                pixel_size, pixel_size))
        
        # Feet
        # Left shoe
        for x in range(4, 8):
            pygame.draw.rect(self.surface, (30, 30, 30), 
                           (x * pixel_size, 24 * pixel_size, pixel_size, pixel_size))
        # Right shoe
        for x in range(8, 12):
            pygame.draw.rect(self.surface, (30, 30, 30), 
                           (x * pixel_size, 24 * pixel_size, pixel_size, pixel_size))
                                
        # Create walking animation frames with smoother transitions
        self.walking_frames = []
        
        # Standing frame
        self.walking_frames.append(self.surface.copy())
        
        # Walking frame 1 - legs slightly apart
        frame1 = self.surface.copy()
        # Clear leg area
        for x in range(4, 12):
            for y in range(16, 25):
                pygame.draw.rect(frame1, (0, 0, 0, 0), 
                               (x * pixel_size, y * pixel_size, 
                                pixel_size, pixel_size))
        
        # Draw legs in new position
        # Left leg moved left and forward
        for x in range(2, 6):
            for y in range(16, 24):
                color = pants_color
                if x < 4:  # Left side shadow
                    color = pants_shadow
                # Make leg slightly shorter to simulate forward motion
                if y < 22:
                    pygame.draw.rect(frame1, color, 
                                   (x * pixel_size, y * pixel_size, 
                                    pixel_size, pixel_size))
        # Left shoe
        for x in range(2, 6):
            pygame.draw.rect(frame1, (30, 30, 30), 
                          (x * pixel_size, 22 * pixel_size, pixel_size, pixel_size))
                          
        # Right leg moved right and backward
        for x in range(10, 14):
            for y in range(16, 25):
                color = pants_color
                if x > 12:  # Right side highlight
                    color = pants_highlight
                # Make leg slightly longer to simulate backward motion
                pygame.draw.rect(frame1, color, 
                               (x * pixel_size, y * pixel_size, 
                                pixel_size, pixel_size))
        # Right shoe
        for x in range(10, 14):
            pygame.draw.rect(frame1, (30, 30, 30), 
                          (x * pixel_size, 24 * pixel_size, pixel_size, pixel_size))
        
        self.walking_frames.append(frame1)
        
        # Walking frame 2 - opposite leg movement
        frame2 = self.surface.copy()
        # Clear leg area
        for x in range(4, 12):
            for y in range(16, 25):
                pygame.draw.rect(frame2, (0, 0, 0, 0), 
                               (x * pixel_size, y * pixel_size, 
                                pixel_size, pixel_size))
        
        # Draw legs in new position
        # Left leg moved forward and right
        for x in range(6, 10):
            for y in range(16, 25):
                color = pants_color
                if x < 8:  # Left side shadow
                    color = pants_shadow
                # Make leg slightly longer to simulate backward motion
                pygame.draw.rect(frame2, color, 
                               (x * pixel_size, y * pixel_size, 
                                pixel_size, pixel_size))
        # Left shoe
        for x in range(6, 10):
            pygame.draw.rect(frame2, (30, 30, 30), 
                          (x * pixel_size, 24 * pixel_size, pixel_size, pixel_size))
        
        # Right leg moved backward and left
        for x in range(8, 12):
            for y in range(16, 23):
                color = pants_color
                if x > 10:  # Right side highlight
                    color = pants_highlight
                # Make leg slightly shorter to simulate forward motion
                pygame.draw.rect(frame2, color, 
                               (x * pixel_size, y * pixel_size, 
                                pixel_size, pixel_size))
        # Right shoe
        for x in range(8, 12):
            pygame.draw.rect(frame2, (30, 30, 30), 
                          (x * pixel_size, 22 * pixel_size, pixel_size, pixel_size))
        
        self.walking_frames.append(frame2)
        
        # Create swimming animation
        self.swimming_frames = []
        
        # Swimming base - similar to standing but with arms out
        swimming_base = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Copy the torso and head from the standing frame
        for x in range(4, 12):
            for y in range(1, 16):
                if x >= 4 and x < 12 and y >= 1 and y < 16:
                    color = self.surface.get_at((x * pixel_size, y * pixel_size))
                    if color.a > 0:  # Only copy non-transparent pixels
                        pygame.draw.rect(swimming_base, color, 
                                      (x * pixel_size, y * pixel_size, pixel_size, pixel_size))
        
        # Draw arms in swimming position - extended horizontally
        skin_color = (255, 200, 150)
        skin_shadow = (220, 170, 130)
        
        # Left arm extended
        for y in range(10, 12):
            for x in range(0, 4):
                color = skin_color if x > 1 else skin_shadow
                pygame.draw.rect(swimming_base, color, 
                               (x * pixel_size, y * pixel_size, pixel_size, pixel_size))
        
        # Right arm extended
        for y in range(10, 12):
            for x in range(12, 16):
                color = skin_color if x < 14 else skin_shadow
                pygame.draw.rect(swimming_base, color, 
                               (x * pixel_size, y * pixel_size, pixel_size, pixel_size))
        
        # Swim frame 1 - legs together
        swim_frame1 = swimming_base.copy()
        for x in range(6, 10):
            for y in range(16, 22):
                pygame.draw.rect(swim_frame1, pants_color, 
                               (x * pixel_size, y * pixel_size, pixel_size, pixel_size))
        
        # Swim frame 2 - legs apart (kicking)
        swim_frame2 = swimming_base.copy()
        # Left leg out
        for x in range(4, 7):
            for y in range(16, 23):
                pygame.draw.rect(swim_frame2, pants_color, 
                               (x * pixel_size, y * pixel_size, pixel_size, pixel_size))
        # Right leg out
        for x in range(9, 12):
            for y in range(16, 23):
                pygame.draw.rect(swim_frame2, pants_color, 
                               (x * pixel_size, y * pixel_size, pixel_size, pixel_size))
        
        # Store swimming frames
        self.swimming_frames.append(swim_frame1)
        self.swimming_frames.append(swim_frame2)
        
        # Animation properties
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 12
        
    def draw(self, screen, x, y, facing_right=True, is_moving=False, is_swimming=False):
        # Update animation
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % (2 if is_moving or is_swimming else 1)
        
        # Select appropriate frame based on movement and swimming state
        if is_swimming:
            # Use swimming animation
            frame = self.swimming_frames[self.current_frame % len(self.swimming_frames)]
        else:
            # Use walking/standing animation
            frame_index = min(self.current_frame, len(self.walking_frames) - 1)
            frame = self.walking_frames[frame_index if is_moving else 0]
        
        # Flip frame if facing left
        if not facing_right:
            frame = pygame.transform.flip(frame, True, False)
            
        # Draw character
        screen.blit(frame, (x, y))

class Princess:
    def __init__(self):
        # Create a 32-bit style princess sprite with more detail
        self.width = 32
        self.height = 48
        
        # Create base surface
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Define pixel size for 32-bit style
        pixel_size = 2  # Reduced from 4 for more detail
        
        # Define enhanced colors for 32-bit style princess
        skin_color = (255, 220, 180)    # Light skin tone
        skin_shadow = (230, 200, 160)   # Skin shadow
        dress_color = (255, 105, 180)   # Pink dress
        dress_highlight = (255, 150, 200)  # Dress highlight
        dress_shadow = (220, 80, 150)   # Dress shadow
        crown_color = (255, 215, 0)     # Gold crown
        crown_highlight = (255, 235, 80) # Crown highlight
        hair_color = (255, 215, 150)    # Blonde hair
        hair_highlight = (255, 235, 180) # Hair highlight
        
        # Draw princess with more detail and shading
        
        # Draw head with shading
        for x in range(5, 11):
            for y in range(2, 8):
                color = skin_color
                if x < 7:  # Left side shadow
                    color = skin_shadow
                pygame.draw.rect(self.surface, color, 
                               (x * pixel_size, y * pixel_size, 
                                pixel_size, pixel_size))
        
        # Draw crown with highlights
        for x in range(4, 12):
            color = crown_color
            if x % 2 == 0:  # Add crown jewels/details
                color = crown_highlight
            pygame.draw.rect(self.surface, color, 
                           (x * pixel_size, 1 * pixel_size, pixel_size, pixel_size))
        
        # Add crown points
        for x in range(5, 11, 2):
            pygame.draw.rect(self.surface, crown_color, 
                          (x * pixel_size, 0 * pixel_size, pixel_size, pixel_size))
        
        # Draw hair with highlights
        for x in range(3, 13):
            for y in range(2, 6):
                if (x == 3 or x == 12) or y == 2:
                    color = hair_color
                    if x % 3 == 0:  # Add highlights
                        color = hair_highlight
                    pygame.draw.rect(self.surface, color, 
                                  (x * pixel_size, y * pixel_size, pixel_size, pixel_size))
        
        # Eyes with more detail
        # Left eye
        pygame.draw.rect(self.surface, (255, 255, 255), 
                       (6 * pixel_size, 4 * pixel_size, 2 * pixel_size, pixel_size))
        pygame.draw.rect(self.surface, (0, 0, 150), 
                       (7 * pixel_size, 4 * pixel_size, pixel_size, pixel_size))
        
        # Right eye
        pygame.draw.rect(self.surface, (255, 255, 255), 
                       (9 * pixel_size, 4 * pixel_size, 2 * pixel_size, pixel_size))
        pygame.draw.rect(self.surface, (0, 0, 150), 
                       (9 * pixel_size, 4 * pixel_size, pixel_size, pixel_size))
        
        # Add eyelashes
        pygame.draw.rect(self.surface, (0, 0, 0), 
                       (6 * pixel_size, 3 * pixel_size, pixel_size, pixel_size))
        pygame.draw.rect(self.surface, (0, 0, 0), 
                       (11 * pixel_size, 3 * pixel_size, pixel_size, pixel_size))
        
        # Smile
        for x in range(7, 10):
            pygame.draw.rect(self.surface, (200, 100, 100), 
                          (x * pixel_size, 6 * pixel_size, pixel_size, pixel_size))
        
        # Draw dress upper body with shading
        for x in range(4, 12):
            for y in range(8, 16):
                color = dress_color
                if x < 6:  # Left side shadow
                    color = dress_shadow
                elif x > 9:  # Right side highlight
                    color = dress_highlight
                pygame.draw.rect(self.surface, color, 
                               (x * pixel_size, y * pixel_size, 
                                pixel_size, pixel_size))
        
        # Draw dress bottom (wider) with shading and details
        for x in range(2, 14):
            for y in range(16, 24):
                # Base dress color with shading
                color = dress_color
                if x < 6:  # Left side shadow
                    color = dress_shadow
                elif x > 9:  # Right side highlight
                    color = dress_highlight
                
                # Add dress pattern - small decorative dots
                if (x + y) % 5 == 0:
                    color = dress_highlight
                
                pygame.draw.rect(self.surface, color, 
                               (x * pixel_size, y * pixel_size, 
                                pixel_size, pixel_size))
        
        # Create walking animation frames with dress movement
        self.walking_frames = []
        
        # Standing frame
        self.walking_frames.append(self.surface.copy())
        
        # Walking frame 1 - dress sways slightly
        frame1 = self.surface.copy()
        # Clear bottom part of dress
        for x in range(2, 14):
            for y in range(20, 24):
                pygame.draw.rect(frame1, (0, 0, 0, 0), 
                               (x * pixel_size, y * pixel_size, 
                                pixel_size, pixel_size))
                
        # Redraw with slight movement - sway right
        for x in range(2, 14):
            offset = 1 if x < 7 else 0  # Move left side right
            
            for y in range(20, 24):
                # Base dress color with shading
                color = dress_color
                if x < 6:  # Left side shadow
                    color = dress_shadow
                elif x > 9:  # Right side highlight
                    color = dress_highlight
                
                # Add dress pattern
                if (x + y) % 5 == 0:
                    color = dress_highlight
                
                pygame.draw.rect(frame1, color, 
                               ((x + offset) * pixel_size, y * pixel_size, 
                                pixel_size, pixel_size))
        self.walking_frames.append(frame1)
        
        # Walking frame 2 - dress sways in opposite direction
        frame2 = self.surface.copy()
        # Clear bottom part of dress
        for x in range(2, 14):
            for y in range(20, 24):
                pygame.draw.rect(frame2, (0, 0, 0, 0), 
                               (x * pixel_size, y * pixel_size, 
                                pixel_size, pixel_size))
                
        # Redraw with slight movement - sway left
        for x in range(2, 14):
            offset = -1 if x > 8 else 0  # Move right side left
            
            for y in range(20, 24):
                # Base dress color with shading
                color = dress_color
                if x < 6:  # Left side shadow
                    color = dress_shadow
                elif x > 9:  # Right side highlight
                    color = dress_highlight
                
                # Add dress pattern
                if (x + y) % 5 == 0:
                    color = dress_highlight
                
                pygame.draw.rect(frame2, color, 
                               ((x + offset) * pixel_size, y * pixel_size, 
                                pixel_size, pixel_size))
        self.walking_frames.append(frame2)
        
        # Animation properties
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 12  # Slower than player for delicate movement
        
        # Add smooth pixel rendering
        for i, frame in enumerate(self.walking_frames):
            # Apply a slight blur for smoother look (optional)
            temp_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            temp_surface.blit(frame, (0, 0))
            self.walking_frames[i] = temp_surface
        
    def draw(self, screen, x, y, facing_right=True, is_moving=False):
        # Only update animation timer and frames if the princess is moving
        if is_moving:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.walking_frames)
        else:
            # When not moving, always show the standing frame (first frame)
            self.current_frame = 0
            
        frame = self.walking_frames[self.current_frame]
        if facing_right:
            screen.blit(frame, (x, y))
        else:
            flipped = pygame.transform.flip(frame, True, False)
            screen.blit(flipped, (x, y))

class Food:
    def __init__(self, food_type="apple"):
        self.type = food_type
        self.width = 16
        self.height = 16
        
        # Create base surface
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Define food types and their attributes with enhanced colors
        food_attributes = {
            "apple": {
                "color": (255, 0, 0),
                "highlight": (255, 100, 100),
                "shadow": (180, 0, 0),
                "healing": 20
            },
            "cake": {
                "color": (222, 184, 135),
                "highlight": (240, 210, 170),
                "shadow": (190, 150, 110),
                "healing": 50
            },
            "cookie": {
                "color": (139, 69, 19),
                "highlight": (160, 90, 40),
                "shadow": (110, 50, 10),
                "healing": 10
            }
        }
        
        # Set food attributes
        self.color = food_attributes[food_type]["color"]
        self.highlight = food_attributes[food_type]["highlight"]
        self.shadow = food_attributes[food_type]["shadow"]
        self.healing = food_attributes[food_type]["healing"]
        
        # Draw food based on type with 32-bit style and shading
        if food_type == "apple":
            # Draw apple base
            pygame.draw.circle(self.surface, self.color, (8, 9), 6)
            
            # Add highlight
            pygame.draw.circle(self.surface, self.highlight, (6, 7), 2)
            
            # Add shadow
            pygame.draw.circle(self.surface, self.shadow, (10, 11), 3, 1)
            
            # Draw stem with gradient
            pygame.draw.rect(self.surface, (101, 67, 33), (8, 2, 2, 3))
            pygame.draw.rect(self.surface, (120, 80, 40), (8, 2, 1, 2))
            
            # Draw leaf with gradient
            pygame.draw.rect(self.surface, (0, 128, 0), (10, 3, 3, 2))
            pygame.draw.rect(self.surface, (50, 150, 50), (10, 3, 2, 1))
            
        elif food_type == "cake":
            # Draw cake base with shading
            pygame.draw.rect(self.surface, self.color, (2, 6, 12, 8))
            
            # Add highlights on top edge
            pygame.draw.line(self.surface, self.highlight, (2, 6), (14, 6), 1)
            
            # Add shadows on bottom edge
            pygame.draw.line(self.surface, self.shadow, (2, 13), (14, 13), 1)
            
            # Draw frosting top with texture
            pygame.draw.rect(self.surface, (255, 255, 255), (2, 4, 12, 2))
            for x in range(3, 13, 2):
                pygame.draw.line(self.surface, (240, 240, 240), (x, 4), (x, 5), 1)
            
            # Draw cherry on top with highlight
            pygame.draw.circle(self.surface, (255, 0, 0), (8, 3), 2)
            pygame.draw.circle(self.surface, (255, 150, 150), (7, 2), 1)
            
            # Add cake layers
            pygame.draw.line(self.surface, self.highlight, (2, 9), (14, 9), 1)
            
        elif food_type == "cookie":
            # Draw cookie base with more texture
            pygame.draw.circle(self.surface, self.color, (8, 8), 6)
            
            # Add edge texture/crumbs
            for i in range(8):
                angle = i * math.pi / 4
                x = 8 + int(6 * math.cos(angle))
                y = 8 + int(6 * math.sin(angle))
                pygame.draw.circle(self.surface, self.highlight, (x, y), 1)
            
            # Add highlight
            pygame.draw.circle(self.surface, self.highlight, (6, 6), 2)
            
            # Draw chocolate chips
            pygame.draw.rect(self.surface, (40, 26, 13), (6, 6, 2, 2))
            pygame.draw.rect(self.surface, (40, 26, 13), (10, 5, 2, 2))
            pygame.draw.rect(self.surface, (40, 26, 13), (7, 10, 2, 2))
            
            # Add highlights to chips
            pygame.draw.rect(self.surface, (60, 40, 20), (6, 6, 1, 1))
            pygame.draw.rect(self.surface, (60, 40, 20), (10, 5, 1, 1))
            pygame.draw.rect(self.surface, (60, 40, 20), (7, 10, 1, 1))
            
    def draw(self, screen, x, y):
        screen.blit(self.surface, (x, y))

class Crab:
    def __init__(self):
        # Create a 32-bit style crab enemy
        self.width = 24
        self.height = 16
        
        # Rainbow chance (e.g., 10%)
        self.is_rainbow = random.random() < 0.1 
        self.rainbow_hue = random.random() * 360 # Initial hue for rainbow cycle
        
        # Create base surface
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Define pixel size for 32-bit style
        pixel_size = 2
        
        # Define standard colors (used if not rainbow)
        self.shell_color = (200, 0, 0)
        self.shell_highlight = (240, 60, 60)
        self.shell_shadow = (150, 0, 0)
        self.leg_color = (160, 0, 0)
        self.claw_color = (180, 20, 20)
        self.eye_color = (0, 0, 0)
        
        # Generate the actual sprite frames (can be done in a separate method for clarity)
        self.walking_frames = self._create_frames()
        
        # Animation properties
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 10
        
        # Stats for enemy
        self.max_health = 30 # Add max_health for health bar consistency
        self.health = self.max_health
        self.damage = 10
        self.attack_range = 40
        self.attack_cooldown = 60
        self.current_cooldown = 0
        
    def _get_current_color(self, base_color_rgb, offset_degrees=0):
        """Gets the current color, either standard or rainbow cycling."""
        if not self.is_rainbow:
            return base_color_rgb
        else:
            # Cycle hue and convert HSL to RGB
            current_hue = (self.rainbow_hue + offset_degrees) % 360
            color = pygame.Color(0) # Create dummy color
            # Use HSL: Hue (0-360), Saturation (0-100), Lightness (0-100)
            color.hsla = (current_hue, 100, 50, 100) 
            return (color.r, color.g, color.b)

    def _create_frames(self):
        """Creates the walking animation frames for the crab."""
        frames = []
        pixel_size = 2

        # Frame 0 (Standing)
        surface0 = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self._draw_crab_body(surface0, pixel_size)
        self._draw_legs(surface0, pixel_size, [(2, 6), (4, 7), (7, 7), (9, 6)])
        self._draw_claws(surface0, pixel_size, is_open=False)
        frames.append(surface0)

        # Frame 1 (Walking)
        surface1 = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self._draw_crab_body(surface1, pixel_size)
        self._draw_legs(surface1, pixel_size, [(2, 7), (4, 6), (7, 6), (9, 7)]) # Different leg positions
        self._draw_claws(surface1, pixel_size, is_open=True) # Claws open slightly
        frames.append(surface1)
        
        return frames

    def _draw_crab_body(self, surface, pixel_size):
        """Helper method to draw the crab body."""
        # Draw crab body (oval shell)
        for x in range(3, 9):
            for y in range(2, 6):
                # Determine base color type for rainbow offset
                base_color = self.shell_color
                offset = 0
                if x == 3 or y == 2:  # Shadow area
                    base_color = self.shell_shadow
                    offset = -30 # Darker shade for rainbow
                elif x == 8 or y == 5:  # Highlight area
                    base_color = self.shell_highlight
                    offset = 30 # Brighter shade for rainbow
                
                color = self._get_current_color(base_color, offset)
                pygame.draw.rect(surface, color, 
                               (x * pixel_size, y * pixel_size, 
                                pixel_size, pixel_size))
                
        # Draw eyes
        eye_col = self._get_current_color(self.eye_color, 180) # Opposite color for eyes maybe?
        pygame.draw.rect(surface, eye_col, (4 * pixel_size, 1 * pixel_size, pixel_size, pixel_size))
        pygame.draw.rect(surface, eye_col, (7 * pixel_size, 1 * pixel_size, pixel_size, pixel_size))

    def _draw_legs(self, surface, pixel_size, positions):
        """Helper method to draw the crab legs."""
        leg_col = self._get_current_color(self.leg_color, -60) # Different offset for legs
        for i, (x, y) in enumerate(positions):
            pygame.draw.rect(surface, leg_col, (x * pixel_size, y * pixel_size, pixel_size, 2 * pixel_size))
            pygame.draw.rect(surface, leg_col, ((11 - x) * pixel_size, y * pixel_size, pixel_size, 2 * pixel_size))

    def _draw_claws(self, surface, pixel_size, is_open=False):
        """Helper method to draw the crab claws (open or closed)."""
        claw_col = self._get_current_color(self.claw_color, 60) # Different offset for claws
        if not is_open:
            # Left claw (closed)
            for y in range(3, 5):
                pygame.draw.rect(surface, claw_col, (1 * pixel_size, y * pixel_size, 2 * pixel_size, pixel_size))
            pygame.draw.rect(surface, claw_col, (0 * pixel_size, 3 * pixel_size, pixel_size, pixel_size))
            # Right claw (closed)
            for y in range(3, 5):
                pygame.draw.rect(surface, claw_col, (9 * pixel_size, y * pixel_size, 2 * pixel_size, pixel_size))
            pygame.draw.rect(surface, claw_col, (11 * pixel_size, 3 * pixel_size, pixel_size, pixel_size))
        else:
            # Left claw (open)
            for y in range(3, 5):
                 pygame.draw.rect(surface, claw_col, (1 * pixel_size, y * pixel_size, 2 * pixel_size, pixel_size))
            pygame.draw.rect(surface, claw_col, (0 * pixel_size, 2 * pixel_size, pixel_size, pixel_size)) # Shifted up
            # Right claw (open)
            for y in range(3, 5):
                 pygame.draw.rect(surface, claw_col, (9 * pixel_size, y * pixel_size, 2 * pixel_size, pixel_size))
            pygame.draw.rect(surface, claw_col, (11 * pixel_size, 2 * pixel_size, pixel_size, pixel_size)) # Shifted up

    def draw(self, screen, x, y, facing_right=True):
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.walking_frames)
            
        # If rainbow, update hue and potentially redraw frames (more costly) or use shader (complex)
        # Simple approach: Update hue and redraw current frame if needed (can be slow)
        # Better approach: Use pre-rendered frames or shaders if performance is an issue.
        # Current implementation redraws the frame logic inside _create_frames using current colors.
        if self.is_rainbow:
             self.rainbow_hue = (self.rainbow_hue + 2) % 360 # Cycle hue speed
             # OPTIONAL: Regenerate frames each draw call for perfect colors (performance hit!)
             # self.walking_frames = self._create_frames() 
             
             # Simpler: Draw the selected frame but modify its colors in place (or use a colored overlay)
             # We will stick with drawing the pre-calculated frame but the colors won't cycle dynamically 
             # unless we regenerate frames constantly. Let's just use the hue from init for now.
             # To make it dynamic, we'd need to change _create_frames to return surfaces
             # and call _draw_crab_body/_legs/_claws directly here using current hue.
             
             # Let's try regenerating the specific frame surface for dynamic color:
             current_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
             self._draw_crab_body(current_surface, 2)
             if self.current_frame == 0:
                 self._draw_legs(current_surface, 2, [(2, 6), (4, 7), (7, 7), (9, 6)])
                 self._draw_claws(current_surface, 2, is_open=False)
             else:
                 self._draw_legs(current_surface, 2, [(2, 7), (4, 6), (7, 6), (9, 7)])
                 self._draw_claws(current_surface, 2, is_open=True)
             frame = current_surface # Use the dynamically colored frame
        else:
            frame = self.walking_frames[self.current_frame]
        
        if facing_right:
            screen.blit(frame, (x, y))
        else:
            flipped = pygame.transform.flip(frame, True, False)
            screen.blit(flipped, (x, y))
            
    def can_attack(self):
        if self.current_cooldown <= 0:
            return True
        return False
        
    def attack(self):
        self.current_cooldown = self.attack_cooldown
        return self.damage
        
    def update(self):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1
            
    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0

class KingCrab:
    def __init__(self):
        # Bigger, tougher crab boss
        self.width = 48  # Larger than regular crab
        self.height = 36
        
        # Create surface
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Define pixel size for 32-bit style
        pixel_size = 3 # Larger pixels for a bigger look
        
        # Color palette - maybe slightly different
        body_color = (200, 50, 0)  # Darker red
        body_shadow = (160, 40, 0)
        claw_color = (180, 100, 20)
        eye_color = (255, 255, 0) # Yellow eyes
        
        # Draw the King Crab body
        for x in range(2, 14):
            for y in range(2, 10):
                color = body_color
                if x < 5 or x > 10 or y < 4:
                    color = body_shadow
                pygame.draw.rect(self.surface, color, 
                               (x * pixel_size, y * pixel_size, 
                                pixel_size, pixel_size))
                                
        # Draw larger claws
        # Left claw
        for x in range(0, 4):
            for y in range(4, 9):
                pygame.draw.rect(self.surface, claw_color, 
                               (x * pixel_size, y * pixel_size, 
                                pixel_size, pixel_size))
        # Right claw
        for x in range(12, 16):
            for y in range(4, 9):
                pygame.draw.rect(self.surface, claw_color, 
                               (x * pixel_size, y * pixel_size, 
                                pixel_size, pixel_size))
                                
        # Draw eyes
        pygame.draw.rect(self.surface, eye_color, 
                       (5 * pixel_size, 3 * pixel_size, 2 * pixel_size, pixel_size))
        pygame.draw.rect(self.surface, eye_color, 
                       (9 * pixel_size, 3 * pixel_size, 2 * pixel_size, pixel_size))
        
        # Store frames (just one for now, add animation later if needed)
        self.walking_frames = [self.surface.copy()]
        
        # Animation properties (basic)
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 15 # Slower animation
        
        # Boss Stats
        self.health = 150 # Much higher health
        self.max_health = 150  # Add max_health to match health
        self.damage = 25  # Higher damage
        self.attack_range = 60 # Slightly longer range
        self.attack_cooldown = 90 # Slower attacks
        self.current_cooldown = 0
        
    def draw(self, screen, x, y, facing_right=True):
        # Simple animation (if more frames added)
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.walking_frames)
            
        frame = self.walking_frames[self.current_frame]
        if facing_right:
            screen.blit(frame, (x, y))
        else:
            flipped = pygame.transform.flip(frame, True, False)
            screen.blit(flipped, (x, y))
            
    def can_attack(self):
        return self.current_cooldown <= 0
        
    def attack(self):
        if self.can_attack():
            self.current_cooldown = self.attack_cooldown
            return self.damage
        return 0
        
    def update(self):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1
            
    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0 # Return True if defeated 

class PrincessNPC:
    def __init__(self, princess, game):
        self.princess = princess
        self.game = game
        self.width = princess.width
        self.height = princess.height
        self.facing_right = True
        self.is_moving = False
        self.x = 0
        self.y = 0

    def draw(self, screen, camera_x):
        # Only draw if on screen
        if self.x + self.width > 0 and self.x < self.game.SCREEN_WIDTH:
            # Draw princess - pass is_moving to princess draw method
            self.princess.draw(screen, self.x, self.y, self.facing_right, self.is_moving)
            
            # ... existing code ... 

class Fish:
    def __init__(self):
        # Create a simple fish sprite
        self.width = 24
        self.height = 12
        
        # Create base surface
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Define pixel size for 32-bit style
        pixel_size = 2
        
        # Define colors
        body_color = (100, 180, 255)  # Blue fish
        fin_color = (80, 160, 240)
        eye_color = (0, 0, 0)
        
        # Draw fish body (oval shape)
        for x in range(1, 10):
            for y in range(2, 5):
                # Body tapers at ends
                if (x == 1 or x == 9) and (y < 2 or y > 4):
                    continue
                    
                pygame.draw.rect(self.surface, body_color, 
                               (x * pixel_size, y * pixel_size, 
                                pixel_size, pixel_size))
                
        # Draw tail fin
        for y in range(2, 5):
            pygame.draw.rect(self.surface, fin_color, 
                           (0 * pixel_size, y * pixel_size, pixel_size, pixel_size))
            
        # Draw top fin
        pygame.draw.rect(self.surface, fin_color, 
                       (5 * pixel_size, 1 * pixel_size, pixel_size, pixel_size))
        
        # Draw eye
        pygame.draw.rect(self.surface, eye_color, 
                       (7 * pixel_size, 3 * pixel_size, pixel_size, pixel_size))
        
        # Store animation frames (just 2 frames for simple animation)
        self.walking_frames = [self.surface.copy()]
        
        # Create second frame with tail moved
        frame2 = self.surface.copy()
        # Clear tail area
        for y in range(2, 5):
            pygame.draw.rect(frame2, (0, 0, 0, 0), 
                           (0 * pixel_size, y * pixel_size, pixel_size, pixel_size))
        # Redraw tail in new position
        for y in range(1, 6):
            if y != 1 and y != 5:  # Don't draw corners for smooth look
                pygame.draw.rect(frame2, fin_color, 
                               (0 * pixel_size, y * pixel_size, pixel_size, pixel_size))
                
        self.walking_frames.append(frame2)
        
        # Animation properties
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 8  # Faster animation for fish
        
        # Fish stats
        self.healing = 10  # Health gained when eaten
        
    def draw(self, screen, x, y, facing_right=True):
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.walking_frames)
            
        frame = self.walking_frames[self.current_frame]
        if facing_right:
            screen.blit(frame, (x, y))
        else:
            flipped = pygame.transform.flip(frame, True, False)
            screen.blit(flipped, (x, y))
    
    def update(self):
        # Fish don't have complex behaviors beyond animation
        pass

class Dinosaur:
    def __init__(self):
        # Create a dinosaur enemy
        self.width = 48
        self.height = 48
        
        # Create base surface
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Define pixel size
        pixel_size = 3
        
        # Define colors
        body_color = (50, 120, 50)  # Green dinosaur
        belly_color = (70, 150, 70)
        eye_color = (200, 0, 0)  # Red eyes
        
        # Draw dinosaur body (T-Rex like)
        # Main body
        for x in range(2, 12):
            for y in range(4, 10):
                color = body_color
                if y >= 8:  # Belly area
                    color = belly_color
                    
                pygame.draw.rect(self.surface, color, 
                               (x * pixel_size, y * pixel_size, 
                                pixel_size, pixel_size))
        
        # Head (larger for T-Rex)
        for x in range(10, 15):
            for y in range(1, 6):
                pygame.draw.rect(self.surface, body_color, 
                               (x * pixel_size, y * pixel_size, 
                                pixel_size, pixel_size))
        
        # Tail
        for i in range(5):
            x = 1 - i
            y = 6 + i
            pygame.draw.rect(self.surface, body_color, 
                           (x * pixel_size, y * pixel_size, 
                            pixel_size, pixel_size))
        
        # Legs
        # Front leg
        for y in range(9, 15):
            pygame.draw.rect(self.surface, body_color, 
                           (10 * pixel_size, y * pixel_size, 
                            pixel_size, pixel_size))
                           
        # Back leg (larger)
        for x in range(3, 6):
            for y in range(10, 16):
                pygame.draw.rect(self.surface, body_color, 
                               (x * pixel_size, y * pixel_size, 
                                pixel_size, pixel_size))
        
        # Eye
        pygame.draw.rect(self.surface, eye_color, 
                       (13 * pixel_size, 2 * pixel_size, 
                        pixel_size, pixel_size))
        
        # Store animation frames
        self.walking_frames = [self.surface.copy()]
        
        # Create second frame with legs in different position
        frame2 = self.surface.copy()
        
        # Clear leg areas
        for y in range(9, 16):
            pygame.draw.rect(frame2, (0, 0, 0, 0), 
                           (10 * pixel_size, y * pixel_size, 
                            pixel_size, pixel_size))
        for x in range(3, 6):
            for y in range(10, 16):
                pygame.draw.rect(frame2, (0, 0, 0, 0), 
                               (x * pixel_size, y * pixel_size, 
                                pixel_size, pixel_size))
        
        # Redraw legs in new positions
        # Front leg
        for y in range(10, 16):
            pygame.draw.rect(frame2, body_color, 
                           (11 * pixel_size, y * pixel_size, 
                            pixel_size, pixel_size))
                           
        # Back leg
        for x in range(4, 7):
            for y in range(9, 15):
                pygame.draw.rect(frame2, body_color, 
                               (x * pixel_size, y * pixel_size, 
                                pixel_size, pixel_size))
                
        self.walking_frames.append(frame2)
        
        # Animation properties
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 12
        
        # Dinosaur stats
        self.max_health = 60
        self.health = self.max_health
        self.damage = 15
        self.attack_range = 50
        self.attack_cooldown = 75
        self.current_cooldown = 0
        
    def draw(self, screen, x, y, facing_right=True):
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.walking_frames)
            
        frame = self.walking_frames[self.current_frame]
        if facing_right:
            screen.blit(frame, (x, y))
        else:
            flipped = pygame.transform.flip(frame, True, False)
            screen.blit(flipped, (x, y))
            
    def can_attack(self):
        return self.current_cooldown <= 0
        
    def attack(self):
        if self.can_attack():
            self.current_cooldown = self.attack_cooldown
            return self.damage
        return 0
        
    def update(self):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1
            
    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0

class PrincessNPC:
    def __init__(self, princess, game):
        self.princess = princess
        self.game = game
        self.width = princess.width
        self.height = princess.height
        self.facing_right = True
        self.is_moving = False
        self.x = 0
        self.y = 0

    def draw(self, screen, camera_x):
        # Only draw if on screen
        if self.x + self.width > 0 and self.x < self.game.SCREEN_WIDTH:
            # Draw princess - pass is_moving to princess draw method
            self.princess.draw(screen, self.x, self.y, self.facing_right, self.is_moving)
            
            # ... existing code ... 
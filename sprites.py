import pygame
import os

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
        # Create a simple 16-bit style character sprite
        self.width = 32
        self.height = 48
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw head
        pygame.draw.circle(self.surface, (255, 218, 185), (16, 12), 8)
        
        # Draw body
        pygame.draw.rect(self.surface, (50, 50, 255), (8, 20, 16, 24))
        
        # Draw arms
        pygame.draw.rect(self.surface, (255, 218, 185), (4, 24, 4, 16))
        pygame.draw.rect(self.surface, (255, 218, 185), (24, 24, 4, 16))
        
        # Draw legs
        pygame.draw.rect(self.surface, (50, 50, 255), (8, 44, 6, 4))
        pygame.draw.rect(self.surface, (50, 50, 255), (18, 44, 6, 4))
        
        # Create sprite sheet for walking animation
        self.walking_frames = []
        for i in range(4):
            frame = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            frame.blit(self.surface, (0, 0))
            # Add slight leg movement for walking animation
            if i % 2 == 0:
                pygame.draw.rect(frame, (50, 50, 255), (8, 44, 6, 4))
                pygame.draw.rect(frame, (50, 50, 255), (18, 44, 6, 4))
            else:
                pygame.draw.rect(frame, (50, 50, 255), (8, 44, 6, 4))
                pygame.draw.rect(frame, (50, 50, 255), (18, 44, 6, 4))
            self.walking_frames.append(frame)
            
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 8
        
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
import pygame
import random
import math

class Particle:
    def __init__(self, x, y, color, particle_type="block"):
        self.x = x
        self.y = y
        self.color = color
        self.type = particle_type
        self.size = random.randint(2, 4)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 4)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.lifetime = 30
        self.alpha = 255
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # Gravity
        self.lifetime -= 1
        self.alpha = int((self.lifetime / 30) * 255)
        
    def draw(self, screen):
        if self.type == "block":
            surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.rect(surface, (*self.color, self.alpha), (0, 0, self.size, self.size))
            screen.blit(surface, (self.x, self.y))
        elif self.type == "spark":
            surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(surface, (255, 255, 255, self.alpha), 
                             (self.size//2, self.size//2), self.size//2)
            screen.blit(surface, (self.x, self.y))

    def draw_with_camera(self, screen, camera_x):
        # Draw with camera offset
        screen_x = self.x - camera_x
        if screen_x < -10 or screen_x > screen.get_width() + 10:
            return  # Off-screen culling
            
        if self.type == "block":
            surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.rect(surface, (*self.color, self.alpha), (0, 0, self.size, self.size))
            screen.blit(surface, (screen_x, self.y))
        elif self.type == "spark":
            surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(surface, (255, 255, 255, self.alpha), 
                             (self.size//2, self.size//2), self.size//2)
            screen.blit(surface, (screen_x, self.y))

class ParticleSystem:
    def __init__(self):
        self.particles = []
        
    def create_block_break(self, x, y, color):
        for _ in range(8):
            self.particles.append(Particle(x, y, color, "block"))
            
    def create_spark(self, x, y):
        for _ in range(4):
            self.particles.append(Particle(x, y, (255, 255, 255), "spark"))
            
    def update(self):
        self.particles = [p for p in self.particles if p.lifetime > 0]
        for particle in self.particles:
            particle.update()
            
    def draw(self, screen, camera_x=0):
        for particle in self.particles:
            if camera_x == 0:
                particle.draw(screen)
            else:
                particle.draw_with_camera(screen, camera_x) 
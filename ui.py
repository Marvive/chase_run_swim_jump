import pygame

class Tooltip:
    def __init__(self):
        self.tooltips = {
            "movement": "WASD/Arrows: Move",
            "jump": "Space: Jump",
            "inventory": "E: Open/Close Inventory",
            "build": "B: Toggle Building Mode",
            "interact": "F/Left Click: Interact/Use Tool",
            "select": "1-2: Quick Select Tools",
            "inventory_nav": "A/D or Arrows: Navigate Inventory",
            "inventory_select": "Space/Enter: Select Tool"
        }
        self.font = pygame.font.Font(None, 24)
        self.show_help = True
        self.help_timeout = 300  # Show help for 5 seconds (60 fps * 5)
        self.help_timer = self.help_timeout
        
    def update(self):
        if self.help_timer > 0:
            self.help_timer -= 1
        else:
            self.show_help = False
            
    def toggle_help(self):
        self.show_help = not self.show_help
        if self.show_help:
            self.help_timer = self.help_timeout
            
    def draw(self, screen):
        if self.show_help:
            # Create semi-transparent background for tooltips
            tooltip_surface = pygame.Surface((300, 240), pygame.SRCALPHA)
            tooltip_surface.fill((0, 0, 0, 150))
            
            # Draw tooltips
            y_offset = 10
            for name, text in self.tooltips.items():
                tooltip_text = self.font.render(text, True, (255, 255, 255))
                tooltip_surface.blit(tooltip_text, (10, y_offset))
                y_offset += 30
                
            # Draw to screen
            screen.blit(tooltip_surface, (10, 50))
            
            # Draw help toggle instructions
            help_text = self.font.render("Press H to hide/show help", True, (255, 255, 255))
            screen.blit(help_text, (10, 300))

class NotificationSystem:
    def __init__(self):
        self.notifications = []
        self.font = pygame.font.Font(None, 24)
        
    def add_notification(self, text, duration=90):  # 1.5 seconds at 60fps
        self.notifications.append({"text": text, "duration": duration})
        
    def update(self):
        # Update notification timers and remove expired ones
        self.notifications = [n for n in self.notifications if n["duration"] > 0]
        for notification in self.notifications:
            notification["duration"] -= 1
            
    def draw(self, screen):
        y_offset = 50  # Start at the top
        for notification in self.notifications:
            alpha = min(255, notification["duration"] * 3)
            notification_text = self.font.render(notification["text"], True, (255, 255, 255))
            text_surface = pygame.Surface(notification_text.get_size(), pygame.SRCALPHA)
            text_surface.fill((0, 0, 0, min(150, alpha)))
            
            # Position on the right side of the screen with some padding
            x_position = screen.get_width() - notification_text.get_width() - 20
            
            screen.blit(text_surface, (x_position - 5, y_offset - 5))
            screen.blit(notification_text, (x_position, y_offset))
            y_offset += 40 
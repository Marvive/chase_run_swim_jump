import pygame
import random

def create_cloud_sprite(variation=0):
    """
    Creates a 16-bit style cloud sprite as a pygame Surface.
    Returns the sprite ready to use in the game.
    
    variation: 0-2 to determine the cloud shape pattern
    """
    # Create a transparent surface for the cloud
    # More consistent sizes
    width = 96 + random.randint(-8, 8)  # Less random width variation
    height = 48 + random.randint(-4, 4)  # Less random height variation
    
    cloud = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Define colors with minimal randomness
    red_value = random.randint(245, 255)
    cloud_color = (red_value, 90 + random.randint(0, 20), 110)  # More consistent red cloud color
    highlight_color = (255, 150 + random.randint(0, 20), 150)  # More consistent highlight
    
    # Fixed pixel size for consistency
    pixel_size = 6
    
    # Different cloud patterns based on variation
    if variation == 0:
        # Classic cumulus cloud shape - puffy with flat bottom
        pixels = []
        
        # Flat bottom
        bottom_y = height - pixel_size
        
        # Top curved part
        for x in range(0, width, pixel_size):
            # Calculate height at this x position (higher in middle, lower at edges)
            rel_x = x / width  # 0 to 1
            
            # Classic cloud shape function (higher in middle)
            if rel_x < 0.2:
                # Left side rises
                column_height = height * 0.4
            elif rel_x < 0.4:
                # Left bump
                column_height = height * 0.8
            elif rel_x < 0.6:
                # Middle bump (highest)
                column_height = height * 0.95
            elif rel_x < 0.8:
                # Right bump
                column_height = height * 0.75
            else:
                # Right side falls
                column_height = height * 0.5
                
            # Add pixels for this column
            for y in range(bottom_y - int(column_height), bottom_y, pixel_size):
                pixels.append((x, y))
    
    elif variation == 1:
        # Wider, flatter cloud with multiple bumps
        pixels = []
        
        # Flat bottom
        bottom_y = height - pixel_size
        
        # Define bump positions and heights
        bumps = [
            (0.1, 0.6),   # (position, height) - position is percentage across width
            (0.3, 0.85),  # height is percentage of total height
            (0.5, 0.9),
            (0.7, 0.8),
            (0.9, 0.55)
        ]
        
        # Draw columns based on proximity to bumps
        for x in range(0, width, pixel_size):
            rel_x = x / width
            
            # Find height based on proximity to bumps
            max_height = 0
            for bump_pos, bump_height in bumps:
                # Calculate influence based on distance to this bump
                distance = abs(rel_x - bump_pos)
                if distance < 0.2:  # Only bumps influence within 20% of width
                    # Height falls off with distance
                    influence = 1 - (distance / 0.2)
                    height_at_bump = height * bump_height * influence
                    max_height = max(max_height, height_at_bump)
            
            # Ensure there's always some height
            column_height = max(max_height, height * 0.3)
                
            # Add pixels for this column
            for y in range(bottom_y - int(column_height), bottom_y, pixel_size):
                pixels.append((x, y))
    
    else:
        # Smaller, more compact cloud
        pixels = []
        
        # Flat bottom with rounded top
        bottom_y = height - pixel_size
        
        # Draw a simple rounded shape
        for x in range(0, width, pixel_size):
            rel_x = x / width
            
            # Parabolic top (rounded)
            # Formula: height * (1 - 4 * (x - 0.5)²)
            column_height = height * 0.7 * (1 - 4 * (rel_x - 0.5) * (rel_x - 0.5))
            column_height = max(column_height, height * 0.2)  # Ensure minimum height
                
            # Add pixels for this column
            for y in range(bottom_y - int(column_height), bottom_y, pixel_size):
                pixels.append((x, y))
    
    # Reduce randomness for more consistent cloud shapes
    final_pixels = pixels
    
    # Generate highlights consistently on top part of cloud
    highlight_pixels = []
    for px, py in final_pixels:
        # Highlights consistently on top part and left edge
        if py < (height * 0.4) or px < (width * 0.25):
            highlight_pixels.append((px, py))
    
    # Draw base of cloud
    for px, py in final_pixels:
        pygame.draw.rect(cloud, cloud_color, (px, py, pixel_size, pixel_size))
    
    # Add highlights
    for px, py in highlight_pixels:
        pygame.draw.rect(cloud, highlight_color, (px, py, pixel_size, pixel_size))
        
    return cloud

# Generate different cloud variations
def create_cloud_variations(world_width, screen_height):
    """
    Creates cloud sprites with consistent shapes.
    Accepts world_width and screen_height but may not use them directly yet.
    Returns a list of cloud sprites.
    """
    clouds = []
    
    # Create each variation type exactly twice
    for variation in range(3):
        for _ in range(2):
            cloud = create_cloud_sprite(variation)
            clouds.append(cloud)
    
    # Only add one set of scaled variations for consistency
    base_clouds = clouds[:3]  # Take one of each variation type
    
    for cloud in base_clouds:
        # Scale consistently
        smaller_cloud = pygame.transform.scale(cloud, 
                         (int(cloud.get_width() * 0.8), int(cloud.get_height() * 0.8)))
        clouds.append(smaller_cloud)
        
        larger_cloud = pygame.transform.scale(cloud, 
                         (int(cloud.get_width() * 1.2), int(cloud.get_height() * 1.2)))
        clouds.append(larger_cloud)
    
    return clouds 
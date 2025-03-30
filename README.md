# Chase Run Swim Jump

A 2D Minecraft-inspired game where you can collect resources and build various structures.

## Features
- Resource collection with different tools (axe, pickaxe)
- Building system with hammer animation
- 16-bit retro style graphics
- Side-scrolling gameplay

## Setup
1. Install Python 3.8 or higher
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the game:
   ```
   python main.py
   ```

## Controls
- Left/Right Arrow: Move
- Space: Jump
- E: Open inventory
- Left Click: Use tool/Build
- Right Click: Select building mode

## Custom Assets
You can add your own custom assets to enhance or customize the game's appearance:

### Adding Custom Graphics
The game currently draws graphics programmatically using Pygame's drawing functions. To add your own custom assets:

1. **Character Sprite**: Modify the `Character` class in `sprites.py` to use your own sprite sheet
   - Create a 32x48 pixel image in 16-bit style
   - Update the class to load your image instead of drawing shapes

2. **Tool Sprites**: Modify the tool sprite classes in `tool_sprites.py`
   - Create 32x32 pixel images for each tool
   - Update each tool class to load your images instead of drawing shapes

3. **World Elements**: Update the `draw` method in the `World` class in `game.py`
   - Modify how trees, stones, and other world elements are drawn
   - Replace drawing code with sprite loading code

Example to load an image:
```python
# In a sprite class
self.image = pygame.image.load('assets/my_sprite.png').convert_alpha()
```

### Creating an Assets Directory
For better organization, create an `assets` directory structure:
```
assets/
  ├── character/
  │   └── player.png
  ├── tools/
  │   ├── axe.png
  │   ├── pickaxe.png
  │   └── hammer.png
  └── world/
      ├── tree.png
      ├── stone.png
      └── ground.png
```

Then update the drawing code to use these images.
import pygame
import os
import numpy
import math

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.load_sounds()
        
    def load_sounds(self):
        # Create a sounds directory if it doesn't exist
        if not os.path.exists("sounds"):
            os.makedirs("sounds")
            
        # Generate simple sound effects
        self.generate_sound("axe_swing", 0.1, 440, 0.5)
        self.generate_sound("pickaxe_swing", 0.1, 220, 0.5)
        self.generate_sound("hammer_swing", 0.1, 330, 0.5)
        self.generate_sound("block_break", 0.05, 880, 0.3)
        
    def generate_sound(self, name, duration, frequency, volume):
        sample_rate = 44100
        num_samples = int(duration * sample_rate)
        buffer = numpy.zeros((num_samples, 2), dtype=numpy.int16)
        
        for i in range(num_samples):
            t = float(i) / sample_rate
            value = int(volume * 32767 * math.sin(2 * math.pi * frequency * t))
            buffer[i] = [value, value]
            
        sound = pygame.sndarray.make_sound(buffer)
        self.sounds[name] = sound
        
    def play(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].play() 
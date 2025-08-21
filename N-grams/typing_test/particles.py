"""
Particle system for visual effects in the typing test game.
"""

import pygame
import random
import math
from typing import Tuple, List
from constants import *

class Particle:
    """Individual particle for visual effects."""
    
    def __init__(self, x: float, y: float, color: Tuple[int, int, int], velocity: Tuple[float, float]):
        self.x = x
        self.y = y
        self.color = color
        self.vx, self.vy = velocity
        self.life = 1.0
        self.decay = random.uniform(0.015, 0.035)
        self.size = random.randint(2, 6)
        self.original_size = self.size
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-3, 3)
        self.alpha = 255
    
    def update(self):
        """Update particle position and properties."""
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.12  # Gravity
        self.life -= self.decay
        self.size = max(0, self.original_size * self.life)
        self.rotation += self.rotation_speed
        self.alpha = int(255 * self.life)
        self.vx += random.uniform(-0.05, 0.05)
    
    def draw(self, screen):
        """Draw the particle on the screen."""
        if self.life > 0:
            surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            points = []
            for i in range(4):
                angle = (i * 90 + self.rotation) * math.pi / 180
                radius = self.size
                x = self.size + radius * math.cos(angle)
                y = self.size + radius * math.sin(angle)
                points.append((x, y))
            if len(points) >= 3:
                pygame.draw.polygon(surf, self.color, points)
                surf.set_alpha(self.alpha)
            screen.blit(surf, (self.x - self.size, self.y - self.size))

class ParticleSystem:
    """Manages all particles in the game."""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.particles = []
        self.background_particles = []
        self.generate_background_particles()
    
    def generate_background_particles(self):
        """Generate background ambient particles."""
        for _ in range(60):
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height)
            colors = [PRIMARY_BLUE, SUCCESS_GREEN, ACCENT_BLUE, WARNING_ORANGE]
            color = random.choice(colors)
            vx = random.uniform(-0.2, 0.2)
            vy = random.uniform(-0.2, 0.2)
            particle = Particle(x, y, color, (vx, vy))
            particle.life = random.uniform(0.3, 0.7)
            self.background_particles.append(particle)
    
    def create_particles(self, x: int, y: int, color: Tuple[int, int, int], count: int = 12):
        """Create a burst of particles at the specified location."""
        for _ in range(count):
            vx = random.uniform(-3, 3)
            vy = random.uniform(-5, -2)
            particle = Particle(x, y, color, (vx, vy))
            self.particles.append(particle)
    
    def update_particles(self):
        """Update all particles."""
        # Update background particles
        for particle in self.background_particles:
            particle.update()
            if particle.life <= 0:
                particle.x = random.randint(0, self.screen_width)
                particle.y = random.randint(0, self.screen_height)
                particle.life = random.uniform(0.3, 0.7)
        
        # Update and clean up effect particles
        self.particles = [p for p in self.particles if p.life > 0]
        for particle in self.particles:
            particle.update()
    
    def draw_particles(self, screen):
        """Draw all particles on the screen."""
        for particle in self.background_particles:
            particle.draw(screen)
        for particle in self.particles:
            particle.draw(screen)
    
    def resize(self, new_width: int, new_height: int):
        """Resize the particle system for new screen dimensions."""
        self.screen_width = new_width
        self.screen_height = new_height
        self.background_particles.clear()
        self.generate_background_particles()

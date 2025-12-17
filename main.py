#!/usr/bin/env python3
"""
Project Artillery - Retro Beach Dog Artillery Game
Sunrise Phase Implementation
"""

import pygame
import math
import sys
import random
import time
import os
import json

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Constants - Sunrise Phase Colors
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 120  # Increased for smoother movement

# Sunrise Color Palette
COLORS = {
    'sky_upper': (135, 206, 250),      # Crisp bright blue sky
    'sky_lower': (176, 224, 255),      # Lighter blue for gradient
    'horizon': (255, 248, 220),        # Light cream horizon
    'water_foam': (232, 248, 245),     # #E8F8F5 - Mint Foam
    'player_coral': (255, 127, 80),    # #FF7F50 - Coral (Players)
    'text_slate': (93, 109, 126),      # #5D6D7E - Slate Gray
    'ui_blush': (253, 237, 236),       # #FDEDEC - Blush White
    'sand': (194, 154, 108),           # Darker, more saturated sand for better contrast
    'sand_highlight': (220, 180, 140), # Lighter sand for dune highlights
    'sand_shadow': (160, 120, 80),     # Darker sand for dune shadows
    'mountain': (101, 67, 33),         # Dark brown for visible mountains/high terrain
    'mountain_shadow': (80, 50, 25),   # Even darker brown for mountain shadows
    'palm_trunk': (139, 69, 19),       # Palm tree trunk
    'palm_leaves': (34, 139, 34)       # Palm tree leaves
}

class GameSettings:
    """Manages game configuration and settings"""
    
    def __init__(self, settings_file="game_settings.json"):
        self.settings_file = settings_file
        
        # Default settings
        self.default_settings = {
            'audio': {
                'master_volume': 0.7,
                'sfx_volume': 0.8,
                'audio_enabled': True
            },
            'visual_effects': {
                'particle_intensity': 1.0,  # 0.5 = low, 1.0 = normal, 1.5 = high
                'explosion_intensity': 1.0,
                'trail_intensity': 1.0,
                'screen_shake': True
            },
            'terrain': {
                'complexity': 1.0,  # 0.5 = simple, 1.0 = normal, 1.5 = complex
                'destructible_terrain': True,
                'varied_terrain': True
            },
            'gameplay': {
                'turn_timer': 30,  # seconds per turn (0 = unlimited)
                'wind_effects': False,
                'gravity_strength': 1.0
            }
        }
        
        # Current settings (loaded from file or defaults)
        self.settings = self.default_settings.copy()
        
        # Load settings from file
        self.load_settings()
    
    def load_settings(self):
        """Load settings from JSON file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    self._merge_settings(self.settings, loaded_settings)
                print(f"Settings loaded from {self.settings_file}")
            else:
                print(f"Settings file not found, using defaults")
        except Exception as e:
            print(f"Error loading settings: {e}, using defaults")
            self.settings = self.default_settings.copy()
    
    def save_settings(self):
        """Save current settings to JSON file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            print(f"Settings saved to {self.settings_file}")
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def _merge_settings(self, target, source):
        """Recursively merge settings dictionaries"""
        for key, value in source.items():
            if key in target:
                if isinstance(value, dict) and isinstance(target[key], dict):
                    self._merge_settings(target[key], value)
                else:
                    target[key] = value
    
    def get_audio_volume(self):
        """Get master audio volume (0.0 to 1.0)"""
        return self.settings['audio']['master_volume']
    
    def set_audio_volume(self, volume):
        """Set master audio volume (0.0 to 1.0)"""
        self.settings['audio']['master_volume'] = max(0.0, min(1.0, volume))
    
    def get_sfx_volume(self):
        """Get sound effects volume (0.0 to 1.0)"""
        return self.settings['audio']['sfx_volume']
    
    def set_sfx_volume(self, volume):
        """Set sound effects volume (0.0 to 1.0)"""
        self.settings['audio']['sfx_volume'] = max(0.0, min(1.0, volume))
    
    def is_audio_enabled(self):
        """Check if audio is enabled"""
        return self.settings['audio']['audio_enabled']
    
    def set_audio_enabled(self, enabled):
        """Enable or disable audio"""
        self.settings['audio']['audio_enabled'] = enabled
    
    def get_particle_intensity(self):
        """Get visual effects particle intensity (0.5 to 2.0)"""
        return self.settings['visual_effects']['particle_intensity']
    
    def set_particle_intensity(self, intensity):
        """Set visual effects particle intensity (0.5 to 2.0)"""
        self.settings['visual_effects']['particle_intensity'] = max(0.5, min(2.0, intensity))
    
    def get_explosion_intensity(self):
        """Get explosion effect intensity (0.5 to 2.0)"""
        return self.settings['visual_effects']['explosion_intensity']
    
    def set_explosion_intensity(self, intensity):
        """Set explosion effect intensity (0.5 to 2.0)"""
        self.settings['visual_effects']['explosion_intensity'] = max(0.5, min(2.0, intensity))
    
    def get_trail_intensity(self):
        """Get projectile trail intensity (0.5 to 2.0)"""
        return self.settings['visual_effects']['trail_intensity']
    
    def set_trail_intensity(self, intensity):
        """Set projectile trail intensity (0.5 to 2.0)"""
        self.settings['visual_effects']['trail_intensity'] = max(0.5, min(2.0, intensity))
    
    def is_screen_shake_enabled(self):
        """Check if screen shake effects are enabled"""
        return self.settings['visual_effects']['screen_shake']
    
    def set_screen_shake_enabled(self, enabled):
        """Enable or disable screen shake effects"""
        self.settings['visual_effects']['screen_shake'] = enabled
    
    def get_terrain_complexity(self):
        """Get terrain generation complexity (0.5 to 2.0)"""
        return self.settings['terrain']['complexity']
    
    def set_terrain_complexity(self, complexity):
        """Set terrain generation complexity (0.5 to 2.0)"""
        self.settings['terrain']['complexity'] = max(0.5, min(2.0, complexity))
    
    def is_destructible_terrain_enabled(self):
        """Check if destructible terrain is enabled"""
        return self.settings['terrain']['destructible_terrain']
    
    def set_destructible_terrain_enabled(self, enabled):
        """Enable or disable destructible terrain"""
        self.settings['terrain']['destructible_terrain'] = enabled
    
    def is_varied_terrain_enabled(self):
        """Check if varied terrain generation is enabled"""
        return self.settings['terrain']['varied_terrain']
    
    def set_varied_terrain_enabled(self, enabled):
        """Enable or disable varied terrain generation"""
        self.settings['terrain']['varied_terrain'] = enabled
    
    def get_turn_timer(self):
        """Get turn timer in seconds (0 = unlimited)"""
        return self.settings['gameplay']['turn_timer']
    
    def set_turn_timer(self, seconds):
        """Set turn timer in seconds (0 = unlimited)"""
        self.settings['gameplay']['turn_timer'] = max(0, seconds)
    
    def reset_to_defaults(self):
        """Reset all settings to default values"""
        self.settings = self.default_settings.copy()
        print("Settings reset to defaults")

class Particle:
    """Individual particle for visual effects"""
    
    def __init__(self, x, y, velocity_x, velocity_y, particle_type="fire", color=None, size=2, lifetime=60):
        self.x = x
        self.y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.particle_type = particle_type
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.active = True
        
        # Set default colors based on particle type
        if color is None:
            if particle_type == "fire":
                self.color = (255, random.randint(100, 255), random.randint(0, 50))
            elif particle_type == "smoke":
                gray = random.randint(80, 150)
                self.color = (gray, gray, gray)
            elif particle_type == "debris":
                self.color = COLORS['sand']
            elif particle_type == "trail":
                self.color = (255, 165, 0)  # Orange trail
            else:
                self.color = (255, 255, 255)
        else:
            self.color = color
    
    def update(self):
        """Update particle position and lifetime"""
        if not self.active:
            return False
        
        # Update position
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Apply physics based on particle type
        if self.particle_type == "fire":
            # Fire rises and slows down
            self.velocity_y -= 0.1
            self.velocity_x *= 0.98
        elif self.particle_type == "smoke":
            # Smoke rises slowly and spreads
            self.velocity_y -= 0.05
            self.velocity_x *= 0.95
        elif self.particle_type == "debris":
            # Debris falls with gravity
            self.velocity_y += 0.3
            self.velocity_x *= 0.99
        elif self.particle_type == "trail":
            # Trail particles fade quickly
            self.velocity_x *= 0.9
            self.velocity_y *= 0.9
        
        # Update lifetime
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.active = False
            return False
        
        return True
    
    def draw(self, screen):
        """Draw the particle"""
        if not self.active:
            return
        
        # Calculate alpha based on remaining lifetime
        alpha_ratio = self.lifetime / self.max_lifetime
        
        # Adjust size based on lifetime for some particle types
        current_size = self.size
        if self.particle_type == "fire":
            current_size = int(self.size * (0.5 + alpha_ratio * 0.5))
        elif self.particle_type == "smoke":
            current_size = int(self.size * (1 + (1 - alpha_ratio) * 0.5))
        
        # Draw particle as circle
        if current_size > 0:
            # Create color with alpha effect by blending with background
            fade_color = (
                int(self.color[0] * alpha_ratio),
                int(self.color[1] * alpha_ratio),
                int(self.color[2] * alpha_ratio)
            )
            pygame.draw.circle(screen, fade_color, (int(self.x), int(self.y)), current_size)

class ParticleSystem:
    """Manages a collection of particles for specific effects"""
    
    def __init__(self, max_particles=100):
        self.particles = []
        self.max_particles = max_particles
    
    def add_particle(self, x, y, velocity_x, velocity_y, particle_type="fire", color=None, size=2, lifetime=60):
        """Add a new particle to the system"""
        if len(self.particles) < self.max_particles:
            particle = Particle(x, y, velocity_x, velocity_y, particle_type, color, size, lifetime)
            self.particles.append(particle)
    
    def add_explosion_particles(self, x, y, intensity=1.0, weapon_type="rocket"):
        """Create explosion effect with fire, smoke, and debris particles"""
        base_particle_count = 25 if weapon_type == "banana" else 20
        particle_count = int(base_particle_count * intensity)
        
        for _ in range(particle_count):
            # Random direction and speed with weapon-specific characteristics
            angle = random.uniform(0, 2 * math.pi)
            
            if weapon_type == "banana":
                # Banana explosions are more chaotic and spread out
                speed = random.uniform(3, 12) * intensity
                particle_type = random.choice(["fire", "fire", "fire", "smoke", "debris", "debris"])
            elif weapon_type == "rocket":
                # Rocket explosions are more focused and intense
                speed = random.uniform(2, 10) * intensity
                particle_type = random.choice(["fire", "fire", "smoke", "debris"])
            else:  # melee
                speed = random.uniform(1, 6) * intensity
                particle_type = random.choice(["fire", "smoke", "debris", "debris"])
            
            velocity_x = math.cos(angle) * speed
            velocity_y = math.sin(angle) * speed
            
            # Scale particle properties with intensity
            if particle_type == "fire":
                size = random.randint(int(2 * intensity), int(5 * intensity))
                lifetime = random.randint(int(40 * intensity), int(100 * intensity))
                # More intense fires are brighter
                if intensity > 1.2:
                    fire_color = (255, random.randint(150, 255), random.randint(0, 100))
                else:
                    fire_color = None  # Use default
            elif particle_type == "smoke":
                size = random.randint(int(1 * intensity), int(4 * intensity))
                lifetime = random.randint(int(80 * intensity), int(150 * intensity))
                fire_color = None
            else:  # debris
                size = random.randint(1, int(3 * intensity))
                lifetime = random.randint(int(60 * intensity), int(120 * intensity))
                # Debris color varies with weapon type
                if weapon_type == "banana":
                    fire_color = (200, 180, 0)  # Yellowish debris
                else:
                    fire_color = None  # Use default sand color
            
            self.add_particle(x, y, velocity_x, velocity_y, particle_type, fire_color, size, lifetime)
    
    def add_trail_particles(self, x, y, velocity_x, velocity_y, weapon_type="rocket", power_level=50):
        """Add trail particles for projectiles with power-based intensity"""
        if weapon_type == "rocket":
            # Enhanced flame trail with power scaling
            power_scale = 1.0 + (power_level / 100.0) * 0.8
            particle_count = int(4 * power_scale)  # More particles for higher power
            
            for _ in range(particle_count):
                # More spread for higher power rockets
                spread = 2 + power_scale
                trail_x = x + random.uniform(-spread, spread)
                trail_y = y + random.uniform(-spread, spread)
                
                # Trail particles move opposite to projectile direction with some randomness
                trail_vel_x = -velocity_x * random.uniform(0.2, 0.4) + random.uniform(-1.5, 1.5)
                trail_vel_y = -velocity_y * random.uniform(0.2, 0.4) + random.uniform(-1.5, 1.5)
                
                # Vary particle properties based on power
                particle_size = random.randint(1, int(2 + power_scale))
                particle_lifetime = random.randint(int(15 * power_scale), int(25 * power_scale))
                
                # Create different types of trail particles
                particle_type = random.choice(["trail", "fire", "fire"])  # More fire particles
                
                # Enhanced colors for trail particles
                if particle_type == "trail":
                    trail_color = (255, random.randint(100, 200), random.randint(0, 50))
                else:
                    trail_color = None  # Use default fire color
                
                self.add_particle(trail_x, trail_y, trail_vel_x, trail_vel_y, 
                                particle_type, trail_color, particle_size, particle_lifetime)
        elif weapon_type == "banana":
            # Banana doesn't have trail particles, but could have a subtle effect
            if random.randint(1, 10) == 1:  # Occasional sparkle
                sparkle_x = x + random.uniform(-3, 3)
                sparkle_y = y + random.uniform(-3, 3)
                self.add_particle(sparkle_x, sparkle_y, 0, 0, "trail", 
                                (255, 255, 100), 1, 5)
    
    def update(self):
        """Update all particles and remove inactive ones"""
        self.particles = [p for p in self.particles if p.update()]
    
    def draw(self, screen):
        """Draw all active particles"""
        for particle in self.particles:
            particle.draw(screen)
    
    def clear(self):
        """Remove all particles"""
        self.particles.clear()

class EffectsManager:
    """Centralized manager for all visual effects"""
    
    def __init__(self, game_settings=None):
        self.game_settings = game_settings
        
        # Get intensity settings
        particle_intensity = 1.0
        if self.game_settings:
            particle_intensity = self.game_settings.get_particle_intensity()
        
        # Scale particle system sizes based on intensity
        explosion_particles = int(200 * particle_intensity)
        trail_particles = int(100 * particle_intensity)
        environment_particles = int(50 * particle_intensity)
        
        self.particle_systems = {
            'explosions': ParticleSystem(explosion_particles),
            'trails': ParticleSystem(trail_particles),
            'environment': ParticleSystem(environment_particles)
        }
        
        # Effect pooling for performance
        self.active_effects = []
        self.effect_pool = []
    
    def create_explosion(self, x, y, intensity=1.0, weapon_type="rocket"):
        """Create explosion effect at specified location"""
        # Apply settings-based intensity scaling
        final_intensity = intensity
        if self.game_settings:
            final_intensity *= self.game_settings.get_explosion_intensity()
        
        self.particle_systems['explosions'].add_explosion_particles(x, y, final_intensity, weapon_type)
    
    def create_projectile_trail(self, x, y, velocity_x, velocity_y, weapon_type="rocket", power_level=50):
        """Create trail effect for projectiles"""
        self.particle_systems['trails'].add_trail_particles(x, y, velocity_x, velocity_y, weapon_type, power_level)
    
    def create_weapon_charge_effect(self, x, y, power_level):
        """Create charging effect for weapons with enhanced visuals at 25%, 50%, 75%, 100% thresholds"""
        if power_level > 10:  # Show effect earlier
            # Scale effect intensity with power level
            intensity = power_level / 100.0
            
            # Escalating particle count at thresholds: 25%, 50%, 75%, 100%
            if power_level >= 100:
                particle_count = 8  # Maximum particles at 100%
            elif power_level >= 75:
                particle_count = 6  # High particles at 75%+
            elif power_level >= 50:
                particle_count = 4  # Medium particles at 50%+
            elif power_level >= 25:
                particle_count = 3  # Low particles at 25%+
            else:
                particle_count = 2  # Minimal particles below 25%
            
            # Add sparkling particles around the weapon
            for _ in range(particle_count):
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(8, 20 + intensity * 10)
                spark_x = x + math.cos(angle) * distance
                spark_y = y + math.sin(angle) * distance
                
                # Particle velocity creates swirling effect
                vel_x = math.cos(angle + math.pi/2) * 0.5
                vel_y = math.sin(angle + math.pi/2) * 0.5 - 0.3  # Slight upward drift
                
                # Color changes at thresholds: 25%, 50%, 75%, 100%
                if power_level >= 100:
                    spark_color = (255, 50, 0)     # Intense red at 100%
                elif power_level >= 75:
                    spark_color = (255, 100, 0)   # Bright orange-red at 75%+
                elif power_level >= 50:
                    spark_color = (255, 200, 0)   # Orange-yellow at 50%+
                elif power_level >= 25:
                    spark_color = (255, 255, 100) # Yellow at 25%+
                else:
                    spark_color = (255, 255, 150) # Pale yellow below 25%
                
                # Particle size scales with thresholds
                if power_level >= 75:
                    particle_size = 3
                elif power_level >= 50:
                    particle_size = 2
                else:
                    particle_size = 1
                    
                particle_lifetime = int(10 + intensity * 15)
                
                self.particle_systems['environment'].add_particle(
                    spark_x, spark_y, vel_x, vel_y, "fire", 
                    spark_color, particle_size, particle_lifetime
                )
            
            # Add central charging glow at 75%+ power levels
            if power_level >= 75:
                # Central glow particle - larger at 100%
                glow_size = 4 if power_level >= 100 else 3
                self.particle_systems['environment'].add_particle(
                    x, y, 0, 0, "fire",
                    (255, 255, 255), glow_size, 5
                )
    
    def update_all_effects(self):
        """Update all particle systems"""
        for system in self.particle_systems.values():
            system.update()
    
    def draw_all_effects(self, screen):
        """Draw all visual effects"""
        for system in self.particle_systems.values():
            system.draw(screen)
    
    def clear_all_effects(self):
        """Clear all effects (useful for game reset)"""
        for system in self.particle_systems.values():
            system.clear()

class AudioManager:
    """Centralized manager for all sound effects and audio"""
    
    def __init__(self, game_settings=None):
        self.sounds = {}
        self.game_settings = game_settings
        self.master_volume = 0.7
        self.sfx_volume = 0.8
        self.audio_enabled = True
        
        # Apply settings if provided
        if self.game_settings:
            self.master_volume = self.game_settings.get_audio_volume()
            self.sfx_volume = self.game_settings.get_sfx_volume()
            self.audio_enabled = self.game_settings.is_audio_enabled()
        
        # Try to initialize audio system
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        except pygame.error as e:
            print(f"Audio initialization failed: {e}")
            self.audio_enabled = False
        
        # Load all sound effects
        self.load_sounds()
    
    def load_sounds(self):
        """Preload all game audio assets"""
        if not self.audio_enabled:
            return
        
        # Define sound files and their properties
        sound_definitions = {
            # Weapon firing sounds
            'rocket_fire': {'volume': 0.8, 'fallback_freq': 440},
            'banana_fire': {'volume': 0.6, 'fallback_freq': 330},
            'melee_fire': {'volume': 0.5, 'fallback_freq': 220},
            
            # Explosion sounds
            'rocket_explosion': {'volume': 1.0, 'fallback_freq': 150},
            'banana_explosion': {'volume': 1.2, 'fallback_freq': 120},
            'melee_explosion': {'volume': 0.8, 'fallback_freq': 180},
            
            # Movement sounds
            'player_jump': {'volume': 0.4, 'fallback_freq': 400},
            'player_land': {'volume': 0.3, 'fallback_freq': 200},
            'player_move': {'volume': 0.2, 'fallback_freq': 300},
            
            # Power and UI sounds
            'power_charge': {'volume': 0.5, 'fallback_freq': 500},
            'power_release': {'volume': 0.6, 'fallback_freq': 600},
            
            # Terrain destruction
            'terrain_destroy': {'volume': 0.7, 'fallback_freq': 100},
            'tree_destroy': {'volume': 0.6, 'fallback_freq': 250}
        }
        
        # Create sounds directory if it doesn't exist
        sounds_dir = "sounds"
        if not os.path.exists(sounds_dir):
            os.makedirs(sounds_dir)
        
        # Load or generate sounds
        for sound_name, properties in sound_definitions.items():
            sound_path = os.path.join(sounds_dir, f"{sound_name}.wav")
            
            try:
                if os.path.exists(sound_path):
                    # Load existing sound file
                    sound = pygame.mixer.Sound(sound_path)
                else:
                    # Skip procedural sound generation for now - just use None
                    # The game will work silently without audio files
                    sound = None
                    print(f"Audio file not found for {sound_name}, running silently")
                
                # Set volume only if sound was created successfully
                if sound is not None:
                    sound.set_volume(properties['volume'] * self.master_volume)
                self.sounds[sound_name] = sound
                
            except pygame.error as e:
                print(f"Failed to load sound {sound_name}: {e}")
                # Create a silent sound as fallback
                self.sounds[sound_name] = None
            except Exception as e:
                print(f"Unexpected error loading sound {sound_name}: {e}")
                self.sounds[sound_name] = None
    
    def _generate_procedural_sound(self, base_freq, sound_type):
        """Generate simple procedural sounds for retro feel"""
        try:
            import numpy as np
            
            sample_rate = 22050
            duration = 0.3  # Default duration
            
            # Adjust duration and characteristics based on sound type
            if 'explosion' in sound_type:
                duration = 0.8
                # Create explosion-like noise with frequency sweep
                t = np.linspace(0, duration, int(sample_rate * duration))
                # Start with noise and sweep down in frequency
                noise = np.random.normal(0, 0.3, len(t))
                freq_sweep = base_freq * np.exp(-t * 3)  # Exponential decay
                wave = np.sin(2 * np.pi * freq_sweep * t) * np.exp(-t * 2)
                sound_array = (noise * 0.3 + wave * 0.7) * 32767
                
            elif 'fire' in sound_type:
                duration = 0.2
                # Create firing sound with quick attack
                t = np.linspace(0, duration, int(sample_rate * duration))
                wave = np.sin(2 * np.pi * base_freq * t) * np.exp(-t * 8)
                # Add some harmonics for richness
                wave += 0.3 * np.sin(2 * np.pi * base_freq * 2 * t) * np.exp(-t * 10)
                sound_array = wave * 32767
                
            elif 'jump' in sound_type:
                duration = 0.15
                # Create jumping sound with frequency rise
                t = np.linspace(0, duration, int(sample_rate * duration))
                freq_rise = base_freq * (1 + t * 2)
                wave = np.sin(2 * np.pi * freq_rise * t) * np.exp(-t * 5)
                sound_array = wave * 32767
                
            elif 'charge' in sound_type:
                duration = 0.1
                # Create charging sound with rising pitch
                t = np.linspace(0, duration, int(sample_rate * duration))
                freq_rise = base_freq * (1 + t * 0.5)
                wave = np.sin(2 * np.pi * freq_rise * t) * (1 - np.exp(-t * 10))
                sound_array = wave * 32767
                
            else:
                # Default simple tone
                t = np.linspace(0, duration, int(sample_rate * duration))
                wave = np.sin(2 * np.pi * base_freq * t) * np.exp(-t * 3)
                sound_array = wave * 32767
            
            # Convert to pygame sound
            sound_array = sound_array.astype(np.int16)
            # Make stereo
            stereo_array = np.array([sound_array, sound_array]).T
            sound = pygame.sndarray.make_sound(stereo_array)
            
            return sound
            
        except ImportError:
            # Fallback if numpy is not available - create simple beep
            return self._create_simple_beep(base_freq, 0.2)
        except Exception as e:
            print(f"Failed to generate procedural sound: {e}")
            return self._create_simple_beep(base_freq, 0.2)
    
    def _create_simple_beep(self, frequency, duration):
        """Create a simple beep sound without numpy"""
        try:
            # Try to use sndarray if available
            sample_rate = 22050
            frames = int(duration * sample_rate)
            
            # Create simple sine wave manually
            sound_data = []
            for i in range(frames):
                t = float(i) / sample_rate
                # Simple sine wave with exponential decay
                amplitude = 0.3 * (1.0 - t / duration)  # Linear decay
                sample = int(amplitude * 32767 * math.sin(2 * math.pi * frequency * t))
                sound_data.append([sample, sample])  # Stereo
            
            # Convert to pygame sound
            sound = pygame.sndarray.make_sound(sound_data)
            return sound
            
        except Exception as e:
            print(f"Failed to create simple beep: {e}")
            # Return None if sound generation fails - game will work without audio
            return None
    
    def play_sound(self, sound_name, volume=1.0):
        """Play named sound effect"""
        if not self.audio_enabled or sound_name not in self.sounds:
            return
        
        sound = self.sounds[sound_name]
        if sound is not None:
            try:
                # Create a copy to avoid conflicts with multiple simultaneous plays
                sound_copy = sound.copy() if hasattr(sound, 'copy') else sound
                # Apply both master volume and SFX volume
                final_volume = volume * self.master_volume * self.sfx_volume
                sound_copy.set_volume(final_volume)
                sound_copy.play()
            except pygame.error as e:
                print(f"Failed to play sound {sound_name}: {e}")
    
    def set_master_volume(self, volume):
        """Control overall audio level"""
        self.master_volume = max(0.0, min(1.0, volume))
        
        # Update volume for all loaded sounds
        for sound_name, sound in self.sounds.items():
            if sound is not None:
                # Get original volume from sound definitions (simplified)
                base_volume = 0.7  # Default volume
                sound.set_volume(base_volume * self.master_volume * self.sfx_volume)
    
    def set_sfx_volume(self, volume):
        """Control sound effects volume level"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        
        # Update volume for all loaded sounds
        for sound_name, sound in self.sounds.items():
            if sound is not None:
                # Get original volume from sound definitions (simplified)
                base_volume = 0.7  # Default volume
                sound.set_volume(base_volume * self.master_volume * self.sfx_volume)
    
    def update_settings(self, game_settings):
        """Update audio settings from game settings"""
        if game_settings:
            self.master_volume = game_settings.get_audio_volume()
            self.sfx_volume = game_settings.get_sfx_volume()
            self.audio_enabled = game_settings.is_audio_enabled()
            
            # Update all sound volumes
            self.set_master_volume(self.master_volume)
    
    def toggle_audio(self):
        """Enable/disable audio system"""
        self.audio_enabled = not self.audio_enabled
        if not self.audio_enabled:
            pygame.mixer.stop()
    
    def play_weapon_fire_sound(self, weapon_type):
        """Play weapon-specific firing sound"""
        sound_map = {
            'rocket': 'rocket_fire',
            'banana': 'banana_fire', 
            'melee': 'melee_fire'
        }
        
        sound_name = sound_map.get(weapon_type, 'rocket_fire')
        self.play_sound(sound_name)
    
    def play_explosion_sound(self, weapon_type):
        """Play weapon-specific explosion sound"""
        sound_map = {
            'rocket': 'rocket_explosion',
            'banana': 'banana_explosion',
            'melee': 'melee_explosion'
        }
        
        sound_name = sound_map.get(weapon_type, 'rocket_explosion')
        self.play_sound(sound_name)
    
    def play_movement_sound(self, movement_type):
        """Play movement-related sound"""
        sound_map = {
            'jump': 'player_jump',
            'land': 'player_land',
            'move': 'player_move'
        }
        
        sound_name = sound_map.get(movement_type, 'player_move')
        self.play_sound(sound_name, 0.3)  # Lower volume for movement sounds
    
    def play_power_sound(self, action):
        """Play power-related sound"""
        if action == 'charge':
            self.play_sound('power_charge', 0.4)
        elif action == 'release':
            self.play_sound('power_release', 0.6)
    
    def play_destruction_sound(self, destruction_type):
        """Play terrain/object destruction sound"""
        sound_map = {
            'terrain': 'terrain_destroy',
            'tree': 'tree_destroy'
        }
        
        sound_name = sound_map.get(destruction_type, 'terrain_destroy')
        self.play_sound(sound_name)

class Projectile:
    def __init__(self, x, y, velocity_x, velocity_y, weapon_type="rocket", power_level=50):
        self.x = x
        self.y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.weapon_type = weapon_type
        self.power_level = power_level
        self.active = True
        self.explosion_radius = 40 if weapon_type == "rocket" else 60  # Banana has bigger explosion
        self.timer = 180 if weapon_type == "banana" else 0  # Banana has 3-second timer at 60fps
        
        # Visual effect properties
        self.rotation = 0  # For spinning banana
        self.trail_particles = []  # For flame trails
        
    def update(self, terrain, players, effects_manager=None, audio_manager=None):
        if not self.active:
            return False
            
        # Update position
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Apply gravity
        self.velocity_y += 0.5
        
        # Update visual effects
        if self.weapon_type == "banana":
            # Spinning animation
            self.rotation += 10
            if self.rotation >= 360:
                self.rotation = 0
        
        # Create trail effects
        if effects_manager and self.weapon_type == "rocket":
            effects_manager.create_projectile_trail(self.x, self.y, self.velocity_x, self.velocity_y, self.weapon_type, self.power_level)
        elif effects_manager and self.weapon_type == "banana":
            # Add subtle sparkle effect for banana
            effects_manager.create_projectile_trail(self.x, self.y, self.velocity_x, self.velocity_y, self.weapon_type, self.power_level)
        
        # Banana timer countdown
        if self.weapon_type == "banana":
            self.timer -= 1
            if self.timer <= 0:
                self.explode(terrain, players, effects_manager, audio_manager)
                return True
        
        # Check ground collision with enhanced terrain system and angled surface detection
        ground_height = terrain.get_ground_height(self.x)
        
        if (self.y >= ground_height or terrain.terrain_map.is_solid_at(self.x, self.y)):
            # Calculate surface angle for more realistic collision
            left_height = terrain.get_ground_height(self.x - 5)
            right_height = terrain.get_ground_height(self.x + 5)
            surface_angle = math.degrees(math.atan2(right_height - left_height, 10))
            
            # For angled surfaces, adjust explosion position to surface level
            if abs(surface_angle) > 5:  # Significant slope
                # Move explosion point to actual surface contact
                surface_y = ground_height
                self.y = surface_y
            
            self.explode(terrain, players, effects_manager, audio_manager)
            return True
            
        # Check tree collision
        for tree in terrain.palm_trees:
            if tree['destroyed']:
                continue
            tree_left = tree['x'] - 6
            tree_right = tree['x'] + 6
            tree_top = terrain.ground_level - tree['height']
            tree_bottom = terrain.ground_level
            
            if (self.x >= tree_left and self.x <= tree_right and
                self.y >= tree_top and self.y <= tree_bottom):
                self.explode(terrain, players, effects_manager, audio_manager)
                return True
        
        # Check if off screen
        if self.x < -50 or self.x > SCREEN_WIDTH + 50 or self.y > SCREEN_HEIGHT + 50:
            self.active = False
            return True
            
        return False
    
    def explode(self, terrain, players, effects_manager=None, audio_manager=None):
        # Play explosion sound first
        if audio_manager:
            audio_manager.play_explosion_sound(self.weapon_type)
        
        # Create explosion visual effects
        if effects_manager:
            # Scale explosion intensity based on weapon type and power
            intensity = 1.0
            if self.weapon_type == "banana":
                intensity = 1.5  # Banana has bigger explosion
            elif self.weapon_type == "rocket":
                intensity = 1.0 + (self.power_level / 100.0) * 0.8  # Scale with power
            elif self.weapon_type == "melee":
                intensity = 0.8  # Smaller explosion for melee
            
            effects_manager.create_explosion(self.x, self.y, intensity, self.weapon_type)
        
        # Damage players in explosion radius
        for player in players:
            distance = math.sqrt((player.x + player.width/2 - self.x)**2 + 
                               (player.y + player.height/2 - self.y)**2)
            if distance <= self.explosion_radius:
                damage = max(0, int(50 - (distance / self.explosion_radius) * 30))
                player.health -= damage
                
                # Knockback effect
                knockback_force = max(0, 15 - distance/3)
                angle = math.atan2(player.y - self.y, player.x - self.x)
                player.velocity_x += math.cos(angle) * knockback_force
                player.velocity_y += math.sin(angle) * knockback_force - 5
        
        # Create crater in terrain using enhanced system
        terrain.terrain_map.create_crater(self.x, self.y, self.explosion_radius)
        
        # Merge overlapping craters
        terrain.terrain_map.merge_overlapping_craters()
        
        # Destroy trees in explosion radius
        tree_destroyed = terrain.destroy_tree_at(self.x, self.y, self.explosion_radius)
        
        # Play terrain destruction sounds
        if audio_manager:
            audio_manager.play_destruction_sound('terrain')
            if tree_destroyed:
                audio_manager.play_destruction_sound('tree')
        
        self.active = False
    
    def draw(self, screen):
        if not self.active:
            return
            
        if self.weapon_type == "rocket":
            # Enhanced rocket visual with power-based scaling
            base_size = 4
            power_scale = 1.0 + (self.power_level / 100.0) * 0.8  # Increased scaling
            rocket_size = int(base_size * power_scale)
            
            # Draw rocket body with more detail and power scaling
            # Outer shell (darker red)
            pygame.draw.circle(screen, (200, 0, 0), (int(self.x), int(self.y)), rocket_size + 1)
            # Main body (bright red)
            pygame.draw.circle(screen, (255, 0, 0), (int(self.x), int(self.y)), rocket_size)
            # Inner core (bright orange/yellow based on power)
            core_intensity = int(100 + (self.power_level / 100.0) * 155)
            core_color = (255, core_intensity, 0)
            pygame.draw.circle(screen, core_color, (int(self.x), int(self.y)), max(1, rocket_size - 1))
            
            # Enhanced flame trail with power-based intensity
            trail_length = 4 + int(power_scale * 3)
            trail_intensity = 0.5 + (self.power_level / 100.0) * 0.5
            
            for i in range(trail_length):
                trail_factor = 0.15 + i * 0.08
                trail_x = self.x - self.velocity_x * trail_factor
                trail_y = self.y - self.velocity_y * trail_factor
                trail_size = max(1, int((rocket_size - i) * trail_intensity))
                
                # More vibrant trail colors based on power
                if i == 0:
                    trail_color = (255, 200, 50)  # Bright yellow-orange
                elif i == 1:
                    trail_color = (255, 150, 0)   # Orange
                else:
                    red_component = max(100, 255 - i * 40)
                    trail_color = (red_component, max(0, 165 - i * 35), 0)
                
                pygame.draw.circle(screen, trail_color, (int(trail_x), int(trail_y)), trail_size)
            
            # Add power-based glow effect
            if self.power_level > 50:
                glow_size = int(rocket_size * 1.5)
                glow_alpha = int((self.power_level - 50) / 50.0 * 100)
                glow_color = (255, 100, 0)
                # Create glow effect by drawing multiple circles with decreasing intensity
                for glow_ring in range(3):
                    glow_radius = glow_size + glow_ring
                    pygame.draw.circle(screen, glow_color, (int(self.x), int(self.y)), glow_radius, 1)
                
        elif self.weapon_type == "banana":
            # Enhanced banana with spinning animation and timer indicator
            # More pronounced rotation effect
            rotation_offset_x = math.sin(math.radians(self.rotation)) * 3
            rotation_offset_y = math.cos(math.radians(self.rotation)) * 1.5
            
            # Draw banana body with enhanced rotation effect
            banana_width = 8 + int(abs(rotation_offset_x))
            banana_height = 5 + int(abs(rotation_offset_y))
            banana_rect = (self.x - banana_width//2, self.y - banana_height//2, banana_width, banana_height)
            
            # Main banana body (bright yellow)
            pygame.draw.ellipse(screen, (255, 255, 0), banana_rect)
            
            # Add banana curve effect based on rotation
            curve_points = []
            for i in range(5):
                curve_x = self.x - banana_width//2 + (i * banana_width//4)
                curve_y = self.y + math.sin(math.radians(self.rotation + i * 30)) * 2
                curve_points.append((curve_x, curve_y))
            
            if len(curve_points) >= 2:
                pygame.draw.lines(screen, (200, 200, 0), False, curve_points, 2)
            
            # Enhanced banana spots with rotation
            spot_color = (180, 180, 0)
            spot1_x = self.x + rotation_offset_x * 0.3 - 2
            spot1_y = self.y + rotation_offset_y * 0.3
            spot2_x = self.x - rotation_offset_x * 0.3 + 2
            spot2_y = self.y - rotation_offset_y * 0.3 + 1
            
            pygame.draw.circle(screen, spot_color, (int(spot1_x), int(spot1_y)), 1)
            pygame.draw.circle(screen, spot_color, (int(spot2_x), int(spot2_y)), 1)
            
            # Enhanced timer indicator with more visual feedback
            if self.timer > 0:
                timer_ratio = self.timer / 180.0
                
                # Multiple timer rings for better visibility
                base_radius = 12
                ring_radius = int(base_radius * timer_ratio) + 5
                
                # Color progression: Green -> Yellow -> Orange -> Red
                if timer_ratio > 0.75:
                    timer_color = (int(255 * (1 - timer_ratio) * 4), 255, 0)  # Green to yellow
                elif timer_ratio > 0.5:
                    timer_color = (255, 255, int(255 * (timer_ratio - 0.5) * 4))  # Yellow to orange
                elif timer_ratio > 0.25:
                    timer_color = (255, int(255 * (timer_ratio - 0.25) * 4), 0)  # Orange to red
                else:
                    timer_color = (255, 0, 0)  # Red
                
                # Enhanced flashing effect when timer is critical
                if self.timer < 60:
                    flash_speed = max(3, self.timer // 10)  # Faster flashing as time runs out
                    if self.timer % flash_speed < flash_speed // 2:
                        # Draw pulsing rings
                        for ring in range(3):
                            ring_size = ring_radius + ring * 2
                            pygame.draw.circle(screen, timer_color, (int(self.x), int(self.y - 12)), ring_size, 2)
                        
                        # Critical warning indicators
                        if self.timer < 30:
                            # Draw warning triangles
                            warning_points = [
                                (self.x - 8, self.y - 20),
                                (self.x + 8, self.y - 20),
                                (self.x, self.y - 25)
                            ]
                            pygame.draw.polygon(screen, (255, 0, 0), warning_points)
                            pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y - 22)), 1)
                else:
                    # Normal timer display
                    pygame.draw.circle(screen, timer_color, (int(self.x), int(self.y - 12)), ring_radius, 2)
                    # Inner timer dot
                    inner_size = max(1, int(ring_radius * 0.3))
                    pygame.draw.circle(screen, timer_color, (int(self.x), int(self.y - 12)), inner_size)
                    
        elif self.weapon_type == "melee":
            # Enhanced melee projectile with power scaling
            base_size = 3
            power_scale = 1.0 + (self.power_level / 100.0) * 0.5
            melee_size = int(base_size * power_scale)
            
            # Draw melee projectile with more detail
            pygame.draw.circle(screen, (100, 50, 0), (int(self.x), int(self.y)), melee_size + 1)  # Outer ring
            pygame.draw.circle(screen, (150, 75, 0), (int(self.x), int(self.y)), melee_size)      # Main body
            pygame.draw.circle(screen, (200, 100, 0), (int(self.x), int(self.y)), max(1, melee_size - 1))  # Inner highlight

class Player:
    def __init__(self, x, y, player_id):
        self.x = x
        self.y = y
        self.player_id = player_id
        self.width = 32
        self.height = 32
        self.health = 100
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        
        # ARCADE MOVEMENT CONSTANTS - Instant response, no momentum
        self.move_speed = 6  # Direct position change per frame (not velocity)
        self.jump_power = -18  # Strong initial jump impulse
        self.gravity = 1.5  # High gravity for tight, snappy jumps
        self.max_fall_speed = 20  # Terminal velocity
        self.is_jumping = False  # Track if jump button is held
        self.moving = False  # Track if movement key is pressed this frame
        
        # Weapon system
        self.aim_angle = -45 if player_id == 0 else -135  # Default angles
        self.power = 0
        self.charging_power = False
        self.current_weapon = "rocket"  # "rocket", "banana", "melee"
        
    def update(self, terrain, audio_manager=None):
        """Pure arcade physics - instant movement, tight jumps, no sliding"""
        old_y = self.y
        
        # HORIZONTAL MOVEMENT - Direct position control, NO velocity/friction
        # Movement is handled directly in move_left/move_right
        # If not moving this frame, velocity is zero (instant stop)
        if not self.moving:
            self.velocity_x = 0
        self.moving = False  # Reset for next frame
        
        # Apply horizontal movement
        self.x += self.velocity_x
        
        # VERTICAL PHYSICS - Gravity and jumping
        if not self.on_ground:
            self.velocity_y += self.gravity
            # Cap fall speed
            if self.velocity_y > self.max_fall_speed:
                self.velocity_y = self.max_fall_speed
        
        # Apply vertical movement
        self.y += self.velocity_y
        
        # GROUND COLLISION - Simple and fast
        ground_collision = False
        min_ground_height = terrain.terrain_map.height
        
        # Check 3 points under player for ground
        for check_x in [self.x + 4, self.x + self.width // 2, self.x + self.width - 4]:
            ground_y = terrain.terrain_map.get_accurate_ground_height(check_x, self.y)
            if self.y + self.height >= ground_y:
                min_ground_height = min(min_ground_height, ground_y)
                ground_collision = True
        
        if ground_collision:
            # Snap to ground - instant, no sliding
            self.y = min_ground_height - self.height
            
            # Landing
            if self.velocity_y > 0:
                if audio_manager and self.velocity_y > 8:
                    audio_manager.play_movement_sound('land')
                self.velocity_y = 0
            
            self.on_ground = True
        else:
            self.on_ground = False
        
        # TREE COLLISION - Simplified
        for tree in terrain.palm_trees:
            if tree['destroyed']:
                continue
            
            tree_left = tree['x'] - 6
            tree_right = tree['x'] + 6
            tree_top = terrain.ground_level - tree['height']
            tree_bottom = terrain.ground_level
            
            if (self.x < tree_right and self.x + self.width > tree_left and
                self.y < tree_bottom and self.y + self.height > tree_top):
                
                # Landing on tree top
                if old_y + self.height <= tree_top + 8 and self.velocity_y >= 0:
                    self.y = tree_top - self.height
                    if audio_manager and self.velocity_y > 8:
                        audio_manager.play_movement_sound('land')
                    self.velocity_y = 0
                    self.on_ground = True
                    break
                else:
                    # Side collision - push out
                    player_center = self.x + self.width / 2
                    if player_center < tree['x']:
                        self.x = tree_left - self.width
                    else:
                        self.x = tree_right
        
        # Screen bounds
        self.x = max(0, min(SCREEN_WIDTH - self.width, self.x))
    
    def move_left(self, audio_manager=None):
        """Instant left movement - no acceleration, no momentum"""
        self.velocity_x = -self.move_speed
        self.moving = True
        if audio_manager and random.randint(1, 15) == 1:
            audio_manager.play_movement_sound('move')
        
    def move_right(self, audio_manager=None):
        """Instant right movement - no acceleration, no momentum"""
        self.velocity_x = self.move_speed
        self.moving = True
        if audio_manager and random.randint(1, 15) == 1:
            audio_manager.play_movement_sound('move')
        
    def jump(self, audio_manager=None):
        """Instant jump - full power immediately"""
        if self.on_ground:
            self.velocity_y = self.jump_power
            self.on_ground = False
            self.is_jumping = True
            if audio_manager:
                audio_manager.play_movement_sound('jump')
    
    def release_jump(self):
        """Variable jump height - cut jump short when released"""
        if self.is_jumping and self.velocity_y < -5:
            # Cut upward velocity significantly for short hops
            self.velocity_y *= 0.4
        self.is_jumping = False
    
    def fire_weapon(self, audio_manager=None):
        """Fire the current weapon with current angle and power"""
        if self.power < 5:  # Minimum power required
            return None
            
        # Play weapon firing sound
        if audio_manager:
            audio_manager.play_weapon_fire_sound(self.current_weapon)
            
        # Calculate firing position (from dog's center)
        fire_x = self.x + self.width / 2
        fire_y = self.y + self.height / 2
        
        # Calculate velocity based on angle and power
        power_multiplier = self.power / 100.0 * 30  # Increased max velocity to 30 for longer range
        velocity_x = math.cos(math.radians(self.aim_angle)) * power_multiplier
        velocity_y = math.sin(math.radians(self.aim_angle)) * power_multiplier
        
        # Create projectile with power level for visual scaling
        projectile = Projectile(fire_x, fire_y, velocity_x, velocity_y, self.current_weapon, self.power)
        
        # Reset power
        self.power = 0
        self.charging_power = False
        
        return projectile
    
    def draw(self, screen, is_current_player=False):
        # More detailed retro dog sprite
        color = COLORS['player_coral']
        darker_color = (color[0] - 40, color[1] - 40, color[2] - 40)
        
        # Dog body (oval shape)
        body_rect = (self.x + 4, self.y + 12, 24, 16)
        pygame.draw.ellipse(screen, color, body_rect)
        
        # Dog head (circle)
        head_center = (int(self.x + 16), int(self.y + 8))
        pygame.draw.circle(screen, color, head_center, 10)
        
        # Dog ears (triangular)
        ear1_points = [(self.x + 8, self.y + 4), (self.x + 12, self.y - 2), (self.x + 14, self.y + 6)]
        ear2_points = [(self.x + 18, self.y + 6), (self.x + 20, self.y - 2), (self.x + 24, self.y + 4)]
        pygame.draw.polygon(screen, darker_color, ear1_points)
        pygame.draw.polygon(screen, darker_color, ear2_points)
        
        # Dog legs (small rectangles)
        leg_width = 4
        leg_height = 8
        pygame.draw.rect(screen, darker_color, (self.x + 6, self.y + 24, leg_width, leg_height))
        pygame.draw.rect(screen, darker_color, (self.x + 12, self.y + 24, leg_width, leg_height))
        pygame.draw.rect(screen, darker_color, (self.x + 18, self.y + 24, leg_width, leg_height))
        pygame.draw.rect(screen, darker_color, (self.x + 24, self.y + 24, leg_width, leg_height))
        
        # Dog tail (small arc - simplified as line)
        tail_start = (int(self.x + 28), int(self.y + 16))
        tail_end = (int(self.x + 34), int(self.y + 10))
        pygame.draw.line(screen, darker_color, tail_start, tail_end, 3)
        
        # Dog snout (small oval)
        snout_rect = (self.x + 12, self.y + 10, 8, 4)
        pygame.draw.ellipse(screen, darker_color, snout_rect)
        
        # Eyes (black dots)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x + 12), int(self.y + 6)), 2)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x + 20), int(self.y + 6)), 2)
        
        # Nose (tiny black dot)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x + 16), int(self.y + 12)), 1)
        
        # Player ID indicator (collar)
        collar_color = (255, 0, 0) if self.player_id == 0 else (0, 0, 255)
        pygame.draw.rect(screen, collar_color, (self.x + 8, self.y + 14, 16, 3))
        
        # Draw aiming line (only for current player)
        if is_current_player:
            center_x = self.x + self.width / 2
            center_y = self.y + self.height / 2
            
            # Aim line length based on power
            line_length = 30 + (self.power / 100.0) * 40
            end_x = center_x + math.cos(math.radians(self.aim_angle)) * line_length
            end_y = center_y + math.sin(math.radians(self.aim_angle)) * line_length
            
            # Color changes based on power
            if self.charging_power:
                line_color = (255, int(255 - self.power * 2.55), 0)  # Red to yellow
            else:
                line_color = (255, 255, 255)
                
            pygame.draw.line(screen, line_color, (center_x, center_y), (end_x, end_y), 3)
            
            # Draw crosshair at end
            pygame.draw.circle(screen, line_color, (int(end_x), int(end_y)), 3, 1)
        
        # Health bar
        health_width = 30
        health_height = 4
        health_x = self.x + 1
        health_y = self.y - 8
        
        # Background
        pygame.draw.rect(screen, (100, 100, 100), 
                        (health_x, health_y, health_width, health_height))
        # Health
        current_health_width = int((self.health / 100) * health_width)
        health_color = (0, 255, 0) if self.health > 30 else (255, 255, 0) if self.health > 10 else (255, 0, 0)
        pygame.draw.rect(screen, health_color, 
                        (health_x, health_y, current_health_width, health_height))

class TerrainMap:
    """Enhanced terrain system with pixel-based destructible terrain"""
    
    def __init__(self, width, height, height_map):
        self.width = width
        self.height = height
        
        # Handle both single ground level and height map
        if isinstance(height_map, list):
            self.height_map = height_map.copy()
            self.ground_level = sum(height_map) // len(height_map)  # Average height
        else:
            # Single ground level (backward compatibility)
            self.ground_level = height_map
            self.height_map = [height_map for _ in range(width)]
        
        # Pixel-based terrain representation - True means terrain exists
        self.terrain_pixels = [[False for _ in range(height)] for _ in range(width)]
        
        # Initialize solid ground based on height map
        for x in range(width):
            ground_height = self.height_map[x] if x < len(self.height_map) else self.ground_level
            for y in range(int(ground_height), height):
                self.terrain_pixels[x][y] = True
        
        # List of craters for merging detection
        self.craters = []
    
    def get_ground_height(self, x):
        """Get terrain height at x coordinate with interpolation"""
        x_int = max(0, min(self.width - 1, int(x)))
        
        # For more accurate collision, check a small area around the point
        search_radius = 3
        min_height = self.height_map[x_int]
        
        for dx in range(-search_radius, search_radius + 1):
            check_x = x_int + dx
            if 0 <= check_x < self.width:
                # Find the topmost solid pixel in this column
                for y in range(self.height):
                    if self.terrain_pixels[check_x][y]:
                        min_height = min(min_height, y)
                        break
        
        return min_height
    
    def get_accurate_ground_height(self, x, y_start=None):
        """Get precise ground height by scanning downward from a starting point"""
        x_int = max(0, min(self.width - 1, int(x)))
        
        if y_start is None:
            y_start = 0
        
        # Scan downward to find first solid pixel
        for y in range(int(y_start), self.height):
            if self.terrain_pixels[x_int][y]:
                return y
        
        return self.height  # If no solid ground found, return bottom
    
    def check_wall_collision(self, x, y, width, height):
        """Check if a rectangle collides with terrain walls (for crater sides)"""
        # Check left and right edges of the rectangle
        for check_y in range(int(y), int(y + height), 2):
            # Left edge
            if self.is_solid_at(x - 1, check_y):
                return 'left'
            # Right edge  
            if self.is_solid_at(x + width, check_y):
                return 'right'
        return None
    
    def is_solid_at(self, x, y):
        """Check if terrain exists at specific pixel"""
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        return self.terrain_pixels[int(x)][int(y)]
    
    def create_crater(self, center_x, center_y, radius):
        """Create circular crater at impact point"""
        center_x = int(center_x)
        center_y = int(center_y)
        
        # Store crater info for merging
        import time
        crater_info = {
            'x': center_x,
            'y': center_y,
            'radius': radius,
            'creation_time': time.time()
        }
        self.craters.append(crater_info)
        
        # Remove terrain pixels within explosion radius
        for x in range(max(0, center_x - radius), min(self.width, center_x + radius + 1)):
            for y in range(max(0, center_y - radius), min(self.height, center_y + radius + 1)):
                distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                if distance <= radius:
                    self.terrain_pixels[x][y] = False
        
        # Update height map after crater creation
        self._update_height_map()
    
    def _update_height_map(self):
        """Update height map based on current terrain pixels"""
        for x in range(self.width):
            # Find the topmost solid pixel in this column
            height = self.height
            for y in range(self.height):
                if self.terrain_pixels[x][y]:
                    height = y
                    break
            self.height_map[x] = height
    
    def merge_overlapping_craters(self):
        """Combine craters that overlap to create larger depressions"""
        if len(self.craters) < 2:
            return
        
        # Sort craters by creation order (newer ones have priority)
        self.craters.sort(key=lambda c: c.get('creation_time', 0))
        
        merged = []
        for current_crater in self.craters:
            merged_with_any = False
            
            # Check if this crater overlaps with any in merged list
            for j, merged_crater in enumerate(merged):
                distance = math.sqrt((current_crater['x'] - merged_crater['x'])**2 + 
                                   (current_crater['y'] - merged_crater['y'])**2)
                
                # If craters overlap (distance < sum of radii * overlap_factor)
                overlap_factor = 0.8  # Allow merging when 80% overlap
                if distance < (current_crater['radius'] + merged_crater['radius']) * overlap_factor:
                    # Merge craters - weighted average based on size
                    total_area = current_crater['radius']**2 + merged_crater['radius']**2
                    weight1 = current_crater['radius']**2 / total_area
                    weight2 = merged_crater['radius']**2 / total_area
                    
                    new_x = int(current_crater['x'] * weight1 + merged_crater['x'] * weight2)
                    new_y = int(current_crater['y'] * weight1 + merged_crater['y'] * weight2)
                    
                    # New radius encompasses both craters with some expansion
                    max_extent = max(
                        distance + current_crater['radius'],
                        distance + merged_crater['radius'],
                        current_crater['radius'] + merged_crater['radius'] * 0.5
                    )
                    new_radius = min(int(max_extent), max(current_crater['radius'], merged_crater['radius']) + 20)
                    
                    merged[j] = {
                        'x': new_x, 
                        'y': new_y, 
                        'radius': new_radius,
                        'creation_time': max(current_crater.get('creation_time', 0), 
                                           merged_crater.get('creation_time', 0))
                    }
                    merged_with_any = True
                    break
            
            if not merged_with_any:
                merged.append(current_crater)
        
        self.craters = merged
        
        # Limit total number of craters for performance
        if len(self.craters) > 50:
            self.craters = self.craters[-50:]

class TerrainGenerator:
    """Procedural terrain generation using sine waves for hills and valleys"""
    
    def __init__(self):
        self.base_ground_level = SCREEN_HEIGHT - 100
        
    def generate_height_map(self, width, complexity=1.0):
        """Creates varied terrain profile with sand dunes and varied slopes"""
        height_map = []
        
        # Multiple sine wave layers for natural-looking terrain
        # Primary wave - main hills and valleys (larger dunes)
        primary_frequency = 0.002 * complexity  # Slightly lower frequency for bigger dunes
        primary_amplitude = 80 * complexity     # Increased amplitude for more dramatic dunes
        
        # Secondary wave - medium dunes
        secondary_frequency = 0.006 * complexity
        secondary_amplitude = 35 * complexity
        
        # Tertiary wave - small dunes and ripples
        tertiary_frequency = 0.015 * complexity
        tertiary_amplitude = 15 * complexity
        
        # Sand ripple wave - fine surface details
        ripple_frequency = 0.05 * complexity
        ripple_amplitude = 5 * complexity
        
        # Dune asymmetry wave - creates realistic dune slopes (steep on one side)
        asymmetry_frequency = 0.004 * complexity
        
        for x in range(width):
            # Combine multiple sine waves for natural terrain
            primary_height = math.sin(x * primary_frequency) * primary_amplitude
            secondary_height = math.sin(x * secondary_frequency) * secondary_amplitude
            tertiary_height = math.sin(x * tertiary_frequency) * tertiary_amplitude
            ripple_height = math.sin(x * ripple_frequency) * ripple_amplitude
            
            # Add asymmetric dune shaping (creates steeper slopes on one side)
            asymmetry_factor = math.sin(x * asymmetry_frequency)
            if asymmetry_factor > 0:
                # Steeper slope on the windward side
                slope_modifier = asymmetry_factor * 20 * complexity
                primary_height += slope_modifier
                secondary_height += slope_modifier * 0.5
            
            # Add some randomness for more natural variation
            random_variation = (random.random() - 0.5) * 12 * complexity
            
            # Create occasional larger dune features
            if x % 200 == 0:  # Every 200 pixels, chance for a major dune
                if random.random() < 0.3:  # 30% chance
                    dune_center = x + random.randint(50, 150)
                    dune_width = random.randint(80, 120)
                    dune_height = random.randint(40, 70) * complexity
                    
                    # Add dune influence to nearby points
                    for dx in range(-dune_width//2, dune_width//2):
                        if 0 <= x + dx < width:
                            distance_factor = 1 - abs(dx) / (dune_width//2)
                            if distance_factor > 0:
                                # Store dune influence for later application
                                pass
            
            # Calculate final height
            total_height = (self.base_ground_level + 
                          primary_height + 
                          secondary_height + 
                          tertiary_height + 
                          ripple_height +
                          random_variation)
            
            # Ensure height stays within reasonable bounds
            min_height = SCREEN_HEIGHT - 220  # Increased range for bigger dunes
            max_height = SCREEN_HEIGHT - 40   # Allow terrain closer to water
            total_height = max(min_height, min(max_height, total_height))
            
            height_map.append(int(total_height))
        
        return height_map
    
    def smooth_terrain(self, height_map, iterations=3):
        """Applies smoothing to reduce sharp edges"""
        smoothed = height_map.copy()
        
        for _ in range(iterations):
            new_smoothed = smoothed.copy()
            
            # Apply smoothing filter (simple moving average)
            for i in range(1, len(smoothed) - 1):
                # Use weighted average with neighbors
                new_smoothed[i] = int((smoothed[i-1] * 0.25 + 
                                     smoothed[i] * 0.5 + 
                                     smoothed[i+1] * 0.25))
            
            smoothed = new_smoothed
        
        return smoothed
    
    def place_features(self, height_map, palm_trees):
        """Adds palm trees and other environmental features based on terrain"""
        updated_trees = []
        
        for tree in palm_trees:
            tree_x = tree['x']
            
            # Ensure tree x is within bounds
            if 0 <= tree_x < len(height_map):
                # Place tree at ground level for this x coordinate
                ground_height = height_map[tree_x]
                
                # Adjust tree height based on terrain slope for visual variety
                slope = 0
                if tree_x > 0 and tree_x < len(height_map) - 1:
                    slope = abs(height_map[tree_x + 1] - height_map[tree_x - 1])
                
                # Trees on slopes are slightly shorter
                height_modifier = max(0.8, 1.0 - slope * 0.002)
                adjusted_height = int(tree['height'] * height_modifier)
                
                updated_tree = tree.copy()
                updated_tree['height'] = adjusted_height
                updated_tree['ground_y'] = ground_height
                updated_trees.append(updated_tree)
        
        return updated_trees
    
    def add_sand_dunes(self, height_map, complexity=1.0):
        """Add distinctive sand dune features to the terrain"""
        enhanced_map = height_map.copy()
        width = len(height_map)
        
        # Add several major sand dunes across the map
        num_dunes = int(3 + complexity * 2)  # 3-5 major dunes
        
        for _ in range(num_dunes):
            # Random dune position and characteristics
            dune_center = random.randint(100, width - 100)
            dune_width = random.randint(80, 150)
            dune_height = random.randint(30, 60) * complexity
            
            # Create asymmetric dune shape (steeper on one side)
            steep_side = random.choice([-1, 1])  # -1 = left steep, 1 = right steep
            
            for x in range(max(0, dune_center - dune_width), 
                          min(width, dune_center + dune_width)):
                distance_from_center = abs(x - dune_center)
                
                if distance_from_center < dune_width:
                    # Calculate dune influence with asymmetric profile
                    if (x - dune_center) * steep_side > 0:
                        # Steep side - sharper falloff
                        influence = (1 - (distance_from_center / dune_width) ** 1.5)
                    else:
                        # Gentle side - gradual falloff
                        influence = (1 - (distance_from_center / dune_width) ** 0.7)
                    
                    if influence > 0:
                        dune_addition = influence * dune_height
                        enhanced_map[x] = int(enhanced_map[x] - dune_addition)  # Subtract to make hills
        
        return enhanced_map
    
    def generate_varied_terrain(self, width, complexity=1.0):
        """Generate complete terrain with sand dunes, hills, valleys, and features"""
        # Generate base height map with enhanced dune patterns
        height_map = self.generate_height_map(width, complexity)
        
        # Add distinctive sand dune features
        dune_enhanced_map = self.add_sand_dunes(height_map, complexity)
        
        # Apply light smoothing to prevent sharp edges while preserving dune character
        smoothed_height_map = self.smooth_terrain(dune_enhanced_map, iterations=1)
        
        return smoothed_height_map

class Terrain:
    def __init__(self, use_varied_terrain=True, terrain_complexity=1.0):
        self.base_ground_level = SCREEN_HEIGHT - 100
        self.terrain_complexity = terrain_complexity
        
        # Initialize terrain generator
        self.terrain_generator = TerrainGenerator()
        
        if use_varied_terrain:
            # Generate varied terrain with hills and valleys
            self.height_map = self.terrain_generator.generate_varied_terrain(
                SCREEN_WIDTH, terrain_complexity
            )
            # Use the average height as the base ground level
            self.ground_level = sum(self.height_map) // len(self.height_map)
        else:
            # Use flat terrain (original behavior)
            self.ground_level = self.base_ground_level
            self.height_map = [self.ground_level] * SCREEN_WIDTH
        
        # Initialize palm trees
        initial_trees = [
            {'x': 200, 'height': 80, 'destroyed': False},
            {'x': 500, 'height': 90, 'destroyed': False},
            {'x': 800, 'height': 75, 'destroyed': False},
            {'x': 1000, 'height': 85, 'destroyed': False}
        ]
        
        # Place trees based on terrain
        self.palm_trees = self.terrain_generator.place_features(self.height_map, initial_trees)
        
        # Initialize enhanced terrain system with varied terrain
        self.terrain_map = TerrainMap(SCREEN_WIDTH, SCREEN_HEIGHT, self.height_map)
    
    def get_ground_height(self, x):
        """Get terrain height using enhanced terrain system"""
        return self.terrain_map.get_ground_height(x)
    
    def destroy_tree_at(self, x, y, radius=50):
        """Destroy trees within explosion radius"""
        for tree in self.palm_trees:
            if tree['destroyed']:
                continue
            
            # Calculate distance from explosion center to tree
            distance = math.sqrt((tree['x'] - x)**2 + ((self.ground_level - tree['height']/2) - y)**2)
            
            if distance <= radius:
                tree['destroyed'] = True
                return True
        return False
    
    def draw(self, screen):
        # Draw crisp blue sky gradient
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            if ratio < 0.7:
                # Blend from upper sky to lower sky
                blend = ratio / 0.7
                color = (
                    int(COLORS['sky_upper'][0] * (1-blend) + COLORS['sky_lower'][0] * blend),
                    int(COLORS['sky_upper'][1] * (1-blend) + COLORS['sky_lower'][1] * blend),
                    int(COLORS['sky_upper'][2] * (1-blend) + COLORS['sky_lower'][2] * blend)
                )
            else:
                # Blend to horizon
                blend = (ratio - 0.7) / 0.3
                color = (
                    int(COLORS['sky_lower'][0] * (1-blend) + COLORS['horizon'][0] * blend),
                    int(COLORS['sky_lower'][1] * (1-blend) + COLORS['horizon'][1] * blend),
                    int(COLORS['sky_lower'][2] * (1-blend) + COLORS['horizon'][2] * blend)
                )
            
            pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))
        
        # Draw destructible terrain using pixel-based system
        self._draw_destructible_terrain(screen)
        
        # Draw terrain outline for better definition
        self._draw_terrain_outline(screen)
        
        # Draw water foam at the edge (reduced to avoid white line issues)
        foam_height = 15
        # Only draw foam where there's actually low terrain
        for x in range(0, SCREEN_WIDTH, 10):
            ground_height = self.get_ground_height(x)
            if ground_height > SCREEN_HEIGHT - 80:  # Only near water level
                pygame.draw.rect(screen, COLORS['water_foam'], 
                               (x, ground_height - foam_height, 10, foam_height))
        
        # Draw palm trees (only non-destroyed ones)
        for tree in self.palm_trees:
            if not tree['destroyed']:
                # Use proper ground height for tree positioning
                tree_ground_y = tree.get('ground_y', self.get_ground_height(tree['x']))
                self.draw_palm_tree(screen, tree['x'], tree['height'], tree_ground_y)
    
    def _draw_destructible_terrain(self, screen):
        """Draw terrain with enhanced sand dune shading and better contrast"""
        chunk_size = 4  # Draw 4x4 pixel chunks
        
        for x in range(0, SCREEN_WIDTH, chunk_size):
            # Start from much higher to catch mountains
            start_y = min(self.ground_level, min(self.height_map) if self.height_map else self.ground_level)
            for y in range(start_y - 50, SCREEN_HEIGHT, chunk_size):
                # Check if any pixel in this chunk has terrain
                has_terrain = False
                for dx in range(chunk_size):
                    for dy in range(chunk_size):
                        if (x + dx < SCREEN_WIDTH and y + dy < SCREEN_HEIGHT and
                            self.terrain_map.is_solid_at(x + dx, y + dy)):
                            has_terrain = True
                            break
                    if has_terrain:
                        break
                
                if has_terrain:
                    # Calculate sand color based on terrain slope and height for dune effect
                    sand_color = self._get_sand_color_for_position(x, y)
                    pygame.draw.rect(screen, sand_color, (x, y, chunk_size, chunk_size))
    
    def _get_sand_color_for_position(self, x, y):
        """Calculate sand color based on terrain slope and position for dune shading"""
        # Get terrain heights around this position for slope calculation
        if x < len(self.height_map) - 10 and x > 10:
            left_height = self.height_map[max(0, x - 8)]
            right_height = self.height_map[min(len(self.height_map) - 1, x + 8)]
            current_height = self.height_map[x] if x < len(self.height_map) else self.ground_level
            
            # Check if this is mountain terrain - fill entire mountain area with brown
            base_ground = SCREEN_HEIGHT - 100
            height_above_base = base_ground - current_height
            
            # If we're in a mountain area (high terrain), fill it completely with brown
            if height_above_base > 60:  # This is mountain terrain
                # All mountain terrain gets brown color
                if height_above_base > 100:
                    return COLORS['mountain_shadow']  # Very high = dark brown
                else:
                    return COLORS['mountain']  # High = brown
            
            # Calculate slope for sand shading
            slope = (right_height - left_height) / 16.0  # Slope over 16 pixels
            
            # Determine if this is a slope facing "sunlight" (left side = highlight, right side = shadow)
            if slope > 2:  # Steep upward slope (shadow side)
                return COLORS['sand_shadow']
            elif slope < -2:  # Steep downward slope (highlight side)
                return COLORS['sand_highlight']
            elif abs(slope) > 0.5:  # Moderate slope
                # Blend between normal and highlight/shadow
                if slope > 0:
                    # Slight shadow
                    blend_factor = min(slope / 2.0, 0.5)
                    return self._blend_colors(COLORS['sand'], COLORS['sand_shadow'], blend_factor)
                else:
                    # Slight highlight
                    blend_factor = min(abs(slope) / 2.0, 0.5)
                    return self._blend_colors(COLORS['sand'], COLORS['sand_highlight'], blend_factor)
            
            # Add subtle depth shading based on distance from surface
            surface_distance = y - current_height
            if surface_distance > 20:  # Deeper underground gets slightly darker
                depth_factor = min((surface_distance - 20) / 50.0, 0.3)
                return self._blend_colors(COLORS['sand'], COLORS['sand_shadow'], depth_factor)
        
        # Default sand color
        return COLORS['sand']
    
    def _blend_colors(self, color1, color2, factor):
        """Blend two colors with given factor (0.0 = color1, 1.0 = color2)"""
        factor = max(0.0, min(1.0, factor))
        return (
            int(color1[0] * (1 - factor) + color2[0] * factor),
            int(color1[1] * (1 - factor) + color2[1] * factor),
            int(color1[2] * (1 - factor) + color2[2] * factor)
        )
    
    def _draw_terrain_outline(self, screen):
        """Draw subtle outline on terrain surface for better definition"""
        outline_color = COLORS['sand_shadow']
        
        # Draw outline along the terrain surface
        for x in range(0, SCREEN_WIDTH - 1, 2):  # Every 2 pixels for performance
            ground_height = self.get_ground_height(x)
            
            # Draw a subtle 1-pixel outline on the terrain surface
            if ground_height < SCREEN_HEIGHT - 1:
                pygame.draw.circle(screen, outline_color, (x, int(ground_height)), 1)
    
    def draw_palm_tree(self, screen, x, height, ground_y=None):
        trunk_width = 12
        trunk_height = height
        
        # Use actual ground height at tree position
        if ground_y is None:
            ground_y = self.get_ground_height(x)
        
        # Trunk - positioned on actual terrain
        trunk_rect = (x - trunk_width//2, int(ground_y - trunk_height), trunk_width, trunk_height)
        pygame.draw.rect(screen, COLORS['palm_trunk'], trunk_rect)
        
        # Palm fronds (simple) - positioned at top of trunk
        frond_y = int(ground_y - trunk_height)
        for angle in range(0, 360, 45):
            end_x = x + math.cos(math.radians(angle)) * 30
            end_y = frond_y + math.sin(math.radians(angle)) * 15
            pygame.draw.line(screen, COLORS['palm_leaves'], (x, frond_y), (end_x, end_y), 4)

class GameManager:
    def __init__(self):
        self.state = "PLAYING"  # "PLAYING", "PROJECTILE_FLYING", "GAME_OVER"
        self.current_player = 0
        self.players = [
            Player(100, 400, 0),
            Player(1100, 400, 1)
        ]
        
        # Initialize game settings first
        self.game_settings = GameSettings()
        
        # Initialize terrain with settings
        terrain_complexity = self.game_settings.get_terrain_complexity()
        use_varied_terrain = self.game_settings.is_varied_terrain_enabled()
        self.terrain = Terrain(use_varied_terrain, terrain_complexity)
        
        self.projectiles = []
        self.turn_timer = 0
        
        # Initialize visual effects manager with settings
        self.effects_manager = EffectsManager(self.game_settings)
        
        # Initialize audio manager with settings
        self.audio_manager = AudioManager(self.game_settings)
        
    def handle_input(self, keys, events):
        if self.state != "PLAYING":
            return
            
        current_p = self.players[self.current_player]
        
        # Movement (only when not charging power)
        if not current_p.charging_power:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                current_p.move_left(self.audio_manager)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                current_p.move_right(self.audio_manager)
            if keys[pygame.K_SPACE]:
                current_p.jump(self.audio_manager)
            else:
                # Release jump for variable jump height
                current_p.release_jump()
        
        # Aiming
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            current_p.aim_angle -= 2
            current_p.aim_angle = max(-180, min(0, current_p.aim_angle))
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            current_p.aim_angle += 2
            current_p.aim_angle = max(-180, min(0, current_p.aim_angle))
        
        # Power charging
        if keys[pygame.K_RETURN]:
            if not current_p.charging_power:
                current_p.charging_power = True
                current_p.power = 0
            else:
                current_p.power = min(100, current_p.power + 10)  # Arcade-fast power charging (2x faster)
                # Add charging visual effect
                fire_x = current_p.x + current_p.width / 2
                fire_y = current_p.y + current_p.height / 2
                self.effects_manager.create_weapon_charge_effect(fire_x, fire_y, current_p.power)
                
                # Play power charging sound - continuous above 50% (Requirement 3.5)
                if current_p.power > 50:
                    # Continuous charging audio above 50% power
                    self.audio_manager.play_power_sound('charge')
                elif current_p.power % 25 == 0:  # Play sound at 25% thresholds below 50%
                    self.audio_manager.play_power_sound('charge')
        
        # Handle key releases and weapon switching
        for event in events:
            if event.type == pygame.KEYDOWN:
                # Weapon switching
                if event.key == pygame.K_1:
                    current_p.current_weapon = "rocket"
                elif event.key == pygame.K_2:
                    current_p.current_weapon = "banana"
                elif event.key == pygame.K_3:
                    current_p.current_weapon = "melee"
                # Settings shortcuts
                elif event.key == pygame.K_F1:
                    # Toggle audio
                    self.game_settings.set_audio_enabled(not self.game_settings.is_audio_enabled())
                    self.audio_manager.update_settings(self.game_settings)
                    self.game_settings.save_settings()
                elif event.key == pygame.K_F2:
                    # Cycle visual effects intensity
                    current_intensity = self.game_settings.get_particle_intensity()
                    new_intensity = 0.5 if current_intensity >= 2.0 else current_intensity + 0.5
                    self.game_settings.set_particle_intensity(new_intensity)
                    self.game_settings.save_settings()
                elif event.key == pygame.K_F3:
                    # Cycle terrain complexity
                    current_complexity = self.game_settings.get_terrain_complexity()
                    new_complexity = 0.5 if current_complexity >= 2.0 else current_complexity + 0.5
                    self.game_settings.set_terrain_complexity(new_complexity)
                    self.game_settings.save_settings()
                    
            elif event.type == pygame.KEYUP:
                # Fire weapon when Enter is released
                if event.key == pygame.K_RETURN and current_p.charging_power:
                    # Play power release sound
                    self.audio_manager.play_power_sound('release')
                    projectile = current_p.fire_weapon(self.audio_manager)
                    if projectile:
                        self.projectiles.append(projectile)
                        self.state = "PROJECTILE_FLYING"
    
    def update(self):
        # Update visual effects
        self.effects_manager.update_all_effects()
        
        # Update players
        for player in self.players:
            player.update(self.terrain, self.audio_manager)
        
        # Update projectiles
        if self.state == "PROJECTILE_FLYING":
            for projectile in self.projectiles[:]:  # Copy list to avoid modification during iteration
                if projectile.update(self.terrain, self.players, self.effects_manager, self.audio_manager):
                    self.projectiles.remove(projectile)
            
            # If no projectiles left, switch turns
            if not self.projectiles:
                self.next_turn()
        
        # Check for game over
        alive_players = [p for p in self.players if p.health > 0]
        if len(alive_players) <= 1:
            self.state = "GAME_OVER"
    
    def next_turn(self):
        """Switch to next player's turn"""
        self.current_player = (self.current_player + 1) % len(self.players)
        
        # Skip dead players
        attempts = 0
        while self.players[self.current_player].health <= 0 and attempts < len(self.players):
            self.current_player = (self.current_player + 1) % len(self.players)
            attempts += 1
            
        self.state = "PLAYING"
        self.turn_timer = 0
    
    def draw(self, screen):
        self.terrain.draw(screen)
        
        # Draw players
        for i, player in enumerate(self.players):
            if player.health > 0:
                is_current = (i == self.current_player and self.state == "PLAYING")
                player.draw(screen, is_current)
        
        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(screen)
        
        # Draw visual effects (drawn last so they appear on top)
        self.effects_manager.draw_all_effects(screen)
            
        # Draw UI
        font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 24)
        
        if self.state == "GAME_OVER":
            # Game over screen
            alive_players = [i for i, p in enumerate(self.players) if p.health > 0]
            if alive_players:
                winner_text = font.render(f"Player {alive_players[0] + 1} Wins!", 
                                        True, COLORS['text_slate'])
                screen.blit(winner_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2))
            else:
                draw_text = font.render("Draw!", True, COLORS['text_slate'])
                screen.blit(draw_text, (SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT//2))
        else:
            # Normal game UI
            current_p = self.players[self.current_player]
            
            player_text = font.render(f"Player {self.current_player + 1}'s Turn", 
                                     True, COLORS['text_slate'])
            screen.blit(player_text, (10, 10))
            
            # Weapon info
            weapon_text = small_font.render(f"Weapon: {current_p.current_weapon.title()}", 
                                          True, COLORS['text_slate'])
            screen.blit(weapon_text, (10, 50))
            
            # Angle info
            angle_text = small_font.render(f"Angle: {int(current_p.aim_angle)}°", 
                                         True, COLORS['text_slate'])
            screen.blit(angle_text, (10, 75))
            
            # Power meter
            if current_p.charging_power:
                power_text = small_font.render(f"Power: {int(current_p.power)}%", 
                                             True, COLORS['text_slate'])
                screen.blit(power_text, (10, 100))
                
                # Power bar
                bar_width = 200
                bar_height = 10
                bar_x = 10
                bar_y = 125
                
                pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
                power_width = int((current_p.power / 100.0) * bar_width)
                power_color = (255, int(255 - current_p.power * 2.55), 0)
                pygame.draw.rect(screen, power_color, (bar_x, bar_y, power_width, bar_height))
        
        # Controls help
        controls = [
            "WASD: Move/Aim  Space: Jump",
            "Enter: Charge/Fire  1/2/3: Weapons", 
            "F1: Audio  F2: Effects  F3: Terrain"
        ]
        
        for i, control in enumerate(controls):
            control_text = small_font.render(control, True, COLORS['text_slate'])
            screen.blit(control_text, (SCREEN_WIDTH - 300, 10 + i * 25))
        
        # Settings display
        settings_info = [
            f"Audio: {'ON' if self.game_settings.is_audio_enabled() else 'OFF'}",
            f"Effects: {self.game_settings.get_particle_intensity():.1f}x",
            f"Terrain: {self.game_settings.get_terrain_complexity():.1f}x"
        ]
        
        for i, setting in enumerate(settings_info):
            setting_text = small_font.render(setting, True, COLORS['text_slate'])
            screen.blit(setting_text, (SCREEN_WIDTH - 150, 100 + i * 20))

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Project Artillery - Sunrise Beach")
    clock = pygame.time.Clock()
    
    game = GameManager()
    
    running = True
    while running:
        # Handle input
        keys = pygame.key.get_pressed()
        events = pygame.event.get()
        
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        game.handle_input(keys, events)
        
        # Update game
        game.update()
        
        # Draw everything
        screen.fill(COLORS['sky_upper'])
        game.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
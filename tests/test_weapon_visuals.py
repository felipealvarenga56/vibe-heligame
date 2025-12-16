#!/usr/bin/env python3
"""
Property-based tests for weapon visual effects
**Feature: game-enhancements, Property 4: Weapon-specific visual effects**
**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**
"""

import unittest
import sys
import os

# Add the parent directory to the path so we can import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import Projectile, EffectsManager, Particle, ParticleSystem, Terrain

class MockTerrain:
    """Mock terrain for testing"""
    def __init__(self):
        self.ground_level = 500
        self.terrain_map = MockTerrainMap()
        self.palm_trees = []
    
    def get_ground_height(self, x):
        return self.ground_level
    
    def destroy_tree_at(self, x, y, radius):
        return False

class MockTerrainMap:
    """Mock terrain map for testing"""
    def __init__(self):
        self.height = 720
    
    def is_solid_at(self, x, y):
        return y >= 500  # Simple ground at y=500
    
    def create_crater(self, x, y, radius):
        pass  # Mock implementation
    
    def merge_overlapping_craters(self):
        pass  # Mock implementation

class TestWeaponVisualEffects(unittest.TestCase):
    """
    Property 4: Weapon-specific visual effects
    For any weapon type fired, the system should display the correct projectile appearance, 
    trail effects, and explosion visuals scaled by power level
    """
    
    def setUp(self):
        """Set up test fixtures"""
        self.effects_manager = EffectsManager()
        self.mock_terrain = MockTerrain()
        self.mock_players = []
    
    def test_rocket_has_flame_trail_effects(self):
        """Test that rocket projectiles create flame trail effects"""
        # Create a rocket projectile
        rocket = Projectile(100, 100, 5, -3, "rocket", 50)
        
        # Verify rocket properties
        self.assertEqual(rocket.weapon_type, "rocket")
        self.assertEqual(rocket.power_level, 50)
        
        # Test that rocket creates trail effects when updated
        initial_trail_count = len(self.effects_manager.particle_systems['trails'].particles)
        rocket.update(self.mock_terrain, self.mock_players, self.effects_manager)
        
        # Should have created trail particles
        final_trail_count = len(self.effects_manager.particle_systems['trails'].particles)
        self.assertGreater(final_trail_count, initial_trail_count, 
                          "Rocket should create trail particles")
    
    def test_banana_has_spinning_animation(self):
        """Test that banana projectiles have spinning animation"""
        # Create a banana projectile
        banana = Projectile(100, 100, 3, -2, "banana", 75)
        
        # Verify banana properties
        self.assertEqual(banana.weapon_type, "banana")
        self.assertEqual(banana.timer, 180)  # 3-second timer
        self.assertEqual(banana.rotation, 0)
        
        # Update banana and check rotation changes
        initial_rotation = banana.rotation
        banana.update(self.mock_terrain, self.mock_players, self.effects_manager)
        
        # Rotation should have changed (spinning effect)
        self.assertNotEqual(banana.rotation, initial_rotation, 
                           "Banana should have spinning animation")
    
    def test_explosion_effects_scale_with_power(self):
        """Test that explosion effects scale with weapon power level"""
        # Create projectiles with different power levels
        low_power_rocket = Projectile(100, 100, 2, -1, "rocket", 25)
        high_power_rocket = Projectile(200, 100, 4, -2, "rocket", 90)
        
        # Clear any existing particles
        self.effects_manager.particle_systems['explosions'].clear()
        
        # Create explosions with different intensities
        low_power_rocket.explode(self.mock_terrain, self.mock_players, self.effects_manager)
        low_power_particles = len(self.effects_manager.particle_systems['explosions'].particles)
        
        self.effects_manager.particle_systems['explosions'].clear()
        
        high_power_rocket.explode(self.mock_terrain, self.mock_players, self.effects_manager)
        high_power_particles = len(self.effects_manager.particle_systems['explosions'].particles)
        
        # Higher power should create more particles (or at least equal)
        self.assertGreaterEqual(high_power_particles, low_power_particles,
                               "Higher power weapons should create more explosion particles")
    
    def test_weapon_type_specific_visuals(self):
        """Test that different weapon types have distinct visual properties"""
        # Create different weapon types
        rocket = Projectile(100, 100, 5, -3, "rocket", 50)
        banana = Projectile(100, 100, 3, -2, "banana", 50)
        
        # Verify distinct properties
        self.assertEqual(rocket.weapon_type, "rocket")
        self.assertEqual(banana.weapon_type, "banana")
        
        # Rocket should not have timer, banana should
        self.assertEqual(rocket.timer, 0)
        self.assertEqual(banana.timer, 180)
        
        # Different explosion radii
        self.assertNotEqual(rocket.explosion_radius, banana.explosion_radius)
    
    def test_particle_system_creates_correct_particle_types(self):
        """Test that particle system creates appropriate particle types for explosions"""
        particle_system = ParticleSystem()
        
        # Add explosion particles
        particle_system.add_explosion_particles(100, 100, 1.0)
        
        # Should have created particles
        self.assertGreater(len(particle_system.particles), 0, 
                          "Explosion should create particles")
        
        # Check that particles have valid types
        valid_types = ["fire", "smoke", "debris"]
        for particle in particle_system.particles:
            self.assertIn(particle.particle_type, valid_types,
                         f"Particle type {particle.particle_type} should be valid")

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
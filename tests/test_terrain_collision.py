#!/usr/bin/env python3
"""
Property-based tests for modified terrain collision accuracy
**Feature: game-enhancements, Property 3: Modified terrain collision accuracy**
**Validates: Requirements 1.3, 1.5**
"""

import unittest
import sys
import os
import math
import random

# Add the parent directory to the path so we can import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from hypothesis import given, strategies as st, settings
    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False
    print("Warning: Hypothesis not available. Install with: pip install hypothesis")

from main import TerrainMap, Player, Projectile, SCREEN_WIDTH, SCREEN_HEIGHT

class TestModifiedTerrainCollision(unittest.TestCase):
    """
    Property 3: Modified terrain collision accuracy
    For any terrain that has been modified by explosions, collision detection 
    and ground height calculations should remain accurate
    """
    
    def setUp(self):
        """Set up test fixtures"""
        self.ground_level = 500
        self.terrain_map = TerrainMap(SCREEN_WIDTH, SCREEN_HEIGHT, self.ground_level)
    
    def test_ground_height_accuracy_after_crater_creation(self):
        """Test that ground height calculations remain accurate after crater creation"""
        # Create a crater at a known location (at ground level to ensure it affects terrain)
        crater_x = 400
        crater_y = self.ground_level + 10  # Slightly below ground level
        crater_radius = 50
        
        # Get original ground height
        original_height = self.terrain_map.get_ground_height(crater_x)
        
        # Create crater
        self.terrain_map.create_crater(crater_x, crater_y, crater_radius)
        
        # Ground height at crater center should be deeper than original
        new_height = self.terrain_map.get_ground_height(crater_x)
        self.assertGreater(new_height, original_height, 
                          "Ground height should be deeper after crater creation")
        
        # Ground height outside crater should remain unchanged
        far_x = crater_x + crater_radius + 100
        far_height = self.terrain_map.get_ground_height(far_x)
        self.assertEqual(far_height, self.ground_level,
                        "Ground height outside crater should remain unchanged")
    
    def test_collision_detection_accuracy_after_modification(self):
        """Test that collision detection works correctly on modified terrain"""
        # Create a crater at ground level
        crater_x = 300
        crater_y = self.ground_level + 10  # Slightly below ground level
        crater_radius = 40
        
        self.terrain_map.create_crater(crater_x, crater_y, crater_radius)
        
        # Test collision detection inside crater (should be empty)
        inside_crater_x = crater_x
        inside_crater_y = crater_y
        self.assertFalse(self.terrain_map.is_solid_at(inside_crater_x, inside_crater_y),
                        "Inside crater should not be solid")
        
        # Test collision detection outside crater (should be solid if below ground level)
        outside_x = crater_x + crater_radius + 20
        outside_y = self.ground_level + 10
        self.assertTrue(self.terrain_map.is_solid_at(outside_x, outside_y),
                      "Outside crater below ground level should be solid")
    
    def test_player_collision_on_modified_terrain(self):
        """Test that player collision works correctly on terrain with craters"""
        # Create a player
        player = Player(350, 400, 0)
        
        # Create terrain with crater at ground level
        crater_x = 400
        crater_y = self.ground_level + 10  # Slightly below ground level
        crater_radius = 50
        self.terrain_map.create_crater(crater_x, crater_y, crater_radius)
        
        # Mock terrain object for player update
        class MockTerrain:
            def __init__(self, terrain_map, ground_level):
                self.terrain_map = terrain_map
                self.ground_level = ground_level
                self.palm_trees = []
        
        mock_terrain = MockTerrain(self.terrain_map, self.ground_level)
        
        # Position player above crater and let them fall
        player.x = crater_x - player.width // 2
        player.y = crater_y - 100
        player.velocity_y = 5  # Falling downward
        
        # Update player position multiple times to let them fall
        for _ in range(20):  # Multiple updates to let player fall
            player.update(mock_terrain)
            if player.on_ground:
                break
        
        # Player should fall into crater, not stop at original ground level
        expected_ground = self.terrain_map.get_ground_height(player.x + player.width // 2)
        
        # Check that player landed on or near the modified terrain surface
        # Allow some tolerance for physics simulation
        self.assertGreaterEqual(player.y + player.height, expected_ground - 10,
                               f"Player should land on modified terrain surface. Player bottom: {player.y + player.height}, Expected ground: {expected_ground}")
        
        # Also verify that the player is actually in the crater (deeper than original ground)
        self.assertGreater(player.y + player.height, self.ground_level,
                          "Player should be deeper than original ground level when in crater")
    
    @unittest.skipUnless(HYPOTHESIS_AVAILABLE, "Hypothesis not available")
    @given(
        crater_x=st.integers(min_value=50, max_value=SCREEN_WIDTH-50),
        crater_y=st.integers(min_value=500, max_value=600),  # At or below ground level
        crater_radius=st.integers(min_value=20, max_value=80),
        test_x=st.integers(min_value=0, max_value=SCREEN_WIDTH-1)
    )
    @settings(max_examples=50, deadline=None)
    def test_property_ground_height_consistency(self, crater_x, crater_y, crater_radius, test_x):
        """
        Property test: Ground height calculations should be consistent and accurate
        for any crater configuration and test position
        """
        # Create fresh terrain for each test
        terrain_map = TerrainMap(SCREEN_WIDTH, SCREEN_HEIGHT, self.ground_level)
        
        # Create crater
        terrain_map.create_crater(crater_x, crater_y, crater_radius)
        
        # Get ground height at test position
        ground_height = terrain_map.get_ground_height(test_x)
        
        # Ground height should be valid (within screen bounds)
        self.assertGreaterEqual(ground_height, 0, "Ground height should be non-negative")
        self.assertLessEqual(ground_height, SCREEN_HEIGHT, "Ground height should be within screen")
        
        # Ground height should be consistent with pixel-level collision detection
        # Check if there's solid terrain at the reported ground height
        if ground_height < SCREEN_HEIGHT:
            # There should be solid terrain at or just below the reported height
            found_solid = False
            for check_y in range(int(ground_height), min(SCREEN_HEIGHT, int(ground_height) + 10)):
                if terrain_map.is_solid_at(test_x, check_y):
                    found_solid = True
                    break
            
            # If we're not in a deep crater, we should find solid terrain
            distance_to_crater = math.sqrt((test_x - crater_x)**2 + (ground_height - crater_y)**2)
            if distance_to_crater > crater_radius:
                self.assertTrue(found_solid, 
                               f"Should find solid terrain near reported ground height at x={test_x}")
    
    @unittest.skipUnless(HYPOTHESIS_AVAILABLE, "Hypothesis not available")
    @given(
        crater_x=st.integers(min_value=50, max_value=SCREEN_WIDTH-50),
        crater_y=st.integers(min_value=500, max_value=600),  # At or below ground level
        crater_radius=st.integers(min_value=20, max_value=80),
        projectile_x=st.integers(min_value=0, max_value=SCREEN_WIDTH-1),
        projectile_y=st.integers(min_value=0, max_value=SCREEN_HEIGHT-1)
    )
    @settings(max_examples=50, deadline=None)
    def test_property_projectile_collision_accuracy(self, crater_x, crater_y, crater_radius, 
                                                   projectile_x, projectile_y):
        """
        Property test: Projectile collision detection should be accurate on modified terrain
        """
        # Create fresh terrain for each test
        terrain_map = TerrainMap(SCREEN_WIDTH, SCREEN_HEIGHT, self.ground_level)
        
        # Create crater
        terrain_map.create_crater(crater_x, crater_y, crater_radius)
        
        # Test collision detection at projectile position
        is_solid = terrain_map.is_solid_at(projectile_x, projectile_y)
        ground_height = terrain_map.get_ground_height(projectile_x)
        
        # If projectile is above ground height, it should not be in solid terrain
        if projectile_y < ground_height:
            self.assertFalse(is_solid, 
                           f"Position above ground height should not be solid at ({projectile_x}, {projectile_y})")
        
        # If projectile is well below original ground level and outside crater, should be solid
        distance_to_crater = math.sqrt((projectile_x - crater_x)**2 + (projectile_y - crater_y)**2)
        if (projectile_y > self.ground_level + 20 and distance_to_crater > crater_radius + 10):
            self.assertTrue(is_solid,
                          f"Position well below ground and outside crater should be solid at ({projectile_x}, {projectile_y})")
    
    def test_multiple_craters_collision_accuracy(self):
        """Test collision accuracy with multiple overlapping craters"""
        # Create multiple craters at ground level
        craters = [
            (300, self.ground_level + 10, 40),
            (350, self.ground_level + 5, 35),
            (320, self.ground_level + 15, 30)
        ]
        
        for crater_x, crater_y, crater_radius in craters:
            self.terrain_map.create_crater(crater_x, crater_y, crater_radius)
        
        # Merge overlapping craters
        self.terrain_map.merge_overlapping_craters()
        
        # Test collision detection in the merged crater area
        center_x = 325  # Roughly center of overlapping craters
        center_y = 480
        
        # Should not be solid in the merged crater area
        self.assertFalse(self.terrain_map.is_solid_at(center_x, center_y),
                        "Merged crater area should not be solid")
        
        # Ground height should reflect the deepest crater
        ground_height = self.terrain_map.get_ground_height(center_x)
        self.assertGreater(ground_height, self.ground_level,
                          "Ground height in merged crater should be deeper than original")
    
    def test_edge_case_collision_detection(self):
        """Test collision detection edge cases on modified terrain"""
        # Create crater at edge of screen at ground level
        edge_crater_x = 50
        edge_crater_y = self.ground_level + 10
        edge_crater_radius = 60
        
        self.terrain_map.create_crater(edge_crater_x, edge_crater_y, edge_crater_radius)
        
        # Test collision at screen boundaries
        self.assertFalse(self.terrain_map.is_solid_at(-1, 500),
                        "Out of bounds positions should return False")
        self.assertFalse(self.terrain_map.is_solid_at(SCREEN_WIDTH, 500),
                        "Out of bounds positions should return False")
        
        # Test collision just inside crater
        inside_x = edge_crater_x + 10
        inside_y = edge_crater_y
        self.assertFalse(self.terrain_map.is_solid_at(inside_x, inside_y),
                        "Position inside crater should not be solid")

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
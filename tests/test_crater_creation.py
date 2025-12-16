#!/usr/bin/env python3
"""
Property-based tests for crater creation and terrain destruction
**Feature: game-enhancements, Property 1: Crater creation and terrain destruction**
**Validates: Requirements 1.1, 1.2**
"""

import unittest
import sys
import os
import math

# Add the parent directory to the path so we can import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from hypothesis import given, strategies as st, settings
    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False
    print("Warning: Hypothesis not available. Install with: pip install hypothesis")

from main import TerrainMap, SCREEN_WIDTH, SCREEN_HEIGHT

class TestCraterCreation(unittest.TestCase):
    """
    Property 1: Crater creation and terrain destruction
    For any explosion at coordinates (x, y) with radius r, terrain within the explosion 
    radius should be destroyed, creating a circular crater
    """
    
    def setUp(self):
        """Set up test fixtures"""
        self.ground_level = 500
        self.terrain_map = TerrainMap(SCREEN_WIDTH, SCREEN_HEIGHT, self.ground_level)
    
    def test_crater_creates_circular_destruction(self):
        """Test that crater creation destroys terrain in a circular pattern"""
        crater_x = 400
        crater_y = 520  # Below ground level
        crater_radius = 50
        
        # Verify terrain exists before crater creation
        self.assertTrue(self.terrain_map.is_solid_at(crater_x, crater_y),
                       "Terrain should exist before crater creation")
        
        # Create crater
        self.terrain_map.create_crater(crater_x, crater_y, crater_radius)
        
        # Check that terrain is destroyed within radius
        self.assertFalse(self.terrain_map.is_solid_at(crater_x, crater_y),
                        "Terrain at crater center should be destroyed")
        
        # Check points within radius are destroyed
        test_points = [
            (crater_x + 20, crater_y),      # Right of center
            (crater_x - 20, crater_y),      # Left of center
            (crater_x, crater_y + 20),      # Below center
            (crater_x, crater_y - 20)       # Above center
        ]
        
        for test_x, test_y in test_points:
            distance = math.sqrt((test_x - crater_x)**2 + (test_y - crater_y)**2)
            if distance <= crater_radius:
                self.assertFalse(self.terrain_map.is_solid_at(test_x, test_y),
                               f"Point at distance {distance} should be destroyed")
    
    def test_crater_preserves_terrain_outside_radius(self):
        """Test that crater creation preserves terrain outside explosion radius"""
        crater_x = 400
        crater_y = 520  # Below ground level
        crater_radius = 40
        
        # Create crater
        self.terrain_map.create_crater(crater_x, crater_y, crater_radius)
        
        # Check that terrain outside radius is preserved
        test_points = [
            (crater_x + crater_radius + 20, crater_y),      # Far right
            (crater_x - crater_radius - 20, crater_y),      # Far left
            (crater_x, crater_y + crater_radius + 20),      # Far below
        ]
        
        for test_x, test_y in test_points:
            if (0 <= test_x < SCREEN_WIDTH and 0 <= test_y < SCREEN_HEIGHT and 
                test_y >= self.ground_level):
                distance = math.sqrt((test_x - crater_x)**2 + (test_y - crater_y)**2)
                if distance > crater_radius + 5:  # Add small buffer for edge cases
                    self.assertTrue(self.terrain_map.is_solid_at(test_x, test_y),
                                   f"Point at distance {distance} should be preserved")
    
    def test_crater_updates_height_map(self):
        """Test that crater creation properly updates the height map"""
        crater_x = 300
        crater_y = 510  # Below ground level
        crater_radius = 60
        
        # Get original height
        original_height = self.terrain_map.get_ground_height(crater_x)
        
        # Create crater
        self.terrain_map.create_crater(crater_x, crater_y, crater_radius)
        
        # Height should be updated (deeper)
        new_height = self.terrain_map.get_ground_height(crater_x)
        self.assertGreater(new_height, original_height,
                          "Ground height should be deeper after crater creation")
    
    @unittest.skipUnless(HYPOTHESIS_AVAILABLE, "Hypothesis not available")
    @given(
        crater_x=st.integers(min_value=50, max_value=SCREEN_WIDTH-50),
        crater_y=st.integers(min_value=500, max_value=600),  # At or below ground level
        crater_radius=st.integers(min_value=10, max_value=100)
    )
    @settings(max_examples=30, deadline=None)
    def test_property_crater_circular_destruction(self, crater_x, crater_y, crater_radius):
        """
        Property test: Crater destruction should always be circular
        For any valid crater parameters, destruction should follow circular pattern
        """
        # Create fresh terrain for each test
        terrain_map = TerrainMap(SCREEN_WIDTH, SCREEN_HEIGHT, self.ground_level)
        
        # Create crater
        terrain_map.create_crater(crater_x, crater_y, crater_radius)
        
        # Test multiple points around the crater
        test_angles = [0, 45, 90, 135, 180, 225, 270, 315]  # 8 directions
        
        for angle in test_angles:
            # Test point just inside radius
            inside_distance = crater_radius * 0.8
            inside_x = crater_x + math.cos(math.radians(angle)) * inside_distance
            inside_y = crater_y + math.sin(math.radians(angle)) * inside_distance
            
            if (0 <= inside_x < SCREEN_WIDTH and 0 <= inside_y < SCREEN_HEIGHT):
                self.assertFalse(terrain_map.is_solid_at(int(inside_x), int(inside_y)),
                               f"Point inside crater radius should be destroyed at angle {angle}")
            
            # Test point just outside radius
            outside_distance = crater_radius * 1.2
            outside_x = crater_x + math.cos(math.radians(angle)) * outside_distance
            outside_y = crater_y + math.sin(math.radians(angle)) * outside_distance
            
            if (0 <= outside_x < SCREEN_WIDTH and 0 <= outside_y < SCREEN_HEIGHT and
                outside_y >= self.ground_level):
                self.assertTrue(terrain_map.is_solid_at(int(outside_x), int(outside_y)),
                              f"Point outside crater radius should be preserved at angle {angle}")
    
    @unittest.skipUnless(HYPOTHESIS_AVAILABLE, "Hypothesis not available")
    @given(
        crater_x=st.integers(min_value=50, max_value=SCREEN_WIDTH-50),
        crater_y=st.integers(min_value=500, max_value=600),
        crater_radius=st.integers(min_value=20, max_value=80)
    )
    @settings(max_examples=30, deadline=None)
    def test_property_crater_storage_and_tracking(self, crater_x, crater_y, crater_radius):
        """
        Property test: Craters should be properly stored and tracked
        """
        # Create fresh terrain for each test
        terrain_map = TerrainMap(SCREEN_WIDTH, SCREEN_HEIGHT, self.ground_level)
        
        initial_crater_count = len(terrain_map.craters)
        
        # Create crater
        terrain_map.create_crater(crater_x, crater_y, crater_radius)
        
        # Should have one more crater
        self.assertEqual(len(terrain_map.craters), initial_crater_count + 1,
                        "Crater should be added to tracking list")
        
        # Crater should have correct properties
        latest_crater = terrain_map.craters[-1]
        self.assertEqual(latest_crater['x'], crater_x)
        self.assertEqual(latest_crater['y'], crater_y)
        self.assertEqual(latest_crater['radius'], crater_radius)
        self.assertIn('creation_time', latest_crater)
    
    def test_multiple_craters_independent_destruction(self):
        """Test that multiple craters create independent destruction patterns"""
        # Create two separate craters
        crater1_x, crater1_y, crater1_radius = 200, 520, 30
        crater2_x, crater2_y, crater2_radius = 400, 530, 40
        
        # Ensure craters don't overlap
        distance = math.sqrt((crater2_x - crater1_x)**2 + (crater2_y - crater1_y)**2)
        self.assertGreater(distance, crater1_radius + crater2_radius,
                          "Test craters should not overlap")
        
        # Create first crater
        self.terrain_map.create_crater(crater1_x, crater1_y, crater1_radius)
        
        # Verify first crater destruction
        self.assertFalse(self.terrain_map.is_solid_at(crater1_x, crater1_y),
                        "First crater center should be destroyed")
        
        # Verify second crater area is still intact
        self.assertTrue(self.terrain_map.is_solid_at(crater2_x, crater2_y),
                      "Second crater area should still be intact")
        
        # Create second crater
        self.terrain_map.create_crater(crater2_x, crater2_y, crater2_radius)
        
        # Verify both craters exist
        self.assertFalse(self.terrain_map.is_solid_at(crater1_x, crater1_y),
                        "First crater should still be destroyed")
        self.assertFalse(self.terrain_map.is_solid_at(crater2_x, crater2_y),
                        "Second crater center should be destroyed")
    
    def test_crater_edge_cases(self):
        """Test crater creation edge cases"""
        # Crater at screen edge
        edge_crater_x = 10
        edge_crater_y = 520
        edge_crater_radius = 30
        
        # Should not crash
        self.terrain_map.create_crater(edge_crater_x, edge_crater_y, edge_crater_radius)
        
        # Crater with very small radius
        small_crater_x = 500
        small_crater_y = 510
        small_crater_radius = 1
        
        self.terrain_map.create_crater(small_crater_x, small_crater_y, small_crater_radius)
        
        # Should have destroyed at least the center point
        self.assertFalse(self.terrain_map.is_solid_at(small_crater_x, small_crater_y),
                        "Small crater should destroy center point")
        
        # Crater with large radius
        large_crater_x = 600
        large_crater_y = 550
        large_crater_radius = 150
        
        self.terrain_map.create_crater(large_crater_x, large_crater_y, large_crater_radius)
        
        # Should have destroyed center
        self.assertFalse(self.terrain_map.is_solid_at(large_crater_x, large_crater_y),
                        "Large crater should destroy center point")

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
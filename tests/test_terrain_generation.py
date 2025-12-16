#!/usr/bin/env python3
"""
Property-based tests for terrain generation quality
**Feature: game-enhancements, Property 6: Terrain generation quality**
**Validates: Requirements 4.1, 4.2, 4.5**
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

from main import TerrainGenerator, Terrain, SCREEN_WIDTH, SCREEN_HEIGHT

class TestTerrainGeneration(unittest.TestCase):
    """
    Property 6: Terrain generation quality
    Generated terrain should create varied, natural-looking landscapes with hills and valleys
    while maintaining playability and accessibility
    """
    
    def setUp(self):
        """Set up test fixtures"""
        self.terrain_generator = TerrainGenerator()
        self.base_ground_level = SCREEN_HEIGHT - 100
    
    def test_terrain_height_map_generation(self):
        """Test that terrain height map is generated with appropriate variation"""
        complexity = 1.0
        height_map = self.terrain_generator.generate_height_map(SCREEN_WIDTH, complexity)
        
        # Should generate height for every x coordinate
        self.assertEqual(len(height_map), SCREEN_WIDTH,
                        "Height map should have entry for every x coordinate")
        
        # Heights should be within reasonable bounds
        min_expected = SCREEN_HEIGHT - 200  # Maximum hill height
        max_expected = SCREEN_HEIGHT - 50   # Minimum valley depth
        
        for i, height in enumerate(height_map):
            self.assertGreaterEqual(height, min_expected,
                                   f"Height at x={i} should be above minimum bound")
            self.assertLessEqual(height, max_expected,
                                f"Height at x={i} should be below maximum bound")
    
    def test_terrain_has_variation(self):
        """Test that generated terrain has meaningful height variation"""
        complexity = 1.0
        height_map = self.terrain_generator.generate_height_map(SCREEN_WIDTH, complexity)
        
        # Calculate variation statistics
        min_height = min(height_map)
        max_height = max(height_map)
        height_range = max_height - min_height
        
        # Should have meaningful variation (at least 50 pixels difference)
        self.assertGreater(height_range, 50,
                          "Terrain should have meaningful height variation")
        
        # Calculate average deviation from mean
        mean_height = sum(height_map) / len(height_map)
        deviations = [abs(h - mean_height) for h in height_map]
        avg_deviation = sum(deviations) / len(deviations)
        
        # Should have reasonable average deviation
        self.assertGreater(avg_deviation, 10,
                          "Terrain should have reasonable height variation")
    
    def test_terrain_smoothing_reduces_sharp_edges(self):
        """Test that terrain smoothing reduces sharp height changes"""
        # Generate unsmoothed terrain
        complexity = 1.0
        raw_height_map = self.terrain_generator.generate_height_map(SCREEN_WIDTH, complexity)
        
        # Apply smoothing
        smoothed_height_map = self.terrain_generator.smooth_terrain(raw_height_map, iterations=3)
        
        # Calculate sharpness (sum of absolute differences between adjacent points)
        def calculate_sharpness(height_map):
            sharpness = 0
            for i in range(1, len(height_map)):
                sharpness += abs(height_map[i] - height_map[i-1])
            return sharpness
        
        raw_sharpness = calculate_sharpness(raw_height_map)
        smoothed_sharpness = calculate_sharpness(smoothed_height_map)
        
        # Smoothed terrain should be less sharp
        self.assertLess(smoothed_sharpness, raw_sharpness,
                       "Smoothed terrain should have less sharp edges")
    
    def test_terrain_complexity_scaling(self):
        """Test that terrain complexity parameter affects generation"""
        low_complexity = 0.5
        high_complexity = 2.0
        
        low_height_map = self.terrain_generator.generate_height_map(SCREEN_WIDTH, low_complexity)
        high_height_map = self.terrain_generator.generate_height_map(SCREEN_WIDTH, high_complexity)
        
        # Calculate variation for both
        def calculate_variation(height_map):
            return max(height_map) - min(height_map)
        
        low_variation = calculate_variation(low_height_map)
        high_variation = calculate_variation(high_height_map)
        
        # Higher complexity should generally produce more variation
        # (Allow some tolerance due to randomness)
        self.assertGreaterEqual(high_variation, low_variation * 0.8,
                               "Higher complexity should produce more terrain variation")
    
    def test_terrain_accessibility(self):
        """Test that generated terrain maintains accessibility for gameplay"""
        terrain = Terrain(use_varied_terrain=True, terrain_complexity=1.0)
        
        # Check that terrain doesn't have impossible slopes
        max_slope_degrees = 60  # Maximum reasonable slope for gameplay
        
        for x in range(0, SCREEN_WIDTH - 10, 10):  # Sample every 10 pixels
            height1 = terrain.get_ground_height(x)
            height2 = terrain.get_ground_height(x + 10)
            
            # Calculate slope angle
            height_diff = abs(height2 - height1)
            slope_angle = math.degrees(math.atan2(height_diff, 10))
            
            self.assertLess(slope_angle, max_slope_degrees,
                           f"Slope at x={x} should not exceed {max_slope_degrees} degrees")
    
    def test_palm_tree_placement_on_varied_terrain(self):
        """Test that palm trees are properly placed on varied terrain"""
        terrain = Terrain(use_varied_terrain=True, terrain_complexity=1.0)
        
        # Check that all palm trees are positioned correctly
        for tree in terrain.palm_trees:
            if not tree['destroyed']:
                tree_x = tree['x']
                
                # Tree should be within screen bounds
                self.assertGreaterEqual(tree_x, 0, "Tree should be within left screen bound")
                self.assertLess(tree_x, SCREEN_WIDTH, "Tree should be within right screen bound")
                
                # Tree should have reasonable height
                self.assertGreater(tree['height'], 50, "Tree should have reasonable minimum height")
                self.assertLess(tree['height'], 150, "Tree should have reasonable maximum height")
                
                # Tree should have ground_y property for varied terrain
                self.assertIn('ground_y', tree, "Tree should have ground_y property for varied terrain")
    
    @unittest.skipUnless(HYPOTHESIS_AVAILABLE, "Hypothesis not available")
    @given(
        complexity=st.floats(min_value=0.5, max_value=2.0),
        width=st.integers(min_value=100, max_value=1000)
    )
    @settings(max_examples=20, deadline=None)
    def test_property_terrain_generation_bounds(self, complexity, width):
        """
        Property test: Generated terrain should always stay within bounds
        """
        height_map = self.terrain_generator.generate_height_map(width, complexity)
        
        # Should generate correct number of points
        self.assertEqual(len(height_map), width, "Height map should match requested width")
        
        # All heights should be within valid bounds
        min_bound = SCREEN_HEIGHT - 200
        max_bound = SCREEN_HEIGHT - 50
        
        for i, height in enumerate(height_map):
            self.assertGreaterEqual(height, min_bound,
                                   f"Height at index {i} should be above minimum bound")
            self.assertLessEqual(height, max_bound,
                                f"Height at index {i} should be below maximum bound")
            self.assertIsInstance(height, int, f"Height at index {i} should be integer")
    
    @unittest.skipUnless(HYPOTHESIS_AVAILABLE, "Hypothesis not available")
    @given(
        complexity=st.floats(min_value=0.5, max_value=2.0),
        smoothing_iterations=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=15, deadline=None)
    def test_property_terrain_smoothing_consistency(self, complexity, smoothing_iterations):
        """
        Property test: Terrain smoothing should be consistent and improve terrain quality
        """
        # Generate terrain
        raw_height_map = self.terrain_generator.generate_height_map(500, complexity)
        
        # Apply smoothing
        smoothed_height_map = self.terrain_generator.smooth_terrain(raw_height_map, smoothing_iterations)
        
        # Smoothed terrain should have same length
        self.assertEqual(len(smoothed_height_map), len(raw_height_map),
                        "Smoothed terrain should maintain same length")
        
        # Smoothed terrain should still be within bounds
        min_bound = SCREEN_HEIGHT - 200
        max_bound = SCREEN_HEIGHT - 50
        
        for height in smoothed_height_map:
            self.assertGreaterEqual(height, min_bound - 10,  # Allow small tolerance
                                   "Smoothed height should be within bounds")
            self.assertLessEqual(height, max_bound + 10,
                                "Smoothed height should be within bounds")
    
    def test_terrain_generation_deterministic_with_seed(self):
        """Test that terrain generation can be made deterministic for testing"""
        import random
        
        # Set seed for reproducible results
        random.seed(12345)
        height_map1 = self.terrain_generator.generate_height_map(200, 1.0)
        
        # Reset seed and generate again
        random.seed(12345)
        height_map2 = self.terrain_generator.generate_height_map(200, 1.0)
        
        # Should be identical with same seed
        self.assertEqual(height_map1, height_map2,
                        "Terrain generation should be deterministic with same seed")
    
    def test_varied_terrain_integration(self):
        """Test that varied terrain integrates properly with game systems"""
        # Create terrain with varied generation
        terrain = Terrain(use_varied_terrain=True, terrain_complexity=1.5)
        
        # Test that terrain map is properly initialized
        self.assertIsNotNone(terrain.terrain_map, "Terrain map should be initialized")
        self.assertEqual(len(terrain.height_map), SCREEN_WIDTH,
                        "Height map should cover full screen width")
        
        # Test that ground height queries work
        for x in range(0, SCREEN_WIDTH, 100):
            height = terrain.get_ground_height(x)
            self.assertIsInstance(height, (int, float), "Ground height should be numeric")
            self.assertGreater(height, 0, "Ground height should be positive")
            self.assertLess(height, SCREEN_HEIGHT, "Ground height should be within screen")
    
    def test_flat_vs_varied_terrain_difference(self):
        """Test that varied terrain is meaningfully different from flat terrain"""
        # Create flat terrain
        flat_terrain = Terrain(use_varied_terrain=False, terrain_complexity=1.0)
        
        # Create varied terrain
        varied_terrain = Terrain(use_varied_terrain=True, terrain_complexity=1.0)
        
        # Sample heights at multiple points
        sample_points = [100, 300, 500, 700, 900, 1100]
        
        flat_heights = [flat_terrain.get_ground_height(x) for x in sample_points]
        varied_heights = [varied_terrain.get_ground_height(x) for x in sample_points]
        
        # Flat terrain should have minimal variation
        flat_variation = max(flat_heights) - min(flat_heights)
        varied_variation = max(varied_heights) - min(varied_heights)
        
        # Varied terrain should have more variation than flat terrain
        self.assertGreater(varied_variation, flat_variation,
                          "Varied terrain should have more height variation than flat terrain")
        
        # Flat terrain should be nearly constant
        self.assertLess(flat_variation, 10,
                       "Flat terrain should have minimal height variation")

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
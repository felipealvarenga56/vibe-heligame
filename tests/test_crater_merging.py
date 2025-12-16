#!/usr/bin/env python3
"""
Property-based tests for crater merging behavior
**Feature: game-enhancements, Property 2: Crater merging behavior**
**Validates: Requirements 1.4**
"""

import unittest
import sys
import os
import math
import time

# Add the parent directory to the path so we can import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from hypothesis import given, strategies as st, settings
    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False
    print("Warning: Hypothesis not available. Install with: pip install hypothesis")

from main import TerrainMap, SCREEN_WIDTH, SCREEN_HEIGHT

class TestCraterMerging(unittest.TestCase):
    """
    Property 2: Crater merging behavior
    When multiple explosions occur in overlapping areas, craters should merge 
    to create larger, more realistic depressions rather than separate holes
    """
    
    def setUp(self):
        """Set up test fixtures"""
        self.ground_level = 500
        self.terrain_map = TerrainMap(SCREEN_WIDTH, SCREEN_HEIGHT, self.ground_level)
    
    def test_overlapping_craters_merge(self):
        """Test that overlapping craters merge into larger depressions"""
        # Create two overlapping craters
        crater1_x, crater1_y, crater1_radius = 300, 520, 40
        crater2_x, crater2_y, crater2_radius = 330, 525, 35
        
        # Verify they overlap
        distance = math.sqrt((crater2_x - crater1_x)**2 + (crater2_y - crater1_y)**2)
        overlap_threshold = (crater1_radius + crater2_radius) * 0.8
        self.assertLess(distance, overlap_threshold, "Craters should overlap for this test")
        
        # Create first crater
        self.terrain_map.create_crater(crater1_x, crater1_y, crater1_radius)
        initial_crater_count = len(self.terrain_map.craters)
        
        # Create second overlapping crater
        self.terrain_map.create_crater(crater2_x, crater2_y, crater2_radius)
        
        # Merge overlapping craters
        self.terrain_map.merge_overlapping_craters()
        
        # Should have fewer craters after merging
        final_crater_count = len(self.terrain_map.craters)
        self.assertLess(final_crater_count, initial_crater_count + 1,
                       "Overlapping craters should merge to reduce total count")
    
    def test_non_overlapping_craters_remain_separate(self):
        """Test that non-overlapping craters remain separate"""
        # Create two non-overlapping craters
        crater1_x, crater1_y, crater1_radius = 200, 520, 30
        crater2_x, crater2_y, crater2_radius = 400, 530, 35
        
        # Verify they don't overlap
        distance = math.sqrt((crater2_x - crater1_x)**2 + (crater2_y - crater1_y)**2)
        overlap_threshold = (crater1_radius + crater2_radius) * 0.8
        self.assertGreater(distance, overlap_threshold, "Craters should not overlap for this test")
        
        # Create both craters
        self.terrain_map.create_crater(crater1_x, crater1_y, crater1_radius)
        self.terrain_map.create_crater(crater2_x, crater2_y, crater2_radius)
        
        initial_crater_count = len(self.terrain_map.craters)
        
        # Merge overlapping craters
        self.terrain_map.merge_overlapping_craters()
        
        # Should have same number of craters (no merging)
        final_crater_count = len(self.terrain_map.craters)
        self.assertEqual(final_crater_count, initial_crater_count,
                        "Non-overlapping craters should remain separate")
    
    def test_merged_crater_properties(self):
        """Test that merged craters have appropriate properties"""
        # Create two overlapping craters with known properties
        crater1_x, crater1_y, crater1_radius = 350, 520, 40
        crater2_x, crater2_y, crater2_radius = 370, 530, 30
        
        # Create craters with slight delay to test creation time handling
        self.terrain_map.create_crater(crater1_x, crater1_y, crater1_radius)
        time.sleep(0.01)  # Small delay
        self.terrain_map.create_crater(crater2_x, crater2_y, crater2_radius)
        
        # Merge craters
        self.terrain_map.merge_overlapping_craters()
        
        # Should have one merged crater
        self.assertEqual(len(self.terrain_map.craters), 1, "Should have one merged crater")
        
        merged_crater = self.terrain_map.craters[0]
        
        # Merged crater position should be between original positions
        self.assertGreater(merged_crater['x'], min(crater1_x, crater2_x))
        self.assertLess(merged_crater['x'], max(crater1_x, crater2_x))
        
        # Merged crater should be larger than individual craters
        self.assertGreater(merged_crater['radius'], max(crater1_radius, crater2_radius))
        
        # Should have creation time
        self.assertIn('creation_time', merged_crater)
    
    def test_multiple_crater_chain_merging(self):
        """Test merging of multiple craters in a chain"""
        # Create a chain of overlapping craters
        craters = [
            (300, 520, 35),
            (325, 525, 30),
            (350, 530, 32),
            (375, 535, 28)
        ]
        
        # Create all craters
        for crater_x, crater_y, crater_radius in craters:
            self.terrain_map.create_crater(crater_x, crater_y, crater_radius)
        
        initial_count = len(self.terrain_map.craters)
        
        # Merge overlapping craters
        self.terrain_map.merge_overlapping_craters()
        
        final_count = len(self.terrain_map.craters)
        
        # Should have fewer craters after merging
        self.assertLess(final_count, initial_count,
                       "Chain of overlapping craters should merge")
        
        # Verify merged crater encompasses the chain area
        if final_count > 0:
            merged_crater = self.terrain_map.craters[0]  # Assuming one large merged crater
            
            # Check that merged crater covers the general area
            leftmost_x = min(crater[0] for crater in craters)
            rightmost_x = max(crater[0] for crater in craters)
            
            # Merged crater should be positioned within the chain area
            self.assertGreaterEqual(merged_crater['x'] + merged_crater['radius'], leftmost_x)
            self.assertLessEqual(merged_crater['x'] - merged_crater['radius'], rightmost_x)
    
    @unittest.skipUnless(HYPOTHESIS_AVAILABLE, "Hypothesis not available")
    @given(
        crater1_x=st.integers(min_value=100, max_value=SCREEN_WIDTH-200),
        crater1_y=st.integers(min_value=500, max_value=580),
        crater1_radius=st.integers(min_value=20, max_value=60),
        crater2_radius=st.integers(min_value=20, max_value=60),
        offset_x=st.integers(min_value=-50, max_value=50),
        offset_y=st.integers(min_value=-30, max_value=30)
    )
    @settings(max_examples=30, deadline=None)
    def test_property_crater_merging_consistency(self, crater1_x, crater1_y, crater1_radius, 
                                               crater2_radius, offset_x, offset_y):
        """
        Property test: Crater merging should be consistent and predictable
        """
        # Create fresh terrain for each test
        terrain_map = TerrainMap(SCREEN_WIDTH, SCREEN_HEIGHT, self.ground_level)
        
        # Calculate second crater position
        crater2_x = crater1_x + offset_x
        crater2_y = crater1_y + offset_y
        
        # Ensure second crater is within bounds
        if not (50 <= crater2_x <= SCREEN_WIDTH - 50 and 500 <= crater2_y <= 600):
            return  # Skip invalid configurations
        
        # Create both craters
        terrain_map.create_crater(crater1_x, crater1_y, crater1_radius)
        terrain_map.create_crater(crater2_x, crater2_y, crater2_radius)
        
        initial_count = len(terrain_map.craters)
        
        # Calculate if craters should overlap
        distance = math.sqrt(offset_x**2 + offset_y**2)
        overlap_threshold = (crater1_radius + crater2_radius) * 0.8
        should_merge = distance < overlap_threshold
        
        # Merge craters
        terrain_map.merge_overlapping_craters()
        
        final_count = len(terrain_map.craters)
        
        if should_merge:
            # Should have merged (fewer craters)
            self.assertLess(final_count, initial_count,
                           f"Craters at distance {distance} with threshold {overlap_threshold} should merge")
            
            # Merged crater should exist and be reasonable
            if final_count > 0:
                merged_crater = terrain_map.craters[0]
                self.assertGreater(merged_crater['radius'], 0, "Merged crater should have positive radius")
                self.assertLess(merged_crater['radius'], 200, "Merged crater should not be unreasonably large")
        else:
            # Should not have merged (same count)
            self.assertEqual(final_count, initial_count,
                           f"Craters at distance {distance} with threshold {overlap_threshold} should not merge")
    
    def test_crater_merging_performance_limit(self):
        """Test that crater merging limits total crater count for performance"""
        # Create many craters to test performance limiting
        for i in range(60):  # More than the 50 crater limit
            crater_x = 200 + (i * 10) % 400  # Spread across terrain
            crater_y = 520 + (i % 5) * 5     # Slight y variation
            crater_radius = 20 + (i % 10)    # Varying sizes
            
            self.terrain_map.create_crater(crater_x, crater_y, crater_radius)
        
        # Merge craters
        self.terrain_map.merge_overlapping_craters()
        
        # Should not exceed performance limit
        self.assertLessEqual(len(self.terrain_map.craters), 50,
                           "Crater count should be limited for performance")
    
    def test_crater_merging_weighted_average(self):
        """Test that crater merging uses weighted average based on size"""
        # Create two craters with very different sizes
        small_crater_x, small_crater_y, small_radius = 300, 520, 20
        large_crater_x, large_crater_y, large_radius = 320, 525, 60
        
        # Position them to overlap
        distance = math.sqrt((large_crater_x - small_crater_x)**2 + (large_crater_y - small_crater_y)**2)
        overlap_threshold = (small_radius + large_radius) * 0.8
        self.assertLess(distance, overlap_threshold, "Craters should overlap")
        
        # Create craters
        self.terrain_map.create_crater(small_crater_x, small_crater_y, small_radius)
        self.terrain_map.create_crater(large_crater_x, large_crater_y, large_radius)
        
        # Merge craters
        self.terrain_map.merge_overlapping_craters()
        
        # Should have one merged crater
        self.assertEqual(len(self.terrain_map.craters), 1)
        
        merged_crater = self.terrain_map.craters[0]
        
        # Merged position should be closer to the larger crater (weighted average)
        distance_to_large = abs(merged_crater['x'] - large_crater_x)
        distance_to_small = abs(merged_crater['x'] - small_crater_x)
        
        # Due to weighted average, merged crater should be closer to larger crater
        self.assertLessEqual(distance_to_large, distance_to_small,
                           "Merged crater should be closer to larger crater due to weighted average")
    
    def test_crater_merging_idempotent(self):
        """Test that crater merging is idempotent (multiple calls don't change result)"""
        # Create overlapping craters
        self.terrain_map.create_crater(300, 520, 40)
        self.terrain_map.create_crater(320, 525, 35)
        
        # Merge once
        self.terrain_map.merge_overlapping_craters()
        first_merge_count = len(self.terrain_map.craters)
        first_merge_crater = self.terrain_map.craters[0].copy() if first_merge_count > 0 else None
        
        # Merge again
        self.terrain_map.merge_overlapping_craters()
        second_merge_count = len(self.terrain_map.craters)
        
        # Should be the same
        self.assertEqual(second_merge_count, first_merge_count,
                        "Multiple merge calls should not change result")
        
        if first_merge_crater and second_merge_count > 0:
            second_merge_crater = self.terrain_map.craters[0]
            self.assertEqual(first_merge_crater['x'], second_merge_crater['x'])
            self.assertEqual(first_merge_crater['y'], second_merge_crater['y'])
            self.assertEqual(first_merge_crater['radius'], second_merge_crater['radius'])

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
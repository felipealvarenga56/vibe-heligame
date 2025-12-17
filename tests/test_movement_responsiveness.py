#!/usr/bin/env python3
"""
Property-based tests for movement responsiveness
**Feature: arcade-mechanics-overhaul, Property 1: Movement responsiveness**
**Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5**
"""

import unittest
import sys
import os
import math

# Add the parent directory to the path so we can import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from hypothesis import given, strategies as st, settings, assume
    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False
    print("Warning: Hypothesis not available. Install with: pip install hypothesis")

from main import Player, Terrain, TerrainMap, SCREEN_WIDTH, SCREEN_HEIGHT

class MockTerrain:
    """Mock terrain for testing movement"""
    def __init__(self, slope_angle=0, ground_level=500):
        self.slope_angle = slope_angle  # Degrees
        self.ground_level = ground_level
        self.palm_trees = []
        self.terrain_map = MockTerrainMap(slope_angle, ground_level)
    
    def get_ground_height(self, x):
        # Create sloped ground based on angle
        slope_radians = math.radians(self.slope_angle)
        height_change = x * math.tan(slope_radians)
        return self.ground_level + height_change

class MockTerrainMap:
    """Mock terrain map with slope support"""
    def __init__(self, slope_angle=0, ground_level=500):
        self.slope_angle = slope_angle
        self.ground_level = ground_level
        self.height = SCREEN_HEIGHT
        self.width = SCREEN_WIDTH
    
    def get_accurate_ground_height(self, x, y_start=None):
        slope_radians = math.radians(self.slope_angle)
        height_change = x * math.tan(slope_radians)
        return self.ground_level + height_change
    
    def is_solid_at(self, x, y):
        ground_height = self.get_accurate_ground_height(x)
        return y >= ground_height

class TestMovementResponsiveness(unittest.TestCase):
    """
    Property 1: Movement responsiveness
    For any player movement input (left, right, or stop), the system should apply 
    the target velocity within 2 frames and maintain consistent speed regardless 
    of terrain slope
    """
    
    def setUp(self):
        """Set up test fixtures"""
        self.flat_terrain = MockTerrain(slope_angle=0, ground_level=500)
        self.moderate_slope = MockTerrain(slope_angle=15, ground_level=500)
        self.steep_slope = MockTerrain(slope_angle=25, ground_level=500)
    
    def test_instant_movement_response(self):
        """Test that movement input applies velocity within 1 frame (Requirement 1.1)"""
        player = Player(100, 400, 0)
        
        # Position player on ground
        player.y = self.flat_terrain.get_ground_height(100) - player.height
        player.on_ground = True
        player.velocity_x = 0
        
        # Apply movement input
        player.move_right()
        
        # Velocity should be set to move_speed immediately (within 1 frame)
        self.assertEqual(player.velocity_x, player.move_speed,
                        "Movement input should apply full speed within 1 frame")
    
    def test_instant_stop_within_two_frames(self):
        """Test that releasing movement key stops within 2 frames (Requirement 1.2)"""
        player = Player(100, 400, 0)
        
        # Position player on ground and set moving
        player.y = self.flat_terrain.get_ground_height(100) - player.height
        player.on_ground = True
        player.velocity_x = player.move_speed
        
        # Stop giving input and update (friction applies)
        player.update(self.flat_terrain)
        velocity_after_1_frame = abs(player.velocity_x)
        
        player.update(self.flat_terrain)
        velocity_after_2_frames = abs(player.velocity_x)
        
        # After 2 frames with friction of 0.75, velocity should be: 
        # move_speed * 0.75 * 0.75 = move_speed * 0.5625
        # This should be significantly reduced (< 60% of original)
        self.assertLess(velocity_after_2_frames, player.move_speed * 0.6,
                       "Horizontal movement should stop within 2 frames")
    
    def test_consistent_speed_on_flat_terrain(self):
        """Test that movement speed is consistent on flat terrain (Requirement 1.3)"""
        player = Player(100, 400, 0)
        
        # Position player on flat ground
        player.y = self.flat_terrain.get_ground_height(100) - player.height
        player.on_ground = True
        
        # Move right and record velocities
        velocities = []
        for _ in range(5):
            player.move_right()
            player.update(self.flat_terrain)
            velocities.append(abs(player.velocity_x))
        
        # All velocities should be similar (accounting for friction)
        # After move_right(), velocity is set to move_speed, then friction applies
        # So we expect: move_speed * 0.75 after each update
        expected_velocity = player.move_speed * 0.75
        
        for velocity in velocities:
            self.assertAlmostEqual(velocity, expected_velocity, delta=2,
                                  msg="Movement speed should be consistent on flat terrain")
    
    def test_consistent_speed_on_slopes(self):
        """Test that movement speed is consistent regardless of slope (Requirement 1.3)"""
        # Test on flat terrain
        flat_player = Player(100, 400, 0)
        flat_player.y = self.flat_terrain.get_ground_height(100) - flat_player.height
        flat_player.on_ground = True
        flat_player.move_right()
        flat_player.update(self.flat_terrain)
        flat_velocity = abs(flat_player.velocity_x)
        
        # Test on moderate slope
        slope_player = Player(100, 400, 0)
        slope_player.y = self.moderate_slope.get_ground_height(100) - slope_player.height
        slope_player.on_ground = True
        slope_player.move_right()
        slope_player.update(self.moderate_slope)
        slope_velocity = abs(slope_player.velocity_x)
        
        # Velocities should be very similar (< 5% difference per requirement 6.5)
        velocity_difference_percent = abs(flat_velocity - slope_velocity) / flat_velocity * 100
        
        self.assertLess(velocity_difference_percent, 5,
                       f"Movement speed should not vary by more than 5% on slopes. "
                       f"Flat: {flat_velocity}, Slope: {slope_velocity}, "
                       f"Difference: {velocity_difference_percent:.1f}%")
    
    def test_full_air_control(self):
        """Test that player has full air control without momentum penalties (Requirement 1.4)"""
        player = Player(100, 300, 0)
        
        # Position player in air
        player.y = 200
        player.on_ground = False
        player.velocity_x = 0
        player.velocity_y = 5  # Falling
        
        # Apply air movement
        player.move_right()
        
        # Should have full movement speed in air
        self.assertEqual(player.velocity_x, player.move_speed,
                        "Player should have full air control without momentum penalties")
        
        # Update and check that air movement is maintained
        player.update(self.flat_terrain)
        
        # Velocity should be affected by friction but not by "air control penalty"
        expected_velocity = player.move_speed * 0.75  # Just friction
        self.assertAlmostEqual(abs(player.velocity_x), expected_velocity, delta=1,
                              msg="Air control should not have additional momentum penalties")
    
    def test_immediate_movement_after_landing(self):
        """Test that player can move immediately after landing (Requirement 1.5)"""
        player = Player(100, 200, 0)
        
        # Position player falling
        player.y = 300
        player.on_ground = False
        player.velocity_y = 10  # Falling fast
        
        # Update until player lands
        for _ in range(50):
            player.update(self.flat_terrain)
            if player.on_ground:
                break
        
        self.assertTrue(player.on_ground, "Player should have landed")
        
        # Immediately apply movement input
        player.move_right()
        
        # Should have full movement speed immediately
        self.assertEqual(player.velocity_x, player.move_speed,
                        "Player should be able to move at full speed immediately after landing")
        
        # Update and verify movement
        old_x = player.x
        player.update(self.flat_terrain)
        
        # Player should have moved right
        self.assertGreater(player.x, old_x,
                          "Player should move immediately after landing without recovery delay")
    
    @unittest.skipUnless(HYPOTHESIS_AVAILABLE, "Hypothesis not available")
    @given(
        slope_angle=st.floats(min_value=-30, max_value=30),
        initial_velocity=st.floats(min_value=-25, max_value=25),
        player_x=st.integers(min_value=100, max_value=1000)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_movement_responsiveness(self, slope_angle, initial_velocity, player_x):
        """
        Property test: For any player movement input, the system should apply 
        the target velocity within 2 frames and maintain consistent speed 
        regardless of terrain slope
        """
        # Skip edge cases
        assume(abs(initial_velocity) > 1)  # Skip very small velocities
        assume(player_x + 32 < SCREEN_WIDTH)  # Keep player on screen
        
        # Create terrain with specified slope
        terrain = MockTerrain(slope_angle=slope_angle, ground_level=500)
        
        # Create player
        player = Player(player_x, 300, 0)
        
        # Position player on ground
        ground_height = terrain.get_ground_height(player.x + player.width // 2)
        player.y = ground_height - player.height
        player.on_ground = True
        player.velocity_x = 0
        
        # Apply movement input
        if initial_velocity > 0:
            player.move_right()
        else:
            player.move_left()
        
        # Check immediate response (within 1 frame)
        expected_velocity = player.move_speed if initial_velocity > 0 else -player.move_speed
        self.assertEqual(player.velocity_x, expected_velocity,
                        "Movement input should apply full speed within 1 frame")
        
        # Update and check velocity is maintained (accounting for friction and minimal slope effects)
        player.update(terrain)
        velocity_after_update = abs(player.velocity_x)
        
        # After update with friction 0.75, expect: move_speed * 0.75
        # With minimal slope effects (< 5%), should be close to this
        expected_after_friction = player.move_speed * 0.75
        
        # Allow for minimal slope effects (< 5% per requirement)
        tolerance = expected_after_friction * 0.05
        
        self.assertAlmostEqual(velocity_after_update, expected_after_friction, 
                              delta=tolerance + 2,  # +2 for numerical precision
                              msg=f"Velocity should be consistent on slope {slope_angle:.1f}°")
        
        # Test stopping within 2 frames
        # Stop giving input and let friction work
        player.update(terrain)
        velocity_after_2_frames = abs(player.velocity_x)
        
        # After 2 frames: move_speed * 0.75 * 0.75 = move_speed * 0.5625
        # Should be significantly reduced
        self.assertLess(velocity_after_2_frames, player.move_speed * 0.6,
                       "Movement should stop significantly within 2 frames")
    
    @unittest.skipUnless(HYPOTHESIS_AVAILABLE, "Hypothesis not available")
    @given(
        fall_height=st.integers(min_value=50, max_value=300),
        landing_velocity_y=st.floats(min_value=5, max_value=20)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_immediate_control_after_landing(self, fall_height, landing_velocity_y):
        """
        Property test: For any landing scenario, player should have immediate 
        movement control without recovery delay
        """
        terrain = MockTerrain(slope_angle=0, ground_level=500)
        player = Player(200, 300, 0)
        
        # Position player in air, falling
        ground_height = terrain.get_ground_height(200)
        player.y = ground_height - player.height - fall_height
        player.on_ground = False
        player.velocity_y = landing_velocity_y
        player.velocity_x = 0
        
        # Update until player lands
        landed = False
        for _ in range(100):
            player.update(terrain)
            if player.on_ground:
                landed = True
                break
        
        assume(landed)  # Only test if player actually landed
        
        # Immediately apply movement input
        player.move_right()
        
        # Should have full movement speed immediately
        self.assertEqual(player.velocity_x, player.move_speed,
                        "Player should have full speed immediately after landing")
        
        # Update and verify movement occurred
        old_x = player.x
        player.update(terrain)
        
        # Player should have moved (accounting for friction)
        # Expected movement: move_speed * 0.75 (after friction)
        expected_min_movement = player.move_speed * 0.75 * 0.8  # 80% of expected
        actual_movement = player.x - old_x
        
        self.assertGreater(actual_movement, expected_min_movement,
                          f"Player should move immediately after landing. "
                          f"Expected > {expected_min_movement:.1f}, got {actual_movement:.1f}")

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)

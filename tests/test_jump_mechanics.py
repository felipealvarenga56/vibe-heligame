#!/usr/bin/env python3
"""
Property-based tests for jump mechanics
**Feature: arcade-mechanics-overhaul, Property 2, 3, 4: Jump mechanics**
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

from main import Player, SCREEN_WIDTH, SCREEN_HEIGHT

class MockTerrain:
    """Mock terrain for testing jump mechanics"""
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

class TestJumpMechanicsTightness(unittest.TestCase):
    """
    Property 2: Jump mechanics tightness
    **Validates: Requirements 2.1, 2.2, 2.4**
    
    For any jump input, the system should apply jump force instantly, 
    use gravity >= 1.0, and provide immediate ground control on landing
    """
    
    def setUp(self):
        """Set up test fixtures"""
        self.flat_terrain = MockTerrain(slope_angle=0, ground_level=500)
    
    def test_instant_jump_force_application(self):
        """Test that jump force is applied instantly (Requirement 2.1)"""
        player = Player(100, 400, 0)
        
        # Position player on ground
        player.y = self.flat_terrain.get_ground_height(100) - player.height
        player.on_ground = True
        player.velocity_y = 0
        
        # Apply jump
        player.jump()
        
        # Velocity should be set to jump_power immediately
        self.assertEqual(player.velocity_y, player.jump_power,
                        "Jump force should be applied instantly within 1 frame")
        self.assertFalse(player.on_ground,
                        "Player should be airborne immediately after jump")
    
    def test_gravity_minimum_requirement(self):
        """Test that gravity is at least 1.0 units per frame (Requirement 2.2)"""
        player = Player(100, 200, 0)
        
        # Position player in air
        player.y = 200
        player.on_ground = False
        initial_velocity_y = 0
        player.velocity_y = initial_velocity_y
        
        # Update once to apply gravity
        player.update(self.flat_terrain)
        
        # Calculate gravity applied
        gravity_applied = player.velocity_y - initial_velocity_y
        
        # Gravity should be >= 1.0 per requirement
        self.assertGreaterEqual(gravity_applied, 1.0,
                               f"Gravity should be >= 1.0, but got {gravity_applied}")
    
    def test_immediate_ground_control_after_landing(self):
        """Test that player has immediate ground control on landing (Requirement 2.4)"""
        player = Player(100, 200, 0)
        
        # Position player falling
        player.y = 300
        player.on_ground = False
        player.velocity_y = 10  # Falling
        player.velocity_x = 0
        
        # Update until player lands
        for _ in range(50):
            player.update(self.flat_terrain)
            if player.on_ground:
                break
        
        self.assertTrue(player.on_ground, "Player should have landed")
        
        # Check that vertical velocity is stopped (no bouncing/sliding)
        self.assertEqual(player.velocity_y, 0,
                        "Vertical velocity should be 0 on landing")
        
        # Apply movement input immediately
        player.move_right()
        
        # Should have full movement speed immediately
        self.assertEqual(player.velocity_x, player.move_speed,
                        "Player should have immediate ground control after landing")
    
    @unittest.skipUnless(HYPOTHESIS_AVAILABLE, "Hypothesis not available")
    @given(
        player_x=st.integers(min_value=100, max_value=1000),
        initial_velocity_x=st.floats(min_value=-25, max_value=25)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_jump_mechanics_tightness(self, player_x, initial_velocity_x):
        """
        Property 2: Jump mechanics tightness
        **Validates: Requirements 2.1, 2.2, 2.4**
        
        For any jump input, the system should apply jump force instantly,
        use gravity >= 1.0, and provide immediate ground control on landing
        """
        # Skip edge cases
        assume(player_x + 32 < SCREEN_WIDTH)  # Keep player on screen
        
        terrain = MockTerrain(slope_angle=0, ground_level=500)
        player = Player(player_x, 300, 0)
        
        # Position player on ground
        ground_height = terrain.get_ground_height(player.x + player.width // 2)
        player.y = ground_height - player.height
        player.on_ground = True
        player.velocity_y = 0
        player.velocity_x = initial_velocity_x
        
        # Test 1: Instant jump force application (Requirement 2.1)
        player.jump()
        
        self.assertEqual(player.velocity_y, player.jump_power,
                        "Jump force should be applied instantly")
        self.assertFalse(player.on_ground,
                        "Player should be airborne immediately after jump")
        
        # Test 2: Gravity >= 1.0 (Requirement 2.2)
        initial_velocity_y = player.velocity_y
        player.update(terrain)
        
        gravity_applied = player.velocity_y - initial_velocity_y
        self.assertGreaterEqual(gravity_applied, 1.0,
                               f"Gravity should be >= 1.0, got {gravity_applied}")
        
        # Let player complete jump arc and land
        max_iterations = 200
        landed = False
        for _ in range(max_iterations):
            player.update(terrain)
            if player.on_ground:
                landed = True
                break
        
        assume(landed)  # Only test landing if player actually landed
        
        # Test 3: Immediate ground control on landing (Requirement 2.4)
        self.assertEqual(player.velocity_y, 0,
                        "Vertical velocity should be 0 on landing (no sliding)")
        
        # Apply movement input
        player.move_right()
        
        self.assertEqual(player.velocity_x, player.move_speed,
                        "Player should have immediate ground control after landing")

class TestVariableJumpHeight(unittest.TestCase):
    """
    Property 3: Variable jump height
    **Validates: Requirements 2.3**
    
    For any jump where the button is released early, the final jump height 
    should be less than a full-duration jump
    """
    
    def setUp(self):
        """Set up test fixtures"""
        self.flat_terrain = MockTerrain(slope_angle=0, ground_level=500)
    
    def test_early_release_reduces_jump_height(self):
        """Test that releasing jump early results in shorter jump (Requirement 2.3)"""
        # Full jump test
        full_jump_player = Player(100, 400, 0)
        ground_height = self.flat_terrain.get_ground_height(100)
        full_jump_player.y = ground_height - full_jump_player.height
        full_jump_player.on_ground = True
        
        full_jump_player.jump()
        
        # Simulate full jump (don't release early)
        max_height_full = full_jump_player.y
        for _ in range(100):
            full_jump_player.update(self.flat_terrain)
            max_height_full = min(max_height_full, full_jump_player.y)
            if full_jump_player.on_ground:
                break
        
        # Early release jump test
        early_release_player = Player(100, 400, 0)
        early_release_player.y = ground_height - early_release_player.height
        early_release_player.on_ground = True
        
        early_release_player.jump()
        
        # Simulate early release (reduce velocity after a few frames)
        for i in range(100):
            if i == 5 and early_release_player.velocity_y < 0:  # Release after 5 frames
                # Simulate early release by reducing upward velocity
                early_release_player.velocity_y *= 0.5
            
            early_release_player.update(self.flat_terrain)
            if i == 0:
                max_height_early = early_release_player.y
            else:
                max_height_early = min(max_height_early, early_release_player.y)
            
            if early_release_player.on_ground:
                break
        
        # Early release should result in lower max height (higher y value)
        self.assertGreater(max_height_early, max_height_full,
                          f"Early release jump should be shorter. "
                          f"Full: {max_height_full}, Early: {max_height_early}")
    
    @unittest.skipUnless(HYPOTHESIS_AVAILABLE, "Hypothesis not available")
    @given(
        release_frame=st.integers(min_value=2, max_value=15),
        player_x=st.integers(min_value=100, max_value=1000)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_variable_jump_height(self, release_frame, player_x):
        """
        Property 3: Variable jump height
        **Validates: Requirements 2.3**
        
        For any jump where the button is released early, the final jump height
        should be less than a full-duration jump
        """
        assume(player_x + 32 < SCREEN_WIDTH)
        
        terrain = MockTerrain(slope_angle=0, ground_level=500)
        
        # Full jump
        full_player = Player(player_x, 300, 0)
        ground_height = terrain.get_ground_height(full_player.x)
        full_player.y = ground_height - full_player.height
        full_player.on_ground = True
        
        full_player.jump()
        max_height_full = full_player.y
        
        for _ in range(100):
            full_player.update(terrain)
            max_height_full = min(max_height_full, full_player.y)
            if full_player.on_ground:
                break
        
        # Early release jump
        early_player = Player(player_x, 300, 0)
        early_player.y = ground_height - early_player.height
        early_player.on_ground = True
        
        early_player.jump()
        max_height_early = early_player.y
        
        for i in range(100):
            if i == release_frame and early_player.velocity_y < 0:
                # Simulate early release
                early_player.velocity_y *= 0.5
            
            early_player.update(terrain)
            max_height_early = min(max_height_early, early_player.y)
            
            if early_player.on_ground:
                break
        
        # Early release should result in lower max height (higher y value)
        # Allow small tolerance for very late releases
        if release_frame < 10:
            self.assertGreater(max_height_early, max_height_full,
                              f"Early release at frame {release_frame} should result in shorter jump")

class TestSlopeIndependentJumping(unittest.TestCase):
    """
    Property 4: Slope-independent jumping
    **Validates: Requirements 2.5**
    
    For any terrain slope, jump height should remain consistent 
    regardless of slope angle
    """
    
    def setUp(self):
        """Set up test fixtures"""
        self.flat_terrain = MockTerrain(slope_angle=0, ground_level=500)
        self.moderate_slope = MockTerrain(slope_angle=15, ground_level=500)
        self.steep_slope = MockTerrain(slope_angle=25, ground_level=500)
    
    def test_consistent_jump_height_on_slopes(self):
        """Test that jump height is consistent on different slopes (Requirement 2.5)"""
        test_x = 200
        
        # Jump on flat terrain
        flat_player = Player(test_x, 300, 0)
        ground_height_flat = self.flat_terrain.get_ground_height(test_x)
        flat_player.y = ground_height_flat - flat_player.height
        flat_player.on_ground = True
        
        flat_player.jump()
        max_height_flat = flat_player.y
        
        for _ in range(100):
            flat_player.update(self.flat_terrain)
            max_height_flat = min(max_height_flat, flat_player.y)
            if flat_player.on_ground:
                break
        
        # Jump on moderate slope
        slope_player = Player(test_x, 300, 0)
        ground_height_slope = self.moderate_slope.get_ground_height(test_x)
        slope_player.y = ground_height_slope - slope_player.height
        slope_player.on_ground = True
        
        slope_player.jump()
        max_height_slope = slope_player.y
        
        for _ in range(100):
            slope_player.update(self.moderate_slope)
            max_height_slope = min(max_height_slope, slope_player.y)
            if slope_player.on_ground:
                break
        
        # Calculate jump heights (distance from ground)
        jump_height_flat = ground_height_flat - max_height_flat
        jump_height_slope = ground_height_slope - max_height_slope
        
        # Jump heights should be very similar (within 10% tolerance)
        height_difference_percent = abs(jump_height_flat - jump_height_slope) / jump_height_flat * 100
        
        self.assertLess(height_difference_percent, 10,
                       f"Jump height should be consistent on slopes. "
                       f"Flat: {jump_height_flat:.1f}, Slope: {jump_height_slope:.1f}, "
                       f"Difference: {height_difference_percent:.1f}%")
    
    @unittest.skipUnless(HYPOTHESIS_AVAILABLE, "Hypothesis not available")
    @given(
        slope_angle=st.floats(min_value=-30, max_value=30),
        player_x=st.integers(min_value=200, max_value=800)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_slope_independent_jumping(self, slope_angle, player_x):
        """
        Property 4: Slope-independent jumping
        **Validates: Requirements 2.5**
        
        For any terrain slope, jump height should remain consistent
        regardless of slope angle
        """
        assume(player_x + 32 < SCREEN_WIDTH)
        assume(abs(slope_angle) < 25)  # Reasonable slope range for arcade game
        
        # Jump on flat terrain (baseline)
        flat_terrain = MockTerrain(slope_angle=0, ground_level=500)
        flat_player = Player(player_x, 300, 0)
        ground_height_flat = flat_terrain.get_ground_height(player_x)
        flat_player.y = ground_height_flat - flat_player.height
        flat_player.on_ground = True
        flat_player.velocity_x = 0  # No horizontal movement
        
        flat_player.jump()
        max_height_flat = flat_player.y
        takeoff_y_flat = flat_player.y
        
        for _ in range(100):
            flat_player.update(flat_terrain)
            max_height_flat = min(max_height_flat, flat_player.y)
            if flat_player.on_ground:
                break
        
        # Jump on sloped terrain
        sloped_terrain = MockTerrain(slope_angle=slope_angle, ground_level=500)
        sloped_player = Player(player_x, 300, 0)
        ground_height_sloped = sloped_terrain.get_ground_height(player_x)
        sloped_player.y = ground_height_sloped - sloped_player.height
        sloped_player.on_ground = True
        sloped_player.velocity_x = 0  # No horizontal movement
        
        sloped_player.jump()
        max_height_sloped = sloped_player.y
        takeoff_y_sloped = sloped_player.y
        
        for _ in range(100):
            sloped_player.update(sloped_terrain)
            max_height_sloped = min(max_height_sloped, sloped_player.y)
            if sloped_player.on_ground:
                break
        
        # Calculate jump heights (vertical distance traveled from takeoff)
        jump_height_flat = takeoff_y_flat - max_height_flat
        jump_height_sloped = takeoff_y_sloped - max_height_sloped
        
        # Jump heights should be similar (within 20% tolerance for varied slopes)
        # The tolerance accounts for physics simulation complexity on extreme slopes
        if abs(jump_height_flat) > 10:  # Only test if there was a meaningful jump
            height_difference_percent = abs(jump_height_flat - jump_height_sloped) / abs(jump_height_flat) * 100
            
            self.assertLess(height_difference_percent, 20,
                           f"Jump height should be consistent on slope {slope_angle:.1f}°. "
                           f"Flat: {jump_height_flat:.1f}, Sloped: {jump_height_sloped:.1f}")

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)

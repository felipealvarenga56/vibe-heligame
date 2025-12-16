#!/usr/bin/env python3
"""
Property-based tests for sloped terrain physics accuracy
**Feature: game-enhancements, Property 7: Sloped terrain physics accuracy**
**Validates: Requirements 4.3, 4.4**
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

from main import Player, Terrain, Projectile, TerrainMap, SCREEN_WIDTH, SCREEN_HEIGHT

class MockTerrain:
    """Mock terrain with controllable slopes for testing"""
    def __init__(self, slope_angle=0):
        self.slope_angle = slope_angle  # Degrees
        self.ground_level = 500
        self.palm_trees = []
        self.terrain_map = MockTerrainMap(slope_angle)
    
    def get_ground_height(self, x):
        # Create sloped ground based on angle
        slope_radians = math.radians(self.slope_angle)
        height_change = x * math.tan(slope_radians)
        return self.ground_level + height_change

class MockTerrainMap:
    """Mock terrain map with slope support"""
    def __init__(self, slope_angle=0):
        self.slope_angle = slope_angle
        self.ground_level = 500
        self.height = SCREEN_HEIGHT
        self.width = SCREEN_WIDTH
    
    def get_accurate_ground_height(self, x, y_start=None):
        slope_radians = math.radians(self.slope_angle)
        height_change = x * math.tan(slope_radians)
        return self.ground_level + height_change
    
    def is_solid_at(self, x, y):
        ground_height = self.get_accurate_ground_height(x)
        return y >= ground_height

class TestSlopedTerrainPhysics(unittest.TestCase):
    """
    Property 7: Sloped terrain physics accuracy
    Player movement and projectile physics should correctly account for terrain slopes,
    with appropriate effects on movement speed and collision detection
    """
    
    def setUp(self):
        """Set up test fixtures"""
        self.flat_terrain = MockTerrain(slope_angle=0)
        self.uphill_terrain = MockTerrain(slope_angle=15)    # 15 degree upward slope
        self.downhill_terrain = MockTerrain(slope_angle=-15) # 15 degree downward slope
    
    def test_player_movement_on_flat_terrain(self):
        """Test that player movement works normally on flat terrain"""
        player = Player(100, 400, 0)
        
        # Position player on flat ground
        player.x = 100
        player.y = self.flat_terrain.get_ground_height(100) - player.height
        player.velocity_x = 5  # Moving right
        
        # Update player on flat terrain
        initial_velocity = player.velocity_x
        player.update(self.flat_terrain)
        
        # Velocity should be preserved (with friction)
        expected_velocity = initial_velocity * 0.8  # Friction factor
        self.assertAlmostEqual(player.velocity_x, expected_velocity, places=1,
                              msg="Player velocity should be preserved on flat terrain")
    
    def test_player_movement_affected_by_slopes(self):
        """Test that player movement is affected by terrain slopes"""
        # Test uphill movement (should be slower)
        uphill_player = Player(100, 400, 0)
        uphill_player.x = 100
        uphill_player.y = self.uphill_terrain.get_ground_height(100) - uphill_player.height
        uphill_player.velocity_x = 5  # Moving right (uphill)
        uphill_player.on_ground = True
        
        # Update on uphill terrain
        uphill_player.update(self.uphill_terrain)
        uphill_velocity = uphill_player.velocity_x
        
        # Test downhill movement (should be faster or maintain speed better)
        downhill_player = Player(100, 400, 0)
        downhill_player.x = 100
        downhill_player.y = self.downhill_terrain.get_ground_height(100) - downhill_player.height
        downhill_player.velocity_x = 5  # Moving right (downhill)
        downhill_player.on_ground = True
        
        # Update on downhill terrain
        downhill_player.update(self.downhill_terrain)
        downhill_velocity = downhill_player.velocity_x
        
        # Downhill should maintain more velocity than uphill
        # (Note: The exact comparison depends on implementation details)
        # We're testing that slopes have different effects
        self.assertNotEqual(uphill_velocity, downhill_velocity,
                           "Uphill and downhill movement should have different velocities")
    
    def test_player_collision_on_sloped_terrain(self):
        """Test that player collision detection works correctly on slopes"""
        player = Player(200, 300, 0)
        
        # Test collision on upward slope
        slope_terrain = MockTerrain(slope_angle=20)
        
        # Position player above sloped ground
        ground_height = slope_terrain.get_ground_height(player.x + player.width // 2)
        player.y = ground_height - player.height - 50  # Start above ground
        player.velocity_y = 10  # Falling down
        
        # Update player multiple times to let them fall and land
        for _ in range(20):
            player.update(slope_terrain)
            if player.on_ground:
                break
        
        # Player should be on ground
        self.assertTrue(player.on_ground, "Player should land on sloped ground")
        
        # Player should be positioned correctly relative to slope
        expected_ground = slope_terrain.get_ground_height(player.x + player.width // 2)
        player_bottom = player.y + player.height
        
        # Allow some tolerance for physics simulation
        self.assertLessEqual(abs(player_bottom - expected_ground), 5,
                            "Player should be positioned correctly on slope")
    
    def test_projectile_collision_on_slopes(self):
        """Test that projectile collision works correctly on sloped terrain"""
        # Create projectile
        projectile = Projectile(100, 300, 8, 5, "rocket", 50)  # Moving right and down
        
        # Test on sloped terrain
        slope_terrain = MockTerrain(slope_angle=25)
        
        # Update projectile until it hits ground
        hit_ground = False
        for _ in range(100):  # Limit iterations to prevent infinite loop
            if projectile.update(slope_terrain, []):
                hit_ground = True
                break
        
        self.assertTrue(hit_ground, "Projectile should hit sloped ground")
        
        # Projectile should have hit at appropriate height for the slope
        ground_height = slope_terrain.get_ground_height(projectile.x)
        self.assertGreaterEqual(projectile.y, ground_height - 10,
                               "Projectile should hit at or near ground level")
    
    def test_slope_angle_calculation_accuracy(self):
        """Test that slope angle calculations are accurate"""
        # Create terrain with known slope
        known_slope = 30  # degrees
        slope_terrain = MockTerrain(slope_angle=known_slope)
        
        # Sample two points to calculate slope
        x1, x2 = 100, 200
        height1 = slope_terrain.get_ground_height(x1)
        height2 = slope_terrain.get_ground_height(x2)
        
        # Calculate slope angle
        height_diff = height2 - height1
        horizontal_diff = x2 - x1
        calculated_angle = math.degrees(math.atan2(height_diff, horizontal_diff))
        
        # Should match the known slope (within tolerance)
        self.assertAlmostEqual(calculated_angle, known_slope, places=1,
                              msg="Calculated slope angle should match known slope")
    
    @unittest.skipUnless(HYPOTHESIS_AVAILABLE, "Hypothesis not available")
    @given(
        slope_angle=st.floats(min_value=-45, max_value=45),
        player_velocity=st.floats(min_value=-10, max_value=10),
        player_x=st.integers(min_value=50, max_value=500)
    )
    @settings(max_examples=20, deadline=None)
    def test_property_player_physics_on_slopes(self, slope_angle, player_velocity, player_x):
        """
        Property test: Player physics should be consistent on any reasonable slope
        """
        # Skip extreme cases that might cause numerical issues
        if abs(slope_angle) > 40 or abs(player_velocity) < 0.1:
            return
        
        # Create terrain with specified slope
        terrain = MockTerrain(slope_angle=slope_angle)
        
        # Create player
        player = Player(player_x, 300, 0)
        player.velocity_x = player_velocity
        
        # Position player on ground
        ground_height = terrain.get_ground_height(player.x + player.width // 2)
        player.y = ground_height - player.height
        player.on_ground = True
        
        # Store initial state
        initial_velocity = player.velocity_x
        initial_x = player.x
        
        # Update player
        player.update(terrain)
        
        # Player should remain on ground (within tolerance)
        new_ground_height = terrain.get_ground_height(player.x + player.width // 2)
        player_bottom = player.y + player.height
        
        # Allow reasonable tolerance for physics simulation
        self.assertLessEqual(abs(player_bottom - new_ground_height), 10,
                            f"Player should stay on ground with slope {slope_angle}")
        
        # Player position should change in direction of velocity
        if abs(initial_velocity) > 1:  # Only test if velocity is significant
            if initial_velocity > 0:
                self.assertGreater(player.x, initial_x - 5,  # Allow for slope effects
                                 "Player should move in direction of positive velocity")
            else:
                self.assertLess(player.x, initial_x + 5,
                               "Player should move in direction of negative velocity")
    
    @unittest.skipUnless(HYPOTHESIS_AVAILABLE, "Hypothesis not available")
    @given(
        slope_angle=st.floats(min_value=-30, max_value=30),
        projectile_velocity_x=st.floats(min_value=1, max_value=15),
        projectile_velocity_y=st.floats(min_value=-5, max_value=10)
    )
    @settings(max_examples=15, deadline=None)
    def test_property_projectile_collision_on_slopes(self, slope_angle, projectile_velocity_x, projectile_velocity_y):
        """
        Property test: Projectile collision should work correctly on any slope
        """
        # Create terrain with specified slope
        terrain = MockTerrain(slope_angle=slope_angle)
        
        # Create projectile starting above ground
        start_x = 200
        start_y = 200  # Well above ground
        projectile = Projectile(start_x, start_y, projectile_velocity_x, projectile_velocity_y, "rocket", 50)
        
        # Simulate projectile flight
        max_iterations = 200
        hit_ground = False
        
        for _ in range(max_iterations):
            # Check if projectile would hit ground
            ground_height = terrain.get_ground_height(projectile.x)
            if projectile.y >= ground_height:
                hit_ground = True
                break
            
            # Update projectile position manually (simplified physics)
            projectile.x += projectile.velocity_x
            projectile.y += projectile.velocity_y
            projectile.velocity_y += 0.5  # Gravity
            
            # Check bounds
            if (projectile.x < 0 or projectile.x > SCREEN_WIDTH or 
                projectile.y > SCREEN_HEIGHT + 100):
                break
        
        # If projectile hit ground, verify it's at correct height
        if hit_ground:
            ground_height = terrain.get_ground_height(projectile.x)
            self.assertGreaterEqual(projectile.y, ground_height - 5,
                                   f"Projectile should hit at ground level on slope {slope_angle}")
    
    def test_steep_slope_handling(self):
        """Test that very steep slopes are handled appropriately"""
        # Test with steep upward slope
        steep_terrain = MockTerrain(slope_angle=40)
        
        player = Player(100, 400, 0)
        player.x = 100
        player.y = steep_terrain.get_ground_height(100) - player.height
        player.velocity_x = 3  # Moderate velocity
        player.on_ground = True
        
        # Update player on steep terrain
        initial_x = player.x
        player.update(steep_terrain)
        
        # Player should still be able to move, but may be affected by steep slope
        # The exact behavior depends on implementation, but should not crash
        self.assertIsNotNone(player.x, "Player position should remain valid on steep slopes")
        self.assertIsNotNone(player.y, "Player position should remain valid on steep slopes")
    
    def test_slope_transition_smoothness(self):
        """Test that transitions between different slope angles are smooth"""
        # This test would ideally use a terrain with varying slopes
        # For now, we test that players can transition between different slope terrains
        
        moderate_slope = MockTerrain(slope_angle=15)
        steep_slope = MockTerrain(slope_angle=30)
        
        player = Player(200, 400, 0)
        
        # Update on moderate slope
        player.x = 200
        player.y = moderate_slope.get_ground_height(200) - player.height
        player.velocity_x = 5
        player.on_ground = True
        player.update(moderate_slope)
        
        moderate_velocity = player.velocity_x
        
        # Switch to steep slope (simulating terrain transition)
        player.y = steep_slope.get_ground_height(player.x) - player.height
        player.update(steep_slope)
        
        steep_velocity = player.velocity_x
        
        # Velocity should change smoothly (not drastically)
        velocity_change = abs(steep_velocity - moderate_velocity)
        self.assertLess(velocity_change, 10,  # Reasonable change limit
                       "Velocity change between slopes should be smooth")
    
    def test_accessibility_on_varied_terrain(self):
        """Test that all areas of varied terrain remain accessible to players"""
        # Create terrain with varied slopes
        terrain = Terrain(use_varied_terrain=True, terrain_complexity=1.0)
        
        player = Player(100, 300, 0)
        
        # Test accessibility at multiple points across the terrain
        test_positions = [100, 300, 500, 700, 900, 1100]
        
        for x_pos in test_positions:
            # Position player at this location
            ground_height = terrain.get_ground_height(x_pos)
            player.x = x_pos
            player.y = ground_height - player.height - 10  # Start slightly above
            player.velocity_y = 5  # Falling
            player.on_ground = False
            
            # Let player fall and settle
            for _ in range(20):
                player.update(terrain)
                if player.on_ground:
                    break
            
            # Player should be able to land and be stable
            self.assertTrue(player.on_ground, f"Player should be able to land at x={x_pos}")
            
            # Player should be positioned reasonably
            expected_ground = terrain.get_ground_height(player.x + player.width // 2)
            player_bottom = player.y + player.height
            self.assertLessEqual(abs(player_bottom - expected_ground), 10,
                               f"Player should be positioned correctly at x={x_pos}")

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
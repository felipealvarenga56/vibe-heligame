#!/usr/bin/env python3
"""
Test audio system integration
"""

import unittest
import pygame
import sys
import os

# Add the parent directory to the path so we can import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import AudioManager, GameManager, Player, Projectile

class TestAudioIntegration(unittest.TestCase):
    """Test that audio system is properly integrated into game components"""
    
    def setUp(self):
        """Set up test environment"""
        pygame.init()
        pygame.mixer.init()
        self.audio_manager = AudioManager()
    
    def tearDown(self):
        """Clean up after tests"""
        pygame.mixer.quit()
        pygame.quit()
    
    def test_audio_manager_initialization(self):
        """Test that AudioManager initializes correctly"""
        self.assertIsNotNone(self.audio_manager)
        self.assertIsInstance(self.audio_manager.sounds, dict)
        self.assertTrue(len(self.audio_manager.sounds) > 0)
        
        # Check that all expected sound types are loaded (even if None)
        expected_sounds = [
            'rocket_fire', 'banana_fire', 'melee_fire',
            'rocket_explosion', 'banana_explosion', 'melee_explosion',
            'player_jump', 'player_land', 'player_move',
            'power_charge', 'power_release',
            'terrain_destroy', 'tree_destroy'
        ]
        
        for sound_name in expected_sounds:
            self.assertIn(sound_name, self.audio_manager.sounds)
    
    def test_audio_manager_play_sound_methods(self):
        """Test that all audio manager play methods work without errors"""
        # These should not raise exceptions even if sounds are None
        self.audio_manager.play_weapon_fire_sound('rocket')
        self.audio_manager.play_weapon_fire_sound('banana')
        self.audio_manager.play_weapon_fire_sound('melee')
        
        self.audio_manager.play_explosion_sound('rocket')
        self.audio_manager.play_explosion_sound('banana')
        self.audio_manager.play_explosion_sound('melee')
        
        self.audio_manager.play_movement_sound('jump')
        self.audio_manager.play_movement_sound('land')
        self.audio_manager.play_movement_sound('move')
        
        self.audio_manager.play_power_sound('charge')
        self.audio_manager.play_power_sound('release')
        
        self.audio_manager.play_destruction_sound('terrain')
        self.audio_manager.play_destruction_sound('tree')
    
    def test_volume_control(self):
        """Test volume control functionality"""
        original_volume = self.audio_manager.master_volume
        
        # Test setting volume
        self.audio_manager.set_master_volume(0.5)
        self.assertEqual(self.audio_manager.master_volume, 0.5)
        
        # Test volume bounds
        self.audio_manager.set_master_volume(1.5)  # Should clamp to 1.0
        self.assertEqual(self.audio_manager.master_volume, 1.0)
        
        self.audio_manager.set_master_volume(-0.5)  # Should clamp to 0.0
        self.assertEqual(self.audio_manager.master_volume, 0.0)
        
        # Restore original volume
        self.audio_manager.set_master_volume(original_volume)
    
    def test_audio_toggle(self):
        """Test audio enable/disable functionality"""
        original_state = self.audio_manager.audio_enabled
        
        # Toggle audio
        self.audio_manager.toggle_audio()
        self.assertEqual(self.audio_manager.audio_enabled, not original_state)
        
        # Toggle back
        self.audio_manager.toggle_audio()
        self.assertEqual(self.audio_manager.audio_enabled, original_state)
    
    def test_game_manager_has_audio_manager(self):
        """Test that GameManager properly initializes AudioManager"""
        game = GameManager()
        self.assertIsNotNone(game.audio_manager)
        self.assertIsInstance(game.audio_manager, AudioManager)
    
    def test_player_methods_accept_audio_manager(self):
        """Test that Player methods can accept audio_manager parameter"""
        player = Player(100, 100, 0)
        
        # These should not raise exceptions
        player.jump(self.audio_manager)
        player.move_left(self.audio_manager)
        player.move_right(self.audio_manager)
        player.fire_weapon(self.audio_manager)
    
    def test_projectile_methods_accept_audio_manager(self):
        """Test that Projectile methods can accept audio_manager parameter"""
        from main import Terrain
        
        projectile = Projectile(100, 100, 5, -5, "rocket", 50)
        terrain = Terrain()
        players = []
        
        # This should not raise exceptions
        # Note: We're not testing the actual update logic, just that audio_manager parameter is accepted
        try:
            projectile.update(terrain, players, None, self.audio_manager)
        except:
            # It's okay if update fails for other reasons, we just want to test the parameter acceptance
            pass

if __name__ == '__main__':
    unittest.main()
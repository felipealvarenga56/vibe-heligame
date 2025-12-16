# 🏖️ Vibe-Heligame: Retro Beach Artillery

A retro-styled beach artillery game inspired by Worms Armageddon, featuring destructible terrain, dynamic weather effects, and authentic 8-bit audio. Built with Python and Pygame following classic game development principles.

## 🎮 Game Features

### Core Gameplay
- **Turn-based Artillery Combat**: Two players battle with various weapons
- **Destructible Terrain**: Pixel-perfect crater creation and merging
- **Dynamic Weapon System**: Rocket launchers, banana bombs, and melee attacks
- **Power-based Shooting**: Charge up shots for increased range and damage

### Visual Effects
- **Sunrise Beach Theme**: Authentic coastal color palette (#FAD7A0, #D6EAF8, #E8F8F5)
- **Particle Systems**: Weapon trails, explosions, and environmental effects
- **Procedural Terrain**: Hills and valleys with realistic slope physics
- **Retro Sprite Art**: 8-bit style characters and animations

### Audio System
- **Authentic 8-bit Sounds**: Procedurally generated retro audio
- **Weapon-specific Audio**: Distinct sounds for each weapon type
- **Environmental Audio**: Terrain destruction and movement feedback
- **Dynamic Volume Control**: Adjustable audio settings

## 🕹️ Controls

| Key | Action |
|-----|--------|
| **WASD** | Move and aim |
| **Space** | Jump |
| **Enter** | Charge power (hold) / Fire (release) |
| **1/2/3** | Switch weapons (Rocket/Banana/Melee) |
| **F1** | Toggle audio on/off |
| **F2** | Cycle visual effects intensity |
| **F3** | Cycle terrain complexity |
| **ESC** | Exit game |

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- Pygame 2.0+

### Installation
```bash
# Clone or download the project
cd vibe-heligame

# Install dependencies
pip install pygame

# Generate audio files (optional)
python create_basic_sounds.py

# Run the game
python main.py
```

## 📁 Project Structure

```
vibe-heligame/
├── main.py                    # Main game file
├── run_tests.py              # Test runner script
├── create_basic_sounds.py    # Audio generation utility
├── generate_sounds.py        # Advanced audio generator
├── game_settings.json        # Persistent game settings
├── sounds/                   # Generated audio files
├── tests/                    # Test suite
│   ├── test_crater_creation.py
│   ├── test_crater_merging.py
│   ├── test_terrain_collision.py
│   ├── test_weapon_visuals.py
│   ├── test_audio_integration.py
│   ├── test_terrain_generation.py
│   ├── test_sloped_terrain_physics.py
│   └── README.md
└── README.md                 # This file
```

## 🧪 Testing

### Run All Tests
```bash
python run_tests.py
```

### Run Specific Tests
```bash
python run_tests.py crater_creation
python run_tests.py audio_integration
```

### Test Coverage
- Property-based testing with Hypothesis (optional)
- Crater creation and merging validation
- Terrain physics accuracy
- Audio system integration
- Visual effects scaling

## ⚙️ Game Settings

Settings are automatically saved to `game_settings.json`:

```json
{
  "audio": {
    "master_volume": 0.7,
    "sfx_volume": 0.8,
    "audio_enabled": true
  },
  "visual_effects": {
    "particle_intensity": 1.0,
    "explosion_intensity": 1.0,
    "trail_intensity": 1.0
  },
  "terrain": {
    "complexity": 1.0,
    "destructible_terrain": true,
    "varied_terrain": true
  }
}
```

## 🎨 Retro Design Philosophy

This game follows authentic 8-bit development principles:

### Color Palette
- **Limited Colors**: Sunrise beach theme with carefully chosen hex values
- **Palette Consistency**: All sprites use the same color scheme
- **High Contrast**: Clear visual hierarchy for gameplay elements

### Audio Design
- **Procedural Generation**: Mathematical waveforms instead of samples
- **Channel Limitations**: Simple sine waves and envelopes
- **Memory Efficiency**: Minimal audio footprint

### Performance
- **60 FPS Target**: Smooth gameplay on modest hardware
- **Efficient Rendering**: Chunked terrain drawing for performance
- **Memory Management**: Object pooling for particles and effects

## 🏗️ Technical Architecture

### Core Systems
- **GameManager**: Main game loop and state management
- **TerrainMap**: Pixel-based destructible terrain system
- **EffectsManager**: Centralized particle and visual effects
- **AudioManager**: Sound generation and playback
- **GameSettings**: Persistent configuration management

### Physics Engine
- **Gravity Simulation**: Realistic projectile arcs
- **Slope Physics**: Movement affected by terrain angles
- **Collision Detection**: Pixel-perfect terrain interaction
- **Crater Merging**: Overlapping explosion handling

## 🎯 Gameplay Balance

### Weapons
- **Rocket**: Fast, precise, moderate damage
- **Banana**: Timed explosive, large blast radius
- **Melee**: Close range, quick firing

### Terrain
- **Destructible**: All terrain can be destroyed
- **Procedural**: Varied landscapes each game
- **Accessible**: All areas remain playable

## 🔧 Development

### Adding New Weapons
1. Add weapon type to `Projectile` class
2. Implement visual effects in `draw()` method
3. Add audio in `AudioManager`
4. Create tests for new weapon behavior

### Extending Terrain
1. Modify `TerrainGenerator` for new patterns
2. Update `TerrainMap` for new collision types
3. Add tests for terrain generation quality

## 📜 License

This project is created for educational purposes, demonstrating retro game development techniques and modern testing practices.

## 🎮 Credits

Inspired by classic artillery games like Worms Armageddon, built with modern Python tools while maintaining authentic 8-bit aesthetics and gameplay feel.

---

*Ready to blast some craters in paradise? Fire up the game and let the beach artillery battle begin!* 🚀🏖️
# Test Suite for Vibe-Heligame

This directory contains comprehensive property-based tests for the retro beach artillery game.

## Test Files

### Core System Tests
- `test_crater_creation.py` - Tests crater creation and terrain destruction (Property 1)
- `test_crater_merging.py` - Tests crater merging behavior (Property 2)  
- `test_terrain_collision.py` - Tests modified terrain collision accuracy (Property 3)

### Visual & Audio Tests
- `test_weapon_visuals.py` - Tests weapon-specific visual effects (Property 4)
- `test_audio_integration.py` - Tests audio system integration

### Terrain Generation Tests
- `test_terrain_generation.py` - Tests terrain generation quality (Property 6)
- `test_sloped_terrain_physics.py` - Tests sloped terrain physics accuracy (Property 7)

## Running Tests

### Run All Tests
```bash
python run_tests.py
```

### Run Specific Test
```bash
python run_tests.py crater_creation
python run_tests.py audio_integration
python run_tests.py terrain_generation
```

### Run Individual Test File
```bash
python tests/test_crater_creation.py
```

## Test Framework

The tests use Python's built-in `unittest` framework with optional `hypothesis` for property-based testing. If hypothesis is not available, property tests are skipped but basic tests still run.

### Installing Hypothesis (Optional)
```bash
pip install hypothesis
```

## Test Coverage

The test suite validates:
- ✅ Crater creation and destruction patterns
- ✅ Crater merging algorithms  
- ✅ Terrain collision detection accuracy
- ✅ Weapon visual effects scaling
- ✅ Audio system integration
- ✅ Procedural terrain generation
- ✅ Sloped terrain physics

All tests are designed to work with the retro game's constraints and validate both functionality and performance characteristics suitable for 8-bit style gameplay.
#!/usr/bin/env python3
"""
Generate basic retro-style sound effects for the game
Pure pygame implementation - no numpy required!
"""

import pygame
import os
import math
import random

def generate_sound_wave(frequency, duration, sample_rate=22050, wave_type='sine'):
    """Generate a basic waveform using pure Python"""
    frames = int(duration * sample_rate)
    arr = []
    
    for i in range(frames):
        t = float(i) / sample_rate
        if wave_type == 'sine':
            sample = math.sin(2 * math.pi * frequency * t)
        elif wave_type == 'square':
            sample = 1 if math.sin(2 * math.pi * frequency * t) > 0 else -1
        elif wave_type == 'sawtooth':
            sample = 2 * (t * frequency - math.floor(t * frequency + 0.5))
        elif wave_type == 'noise':
            sample = random.uniform(-1, 1)
        else:
            sample = 0
        
        arr.append(sample)
    
    return arr

def apply_envelope(arr, attack=0.1, decay=0.1, sustain=0.7, release=0.2):
    """Apply ADSR envelope to sound"""
    frames = len(arr)
    
    attack_frames = int(attack * frames)
    decay_frames = int(decay * frames)
    release_frames = int(release * frames)
    sustain_frames = frames - attack_frames - decay_frames - release_frames
    
    result = []
    
    for i in range(frames):
        envelope_value = 1.0
        
        if i < attack_frames:
            # Attack phase
            envelope_value = i / attack_frames
        elif i < attack_frames + decay_frames:
            # Decay phase
            decay_progress = (i - attack_frames) / decay_frames
            envelope_value = 1 - (1 - sustain) * decay_progress
        elif i < attack_frames + decay_frames + sustain_frames:
            # Sustain phase
            envelope_value = sustain
        else:
            # Release phase
            release_progress = (i - attack_frames - decay_frames - sustain_frames) / release_frames
            envelope_value = sustain * (1 - release_progress)
        
        result.append(arr[i] * envelope_value)
    
    return result

def create_explosion_sound(base_freq=100, duration=0.8):
    """Create explosion sound with noise and frequency sweep"""
    sample_rate = 22050
    frames = int(duration * sample_rate)
    
    # Start with noise
    noise = generate_sound_wave(0, duration, sample_rate, 'noise')
    noise = [n * 0.3 for n in noise]
    
    # Add frequency sweep (high to low)
    sweep = []
    for i in range(frames):
        t = float(i) / sample_rate
        freq = base_freq * math.exp(-t * 3)  # Exponential decay
        sample = math.sin(2 * math.pi * freq * t) * 0.7
        sweep.append(sample)
    
    # Combine noise and sweep
    sound = [noise[i] + sweep[i] for i in range(frames)]
    sound = apply_envelope(sound, attack=0.01, decay=0.1, sustain=0.3, release=0.6)
    
    return sound

def create_firing_sound(base_freq=440, duration=0.2):
    """Create weapon firing sound"""
    # Quick attack with harmonics
    fundamental = generate_sound_wave(base_freq, duration, 22050, 'sine')
    harmonic2 = generate_sound_wave(base_freq * 2, duration, 22050, 'sine')
    harmonic3 = generate_sound_wave(base_freq * 3, duration, 22050, 'sine')
    
    # Mix harmonics
    sound = []
    for i in range(len(fundamental)):
        mixed = (fundamental[i] + 
                harmonic2[i] * 0.3 + 
                harmonic3[i] * 0.1)
        sound.append(mixed)
    
    sound = apply_envelope(sound, attack=0.01, decay=0.3, sustain=0.2, release=0.4)
    
    return sound

def create_jump_sound(base_freq=400, duration=0.15):
    """Create jumping sound with frequency rise"""
    sample_rate = 22050
    frames = int(duration * sample_rate)
    
    sound = []
    for i in range(frames):
        t = float(i) / sample_rate
        freq = base_freq * (1 + t * 2)  # Rising frequency
        sample = math.sin(2 * math.pi * freq * t)
        sound.append(sample)
    
    sound = apply_envelope(sound, attack=0.01, decay=0.2, sustain=0.3, release=0.4)
    return sound

def create_power_charge_sound(base_freq=500, duration=0.1):
    """Create power charging sound"""
    sample_rate = 22050
    frames = int(duration * sample_rate)
    
    sound = []
    for i in range(frames):
        t = float(i) / sample_rate
        freq = base_freq * (1 + t * 0.5)  # Slight rise
        sample = math.sin(2 * math.pi * freq * t)
        sound.append(sample)
    
    sound = apply_envelope(sound, attack=0.02, decay=0.1, sustain=0.8, release=0.1)
    return sound

def save_sound(sound_array, filename, sample_rate=22050):
    """Save sound array as WAV file"""
    # Normalize sound
    max_val = max(abs(s) for s in sound_array)
    if max_val > 0:
        sound_array = [s / max_val for s in sound_array]
    
    # Convert to 16-bit integers
    sound_16bit = [int(s * 32767) for s in sound_array]
    
    # Make stereo (duplicate mono to both channels)
    stereo_array = []
    for sample in sound_16bit:
        stereo_array.append([sample, sample])
    
    # Ensure sounds directory exists
    os.makedirs("sounds", exist_ok=True)
    
    # Create pygame sound
    try:
        sound = pygame.sndarray.make_sound(stereo_array)
        
        # Save as WAV file using pygame
        filepath = os.path.join("sounds", filename)
        
        # Simple WAV file creation
        import wave
        import struct
        
        with wave.open(filepath, 'w') as wav_file:
            wav_file.setnchannels(2)  # Stereo
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            
            # Write audio data
            for sample_pair in stereo_array:
                wav_file.writeframes(struct.pack('<hh', sample_pair[0], sample_pair[1]))
        
        print(f"Created: {filepath}")
        
    except Exception as e:
        print(f"Error creating {filename}: {e}")

def main():
    """Generate all game sound effects"""
    pygame.init()
    pygame.mixer.init()
    
    print("Generating retro sound effects...")
    print("This might take a moment - creating authentic 8-bit style audio!")
    
    # Weapon firing sounds
    print("Creating weapon sounds...")
    save_sound(create_firing_sound(440, 0.2), "rocket_fire.wav")
    save_sound(create_firing_sound(330, 0.15), "banana_fire.wav")
    save_sound(create_firing_sound(220, 0.1), "melee_fire.wav")
    
    # Explosion sounds
    print("Creating explosion sounds...")
    save_sound(create_explosion_sound(150, 0.8), "rocket_explosion.wav")
    save_sound(create_explosion_sound(120, 1.0), "banana_explosion.wav")
    save_sound(create_explosion_sound(180, 0.6), "melee_explosion.wav")
    
    # Movement sounds
    print("Creating movement sounds...")
    save_sound(create_jump_sound(400, 0.15), "player_jump.wav")
    save_sound(create_firing_sound(200, 0.1), "player_land.wav")
    save_sound(create_firing_sound(300, 0.05), "player_move.wav")
    
    # Power sounds
    print("Creating power sounds...")
    save_sound(create_power_charge_sound(500, 0.1), "power_charge.wav")
    save_sound(create_firing_sound(600, 0.2), "power_release.wav")
    
    # Destruction sounds
    print("Creating destruction sounds...")
    save_sound(create_explosion_sound(100, 0.5), "terrain_destroy.wav")
    save_sound(create_firing_sound(250, 0.3), "tree_destroy.wav")
    
    print("\n🎵 All sound effects generated successfully!")
    print("🎮 You can now run the game with full retro audio!")
    print("🔊 Press F1 in-game to toggle audio on/off")

if __name__ == "__main__":
    main()
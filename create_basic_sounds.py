#!/usr/bin/env python3
"""
Create basic sound files for the game using pure Python
No external dependencies - just like the old days!
"""

import wave
import struct
import math
import os

def create_simple_beep(frequency, duration, sample_rate=22050, volume=0.5):
    """Create a simple sine wave beep"""
    frames = int(duration * sample_rate)
    
    # Generate sine wave
    audio_data = []
    for i in range(frames):
        t = float(i) / sample_rate
        # Simple envelope to avoid clicks
        envelope = 1.0
        if i < sample_rate * 0.01:  # 10ms attack
            envelope = i / (sample_rate * 0.01)
        elif i > frames - sample_rate * 0.01:  # 10ms release
            envelope = (frames - i) / (sample_rate * 0.01)
        
        sample = math.sin(2 * math.pi * frequency * t) * volume * envelope
        # Convert to 16-bit integer
        sample_int = int(sample * 32767)
        # Stereo (same sample for both channels)
        audio_data.append(struct.pack('<hh', sample_int, sample_int))
    
    return b''.join(audio_data)

def create_explosion_sound(duration=0.5, sample_rate=22050, volume=0.3):
    """Create explosion sound using frequency sweep and noise"""
    frames = int(duration * sample_rate)
    
    audio_data = []
    for i in range(frames):
        t = float(i) / sample_rate
        
        # Frequency sweep from high to low
        freq = 200 * math.exp(-t * 4)
        
        # Add some harmonics and noise
        sample = (math.sin(2 * math.pi * freq * t) * 0.7 +
                 math.sin(2 * math.pi * freq * 2 * t) * 0.2 +
                 (hash(i) % 1000 - 500) / 1000.0 * 0.1)  # Simple noise
        
        # Envelope (quick attack, long decay)
        envelope = math.exp(-t * 2)
        sample *= envelope * volume
        
        # Convert to 16-bit integer
        sample_int = int(max(-32767, min(32767, sample * 32767)))
        # Stereo
        audio_data.append(struct.pack('<hh', sample_int, sample_int))
    
    return b''.join(audio_data)

def create_jump_sound(duration=0.15, sample_rate=22050, volume=0.4):
    """Create jump sound with rising frequency"""
    frames = int(duration * sample_rate)
    
    audio_data = []
    for i in range(frames):
        t = float(i) / sample_rate
        
        # Rising frequency
        freq = 300 + t * 400
        
        sample = math.sin(2 * math.pi * freq * t)
        
        # Quick envelope
        envelope = math.exp(-t * 8)
        sample *= envelope * volume
        
        # Convert to 16-bit integer
        sample_int = int(max(-32767, min(32767, sample * 32767)))
        # Stereo
        audio_data.append(struct.pack('<hh', sample_int, sample_int))
    
    return b''.join(audio_data)

def save_wav_file(audio_data, filename, sample_rate=22050):
    """Save audio data as WAV file"""
    os.makedirs("sounds", exist_ok=True)
    filepath = os.path.join("sounds", filename)
    
    with wave.open(filepath, 'w') as wav_file:
        wav_file.setnchannels(2)  # Stereo
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data)
    
    print(f"Created: {filepath}")

def main():
    """Create all basic sound effects"""
    print("Creating basic retro sound effects...")
    print("Using pure Python - no dependencies needed!")
    
    # Weapon firing sounds (different frequencies)
    print("Creating weapon sounds...")
    save_wav_file(create_simple_beep(440, 0.2, volume=0.6), "rocket_fire.wav")
    save_wav_file(create_simple_beep(330, 0.15, volume=0.5), "banana_fire.wav")
    save_wav_file(create_simple_beep(220, 0.1, volume=0.4), "melee_fire.wav")
    
    # Explosion sounds
    print("Creating explosion sounds...")
    save_wav_file(create_explosion_sound(0.8, volume=0.4), "rocket_explosion.wav")
    save_wav_file(create_explosion_sound(1.0, volume=0.5), "banana_explosion.wav")
    save_wav_file(create_explosion_sound(0.6, volume=0.3), "melee_explosion.wav")
    
    # Movement sounds
    print("Creating movement sounds...")
    save_wav_file(create_jump_sound(0.15, volume=0.3), "player_jump.wav")
    save_wav_file(create_simple_beep(200, 0.1, volume=0.2), "player_land.wav")
    save_wav_file(create_simple_beep(300, 0.05, volume=0.1), "player_move.wav")
    
    # Power sounds
    print("Creating power sounds...")
    save_wav_file(create_simple_beep(500, 0.1, volume=0.3), "power_charge.wav")
    save_wav_file(create_simple_beep(600, 0.2, volume=0.4), "power_release.wav")
    
    # Destruction sounds
    print("Creating destruction sounds...")
    save_wav_file(create_explosion_sound(0.5, volume=0.3), "terrain_destroy.wav")
    save_wav_file(create_simple_beep(250, 0.3, volume=0.3), "tree_destroy.wav")
    
    print("\n🎵 Basic sound effects created successfully!")
    print("🎮 Run the game now to hear the retro audio!")
    print("🔊 Use F1 to toggle audio, F2 for effects, F3 for terrain settings")

if __name__ == "__main__":
    main()
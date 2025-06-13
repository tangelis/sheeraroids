"""
Audio system for game sounds and music
"""
import pygame
import numpy as np
import os
from constants import assets_dir

# Load shooting sound
def load_shoot_sound():
    """Load the bark shooting sound"""
    try:
        shoot_sound = pygame.mixer.Sound(os.path.join(assets_dir, "bark_shoot_converted.wav"))
        shoot_sound.set_volume(0.5)
        return shoot_sound
    except:
        print("Could not load bark shoot converted.wav")
        return None

def create_explosion_sound(duration=1.0, sample_rate=22050):
    """Create a digital explosion sound effect using numpy"""
    try:
        frames = int(duration * sample_rate)
        
        # Create multiple noise layers
        white_noise = np.random.normal(0, 0.3, frames)
        
        # Low frequency rumble
        time = np.linspace(0, duration, frames)
        low_freq = np.sin(2 * np.pi * 40 * time) * 0.5
        low_freq2 = np.sin(2 * np.pi * 60 * time) * 0.3
        
        # Envelope that starts loud and fades out exponentially
        envelope = np.exp(-time * 5)
        
        # Add some "crackle" with rapid oscillations
        crackle = np.sin(2 * np.pi * 150 * time) * 0.2 * (time < 0.1)
        
        # Combine all components
        explosion = (white_noise + low_freq + low_freq2 + crackle) * envelope
        
        # Add initial "punch" 
        punch_duration = 0.05
        punch_frames = int(punch_duration * sample_rate)
        punch = np.sin(2 * np.pi * 80 * time[:punch_frames]) * 2
        explosion[:punch_frames] += punch * np.exp(-time[:punch_frames] * 20)
        
        # Normalize and convert to 16-bit
        explosion = np.clip(explosion, -1, 1)
        explosion = (explosion * 32767).astype(np.int16)
        
        # Convert to stereo
        stereo_explosion = np.zeros((frames, 2), dtype=np.int16)
        stereo_explosion[:, 0] = explosion
        stereo_explosion[:, 1] = explosion
        
        return pygame.sndarray.make_sound(stereo_explosion)
    except Exception as e:
        print(f"Could not create explosion sound: {e}")
        return None

def create_80s_death_sound(duration=2.0, sample_rate=22050):
    """Create an 80s-style death sound effect"""
    try:
        frames = int(duration * sample_rate)
        time = np.linspace(0, duration, frames)
        
        # 80s synth bass drop - starts high and drops down
        start_freq = 800
        end_freq = 60
        freq_sweep = start_freq * np.exp(-time * 2.5) + end_freq
        
        # Main synth wave with frequency sweep
        synth_wave = np.sin(2 * np.pi * freq_sweep * time)
        
        # Add some harmonics for richer sound
        harmonic1 = 0.3 * np.sin(2 * np.pi * freq_sweep * 2 * time)
        harmonic2 = 0.2 * np.sin(2 * np.pi * freq_sweep * 0.5 * time)
        
        # 80s style envelope - quick attack, sustained, then fade
        envelope = np.ones_like(time)
        fade_start = int(frames * 0.7)
        envelope[fade_start:] = np.linspace(1, 0, frames - fade_start)
        
        # Add some retro "digital" artifacts
        digital_noise = 0.1 * np.random.choice([-1, 1], frames) * np.exp(-time * 2)
        
        # Combine all elements
        sound_80s = (synth_wave + harmonic1 + harmonic2 + digital_noise) * envelope
        
        # Add some "gated" effect (80s style)
        gate_freq = 8  # Hz
        gate_wave = (np.sin(2 * np.pi * gate_freq * time) + 1) / 2
        gate_wave = np.where(gate_wave > 0.5, 1, 0.3)
        
        # Apply gate only in middle section
        gate_start = int(frames * 0.2)
        gate_end = int(frames * 0.6)
        sound_80s[gate_start:gate_end] *= gate_wave[gate_start:gate_end]
        
        # Normalize and convert to 16-bit
        sound_80s = np.clip(sound_80s, -1, 1)
        sound_80s = (sound_80s * 32767).astype(np.int16)
        
        # Convert to stereo with slight delay for width
        stereo_sound = np.zeros((frames, 2), dtype=np.int16)
        stereo_sound[:, 0] = sound_80s
        delay_samples = int(0.002 * sample_rate)
        stereo_sound[delay_samples:, 1] = sound_80s[:-delay_samples]
        
        return pygame.sndarray.make_sound(stereo_sound)
    except Exception as e:
        print(f"Could not create 80s death sound: {e}")
        return None

def create_80s_transition_music(duration=5.0, sample_rate=22050):
    """Create 80s-style transition music for game over sequence"""
    try:
        frames = int(duration * sample_rate)
        time = np.linspace(0, duration, frames)
        
        # Main synth pad chord progression (Am - F - C - G)
        chord_duration = duration / 4
        
        # Frequencies for chords
        am_freqs = [220, 261.63, 329.63]
        f_freqs = [174.61, 220, 261.63]
        c_freqs = [261.63, 329.63, 392]
        g_freqs = [196, 246.94, 293.66]
        
        chord_progression = [am_freqs, f_freqs, c_freqs, g_freqs]
        
        # Create the main synth pad
        synth_pad = np.zeros(frames)
        
        for chord_idx, chord in enumerate(chord_progression):
            start_frame = int(chord_idx * chord_duration * sample_rate)
            end_frame = int((chord_idx + 1) * chord_duration * sample_rate)
            
            if end_frame > frames:
                end_frame = frames
            
            chord_time = time[start_frame:end_frame]
            chord_samples = np.zeros(len(chord_time))
            
            # Add each note in the chord
            for freq in chord:
                chord_samples += 0.3 * np.sin(2 * np.pi * freq * chord_time)
                chord_samples += 0.1 * np.sin(2 * np.pi * (freq * 1.005) * chord_time)
                chord_samples += 0.15 * np.sin(2 * np.pi * (freq * 0.5) * chord_time)
            
            synth_pad[start_frame:end_frame] = chord_samples
        
        # Add 80s style arpeggio
        arp_notes = [220, 261.63, 329.63, 392, 329.63, 261.63]
        arp_beat_duration = 0.2
        arpeggio = np.zeros(frames)
        
        for i, freq in enumerate(arp_notes * 4):
            start_time = i * arp_beat_duration
            if start_time >= duration:
                break
            
            start_frame = int(start_time * sample_rate)
            end_frame = int((start_time + arp_beat_duration) * sample_rate)
            
            if end_frame > frames:
                end_frame = frames
            
            note_time = time[start_frame:end_frame]
            envelope = np.exp(-note_time[note_time >= start_time] * 8)
            if len(envelope) > 0:
                note_samples = 0.2 * np.sin(2 * np.pi * freq * note_time[note_time >= start_time]) * envelope
                if len(note_samples) <= len(arpeggio[start_frame:end_frame]):
                    arpeggio[start_frame:start_frame + len(note_samples)] += note_samples
        
        # Add bass line
        bass_notes = [110, 87.31, 130.81, 98]
        bassline = np.zeros(frames)
        
        for i, freq in enumerate(bass_notes):
            start_frame = int(i * chord_duration * sample_rate)
            end_frame = int((i + 1) * chord_duration * sample_rate)
            
            if end_frame > frames:
                end_frame = frames
            
            bass_time = time[start_frame:end_frame]
            bass_wave = np.sign(np.sin(2 * np.pi * freq * bass_time)) * 0.3
            bassline[start_frame:end_frame] = bass_wave
        
        # Combine all elements
        final_music = synth_pad + arpeggio + bassline
        
        # Add overall envelope
        fade_in_frames = int(0.5 * sample_rate)
        fade_out_frames = int(1.0 * sample_rate)
        
        final_music[:fade_in_frames] *= np.linspace(0, 1, fade_in_frames)
        final_music[-fade_out_frames:] *= np.linspace(1, 0, fade_out_frames)
        
        # Normalize and convert to 16-bit
        final_music = np.clip(final_music, -1, 1)
        final_music = (final_music * 32767).astype(np.int16)
        
        # Convert to stereo
        stereo_music = np.zeros((frames, 2), dtype=np.int16)
        stereo_music[:, 0] = final_music
        stereo_music[:, 1] = final_music
        
        return pygame.sndarray.make_sound(stereo_music)
    except Exception as e:
        print(f"Could not create 80s transition music: {e}")
        return None

def load_all_sounds():
    """Load all game sounds"""
    shoot_sound = load_shoot_sound()
    explosion_sound = create_explosion_sound()
    if explosion_sound:
        explosion_sound.set_volume(0.7)
    
    death_sound_80s = create_80s_death_sound()
    if death_sound_80s:
        death_sound_80s.set_volume(0.6)
    
    transition_music_80s = create_80s_transition_music()
    if transition_music_80s:
        transition_music_80s.set_volume(0.5)
    
    return shoot_sound, explosion_sound, death_sound_80s, transition_music_80s
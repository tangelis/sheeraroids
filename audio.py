"""
Audio system for game sounds and music
"""
import pygame
import numpy as np
import os
import random
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

def create_explosion_sound(duration=0.3, sample_rate=22050):
    """Create a sharp, punchy first explosion sound (80s arcade style)"""
    try:
        frames = int(duration * sample_rate)
        time = np.linspace(0, duration, frames)
        
        # Sharp white noise burst
        white_noise = np.random.normal(0, 0.8, frames)
        
        # High frequency sweep for sharpness
        freq_sweep = 1000 * np.exp(-time * 15)  # Fast drop from 1000Hz
        sweep = np.sin(2 * np.pi * freq_sweep * time)
        
        # Quick punch
        punch_env = np.exp(-time * 30)  # Very fast decay
        
        # Combine with emphasis on high frequencies
        explosion = (white_noise * 0.7 + sweep * 0.3) * punch_env
        
        # Add click at start for extra punch
        click_frames = int(0.002 * sample_rate)
        explosion[:click_frames] = 0.9
        
        # Normalize and convert
        explosion = np.clip(explosion, -1, 1)
        explosion = (explosion * 32767).astype(np.int16)
        
        # Stereo
        stereo = np.zeros((frames, 2), dtype=np.int16)
        stereo[:, 0] = explosion
        stereo[:, 1] = explosion
        
        return pygame.sndarray.make_sound(stereo)
    except Exception as e:
        print(f"Could not create explosion sound: {e}")
        return None

def create_explosion_sound_2(duration=0.5, sample_rate=22050):
    """Create a deeper, bigger second explosion sound (80s arcade style)"""
    try:
        frames = int(duration * sample_rate)
        time = np.linspace(0, duration, frames)
        
        # Deeper noise with more bass
        white_noise = np.random.normal(0, 0.6, frames)
        brown_noise = np.cumsum(np.random.normal(0, 0.1, frames))  # Brownian noise
        brown_noise = brown_noise / np.max(np.abs(brown_noise))  # Normalize
        
        # Low frequency rumble
        rumble1 = np.sin(2 * np.pi * 40 * time) * 0.8
        rumble2 = np.sin(2 * np.pi * 60 * time) * 0.6
        rumble3 = np.sin(2 * np.pi * 30 * time) * 0.4
        
        # Slower frequency sweep
        freq_sweep = 500 * np.exp(-time * 5)  # Slower drop from 500Hz
        sweep = np.sign(np.sin(2 * np.pi * freq_sweep * time))  # Square wave
        
        # Longer envelope with sustain
        envelope = np.ones_like(time)
        envelope[:int(0.1 * sample_rate)] = np.linspace(0, 1, int(0.1 * sample_rate))  # Attack
        envelope[int(0.2 * sample_rate):] = np.exp(-time[int(0.2 * sample_rate):] * 3)  # Decay
        
        # Combine with emphasis on low frequencies
        explosion = (white_noise * 0.3 + brown_noise * 0.3 + 
                    rumble1 + rumble2 + rumble3 + sweep * 0.2) * envelope
        
        # Add sub-bass thump
        thump = np.sin(2 * np.pi * 25 * time) * np.exp(-time * 10)
        explosion += thump * 0.5
        
        # Normalize and add compression
        explosion = np.tanh(explosion * 0.7)
        explosion = (explosion * 32767 * 0.9).astype(np.int16)
        
        # Stereo with slight delay for width
        stereo = np.zeros((frames, 2), dtype=np.int16)
        stereo[:, 0] = explosion
        delay = int(0.005 * sample_rate)
        stereo[delay:, 1] = explosion[:-delay]
        
        return pygame.sndarray.make_sound(stereo)
    except Exception as e:
        print(f"Could not create explosion sound 2: {e}")
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

def create_particle_shrinking_sound(duration=3.0, sample_rate=22050):
    """Create 80s arcade particle shrinking/fading sound effect"""
    try:
        frames = int(duration * sample_rate)
        time = np.linspace(0, duration, frames)
        sound = np.zeros(frames)
        
        # Multiple high-frequency sine waves that descend and fade
        # Like Defender or Asteroids particle dispersal
        num_particles = 8
        
        for i in range(num_particles):
            # Each particle starts at a different time
            particle_delay = i * 0.1
            particle_start = int(particle_delay * sample_rate)
            
            if particle_start < frames:
                particle_time = time[particle_start:]
                particle_frames = len(particle_time)
                
                # Frequency starts high and drops exponentially (shrinking effect)
                start_freq = 2000 + i * 200  # Each particle slightly different
                freq_decay = np.exp(-particle_time * 2)  # Exponential frequency drop
                particle_freq = start_freq * freq_decay + 100  # Minimum frequency
                
                # Create the shrinking sound - sine wave with frequency modulation
                particle_sound = np.sin(2 * np.pi * particle_freq * particle_time)
                
                # Add some flutter/warble for that analog feel
                flutter_rate = 20 + i * 2
                flutter = 1 + 0.1 * np.sin(2 * np.pi * flutter_rate * particle_time)
                particle_sound *= flutter
                
                # Volume envelope - quick attack, slow exponential decay (shrinking)
                attack_frames = int(0.02 * sample_rate)
                envelope = np.ones(particle_frames)
                if attack_frames < particle_frames:
                    envelope[:attack_frames] = np.linspace(0, 1, attack_frames)
                # Exponential decay for shrinking effect
                decay_start = attack_frames
                envelope[decay_start:] = np.exp(-particle_time[decay_start:] * (1.5 + i * 0.1))
                
                # Apply envelope
                particle_sound *= envelope
                
                # Add filtered white noise for texture (like pixel breakup)
                noise = np.random.normal(0, 0.05, particle_frames)
                # Simple low-pass filter simulation
                filtered_noise = np.convolve(noise, np.ones(5)/5, mode='same')
                particle_sound += filtered_noise * envelope * 0.3
                
                # Stereo positioning - particles spread across stereo field
                left_gain = 0.5 + 0.5 * np.cos(i * np.pi / num_particles)
                right_gain = 0.5 + 0.5 * np.sin(i * np.pi / num_particles)
                
                # Add to main sound
                sound[particle_start:] += particle_sound * 0.4
        
        # Add subtle ring modulation for that classic 80s digital sound
        ring_freq = 500
        ring_mod = np.sin(2 * np.pi * ring_freq * time)
        sound = sound * (1 + 0.3 * ring_mod)
        
        # Final high-pass filter effect (emphasize the shrinking)
        # Simple differencing as high-pass
        hp_sound = np.diff(sound, prepend=sound[0])
        sound = sound * 0.7 + hp_sound * 0.3
        
        # Normalize and clip
        sound = np.clip(sound, -1, 1)
        sound = (sound * 32767 * 0.6).astype(np.int16)
        
        # Create stereo with particle spread
        stereo_sound = np.zeros((frames, 2), dtype=np.int16)
        # Base sound in both channels
        stereo_sound[:, 0] = sound
        stereo_sound[:, 1] = sound
        
        # Add stereo width with slight delays
        for i in range(num_particles):
            delay = int((0.005 + i * 0.002) * sample_rate)
            if delay < frames:
                if i % 2 == 0:
                    stereo_sound[delay:, 0] += sound[:-delay] // (i + 2)
                else:
                    stereo_sound[delay:, 1] += sound[:-delay] // (i + 2)
        
        return pygame.sndarray.make_sound(stereo_sound)
    except Exception as e:
        print(f"Could not create particle shrinking sound: {e}")
        return None

def create_final_death_sound_80s(duration=0.5, sample_rate=22050):
    """Create a SHORT explosive 80s arcade death sound"""
    try:
        frames = int(duration * sample_rate)
        time = np.linspace(0, duration, frames)
        
        # Big initial explosion - white noise burst
        explosion = np.random.normal(0, 1.0, frames)
        
        # Add low frequency thump
        thump_freq = 50 * np.exp(-time * 10)  # Rapidly dropping frequency
        thump = np.sin(2 * np.pi * thump_freq * time) * 2
        
        # Square wave blast
        blast_freq = 200 * np.exp(-time * 8)
        blast = np.sign(np.sin(2 * np.pi * blast_freq * time))
        
        # Combine
        sound = explosion + thump + blast * 0.5
        
        # Sharp envelope - immediate attack, quick decay
        envelope = np.exp(-time * 15)
        sound *= envelope
        
        # Add some crunch
        sound = np.sign(sound) * np.power(np.abs(sound), 0.7)
        
        # Normalize
        sound = np.clip(sound, -1, 1)
        sound = (sound * 32767 * 0.9).astype(np.int16)
        
        stereo = np.stack([sound, sound], axis=-1)
        return pygame.sndarray.make_sound(stereo)
    except Exception as e:
        print(f"Could not create final death sound: {e}")
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

def create_game_over_music(duration=10.0, sample_rate=22050):
    """Create dramatic 80s game over screen music"""
    try:
        frames = int(duration * sample_rate)
        time = np.linspace(0, duration, frames)
        music = np.zeros(frames)
        
        # Slow, dramatic bass line
        bass_pattern = [55, 58.27, 61.74, 65.41]  # A, Bb, B, C
        bass_duration = 2.0
        
        for i, freq in enumerate(bass_pattern * 3):
            start = i * bass_duration
            if start >= duration:
                break
            start_frame = int(start * sample_rate)
            end_frame = int((start + bass_duration) * sample_rate)
            if end_frame > frames:
                end_frame = frames
            
            bass_time = time[start_frame:end_frame]
            # Deep synth bass
            bass = np.sin(2 * np.pi * freq * bass_time)
            bass += 0.3 * np.sin(2 * np.pi * freq * 0.5 * bass_time)  # Sub bass
            envelope = np.ones(len(bass_time))
            envelope[:100] = np.linspace(0, 1, min(100, len(envelope)))
            envelope[-500:] = np.linspace(1, 0, min(500, len(envelope)))
            
            music[start_frame:end_frame] += bass * envelope * 0.5
        
        # Add dramatic pad chords
        chord_times = np.arange(0, duration, 2.0)
        for chord_time in chord_times:
            start_frame = int(chord_time * sample_rate)
            chord_duration = int(2.0 * sample_rate)
            if start_frame + chord_duration > frames:
                chord_duration = frames - start_frame
            
            # Minor chord for drama
            frequencies = [220, 261.63, 329.63]  # Am
            for freq in frequencies:
                chord = np.sin(2 * np.pi * freq * time[start_frame:start_frame + chord_duration])
                chord_env = np.ones(chord_duration)
                chord_env[:1000] = np.linspace(0, 1, min(1000, chord_duration))
                chord_env[-5000:] = np.linspace(1, 0.3, min(5000, chord_duration))
                music[start_frame:start_frame + chord_duration] += chord * chord_env * 0.15
        
        music = np.clip(music, -1, 1)
        music = (music * 32767 * 0.6).astype(np.int16)
        stereo = np.stack([music, music], axis=-1)
        return pygame.sndarray.make_sound(stereo)
    except Exception as e:
        print(f"Could not create game over music: {e}")
        return None

def create_typing_sound(sample_rate=22050):
    """Create 80s computer typing beep for high score entry"""
    try:
        duration = 0.05
        frames = int(duration * sample_rate)
        time = np.linspace(0, duration, frames)
        
        # High pitched beep
        beep = np.sin(2 * np.pi * 880 * time)  # A5
        beep += 0.3 * np.sin(2 * np.pi * 1760 * time)  # A6 harmonic
        
        # Quick envelope
        envelope = np.exp(-time * 50)
        beep *= envelope
        
        beep = np.clip(beep, -1, 1)
        beep = (beep * 32767 * 0.5).astype(np.int16)
        stereo = np.stack([beep, beep], axis=-1)
        return pygame.sndarray.make_sound(stereo)
    except Exception as e:
        print(f"Could not create typing sound: {e}")
        return None

def create_high_scores_music(duration=30.0, sample_rate=22050):
    """Create upbeat 80s music for high scores screen"""
    try:
        frames = int(duration * sample_rate)
        time = np.linspace(0, duration, frames)
        music = np.zeros(frames)
        
        # Upbeat bass line
        bass_pattern = [130.81, 146.83, 164.81, 174.61]  # C, D, E, F
        beat_duration = 0.25  # Fast tempo
        
        for i, freq in enumerate(bass_pattern * int(duration / (len(bass_pattern) * beat_duration))):
            start = i * beat_duration
            if start >= duration:
                break
            start_frame = int(start * sample_rate)
            end_frame = int((start + beat_duration) * sample_rate)
            if end_frame > frames:
                end_frame = frames
            
            # Punchy synth bass
            bass = np.sign(np.sin(2 * np.pi * freq * time[start_frame:end_frame]))
            music[start_frame:end_frame] += bass * 0.3
        
        # Add hi-hat pattern
        hihat_times = np.arange(0, duration, 0.125)  # 16th notes
        for hihat_time in hihat_times:
            start_frame = int(hihat_time * sample_rate)
            hihat_duration = int(0.05 * sample_rate)
            if start_frame + hihat_duration < frames:
                hihat = np.random.normal(0, 0.3, hihat_duration)
                hihat_env = np.exp(-np.linspace(0, 30, hihat_duration))
                music[start_frame:start_frame + hihat_duration] += hihat * hihat_env * 0.5
        
        # Add melody
        melody_notes = [523.25, 587.33, 659.25, 698.46, 783.99]  # C5 to G5
        for i, note in enumerate(melody_notes * int(duration / 2)):
            note_time = i * 0.5
            if note_time >= duration:
                break
            note_start = int(note_time * sample_rate)
            note_duration = int(0.4 * sample_rate)
            if note_start + note_duration < frames:
                melody = np.sin(2 * np.pi * note * time[note_start:note_start + note_duration])
                melody_env = np.ones(note_duration)
                melody_env[-1000:] = np.linspace(1, 0, min(1000, note_duration))
                music[note_start:note_start + note_duration] += melody * melody_env * 0.2
        
        music = np.clip(music, -1, 1)
        music = (music * 32767 * 0.5).astype(np.int16)
        stereo = np.stack([music, music], axis=-1)
        return pygame.sndarray.make_sound(stereo)
    except Exception as e:
        print(f"Could not create high scores music: {e}")
        return None

def create_transition_sweep(duration=0.5, sample_rate=22050):
    """Create 80s style transition sweep sound"""
    try:
        frames = int(duration * sample_rate)
        time = np.linspace(0, duration, frames)
        
        # Frequency sweep up
        freq_start = 200
        freq_end = 2000
        freq_sweep = np.linspace(freq_start, freq_end, frames)
        
        # Create sweep
        sweep = np.sin(2 * np.pi * freq_sweep * time)
        sweep += 0.3 * np.sin(2 * np.pi * freq_sweep * 2 * time)  # Harmonic
        
        # White noise swoosh
        noise = np.random.normal(0, 0.2, frames)
        noise_env = np.sin(np.pi * time / duration)  # Fade in and out
        
        # Combine
        sound = sweep * 0.6 + noise * noise_env
        
        # Overall envelope
        envelope = np.sin(np.pi * time / duration)
        sound *= envelope
        
        sound = np.clip(sound, -1, 1)
        sound = (sound * 32767 * 0.7).astype(np.int16)
        stereo = np.stack([sound, sound], axis=-1)
        return pygame.sndarray.make_sound(stereo)
    except Exception as e:
        print(f"Could not create transition sweep: {e}")
        return None

def create_player_death_sound(duration=0.8, sample_rate=22050):
    """Create 80s arcade player death sound (for non-final deaths)"""
    try:
        frames = int(duration * sample_rate)
        time = np.linspace(0, duration, frames)
        
        # Descending frequency sweep (classic arcade death)
        freq_start = 800
        freq_end = 100
        freq_sweep = np.linspace(freq_start, freq_end, frames)
        
        # Main death tone with warble
        warble = 1 + 0.2 * np.sin(2 * np.pi * 20 * time)  # 20Hz warble
        death_tone = np.sin(2 * np.pi * freq_sweep * time * warble)
        
        # Add some square wave harshness
        square_wave = np.sign(death_tone) * 0.3
        
        # Digital glitch sounds
        glitch_mask = np.random.random(frames) > 0.9
        glitch = np.random.normal(0, 0.5, frames) * glitch_mask
        
        # Combine
        sound = death_tone * 0.6 + square_wave + glitch * 0.2
        
        # Envelope - quick attack, sustain, then fade
        envelope = np.ones_like(time)
        envelope[:int(0.05 * sample_rate)] = np.linspace(0, 1, int(0.05 * sample_rate))
        envelope[int(0.5 * sample_rate):] = np.linspace(1, 0, frames - int(0.5 * sample_rate))
        
        sound *= envelope
        
        # Add echo effect
        echo_delay = int(0.1 * sample_rate)
        echo = np.zeros_like(sound)
        echo[echo_delay:] = sound[:-echo_delay] * 0.4
        sound += echo
        
        # Normalize
        sound = np.clip(sound, -1, 1)
        sound = (sound * 32767 * 0.7).astype(np.int16)
        
        stereo = np.stack([sound, sound], axis=-1)
        return pygame.sndarray.make_sound(stereo)
    except Exception as e:
        print(f"Could not create player death sound: {e}")
        return None

def create_wrong_answer_sound(duration=0.3, sample_rate=22050):
    """Create 80s style wrong answer buzzer"""
    try:
        frames = int(duration * sample_rate)
        time = np.linspace(0, duration, frames)
        
        # Harsh buzzer sound
        buzzer_freq = 150  # Low frequency
        buzzer = np.sign(np.sin(2 * np.pi * buzzer_freq * time))  # Square wave
        
        # Add some harmonics for harshness
        buzzer += 0.5 * np.sign(np.sin(2 * np.pi * buzzer_freq * 2 * time))
        buzzer += 0.3 * np.sign(np.sin(2 * np.pi * buzzer_freq * 3 * time))
        
        # Quick fade in/out
        envelope = np.ones_like(time)
        fade_samples = int(0.02 * sample_rate)
        envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
        envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
        
        buzzer *= envelope
        buzzer = np.clip(buzzer, -1, 1)
        buzzer = (buzzer * 32767 * 0.5).astype(np.int16)
        stereo = np.stack([buzzer, buzzer], axis=-1)
        return pygame.sndarray.make_sound(stereo)
    except Exception as e:
        print(f"Could not create wrong answer sound: {e}")
        return None

def create_victory_fanfare(duration=2.0, sample_rate=22050):
    """Create 80s victory fanfare for correct answer"""
    try:
        frames = int(duration * sample_rate)
        time = np.linspace(0, duration, frames)
        fanfare = np.zeros(frames)
        
        # Victory chord progression
        notes = [
            (0.0, [523.25, 659.25, 783.99]),      # C major
            (0.3, [587.33, 739.99, 880]),          # D major  
            (0.6, [659.25, 830.61, 987.77]),       # E major
            (0.9, [783.99, 987.77, 1174.66]),      # G major
            (1.2, [1046.5, 1318.51, 1567.98])      # C major octave up
        ]
        
        for note_time, chord in notes:
            start_frame = int(note_time * sample_rate)
            duration_frames = int(0.4 * sample_rate)
            if start_frame + duration_frames < frames:
                for freq in chord:
                    note = np.sin(2 * np.pi * freq * time[start_frame:start_frame + duration_frames])
                    # Bright square wave for 80s sound
                    note = np.sign(note) * 0.3
                    envelope = np.ones(duration_frames)
                    envelope[:100] = np.linspace(0, 1, min(100, duration_frames))
                    envelope[-200:] = np.linspace(1, 0, min(200, duration_frames))
                    fanfare[start_frame:start_frame + duration_frames] += note * envelope
        
        # Add sparkle
        sparkle_times = np.linspace(0.2, 1.5, 10)
        for sparkle_time in sparkle_times:
            start_frame = int(sparkle_time * sample_rate)
            sparkle_duration = int(0.1 * sample_rate)
            if start_frame + sparkle_duration < frames:
                freq = random.choice([2093, 2349.32, 2637.02])  # High notes
                sparkle = np.sin(2 * np.pi * freq * time[start_frame:start_frame + sparkle_duration])
                sparkle_env = np.exp(-np.linspace(0, 10, sparkle_duration))
                fanfare[start_frame:start_frame + sparkle_duration] += sparkle * sparkle_env * 0.2
        
        fanfare = np.clip(fanfare, -1, 1)
        fanfare = (fanfare * 32767 * 0.6).astype(np.int16)
        stereo = np.stack([fanfare, fanfare], axis=-1)
        return pygame.sndarray.make_sound(stereo)
    except Exception as e:
        print(f"Could not create victory fanfare: {e}")
        return None

def create_shield_bounce_sound(duration=0.2, sample_rate=22050):
    """Create shield bounce sound effect"""
    try:
        frames = int(duration * sample_rate)
        time = np.linspace(0, duration, frames)
        
        # High frequency ping with quick decay
        freq = 1200
        ping = np.sin(2 * np.pi * freq * time)
        
        # Add some harmonics for richness
        ping += 0.3 * np.sin(2 * np.pi * freq * 2 * time)
        
        # Quick decay envelope
        envelope = np.exp(-time * 30)
        ping *= envelope
        
        # Add some digital artifacts for sci-fi feel
        artifacts = np.random.normal(0, 0.2, frames) * np.exp(-time * 40)
        
        # Combine
        sound = ping + artifacts
        
        # Normalize
        sound = np.clip(sound, -1, 1)
        sound = (sound * 32767 * 0.7).astype(np.int16)
        
        stereo = np.stack([sound, sound], axis=-1)
        return pygame.sndarray.make_sound(stereo)
    except Exception as e:
        print(f"Could not create shield bounce sound: {e}")
        return None

def load_all_sounds():
    """Load all game sounds"""
    shoot_sound = load_shoot_sound()
    explosion_sound = create_explosion_sound()
    if explosion_sound:
        explosion_sound.set_volume(0.7)
    
    explosion_sound_2 = create_explosion_sound_2()
    if explosion_sound_2:
        explosion_sound_2.set_volume(0.8)  # Louder for second explosion
    
    death_sound_80s = create_80s_death_sound()
    if death_sound_80s:
        death_sound_80s.set_volume(0.6)
    
    final_death_sound_80s = create_final_death_sound_80s()
    if final_death_sound_80s:
        final_death_sound_80s.set_volume(0.8)  # Louder for dramatic effect
    
    transition_music_80s = create_80s_transition_music()
    if transition_music_80s:
        transition_music_80s.set_volume(0.5)
    
    # New screen sounds
    game_over_music = create_game_over_music()
    if game_over_music:
        game_over_music.set_volume(0.4)
    
    typing_sound = create_typing_sound()
    if typing_sound:
        typing_sound.set_volume(0.5)
    
    high_scores_music = create_high_scores_music()
    if high_scores_music:
        high_scores_music.set_volume(0.3)
    
    transition_sweep = create_transition_sweep()
    if transition_sweep:
        transition_sweep.set_volume(0.6)
    
    victory_fanfare = create_victory_fanfare()
    if victory_fanfare:
        victory_fanfare.set_volume(0.7)
    
    wrong_answer_sound = create_wrong_answer_sound()
    if wrong_answer_sound:
        wrong_answer_sound.set_volume(0.6)
    
    particle_shrinking_sound = create_particle_shrinking_sound()
    if particle_shrinking_sound:
        particle_shrinking_sound.set_volume(0.7)
    
    player_death_sound = create_player_death_sound()
    if player_death_sound:
        player_death_sound.set_volume(0.7)
    
    shield_bounce_sound = create_shield_bounce_sound()
    if shield_bounce_sound:
        shield_bounce_sound.set_volume(0.6)
    
    return (shoot_sound, explosion_sound, explosion_sound_2, death_sound_80s, transition_music_80s, 
            final_death_sound_80s, game_over_music, typing_sound, high_scores_music,
            transition_sweep, victory_fanfare, wrong_answer_sound, particle_shrinking_sound,
            player_death_sound, shield_bounce_sound)
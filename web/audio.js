// Audio handling for Sheeraroids

class AudioManager {
    constructor() {
        this.sounds = {};
        this.musicPlaying = false;
        this.soundEnabled = true;
        
        // Load sounds
        this.loadSounds();
    }
    
    loadSounds() {
        // Define sounds to load
        const soundFiles = {
            shoot: 'bark_shoot_converted.wav',
            explosion: 'explosion.wav'
        };
        
        // Load each sound
        for (const [name, file] of Object.entries(soundFiles)) {
            const sound = new Audio(ASSETS_PATH + file);
            sound.preload = 'auto';
            this.sounds[name] = sound;
        }
    }
    
    playSound(name) {
        if (!this.soundEnabled) return;
        
        const sound = this.sounds[name];
        if (sound) {
            // Clone the sound to allow overlapping playback
            const soundClone = sound.cloneNode();
            soundClone.volume = 0.5;
            soundClone.play().catch(e => console.log('Error playing sound:', e));
        }
    }
    
    toggleSound() {
        this.soundEnabled = !this.soundEnabled;
        return this.soundEnabled;
    }
}

// Create global audio manager
const audioManager = new AudioManager();
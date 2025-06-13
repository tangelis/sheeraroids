// Main game class for Sheeraroids

class Game {
    constructor(gameMode) {
        this.score = 0;
        this.level = 1;
        this.gameOver = false;
        this.paused = false;
        this.controlsDisabled = false;
        this.explosionCreated = false;
        this.gameMode = gameMode || "normal";
        
        // High score system
        this.highScoreManager = new HighScoreManager();
        this.highScoreEntry = null;
        this.retroGameOver = null;
        this.gameState = "playing"; // "playing", "game_over_80s", "entering_initials"
        
        // Speed multipliers based on game mode
        if (gameMode === "accelerated") {
            this.speedMultiplier = 1.5;
            this.rotationMultiplier = 1.5;
        } else if (gameMode === "slowed") {
            this.speedMultiplier = 0.5;
            this.rotationMultiplier = 0.5;
        } else {
            this.speedMultiplier = 1.0;
            this.rotationMultiplier = 1.0;
        }
        
        // Create sprite collections
        this.allSprites = [];
        this.asteroids = [];
        this.bullets = [];
        this.explosions = [];
        this.particles = [];
        
        // Create player (Sheera) with the selected game mode
        this.player = new Sheera(gameMode);
        // Apply game mode modifiers to player
        this.player.rotationSpeed *= this.rotationMultiplier;
        this.player.acceleration *= this.speedMultiplier;
        this.player.maxSpeed *= this.speedMultiplier;
        this.allSprites.push(this.player);
        
        // Spawn initial asteroids
        this.spawnAsteroids(this.level + 2);
        
        // Input state
        this.keys = {
            left: false,
            right: false,
            up: false,
            space: false,
            p: false,
            escape: false,
            enter: false
        };
        
        // Mouse state
        this.mouse = {
            x: 0,
            y: 0,
            clicked: false
        };
    }
    
    spawnAsteroids(count) {
        for (let i = 0; i < count; i++) {
            const asteroid = new Asteroid(3); // Start with large asteroids
            // Apply speed multiplier to asteroid
            asteroid.velocity.x *= this.speedMultiplier;
            asteroid.velocity.y *= this.speedMultiplier;
            asteroid.rotationSpeed *= this.rotationMultiplier;
            
            // Make sure asteroids don't spawn too close to the player
            let tooClose = true;
            while (tooClose) {
                asteroid.position.x = Math.random() * WIDTH;
                asteroid.position.y = Math.random() * HEIGHT;
                
                const dx = asteroid.position.x - this.player.position.x;
                const dy = asteroid.position.y - this.player.position.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance >= 150) {
                    tooClose = false;
                }
            }
            
            this.asteroids.push(asteroid);
            this.allSprites.push(asteroid);
        }
    }
    
    handleInput(keys, mouse) {
        this.keys = keys;
        this.mouse = mouse;
        
        // Handle different game states
        if (this.gameState === "playing") {
            if (this.keys.escape) {
                return false; // Exit game
            }
            
            if (this.keys.p && !this.controlsDisabled) {
                this.keys.p = false; // Reset key to prevent toggle spam
                this.paused = !this.paused;
            }
            
            if (this.gameOver && this.keys.enter) {
                return "restart";
            }
        } else if (this.gameState === "game_over_80s") {
            if (this.keys.enter) {
                return "restart";
            }
        } else if (this.gameState === "entering_initials") {
            // Handle initial entry
            if (this.highScoreEntry) {
                // Convert key presses to input for high score entry
                for (const [key, pressed] of Object.entries(keys)) {
                    if (pressed) {
                        if (key === 'enter') {
                            this.highScoreEntry.handleInput('Enter');
                        } else if (key === 'arrowLeft') {
                            this.highScoreEntry.handleInput('ArrowLeft');
                        } else if (key === 'arrowRight') {
                            this.highScoreEntry.handleInput('ArrowRight');
                        } else if (/^[a-z]$/.test(key)) {
                            this.highScoreEntry.handleInput(key.toUpperCase());
                        }
                        
                        // Reset key to prevent multiple inputs
                        this.keys[key] = false;
                    }
                }
                
                if (this.highScoreEntry.done) {
                    return "restart";
                }
            }
        }
        
        return true;
    }
    
    update() {
        // Handle paused or game over states
        if (this.paused || this.gameState !== "playing") {
            // Update 80s screen if active
            if (this.gameState === "game_over_80s" && this.retroGameOver) {
                this.retroGameOver.update();
                // After 2 seconds, automatically show initials entry
                if (this.retroGameOver.shouldShowInitials()) {
                    this.gameState = "entering_initials";
                    this.highScoreEntry = new HighScoreEntry(this.score, this.highScoreManager);
                }
            } else if (this.gameState === "entering_initials" && this.highScoreEntry) {
                this.highScoreEntry.update();
            }
            return;
        }
        
        // FIRST: Check if game just ended - go directly to 80s screen
        if (this.gameOver && !this.explosionCreated) {
            this.explosionCreated = true;
            this.controlsDisabled = true;
            // Hide the player sprite completely
            this.player.hidden = true;
            
            // Play death sound
            audioManager.playSound('explosion');
            
            // Go DIRECTLY to 80s screen
            this.gameState = "game_over_80s";
            this.retroGameOver = new RetroGameOverScreen(this.score, this.highScoreManager.getHighScores());
            return;
        }
        
        // Handle player controls if not disabled
        if (!this.controlsDisabled) {
            // Rotation
            if (this.keys.left) {
                this.player.rotate(-1);
            } else if (this.keys.right) {
                this.player.rotate(1);
            } else {
                this.player.stopRotation();
            }
            
            // Thrust
            if (this.keys.up) {
                this.player.accelerate();
            }
            
            // Shooting
            if (this.keys.space) {
                const bullet = this.player.shoot();
                if (bullet) {
                    bullet.velocity.x *= this.speedMultiplier;
                    bullet.velocity.y *= this.speedMultiplier;
                    this.bullets.push(bullet);
                    this.allSprites.push(bullet);
                    audioManager.playSound('shoot');
                }
            }
            
            // Shield
            if (this.keys.shift) {
                this.player.activateShield();
            } else {
                this.player.deactivateShield();
            }
        }
        
        // Update all sprites
        for (let i = this.allSprites.length - 1; i >= 0; i--) {
            const sprite = this.allSprites[i];
            sprite.update();
            
            // Remove inactive sprites
            if (!sprite.active) {
                this.allSprites.splice(i, 1);
                
                // Also remove from specific collections
                if (sprite instanceof SoundWave) {
                    const index = this.bullets.indexOf(sprite);
                    if (index !== -1) this.bullets.splice(index, 1);
                } else if (sprite instanceof Asteroid) {
                    const index = this.asteroids.indexOf(sprite);
                    if (index !== -1) this.asteroids.splice(index, 1);
                } else if (sprite instanceof Explosion) {
                    const index = this.explosions.indexOf(sprite);
                    if (index !== -1) this.explosions.splice(index, 1);
                } else if (sprite instanceof FireworkParticle) {
                    const index = this.particles.indexOf(sprite);
                    if (index !== -1) this.particles.splice(index, 1);
                }
            }
        }
        
        // Check for shield-bullet collisions (reflect bullets)
        if (this.player.shieldActive) {
            const shieldRadius = this.player.radius * (1.5 + this.player.shieldStrength / this.player.maxShield);
            for (const bullet of this.bullets) {
                // Calculate distance between bullet and player center
                const dx = bullet.position.x - this.player.position.x;
                const dy = bullet.position.y - this.player.position.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < shieldRadius) {
                    // Reflect the bullet by reversing its velocity and slightly randomizing direction
                    const angle = Math.atan2(bullet.velocity.y, bullet.velocity.x);
                    const newAngle = angle + Math.PI + (Math.random() - 0.5) * Math.PI / 5;
                    const speed = Math.sqrt(bullet.velocity.x * bullet.velocity.x + bullet.velocity.y * bullet.velocity.y);
                    
                    bullet.velocity.x = Math.cos(newAngle) * speed;
                    bullet.velocity.y = Math.sin(newAngle) * speed;
                    
                    // Reset bullet lifetime
                    bullet.spawnTime = Date.now();
                    
                    // Add some visual effect for reflection
                    this.createReflectionEffect(bullet.position);
                }
            }
        }
        
        // Check for bullet-asteroid collisions
        for (let i = this.asteroids.length - 1; i >= 0; i--) {
            const asteroid = this.asteroids[i];
            
            for (let j = this.bullets.length - 1; j >= 0; j--) {
                const bullet = this.bullets[j];
                
                if (asteroid.collidesWith(bullet)) {
                    // Score based on asteroid size
                    this.score += (4 - asteroid.size) * 100;
                    
                    // Create explosion
                    const explosion = new Explosion(asteroid.position.x, asteroid.position.y, asteroid.size);
                    this.explosions.push(explosion);
                    this.allSprites.push(explosion);
                    
                    // Play explosion sound
                    audioManager.playSound('explosion');
                    
                    // Split asteroid
                    const newAsteroids = asteroid.split();
                    for (const newAsteroid of newAsteroids) {
                        newAsteroid.position.x = asteroid.position.x;
                        newAsteroid.position.y = asteroid.position.y;
                        
                        // Apply speed multiplier to split asteroids
                        newAsteroid.velocity.x *= this.speedMultiplier;
                        newAsteroid.velocity.y *= this.speedMultiplier;
                        newAsteroid.rotationSpeed *= this.rotationMultiplier;
                        
                        this.asteroids.push(newAsteroid);
                        this.allSprites.push(newAsteroid);
                    }
                    
                    // Remove asteroid and bullet
                    asteroid.active = false;
                    bullet.active = false;
                    
                    // Remove from collections
                    this.asteroids.splice(i, 1);
                    this.bullets.splice(j, 1);
                    
                    // Find and remove from allSprites
                    const asteroidIndex = this.allSprites.indexOf(asteroid);
                    if (asteroidIndex !== -1) this.allSprites.splice(asteroidIndex, 1);
                    
                    const bulletIndex = this.allSprites.indexOf(bullet);
                    if (bulletIndex !== -1) this.allSprites.splice(bulletIndex, 1);
                    
                    break; // Break inner loop, continue with next asteroid
                }
            }
        }
        
        // Check for ship-asteroid collisions if player is not invulnerable or shielded
        if (!this.player.invulnerable && !this.player.hidden && !this.player.shieldActive) {
            for (let i = this.asteroids.length - 1; i >= 0; i--) {
                const asteroid = this.asteroids[i];
                
                if (asteroid.collidesWith(this.player)) {
                    this.player.lives--;
                    
                    // Create explosion
                    const explosion = new Explosion(asteroid.position.x, asteroid.position.y, asteroid.size);
                    this.explosions.push(explosion);
                    this.allSprites.push(explosion);
                    
                    // Play explosion sound
                    audioManager.playSound('explosion');
                    
                    // Split asteroid
                    const newAsteroids = asteroid.split();
                    for (const newAsteroid of newAsteroids) {
                        newAsteroid.position.x = asteroid.position.x;
                        newAsteroid.position.y = asteroid.position.y;
                        
                        // Apply speed multiplier to split asteroids
                        newAsteroid.velocity.x *= this.speedMultiplier;
                        newAsteroid.velocity.y *= this.speedMultiplier;
                        newAsteroid.rotationSpeed *= this.rotationMultiplier;
                        
                        this.asteroids.push(newAsteroid);
                        this.allSprites.push(newAsteroid);
                    }
                    
                    // Remove asteroid
                    asteroid.active = false;
                    this.asteroids.splice(i, 1);
                    
                    // Find and remove from allSprites
                    const asteroidIndex = this.allSprites.indexOf(asteroid);
                    if (asteroidIndex !== -1) this.allSprites.splice(asteroidIndex, 1);
                    
                    if (this.player.lives <= 0) {
                        // Game over
                        this.gameOver = true;
                    } else {
                        // Hide player temporarily
                        this.player.hide();
                    }
                    
                    break;
                }
            }
        }
        
        // Check if all asteroids are destroyed
        if (this.asteroids.length === 0) {
            this.level++;
            this.spawnAsteroids(this.level + 2);
        }
    }
    
    draw() {
        // Handle different game states
        if (this.gameState === "game_over_80s") {
            if (this.retroGameOver) {
                this.retroGameOver.draw();
            }
            return;
        } else if (this.gameState === "entering_initials") {
            if (this.highScoreEntry) {
                this.highScoreEntry.draw();
            }
            return;
        }
        
        // Normal gameplay drawing
        // Draw background
        ctx.fillStyle = BLACK;
        ctx.fillRect(0, 0, WIDTH, HEIGHT);
        
        // Draw all sprites
        for (const sprite of this.allSprites) {
            if (sprite !== this.player) {
                sprite.draw();
            }
        }
        
        // Draw player with shield or glow (only if not exploding)
        if (!this.player.hidden) {
            // Blink during invulnerability
            let shouldDraw = true;
            if (this.player.invulnerable) {
                // Blink every 100ms during invulnerability
                const blinkTime = Date.now() % 200;
                shouldDraw = blinkTime < 100;
            }
            
            if (shouldDraw) {
                this.player.draw();
            }
        }
        
        // Draw HUD
        this.drawHUD();
        
        if (this.gameOver) {
            this.drawGameOver();
        }
        
        if (this.paused) {
            this.drawPaused();
        }
    }
    
    drawHUD() {
        // Score and level
        ctx.font = "24px Arial";
        ctx.fillStyle = WHITE;
        ctx.textAlign = "left";
        ctx.fillText(`Score: ${this.score}`, 10, 30);
        ctx.fillText(`Level: ${this.level}`, 10, 60);
        
        // Lives
        ctx.textAlign = "right";
        ctx.fillText(`Lives: ${this.player.lives}`, WIDTH - 10, 30);
        
        // Heat level
        if (this.player.heat > 0) {
            const heatPercent = Math.floor((this.player.heat / this.player.maxHeat) * 100);
            ctx.fillText(`Heat: ${heatPercent}%`, WIDTH - 10, 60);
        }
        
        // Shield level
        if (this.player.shieldStrength > 0) {
            const shieldPercent = Math.floor((this.player.shieldStrength / this.player.maxShield) * 100);
            ctx.fillText(`Shield: ${shieldPercent}%`, WIDTH - 10, 90);
        }
        
        // Game mode
        const modeText = this.gameMode === "accelerated" ? "ACCELERATED" : 
                         this.gameMode === "slowed" ? "SLOWED" : "NORMAL";
        const modeColor = this.gameMode === "accelerated" ? '#FFC864' : 
                         this.gameMode === "slowed" ? '#64C8FF' : WHITE;
        
        ctx.textAlign = "center";
        ctx.fillStyle = modeColor;
        ctx.fillText(`Mode: ${modeText}`, WIDTH / 2, 30);
    }
    
    drawGameOver() {
        ctx.font = "48px Arial";
        ctx.fillStyle = RED;
        ctx.textAlign = "center";
        ctx.fillText("GAME OVER", WIDTH / 2, HEIGHT / 2 - 30);
        
        ctx.font = "24px Arial";
        ctx.fillStyle = WHITE;
        ctx.fillText(`Final Score: ${this.score}`, WIDTH / 2, HEIGHT / 2 + 10);
        ctx.fillText("Press ESC to exit", WIDTH / 2, HEIGHT / 2 + 50);
        ctx.fillText("Press ENTER to start over", WIDTH / 2, HEIGHT / 2 + 90);
    }
    
    drawPaused() {
        ctx.font = "48px Arial";
        ctx.fillStyle = WHITE;
        ctx.textAlign = "center";
        ctx.fillText("PAUSED", WIDTH / 2, HEIGHT / 2);
        
        ctx.font = "24px Arial";
        ctx.fillText("Press P to continue", WIDTH / 2, HEIGHT / 2 + 40);
    }
    
    createReflectionEffect(position) {
        // Create a small flash effect when bullets reflect off shield
        for (let i = 0; i < 5; i++) {
            // Random direction
            const angle = Math.random() * Math.PI * 2;
            const speed = Math.random() * 2 + 1;
            const velocity = {
                x: Math.cos(angle) * speed,
                y: Math.sin(angle) * speed
            };
            
            // Use shield color for reflection particles
            const colorIndex = Math.min(this.player.shieldColors.length - 1,
                                      Math.floor((this.player.shieldStrength / this.player.maxShield) * 
                                                this.player.shieldColors.length));
            const color = this.player.shieldColors[colorIndex];
            
            // Create particle
            const particle = new FireworkParticle(
                position.x,
                position.y,
                velocity,
                color
            );
            particle.lifetime = 10; // Short lifetime
            this.particles.push(particle);
            this.allSprites.push(particle);
        }
    }
}
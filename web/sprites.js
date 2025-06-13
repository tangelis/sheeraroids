// Sprite classes for Sheeraroids

class Sprite {
    constructor(x, y) {
        this.position = { x, y };
        this.velocity = { x: 0, y: 0 };
        this.rotation = 0;
        this.rotationSpeed = 0;
        this.size = { width: 0, height: 0 };
        this.active = true;
    }

    update() {
        // Update position based on velocity
        this.position.x += this.velocity.x;
        this.position.y += this.velocity.y;
        
        // Update rotation
        this.rotation += this.rotationSpeed;
        
        // Screen wrapping
        if (this.position.x < 0) this.position.x = WIDTH;
        if (this.position.x > WIDTH) this.position.x = 0;
        if (this.position.y < 0) this.position.y = HEIGHT;
        if (this.position.y > HEIGHT) this.position.y = 0;
    }

    draw() {
        // Override in subclasses
    }

    collidesWith(other) {
        // Simple circle collision
        const dx = this.position.x - other.position.x;
        const dy = this.position.y - other.position.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        return distance < (this.radius + other.radius);
    }
}

class Sheera extends Sprite {
    constructor(gameMode) {
        super(WIDTH / 2, HEIGHT / 2);
        this.radius = 20;
        this.rotation = -Math.PI / 2; // Point upward
        this.rotationSpeed = 0;
        this.acceleration = 0.2;
        this.friction = 0.98;
        this.maxSpeed = 5;
        this.lives = 3;
        this.invulnerable = false;
        this.invulnerableTime = 0;
        this.hidden = false;
        this.shootCooldown = 0;
        this.heat = 0;
        this.maxHeat = 100;
        this.heatCooldownRate = 0.5;
        this.shield = false;
        this.shieldStrength = 100;
        this.maxShield = 100;
        this.shieldRechargeRate = 0.1;
        this.shieldActive = false;
        this.shieldColors = [
            '#00FFFF', '#00CCFF', '#0099FF', '#0066FF', '#0033FF'
        ];
        
        // Apply game mode modifiers
        if (gameMode === "accelerated") {
            this.acceleration *= 1.5;
            this.maxSpeed *= 1.5;
            this.rotationSpeed *= 1.5;
        } else if (gameMode === "slowed") {
            this.acceleration *= 0.5;
            this.maxSpeed *= 0.5;
            this.rotationSpeed *= 0.5;
        }
        
        // Load ship image
        this.image = new Image();
        this.image.src = ASSETS_PATH + 'ship.png';
    }

    update() {
        if (this.hidden) return;
        
        super.update();
        
        // Apply friction
        this.velocity.x *= this.friction;
        this.velocity.y *= this.friction;
        
        // Cool down weapon heat
        if (this.heat > 0) {
            this.heat -= this.heatCooldownRate;
            if (this.heat < 0) this.heat = 0;
        }
        
        // Recharge shield
        if (!this.shieldActive && this.shieldStrength < this.maxShield) {
            this.shieldStrength += this.shieldRechargeRate;
            if (this.shieldStrength > this.maxShield) {
                this.shieldStrength = this.maxShield;
            }
        }
        
        // Handle invulnerability timer
        if (this.invulnerable) {
            this.invulnerableTime--;
            if (this.invulnerableTime <= 0) {
                this.invulnerable = false;
            }
        }
        
        // Decrease shoot cooldown
        if (this.shootCooldown > 0) {
            this.shootCooldown--;
        }
    }

    draw() {
        if (this.hidden) return;
        
        ctx.save();
        ctx.translate(this.position.x, this.position.y);
        ctx.rotate(this.rotation);
        
        // Draw ship
        ctx.drawImage(this.image, -this.radius, -this.radius, this.radius * 2, this.radius * 2);
        
        // Draw shield if active
        if (this.shieldActive) {
            this.drawShield();
        }
        
        // Draw heat glow if hot
        if (this.heat > 0) {
            this.drawGlow();
        }
        
        ctx.restore();
    }

    drawShield() {
        const shieldRadius = this.radius * (1.5 + this.shieldStrength / this.maxShield * 0.5);
        const colorIndex = Math.min(this.shieldColors.length - 1, 
                                   Math.floor((this.shieldStrength / this.maxShield) * this.shieldColors.length));
        
        ctx.beginPath();
        ctx.arc(0, 0, shieldRadius, 0, Math.PI * 2);
        ctx.strokeStyle = this.shieldColors[colorIndex];
        ctx.lineWidth = 3;
        ctx.globalAlpha = 0.7;
        ctx.stroke();
        ctx.globalAlpha = 1.0;
    }

    drawGlow() {
        const glowRadius = this.radius * (1 + this.heat / this.maxHeat * 0.5);
        const gradient = ctx.createRadialGradient(0, 0, this.radius, 0, 0, glowRadius);
        
        gradient.addColorStop(0, 'rgba(255, 100, 0, 0.8)');
        gradient.addColorStop(1, 'rgba(255, 50, 0, 0)');
        
        ctx.beginPath();
        ctx.arc(0, 0, glowRadius, 0, Math.PI * 2);
        ctx.fillStyle = gradient;
        ctx.fill();
    }

    accelerate() {
        const dx = Math.cos(this.rotation) * this.acceleration;
        const dy = Math.sin(this.rotation) * this.acceleration;
        
        this.velocity.x += dx;
        this.velocity.y += dy;
        
        // Limit speed
        const speed = Math.sqrt(this.velocity.x * this.velocity.x + this.velocity.y * this.velocity.y);
        if (speed > this.maxSpeed) {
            const ratio = this.maxSpeed / speed;
            this.velocity.x *= ratio;
            this.velocity.y *= ratio;
        }
    }

    rotate(direction) {
        this.rotationSpeed = direction * 0.05;
    }

    stopRotation() {
        this.rotationSpeed = 0;
    }

    shoot() {
        if (this.shootCooldown > 0 || this.hidden) return null;
        
        // Add heat when shooting
        this.heat += 10;
        if (this.heat > this.maxHeat) {
            this.heat = this.maxHeat;
            return null; // Too hot to shoot
        }
        
        this.shootCooldown = 10;
        
        return new SoundWave(
            this.position.x + Math.cos(this.rotation) * this.radius,
            this.position.y + Math.sin(this.rotation) * this.radius,
            this.rotation
        );
    }

    activateShield() {
        if (this.shieldStrength > 0 && !this.hidden) {
            this.shieldActive = true;
        }
    }

    deactivateShield() {
        this.shieldActive = false;
    }

    hide() {
        this.hidden = true;
        this.invulnerable = true;
        this.invulnerableTime = 180; // 3 seconds at 60fps
        
        // Respawn after 2 seconds
        setTimeout(() => {
            this.position.x = WIDTH / 2;
            this.position.y = HEIGHT / 2;
            this.velocity.x = 0;
            this.velocity.y = 0;
            this.hidden = false;
        }, 2000);
    }
}

class SoundWave extends Sprite {
    constructor(x, y, angle) {
        super(x, y);
        this.radius = 5;
        this.speed = 10;
        this.velocity.x = Math.cos(angle) * this.speed;
        this.velocity.y = Math.sin(angle) * this.speed;
        this.spawnTime = Date.now();
        this.lifetime = 2000; // 2 seconds
    }

    update() {
        super.update();
        
        // Check if bullet has expired
        if (Date.now() - this.spawnTime > this.lifetime) {
            this.active = false;
        }
    }

    draw() {
        ctx.save();
        ctx.translate(this.position.x, this.position.y);
        
        // Draw sound wave
        ctx.beginPath();
        ctx.arc(0, 0, this.radius, 0, Math.PI * 2);
        ctx.fillStyle = '#00FFFF';
        ctx.fill();
        
        // Draw wave rings
        const age = (Date.now() - this.spawnTime) / 100;
        for (let i = 0; i < 3; i++) {
            const ringRadius = this.radius + (i + 1) * 3 + Math.sin(age + i) * 2;
            ctx.beginPath();
            ctx.arc(0, 0, ringRadius, 0, Math.PI * 2);
            ctx.strokeStyle = `rgba(0, 255, 255, ${0.7 - i * 0.2})`;
            ctx.lineWidth = 1;
            ctx.stroke();
        }
        
        ctx.restore();
    }
}

class Asteroid extends Sprite {
    constructor(size, x, y) {
        // If position not provided, use random position
        x = x || Math.random() * WIDTH;
        y = y || Math.random() * HEIGHT;
        
        super(x, y);
        
        this.size = size || 3; // 3 = large, 2 = medium, 1 = small
        this.radius = this.size * 20;
        
        // Random velocity
        const speed = (4 - this.size) * 0.5 + 0.5;
        const angle = Math.random() * Math.PI * 2;
        this.velocity.x = Math.cos(angle) * speed;
        this.velocity.y = Math.sin(angle) * speed;
        
        // Random rotation
        this.rotationSpeed = (Math.random() - 0.5) * 0.04;
        
        // Create asteroid shape (vertices)
        this.vertices = [];
        const numVertices = 10 + this.size * 2;
        for (let i = 0; i < numVertices; i++) {
            const angle = (i / numVertices) * Math.PI * 2;
            const distance = this.radius * (0.8 + Math.random() * 0.4);
            this.vertices.push({
                x: Math.cos(angle) * distance,
                y: Math.sin(angle) * distance
            });
        }
        
        // Load iguana image
        this.image = new Image();
        this.image.src = ASSETS_PATH + 'iguana.png';
    }

    draw() {
        ctx.save();
        ctx.translate(this.position.x, this.position.y);
        ctx.rotate(this.rotation);
        
        // Draw asteroid (iguana)
        ctx.drawImage(this.image, -this.radius, -this.radius, this.radius * 2, this.radius * 2);
        
        ctx.restore();
    }

    split() {
        if (this.size <= 1) {
            return []; // Too small to split
        }
        
        const newAsteroids = [];
        for (let i = 0; i < 2; i++) {
            const newAsteroid = new Asteroid(this.size - 1, this.position.x, this.position.y);
            newAsteroids.push(newAsteroid);
        }
        
        return newAsteroids;
    }
}

class FireworkParticle extends Sprite {
    constructor(x, y, velocity, color) {
        super(x, y);
        this.velocity = velocity || { x: (Math.random() - 0.5) * 5, y: (Math.random() - 0.5) * 5 };
        this.color = color || '#FFFFFF';
        this.radius = 2;
        this.lifetime = 60; // 1 second at 60fps
        this.initialLifetime = this.lifetime;
    }

    update() {
        super.update();
        
        // Apply gravity
        this.velocity.y += 0.1;
        
        // Decrease lifetime
        this.lifetime--;
        if (this.lifetime <= 0) {
            this.active = false;
        }
    }

    draw() {
        const alpha = this.lifetime / this.initialLifetime;
        
        ctx.save();
        ctx.globalAlpha = alpha;
        ctx.beginPath();
        ctx.arc(this.position.x, this.position.y, this.radius, 0, Math.PI * 2);
        ctx.fillStyle = this.color;
        ctx.fill();
        ctx.restore();
    }
}
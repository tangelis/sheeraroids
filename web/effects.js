// Visual effects for Sheeraroids

class Explosion {
    constructor(x, y, size) {
        this.position = { x, y };
        this.size = size || 3;
        this.radius = this.size * 20;
        this.particles = [];
        this.active = true;
        this.lifetime = 60; // 1 second at 60fps
        
        // Create explosion particles
        this.createParticles();
    }
    
    createParticles() {
        const numParticles = this.size * 15;
        const colors = ['#FF0000', '#FF5500', '#FFAA00', '#FFFF00', '#FFFFFF'];
        
        for (let i = 0; i < numParticles; i++) {
            const angle = Math.random() * Math.PI * 2;
            const speed = Math.random() * 3 + 2;
            const velocity = {
                x: Math.cos(angle) * speed,
                y: Math.sin(angle) * speed
            };
            const color = colors[Math.floor(Math.random() * colors.length)];
            
            const particle = new FireworkParticle(
                this.position.x,
                this.position.y,
                velocity,
                color
            );
            
            particle.lifetime = 30 + Math.random() * 30;
            particle.initialLifetime = particle.lifetime;
            this.particles.push(particle);
        }
    }
    
    update() {
        // Update all particles
        for (let i = this.particles.length - 1; i >= 0; i--) {
            this.particles[i].update();
            
            // Remove inactive particles
            if (!this.particles[i].active) {
                this.particles.splice(i, 1);
            }
        }
        
        // Decrease lifetime
        this.lifetime--;
        if (this.lifetime <= 0 || this.particles.length === 0) {
            this.active = false;
        }
    }
    
    draw() {
        // Draw all particles
        for (const particle of this.particles) {
            particle.draw();
        }
    }
}
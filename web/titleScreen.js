// Title screen for Sheeraroids

class TitleScreen {
    constructor() {
        this.particles = [];
        this.stars = [];
        this.time = 0;
        this.blinkTimer = 0;
        this.showStart = true;
        
        // Create stars
        this.createStars();
        
        // Load ship image
        this.shipImg = new Image();
        this.shipImg.src = ASSETS_PATH + 'ship.png';
        
        // Ship animation variables
        this.shipPos = { x: WIDTH / 2, y: HEIGHT / 2 + 100 };
        this.shipAngle = 0;
    }
    
    createStars() {
        // Create background stars
        for (let i = 0; i < 100; i++) {
            const star = {
                pos: { 
                    x: Math.random() * WIDTH, 
                    y: Math.random() * HEIGHT 
                },
                size: Math.random() * 2 + 1,
                brightness: Math.random() * 155 + 100,
                speed: Math.random() * 0.8 + 0.2
            };
            this.stars.push(star);
        }
    }
    
    createFirework() {
        // Create a firework explosion at random position
        const pos = {
            x: Math.random() * WIDTH / 2 + WIDTH / 4,
            y: Math.random() * HEIGHT / 2 + HEIGHT / 4
        };
        
        const colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF'];
        
        for (let i = 0; i < 50; i++) {
            const angle = Math.random() * Math.PI * 2;
            const speed = Math.random() * 4 + 1;
            const velocity = {
                x: Math.cos(angle) * speed,
                y: Math.sin(angle) * speed
            };
            const color = colors[Math.floor(Math.random() * colors.length)];
            
            const particle = {
                pos: { x: pos.x, y: pos.y },
                vel: velocity,
                color: color,
                size: Math.random() * 2 + 2,
                lifetime: Math.random() * 30 + 30
            };
            
            this.particles.push(particle);
        }
    }
    
    update() {
        this.time++;
        
        // Update stars
        for (const star of this.stars) {
            star.pos.y += star.speed;
            if (star.pos.y > HEIGHT) {
                star.pos.y = 0;
                star.pos.x = Math.random() * WIDTH;
            }
        }
        
        // Update particles
        for (let i = this.particles.length - 1; i >= 0; i--) {
            const particle = this.particles[i];
            
            particle.pos.x += particle.vel.x;
            particle.pos.y += particle.vel.y;
            particle.vel.y += 0.1; // Gravity
            particle.lifetime--;
            
            if (particle.lifetime <= 0) {
                this.particles.splice(i, 1);
            }
        }
        
        // Occasionally create fireworks
        if (Math.random() < 0.02) {
            this.createFirework();
        }
        
        // Update ship animation
        this.shipAngle = 10 * Math.sin(this.time * 0.05) * Math.PI / 180;
        
        // Blink the start text
        this.blinkTimer++;
        if (this.blinkTimer >= 30) {
            this.blinkTimer = 0;
            this.showStart = !this.showStart;
        }
    }
    
    draw() {
        // Clear screen
        ctx.fillStyle = BLACK;
        ctx.fillRect(0, 0, WIDTH, HEIGHT);
        
        // Draw stars
        for (const star of this.stars) {
            ctx.fillStyle = `rgb(${star.brightness}, ${star.brightness}, ${star.brightness})`;
            ctx.beginPath();
            ctx.arc(star.pos.x, star.pos.y, star.size, 0, Math.PI * 2);
            ctx.fill();
        }
        
        // Draw particles
        for (const particle of this.particles) {
            const alpha = particle.lifetime / 60;
            ctx.globalAlpha = alpha;
            ctx.fillStyle = particle.color;
            ctx.beginPath();
            ctx.arc(particle.pos.x, particle.pos.y, particle.size, 0, Math.PI * 2);
            ctx.fill();
        }
        
        ctx.globalAlpha = 1.0;
        
        // Draw title with glow effect
        const titleText = "SHEERAROIDS";
        ctx.font = "80px Arial";
        ctx.textAlign = "center";
        
        // Glow effect
        const glowColors = [
            'rgba(255, 0, 0, 0.3)',
            'rgba(0, 255, 0, 0.3)',
            'rgba(0, 0, 255, 0.3)'
        ];
        
        for (let i = 0; i < glowColors.length; i++) {
            const offset = 5 * Math.sin(this.time * 0.05 + i);
            ctx.fillStyle = glowColors[i];
            ctx.fillText(titleText, WIDTH / 2 + offset, HEIGHT / 3);
        }
        
        // Main title
        ctx.fillStyle = '#FFFF00';
        ctx.fillText(titleText, WIDTH / 2, HEIGHT / 3);
        
        // Draw ship
        ctx.save();
        ctx.translate(this.shipPos.x, this.shipPos.y);
        ctx.rotate(this.shipAngle);
        ctx.drawImage(this.shipImg, -50, -37.5, 100, 75);
        ctx.restore();
        
        // Draw start text (blinking)
        if (this.showStart) {
            ctx.font = "40px Arial";
            ctx.fillStyle = WHITE;
            ctx.fillText("Press SPACE to Start", WIDTH / 2, HEIGHT * 2 / 3);
        }
        
        // Draw creator credit
        ctx.font = "20px Arial";
        ctx.fillStyle = '#CCCCCC';
        ctx.fillText("Created by LBL", WIDTH / 2, HEIGHT - 50);
    }
    
    handleInput(keys) {
        if (keys.space) {
            return true; // Exit title screen
        }
        return false;
    }
}
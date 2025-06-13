// User interface components for Sheeraroids

class ModeSelection {
    constructor() {
        // Load mode selection images
        this.mode1Img = new Image();
        this.mode1Img.src = ASSETS_PATH + 'ChatGPT Image Jun 12, 2025, 07_17_20 PM.png';
        
        this.mode2Img = new Image();
        this.mode2Img.src = ASSETS_PATH + 'Generated Image June 12, 2025 - 7_16PM.png';
        
        this.selectedMode = null;
    }
    
    update(mouseX, mouseY, mouseClicked, keys) {
        // Check for key presses
        if (keys.digit1) {
            this.selectedMode = "accelerated";
            return true;
        } else if (keys.digit2) {
            this.selectedMode = "slowed";
            return true;
        }
        
        // Check for mouse clicks
        if (mouseClicked) {
            // Check if clicked on mode 1
            if (mouseX >= 50 && mouseX <= 350 && mouseY >= 200 && mouseY <= 500) {
                this.selectedMode = "accelerated";
                return true;
            }
            // Check if clicked on mode 2
            else if (mouseX >= 450 && mouseX <= 750 && mouseY >= 200 && mouseY <= 500) {
                this.selectedMode = "slowed";
                return true;
            }
        }
        
        return false;
    }
    
    draw() {
        // Clear screen
        ctx.fillStyle = BLACK;
        ctx.fillRect(0, 0, WIDTH, HEIGHT);
        
        // Title
        ctx.font = "64px Arial";
        ctx.fillStyle = WHITE;
        ctx.textAlign = "center";
        ctx.fillText("CHOOSE YOUR MODE", WIDTH / 2, 100);
        
        // Instruction
        ctx.font = "24px Arial";
        ctx.fillText("Choose your gameplay speed mode", WIDTH / 2, 150);
        
        // Mode 1 - Accelerated
        ctx.drawImage(this.mode1Img, 50, 200, 300, 300);
        ctx.font = "36px Arial";
        ctx.fillStyle = '#FFC864';
        ctx.fillText("ACCELERATED", 200, 520);
        ctx.font = "24px Arial";
        ctx.fillStyle = WHITE;
        ctx.fillText("Press 1 or Click", 200, 550);
        
        // Mode 2 - Slowed
        ctx.drawImage(this.mode2Img, 450, 200, 300, 300);
        ctx.font = "36px Arial";
        ctx.fillStyle = '#64C8FF';
        ctx.fillText("SLOWED", 600, 520);
        ctx.font = "24px Arial";
        ctx.fillStyle = WHITE;
        ctx.fillText("Press 2 or Click", 600, 550);
    }
    
    getSelectedMode() {
        return this.selectedMode;
    }
}

class HighScoreManager {
    constructor() {
        this.highScores = this.loadHighScores();
    }
    
    loadHighScores() {
        const savedScores = localStorage.getItem('sheeraroids-highscores');
        if (savedScores) {
            return JSON.parse(savedScores);
        }
        return [
            { name: "LBL", score: 10000 },
            { name: "SHR", score: 8000 },
            { name: "AWS", score: 6000 },
            { name: "GPT", score: 4000 },
            { name: "CPU", score: 2000 }
        ];
    }
    
    saveHighScores() {
        localStorage.setItem('sheeraroids-highscores', JSON.stringify(this.highScores));
    }
    
    addScore(name, score) {
        this.highScores.push({ name, score });
        this.highScores.sort((a, b) => b.score - a.score);
        this.highScores = this.highScores.slice(0, 10); // Keep only top 10
        this.saveHighScores();
    }
    
    getHighScores() {
        return this.highScores;
    }
    
    isHighScore(score) {
        return score > 0 && (
            this.highScores.length < 10 || 
            score > this.highScores[this.highScores.length - 1].score
        );
    }
}

class HighScoreEntry {
    constructor(score, highScoreManager) {
        this.score = score;
        this.highScoreManager = highScoreManager;
        this.initials = "AAA";
        this.currentPosition = 0;
        this.done = false;
        this.blinkTimer = 0;
        this.showCursor = true;
    }
    
    update() {
        // Blink cursor
        this.blinkTimer++;
        if (this.blinkTimer >= 30) {
            this.blinkTimer = 0;
            this.showCursor = !this.showCursor;
        }
    }
    
    handleInput(key) {
        if (key === 'Enter') {
            this.highScoreManager.addScore(this.initials, this.score);
            this.done = true;
            return;
        }
        
        if (key === 'ArrowLeft') {
            this.currentPosition = Math.max(0, this.currentPosition - 1);
            return;
        }
        
        if (key === 'ArrowRight') {
            this.currentPosition = Math.min(2, this.currentPosition + 1);
            return;
        }
        
        // Handle letter input (A-Z)
        if (/^[A-Z]$/.test(key)) {
            const initialsArray = this.initials.split('');
            initialsArray[this.currentPosition] = key;
            this.initials = initialsArray.join('');
            this.currentPosition = Math.min(2, this.currentPosition + 1);
        }
    }
    
    draw() {
        // Clear screen
        ctx.fillStyle = BLACK;
        ctx.fillRect(0, 0, WIDTH, HEIGHT);
        
        // Title
        ctx.font = "64px Arial";
        ctx.fillStyle = '#FFFF00';
        ctx.textAlign = "center";
        ctx.fillText("HIGH SCORE!", WIDTH / 2, 150);
        
        // Score
        ctx.font = "36px Arial";
        ctx.fillStyle = WHITE;
        ctx.fillText(`Your Score: ${this.score}`, WIDTH / 2, 220);
        
        // Instructions
        ctx.font = "24px Arial";
        ctx.fillText("Enter your initials:", WIDTH / 2, 280);
        
        // Draw initials (with cursor)
        ctx.font = "72px Arial";
        ctx.fillStyle = '#00FFFF';
        
        const letterWidth = 50;
        const startX = WIDTH / 2 - letterWidth * 1.5;
        
        for (let i = 0; i < 3; i++) {
            const x = startX + i * letterWidth;
            
            // Draw box
            ctx.strokeStyle = WHITE;
            ctx.lineWidth = 2;
            ctx.strokeRect(x - 25, 320, 50, 70);
            
            // Draw letter
            ctx.fillText(this.initials[i], x, 375);
            
            // Draw cursor
            if (i === this.currentPosition && this.showCursor) {
                ctx.fillRect(x - 20, 385, 40, 5);
            }
        }
        
        // Instructions
        ctx.font = "24px Arial";
        ctx.fillStyle = WHITE;
        ctx.fillText("Use arrow keys to move, letters to type", WIDTH / 2, 450);
        ctx.fillText("Press ENTER when done", WIDTH / 2, 480);
    }
}

class RetroGameOverScreen {
    constructor(score, highScores) {
        this.score = score;
        this.highScores = highScores;
        this.timer = 0;
        this.showInitials = false;
    }
    
    update() {
        this.timer++;
        if (this.timer > 120) { // 2 seconds at 60fps
            this.showInitials = true;
        }
    }
    
    draw() {
        // Clear screen
        ctx.fillStyle = BLACK;
        ctx.fillRect(0, 0, WIDTH, HEIGHT);
        
        // Game Over text
        ctx.font = "72px Arial";
        ctx.fillStyle = '#FF0000';
        ctx.textAlign = "center";
        ctx.fillText("GAME OVER", WIDTH / 2, 150);
        
        // Score
        ctx.font = "36px Arial";
        ctx.fillStyle = WHITE;
        ctx.fillText(`Your Score: ${this.score}`, WIDTH / 2, 220);
        
        // High Scores
        ctx.font = "48px Arial";
        ctx.fillStyle = '#FFFF00';
        ctx.fillText("HIGH SCORES", WIDTH / 2, 300);
        
        // List high scores
        ctx.font = "24px Arial";
        ctx.fillStyle = WHITE;
        ctx.textAlign = "left";
        
        const scoreX = WIDTH / 2 - 150;
        let scoreY = 350;
        
        for (let i = 0; i < Math.min(5, this.highScores.length); i++) {
            const score = this.highScores[i];
            ctx.fillText(`${i + 1}. ${score.name}`, scoreX, scoreY);
            ctx.textAlign = "right";
            ctx.fillText(`${score.score}`, scoreX + 300, scoreY);
            ctx.textAlign = "left";
            scoreY += 30;
        }
        
        // Instructions
        ctx.textAlign = "center";
        ctx.fillStyle = this.timer % 60 < 30 ? WHITE : '#AAAAAA';
        ctx.fillText("Press ENTER to play again", WIDTH / 2, HEIGHT - 100);
    }
    
    shouldShowInitials() {
        return this.showInitials;
    }
}
// Main entry point for Sheeraroids web version

// Game states
const GameState = {
    TITLE_SCREEN: 'title_screen',
    MODE_SELECTION: 'mode_selection',
    GAME: 'game'
};

// Game variables
let gameState = GameState.TITLE_SCREEN;
let titleScreen = null;
let modeSelection = null;
let game = null;
let lastTime = 0;
let selectedMode = null;

// Input state
const keys = {
    left: false,
    right: false,
    up: false,
    down: false,
    space: false,
    shift: false,
    enter: false,
    escape: false,
    p: false,
    digit1: false,
    digit2: false,
    arrowLeft: false,
    arrowRight: false
};

// Mouse state
const mouse = {
    x: 0,
    y: 0,
    clicked: false
};

// Initialize game
function init() {
    // Get canvas and context
    canvas = document.getElementById('game-canvas');
    ctx = canvas.getContext('2d');
    
    // Set up event listeners
    setupEventListeners();
    
    // Create title screen
    titleScreen = new TitleScreen();
    
    // Start game loop
    requestAnimationFrame(gameLoop);
}

// Set up event listeners
function setupEventListeners() {
    // Keyboard events
    window.addEventListener('keydown', (e) => {
        switch (e.key) {
            case 'ArrowLeft':
            case 'a':
                keys.left = true;
                keys.arrowLeft = true;
                break;
            case 'ArrowRight':
            case 'd':
                keys.right = true;
                keys.arrowRight = true;
                break;
            case 'ArrowUp':
            case 'w':
                keys.up = true;
                break;
            case 'ArrowDown':
            case 's':
                keys.down = true;
                break;
            case ' ':
                keys.space = true;
                break;
            case 'Shift':
                keys.shift = true;
                break;
            case 'Enter':
                keys.enter = true;
                break;
            case 'Escape':
                keys.escape = true;
                break;
            case 'p':
            case 'P':
                keys.p = true;
                break;
            case '1':
                keys.digit1 = true;
                break;
            case '2':
                keys.digit2 = true;
                break;
        }
    });
    
    window.addEventListener('keyup', (e) => {
        switch (e.key) {
            case 'ArrowLeft':
            case 'a':
                keys.left = false;
                keys.arrowLeft = false;
                break;
            case 'ArrowRight':
            case 'd':
                keys.right = false;
                keys.arrowRight = false;
                break;
            case 'ArrowUp':
            case 'w':
                keys.up = false;
                break;
            case 'ArrowDown':
            case 's':
                keys.down = false;
                break;
            case ' ':
                keys.space = false;
                break;
            case 'Shift':
                keys.shift = false;
                break;
            case 'Enter':
                keys.enter = false;
                break;
            case 'Escape':
                keys.escape = false;
                break;
            case 'p':
            case 'P':
                keys.p = false;
                break;
            case '1':
                keys.digit1 = false;
                break;
            case '2':
                keys.digit2 = false;
                break;
        }
    });
    
    // Mouse events
    canvas.addEventListener('mousemove', (e) => {
        const rect = canvas.getBoundingClientRect();
        mouse.x = e.clientX - rect.left;
        mouse.y = e.clientY - rect.top;
    });
    
    canvas.addEventListener('mousedown', () => {
        mouse.clicked = true;
    });
    
    canvas.addEventListener('mouseup', () => {
        mouse.clicked = false;
    });
}

// Main game loop
function gameLoop(timestamp) {
    // Calculate delta time
    const deltaTime = timestamp - lastTime;
    lastTime = timestamp;
    
    // Update based on current game state
    switch (gameState) {
        case GameState.TITLE_SCREEN:
            titleScreen.update();
            titleScreen.draw();
            
            // Check for input to exit title screen
            if (keys.space || keys.enter) {
                keys.space = false;
                keys.enter = false;
                
                // Move to mode selection
                gameState = GameState.MODE_SELECTION;
                modeSelection = new ModeSelection();
            }
            break;
            
        case GameState.MODE_SELECTION:
            // Check for mode selection
            if (modeSelection.update(mouse.x, mouse.y, mouse.clicked, keys)) {
                mouse.clicked = false;
                
                // Get selected mode and start game
                selectedMode = modeSelection.getSelectedMode();
                game = new Game(selectedMode);
                gameState = GameState.GAME;
            }
            
            modeSelection.draw();
            break;
            
        case GameState.GAME:
            // Handle game input
            const result = game.handleInput(keys, mouse);
            
            if (result === "restart") {
                // Restart game with same mode
                game = new Game(selectedMode);
            } else if (result === false) {
                // Exit to title screen
                gameState = GameState.TITLE_SCREEN;
                titleScreen = new TitleScreen();
            } else {
                // Update and draw game
                game.update();
                game.draw();
            }
            
            // Reset mouse click
            mouse.clicked = false;
            break;
    }
    
    // Continue game loop
    requestAnimationFrame(gameLoop);
}

// Start the game when page loads
window.addEventListener('load', init);
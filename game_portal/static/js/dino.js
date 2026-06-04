// Динозаврик (Chrome Dino clone)
const canvas = document.createElement('canvas');
canvas.width = 600;
canvas.height = 200;
document.getElementById('game-container').appendChild(canvas);
const ctx = canvas.getContext('2d');

// Игрок
const dino = {
    x: 50,
    y: 150,
    width: 40,
    height: 40,
    velocityY: 0,
    jumping: false
};

const gravity = 0.6;
const jumpForce = -12;
let obstacles = [];
let score = 0;
let gameSpeed = 5;
let gameRunning = false;

document.addEventListener('keydown', (e) => {
    if (e.code === 'Space' && !dino.jumping && gameRunning) {
        dino.velocityY = jumpForce;
        dino.jumping = true;
    }
});

function update() {
    // Физика
    dino.velocityY += gravity;
    dino.y += dino.velocityY;

    if (dino.y >= 150) {
        dino.y = 150;
        dino.velocityY = 0;
        dino.jumping = false;
    }

    // Препятствия
    if (Math.random() < 0.02) {
        obstacles.push({
            x: 600,
            y: 170,
            width: 20,
            height: 30
        });
    }

    for (let i = obstacles.length - 1; i >= 0; i--) {
        obstacles[i].x -= gameSpeed;
        
        // Удаление за экраном
        if (obstacles[i].x + obstacles[i].width < 0) {
            obstacles.splice(i, 1);
            score += 10;
        }
        
        // Столкновение
        if (dino.x < obstacles[i].x + obstacles[i].width &&
            dino.x + dino.width > obstacles[i].x &&
            dino.y < obstacles[i].y + obstacles[i].height &&
            dino.y + dino.height > obstacles[i].y) {
            gameOver();
        }
    }
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Земля
    ctx.fillStyle = '#555';
    ctx.fillRect(0, 190, canvas.width, 10);

    // Динозавр
    ctx.fillStyle = '#333';
    ctx.fillRect(dino.x, dino.y, dino.width, dino.height);

    // Препятствия
    ctx.fillStyle = '#e94560';
    obstacles.forEach(obs => {
        ctx.fillRect(obs.x, obs.y, obs.width, obs.height);
    });

    // Счет
    ctx.fillStyle = '#e94560';
    ctx.font = '20px Arial';
    ctx.fillText('Score: ' + score, 10, 30);
}

function gameLoop() {
    if (!gameRunning) return;
    update();
    draw();
    requestAnimationFrame(gameLoop);
}

function startGame() {
    if (gameRunning) return;
    obstacles = [];
    score = 0;
    dino.y = 150;
    dino.velocityY = 0;
    gameRunning = true;
    gameLoop();
}

function gameOver() {
    gameRunning = false;
    alert("Игра окончена! Счет: " + score);
    submitScore(score);
}

function submitScore(finalScore) {
    fetch('/api/score/{{ game.id }}/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'
        },
        body: JSON.stringify({score: finalScore})
    });
}

document.getElementById('start-btn').addEventListener('click', startGame);

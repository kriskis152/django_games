import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'game_portal.settings')

import django
django.setup()

from games.models import Game

# Змейка — использует переданные canvas, ctx, submitScore
snake_js = """
// Настройка canvas
canvas.width = 400;
canvas.height = 400;
canvas.style.backgroundColor = '#1a1a2e';

const gridSize = 20;
const tileCount = canvas.width / gridSize;

let snake = [{x: 10, y: 10}];
let food = {x: 15, y: 15};
let dx = 1;
let dy = 0;
let score = 0;
let gameLoop = null;

function changeDirection(event) {
    const key = event.keyCode;
    if (key === 37 && dx !== 1) { dx = -1; dy = 0; }
    if (key === 38 && dy !== 1) { dx = 0; dy = -1; }
    if (key === 39 && dx !== -1) { dx = 1; dy = 0; }
    if (key === 40 && dy !== -1) { dx = 0; dy = 1; }
}

function drawGame() {
    const head = {x: snake[0].x + dx, y: snake[0].y + dy};
    snake.unshift(head);
    
    if (snake[0].x === food.x && snake[0].y === food.y) {
        score += 10;
        generateFood();
    } else {
        snake.pop();
    }

    // Очистка
    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Сетка (тонкая)
    ctx.strokeStyle = '#252540';
    ctx.lineWidth = 0.5;
    for (let i = 0; i < tileCount; i++) {
        ctx.beginPath();
        ctx.moveTo(i * gridSize, 0);
        ctx.lineTo(i * gridSize, canvas.height);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(0, i * gridSize);
        ctx.lineTo(canvas.width, i * gridSize);
        ctx.stroke();
    }

    // Змейка
    ctx.fillStyle = '#00ff00';
    snake.forEach((part, i) => {
        ctx.fillStyle = i === 0 ? '#00ff00' : '#00cc00';
        ctx.fillRect(part.x * gridSize + 1, part.y * gridSize + 1, gridSize - 2, gridSize - 2);
    });

    // Еда
    ctx.fillStyle = '#ff4444';
    ctx.beginPath();
    ctx.arc(food.x * gridSize + gridSize/2, food.y * gridSize + gridSize/2, gridSize/2 - 2, 0, Math.PI * 2);
    ctx.fill();

    // Счёт
    ctx.fillStyle = '#ffffff';
    ctx.font = '16px Arial';
    ctx.fillText('Score: ' + score, 10, 20);

    // Проверка столкновений
    if (snake[0].x < 0 || snake[0].x >= tileCount || snake[0].y < 0 || snake[0].y >= tileCount) {
        gameOver();
        return;
    }
    for(let i = 1; i < snake.length; i++) {
        if(snake[i].x === snake[0].x && snake[i].y === snake[0].y) {
            gameOver();
            return;
        }
    }
}

function generateFood() {
    food.x = Math.floor(Math.random() * tileCount);
    food.y = Math.floor(Math.random() * tileCount);
}

function gameOver() {
    clearInterval(gameLoop);
    gameLoop = null;
    document.removeEventListener('keydown', changeDirection);
    
    // Экран окончания игры
    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#ff4444';
    ctx.font = '30px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Game Over!', canvas.width/2, canvas.height/2 - 20);
    ctx.fillStyle = '#ffffff';
    ctx.font = '20px Arial';
    ctx.fillText('Score: ' + score, canvas.width/2, canvas.height/2 + 20);
    ctx.textAlign = 'left';
    
    submitScore(score);
}

function startGame() {
    if (gameLoop) clearInterval(gameLoop);
    snake = [{x: 10, y: 10}];
    dx = 1; dy = 0;
    score = 0;
    generateFood();
    document.addEventListener('keydown', changeDirection);
    gameLoop = setInterval(drawGame, 200);
}

startGame();
"""

# Динозаврик — использует переданные canvas, ctx, submitScore
dino_js = """
// Настройка canvas
canvas.width = 600;
canvas.height = 250;
canvas.style.backgroundColor = '#87CEEB';

const dino = {
    x: 50,
    y: 180,
    width: 40,
    height: 50,
    velocityY: 0,
    jumping: false
};

const gravity = 0.8;
const jumpForce = -15;
let obstacles = [];
let score = 0;
let gameSpeed = 6;
let gameRunning = false;
let animFrame = null;

document.addEventListener('keydown', (e) => {
    if ((e.code === 'Space' || e.code === 'ArrowUp') && !dino.jumping && gameRunning) {
        e.preventDefault();
        dino.velocityY = jumpForce;
        dino.jumping = true;
    }
});

function update() {
    dino.velocityY += gravity;
    dino.y += dino.velocityY;

    if (dino.y >= 180) {
        dino.y = 180;
        dino.velocityY = 0;
        dino.jumping = false;
    }

    // Генерация препятствий
    if (Math.random() < 0.015) {
        obstacles.push({
            x: 600,
            y: 200,
            width: 20 + Math.random() * 15,
            height: 30 + Math.random() * 20
        });
    }

    for (let i = obstacles.length - 1; i >= 0; i--) {
        obstacles[i].x -= gameSpeed;
        
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
    // Небо
    ctx.fillStyle = '#87CEEB';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Солнце
    ctx.fillStyle = '#FFD700';
    ctx.beginPath();
    ctx.arc(520, 40, 25, 0, Math.PI * 2);
    ctx.fill();
    
    // Облака
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.arc(100, 40, 20, 0, Math.PI * 2);
    ctx.arc(130, 35, 25, 0, Math.PI * 2);
    ctx.arc(160, 40, 20, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(350, 50, 15, 0, Math.PI * 2);
    ctx.arc(375, 45, 20, 0, Math.PI * 2);
    ctx.arc(400, 50, 15, 0, Math.PI * 2);
    ctx.fill();

    // Земля
    ctx.fillStyle = '#8B4513';
    ctx.fillRect(0, 230, canvas.width, 20);
    ctx.fillStyle = '#228B22';
    ctx.fillRect(0, 225, canvas.width, 8);

    // Динозавр (милый кубик с глазами)
    ctx.fillStyle = '#4CAF50';
    ctx.fillRect(dino.x, dino.y, dino.width, dino.height);
    // Глаза
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(dino.x + 25, dino.y + 10, 10, 10);
    ctx.fillStyle = '#000000';
    ctx.fillRect(dino.x + 30, dino.y + 13, 5, 5);
    // Ножки
    ctx.fillStyle = '#388E3C';
    if (Math.floor(Date.now() / 100) % 2 === 0) {
        ctx.fillRect(dino.x + 5, dino.y + dino.height, 10, 10);
        ctx.fillRect(dino.x + 25, dino.y + dino.height, 10, 10);
    } else {
        ctx.fillRect(dino.x + 10, dino.y + dino.height, 10, 10);
        ctx.fillRect(dino.x + 20, dino.y + dino.height, 10, 10);
    }

    // Препятствия (кактусы)
    obstacles.forEach(obs => {
        ctx.fillStyle = '#2E7D32';
        ctx.fillRect(obs.x, obs.y, obs.width, obs.height);
        ctx.fillStyle = '#1B5E20';
        ctx.fillRect(obs.x + 2, obs.y + 2, obs.width - 4, obs.height - 4);
    });

    // Счёт
    ctx.fillStyle = '#333333';
    ctx.font = 'bold 18px Arial';
    ctx.fillText('Score: ' + score, 10, 30);
}

function gameLoopFn() {
    if (!gameRunning) return;
    update();
    draw();
    animFrame = requestAnimationFrame(gameLoopFn);
}

function startGame() {
    if (gameRunning) return;
    obstacles = [];
    score = 0;
    dino.y = 180;
    dino.velocityY = 0;
    gameRunning = true;
    gameLoopFn();
}

function gameOver() {
    gameRunning = false;
    cancelAnimationFrame(animFrame);
    
    // Экран окончания игры
    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#ff4444';
    ctx.font = 'bold 30px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Game Over!', canvas.width/2, canvas.height/2 - 20);
    ctx.fillStyle = '#ffffff';
    ctx.font = '20px Arial';
    ctx.fillText('Score: ' + score, canvas.width/2, canvas.height/2 + 20);
    ctx.textAlign = 'left';
    
    submitScore(score);
}

startGame();
"""

# Удаляем старые игры и создаём новые
Game.objects.filter(slug='snake').delete()
Game.objects.filter(slug='dino').delete()

Game.objects.create(
    slug='snake',
    title='Змейка',
    description='Классическая игра Змейка. Управление: стрелки. Собирайте красные яблоки!',
    js_code=snake_js,
    is_published=True
)

Game.objects.create(
    slug='dino',
    title='Динозаврик',
    description='Прыгайте через кактусы! Управление: Пробел или стрелка вверх.',
    js_code=dino_js,
    is_published=True
)

print('Games updated successfully!')

import streamlit as st
import streamlit.components.v1 as components
import base64

st.set_page_config(page_title="Game Bắn Xe Tăng 2D", layout="centered")
st.title("🪖 Game Bắn Xe Tăng 2D (Battle City Classic)")

game_code = """
<!DOCTYPE html>
<html>
<head>
<meta charset='utf-8'>
<style>
  body { margin: 0; padding: 5px; text-align: center; font-family: sans-serif; background: #0f0f1a; color: white; }
  canvas { background: #111; display: block; margin: 5px auto; border-radius: 12px; box-shadow: 0 8px 20px rgba(0,0,0,0.6); cursor: crosshair; }
</style>
</head>
<body>
<canvas id='c' width='480' height='480'></canvas>
<script>
const cvs = document.getElementById('c'), ctx = cvs.getContext('2d');
let gameState = 'MENU';
let score = 0, lives = 3, healCounter = 0, lastShotTime = 0;
let level = 1, enemiesTotal = 5, enemiesSpawned = 0, enemiesDefeated = 0;
let isCharging = false, chargeStart = 0;
let player = {x: 200, y: 400, size: 28, speed: 2.5, dir: 0, color: '#FF5964', hp: 10, maxHp: 10};
let bullets = [], enemies = [], keys = {};
let hqHp = 20, hqMaxHp = 20, mapGrid = [], gridSize = 16, tileSize = 30;

window.addEventListener('keydown', e => {
    if(['ArrowUp','ArrowDown','ArrowLeft','ArrowRight','Space'].includes(e.code)) e.preventDefault();
    keys[e.code] = true;
});
window.addEventListener('keyup', e => { keys[e.code] = false; });

cvs.addEventListener('click', e => {
    let rect = cvs.getBoundingClientRect();
    let mouseX = e.clientX - rect.left;
    let mouseY = e.clientY - rect.top;
    
    if(gameState === 'MENU'){
        // 10 levels dạng lưới 5 cột x 2 hàng
        let startX = 45, startY = 120, btnW = 75, btnH = 36, gapX = 12, gapY = 12;
        for(let i = 1; i <= 10; i++){
            let r = Math.floor((i - 1) / 5), c = (i - 1) % 5;
            let bx = startX + c * (btnW + gapX), by = startY + r * (btnH + gapY);
            if(mouseX >= bx && mouseX <= bx + btnW && mouseY >= by && mouseY <= by + btnH){
                startGame(i);
                break;
            }
        }
    } else if(gameState === 'PLAYING'){
        // Nút THOÁT ra MENU góc trên phải khi đang chơi
        if(mouseX >= cvs.width - 85 && mouseX <= cvs.width - 10 && mouseY >= 10 && mouseY <= 32){
            gameState = 'MENU';
        }
    } else if(gameState === 'GAMEOVER' || gameState === 'VICTORY'){
        let cx = cvs.width / 2, cy = cvs.height / 2;
        if(mouseX >= cx - 90 && mouseX <= cx + 90 && mouseY >= cy + 30 && mouseY <= cy + 70){
            gameState = 'MENU';
        }
    }
});

cvs.addEventListener('mousedown', () => {
    if(gameState !== 'PLAYING') return;
    let now = Date.now();
    if(now - lastShotTime >= 200){ isCharging = true; chargeStart = now; }
});

cvs.addEventListener('mouseup', () => {
    if(!isCharging || gameState !== 'PLAYING') return;
    isCharging = false;
    let duration = (Date.now() - chargeStart) / 1000, dmg = 1, bSize = 8, bColor = '#FFE600';
    if(duration >= 4.5){ dmg = 5; bSize = 18; bColor = '#00F5D4'; }
    else if(duration >= 3.0){ dmg = 4; bSize = 15; bColor = '#F72585'; }
    else if(duration >= 1.5){ dmg = 3; bSize = 12; bColor = '#4CC9F0'; }
    else if(duration >= 0.5){ dmg = 2; bSize = 10; bColor = '#FB8500'; }
    lastShotTime = Date.now();
    shootPlayer(dmg, bSize, bColor);
});

function startGame(lvl){
    level = lvl;
    // Mở rộng từ 16x16 lên tối đa 25x25 cho 10 level
    gridSize = 16 + Math.floor((level - 1) * 9 / 9);
    tileSize = cvs.width / gridSize;
    enemiesTotal = 5 + (level - 1) * 2;
    mapGrid = [];
    for(let r = 0; r < gridSize; r++){
        let row = [];
        for(let c = 0; c < gridSize; c++){
            if(r === gridSize - 1 && c === Math.floor(gridSize / 2)){ row.push(3); }
            else if((r % 3 === 1) && (c % 4 === 1)){ row.push(2); }
            else if((r % 2 === 0 && c % 3 === 0) && r > 0 && r < gridSize - 2){ row.push(1); }
            else { row.push(0); }
        }
        mapGrid.push(row);
    }
    enemiesSpawned = 0; enemiesDefeated = 0;
    enemies = []; bullets = [];
    player.size = Math.max(14, tileSize - 4);
    player.x = (gridSize * tileSize) / 2 - player.size / 2;
    player.y = (gridSize - 2) * tileSize;
    player.hp = player.maxHp;
    hqHp = 20; hqMaxHp = 20;
    score = 0; lives = 3; gameState = 'PLAYING';
}

function shootPlayer(dmg, bSize, bColor){
    let bx = player.x + player.size/2, by = player.y + player.size/2, bdx = 0, bdy = 0;
    if(player.dir === 0) bdy = -6;
    else if(player.dir === 1) bdx = 6;
    else if(player.dir === 2) bdy = 6;
    else if(player.dir === 3) bdx = -6;
    bullets.push({x: bx - bSize/2, y: by - bSize/2, w: bSize, h: bSize, dx: bdx, dy: bdy, fromPlayer: true, damage: dmg, color: bColor});
}

function checkCollision(x, y, size){
    let left = x, right = x + size, top = y, bottom = y + size;
    if(left < 0 || right > cvs.width || top < 0 || bottom > cvs.height) return true;
    let r

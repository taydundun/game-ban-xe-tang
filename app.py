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
  body { margin: 0; padding: 10px; text-align: center; font-family: sans-serif; background: #0f0f1a; color: white; }
  canvas { background: #111; display: block; margin: 10px auto; border-radius: 12px; box-shadow: 0 8px 20px rgba(0,0,0,0.6); cursor: crosshair; }
</style>
</head>
<body>
<canvas id='c' width='400' height='400'></canvas>
<script>
const cvs = document.getElementById('c'), ctx = cvs.getContext('2d');
let gameState = 'MENU';
let score = 0, lives = 3, healCounter = 0, lastShotTime = 0;
let level = 1, enemiesTotal = 5, enemiesSpawned = 0, enemiesDefeated = 0;
let isCharging = false, chargeStart = 0;
let player = {x: 180, y: 320, size: 28, speed: 2, dir: 0, color: '#FF5964', hp: 10, maxHp: 10};
let bullets = [], enemies = [], keys = {};
let hqAlive = true, mapGrid = [], gridSize = 10, tileSize = 40;

window.addEventListener('keydown', e => { keys[e.code] = true; });
window.addEventListener('keyup', e => { keys[e.code] = false; });

cvs.addEventListener('click', e => {
    let rect = cvs.getBoundingClientRect();
    let mouseX = e.clientX - rect.left;
    let mouseY = e.clientY - rect.top;
    if(gameState === 'MENU'){
        let cx = cvs.width / 2;
        if(mouseX >= cx - 100 && mouseX <= cx + 100 && mouseY >= 180 && mouseY <= 230) startGame(1);
        else if(mouseX >= cx - 100 && mouseX <= cx + 100 && mouseY >= 250 && mouseY <= 300) startGame(2);
        else if(mouseX >= cx - 100 && mouseX <= cx + 100 && mouseY >= 320 && mouseY <= 370) startGame(3);
    } else if(gameState === 'GAMEOVER' || gameState === 'VICTORY'){
        let cx = cvs.width / 2, cy = cvs.height / 2;
        if(mouseX >= cx - 100 && mouseX <= cx + 100 && mouseY >= cy + 40 && mouseY <= cy + 90) gameState = 'MENU';
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
    if(level === 1){ gridSize = 10; enemiesTotal = 5; }
    else if(level === 2){ gridSize = 12; enemiesTotal = 8; }
    else if(level === 3){ gridSize = 14; enemiesTotal = 12; }
    cvs.width = gridSize * tileSize;
    cvs.height = gridSize * tileSize;
    mapGrid = [];
    for(let r = 0; r < gridSize; r++){
        let row = [];
        for(let c = 0; c < gridSize; c++){
            if(r === gridSize - 1 && c === Math.floor(gridSize / 2)){ row.push(3); }
            else if((r === 1 || r === gridSize - 3) && (c === 2 || c === gridSize - 3)){ row.push(2); }
            else if((r % 2 === 0 && c % 3 === 0) && r > 0 && r < gridSize - 2){ row.push(1); }
            else { row.push(0); }
        }
        mapGrid.push(row);
    }
    enemiesSpawned = 0; enemiesDefeated = 0;
    enemies = []; bullets = [];
    player.x = (gridSize * tileSize) / 2 - 14;
    player.y = (gridSize - 2) * tileSize;
    player.hp = player.maxHp;
    hqAlive = true; score = 0; lives = 3;
    gameState = 'PLAYING';
}

function shootPlayer(dmg, bSize, bColor){
    let bx = player.x + player.size/2, by = player.y + player.size/2, bdx = 0, bdy = 0;
    if(player.dir === 0) bdy = -5;
    else if(player.dir === 1) bdx = 5;
    else if(player.dir === 2) bdy = 5;
    else if(player.dir === 3) bdx = -5;
    bullets.push({x: bx - bSize/2, y: by - bSize/2, w: bSize, h: bSize, dx: bdx, dy: bdy, fromPlayer: true, damage: dmg, color: bColor});
}

function checkCollision(x, y, size){
    let left = x, right = x + size, top = y, bottom = y + size;
    if(left < 0 || right > cvs.width || top < 0 || bottom > cvs.height) return true;
    let r1 = Math.floor(top/tileSize), r2 = Math.floor(bottom/tileSize), c1 = Math.floor(left/tileSize), c2 = Math.floor(right/tileSize);
    for(let r = r1; r <= r2; r++){
        for(let c = c1; c <= c2; c++){
            if(r >= 0 && r < gridSize && c >= 0 && c < gridSize){
                if(mapGrid[r][c] === 1 || mapGrid[r][c] === 2 || (mapGrid[r][c] === 3 && hqAlive)) return true;
            }
        }
    }
    return false;
}

function spawnEnemy(){
    if(gameState === 'PLAYING' && enemies.length < 3 && enemiesSpawned < enemiesTotal){
        let size = 28, ex, eyn = 20, safe = false, attempts = 0;
        while(!safe && attempts < 15){
            ex = Math.random() * (cvs.width - size - 20) + 10;
            if(!checkCollision(ex, eyn, size)){ safe = true; }
            attempts++;
        }
        if(safe){
            let eSpeed = 1 + (level - 1) * 0.2, eHp = 10 + (level - 1) * 2;
            enemies.push({x: ex, y: eyn, size: size, speed: eSpeed, dir: 2, color: '#35A7FF', shootTimer: 0, hp: eHp, maxHp: eHp});
            enemiesSpawned++;
        }
    }
}
setInterval(spawnEnemy, 2500);

function update(){
    if(gameState !== 'PLAYING') return;
    healCounter++;
    if(healCounter >= 300){
        healCounter = 0;
        if(player.hp < player.maxHp) player.hp = Math.min(player.maxHp, player.hp + 0

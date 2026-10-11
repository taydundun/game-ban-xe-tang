import streamlit as st
import streamlit.components.v1 as components
import base64

st.set_page_config(page_title="Game Bắn Xe Tăng 2D", layout="centered")
st.title("🪖 Game Bắn Xe Tăng 2D (Battle City Classic)")

html_code = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8">
<style>
body { margin: 0; text-align: center; font-family: sans-serif; background: #0f0f1a; color: white; }
canvas { background: #111; display: block; margin: 10px auto; border-radius: 12px; box-shadow: 0 8px 20px rgba(0,0,0,0.6); cursor: crosshair; }
</style>
</head>
<body>
<canvas id="c" width="480" height="480"></canvas>
<script>
const cvs = document.getElementById("c"), ctx = cvs.getContext("2d");
let score = 0, lives = 3, gameOver = false, healCounter = 0;

// Hướng: 0: Lên, 1: Phải, 2: Xuống, 3: Trái
let player = { x: 200, y: 400, size: 28, speed: 2, dir: 0, color: "#FF5964", hp: 10, maxHp: 10 };
let bullets = [], enemies = [];
let keys = {};

// Bản đồ tường: 1 = Gạch (bắn vỡ được), 2 = Thép (bất tử)
let mapGrid = [
    [0,0,0,0,0,0,0,0,0,0,0,0],
    [0,1,1,0,2,2,0,1,1,0,0,0],
    [0,1,0,0,0,0,0,0,1,1,0,0],
    [0,0,0,1,1,1,1,0,0,0,0,0],
    [0,2,0,1,0,0,1,0,2,2,0,0],
    [0,0,0,1,0,0,1,0,0,0,0,0],
    [0,0,0,0,1,1,0,0,0,0,0,0],
    [0,1,1,0,0,0,0,1,1,0,2,0],
    [0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,2,2,0,0,2,2,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0]
];
let tileSize = 40;

window.addEventListener("keydown", e => { keys[e.code] = true; });
window.addEventListener("keyup", e => { keys[e.code] = false; });

cvs.addEventListener("click", () => {
    if (gameOver) return;
    shootPlayer();
});

function shootPlayer() {
    let bx = player.x + player.size/2, by = player.y + player.size/2;
    let bdx = 0, bdy = 0;
    if (player.dir === 0) bdy = -5;
    else if (player.dir === 1) bdx = 5;
    else if (player.dir === 2) bdy = 5;
    else if (player.dir === 3) bdx = -5;
    bullets.push({ x: bx-4, y: by-4, w: 8, h: 8, dx: bdx, dy: bdy, fromPlayer: true });
}

function spawnEnemy() {
    if (enemies.length < 3 && !gameOver) {
        let ex = Math.random() * (cvs.width - 40);
        enemies.push({ x: ex, y: 20, size: 28, speed: 1, dir: 2, color: "#35A7FF", shootTimer: 0, hp: 10, maxHp: 10 });
    }
}
setInterval(spawnEnemy, 3000);

function checkCollision(x, y, size) {
    let left = x, right = x + size, top = y, bottom = y + size;
    if (left < 0 || right > cvs.width || top < 0 || bottom > cvs.height) return true;
    
    let r1 = Math.floor(top / tileSize), r2 = Math.floor(bottom / tileSize);
    let c1 = Math.floor(left / tileSize), c2 = Math.floor(right / tileSize);
    
    for (let r = r1; r <= r2; r++) {
        for (let c = c1; c <= c2; c++) {
            if (r >= 0 && r < 12 && c >= 0 && c < 12) {
                if (mapGrid[r][c] > 0) return true;
            }
        }
    }
    return false;
}

function update() {
    if (gameOver) return;

    // Hồi 0.5/10 máu mỗi 5 giây (Giả sử 60 khung hình/giây -> 5 giây = 300 khung hình)
    healCounter++;
    if (healCounter >= 300) {
        healCounter = 0;
        if (player.hp < player.maxHp) {
            player.hp = Math.min(player.maxHp, player.hp + 0.5);
        }
    }

    // Di chuyển Người chơi
    let moving = false;
    let nx = player.x, ny = player.y;
    if (keys["ArrowUp"] || keys["KeyW"]) { player.dir = 0; ny -= player.speed; moving = true; }
    else if (keys["ArrowDown"] || keys["KeyS"]) { player.dir = 2; ny += player.speed; moving = true; }
    else if (keys["ArrowLeft"] || keys["KeyA"]) { player.dir = 3; nx -= player.speed; moving = true; }
    else if (keys["ArrowRight"] || keys["KeyD"]) { player.dir = 1; nx += player.speed; moving = true; }

    if (moving) {
        if (!checkCollision(nx, player.y, player.size)) player.x = nx;
        if (!checkCollision(player.x, ny, player.size)) player.y = ny;
    }

    // Cập nhật Đạn
    bullets.forEach((b, index) => {
        b.x += b.dx; b.y += b.dy;
        
        let cr = Math.floor((b.y + b.h/2) / tileSize);
        let cc = Math.floor((b.x + b.w/2) / tileSize);
        if (cr >= 0 && cr < 12 && cc >= 0 && cc < 12) {
            if (mapGrid[cr][cc] === 1) {
                mapGrid[cr][cc] = 0;
                bullets.splice(index, 1);
                return;
            } else if (mapGrid[cr][cc] === 2) {
                bullets.splice(index, 1);
                return;
            }
        }

        if (b.x < 0 || b

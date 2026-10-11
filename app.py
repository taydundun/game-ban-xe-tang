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
canvas { background: #111; display: block; margin: 10px auto; border-radius: 12px; box-shadow: 0 8px 20px rgba(0,0,0,0.6); }
</style>
</head>
<body>
<canvas id="c" width="480" height="480"></canvas>
<script>
const cvs = document.getElementById("c"), ctx = cvs.getContext("2d");
let score = 0, lives = 3, gameOver = false;

// Hướng: 0: Lên, 1: Phải, 2: Xuống, 3: Trái
let player = { x: 200, y: 400, size: 28, speed: 2, dir: 0, color: "#FF5964" };
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

window.addEventListener("keydown", e => { keys[e.code] = true; if(e.code === "Space") shootPlayer(); });
window.addEventListener("keyup", e => { keys[e.code] = false; });

function shootPlayer() {
    if (gameOver) return;
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
        enemies.push({ x: ex, y: 20, size: 28, speed: 1, dir: 2, color: "#35A7FF", shootTimer: 0 });
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

    // Di chuyển Người chơi (Chỉ 4 hướng ngang/dọc)
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
        
        // Kiểm tra va chạm đạn với tường
        let cr = Math.floor((b.y + b.h/2) / tileSize);
        let cc = Math.floor((b.x + b.w/2) / tileSize);
        if (cr >= 0 && cr < 12 && cc >= 0 && cc < 12) {
            if (mapGrid[cr][cc] === 1) {
                mapGrid[cr][cc] = 0; // Phá tường gạch
                bullets.splice(index, 1);
                return;
            } else if (mapGrid[cr][cc] === 2) {
                bullets.splice(index, 1); // Đạn mất khi trúng thép
                return;
            }
        }

        // Đạn ra ngoài màn hình
        if (b.x < 0 || b.x > cvs.width || b.y < 0 || b.y > cvs.height) {
            bullets.splice(index, 1);
            return;
        }

        // Đạn người chơi bắn địch
        if (b.fromPlayer) {
            enemies.forEach((en, eIdx) => {
                if (b.x < en.x + en.size && b.x + b.w > en.x && b.y < en.y + en.size && b.y + b.h > en.y) {
                    enemies.splice(eIdx, 1);
                    bullets.splice(index, 1);
                    score += 100;
                }
            });
        } else {
            // Đạn địch bắn người chơi
            if (b.x < player.x + player.size && b.x + b.w > player.x && b.y < player.y + player.size && b.y + b.h > player.y) {
                lives--;
                bullets.splice(index, 1);
                if (lives <= 0) gameOver = true;
                else { player.x = 200; player.y = 400; }
            }
        }
    });

    // Cập nhật Kẻ địch đơn giản
    enemies.forEach(en => {
        en.shootTimer++;
        if (en.shootTimer > 90) {
            en.shootTimer = 0;
            let edx = 0, edy = 0;
            if (en.dir === 0) edy = -4;
            else if (en.dir === 1) edx = 4;
            else if (en.dir === 2) edy = 4;
            else if (en.dir === 3) edx = -4;
            bullets.push({ x: en.x + en.size/2 - 4, y: en.y + en.size/2 - 4, w: 8, h: 8, dx: edx, dy: edy, fromPlayer: false });
        }
        
        // Địch di chuyển ngẫu nhiên đơn giản
        let exn = en.x, eyn = en.y;
        if (en.dir === 0) eyn -= en.speed;
        else if (en.dir === 1) exn += en.speed;
        else if (en.dir === 2) eyn += en.speed;
        else if (en.dir === 3) exn -= en.speed;

        if (!checkCollision(exn, eyn, en.size)) {
            en.x = exn; en.y = eyn;
        } else {
            en.dir = Math.floor(Math.random() * 4);
        }
    });
}

function drawTank(t) {
    ctx.save();
    ctx.translate(t.x + t.size/2, t.y + t.size/2);
    let angle = 0;
    if (t.dir === 1) angle = Math.PI/2;
    else if (t.dir === 2) angle = Math.PI;
    else if (t.dir === 3) angle = -Math.PI/2;
    ctx.rotate(angle);
    
    // Thân xe
    ctx.fillStyle = t.color;
    ctx.fillRect(-t.size/2, -t.size/2, t.size, t.size);
    // Nòng pháo
    ctx.fillStyle = "#FFF";
    ctx.fillRect(-3, -t.size/2 - 6, 6, 12);
    ctx.restore();
}

function draw() {
    ctx.clearRect(0, 0, cvs.width, cvs.height);

    // Vẽ Bản đồ
    for (let r = 0; r < 12; r++) {
        for (let c = 0; c < 12; c++) {
            if (mapGrid[r][c] === 1) {
                ctx.fillStyle = "#B22222"; // Gạch đỏ
                ctx.fillRect(c * tileSize, r * tileSize, tileSize - 2, tileSize - 2);
            } else if (mapGrid[r][c] === 2) {
                ctx.fillStyle = "#708090"; // Thép xám
                ctx.fillRect(c * tileSize, r * tileSize, tileSize - 2, tileSize - 2);
            }
        }
    }

    // Vẽ Điểm & Mạng
    ctx.fillStyle = "#FFF"; ctx.font = "bold 14px sans-serif";
    ctx.fillText("Điểm: " + score, 20, 20);
    ctx.fillText("Mạng: " + lives, 410, 20);

    // Vẽ Xe tăng người chơi & Địch
    drawTank(player);
    enemies.forEach(en => drawTank(en));

    // Vẽ Đạn
    ctx.fillStyle = "#FFE600";
    bullets.forEach(b => ctx.fillRect(b.x, b.y, b.w, b.h));

    if (gameOver) {
        ctx.fillStyle = "rgba(0,0,0,0.85)"; ctx.fillRect(0, 0, cvs.width, cvs.height);
        ctx.fillStyle = "#FF5964"; ctx.font = "bold 32px sans-serif"; ctx.textAlign = "center";
        ctx.fillText("GAME OVER", cvs.width/2, cvs.height/2 - 20);
        ctx.fillStyle = "#FFF"; ctx.font = "16px sans-serif";
        ctx.fillText("Tổng điểm: " + score, cvs.width/2, cvs.height/2 + 20);
        ctx.textAlign = "left";
    }
}

function loop() { update(); draw(); requestAnimationFrame(loop); }
loop();
</script>
</body>
</html>
"""

encoded_html = base64.b64encode(html_code.encode("utf-8")).decode("utf-8")
components.iframe(f"data:text/html;base64,{encoded_html}", height=520)

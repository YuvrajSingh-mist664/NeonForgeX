const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const startPanel = document.getElementById("startPanel");
const gameOverPanel = document.getElementById("gameOverPanel");
const startButton = document.getElementById("startButton");
const restartButton = document.getElementById("restartButton");
const scoreLabel = document.getElementById("scoreLabel");
const healthLabel = document.getElementById("healthLabel");
const waveLabel = document.getElementById("waveLabel");
const bestLabel = document.getElementById("bestLabel");
const finalScore = document.getElementById("finalScore");

const keys = new Set();
const pointer = { active: false, x: 0, y: 0 };
const rand = (min, max) => Math.random() * (max - min) + min;
const clamp = (value, min, max) => Math.max(min, Math.min(max, value));

let width = 0;
let height = 0;
let dpr = 1;
let lastTime = 0;
let spawnTimer = 0;
let shotTimer = 0;
let shake = 0;
let bestScore = Number(localStorage.getItem("neonforgex-best") || 0);

const game = {
    mode: "menu",
    score: 0,
    health: 100,
    wave: 1,
    time: 0,
    player: { x: 0, y: 0, radius: 22, cooldown: 0 },
    bullets: [],
    enemies: [],
    sparks: [],
    pickups: [],
    stars: []
};

function resize() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = Math.floor(width * dpr);
    canvas.height = Math.floor(height * dpr);
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    game.player.x = game.player.x || width / 2;
    game.player.y = height - 110;
    seedStars();
}

function seedStars() {
    const count = Math.max(80, Math.floor((width * height) / 11000));
    game.stars = Array.from({ length: count }, () => ({
        x: rand(0, width),
        y: rand(0, height),
        size: rand(0.7, 2.4),
        speed: rand(16, 64),
        tint: Math.random() > 0.66 ? "#37e4ff" : Math.random() > 0.5 ? "#9cff4f" : "#ffffff"
    }));
}

function resetGame() {
    game.mode = "playing";
    game.score = 0;
    game.health = 100;
    game.wave = 1;
    game.time = 0;
    game.player = { x: width / 2, y: height - 112, radius: Math.max(18, Math.min(30, width * 0.027)), cooldown: 0 };
    game.bullets = [];
    game.enemies = [];
    game.sparks = [];
    game.pickups = [];
    spawnTimer = 0;
    shotTimer = 0;
    shake = 0;
    startPanel.classList.add("is-hidden");
    gameOverPanel.classList.add("is-hidden");
    updateHud();
}

function endGame() {
    game.mode = "over";
    bestScore = Math.max(bestScore, Math.floor(game.score));
    localStorage.setItem("neonforgex-best", String(bestScore));
    finalScore.textContent = `Score ${Math.floor(game.score)}`;
    gameOverPanel.classList.remove("is-hidden");
    updateHud();
}

function updateHud() {
    scoreLabel.textContent = `Score ${Math.floor(game.score)}`;
    healthLabel.textContent = `Hull ${Math.max(0, Math.ceil(game.health))}`;
    waveLabel.textContent = `Wave ${game.wave}`;
    bestLabel.textContent = `Best ${bestScore}`;
}

function createEnemy() {
    const roll = Math.random();
    const type = roll > 0.82 ? "brute" : roll > 0.45 ? "drone" : "shard";
    const radius = type === "brute" ? 28 : type === "drone" ? 22 : 17;
    const hp = type === "brute" ? 5 : type === "drone" ? 3 : 1;
    const speed = rand(78, 138) + game.wave * 8 - radius;
    game.enemies.push({
        type,
        x: rand(radius + 16, width - radius - 16),
        y: -radius - rand(0, 160),
        radius,
        hp,
        maxHp: hp,
        speed,
        spin: rand(-2.2, 2.2),
        sway: rand(0.4, 1.4),
        phase: rand(0, Math.PI * 2)
    });
}

function fire() {
    const p = game.player;
    game.bullets.push({ x: p.x, y: p.y - p.radius, vx: 0, vy: -620, radius: 5, power: 1 });
    game.bullets.push({ x: p.x - p.radius * 0.55, y: p.y - 8, vx: -34, vy: -560, radius: 4, power: 1 });
    game.bullets.push({ x: p.x + p.radius * 0.55, y: p.y - 8, vx: 34, vy: -560, radius: 4, power: 1 });
}

function burst(x, y, color, amount = 14) {
    for (let i = 0; i < amount; i += 1) {
        const angle = rand(0, Math.PI * 2);
        const speed = rand(60, 280);
        game.sparks.push({
            x,
            y,
            vx: Math.cos(angle) * speed,
            vy: Math.sin(angle) * speed,
            radius: rand(1.5, 4.5),
            life: rand(0.35, 0.8),
            maxLife: 0.8,
            color
        });
    }
}

function damagePlayer(amount) {
    game.health -= amount;
    shake = Math.min(16, shake + amount * 0.45);
    burst(game.player.x, game.player.y, "#ff3d81", 18);
    if (game.health <= 0) {
        endGame();
    }
}

function update(dt) {
    game.time += dt;
    if (game.mode !== "playing") {
        updateBackground(dt);
        updateSparks(dt);
        return;
    }

    updatePlayer(dt);
    updateShots(dt);
    updateEnemies(dt);
    updatePickups(dt);
    updateSparks(dt);
    updateBackground(dt);

    game.wave = 1 + Math.floor(game.score / 850);
    game.score += dt * (12 + game.wave);
    shake = Math.max(0, shake - dt * 30);
    updateHud();
}

function updatePlayer(dt) {
    const p = game.player;
    const speed = 370 + Math.min(game.wave, 8) * 14;
    let dx = 0;
    let dy = 0;

    if (keys.has("arrowleft") || keys.has("a")) dx -= 1;
    if (keys.has("arrowright") || keys.has("d")) dx += 1;
    if (keys.has("arrowup") || keys.has("w")) dy -= 1;
    if (keys.has("arrowdown") || keys.has("s")) dy += 1;

    if (dx || dy) {
        const length = Math.hypot(dx, dy);
        p.x += (dx / length) * speed * dt;
        p.y += (dy / length) * speed * dt;
    }

    if (pointer.active) {
        p.x += (pointer.x - p.x) * Math.min(1, dt * 9);
        p.y += (pointer.y - p.y) * Math.min(1, dt * 9);
    }

    p.x = clamp(p.x, p.radius + 12, width - p.radius - 12);
    p.y = clamp(p.y, height * 0.25, height - p.radius - 24);
}

function updateShots(dt) {
    shotTimer -= dt;
    if (shotTimer <= 0) {
        fire();
        shotTimer = keys.has(" ") ? 0.09 : 0.15;
    }

    for (const bullet of game.bullets) {
        bullet.x += bullet.vx * dt;
        bullet.y += bullet.vy * dt;
    }
    game.bullets = game.bullets.filter((bullet) => bullet.y > -40 && bullet.x > -40 && bullet.x < width + 40);
}

function updateEnemies(dt) {
    spawnTimer -= dt;
    if (spawnTimer <= 0) {
        createEnemy();
        spawnTimer = Math.max(0.24, 0.9 - game.wave * 0.045);
    }

    for (const enemy of game.enemies) {
        enemy.y += enemy.speed * dt;
        enemy.x += Math.sin(game.time * enemy.sway + enemy.phase) * (25 + game.wave) * dt;

        for (const bullet of game.bullets) {
            if (distance(enemy, bullet) < enemy.radius + bullet.radius) {
                enemy.hp -= bullet.power;
                bullet.y = -999;
                burst(bullet.x, bullet.y + 14, "#37e4ff", 4);
            }
        }

        if (distance(enemy, game.player) < enemy.radius + game.player.radius) {
            enemy.hp = 0;
            damagePlayer(enemy.type === "brute" ? 24 : 16);
        }

        if (enemy.y > height + enemy.radius) {
            enemy.hp = 0;
            damagePlayer(enemy.type === "brute" ? 12 : 8);
        }

        if (enemy.hp <= 0) {
            const value = enemy.type === "brute" ? 90 : enemy.type === "drone" ? 55 : 30;
            game.score += value;
            burst(enemy.x, enemy.y, enemy.type === "brute" ? "#ffb84f" : "#9cff4f", enemy.type === "brute" ? 28 : 16);
            if (Math.random() > 0.72) {
                game.pickups.push({ x: enemy.x, y: enemy.y, radius: 10, vy: 130 });
            }
        }
    }

    game.bullets = game.bullets.filter((bullet) => bullet.y > -100);
    game.enemies = game.enemies.filter((enemy) => enemy.hp > 0);
}

function updatePickups(dt) {
    for (const pickup of game.pickups) {
        pickup.y += pickup.vy * dt;
        pickup.x += Math.sin(game.time * 4 + pickup.y * 0.01) * 30 * dt;

        if (distance(pickup, game.player) < pickup.radius + game.player.radius) {
            pickup.y = height + 999;
            game.score += 120;
            game.health = Math.min(100, game.health + 4);
            burst(pickup.x, pickup.y, "#f8ff6a", 12);
        }
    }

    game.pickups = game.pickups.filter((pickup) => pickup.y < height + 60);
}

function updateSparks(dt) {
    for (const spark of game.sparks) {
        spark.x += spark.vx * dt;
        spark.y += spark.vy * dt;
        spark.vx *= 0.96;
        spark.vy *= 0.96;
        spark.life -= dt;
    }
    game.sparks = game.sparks.filter((spark) => spark.life > 0);
}

function updateBackground(dt) {
    for (const star of game.stars) {
        star.y += star.speed * dt * (game.mode === "playing" ? 1.5 : 0.6);
        if (star.y > height + 8) {
            star.y = -8;
            star.x = rand(0, width);
        }
    }
}

function distance(a, b) {
    return Math.hypot(a.x - b.x, a.y - b.y);
}

function draw() {
    ctx.save();
    ctx.clearRect(0, 0, width, height);
    drawBackground();

    if (shake > 0) {
        ctx.translate(rand(-shake, shake), rand(-shake, shake));
    }

    drawPickups();
    drawBullets();
    drawEnemies();
    drawPlayer();
    drawSparks();
    ctx.restore();
}

function drawBackground() {
    const gradient = ctx.createLinearGradient(0, 0, width, height);
    gradient.addColorStop(0, "#03060d");
    gradient.addColorStop(0.55, "#061827");
    gradient.addColorStop(1, "#0b0914");
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);

    ctx.globalAlpha = 0.78;
    for (const star of game.stars) {
        ctx.fillStyle = star.tint;
        ctx.fillRect(star.x, star.y, star.size, star.size * 2.3);
    }
    ctx.globalAlpha = 1;

    const horizon = height * 0.2;
    ctx.strokeStyle = "rgba(55, 228, 255, 0.16)";
    ctx.lineWidth = 1;
    for (let y = horizon; y < height + 80; y += 42) {
        const depth = (y - horizon) / Math.max(1, height - horizon);
        ctx.beginPath();
        ctx.moveTo(0, y + depth * depth * 160);
        ctx.lineTo(width, y + depth * depth * 160);
        ctx.stroke();
    }
    for (let i = -8; i <= 8; i += 1) {
        const x = width / 2 + i * width * 0.095;
        ctx.beginPath();
        ctx.moveTo(width / 2, horizon);
        ctx.lineTo(x, height);
        ctx.stroke();
    }
}

function drawPlayer() {
    const p = game.player;
    if (game.mode === "menu") return;

    ctx.save();
    ctx.translate(p.x, p.y);
    ctx.shadowColor = "#37e4ff";
    ctx.shadowBlur = 24;

    ctx.fillStyle = "#07131f";
    ctx.strokeStyle = "#37e4ff";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(0, -p.radius * 1.45);
    ctx.lineTo(p.radius * 1.05, p.radius * 1.1);
    ctx.lineTo(0, p.radius * 0.62);
    ctx.lineTo(-p.radius * 1.05, p.radius * 1.1);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = "#9cff4f";
    ctx.beginPath();
    ctx.arc(0, -p.radius * 0.24, p.radius * 0.26, 0, Math.PI * 2);
    ctx.fill();

    ctx.shadowColor = "#ff3d81";
    ctx.fillStyle = "#ff3d81";
    ctx.fillRect(-p.radius * 0.42, p.radius * 0.95, p.radius * 0.22, p.radius * 0.86);
    ctx.fillRect(p.radius * 0.2, p.radius * 0.95, p.radius * 0.22, p.radius * 0.86);
    ctx.restore();
}

function drawBullets() {
    ctx.save();
    ctx.shadowColor = "#37e4ff";
    ctx.shadowBlur = 16;
    for (const bullet of game.bullets) {
        ctx.fillStyle = "#c8fbff";
        ctx.beginPath();
        ctx.roundRect(bullet.x - bullet.radius, bullet.y - 12, bullet.radius * 2, 24, bullet.radius);
        ctx.fill();
    }
    ctx.restore();
}

function drawEnemies() {
    for (const enemy of game.enemies) {
        ctx.save();
        ctx.translate(enemy.x, enemy.y);
        ctx.rotate(game.time * enemy.spin);
        ctx.shadowColor = enemy.type === "brute" ? "#ffb84f" : "#ff3d81";
        ctx.shadowBlur = 18;
        ctx.fillStyle = enemy.type === "brute" ? "#341312" : enemy.type === "drone" ? "#230b2e" : "#2e0920";
        ctx.strokeStyle = enemy.type === "brute" ? "#ffb84f" : "#ff3d81";
        ctx.lineWidth = 2.5;
        ctx.beginPath();
        const sides = enemy.type === "brute" ? 6 : 4;
        for (let i = 0; i < sides; i += 1) {
            const angle = -Math.PI / 2 + (i / sides) * Math.PI * 2;
            const r = enemy.radius * (i % 2 ? 0.76 : 1);
            const x = Math.cos(angle) * r;
            const y = Math.sin(angle) * r;
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        ctx.closePath();
        ctx.fill();
        ctx.stroke();

        const hpWidth = enemy.radius * 1.8 * (enemy.hp / enemy.maxHp);
        ctx.fillStyle = "#9cff4f";
        ctx.fillRect(-enemy.radius * 0.9, enemy.radius + 8, hpWidth, 4);
        ctx.restore();
    }
}

function drawPickups() {
    for (const pickup of game.pickups) {
        ctx.save();
        ctx.translate(pickup.x, pickup.y);
        ctx.rotate(game.time * 4);
        ctx.shadowColor = "#f8ff6a";
        ctx.shadowBlur = 18;
        ctx.fillStyle = "#f8ff6a";
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(0, 0, pickup.radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
        ctx.restore();
    }
}

function drawSparks() {
    ctx.save();
    for (const spark of game.sparks) {
        const alpha = clamp(spark.life / spark.maxLife, 0, 1);
        ctx.globalAlpha = alpha;
        ctx.fillStyle = spark.color;
        ctx.beginPath();
        ctx.arc(spark.x, spark.y, spark.radius * alpha, 0, Math.PI * 2);
        ctx.fill();
    }
    ctx.globalAlpha = 1;
    ctx.restore();
}

function loop(timestamp) {
    const dt = Math.min(0.034, (timestamp - lastTime) / 1000 || 0);
    lastTime = timestamp;
    update(dt);
    draw();
    requestAnimationFrame(loop);
}

function canvasPoint(event) {
    const rect = canvas.getBoundingClientRect();
    return {
        x: event.clientX - rect.left,
        y: event.clientY - rect.top
    };
}

function setPointer(event, active = true) {
    const point = canvasPoint(event);
    pointer.active = active;
    pointer.x = point.x;
    pointer.y = point.y;
}

startButton.addEventListener("click", resetGame);
restartButton.addEventListener("click", resetGame);
window.addEventListener("resize", resize);
window.addEventListener("keydown", (event) => {
    if ([" ", "ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(event.key)) {
        event.preventDefault();
    }
    keys.add(event.key.toLowerCase());
    if ((event.key === "Enter" || event.key === " ") && game.mode !== "playing") {
        resetGame();
    }
});
window.addEventListener("keyup", (event) => keys.delete(event.key.toLowerCase()));

canvas.addEventListener("pointerdown", (event) => {
    canvas.setPointerCapture(event.pointerId);
    setPointer(event, true);
    if (game.mode !== "playing") resetGame();
});
canvas.addEventListener("pointermove", (event) => {
    if (pointer.active) setPointer(event, true);
});
canvas.addEventListener("pointerup", () => {
    pointer.active = false;
});
canvas.addEventListener("pointercancel", () => {
    pointer.active = false;
});

bestLabel.textContent = `Best ${bestScore}`;
resize();
requestAnimationFrame(loop);

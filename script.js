// 1. بيانات البطاقات المتاحة في اللعبة
const availableCards = [
    { name: "ضربة سيف", type: "attack", value: 20, desc: "تسبب 20 ضرر للخصم" },
    { name: "صاعقة سحرية", type: "attack", value: 30, desc: "تسبب 30 ضرر للخصم" },
    { name: "درع حديدي", type: "defense", value: 15, desc: "تضيف 15 نقطة درع حماية" },
    { name: "حواجز طاقة", type: "defense", value: 25, desc: "تضيف 25 نقطة درع حماية" },
    { name: "جرعة شفاء", type: "heal", value: 20, desc: "تعيد لك 20 نقطة حياة" }
];

// 2. حالة اللعبة الحالية (State)
let gameState = {
    playerHealth: 100,
    playerShield: 0,
    enemyHealth: 100,
    enemyShield: 0,
    isPlayerTurn: true,
    gameOver: false
};

// 3. جلب عناصر واجهة المستخدم (DOM Elements)
const playerHealthBar = document.getElementById("player-health-bar");
const playerHealthText = document.getElementById("player-health-text");
const playerShieldText = document.getElementById("player-shield-text");

const enemyHealthBar = document.getElementById("enemy-health-bar");
const enemyHealthText = document.getElementById("enemy-health-text");
const enemyShieldText = document.getElementById("enemy-shield-text");

const battleStatus = document.getElementById("battle-status");
const cardsHand = document.getElementById("cards-hand");

// 4. بدء اللعبة وتوليد بطاقات اللاعب
function initGame() {
    renderPlayerHand();
    updateUI();
}

// توليد 4 بطاقات عشوائية في يد اللاعب
function renderPlayerHand() {
    cardsHand.innerHTML = "";
    for (let i = 0; i < 4; i++) {
        const randomCard = availableCards[Math.floor(Math.random() * availableCards.length)];
        
        const cardElement = document.createElement("div");
        cardElement.className = `card ${randomCard.type}`;
        cardElement.innerHTML = `
            <div class="card-name">${randomCard.name}</div>
            <div class="card-desc">${randomCard.desc}</div>
            <div class="card-value">${randomCard.value}</div>
        `;
        
        // عند الضغط على البطاقة يتم لعبها
        cardElement.addEventListener("click", () => {
            if (gameState.isPlayerTurn && !gameState.gameOver) {
                playCard(randomCard, "player");
            }
        });
        
        cardsHand.appendChild(cardElement);
    }
}

// 5. منطق لعب البطاقة
function playCard(card, sender) {
    if (gameState.gameOver) return;

    if (sender === "player") {
        gameState.isPlayerTurn = false;
        cardsHand.classList.add("disabled"); // تعطيل الضغط على البطاقات

        // تنفيذ تأثير البطاقة على حسب نوعها
        if (card.type === "attack") {
            let damage = card.value;
            if (gameState.enemyShield > 0) {
                if (damage <= gameState.enemyShield) {
                    gameState.enemyShield -= damage;
                    damage = 0;
                } else {
                    damage -= gameState.enemyShield;
                    gameState.enemyShield = 0;
                }
            }
            gameState.enemyHealth = Math.max(0, gameState.enemyHealth - damage);
            battleStatus.innerText = `أنت استخدمت [${card.name}] وسببت ${card.value} ضرر للعدو!`;
        } 
        else if (card.type === "defense") {
            gameState.playerShield += card.value;
            battleStatus.innerText = `أنت استخدمت [${card.name}] وحصلت على ${card.value} درع حماية!`;
        } 
        else if (card.type === "heal") {
            gameState.playerHealth = Math.min(100, gameState.playerHealth + card.value);
            battleStatus.innerText = `أنت استخدمت [${card.name}] واستعدت ${card.value} نقاط حياة!`;
        }

        updateUI();
        checkGameOver();

        // انتقال الدور للكمبيوتر بعد ثانيتين
        if (!gameState.gameOver) {
            setTimeout(enemyTurn, 1500);
        }
    } 
    // دور الكمبيوتر
    else {
        if (card.type === "attack") {
            let damage = card.value;
            if (gameState.playerShield > 0) {
                if (damage <= gameState.playerShield) {
                    gameState.playerShield -= damage;
                    damage = 0;
                } else {
                    damage -= gameState.playerShield;
                    gameState.playerShield = 0;
                }
            }
            gameState.playerHealth = Math.max(0, gameState.playerHealth - damage);
            battleStatus.innerText = `العدو استخدم [${card.name}] وسبب لك ${card.value} ضرر!`;
        } 
        else if (card.type === "defense") {
            gameState.enemyShield += card.value;
            battleStatus.innerText = `العدو استخدم [${card.name}] وحصل على ${card.value} درع حماية!`;
        } 
        else if (card.type === "heal") {
            gameState.enemyHealth = Math.min(100, gameState.enemyHealth + card.value);
            battleStatus.innerText = `العدو استخدم [${card.name}] واستعاد ${card.value} نقاط حياة!`;
        }

        updateUI();
        checkGameOver();

        // إعادة الدور للاعب وتجديد بطاقاته
        if (!gameState.gameOver) {
            gameState.isPlayerTurn = true;
            cardsHand.classList.remove("disabled");
            renderPlayerHand(); // سحب بطاقات جديدة للاعب
        }
    }
}

// 6. ذكاء اصطناعي بسيط للكمبيوتر (Enemy AI)
function enemyTurn() {
    // إذا كانت صحة الكمبيوتر منخفضة، تزيد احتمالية اختياره للعلاج
    let computerChoice;
    if (gameState.enemyHealth < 40 && Math.random() > 0.5) {
        computerChoice = availableCards.find(c => c.type === "heal") || availableCards[Math.floor(Math.random() * availableCards.length)];
    } else {
        computerChoice = availableCards[Math.floor(Math.random() * availableCards.length)];
    }

    playCard(computerChoice, "enemy");
}

// 7. تحديث واجهة المستخدم الرسومية
function updateUI() {
    // تحديث اللاعب
    playerHealthBar.style.width = `${gameState.playerHealth}%`;
    playerHealthText.innerText = gameState.playerHealth;
    playerShieldText.innerText = `الدرع: ${gameState.playerShield}`;

    // تحديث العدو
    enemyHealthBar.style.width = `${gameState.enemyHealth}%`;
    enemyHealthText.innerText = gameState.enemyHealth;
    enemyShieldText.innerText = `الدرع: ${gameState.enemyShield}`;
}

// 8. التحقق من انتهاء اللعبة
function checkGameOver() {
    if (gameState.enemyHealth <= 0) {
        battleStatus.innerText = "🎉 مبروك! لقد هزمت الوحش وانتصرت في المعركة!";
        battleStatus.style.color = "#4ee54e";
        gameState.gameOver = true;
        cardsHand.classList.add("disabled");
    } else if (gameState.playerHealth <= 0) {
        battleStatus.innerText = "💀 للأسف، لقد هزمت! حاول مجدداً.";
        battleStatus.style.color = "#e43f5a";
        gameState.gameOver = true;
        cardsHand.classList.add("disabled");
    }
}

// تشغيل اللعبة عند تحميل الصفحة
initGame();

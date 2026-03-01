import telebot
import sqlite3
import random
import os

# ====== التوكن ======
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("❌ لم يتم العثور على TOKEN في Environment Variables")

bot = telebot.TeleBot(TOKEN)

# ====== بيانات القناة ======
CHANNEL_USERNAME = "@arthursamad"
CHANNEL_LINK = "https://t.me/arthursamad"

# ====== التحقق من الاشتراك ======
def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

def force_subscribe(message):
    if not is_subscribed(message.from_user.id):
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton("🔔 انضم للقناة", url=CHANNEL_LINK)
        markup.add(btn)

        bot.send_message(
            message.chat.id,
            "🚫 يجب عليك الاشتراك في القناة أولاً لاستخدام البوت 👇",
            reply_markup=markup
        )
        return True
    return False

# ====== قاعدة البيانات ======
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    unique_id TEXT UNIQUE,
    points INTEGER
)
""")
conn.commit()

# ====== توليد ID فريد ======
def generate_unique_id():
    while True:
        new_id = str(random.randint(1000000000, 9999999999))
        cursor.execute("SELECT * FROM users WHERE unique_id=?", (new_id,))
        if not cursor.fetchone():
            return new_id

# ====== تسجيل المستخدم ======
def register_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if not cursor.fetchone():
        unique_id = generate_unique_id()
        cursor.execute("INSERT INTO users VALUES (?, ?, ?)",
                       (user_id, unique_id, 100))
        conn.commit()

# ====== جلب بيانات المستخدم ======
def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone()

# ====== /start ======
@bot.message_handler(commands=['start'])
def start(message):

    if force_subscribe(message):
        return

    register_user(message.from_user.id)
    user = get_user(message.from_user.id)

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📦 الخدمات", "👤 معلومات حسابي")
    markup.row("💸 تحويل نقاط", "💰 اشحن نقاط")

    bot.send_message(
        message.chat.id,
        f"👋 أهلاً بك في البوت 🔥\n\n"
        f"🆔 ID الخاص بك:\n{user[1]}\n\n"
        f"💰 رصيدك الحالي: {user[2]} نقطة",
        reply_markup=markup
    )

# ====== معلومات حسابي ======
@bot.message_handler(func=lambda m: m.text == "👤 معلومات حسابي")
def account_info(message):

    if force_subscribe(message):
        return

    user = get_user(message.from_user.id)

    bot.send_message(
        message.chat.id,
        f"👤 معلومات حسابك\n\n"
        f"🆔 ID الخاص بك:\n{user[1]}\n\n"
        f"💰 رصيدك الحالي: {user[2]} نقطة"
    )

# ====== الخدمات ======
@bot.message_handler(func=lambda m: m.text == "📦 الخدمات")
def services(message):

    if force_subscribe(message):
        return

    bot.send_message(
        message.chat.id,
        "📦 الخدمات:\n\n"
        "1️⃣ مثبت ايم - 50 نقطة\n"
        "2️⃣ فري فاير سيرفر اكس مود - 70 نقطة\n\n"
        "اكتب:\nشراء 1\nأو\nشراء 2"
    )

# ====== شراء ======
@bot.message_handler(func=lambda m: m.text and m.text.startswith("شراء"))
def buy(message):

    if force_subscribe(message):
        return

    user = get_user(message.from_user.id)
    if not user:
        return

    if "1" in message.text:
        price = 50
        content = "📂 الملف:\nhttps://www.mediafire.com/file/ha7gejsg2oitifp/UMP_REGEDIT/file"
    elif "2" in message.text:
        price = 70
        content = "📂 سيرفر اكس مود:\nhttps://download.ffxmodz.com/XMODZ.OB52.apks.apk"
    else:
        return

    if user[2] >= price:
        new_points = user[2] - price
        cursor.execute("UPDATE users SET points=? WHERE user_id=?",
                       (new_points, message.from_user.id))
        conn.commit()

        bot.send_message(
            message.chat.id,
            f"✅ تم خصم {price} نقطة\n\n{content}"
        )
    else:
        bot.send_message(message.chat.id, "❌ رصيدك غير كافي")

# ====== تشغيل البوت ======
print("✅ Bot Running...")
bot.infinity_polling()


import sqlite3
import random

import os
TOKEN = os.getenv("8742758369:AAFbYiE18RRSDr_-t7QKkuL0cAjX2N-M5is")
bot = telebot.TeleBot(TOKEN)

# إنشاء قاعدة البيانات
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

# توليد ID فريد 10 أرقام
def generate_unique_id():
    while True:
        new_id = str(random.randint(1000000000, 9999999999))
        cursor.execute("SELECT * FROM users WHERE unique_id=?", (new_id,))
        if not cursor.fetchone():
            return new_id

# تسجيل المستخدم
def register_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if not cursor.fetchone():
        unique_id = generate_unique_id()
        cursor.execute("INSERT INTO users VALUES (?, ?, ?)",
                       (user_id, unique_id, 100))
        conn.commit()

# جلب بيانات المستخدم
def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone()

# /start
@bot.message_handler(commands=['start'])
def start(message):
    register_user(message.from_user.id)
    user = get_user(message.from_user.id)

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📦 الخدمات", "👤 معلومات حسابي")
    markup.row("💸 تحويل نقاط", "💰 اشحن نقاط")

    bot.send_message(message.chat.id,
                     f"👋 أهلاً بك في البوت 🔥\n\n"
                     f"🆔 ID الخاص بك:\n{user[1]}\n\n"
                     f"💰 رصيدك الحالي: {user[2]} نقطة",
                     reply_markup=markup)

# معلومات حسابي
@bot.message_handler(func=lambda m: m.text == "👤 معلومات حسابي")
def account_info(message):
    user = get_user(message.from_user.id)

    bot.send_message(message.chat.id,
                     f"👤 معلومات حسابك\n\n"
                     f"🆔 ID الخاص بك:\n{user[1]}\n\n"
                     f"💰 رصيدك الحالي: {user[2]} نقطة")

# الخدمات
@bot.message_handler(func=lambda m: m.text == "📦 الخدمات")
def services(message):
    bot.send_message(message.chat.id,
                     "📦 الخدمات:\n\n"
                     "1️⃣ مثبت ايم - 50 نقطة\n"
                     "2️⃣ فري فاير سيرفر اكس مود - 70 نقطة\n\n"
                     "اكتب:\nشراء 1\nأو\nشراء 2")

# شراء
@bot.message_handler(func=lambda m: m.text and m.text.startswith("شراء"))
def buy(message):
    user = get_user(message.from_user.id)
    if not user:
        return

    if "1" in message.text:
        price = 50
        content = "📂 الملف:\nhttps://www.mediafire.com/file/ha7gejsg2oitifp/UMP_REGEDIT_%25F0%259F%25A9%25B8%25E2%259A%2599%25EF%25B8%258F%25E2%259A%25A1.7z/file\n\n📺 الشرح:\nhttps://youtu.be/aTl4pgj80IQ"
    elif "2" in message.text:
        price = 70
        content = "📂 سيرفر اكس مود:\nhttps://download.ffxmodz.com/XMODZ.OB52.apks.apk\n\n🎁 تفعيل الحساب:\nhttps://ffkipas.my.id/verifyuid\n\nماكس إستور♕🌹"
    else:
        return

    if user[2] >= price:
        new_points = user[2] - price
        cursor.execute("UPDATE users SET points=? WHERE user_id=?",
                       (new_points, message.from_user.id))
        conn.commit()
        bot.send_message(message.chat.id,
                         f"✅ تم خصم {price} نقطة\n\n{content}")
    else:
        bot.send_message(message.chat.id, "❌ رصيدك غير كافي")

# تحويل نقاط
pending_transfer = {}

@bot.message_handler(func=lambda m: m.text == "💸 تحويل نقاط")
def transfer_start(message):
    pending_transfer[message.from_user.id] = {}
    bot.send_message(message.chat.id, "📨 أرسل ID الشخص الذي تريد التحويل له")

@bot.message_handler(func=lambda m: m.from_user.id in pending_transfer and "target" not in pending_transfer[m.from_user.id])
def get_target(message):
    cursor.execute("SELECT * FROM users WHERE unique_id=?", (message.text,))
    target = cursor.fetchone()

    if target:
        pending_transfer[message.from_user.id]["target"] = target
        bot.send_message(message.chat.id, "💰 أرسل الكمية")
    else:
        bot.send_message(message.chat.id, "❌ ID غير صحيح")

@bot.message_handler(func=lambda m: m.from_user.id in pending_transfer and "amount" not in pending_transfer[m.from_user.id] and m.text.isdigit())
def get_amount(message):
    sender = get_user(message.from_user.id)
    amount = int(message.text)

    if sender[2] >= amount:
        pending_transfer[message.from_user.id]["amount"] = amount

        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("نعم", "لا")

        bot.send_message(message.chat.id,
                         f"هل تريد تحويل {amount} نقطة؟",
                         reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "❌ رصيدك غير كافي")

@bot.message_handler(func=lambda m: m.text in ["نعم", "لا"])
def confirm_transfer(message):
    if message.from_user.id not in pending_transfer:
        return

    if message.text == "نعم":
        data = pending_transfer[message.from_user.id]
        sender = get_user(message.from_user.id)
        receiver = data["target"]
        amount = data["amount"]

        cursor.execute("UPDATE users SET points=? WHERE user_id=?",
                       (sender[2] - amount, sender[0]))
        cursor.execute("UPDATE users SET points=? WHERE user_id=?",
                       (receiver[2] + amount, receiver[0]))
        conn.commit()

        bot.send_message(message.chat.id, "عملية ناجحة ✅")
    else:
        bot.send_message(message.chat.id, "❌ تم الإلغاء")

    del pending_transfer[message.from_user.id]

# شحن نقاط
@bot.message_handler(func=lambda m: m.text == "💰 اشحن نقاط")
def recharge(message):
    bot.send_message(message.chat.id,
                     "💰 باقات الشحن:\n\n"
                     "500 نقطة - 1500ج.س\n"
                     "1000 نقطة - 3000ج.س\n"
                     "2000 نقطة - 6000ج.س\n\n"
                     "📱 واتساب:\n+249925605381\n\n"
                     "📩 تليجرام:\n@maxgame7799")

print("Bot Running...")
bot.infinity_polling()

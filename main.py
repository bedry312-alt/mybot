import telebot
import sqlite3
import random
import os
import datetime

TOKEN = os.getenv("8742758369:AAFbYiE18RRSDr_-t7QKkuL0cAjX2N-M5is")

if not TOKEN:
    raise ValueError("TOKEN not found")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

CHANNEL_USERNAME = "@arthursamad"
CHANNEL_LINK = "https://t.me/arthursamad"

# ================= قاعدة البيانات =================
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
user_id INTEGER PRIMARY KEY,
unique_id TEXT UNIQUE,
points INTEGER,
last_gift TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS used_codes(
user_id INTEGER,
code TEXT,
PRIMARY KEY(user_id, code)
)
""")

conn.commit()

# ================= الخدمات =================
services = {
    1: ("مثبت ايم", 100, "https://www.mediafire.com/file/ha7gejsg2oitifp/UMP_REGEDIT/file"),
    2: ("فري فاير سيرفر اكس مود", 70, "https://download.ffxmodz.com/XMODZ.OB52.apks.apk"),
    3: ("بوت اختراق", 100, "@QR_l4229BOT"),
    4: ("بوت ارقام فيك", 120, "@Allnumbersultra_Bot"),
    5: ("بوت ماي سوداني", 70, "@Sudaniotpbot"),
    6: ("موقع رشق لايكات تيك توك مجانا", 80, "قريباً")
}

# ================= اكواد الشحن =================
recharge_codes = {
    "max:f766": 100,
    "mxx:v5800": 200,
    "rymax:f700": 500
}

# ================= وظائف مساعدة =================
def generate_id():
    while True:
        new_id = str(random.randint(1000000000, 9999999999))
        cursor.execute("SELECT * FROM users WHERE unique_id=?", (new_id,))
        if not cursor.fetchone():
            return new_id

def register(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?)",
                       (user_id, generate_id(), 100, ""))
        conn.commit()

def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone()

def update_points(user_id, amount):
    cursor.execute("UPDATE users SET points=? WHERE user_id=?", (amount, user_id))
    conn.commit()

def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

def force_sub(message):
    if not is_subscribed(message.from_user.id):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("🔔 انضم للقناة", url=CHANNEL_LINK),
            telebot.types.InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_sub")
        )
        bot.send_message(message.chat.id,
                         "🚫 يجب الاشتراك بالقناة أولاً",
                         reply_markup=markup)
        return True
    return False

# ================= الواجهة الرئيسية =================
def main_menu(chat_id):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("📦 الخدمات", callback_data="services"),
        telebot.types.InlineKeyboardButton("👤 معلومات حسابي", callback_data="account")
    )
    markup.add(
        telebot.types.InlineKeyboardButton("💸 تحويل نقاط", callback_data="transfer"),
        telebot.types.InlineKeyboardButton("💰 اشحن نقاط", callback_data="recharge")
    )
    markup.add(
        telebot.types.InlineKeyboardButton("🎁 الهدية اليومية", callback_data="daily")
    )
    bot.send_message(chat_id, "اختر من القائمة:", reply_markup=markup)

# ================= start =================
@bot.message_handler(commands=['start'])
def start(message):
    if force_sub(message): return
    register(message.from_user.id)
    main_menu(message.chat.id)

# ================= تحقق الاشتراك =================
@bot.callback_query_handler(func=lambda call: call.data=="check_sub")
def check_sub(call):
    if is_subscribed(call.from_user.id):
        bot.edit_message_text("✅ تم التحقق يمكنك استخدام البوت",
                              call.message.chat.id,
                              call.message.message_id)
        main_menu(call.message.chat.id)
    else:
        bot.answer_callback_query(call.id, "❌ لم يتم الاشتراك بعد")

# ================= عرض الخدمات =================
@bot.callback_query_handler(func=lambda call: call.data=="services")
def show_services(call):
    text = "📦 الخدمات:\n\n"
    for num in services:
        text += f"{num}/ {services[num][0]} - {services[num][1]} نقطة\n"
    text += "\nارسل رقم الخدمة للشراء"
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("🔙 عودة", callback_data="back_main")
    )
    bot.edit_message_text(text, call.message.chat.id,
                          call.message.message_id,
                          reply_markup=markup)

# ================= شراء خدمة =================
@bot.message_handler(func=lambda m: m.text and m.text.isdigit())
def buy_service(message):
    if force_sub(message): return
    num = int(message.text)
    if num not in services: return
    user = get_user(message.from_user.id)
    price = services[num][1]
    if user[2] < price:
        bot.send_message(message.chat.id, "❌ رصيدك غير كافي")
        return
    update_points(user[0], user[2]-price)
    bot.send_message(message.chat.id,
                     f"✅ تم شراء {services[num][0]}\n{services[num][2]}")
    bot.send_message(CHANNEL_USERNAME,
                     f"🛒 عملية شراء جديدة\nالخدمة: {services[num][0]}\nالمستخدم: {user[1]}")

# ================= معلومات الحساب =================
@bot.callback_query_handler(func=lambda call: call.data=="account")
def account(call):
    user = get_user(call.from_user.id)
    text = f"🆔 ID: {user[1]}\n💰 الرصيد: {user[2]}"
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("🔙 عودة", callback_data="back_main")
    )
    bot.edit_message_text(text,
                          call.message.chat.id,
                          call.message.message_id,
                          reply_markup=markup)

# ================= الهدية اليومية =================
@bot.callback_query_handler(func=lambda call: call.data=="daily")
def daily(call):
    user = get_user(call.from_user.id)
    today = str(datetime.date.today())
    if user[3] == today:
        bot.answer_callback_query(call.id, "❌ اخذت هديتك اليوم")
        return
    new_points = user[2] + 20
    cursor.execute("UPDATE users SET points=?, last_gift=? WHERE user_id=?",
                   (new_points, today, user[0]))
    conn.commit()
    bot.edit_message_text("🎁 تم إضافة 20 نقطة",
                          call.message.chat.id,
                          call.message.message_id)
    main_menu(call.message.chat.id)

# ================= الشحن =================
@bot.callback_query_handler(func=lambda call: call.data=="recharge")
def recharge(call):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("💳 شحن عبر كود", callback_data="code_recharge"),
        telebot.types.InlineKeyboardButton("🔙 عودة", callback_data="back_main")
    )
    bot.edit_message_text("اختر طريقة الشحن",
                          call.message.chat.id,
                          call.message.message_id,
                          reply_markup=markup)

# ================= شحن عبر كود =================
@bot.callback_query_handler(func=lambda call: call.data=="code_recharge")
def ask_code(call):
    msg = bot.send_message(call.message.chat.id, "ارسل كود الشحن:")
    bot.register_next_step_handler(msg, process_code)

def process_code(message):
    code = message.text.strip()
    user_id = message.from_user.id
    if code not in recharge_codes:
        bot.send_message(message.chat.id, "❌ كود غير صحيح")
        return
    cursor.execute("SELECT * FROM used_codes WHERE user_id=? AND code=?",
                   (user_id, code))
    if cursor.fetchone():
        bot.send_message(message.chat.id, "❌ استخدمت هذا الكود مسبقاً")
        return
    points = recharge_codes[code]
    user = get_user(user_id)
    update_points(user_id, user[2] + points)
    cursor.execute("INSERT INTO used_codes VALUES (?,?)", (user_id, code))
    conn.commit()
    bot.send_message(message.chat.id, f"✅ تم شحن {points} نقطة")
    bot.send_message(CHANNEL_USERNAME,
                     f"💳 شحن جديد\nالمستخدم: {user[1]}\nالقيمة: {points}")

# ================= رجوع =================
@bot.callback_query_handler(func=lambda call: call.data=="back_main")
def back(call):
    bot.edit_message_text("العودة للقائمة الرئيسية",
                          call.message.chat.id,
                          call.message.message_id)
    main_menu(call.message.chat.id)

print("Bot Running...")
bot.infinity_polling()

from telebot import TeleBot, types
import json
import time
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import CallbackQuery


with open("data.json", "r", encoding="utf-8") as file:
    users_data = json.load(file)

print(users_data)


TOKEN = "7633565934:AAGe6hjn6sNmoOEerM1vYndyvsHGDd0KDW4"
bot = TeleBot(TOKEN)
ADMIN_ID = 6127250344  # Admin Telegram ID-sini shu yerga yozing
CHANNELS = [
    {"username": "@TgPremium_Xizmati", "name": "TgPremium Xizmati"},
    {"username": "@IT_JobsUzb", "name": "IT Jobs Uzb"},
    {"username": "@Intizom365", "name": "Intizom365"}
]
users = set()
# Foydalanuvchilar ma'lumotlari saqlanadigan JSON fayl
DATA_FILE = "data.json"
USERS_FILE = "users.json"  # Foydalanuvchilar saqlanadigan fayl
users_data = {}  # Agar JSON yoki faylga bog‘langan bo‘lsa, shu yerdan yuklanadi

def load_data():
    try:
        with open("data.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"users": {}}

def save_data(data):
    with open("data.json", "w") as file:
        json.dump(data, file, indent=4)

# Kanallarga obunani tekshirish
def check_subscription(user_id):
    for channel in CHANNELS:
        chat_member = bot.get_chat_member(channel["username"], user_id)
        if chat_member.status in ["left", "kicked"]:
            return False
    return True

# Asosiy menyu
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("⭐ Premium Olish")
    return markup

def check_subscription(user_id):
    """Foydalanuvchi barcha kanallarga obuna bo‘lganligini tekshiradi"""
    for channel in CHANNELS:
        try:
            status = bot.get_chat_member(channel["username"], user_id).status
            if status not in ["member", "administrator", "creator"]:
                return False
        except Exception:
            return False
    return True


def get_top_users():
    try:
        with open("data.json", "r", encoding="utf-8") as file:
            users_data = json.load(file)

        # Foydalanuvchilar faqat "users" kaliti ichida saqlangan
        if "users" not in users_data or not isinstance(users_data["users"], dict):
            return "Hozircha reytingda foydalanuvchilar yo‘q."

        users = users_data["users"]

        sorted_users = sorted(
            users.items(),
            key=lambda x: x[1].get("balance", 0),
            reverse=True
        )

        result = ""
        for i, (user_id, user_info) in enumerate(sorted_users[:10], start=1):
            name = user_info.get("name", f"ID {user_id}")
            balance = user_info.get("balance", 0)
            result += f"{i}. {name} - {balance} so'm\n"

        return result if result.strip() else "Hozircha reytingda foydalanuvchilar yo‘q."

    except Exception as e:
        return f"Xatolik yuz berdi: {str(e)}"

def main_menu():
    """Asosiy menyu tugmalarini yaratadi"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        types.KeyboardButton("⭐ Premium Olish"),
        types.KeyboardButton("TOP foydalanuvchilar"),
        types.KeyboardButton("💰 Premium Narxlari"),
        types.KeyboardButton("💳 Mening Hisobim"),
        types.KeyboardButton("🎁 Bonus olish"),
        types.KeyboardButton("📄 Qo‘llanma"),
        types.KeyboardButton("👨‍💼 Administrator"),
        types.KeyboardButton("⭐ Stars olish"),
    ]
    markup.add(*buttons)
    return markup

@bot.message_handler(commands=["start"])
def send_welcome(message):
    user_id = str(message.from_user.id)
    data = load_data()

    # Foydalanuvchi ro‘yxatda yo‘q bo‘lsa, qo‘shamiz
    if user_id not in data["users"]:
        data["users"][user_id] = {"balance": 0, "referred_by": None}

    # Referal orqali kirgan bo‘lsa
    args = message.text.split()
    if len(args) > 1:
        referrer_id = args[1]  # Referal ID
        if referrer_id != user_id and data["users"][user_id]["referred_by"] is None:
            if referrer_id in data["users"]:
                data["users"][referrer_id]["balance"] += 100  # Taklif qilgan odamga 500 so‘m
                data["users"][user_id]["balance"] += 1000  # Yangi foydalanuvchiga 500 so‘m
            data["users"][user_id]["referred_by"] = referrer_id  # Kim taklif qilganini saqlaymiz

    save_data(data)

    # Agar foydalanuvchi barcha kanallarga obuna bo‘lsa
    if check_subscription(user_id):
        bot.send_message(user_id, "🎉 Raxmat! Siz barcha kanallarga obuna bo‘lgansiz.", reply_markup=main_menu())
    else:
        markup = types.InlineKeyboardMarkup()

        for channel in CHANNELS:
            btn = types.InlineKeyboardButton(f"✅ {channel['name']}", url=f"https://t.me/{channel['username'][1:]}")
            markup.add(btn)

        check_btn = types.InlineKeyboardButton("🔄 Obunani tekshirish", callback_data="check_subs")
        markup.add(check_btn)

        bot.send_message(user_id, "📌 Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "check_subs")
def check_subscriptions(call):
    user_id = call.from_user.id

    if check_subscription(user_id):
        bot.delete_message(call.message.chat.id, call.message.message_id)  # Eski xabarni o‘chirish
        bot.send_message(user_id, "🎉 Raxmat! Endi botdan foydalanishingiz mumkin.", reply_markup=main_menu())
    else:
        bot.answer_callback_query(call.id, "🚫 Hali ham barcha kanallarga obuna bo‘lmadingiz!")

# TOP foydalanuvchilar tugmasi bosilganda javob berish
@bot.message_handler(func=lambda message: message.text.lower() == "top foydalanuvchilar")
def send_top_users(message):
    top_list = get_top_users()
    bot.send_message(message.chat.id, top_list, parse_mode="Markdown")
@bot.message_handler(func=lambda message: message.text.lower() == "💳 mening hisobim")
def send_user_balance(message):
    user_id = str(message.from_user.id)
    data = load_data()

    if user_id in data["users"]:
        balance = data["users"][user_id]["balance"]
        bot.send_message(message.chat.id, f"💰 Sizning hisobingiz: *{balance} so'm*", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "🔍 Hisob topilmadi. Sizda hali balans mavjud emas.")
@bot.message_handler(func=lambda message: message.text.lower() == "🎁 bonus olish")
def claim_daily_bonus(message):
    user_id = str(message.from_user.id)
    data = load_data()

    # Agar "users" kaliti mavjud bo'lmasa, uni yaratamiz
    if "users" not in data:
        data["users"] = {}

    if user_id not in data["users"]:
        data["users"][user_id] = {"name": message.from_user.first_name, "balance": 0, "last_bonus": 0}

    current_time = time.time()
    last_bonus_time = data["users"][user_id].get("last_bonus", 0)

    if current_time - last_bonus_time >= 86400:  # 24 soat (86400 sekund)
        data["users"][user_id]["balance"] += 500  # 500 so‘m bonus
        data["users"][user_id]["last_bonus"] = current_time
        save_data(data)
        bot.send_message(message.chat.id, "🎉 Tabriklaymiz! Siz 500 so‘m bonus oldingiz. 💰")
    else:
        remaining_time = int((last_bonus_time + 86400) - current_time)
        hours = remaining_time // 3600
        minutes = (remaining_time % 3600) // 60
        bot.send_message(message.chat.id, f"⏳ Siz bonusni allaqachon olgansiz! Yangi bonus {hours} soat {minutes} daqiqadan keyin mavjud bo‘ladi.")
@bot.message_handler(func=lambda message: message.text == "⭐ Premium Olish")
def buy_premium(message):
    user_id = str(message.from_user.id)
    data = load_data()

    # Agar foydalanuvchi mavjud bo'lmasa yoki hisobida mablag' bo'lmasa, uni 0 ga teng deb olamiz
    balance = data["users"].get(user_id, {}).get("balance", 0)

    # Inline tugmalar
    markup = types.InlineKeyboardMarkup()
    buy_button = types.InlineKeyboardButton("💎 Premium olish", callback_data="buy_premium")
    markup.add(buy_button)

    # Xabarni yuborish
    bot.send_photo(
        message.chat.id,
        photo=open("p.jpg", "rb"),  # Faylni o'zingiz yuklagan rasmga o'zgartiring
        caption=(
            "📢 *Assalomu alaykum!*\n\n"
            "Siz do‘stlaringizni ushbu referal orqali taklif qilishingiz mumkin:\n"
            f"https://t.me/{bot.get_me().username}?start={user_id}\n\n"
            "🎁 Har bir do‘stingiz uchun *1000 so‘m* oling! 💰\n\n"
            "💳 *Premium narxi:* ⬇️\n"
            "💎 *1 oylik - 50 000 so‘m*\n\n"
            "📌 *Sotib olish uchun tugmani bosing!*"
        ),
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "buy_premium")
def confirm_premium(call):
    user_id = str(call.from_user.id)
    data = load_data()
    balance = data["users"].get(user_id, {}).get("balance", 0)

    if balance >= 50000:
        # Tasdiqlash tugmalari
        confirm_markup = types.InlineKeyboardMarkup()
        yes_button = types.InlineKeyboardButton("✅ Ha", callback_data="confirm_premium")
        no_button = types.InlineKeyboardButton("❌ Yo‘q", callback_data="cancel_premium")
        confirm_markup.add(yes_button, no_button)

        bot.send_message(call.message.chat.id, "💰 Sizning hisobingizda yetarli mablag‘ bor. Premium olishni tasdiqlaysizmi?", reply_markup=confirm_markup)
    else:
        bot.send_message(call.message.chat.id, "⚠️ Hisobingizda yetarli mablag‘ yo‘q. Premium olish uchun *50 000 so‘m* kerak.")

@bot.callback_query_handler(func=lambda call: call.data == "cancel_premium")
def cancel_premium(call):
    bot.send_message(call.message.chat.id, "❌ Premium olish bekor qilindi.")

@bot.callback_query_handler(func=lambda call: call.data == "confirm_premium")
def process_premium(call):
    user_id = str(call.from_user.id)
    data = load_data()

    if data["users"].get(user_id, {}).get("balance", 0) >= 50000:
        # Hisobdan 50 000 so‘m ayirish
        data["users"][user_id]["balance"] -= 50000
        save_data(data)

        bot.send_message(call.message.chat.id, "🎉 Tabriklaymiz! Siz Premium foydalanuvchi bo‘ldingiz! 💎")

        # Bu joyga premiumni qanday aktiv qilishni qo‘shing
        # Masalan, foydalanuvchini bazaga premium sifatida saqlash
    else:
        bot.send_message(call.message.chat.id, "⚠️ Hisobingizda yetarli mablag‘ yo‘q.")
@bot.message_handler(func=lambda message: message.text == "💰 Premium Narxlari")
def premium_prices(message):
    # Inline tugma yaratish
    markup = types.InlineKeyboardMarkup()
    premium_link = "https://t.me/abduzohid_buriboyev?start=premium"  # O'z admin panel yoki kerakli linkni kiriting
    buy_button = types.InlineKeyboardButton("💎 Premium sotib olish", url=premium_link)
    markup.add(buy_button)

    bot.send_photo(
        message.chat.id,
        photo=open("p.jpg", "rb"),  # Rasm faylini to'g'ri nom bilan almashtiring
        caption=(
            "✅ *Profilga kirish orqali*\n"
            "🎁 *1 OYLIK OBUNA - 50.000 SO‘M*\n"
            "🎉 *12 OYLIK OBUNA - 300.000 SO‘M*\n\n"
            "✅ *Akauntga kirmasdan olinadi*\n"
            "🎊 *3 OYLIK OBUNA - 175.000 SO‘M*\n"
            "🎉 *6 OYLIK OBUNA - 250.000 SO‘M*\n"
            "🎊 *12 OYLIK OBUNA - 410.000 SO‘M*\n\n"
            "☑️ *Do‘stlar yoki yaqin insonlaringizga sovg‘a ham qilishingiz mumkin* ✔️"
        ),
        parse_mode="Markdown",
        reply_markup=markup
    )
@bot.message_handler(func=lambda message: message.text == "👨‍💼 Administrator")
def send_admin_info(message):
    bot.send_photo(
        message.chat.id,
        photo=open("p.jpg", "rb"),  # Rasm nomini yuklagan fayl nomiga o'zgartiring
        caption=(
            "🏢 *Savollar uchun:* [@abduzohid_buriboyev](https://t.me/abduzohid_buriboyev)\n\n"
            "📢 *Kanal:* [@TgPremium_Xizmati](https://t.me/TgPremium_Xizmati)\n\n"
            "💬 *Guruh:* [@TeligramPremium_xizmati](https://t.me/TeligramPremium_xizmati)"
        ),
        parse_mode="Markdown"
    )
@bot.message_handler(func=lambda message: message.text == "📄 Qo‘llanma")
def send_guide_info(message):
    bot.send_photo(
        message.chat.id,
        photo=open("p.jpg", "rb"),  # Rasm nomini yuklagan fayl nomiga o'zgartiring
        caption=(
            "📌 *Muhim Qoidalari ❗*\n\n"
            "*Botimizdan foydalanish qo‘llanmasi:*\n\n"
            "1. *Botdan ro‘yxatdan o‘ting*\n"
            "2. *Premium olish uchun shaxsiy pul tolab yoki ref toplab premium oling*\n"
            "3. *Yetarlicha pul to‘planganda, Premium olishingiz mumkin*\n"
            "4. *Dostingizga sovga qilishingiz mumkin*\n"
            "5. *Guruhimizda yoki Profilimda nojoiz gaplar yozsangiz BAN olasiz *\n"
        ),
        parse_mode="Markdown"
    )
@bot.message_handler(func=lambda message: message.text == "⭐ Stars olish")
def send_guide_info(message):
    bot.send_photo(
        message.chat.id,
        photo=open("x.jpg", "rb"),  # Rasm nomini yuklagan fayl nomiga o'zgartiring
        caption=(
            "📌 *Endi siz  orqali Telegram Stars'ni qulay va tezkor tarzda xarid qilishingiz mumkin! ❗*\n\n"
            "*⭐ Stars narxlari:*\n\n"
            " *100 ta stars 35.000 soʻm*\n\n"
            " *250 ta stars 75.000 soʻm*\n\n"
            " *350 ta stars 100.000 soʻm*\n\n"
            " *500 ta stars 140.000 soʻm*\n\n"
            " *Akauntga kirmasdan olinadi. *\n"
            " *🔹 Nega aynan biz?. *\n"
            " *✅ Telegram hisobingizga kirmasdan Stars xarid qilish imkoniyati.. *\n"
            " *✅ Tezkor xizmat va ishonchli oʻtkazib berish... *\n"
            " *✅ Arzon va qulay narxlar!... *\n"
        ),
        parse_mode="Markdown"
    )
# Admin panel
@bot.message_handler(commands=["admin"])
def admin_panel(message):
    data = load_data()

    if "admin" not in data:
        data["admin"] = None
        save_data(data)

    if data["admin"] is None:
        data["admin"] = message.chat.id
        save_data(data)

    if message.chat.id != data["admin"]:
        bot.send_message(message.chat.id, "❌ Siz admin emassiz!")
        return

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📢 Xabar yuborish", callback_data="send_message"))
    markup.add(InlineKeyboardButton("👥 Foydalanuvchilar", callback_data="list_users"))
    markup.add(InlineKeyboardButton("💰 Balans o‘zgartirish", callback_data="change_balance"))

    bot.send_message(message.chat.id, "🔧 Admin Panelga xush kelibsiz!", reply_markup=markup)

# Hamma foydalanuvchilarga xabar yuborish
@bot.callback_query_handler(func=lambda call: call.data == "send_message")
def ask_message(call):
    bot.send_message(call.message.chat.id, "📩 Xabar matnini kiriting:")
    bot.register_next_step_handler(call.message, send_message_to_all)

def send_message_to_all(message):
    data = load_data()
    text = message.text
    count = 0

    for user_id in data["users"]:
        try:
            bot.send_message(user_id, f"📢 Yangi e'lon:\n\n{text}")
            count += 1
        except Exception as e:
            print(f"Xabar yuborib bo‘lmadi: {user_id} - {e}")

    bot.send_message(message.chat.id, f"✅ Xabar {count} ta foydalanuvchiga yuborildi!")

# Foydalanuvchilar ro‘yxati
@bot.callback_query_handler(func=lambda call: call.data == "list_users")
def list_users(call):
    data = load_data()
    users = data.get("users", [])
    user_list = "\n".join([str(user) for user in users])
    bot.send_message(call.message.chat.id, f"👥 Foydalanuvchilar:\n{user_list}")

# Balansni o‘zgartirish
@bot.callback_query_handler(func=lambda call: call.data == "change_balance")
def ask_user_id(call):
    bot.send_message(call.message.chat.id, "💰 Foydalanuvchi ID sini kiriting:")
    bot.register_next_step_handler(call.message, ask_balance_amount)

def ask_balance_amount(message):
    user_id = message.text
    bot.send_message(message.chat.id, "💰 Yangi balans miqdorini kiriting:")
    bot.register_next_step_handler(message, lambda msg: change_balance(msg, user_id))

def change_balance(message, user_id):
    new_balance = message.text
    data = load_data()

    if user_id in data["users"]:
        data["users"][user_id]["balance"] = int(new_balance)
        save_data(data)
        bot.send_message(message.chat.id, f"✅ {user_id} uchun yangi balans: {new_balance} so‘m")
    else:
        bot.send_message(message.chat.id, "❌ Foydalanuvchi topilmadi!")

bot.polling()

import telebot
import os

# Bot Token and Owner ID from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN", "8195816361:AAGLPEe-qJ2i8SyhXF6hO5vopAc-Blun_-E")
OWNER_ID = int(os.getenv("OWNER_ID", "7845479937"))

bot = telebot.TeleBot(BOT_TOKEN)

# In-memory balances (for demo; use database in production)
user_balances = {}
banned_users = set()

def is_owner(message):
    return message.from_user.id == OWNER_ID

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id in banned_users:
        bot.reply_to(message, "🚫 You are banned from using this bot.")
        return
    bot.reply_to(message, "Welcome to the bot! Use /help to see options.")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.reply_to(message, "/balance - check your balance\n"
                          "/redeem <amount> - redeem balance")

@bot.message_handler(commands=['balance'])
def balance(message):
    uid = message.from_user.id
    bal = user_balances.get(uid, 0)
    bot.reply_to(message, f"💰 Your balance: {bal}")

@bot.message_handler(commands=['redeem'])
def redeem(message):
    uid = message.from_user.id
    if uid in banned_users:
        bot.reply_to(message, "🚫 You are banned.")
        return
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "Usage: /redeem <amount>")
            return
        amt = int(parts[1])
        current = user_balances.get(uid, 0)
        if amt <= 0 or amt > current:
            bot.reply_to(message, "❌ Invalid amount.")
            return
        user_balances[uid] = current - amt
        bot.reply_to(message, f"✅ Redeemed {amt}. New balance: {user_balances[uid]}")
    except Exception as e:
        bot.reply_to(message, "Error: " + str(e))

# --- ADMIN PANEL ---
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if not is_owner(message):
        return
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("➕ Add Balance", "🚫 Ban User")
    keyboard.add("✅ Unban User", "📢 Broadcast")
    bot.send_message(message.chat.id, "⚙️ Admin Panel", reply_markup=keyboard)

@bot.message_handler(func=lambda m: is_owner(m) and m.text == "➕ Add Balance")
def admin_add_balance(message):
    bot.send_message(message.chat.id, "Send user_id and amount (format: user_id amount)")
    bot.register_next_step_handler(message, process_add_balance)

def process_add_balance(message):
    try:
        uid, amt = message.text.split()
        uid = int(uid)
        amt = int(amt)
        user_balances[uid] = user_balances.get(uid, 0) + amt
        bot.reply_to(message, f"✅ Added {amt} to {uid}. New balance: {user_balances[uid]}")
    except:
        bot.reply_to(message, "❌ Invalid format. Use: user_id amount")

@bot.message_handler(func=lambda m: is_owner(m) and m.text == "🚫 Ban User")
def admin_ban(message):
    bot.send_message(message.chat.id, "Send user_id to ban")
    bot.register_next_step_handler(message, process_ban)

def process_ban(message):
    try:
        uid = int(message.text)
        banned_users.add(uid)
        bot.reply_to(message, f"🚫 User {uid} banned.")
    except:
        bot.reply_to(message, "❌ Invalid user_id.")

@bot.message_handler(func=lambda m: is_owner(m) and m.text == "✅ Unban User")
def admin_unban(message):
    bot.send_message(message.chat.id, "Send user_id to unban")
    bot.register_next_step_handler(message, process_unban)

def process_unban(message):
    try:
        uid = int(message.text)
        banned_users.discard(uid)
        bot.reply_to(message, f"✅ User {uid} unbanned.")
    except:
        bot.reply_to(message, "❌ Invalid user_id.")

@bot.message_handler(func=lambda m: is_owner(m) and m.text == "📢 Broadcast")
def admin_broadcast(message):
    bot.send_message(message.chat.id, "Send broadcast message")
    bot.register_next_step_handler(message, process_broadcast)

def process_broadcast(message):
    text = message.text
    for uid in user_balances.keys():
        try:
            bot.send_message(uid, f"📢 Broadcast: {text}")
        except:
            pass
    bot.reply_to(message, "✅ Broadcast sent.")

print("Bot is running...")
bot.infinity_polling()

import telebot
from telebot import types
import sqlite3
from datetime import datetime

# ===== КОНФИГУРАЦИЯ =====
TOKEN = '8616517231:AAH5Wj3pJ1nolhEoZadfN-EbYpWoXA1HZo4'  # Твой токен от @BotFather
ADMIN_IDS = [5186843419]  # Твой Telegram ID
WEB_APP_URL = 'https://darkdev1337.github.io/casino/sait.html'  # URL твоего сайта

bot = telebot.TeleBot(TOKEN)

# ===== БАЗА ДАННЫХ (ОПЦИОНАЛЬНО) =====
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY,
                  username TEXT,
                  first_name TEXT,
                  last_visit TEXT)''')
    conn.commit()
    conn.close()

# ===== КОМАНДА СТАРТ =====
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    # Сохраняем визит (опционально)
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO users (user_id, username, first_name, last_visit) VALUES (?, ?, ?, ?)",
                  (user_id, username, first_name, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    except:
        pass
    
    # Создаем WebApp кнопку
    web_app = types.WebAppInfo(url=f"{WEB_APP_URL}?user_id={user_id}")
    
    # Клавиатура с одной кнопкой
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🎰 ОТКРЫТЬ КАЗИНО", web_app=web_app))
    
    # Отправляем сообщение
    bot.send_message(
        message.chat.id,
        f"👋 Привет, {first_name}!\n\n👇 Нажми на кнопку ниже, чтобы открыть казино:",
        reply_markup=markup
    )

# ===== АДМИН ПАНЕЛЬ (ПРОСТАЯ) =====
@bot.message_handler(commands=['admin'])
def admin(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "❌ У тебя нет прав администратора!")
        return
    
    markup = types.InlineKeyboardMarkup()
    
    # Кнопка для админа (тоже открывает сайт)
    web_app = types.WebAppInfo(url=f"{WEB_APP_URL}?user_id={message.from_user.id}&admin=1")
    markup.add(types.InlineKeyboardButton("👑 ОТКРЫТЬ АДМИНКУ", web_app=web_app))
    
    # Кнопка статистики
    markup.add(types.InlineKeyboardButton("📊 Статистика", callback_data="stats"))
    
    bot.send_message(
        message.chat.id,
        "👑 Админ панель\n\nНажми кнопку для открытия админ-версии сайта:",
        reply_markup=markup
    )

# ===== СТАТИСТИКА ДЛЯ АДМИНА =====
@bot.callback_query_handler(func=lambda call: call.data == "stats")
def stats(callback):
    if callback.from_user.id not in ADMIN_IDS:
        bot.answer_callback_query(callback.id, "❌ Нет доступа!")
        return
    
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users")
        total_users = c.fetchone()[0]
        
        c.execute("SELECT first_name, last_visit FROM users ORDER BY last_visit DESC LIMIT 5")
        recent = c.fetchall()
        conn.close()
        
        text = f"📊 СТАТИСТИКА\n\n"
        text += f"👥 Всего пользователей: {total_users}\n\n"
        text += f"🕐 Последние визиты:\n"
        for name, visit in recent:
            text += f"• {name}: {visit[:10]}\n"
        
        bot.answer_callback_query(callback.id, text, show_alert=True)
    except:
        bot.answer_callback_query(callback.id, "❌ Ошибка загрузки статистики", show_alert=True)

# ===== ЗАПУСК =====
if __name__ == '__main__':
    init_db()
    print("=" * 50)
    print("🎰 WEBAPP CASINO BOT")
    print("=" * 50)
    print(f"✅ Бот запущен!")
    print(f"🌐 WebApp URL: {WEB_APP_URL}")
    print(f"👑 Admin ID: {ADMIN_IDS[0]}")
    print("=" * 50)
    print("📱 Напиши /start в Telegram")
    print("=" * 50)
    
    bot.infinity_polling()

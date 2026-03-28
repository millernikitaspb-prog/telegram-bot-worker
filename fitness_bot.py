import telebot
import sqlite3
import schedule
import threading 
import time 
import datetime 

TOKEN = "8401436152:AAEl0EEuMuJQ5lJbXCBIV1QDP88osAUd6nE"
bot = telebot.TeleBot(TOKEN)

def init_db():
	conn = sqlite3.connect("fitness.db")
	cursor = conn.cursor()
	cursor.execute("""CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, chat_id INTEGER UNIQUE, name TEXT, weight REAL, height REAL, goal TEXT, reminder_time TEXT)""")
	conn.commit()
	conn.close()

@bot.message_handler(commands=["start"])
def start(message):
	bot.send_message(message.chat.id, "Как тебя зовут?")
	bot.register_next_step_handler(message, get_name)

def get_name(message):
	name = message.text
	bot.send_message(message.chat.id, "Введи вес в кг:")
	bot.register_next_step_handler(message, lambda m: get_weight(m, name))

def get_weight(message, name):
	weight = float(message.text)
	bot.send_message(message.chat.id, "Введи рост в см:")
	bot.register_next_step_handler(message, lambda m: get_height(m, name, weight))

def get_height(message, name, weight):
	height = float(message.text)
	conn = sqlite3.connect("fitness.db")
	cursor = conn.cursor()
	cursor.execute("INSERT OR REPLACE INTO users (chat_id, name, weight, height) VALUES (?, ?, ?, ?)", (message.chat.id, name, weight, height))
	conn.commit()
	conn.close()
	bot.send_message(message.chat.id, f"Готово! Имя: {name}, Вес: {weight}кг, Рост: {height}см. Напиши /имт, чтобы узнать индекс массы тела или /напоминание, чтобы установить напоминание")

@bot.message_handler(commands=["имт"])
def имт(message):
	conn = sqlite3.connect("fitness.db")
	cursor = conn.cursor()
	user = cursor.execute("SELECT * FROM users WHERE chat_id = ?", (message.chat.id,)).fetchone()
	conn.close()
	if user:
		imt = user[3] / ((user[4]/100) ** 2)
		bot.send_message(message.chat.id, f"Твой ИМТ: {imt:.1f}")
	else:
		bot.send_message(message.chat.id, "Сначала зарегистрируйся - /регистрация")

def send_reminder():
	now = datetime.datetime.now().strftime("%H:%M")
	conn = sqlite3.connect("fitness.db")
	cursor = conn.cursor()
	users = cursor.execute("SELECT chat_id, name, reminder_time FROM users WHERE reminder_time = ?", (now,)).fetchall()
	conn.close()
	for user in users:
		bot.send_message(user[0], f"{user[1]}, время тренироваться!")

def run_sheduler():
	schedule.every().minute.do(send_reminder)
	while True:
		schedule.run_pending()
		time.sleep(60)

@bot.message_handler(commands=["напоминание"])
def напоминание(message):
	time_str = message.text.replace("/напоминание", "").strip()
	if time_str:
		conn = sqlite3.connect("fitness.db")
		cursor = conn.cursor()
		cursor.execute("UPDATE users SET reminder_time = ? WHERE chat_id = ?", (time_str, message.chat.id))
		conn.commit()
		conn.close()
		bot.send_message(message.chat.id, f"Напоминание установлено на {time_str}!")
	else:
		bot.send_message(message.chat.id, "Укажи время: /напоминание «00:00»")

init_db()
t = threading.Thread(target=run_sheduler)
t.daemon = True
t.start()
bot.polling()
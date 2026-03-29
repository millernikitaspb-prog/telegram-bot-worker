import telebot
import psycopg2
import threading 
import time 
import datetime
import os

TOKEN = os.environ.get("BOT_TOKEN")
DATABASE_URL = os.environ.get("DATABASE_URL")

bot = telebot.TeleBot(TOKEN)

def get_conn():
	return psycopg2.connect(DATABASE_URL)

def init_db():
	conn = get_conn()
	cursor = conn.cursor()
	cursor.execute('''
		CREATE TABLE IF NOT EXISTS users (
			id SERIAL PRIMARY KEY,
			chat_id BIGINT UNIQUE,
			name TEXT,
			weight REAL,
			height REAL,
			reminder_time TEXT
		)
	''')
	conn.commit()
	cursor.close()
	conn.close()

@bot.message_handler(commands=['start'])
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
	conn = get_conn()
	cursor = conn.cursor()
	cursor.execute(
		"INSERT INTO users (chat_id, name, weight, height) VALUES (%s, %s, %s, %s) ON CONFLICT (chat_id) DO UPDATE SET name=%s, weight=%s, height=%s",
		(message.chat.id, name, weight, height, name, weight, height)
	)
	conn.commit()
	cursor.close()
	conn.close()
	bot.send_message(message.chat.id, f"Готово! Имя: {name}, Вес: {weight}кг, Рост: {height}см. Напиши /имт, чтобы узнать индекс массы тела")

@bot.message_handler(commands=['имт'])
def имт(message):
	conn = get_conn()
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM users WHERE chat_id = %s", (message.chat.id,))
	user = cursor.fetchone()
	cursor.close()
	conn.close()
	if user:
		imt = user[3] /  ((user[4]/100) ** 2)
		bot.send_message(message.chat.id, f"Твой ИМТ: {imt:.1}")
	else:
		bot.send_message(message.chat.id, "Сначала зарегистрируйся - /start")

@bot.message_handler(commands=["напоминание"])
def напоминание(message):
	time_str = message.text.replace("/напоминание", "").strip()
	if time_str:
		user_time = datetime.datetime.strptime(time_str, "%H:%M")
		utc_time = user_time - datetime.timedelta(hours=3)
		utc_str = utc_time.strptime("%H:%M")
		conn = get_conn()
		cursor = conn.cursor()
		cursor.execute("UPDATE users SET reminder_time = %s WHERE chat_id = %s", (time_str, message.chat.id))
		conn.commit()
		cursor.close()
		conn.close()
		bot.send_message(message.chat.id, f"Напоминание установлено на {time_str}!")
	else:
		bot.send_message(message.chat.id, "Укажи время: /напоминание 00:00")

def run_scheduler():
	while True:
		now = datetime.datetime.utcnow().strftime("%H:%M")
		conn = get_conn()
		cursor = conn.cursor()
		cursor.execute("SELECT chat_id, name FROM users WHERE reminder_time = %s", (now,))
		users = cursor.fetchall()
		cursor.close()
		conn.close()
		for user in users:
			bot.send_message(user[0], f"{user[1]}, время тренироваться!")
		time.sleep(60)

init_db()
t = threading.Thread(target=run_scheduler)
t.daemon = True
t.start()
bot.polling()
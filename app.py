import telebot
import requests
import datetime
import sqlite3
import random

bot = telebot.TeleBot("8733508077:AAFg6ZlARpEaATZ6lQKK3y5P3mUjlh5rF6k")
ключ = "8d18d8f5fed1302f0d3025adc1bf19c7"

conn = sqlite3.connect("пользователи.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER, имя TEXT)")
conn.commit()

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Привет! Напиши /погода «город», /курсы, /меню, /menu, /info /время или /запомни «имя»")

@bot.message_handler(commands=["монетка"])
def монетка(message):
    результат = random.choice(["Орел", "Решка"])
    bot.send_message(message.chat.id, результат)

@bot.message_handler(commands=["запомни"])
def запомни(message):
    имя = message.text.split(None, 1)[1] if len(message.text.split()) > 1 else ""
    c = sqlite3.connect("пользователи.db")
    c.execute("INSERT INTO users VALUES (?, ?)", (message.chat.id, имя))
    c.commit()
    c.close()
    bot.send_message(message.chat.id, f"Запомнил! Привет, {имя}!")

@bot.message_handler(commands=["info"])
def info(message):
     bot.send_message(message.chat.id, "Это мой первый бот! С его помощью я изучаю python!")

@bot.message_handler(commands=["время"])
def время(message):
    сейчас = datetime.datetime.now()
    bot.send_message(message.chat.id, f"Сейчас: {сейчас.strftime('%H:%M:%S')}")

@bot.message_handler(commands=["меню"])
def помощь(message):
    bot.send_message(message.chat.id, "Список команд:\n/погода «город» - погода в городе\n/курсы - курсы валют\n/меню - список команд\n/время - время сейчас\n/запомни «имя» - бот запомнит имя")

@bot.message_handler(commands=["menu"])
def menu(message):
    bot.send_message(message.chat.id, "List of commands:\n/погода «город» - weather in town\n/курсы - exchange rates\n/меню - list of commands\n/время - time now\n/запомни «имя» - remember name")

@bot.message_handler(commands=["погода"])
def погода(message):
    город = message.text.replace("/погода", "").strip()
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={город}&appid={ключ}&units=metric&lang=ru"
        data = requests.get(url).json()
        if data["cod"] == 200:
            темп = data["main"]["temp"]
            описание = data["weather"][0]["description"]
            bot.send_message(message.chat.id, f"Погода в {город}: {темп}C, {описание}")
        else:
            bot.send_message(message.chat.id, "Город не найден!")
    except:
        bot.send_message(message.chat.id, "Ошибка соединения!")

@bot.message_handler(commands=["курсы"])
def валюта(message):
    data = requests.get("https://api.exchangerate-api.com/v4/latest/USD").json()
    ответ = f"Курсы валют к доллару:\n"
    ответ += f"USD/RUB: {data['rates']['RUB']}\n"
    ответ += f"USD/EUR: {data['rates']['EUR']}\n"
    ответ += f"USD/GBR: {data['rates']['GBP']}\n"
    ответ += f"USD/CNY: {data['rates']['CNY']}\n"
    bot.send_message(message.chat.id, ответ)

@bot.message_handler(func=lambda message: True)
def ответ(message):
    bot.send_message(message.chat.id, "Выбери команду из доступных: /погода «город», /курсы, /меню или /время")

bot.polling()

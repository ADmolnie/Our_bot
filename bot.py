from config import *
import telebot
import time
import sqlite3 
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from random import randint
from logic import Text2ImageAPI
from translate import Translator

bot = telebot.TeleBot(TOKEN)

translator = Translator(from_lang="en", to_lang="ru")
sent4 = ''
sent5 = ''
r = 0

def senf_info(bot, message, row):
    global sent4
    global sent5
        
    info = f"""
📍Title of movie:   {row[2]}
📍Year:                   {row[3]}
📍Genres:              {row[4]}
📍Rating IMDB:      {row[5]}


🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻
{row[6]}
"""     
    sent5 = row[6]
    if sent4 == "off":
        bot.send_photo(message.chat.id, row[1])
    else:
        prompt = {row[6]}
        api = Text2ImageAPI('https://api-key.fusionbrain.ai/', api_key, secret_key)
        model_id = api.get_model()
        uuid = api.generate(prompt, model_id)
        images = api.check_generation(uuid)[0]
        file_path = 'decoded_image.jpg'
        api.save_image(images, file_path)
        with open(file_path,'rb') as photo:
            bot.send_photo(message.chat.id, photo)
    bot.send_message(message.chat.id, info)


def main_markup():
  markup = ReplyKeyboardMarkup()
  markup.add(KeyboardButton('/random'))
  return markup


@bot.message_handler(commands=['trans'])
def trans(message):
    global r
    global translator
    global sent5
    if r > 0:
        translation = translator.translate(sent5)
        bot.send_message(message.chat.id, translation)
    else:
        bot.send_message(message.chat.id, " ")


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, """Привет! Добро пожаловать в лучший Кино-Чат-Бот🎥!
Здесь вы можете найти 1000 фильмов 🔥
Нажмите /random, чтобы получить случайный фильм
Или напишите название фильма, и я постараюсь его найти! 🎬

!!!Обязательно: /help, иначе вы не сможете нормально пользоваться ботом""", reply_markup=main_markup())


@bot.message_handler(commands=['random'])
def random_movie(message):
    global r
    r += 1
    con = sqlite3.connect("movie_database.db")
    with con:
        cur = con.cursor()
        cur.execute(f"SELECT * FROM movies ORDER BY RANDOM() LIMIT 1")
        row = cur.fetchall()[0]
        cur.close()
    senf_info(bot, message, row)


@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.send_message(message.chat.id, """ Я тебе помогу!!!

/genre - после чего тебе нужно написать жанр на английском, с большой буквы, после чего тебе выдатут фильм с этим жанром, если хотите несколько жанров, то пишите каждую с большой буквы и через запятую
                     
/year - чабарнутая штука, которая выдаёт тебе фильм по дате выпуска (нужно писать так: пишем мначала знак >, < или == затем пишем год (> 2009) пробел обязателен!!!)
                     
/rating - сортирует по рейтингу, пишем почти также, как и /year (знак >, < или =, затем пишем: цифра.цифра (> 8.9))
                     
/random - выдаёт тебе рандомный фильм
                     
/AI - будет ли ИИ генерировать для вас изображение или нет, по умолчанию она включена(on)
                     
/trans - переведёт описание фильма на русский

Можете просто отправить название фильма, с большой буквы на инглиш
                     
если подумали: а где же избранное? То обломитесь, если понравилось, сразу смотрите!
            
                ВСЁ!""", reply_markup=main_markup())





@bot.message_handler(content_types=['text'])
def hello(message):
    if message.text == '/genre':
        sent1 = bot.send_message(message.from_user.id, "Каков?")
        bot.register_next_step_handler(sent1, genress)
    elif message.text == '/year':
        sent2 = bot.send_message(message.from_user.id, "Какой?")
        bot.register_next_step_handler(sent2, yearss)
    elif message.text == '/rating':
        sent3 = bot.send_message(message.from_user.id, "Какив?")
        bot.register_next_step_handler(sent3, ratingg)
    else: 
        if message.text == '/AI':
            sent4 = bot.send_message(message.from_user.id, "Введите on(ИИ -БУДЕТ- генерировать), или off(ИИ -НЕ БУДЕТ- генерировать)")
            bot.register_next_step_handler(sent4, AI)


def genress(message):
    global r
    r += 1
    sent1 = message.text
    con = sqlite3.connect("movie_database.db")
    with con:
        cur = con.cursor()
        cur.execute(f"SELECT * FROM movies WHERE genre LIKE '%{sent1}%' ORDER BY RANDOM() LIMIT 1")
        row = cur.fetchall()[0]
        cur.close()
    senf_info(bot, message, row)


def yearss(message): 
    global r
    sent2 = message.text
    a = ''
    a1 = ''
    b = 0
    c = 0
    for i in sent2:
        if b == 1:
            a1 += str(i)
        if str(i) != ' ' and b == 0:
            a += str(i)
        elif i == ' ':
            b += 1
        else:
            pass
    d = a + ' ' + '"' + a1 + '"'
    bot.send_message(message.chat.id, d)
    if a != '>' or a != '<' or a != '==':
        bot.send_message(message.chat.id, "Давай по новой(неправильный знак)")
        bot.send_message(message.chat.id, a)
        bot.send_message(message.chat.id, a1)
    elif a == '>' and int(a1) > 2020:
        bot.send_message(message.chat.id, "Фильм с годом больше чем 2020 нет")
    elif a == '<' and int(a1) < 1920:
        bot.send_message(message.chat.id, "Фильм с годом меньше чем 1920 нет")
    else:
        r += 1
        con = sqlite3.connect("movie_database.db")
        with con:
            cur = con.cursor()
            cur.execute(f"SELECT * FROM movies WHERE year {d} ORDER BY RANDOM() LIMIT 1")
            row = cur.fetchall()[0]
            cur.close()
        senf_info(bot, message, row)


def ratingg(message):
    global r
    sent3 = message.text
    a = ''
    a1 = ''
    a2 = ' '
    b = 0
    c = 0
    for i in sent3:
        if b == 1:
            a1 += str(i)
        if str(i) != ' ' and b == 0:
            a += str(i)
        elif i == ' ':
            b += 1
        else:
            pass
    d = a + a2 + '"' + a1 + '"'
    if a != '>' or a != '<' or a != '=':
        bot.send_message(message.chat.id, "Давай по новой(неправильный знак)")
    elif a == '>' and a1 == '9.3':
        bot.send_message(message.chat.id, "Фильм с рейтингом больше чем 9.3 нет")
    elif a == '<' and a1 == '7.6':
        bot.send_message(message.chat.id, "Фильм с рейтингом меньше чем 7.6 нет")
    else:
        r += 1
        con = sqlite3.connect("movie_database.db")
        with con:
            cur = con.cursor()
            cur.execute(f"SELECT * FROM movies WHERE rating {d} ORDER BY RANDOM() LIMIT 1")
            row = cur.fetchall()[0]
            cur.close()
        senf_info(bot, message, row)


def AI(message):
    global sent4
    sent4 = message.text
    if sent4 == 'off' or sent4 == 'on':
        bot.send_message(message.chat.id, "OKEY")
    else:
        bot.send_message(message.chat.id, "Давай по новой(не тот включатель или выключатель)")

    
@bot.message_handler(func=lambda message: True)
def echo_message(message):

    con = sqlite3.connect("movie_database.db")
    with con:
        cur = con.cursor()
        cur.execute(f"select * from movies where LOWER(title) = '{message.text.lower()}'")
        row = cur.fetchall()
        if row:
            row = row[0]
            bot.send_message(message.chat.id,"Of course! I know this movie😌")
            senf_info(bot, message, row)
        else:
            bot.send_message(message.chat.id,"I don't know this movie ")

        cur.close()



bot.infinity_polling()
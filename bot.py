# coding=utf-8
import telebot
from telebot import types
import mysql.connector
from variables import *
import random

global back
back = []
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id, start_mess)


@bot.message_handler(commands=['help'])
def help_handler(message):
    bot.send_message(message.chat.id, help_mess)


@bot.message_handler(commands=['go'])
def dish_command(message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(
        types.InlineKeyboardButton('второе', callback_data='get-garnish'),
        types.InlineKeyboardButton('десерт', callback_data='get-desserts'),
        types.InlineKeyboardButton('первое', callback_data='get-soups')
    )
    keyboard.row(
        types.InlineKeyboardButton('напиток', callback_data='get-drinks'),
        types.InlineKeyboardButton('сэндвич', callback_data='get-sandwiches'),
        types.InlineKeyboardButton('салат', callback_data='get-salads')
    )
    keyboard.row(
        types.InlineKeyboardButton('соус', callback_data='get-sauces'),
        types.InlineKeyboardButton('закуски', callback_data='get-snacks')
    )
    bot.send_message(
        message.chat.id,
        'Выберите, что вы хотите приготовить:',
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: True)
def iq_callback(call):
    global back
    data = call.data
    if data.startswith('get-'):
        bot.send_message(call.message.chat.id, kcal_mess)
        back.append([call.message.chat.id, data[4:]])


@bot.message_handler(content_types=['text'])
def send_text(message):
    global back
    try:
        kcal_borders = message.text.split()
        if len(kcal_borders) != 2:
            kcal_borders = 'error'
            kcal_borders = [int(item) for item in kcal_borders]
        else:
            kcal_borders = [int(item) for item in kcal_borders]
    except ValueError:
        bot.send_message(message.chat.id, sorry_error)
    else:
        for i in back:
            if i[0] == message.chat.id:
                if find_dishes(i[1], kcal_borders[0], kcal_borders[1]) is not None:
                    id_dish = find_dishes(i[1], kcal_borders[0], kcal_borders[1])
                    print_dishes(i[1], id_dish, message)
                else:
                    bot.send_message(message.chat.id, sorry)


def print_dishes(dish, id_dish, id_person):
    connection = mysql.connector.connect(host='localhost', database='12team', user='root', password='')
    cur = connection.cursor()
    s = 'SELECT * FROM ' + dish
    cur.execute(s)
    rows = cur.fetchall()
    for row in rows:
        if row[0] == id_dish:
            recipe = '{0}\n\n{1}\n\n{2}\n\nКолличество порций: {3}\n\n{4}'.format(str(row[1]), str(row[4]),
                                                                                  str(row[5]).strip('\n'), str(row[6]),
                                                                                  str(row[2]))
            bot.send_message(id_person.chat.id, recipe)


def find_dishes(dish, kcal_person_min, kcal_person_max):
    connection = mysql.connector.connect(host='localhost', database='12team', user='root', password='')
    cur = connection.cursor()
    s = 'SELECT * FROM ' + dish
    cur.execute(s)
    kcal = []
    a = False
    rows = cur.fetchall()
    for row in rows:
        if (row[3] <= kcal_person_max) and (row[3] >= kcal_person_min):
            kcal.append(row[0])
            a = True
    if a:
        return random.choice(kcal)
    else:
        return None


bot.polling()

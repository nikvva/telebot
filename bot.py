# coding=utf-8
import telebot
from telebot import types
import mysql.connector
import random
import os
from variables import *


class person:  # класс с двумя атрибутами, первый - id чата, второй - блюдо, которое выбрал пользователь
    def __init__(self, new_id, new_callback):
        self.id = new_id
        self.callback = new_callback


def print_dishes(dish, id_person):  # функция отправляет пользователю блюдо по данным им критериям
    recipe = '{0}\n\n{1}\n\n{2}\n\nКолличество порций: {3}\n\n{4}'.format(str(dish[1]), str(dish[4]),
                                                                          str(dish[5]).strip('\n'),
                                                                          str(dish[6]), str(dish[2]))
    # 1-название, 4-ингридиенты, 5-рецепт приготовления, 6-количетво порций, на которое рассчитан рецепт, 2-изображение
    bot.send_message(id_person, recipe)


def find_dishes(kcal_person_min, kcal_person_max, id_person):  # функция поиска блюда в базе данных по данным критериям
    connection = mysql.connector.connect(host='eu-cdbr-west-03.cleardb.net', database='heroku_05c0bf788994a4e ', user='b49a02d4dd4fbd', password='2e7e444c')
    cur = connection.cursor()  # подключились к базе данных
    s = 'SELECT * FROM ' + str(d[id_person].callback)
    cur.execute(s)  # сделали запрос в базу и вывели необходимую таблицу
    title = []  # в этом массиве будут храниться строки с блюда, удовлетворяющему критериям
    rows = cur.fetchall()
    for row in rows:
        if (row[3] <= kcal_person_max) and (row[3] >= kcal_person_min):  # проверяем блюда на необходимое число калори1
            title.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6]])  # записываем блюдо в массив
    if title:
        print_dishes(random.choice(title), id_person)  # если блюдо нашлось, то выводим рандомное
    else:
        bot.send_message(id_person, sorry)  # если блюдо не нашлось, то выводим сообщение о том, что его нет


TOKEN = os.environ.get('bot_token')
bot = telebot.TeleBot(TOKEN)
d = {}


@bot.message_handler(commands=['start'])  # обработка команды start
def start_handler(message):
    bot.send_message(message.chat.id, start_mess)


@bot.message_handler(commands=['help'])  # обработка команды help
def help_handler(message):
    bot.send_message(message.chat.id, help_mess)


@bot.message_handler(commands=['go'])  # обработка команды go
def dish_command(message):  # создаем клавиатуру с вариантами категорий блюд
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(
        types.InlineKeyboardButton('второе', callback_data='garnish'),
        types.InlineKeyboardButton('десерт', callback_data='desserts'),
        types.InlineKeyboardButton('первое', callback_data='soups')
    )
    keyboard.row(
        types.InlineKeyboardButton('напиток', callback_data='drinks'),
        types.InlineKeyboardButton('сэндвич', callback_data='sandwiches'),
        types.InlineKeyboardButton('салат', callback_data='salads')
    )
    keyboard.row(
        types.InlineKeyboardButton('выпечка', callback_data='cakes'),
        types.InlineKeyboardButton('соус', callback_data='sauces'),
        types.InlineKeyboardButton('закуски', callback_data='snacks')
    )
    bot.send_message(  # отправляем эту клавиатуру пользователю
        message.chat.id,
        'Выберите, что вы хотите приготовить:',
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: True)  # принимаем выбранное блюдо
def iq_callback(call):
    d[call.message.chat.id] = person(call.message.chat.id, call.data)  # записываем в словарь  id и блюдо пользователя
    bot.send_message(call.message.chat.id, kcal_mess)  # отправляем сообщение о дальнейшем действии


@bot.message_handler(content_types=['text'])  # принимаем сообщение
def send_text(message):
    try:  # проверка на первое сообщение в чате, без выбора блюда
        Processing_message(message)
    except KeyError:
        bot.send_message(message.chat.id, sorry_error)
    else:
        Processing_message(message)


def Processing_message(message):
    try:  # проверка на правильность введенных калорий
        kcal_borders = message.text.split()
        if len(kcal_borders) != 2:
            kcal_borders = 'error'  # если числа не два, то ошибка (строка 94)
            kcal_borders = [int(item) for item in kcal_borders]
        else:
            kcal_borders = [int(item) for item in kcal_borders]
    except ValueError:
        bot.send_message(message.chat.id, sorry_error)  # если данные введены неправильно, говорим об этом
    else:
        find_dishes(kcal_borders[0], kcal_borders[1], message.chat.id)  # находим и выводим необходимое блюдо


bot.polling()


# t.me/Crypto888_Bot
import requests
import json
import telebot
from telebot import types

from config import keys, TOKEN
from extensions import ConversionException, Converter
import traceback


def create_markup(base=None):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    buttons = []
    for val in keys.keys():
        if val != base:
            buttons.append(types.KeyboardButton(val.capitalize()))

    markup.add(*buttons)
    return markup


bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def start(message: telebot.types.Message):
    text = 'Доброго времени суток.\nДля начала работы, введите команду боту в следующем формате:\n<Имя валюты> \
<в какую валюту перевести> \
<количество переводимой валюты>\nУвидеть список доступных валют: /values'
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['values'])
def values(message: telebot.types.Message):
    text = 'Доступные валюты:\n/convert '
    for key in keys.keys():
        text = '\n'.join((text, key))
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['convert'])
def values(message: telebot.types.Message):
    text = 'Выберите валюту, из которой нужно конвертировать: '
    bot.send_message(message.chat.id, text, reply_markup=create_markup())
    bot.register_next_step_handler(message, base_handler)

def base_handler(message: telebot.types.Message):
    base = message.text.strip().lower()
    text = 'Выберите валюту, в которую нужно конвертировать: '
    bot.send_message(message.chat.id, text, reply_markup=create_markup(base))
    bot.register_next_step_handler(message, sym_handler, base)

def sym_handler(message: telebot.types.Message, base):
    sym = message.text.strip().lower()
    text = 'Выберите количество конвертируемой валюты: '
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, amount_handler, base, sym)

def amount_handler(message: telebot.types.Message, base, sym):
    amount = message.text.strip()
    try:
        new_price = Converter.get_price(base, sym, amount)
    except ConversionException as e:
        bot.send_message(message.chat.id, f"Ошибка конвертации:\n{e}")
    else:
        text = f"Цена {amount} {base} в {sym} : {new_price}"
        bot.send_message(message.chat.id, text)

@bot.message_handler(content_types=['text'])
def converter(message: telebot.types.Message):
    values = message.text.split(' ')

    try:
        if len(values) != 3:
            raise ConversionException('Неверное количество параметров!')

        answer = Converter.get_price(*values)


    except ConversionException as e:
        bot.reply_to(message, f'Ошибка пользователя.\n{e}')
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        bot.reply_to(message, f'Не удалось обработать команду\n{e}')
    else:
        bot.reply_to(message, answer)


bot.polling()
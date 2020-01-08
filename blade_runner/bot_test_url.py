# -*- coding: utf-8 -*-

import telegram

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from functools import wraps

import logging
import cv2
import os
import numpy as np
import urllib.request

BOT_TOKEN = "934772940:AAFqqYQK_LOfrjlEpIYv1dT30-oVLX289Sc"
URL = "https://api.telegram.org/bot%s/" % BOT_TOKEN

# logic:
# 1 welcome v
# 2 get image v
# 3 show menu
# 4 read menu button
# 5 proceed calculations
#       or handle an exception with message to user v

updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher
bot = telegram.Bot(token=BOT_TOKEN)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


# Menu content
def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu


button_list = [
    InlineKeyboardButton('3,2 м', callback_data=3.2),
    InlineKeyboardButton('3,9 м', callback_data=3.9),
    InlineKeyboardButton('4,8 м', callback_data=4.8),
    InlineKeyboardButton('5,2 м', callback_data=5.2),
    InlineKeyboardButton('6 м', callback_data=6.0)
]
print('button type: ', type(button_list[0]))
wood_length_menu = InlineKeyboardMarkup(build_menu(buttons=button_list,
                                                   n_cols=2, ))


def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text='Загрузите фотографию лесовоза, условия: \n' +
                                  '1. Автомобиль целиком помещается в кадр. \n' +
                                  '2. Вертикальное фото сзади, строго перпендикулярно. \n' +
                                  '3. Номерной знак в кадре и хорошо читаем.')


def get_help(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text=' - Для запуска бота используйте команду /start \n' +
                                                                  '- Если бот не может обнаружить номерной знак,'
                                                                  ' возможно, что он загрязнен или нечитаем, попробуйте'
                                                                  ' другое фото \n' +
                                                                  '- В демо-версии бот корректно обрабатывает '
                                                                  'изображения, на которых древесина по длине уложена'
                                                                  ' до задней границы лесовоза')


# function for wood detection on image
def detect_wood(image, wood_length, **kwargs) -> float:
    # code for counting wood volume
    pass


def url_to_image(url):
    # download the image, convert it to a NumPy array, and then read
    # it into OpenCV format
    resp = urllib.request.urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    return image


# function to get wood length by keyboard markup
def send_wood_length(update, context):
    update.message.reply_text(text='Укажите длину брёвен в метрах:',
                              reply_markup=wood_length_menu)


def count_wood(update, context):
    query = update.callback_query
    wood_length = float(query.data)
    context.bot.send_message(chat_id=query.message.chat_id, text='Длина брёвен %f ' % wood_length)


# function that called when user sends image to the bot
def get_truck_image(update, context):
    update.message.reply_text('Обрабатываю изображение')

    # Use update.message.photo[-1] to get the biggest size.
    photo_file = bot.getFile(update.message.photo[-1].file_id)
    # get filepath, more on https://core.telegram.org/bots/api/#file
    image_path = photo_file.file_path  # image.jpg url on tg servers
    truck_image = url_to_image(image_path)
    update.message.reply_text('Изображение загружено')

    # probably should call send_wood_length from here
    send_wood_length(update, context)
    try:
        detect_wood(image=truck_image)
        # code for wood detection here
    except NotImplementedError as error:
        context.bot.send_message(chat_id=update.message.chat_id, text='При обработке возникла ошибка %s' % error)


def unknown(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text='Мне не известна эта команда, попробуйте /help')


def main():
    # start and help handlers
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(CommandHandler('help', get_help))

    # handler for image content
    get_truck_image_handler = MessageHandler(filters=Filters.photo, callback=get_truck_image)
    dispatcher.add_handler(get_truck_image_handler)

    # handler for user menu choice
    dispatcher.add_handler(CallbackQueryHandler(count_wood))

    # # handler for errors
    # dispatcher.add_error_handler(error_callback)

    # handler for unknown commands
    unknown_handler = CommandHandler('unknown', unknown)
    dispatcher.add_handler(unknown_handler)

    # starting a bot
    updater.start_polling()


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
import telegram
import logging
import urllib.request
from typing import TYPE_CHECKING
from telegram.ext import Updater, CommandHandler


if TYPE_CHECKING:
    from telegram import Update
    from telegram.ext import CallbackContext

# TODO: get bot token
BOT_TOKEN = "934772940:AAFqqYQK_LOfrjlEpIYv1dT30-oVLX289Sc"
URL = "https://api.telegram.org/bot%s/" % BOT_TOKEN


def start(update: 'Update', context: 'CallbackContext') -> None:
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Hello! What\'s my purpose?'
    )


def get_help(update: 'Update', context: 'CallbackContext') -> None:
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='I am here to serve'
    )


# bot should be an admin
def check_priveleges(update: 'Update', context: 'CallbackContext') -> None:
    bot_member_info = context.bot.get_chat_member(chat_id=update.message.chat_id, user_id=context.bot.id)
    bot_member_info.status = 'administrator'


# TODO: make bot delete user from chat
# https://python-telegram-bot.readthedocs.io/en/stable/telegram.chat.html#telegram.Chat.kick_member
def purge(update: 'Update', context: 'CallbackContext', target_name: 'telegram.User.name') -> None:
    # somehow get user or user_id from User.name, check docs for get_chat_member
    target = context.bot.get_chat_member(target_name)

    if target.user.is_bot:
        context.bot.kick_chat_member(target_name)
        context.bot.send_message(chat_id=update.message.chat_id, text='You have failed Turing test')
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text='I can not purge meatbags')


def unknown(update: 'Update', context: 'CallbackContext') -> None:
    context.bot.send_message(
        chat_id=update.message.chat_id, text='I am not programmed to do that'
    )


def main():
    updater = Updater(token=BOT_TOKEN, use_context=True)
    add_handler = updater.dispatcher.add_handler

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s- %(message)s',
                        level=logging.INFO)

    add_handler(CommandHandler('start', start))
    add_handler(CommandHandler('help', get_help))
    add_handler(CommandHandler('unknown', unknown))

    # add purge handler
    add_handler(CommandHandler('purge', purge))

    # start blade runner
    updater.start_polling()


if __name__ == '__main__':
    main()

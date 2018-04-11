from telegram import ReplyKeyboardMarkup # модуль почему-то просто telegram ¯\_(ツ)_/¯
from telegram.ext import Updater  # пакет называется python-telegram-bot, но Python-

import logging
import time as t

class Bot:
    def __init__(self,token,filename):
        self.updater = Updater(token)
        logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s  %(message)s',
                        filename=filename, filemode='w')

        self.reply_keyboard = [['Русский язык', 'Математика'], ['Литература', 'История']]
    def start(self,bot, update):
        bot.sendMessage(chat_id=update.message.chat_id, text="Привет, что ты хочешь изучать?", reply_markup = ReplyKeyboardMarkup(self.reply_keyboard, one_time_keyboard=True))


    def text_handler(self, bot, update):
        good_chose = 'хороший выбор'
        mes = update.message.text
        if mes == 'Русский язык':
            bot.sendMessage(chat_id=update.message.chat_id, text=good_chose)

        elif mes == 'Математика':
            bot.sendMessage(chat_id=update.message.chat_id, text=good_chose)
        elif mes == 'Литература':
            bot.sendMessage(chat_id=update.message.chat_id, text=good_chose)
        elif mes == 'История':
            bot.sendMessage(chat_id=update.message.chat_id, text=good_chose)

        logging.info('%s,%s,%s'%(t.time(),update.message.from_user.first_name,mes))


    def begin_work(self,start_handler,message_handler):
        self.updater.dispatcher.add_handler(start_handler)
        self.updater.dispatcher.add_handler(message_handler)

        self.updater.start_polling()



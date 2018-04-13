from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater
import logging
import time as t

from telegram.ext.dispatcher import run_async

import db
import random as r
import copy

import literature, hist, mathematic, russ


class Bot:
    def __init__(self, token, filename, db_filename, log_level):
        self.updater = Updater(token)
        logging.basicConfig(level=log_level, format='[%(asctime)s] %(levelname)s  %(message)s',
                            filename=filename, filemode='w')

        self.reply_keyboard = [['Русский язык', 'Математика'], ['Литература', 'История']]

        self.db = db.DB()
        self.con = self.db.begin(db_filename)
        self.cur = self.con.cursor()

        # self.db.create(self.cur,'CREATE TABLE Users (id INTEGER PRIMARY KEY, tg_userID VARCHAR(15), tg_first_name VARCHAR(20), tg_last_name VARCHAR(20))')
        # self.con.commit()

        self.russian = russ.russian

        self.math = mathematic.math

        self.history = hist.history

        self.literature = literature.literature

        self.obj = None
        self.question = None

    def get_question(self, obj):
        if obj == 'Русский язык':
            question = copy.deepcopy(self.russian)
        if obj == 'Математика':
            question = copy.deepcopy(self.math)
        if obj == 'Литература':
            question = copy.deepcopy(self.literature)
        if obj == 'История':
            question = copy.deepcopy(self.history)

        keys = r.choice(list(question.keys()))
        answers = question[keys]
        true_answer = answers[len(answers) - 1]
        r.shuffle(answers)

        return [true_answer, answers, keys]

    def ask_question(self, obj, disc, bot, update):

        self.quest = self.get_question(obj)

        self.answers = [self.quest[1]]
        self.answers.append(['Вернуться назад'])
        bot.sendMessage(chat_id=update.message.chat_id, text=disc + self.quest[2],
                        reply_markup=ReplyKeyboardMarkup(self.answers, one_time_keyboard=False))

    def start(self, bot, update):
        bot.sendMessage(chat_id=update.message.chat_id, text="Привет, что ты хочешь изучать?",
                        reply_markup=ReplyKeyboardMarkup(self.reply_keyboard, one_time_keyboard=True))
        self.db.insert_user(self.con, update)

    def help_handler(self, bot, update):
        bot.sendMessage(chat_id=update.message.chat_id, text='Внизу выбери, что ты хочешь изучать.\n'
                                                             'Ответь правильно на вопрос и развивайся дальше\n'
                                                             'Если тебе надоело на каком-то предмете нажми "Вернуться назад"\n'
                                                             'Прежде чем ответить - подумай\n'
                                                             ''
                                                             'Удачи!')

    @run_async
    def object_handler(self, bot, update):
        mes = update.message.text
        if mes == 'Русский язык':
            self.question = 'Где правильно выделен корень у слова '
            self.obj = 'Русский язык'
            self.ask_question(self.obj, self.question, bot, update)


        elif mes == 'Математика':
            self.question = 'Найди значение выражения '
            self.obj = 'Математика'
            self.ask_question(self.obj, self.question, bot, update)
        elif mes == 'Литература':
            self.question = 'Кто написал произведение '
            self.obj = 'Литература'
            self.ask_question(self.obj, self.question, bot, update)
        elif mes == 'История':
            self.question = 'Выбери правилльную столицу у '
            self.obj = 'История'
            self.ask_question(self.obj, self.question, bot, update)
        if update.message.text == 'Вернуться назад':
            self.obj = None
            self.question = None
            bot.sendMessage(chat_id=update.message.chat_id, text="Возращаю",
                            reply_markup=ReplyKeyboardMarkup(self.reply_keyboard, one_time_keyboard=True))
        try:
            logging.debug(self.quest)
        except NameError:
            pass
        if any(mes in s for s in self.quest[1]):
            logging.debug("ANSWER IN DICT")
            if str(mes) == self.quest[0]:
                bot.sendMessage(chat_id=update.message.chat_id, text='✅Правильно')
                self.db.insert_answers(self.con, update, self.obj, 1, 0)
                self.ask_question(self.obj, self.question, bot, update)
            else:
                self.db.insert_answers(self.con, update, self.obj, 0, 1)
                r.shuffle(self.quest[1])
                bot.sendMessage(chat_id=update.message.chat_id, text='❌Неправильно, попробуй еще',
                                reply_markup=ReplyKeyboardMarkup(self.answers, one_time_keyboard=False))

        else:
            bot.sendMessage(chat_id=update.message.chat_id, text='Выбирете ответ на кнопках, пожалуйста')

        logging.info('%s,%s' % (update.message.from_user.first_name, mes))

    def begin_work(self, start_handler, message_handler, help_handler):
        self.updater.dispatcher.add_handler(start_handler)
        self.updater.dispatcher.add_handler(message_handler)
        self.updater.dispatcher.add_handler(help_handler)

        self.updater.start_polling(poll_interval=2)

from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater
import logging
import time as t

from telegram.ext.dispatcher import run_async

import db
import random as r
import copy
import config


class Bot:
    def __init__(self, token, filename, db_filename, log_level):
        self.updater = Updater(token, request_kwargs={'proxy_url': 'socks5://5.189.165.75:1080/'})
        logging.basicConfig(level=log_level, format='[%(asctime)s] %(levelname)s  %(message)s',
                            filename=filename, filemode='w')

        self.reply_keyboard = [['Русский язык', 'Математика'], ['Литература', 'История'], ['Статистика']]

        self.db = db.DB()
        self.con = self.db.begin(db_filename)
        self.cur = self.con.cursor()

        # self.db.create(self.cur,'CREATE TABLE Users (id INTEGER PRIMARY KEY, tg_userID VARCHAR(15), tg_first_name VARCHAR(20), tg_last_name VARCHAR(20))')
        # self.con.commit()

        math_conf = config.Read('mathematic.json')
        math = math_conf.getDict()

        russ_conf = config.Read('russ.json')
        russ = russ_conf.getDict()

        hist_conf = config.Read('hist.json')
        hist = hist_conf.getDict()

        lit_conf = config.Read('literature.json')
        lit = lit_conf.getDict()

        self.russian = russ

        self.math = math

        self.history = hist

        self.literature = lit

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

    def stat(self, bot, update):
        self.top = [['ТОП часа', 'ТОП дня'], ['ТОП за всё время'], ['Вернуться назад']]
        mes = update.message.text
        print(mes)
        if mes == 'Статистика':
            bot.sendMessage(chat_id=update.message.chat_id, text='Сейчас покажу',
                            reply_markup=ReplyKeyboardMarkup(self.top, one_time_keyboard=False))


        elif mes == 'ТОП часа':
            ret = self.db.get_stat(self.con, update, 2)
            bot.sendMessage(chat_id=update.message.chat_id,
                            text='Общий рейтинг пользователей за час:\n\n' + ret)

        elif mes == 'ТОП дня':
            ret = self.db.get_stat(self.con, update, 1)
            bot.sendMessage(chat_id=update.message.chat_id,
                            text='Общий рейтинг пользователей за день:\n\n' + ret)

        elif mes == 'ТОП за всё время':
            ret=self.db.get_stat(self.con, update, 0)
            bot.sendMessage(chat_id=update.message.chat_id,
                            text='Общий рейтинг пользователей за всё время:\n\n'+ret)

        # else:
        #   bot.sendMessage(chat_id=update.message.chat_id, text='Выбирете ответ на кнопках, пожалуйста')

    def help_handler(self, bot, update):
        bot.sendMessage(chat_id=update.message.chat_id, text='Внизу выбери, что ты хочешь изучать.\n'
                                                             'Ответь правильно на вопрос и развивайся дальше\n'
                                                             'Если тебе надоело на каком-то предмете нажми "Вернуться назад"\n'
                                                             'Прежде чем ответить - подумай\n'
                                                             ''
                                                             'Удачи!')

    def object_handler(self, bot, update):
        mes = update.message.text
        self.stat(bot, update)
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
        except AttributeError:
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

        logging.info('%s,%s' % (update.message.from_user.first_name, mes))

    def begin_work(self, start_handler, message_handler, help_handler):
        self.updater.dispatcher.add_handler(start_handler)

        self.updater.dispatcher.add_handler(message_handler)
        ##self.updater.dispatcher.add_handler(top)
        self.updater.dispatcher.add_handler(help_handler)

        self.updater.start_polling(poll_interval=1, timeout=30)

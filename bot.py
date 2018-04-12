from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater
import logging
import time as t

import db
import random as r
import copy



class Bot:
    def __init__(self,token,filename,db_filename):
        self.updater = Updater(token)
        logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)s  %(message)s',
                        filename=filename, filemode='w')



        self.reply_keyboard = [['Русский язык', 'Математика'], ['Литература', 'История']]



        self.db = db.DB()
        self.con = self.db.begin(db_filename)
        self.cur = self.con.cursor()

        #self.db.create(self.cur,'CREATE TABLE Users (id INTEGER PRIMARY KEY, tg_userID VARCHAR(15), tg_first_name VARCHAR(20), tg_last_name VARCHAR(20))')
        #self.con.commit()

        self.russian = {
            "Бегемот?": ["-бег-", "-бегем-", "-бегемот-"],
            "Ложка?":['-ложка-','-ложк-','-лож-'],
            "Телефон?":['-телефон-','-теле- и -фон-','-тел- и -фон-'],
            "Дорожка?":['-дорожк-','-дорожка-','-дорож-'],


            "Курица?":['-ку-','-куриц-','-кур-'],
            "Попугай?":['-поп-','-пуг-','-попугай-'],
            "Птицы?":['-пт-','-птицы-','-птиц-'],
            "Делать?":['-делать-','-лат-','-дел-'],
            "Расти?":['-рас-','-расти-','-раст-'],
            "Идти?":['-идти-','-идт-','-ид-'],
            "Пушистые?":['-пушистые-','-пушист-','-пуш-'],
            "Раскрас?":['-раскрас-','-рас-','-крас-'],
            "Кукуруза?":['-куку-','-куку- и -руз-','-кукуруз-'],
            "Акула?":['-ак-','-акула-','-акул-'],
            }
        self.math = {
            '20*20':   ['40', '4000', '400'],
            '7*13':    ['70', '121', '101'],
            '346+285': ['501', '701', '631'],
            '738-256': ['582', '382', '482']
        }

        self.history = {
            'Греция':   ['Анкара','Рим','Афины'],
            'Россия':   ['Тверь','Санкт-Петебург','Москва'],
            'Ярославль':['Вавилон','Афины','Нет столицы'],
            'Америка':  ['Оттава','Хельсинки','Вашингтон']
        }

        self.literature = {
            'Заячьи лапы':['Л.Толстой','А.Пушкин','К.Паустовский'],
            'Снежная королева':['А.Толстой','','Г.Андерсен'],
            'Лев и собачка':['С.Есенин','А.Толстой','Л.Толстой'],
            'Васюткино озеро':['А.Пушкин','В.Жуковский','В.Астафьев']
        }

        self.obj = None
        self.question = None
    def get_question(self,obj):
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
        true_answer = answers[len(answers)-1]
        r.shuffle(answers)

        return [true_answer, answers, keys]


    def ask_question(self,obj,disc,bot,update):


        self.quest = self.get_question(obj)

        self.answers = [self.quest[1]]
        self.answers.append(['Вернуться назад'])
        bot.sendMessage(chat_id=update.message.chat_id, text=disc + self.quest[2],
                        reply_markup=ReplyKeyboardMarkup(self.answers, one_time_keyboard=False))



    def start(self,bot, update):
        bot.sendMessage(chat_id=update.message.chat_id, text="Привет, что ты хочешь изучать?", reply_markup = ReplyKeyboardMarkup(self.reply_keyboard, one_time_keyboard=True))
        self.db.insert_user(self.con, update)




    def object_handler(self, bot, update):
        mes = update.message.text
        if mes == 'Русский язык':
            self.question = 'Где правильно выделен корень у слова '
            self.obj = 'Русский язык'
            self.ask_question(self.obj,self.question,bot,update)


        elif mes == 'Математика':
            self.question ='Найди значение выражения '
            self.obj = 'Математика'
            self.ask_question(self.obj, self.question, bot, update)
        elif mes == 'Литература':
            self.question ='Кто написал '
            self.obj = 'Литература'
            self.ask_question(self.obj, self.question, bot, update)
        elif mes == 'История':
            self.question ='Выбери правилльную столицу у '
            self.obj = 'История'
            self.ask_question(self.obj, self.question, bot, update)
        if update.message.text == 'Вернуться назад':
            self.obj = None
            self.question = None
            bot.sendMessage(chat_id=update.message.chat_id, text="Возращаю", reply_markup = ReplyKeyboardMarkup(self.reply_keyboard, one_time_keyboard=True))

        logging.debug(self.quest)

        if any(mes in s for s in self.quest[1]):
            logging.debug("ANSWER IN DICT")
            if str(mes) == self.quest[0]:
                bot.sendMessage(chat_id=update.message.chat_id, text = 'Правильно')

                self.ask_question(self.obj,self.question,bot,update)
            else:
                r.shuffle(self.quest[1])
                bot.sendMessage(chat_id=update.message.chat_id, text='Неправильно, попробуй еще',reply_markup = ReplyKeyboardMarkup(self.answers, one_time_keyboard=False))

        else:
            bot.sendMessage(chat_id = update.message.chat_id, text = 'Выбирете ответ на кнопках, пожалуйста')

        logging.info('%s,%s,%s' % (t.asctime(), update.message.from_user.first_name, mes))

    def begin_work(self,start_handler,message_handler):
        self.updater.dispatcher.add_handler(start_handler)
        self.updater.dispatcher.add_handler(message_handler)

        self.updater.start_polling(poll_interval=2)
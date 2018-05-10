from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater
import logging
import db
import random as r
import config
import Object


class Bot:
    def __init__(self, token, filename, db_filename, log_level, proxy_url, obj_path):
        if proxy_url:
            self.updater = Updater(token, request_kwargs={'proxy_url': proxy_url})
        else:
            self.updater = Updater(token)

        logging.basicConfig(level=log_level, format='[%(asctime)s] %(levelname)s  %(message)s',
                            filename=filename, filemode='w')
        conf = config.Read(obj_path)

        self.data = conf.getVars('data')

        self.reply_keyboard = self.data_for_keyboard(self.data)

        self.db = db.DB()
        self.con = self.db.begin(db_filename)
        self.cur = self.con.cursor()

        self.objects = Object.get_objects(obj_path)

        self.question = None

    def data_for_keyboard(self, data):
        objects = []
        obj_test = []
        for i in range(0, len(data) + 1):
            if len(obj_test) == 2:
                objects.append(obj_test)
                obj_test = []
            if i == len(data) and len(obj_test) != 2 and len(data) % 2 != 0:
                objects.append(data[i - 1])
            try:
                obj_test.append(data[i]["name"])
            except:
                pass
        objects.append(['Статистика'])
        return objects

    def load_subj_json(self, obj_name):
        for i in range(len(self.data)):

            if self.data[i]["name"] == obj_name:
                path = self.data[i]["path"]
                return config.Read(path).getDict()

    def ask_question(self, bot, update, obj):

        self.quest = Object.get_question(obj)

        self.db.insert_questions(self.con, update, self.quest, obj)

        self.answers = [self.quest[1]]
        self.answers.append(['Вернуться назад'])
        bot.sendMessage(chat_id=update.message.chat_id, text=obj.question + self.quest[2],
                        reply_markup=ReplyKeyboardMarkup(self.answers, one_time_keyboard=False, resize_keyboard=True))

    def start(self, bot, update):
        bot.sendMessage(chat_id=update.message.chat_id, text="Привет, что ты хочешь изучать?",
                        reply_markup=ReplyKeyboardMarkup(self.reply_keyboard, one_time_keyboard=True,
                                                         resize_keyboard=True))
        self.db.insert_user(self.con, update)

    def stat(self, bot, update):
        self.top = [['ТОП часа', 'ТОП дня'], ['ТОП за всё время'], ['Вернуться назад']]
        mes = update.message.text
        print(mes)
        if mes == 'Статистика':
            bot.sendMessage(chat_id=update.message.chat_id, text='Сейчас покажу',
                            reply_markup=ReplyKeyboardMarkup(self.top, one_time_keyboard=False, resize_keyboard=True))

        elif mes == 'ТОП часа':
            ret = self.db.get_stat(self.con, update, 2)
            bot.sendMessage(chat_id=update.message.chat_id,
                            text='Общий рейтинг пользователей за час:\n\n' + ret)

        elif mes == 'ТОП дня':
            ret = self.db.get_stat(self.con, update, 1)
            bot.sendMessage(chat_id=update.message.chat_id,
                            text='Общий рейтинг пользователей за день:\n\n' + ret)

        elif mes == 'ТОП за всё время':
            ret = self.db.get_stat(self.con, update, 0)
            bot.sendMessage(chat_id=update.message.chat_id,
                            text='Общий рейтинг пользователей за всё время:\n\n' + ret)

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

        tmp_obj = Object.get_object(self.objects, mes)
        if tmp_obj:
            obj = tmp_obj
            self.ask_question(bot, update, obj)

        self.quest_for_check = self.db.select_ques_for_user(self.con, update)
        # print(self.quest_for_check)

        if update.message.text == 'Вернуться назад':
            self.db.delete_row(self.con, update)
            #    print('type keyboard', type(self.reply_keyboard))
            #   print('reply_keyboard', self.reply_keyboard)
            self.question = None
            bot.sendMessage(chat_id=update.message.chat_id, text="Возращаю",
                            reply_markup=ReplyKeyboardMarkup(self.reply_keyboard, one_time_keyboard=True,
                                                             resize_keyboard=True))

        try:
            logging.debug(self.quest)
        except AttributeError:
            pass

        self.check_answer(mes, bot, update, self.quest_for_check)

    def check_answer(self, mes, bot, update, quest):

        if any(mes in s for s in quest[1]):
            obj = Object.get_object(self.objects, self.quest_for_check[2])
            logging.debug("ANSWER IN DICT")
            if str(mes) == quest[0]:
                bot.sendMessage(chat_id=update.message.chat_id, text='✅Правильно')
                self.db.insert_answers(self.con, update, obj.name, 1, 0)

                self.ask_question(bot, update, obj)
            else:

                inc_answ = self.db.add_incorrect_answer(self.con, update)

                if inc_answ[0][0] == len(quest[1]) - 2:
                    bot.sendMessage(chat_id=update.message.chat_id,
                                    text='❌Неправильно\n ‼ На самом деле правильный ответ: ' + quest[0])
                    self.ask_question(bot, update, obj)

                else:
                    self.db.insert_answers(self.con, update, obj.name, 0, 1)

                    r.shuffle(quest[1])
                    ques = []
                    ques.append(quest[1])
                    ques.append(['Вернуться назад'])
                    bot.sendMessage(chat_id=update.message.chat_id, text='❌Неправильно, попробуй еще',
                                    reply_markup=ReplyKeyboardMarkup(ques, one_time_keyboard=False,
                                                                     resize_keyboard=True))

        logging.info('%s,%s' % (update.message.from_user.first_name, mes))

    def begin_work(self, start_handler, message_handler, help_handler):
        self.updater.dispatcher.add_handler(start_handler)

        self.updater.dispatcher.add_handler(message_handler)
        ##self.updater.dispatcher.add_handler(top)
        self.updater.dispatcher.add_handler(help_handler)
        self.updater.start_polling()

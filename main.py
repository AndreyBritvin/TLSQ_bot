from telegram.ext import CommandHandler, MessageHandler, Filters

import bot
import db
import config


def main():
    conf = config.Read('config.json')
    token = conf.getVars('BOT_TOKEN')
    log_file = conf.getVars('LOG_FILE_NAME')
    db_file = conf.getVars('DB_FILE_PATH')

    tg_bot = bot.Bot(token, log_file)

    start_handler = CommandHandler('start', tg_bot.start)
    message_handler = MessageHandler(Filters.text, tg_bot.text_handler)
    tg_bot.begin_work(start_handler,message_handler)


    db_con = db.DB()
    con = db_con.begin(db_file)
    cur = con.cursor()
    con.close()

main()
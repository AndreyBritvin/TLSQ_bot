from telegram.ext import CommandHandler, MessageHandler, Filters

import bot
import config




def main():
    conf = config.Read('config.json')
    token = conf.getVars('BOT_TOKEN')
    log_file = conf.getVars('LOG_FILE_NAME')
    db_file = conf.getVars('DB_FILE_PATH')

    tg_bot = bot.Bot(token, log_file,db_file)

    start_handler = CommandHandler('start', tg_bot.start)
    message_handler = MessageHandler(Filters.text, tg_bot.object_handler)
    tg_bot.begin_work(start_handler,message_handler)




main()

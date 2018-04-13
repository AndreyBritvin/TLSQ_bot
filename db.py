import sqlite3


class DB:
    def create(self, cur, arg):
        cur.execute(arg)

    def insert(self, cur, arg):
        print(arg)
        cur.execute(arg)

    def insert_user(self, con, update):
        cur = con.cursor()
        print(update.message)
        print(update.message.from_user)
        cur.execute('insert or ignore into Users (tg_userID, tg_first_name, tg_last_name) values (?, ?, ?)', (
        update.message.from_user.id, update.message.from_user.first_name, update.message.from_user.last_name))
        con.commit()
        print("Added into DB")

    def insert_answers(self, con, update, subj, correct, incorrect):
        cur = con.cursor()
        print(update.message)
        print(update.message.from_user)
        cur.execute(
            'insert into  Stat_answers(id_user, id_subj, count_correct, count_incorrect, time) values((Select id from Users where tg_userID == ?), (select id from Subj where subj_name == ?), ?, ?, DATETIME("now", "localtime"))',
            (update.message.from_user.id, subj, correct, incorrect))

        con.commit()
        print("Added into DB")

    def select(self, cur, arg):
        cur.execute(arg)

    def begin(self, path):
        con = sqlite3.connect(path, check_same_thread=False)
        return con

##select * from stat_answers where time between '2018-04-00 21:00:00'  and '2018-05-00 21:14:00'

import sqlite3
from time import localtime, strftime
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

    def get_stat(self, con, update, mode):

        day = strftime("%Y-%m-%d", localtime())
        hour = strftime("%Y-%m-%d %H", localtime())
        # print(hour)
        cur = con.cursor()
        # print(update.message)
        # print(update.message.from_user)
        cur.execute('select * from Users')
        users = cur.fetchall()
        ret = []

        if mode == 0:
            query = 'select SUM(count_correct ) as "Correct", SUM(count_incorrect) as "Incorrect" from Stat_answers where id_user==?'
        elif mode == 1:
            query = 'select SUM(count_correct ) as "Correct", SUM(count_incorrect) as "Incorrect"  from Stat_answers where id_user=? and  time between "' + day + ' 00:00:00" and "' + day + ' 23:59:00"'
        elif mode == 2:
            query = 'select SUM(count_correct ) as "Correct", SUM(count_incorrect) as "Incorrect"  from Stat_answers where id_user=? and  time between "' + hour + ':00:00" and "' + hour + ':59:00"'

        # print(query)

        for user in users:
            # print(user)
            # ret+=user[2]+" "+user[3]+":"
            # print(user[0])
            # cur.execute('select SUM(count_correct ) as "Correct", SUM(count_incorrect) as "Incorrect" from Stat_answers where id_user==?', ( user[0],))
            cur.execute(query, (user[0],))

            stats = cur.fetchall()
            # print(stats)
            if stats[0][0] != None or stats[0][1] != None:
                for stat in stats:
                    delta = stat[0] - stat[1]
                    # ret += str(stat[0]) + " " + str(stat[1]) + " -> "+str(delta)+"\n"
                    ret.append([user[2], user[3], stat[0], stat[1], delta])
                ret_sort = sorted(ret, key=lambda x: x[4], reverse=True)
                # print('Ret', ret_sort)
                # print(stats)
                ret_str = ''
                pos = 1
                for i in ret_sort:
                    ret_str += str(pos) + '. ' + i[0] + ' ' + i[1] + ':  ✅:' + str(i[2]) + ' ❌:' + str(
                        i[3]) + ' 🏆:' + str(i[4]) + '\n'
                    pos += 1
        return ret_str
        # con.commit()
        # print("Added into DB")


    def select(self, cur, arg):
        cur.execute(arg)

    def begin(self, path):
        con = sqlite3.connect(path, check_same_thread=False)
        return con

##select * from stat_answers where time between '2018-04-00 21:00:00'  and '2018-05-00 21:14:00'

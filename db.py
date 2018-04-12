import sqlite3



class DB:
    def create(self,cur,arg):
        cur.execute(arg)

    def insert(self,cur,arg):
        print(arg)
        cur.execute(arg)


    def insert_user(self,con,update):

        cur=con.cursor()
        print(update.message)
        print(update.message.from_user)
        cur.execute('insert or ignore into Users (tg_userID, tg_first_name, tg_last_name) values (?, ?, ?)', (update.message.from_user.id, update.message.from_user.first_name, update.message.from_user.last_name))
        con.commit()
        print("Added into DB")


    def select(self,cur,arg):
        cur.execute(arg)

    def begin(self,path):
        con = sqlite3.connect(path,check_same_thread=False)
        return con


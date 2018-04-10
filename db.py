import sqlite3



class DB:

    def create(self,arg):
        cur.execute(arg)

    def insert(self,arg):
        cur.execute(arg)

    def select(self,arg):
        cur.execute(arg)

    def begin(self,place):
        con = sqlite3.connect(place)
        return con


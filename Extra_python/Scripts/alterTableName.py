from cs50 import SQL

db = SQL("sqlite:///immuns.db")

dbList = []

for table in db.execute("SELECT name FROM sqlite_master WHERE type = 'table'"):
    dbList.append(table)

#for num in range(0,28):
    #dbList.pop(0)

for table in dbList:
    print(table["name"])
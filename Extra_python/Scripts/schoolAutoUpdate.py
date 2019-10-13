from cs50 import SQL

db = SQL("sqlite:///immuns.db")

dbList = []

for table in db.execute("SELECT name FROM sqlite_master WHERE type = 'table'"):
    dbList.append(table)

for num in range(0,7):
    dbList.pop(0)
#for num in range(0,8):
    #dbList.pop(1)


def checkList():
    count = 1
    for table in dbList:
        print( str(count) + str(table))
        count = count + 1

def schoolUpdate():
    for table in dbList:
        tableName = table["name"]
        theTable = db.execute("SELECT * FROM :table", table=tableName)
        for delegate in theTable:
            comm = delegate["committee"]
            if comm[-2:] == "MS":
                db.execute("UPDATE msen SET delegate_school = :school WHERE committee=:com AND country=:con", school=table["name"], com=delegate["committee"], con=delegate["country"])
                db.execute("UPDATE mssp SET delegate_school = :school WHERE committee=:com AND country=:con", school=table["name"], com=delegate["committee"], con=delegate["country"])
            elif comm[-2:] == "HS":
                db.execute("UPDATE hsen SET delegate_school = :school WHERE committee=:com AND country=:con", school=table["name"], com=delegate["committee"], con=delegate["country"])
                db.execute("UPDATE hssp SET delegate_school = :school WHERE committee=:com AND country=:con", school=table["name"], com=delegate["committee"], con=delegate["country"])
            else:
                db.execute("UPDATE hsen SET delegate_school = :school WHERE committee=:com AND country=:con", school=table["name"], com=delegate["committee"], con=delegate["country"])
            db.execute("UPDATE generalList SET delegate_school = :school WHERE committee=:com AND country=:con", school=table["name"], com=delegate["committee"] ,con=delegate["country"])

def nameUpdate():
    for table in dbList:
        tableName = table["name"]
        theTable = db.execute("SELECT * FROM :table", table=tableName)
        for delegate in theTable:
            comm = delegate["committee"]
            if comm[-2:] == "MS":
                db.execute("UPDATE msen SET delegate_name = :school WHERE committee=:com AND country=:con", school="taken", com=delegate["committee"], con=delegate["country"])
                db.execute("UPDATE mssp SET delegate_name = :school WHERE committee=:com AND country=:con", school="taken", com=delegate["committee"], con=delegate["country"])
            elif comm[-2:] == "HS":
                db.execute("UPDATE hsen SET delegate_name = :school WHERE committee=:com AND country=:con", school="taken", com=delegate["committee"], con=delegate["country"])
                db.execute("UPDATE hssp SET delegate_name = :school WHERE committee=:com AND country=:con", school="taken", com=delegate["committee"], con=delegate["country"])
            else:
                db.execute("UPDATE hsen SET delegate_name = :school WHERE committee=:com AND country=:con", school="taken", com=delegate["committee"], con=delegate["country"])
            db.execute("UPDATE generalList SET delegate_name = :school WHERE committee=:com AND country=:con", school="taken", com=delegate["committee"] ,con=delegate["country"])

checkList()
#schoolUpdate()
#nameUpdate()

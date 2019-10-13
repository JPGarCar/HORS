from cs50 import SQL

db = SQL("sqlite:///immuns.db")

global currentUser


def randomCountry(number, dataBase, school):
    stem = db.execute("SELECT * FROM :dataBase WHERE id = :ids", dataBase=dataBase, ids=number)
    for stoop in stem:
        if stoop["delegate_name"] == "":
            db.execute("INSERT INTO :tableName (committee, country, delegateName) VALUES(:committee, :country, :delNam)",
            tableName=currentUser, committee=stoop["committee"], country=stoop["country"], delNam="")
            db.execute("UPDATE :dataBase SET delegate_name = 'taken' WHERE id=:id", dataBase=dataBase, id=number)
            db.execute("UPDATE generalList SET delegate_name = 'taken' WHERE committee=:com AND country=:con", com=stoop["committee"] ,con=stoop["country"])
            db.execute("UPDATE :dataBase SET delegate_school = :school WHERE id=:id", dataBase=dataBase, school=school, id=number)
            db.execute("UPDATE generalList SET delegate_school = :school WHERE committee=:com AND country=:con", school=school, com=stoop["committee"] ,con=stoop["country"])

currentUser = "DianaRubioColegioAmericanoSaltillo"
numberList = [148,156,157]
subList = "hsen"

for number in numberList:
    randomCountry(number, subList, currentUser)
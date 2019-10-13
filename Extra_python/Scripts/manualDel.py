from cs50 import SQL

db = SQL("sqlite:///immuns.db")

global currentUser


def manualDel(number, curUser):
    stem = db.execute("SELECT * FROM :dataBase WHERE id=:ids", dataBase=curUser, ids=number)
    for stoop in stem:
        comm = stoop["committee"]
        db.execute("UPDATE generalList SET delegate_name = '' WHERE committee=:com AND country=:con", com=stoop["committee"] ,con=stoop["country"])
        db.execute("UPDATE generalList SET delegate_school = '' WHERE committee=:com AND country=:con", com=stoop["committee"] ,con=stoop["country"])
        if comm[-2:] == "MS":
            db.execute("UPDATE msen SET delegate_name = '' WHERE committee=:com AND country=:con", com=stoop["committee"] ,con=stoop["country"])
            db.execute("UPDATE mssp SET delegate_name = '' WHERE committee=:com AND country=:con", com=stoop["committee"] ,con=stoop["country"])
            db.execute("UPDATE msen SET delegate_school = '' WHERE committee=:com AND country=:con", com=stoop["committee"] ,con=stoop["country"])
            db.execute("UPDATE mssp SET delegate_school = '' WHERE committee=:com AND country=:con", com=stoop["committee"] ,con=stoop["country"])
        elif comm[-2:] == "HS":
            db.execute("UPDATE hsen SET delegate_name = '' WHERE committee=:com AND country=:con", com=stoop["committee"] ,con=stoop["country"])
            db.execute("UPDATE hssp SET delegate_name = '' WHERE committee=:com AND country=:con", com=stoop["committee"] ,con=stoop["country"])
            db.execute("UPDATE hsen SET delegate_school = '' WHERE committee=:com AND country=:con", com=stoop["committee"] ,con=stoop["country"])
            db.execute("UPDATE hssp SET delegate_school = '' WHERE committee=:com AND country=:con", com=stoop["committee"] ,con=stoop["country"])
        else:
            db.execute("UPDATE hsen SET delegate_name = '' WHERE committee=:com AND country=:con", com=stoop["committee"] ,con=stoop["country"])
            db.execute("UPDATE hsen SET delegate_school = '' WHERE committee=:com AND country=:con", com=stoop["committee"] ,con=stoop["country"])
        db.execute("DELETE FROM :dataBase WHERE id=:ids", dataBase=curUser, ids=number)

currentUser = "GuillermoLopezIndividualGuillermo"
numberList = [1]
for number in numberList:
    manualDel(number, currentUser)

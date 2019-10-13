from cs50 import SQL


db = SQL("sqlite:///immuns.db")

def idArange(user):
    countries = db.execute("SELECT * FROM :user", user=user)
    x = 1
    for country in countries:
        db.execute("UPDATE :user SET id=:idx WHERE id=:firstID", user=user, idx=x, firstID=country["id"])
        x = x + 1

#idArange("msen")
#idArange("mssp")
#idArange("hsen")
#idArange("hssp")

#idArange("generalList")

#idArange("Marissa Aguilar_ASFM")
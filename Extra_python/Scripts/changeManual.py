from cs50 import SQL
from IDArange import idArange

db = SQL("sqlite:///immuns.db")


def changeMan(dataBase, user):
    for pair in changeList:
        db.execute("UPDATE :dataBase SET delegate_name = '' WHERE committee=:com AND country=:con", dataBase=dataBase, com=pair[0], con=pair[1])
        db.execute("UPDATE generalList SET delegate_name = '' WHERE committee=:com AND country=:con", com=pair[0], con=pair[1])
        db.execute("DELETE FROM :user WHERE committee=:com AND country=:con", user=user, com=pair[0], con=pair[1])
    idArange(user)


changeList = [("European Council MS", "Austria"), ("World Health Organization MS", "Mexico"), ("Organization of American States MS", "Brazil"),
                ("Security Council MS", "United Kingdom"), ("European Council MS", "Croatia"), ("European Council MS", "United Kingdom"),
                ("World Health Organization MS", "Saudi Arabia"), ("ECOSOC MS", "Sweden"), ("ECOSOC MS", "Finland"), ("World Health Organization MS", "Afghanistan"),
                ("ECOSOC MS", "Japan"), ("Security Council MS", "Syria")]
changeMan("msen", "Christian Mustouh_Liceo de Hombres")

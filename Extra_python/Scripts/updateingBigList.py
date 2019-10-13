from cs50 import SQL


db = SQL("sqlite:///immuns.db")

committeesEnHS = ["ICC"]
countEnHS = ["8 Defense Attorney", "8 Prosecutor"]

listt = "hsen"
typeOfCom = "HS EN"

for i in range(0,len(committeesEnHS)):
    for y in range(0,len(countEnHS)):
        x = y + 23
        db.execute("INSERT INTO generalList (committee, country, country_id, delegate_name, delegate_school, typeOfCom) VALUES(:comm, :country, :countryID, :delnam, :delschool, :typeOfCom)",
        comm=committeesEnHS[i], country=countEnHS[y], countryID=x, delnam="", delschool="", typeOfCom=typeOfCom)
        db.execute("INSERT INTO :listt (committee, country, country_id, delegate_name, delegate_school, typeOfCom) VALUES(:comm, :country, :countryID, :delnam, :delschool, :typeOfCom)",
        listt=listt, comm=committeesEnHS[i], country=countEnHS[y], countryID=x, delnam="", delschool="", typeOfCom=typeOfCom)
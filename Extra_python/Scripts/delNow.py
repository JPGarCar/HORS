from cs50 import SQL

db = SQL("sqlite:///immuns.db")

db.execute("UPDATE msen SET delegate_name = '' WHERE committee = 'General Assembly MS 2' ")
db.execute("UPDATE msen SET delegate_school = '' WHERE committee = 'General Assembly MS 2' ")

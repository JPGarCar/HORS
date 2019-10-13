from cs50 import SQL

db = SQL("sqlite:///immuns.db")


def maxNumInDBUser(user):
    x = 0
    spots = db.execute("SELECT * FROM :user WHERE delegate_name = '' ", user=user)
    for spot in spots:
        x = x + 1
    return x

msen = maxNumInDBUser("msen")
mssp = maxNumInDBUser("mssp")
hsen = maxNumInDBUser("hsen")
hssp = maxNumInDBUser("hssp")

print("msen " + str(msen))
print("mssp " + str(mssp))
print("hsen " + str(hsen))
print("hssp " + str(hssp))
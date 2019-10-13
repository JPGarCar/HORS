from helpers import *
from assignment import *
from delegate import *


# flask for web service
from flask import Flask, redirect, render_template, request, url_for, session, flash, send_file
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# assigns variable 'db' to the SQL database immuns.db
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///immuns.db"
app.config["SQLALCHEMY_ECHO"] = True

db = SQLAlchemy(app)

### replaceSpecial (String -> String)
### strips a string from special characters
def replaceSpecial(string):
    string = string.replace(" ", "")
    string = string.replace("_", "")
    string = string.replace("-", "")
    string = string.replace("'", "")
    string = string.replace(".", "")
    return string


class Teacher(db.Model):

    __tablename__ = "teachers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    email = db.Column(db.Text)
    school = db.Column(db.Text)
    password = db.Column(db.Text)
    confirmationCode = db.Column(db.Text)
    delegates = db.relationship("Delegate", backref="teacher")


    def __init__(self, name, email, password, school, code):
        self.name = name
        self.email = email
        self.password = password
        self.school = school
        self.confirmationCode = code
        self.numOfStudents = getSpecial(code)
        self.sessionUser = makeUser()

    # def createClassroom(self):
    #     classroom = db.Table(self.dataBaseName,
    #     db.Column("id", db.Integer, primary_key=True),
    #     db.Column("committee", db.Text),
    #     db.Column("country", db.Text),
    #     db.Column("delegateName", db.Text),
    #     db.Column("room", db.Text),
    #     db.Column("important", db.Text))
    #     db.create_all()

    ### MaxNumInUser (String -> Number)
    def maxNumInUser(self):
        num = 0
        # grabs all assignments of user
        assignments = self.delegates
        # iterates over all the assignments in the table adding one to the variable num
        for assignment in assignments:
            num = num + 1
        return num

    ### returnUserPageOld (Void -> templateRendered)
    ### returns the rendered template userPageOld.html with corresponding data from current user's table
    def returnUserPageOld(self):
        user = self.delegates
        return render_template("userPageOld.html", users=user)


    ### makeUser (String String -> String)
    ### produces unique user id from its name and school without any special characters
    def makeUser(self):
        return replaceSpecial(self.name) + replaceSpecial(self.school)

    ### recheck the number of students available
    def checkSpecialCode(self):
        self.numOfStudents = getSpecial(self.confirmationCode)

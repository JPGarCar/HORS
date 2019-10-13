from helpers import *
from delegate import *
from teacher import *

# flask for web service
from flask import Flask, redirect, render_template, request, url_for, session, flash, send_file
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# assigns variable 'db' to the SQL database immuns.db
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///immuns.db"
app.config["SQLALCHEMY_ECHO"] = True

db = SQLAlchemy(app)

class Assignment(db.Model):

    __tablename__ = "generalList"
    id = db.Column(db.Integer, primary_key=True)
    committee = db.Column(db.Text)
    country = db.Column(db.Text)
    country_id = db.Column(db.Integer)
    #delegate_name = db.Column(db.Text)
    #delegate_school = db.Column(db.Text)
    typeOfCom = db.Column(db.Text)
    room = db.Column(db.Text)
    important = db.Column(db.Text)
    delegate = db.relationship("Delegate", backref="assignment", uselist=False)

    def __init__(self, committee, country, country_id, typeOfCom, room, important):
        self.committee = committee
        self.country = country
        self.country_id = country_id
        # self.delegate_name = delegate_name
        # self.delegate_school = delegate_school
        self.typeOfCom = typeOfCom
        self.room = room
        self.important = important





### randomCountry (Number String String Teacher -> Void)
### Randomly assigns assignments to current user's table as specified
def randomCountry(number, typeOfCom, Important, teacher):
    # used to have different iterations of the random function to be more random
    ranNum = 1
    numAssign = number
    # iterates until all the assignments pending are assigned
    while numAssign > 0:
        # number of countries as specified in generalList
        maxNumInDBNow = maxTypeInGen(typeOfCom, Important)
        # assigns a random number to "codeID", -1 because list starts at 0
        for i in range(0,ranNum):
            codeID = randint(1, maxNumInDBNow) - 1
        # all assignments of type of committee and importance on generalList
        assignments = Assignment.querry.filter(Assignment.delegate == None and Assignment.typeOfCom == typeOfCom and Assignment.important == Important).all()
        # assignment from assignemnts in index "codeID"
        assignment = assignments[codeID]
        # assignment assigned to current user and its table updated
        #if not assignment["room"] == "":
        delegate = Delegate(" ", assignment, teacher)
        db.session.add(delegate)
        db.session.commit()

            #db.execute("INSERT INTO :tableName (committee, country, delegateName, room, important) VALUES(:committee, :country, :delNam, :room, :imp)",
            #tableName=session["currentUser"], committee=assignment["committee"], country=assignment["country"], delNam="", room=assignment["room"], imp=assignment["Important"])
        # else:
        #     delegate = Delegate(teacher.dataBaseName, assignment.committee, assignment.country, "", "", assignment.important)
        #     db.session.add(delegate)
        #     db.session.commit()

            #db.execute("INSERT INTO :tableName (committee, country, delegateName, room, important) VALUES(:committee, :country, :delNam, :room, :imp)",
            #tableName=session["currentUser"], committee=assignment["committee"], country=assignment["country"], delNam="", room="", imp=assignment["Important"])

        # updates the generalList
        # assignment.delegate_name = "taken"
        # assignment.delegate_school = teacher.school
        # db.session.commit()

        #db.execute("UPDATE generalList SET delegate_name='taken', delegate_school =:school WHERE committee=:com AND country=:con",
        #school=session["currentUser"], com=assignment["committee"] ,con=assignment["country"])

        # reduces number of pedning assignments by one
        numAssign = numAssign - 1
        # increase the numer of iterations of random
        ranNum = ranNum + 1

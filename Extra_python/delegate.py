from helpers import *
from assignment import *
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

class Delegate(db.Model):

    __tablename__ = "delegates"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    assignment_id = db.Column(db.Integer, db.ForeignKey("assignment.id"))
    teacher_id = db.Column(db.Integer, db.ForeignKey("teacher.id"))

    #committee = db.Column(db.Text)
    #country = db.Column(db.Text)
    #room = db.Column(db.Text)
    #important = db.Column(db.Text)

    def __init__(self, name, assignment, teacher):
        self.name = name
        self.assignment_id = assignment
        self.teacher_id = teacher



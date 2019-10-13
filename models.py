# flask for web service
from flask import Flask, redirect, render_template, request, url_for, session, flash, send_file
from flask_sqlalchemy import SQLAlchemy
import helpers
from typeOfCommittee import TypeOfCom
from Important import Important
from advanced import Advanced
from application import db
from passlib.apps import custom_app_context as pwd_context


class Teacher(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    email = db.Column(db.Text)
    school = db.Column(db.Text)
    password = db.Column(db.Text)
    confirmationCode = db.Column(db.Text)
    delegates = db.relationship('Delegate', backref='teacher', lazy=True)

    ### chagnePassword() (String -> void)
    ### change the teacher's password, hashed and all
    def changePassword(self, newPassword):
        self.password = pwd_context.hash(newPassword);



    ### canAddDelegate() ( -> bool)
    ### return true if teacher has space for more delegates, else false
    def canAddDelegate(self):
        if self.getNumOfStudents() < self.getNumOfMaxStudents():
            return True
        else:
            return False

    ### getNumOfStudents (String -> Number)
    ### return number of students in teacher
    def getNumOfStudents(self):
        num = 0
        # grabs all assignments of user
        assignments = self.delegates
        # iterates over all the assignments in the table adding one to the variable num
        for assignment in assignments:
            num = num + 1
        return num

    ### returnUserPageOld (Void -> templateRendered)
    ### returns the rendered template user_oldTeacherPage.html with corresponding data from current user's table
    def returnUserPageOld(self):
        delegates = self.delegates
        return render_template("user_oldTeacherPage.html", delegates=delegates)


    ### makeUser (String String -> String)
    ### produces unique user id from its name and school without any special characters
    def getTeacherSession(self):
        return helpers.replaceSpecial(self.name) + helpers.replaceSpecial(self.school)

    ### recheck the number of students available
    def getNumOfMaxStudents(self):
        return helpers.getSpecial(self.confirmationCode)


    def __init__(self, name, email, password, school, code):
        self.name = name
        self.email = email
        self.password = password
        self.school = school
        self.confirmationCode = code
        # Flask-Login stuff
        self.is_authenticaded = False
        self.is_active = True
        self.is_anonymous = False

    ###### Flask-Login stuff #######
    def get_id(self):
        return chr(Teacher.query.filter(Teacher.name == self.name, Teacher.email == self.email).first().id)




class Assignment(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.Text)
    country_id = db.Column(db.Integer)
    important = db.Column(db.Text)
    delegate = db.relationship('Delegate', backref='assignment', uselist=False)
    committee_id = db.Column(db.Integer, db.ForeignKey("committee.id"), nullable=False)

    def __init__(self, committeeID, country, country_id, important : Important):
        self.country = country
        self.country_id = country_id
        self.important = important
        self.committee_id = committeeID


class Delegate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)

    def __init__(self, name, assignment, teacher):
        self.name = name
        self.assignment_id = assignment
        self.teacher_id = teacher


class Committee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    typeOfCom = db.Column(db.Text)
    room = db.Column(db.Text)
    advanced = db.Column(db.Text)
    assignments = db.relationship("Assignment", backref="committee")

    def __init__(self, name, typeOfCom : TypeOfCom, room, advanced):
        self.name = name
        self.typeOfCom = typeOfCom
        self.room = room
        self.advanced = advanced

    ### return number of assignments in this committee
    def numOfAssignments(self):
        num = 0
        for assignment in self.assignments:
            if assignment.important == Important.NO.value:
                num = num + 1
        return num

    ### return number of important assignments in this committee
    def numOfImportantAssignments(self):
        num = 0
        for assignment in self.assignments:
            if assignment.important == Important.YES.value:
                num = num + 1
        return num

    ### return number of assignments with a delegate in this committee
    def numOfDelegates(self):
        num = 0
        for assignment in self.assignments:
            if assignment.important == Important.NO.value and assignment.delegate is not None:
                num = num + 1
        return num

    ### return number of important assignments with a delegate in this committee
    def numOfImportantDelegates(self):
        num = 0
        for assignment in self.assignments:
            if assignment.important == Important.YES.value and assignment.delegate is not None:
                num = num + 1
        return num

    ### return true if there are more assignments available than delegates in the committee by half
    def codeYellow(self, isImportant):
        print("inside code yellow")
        if isImportant:
            if self.numOfImportantAssignments() - self.numOfImportantDelegates() >= self.numOfImportantAssignments() / 2:
                return True
            else:
                return False
        else:
            if self.numOfAssignments() - self.numOfDelegates() >= self.numOfAssignments() / 2:
                print("inside true for code yellow")
                return True
            else:
                return False

    ### return true if there are more assignments available than delegates in the committe by two thirds
    def codeRed(self, isImportant):
        print("inside code red")
        if isImportant:
            if self.numOfImportantAssignments() - self.numOfImportantDelegates() >= self.numOfImportantAssignments() * 0.6:
                return True
            else:
                return False
        else:
            if self.numOfAssignments() - self.numOfDelegates() >= self.numOfAssignments() * 0.6:
                print("inside true for code red")
                return True
            else:
                return False

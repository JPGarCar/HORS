#!/usr/bin/python

## Things to improve:
# - return redirect(url_for(""))
# - database INDEX ids to be faster at searching
# DONE - SELECT * FROM users JOIN zipcodes ON users.zipcode = zipcodes.id 59:00
# DONE - use foreign keys to not having reocurring data in a table, the data is in a different table and its id is in the original table
# DONE - use of classes ORM, in minute 1hr 30 min week 9 using SQLAlchemy
# DONE - hashed values for passwords
# - use javascript code or other peoples code to make sign up better as well as sing in and old user page
# - javascript warning for special functions
# - javascript for the admin page search filters
# - javascript edit teacher info warnings
# - javascript generate special code for teachers
# - use localStorage in javascript for add committee country etc, pages so no need to use session in python
# DONE - Get GITHUB working here
# - use ajax to get new admin data every so time or after click of button

# DONE - add num of available assignments on user_newTeacherPage

## javascript is not an alternative to checks and validation ##
## Thus you need to do it in both python and javascript ##

## mix javascript with bootstrap ##


# import multiple packeges
# flask for web service
from flask import Flask, redirect, render_template, request, url_for, session, flash, send_file
# flask-login
# from flask_login import LoginManager, login_required
# for the random assignment generator
import random
# basic math needed
import math
# for sentry issue resolver
# from raven.contrib.flask import Sentry
# for pasword hashing
from passlib.apps import custom_app_context as pwd_context
# for the random string in the special code
import string

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_

# defines variable 'app' to the flask
app = Flask(__name__)
app.secret_key = "b/xc7&xc9qx00f#xc2!xc3?xd1¡xb1U¿xbeo{xb0]xc6*xc2"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///immuns.db"
app.config["SQLALCHEMY_ECHO"] = False

db = SQLAlchemy(app)

import helpers
import model_helpers as modHelpers
from typeOfCommittee import TypeOfCom
from Important import Important
from advanced import Advanced
from models import Teacher, Committee, Assignment, Delegate

# if there is any session data on the users computer then clear it
if session:
    session.clear()
    session.pop('_flashes', None)


# login_manager = LoginManager()
# login_manager.init_app(app)

# assing sentry its code to connect to account
# sentry = Sentry(app, dsn='https://effbb4c86ee440eebbb9f8d2de12cd6f:e32dca8980a440e699031e80789d3a06@sentry.io/1238266')

##### no globals are used, instead the session module from flask is used, it uses cookies so that is way better.

###############################################################################################################################################################
###############################################################################################################################################################
#######################################################  Routes for main Page   ###############################################################################
###############################################################################################################################################################
###############################################################################################################################################################

# @login_manager.user_loader
# def load_user(user_id):
#     return Teacher.query.get(user_id)


### / (GET POST -> templateRendered)
### main route to the sign in page,
### GET: returns the registration template
### POST: signs in a teacher if email and password match or sign admin
@app.route("/", methods=["GET", "POST"])
def user_registration():
    ### GET
    if request.method == "GET":
        return render_template("user_registration.html")

    ### POST
    elif request.method == "POST":
        # restart seesion
        session["currentTeacher"] = None

        ### Check In Admin ###
        if request.form["signInEmail"] == "admin@gmail.com" and pwd_context.verify(request.form["signInPassword"],
                                                                                   pwd_context.hash("adminPassword")):
            session["adminIn"] = True
            return modHelpers.returnAdminPage("", None)

        ### Sign In Teacher ###
        # grabs the Teacher from table teacher with the inputed email
        teachers = Teacher.query.filter(Teacher.email == request.form["signInEmail"]).all()

        # loops over the teacher, if there is no teacher it will not enter the loop and return the same page with flash
        for teacher in teachers:
            # check the hashed password
            if pwd_context.verify(request.form["signInPassword"], teacher.password):
                if teacher.name != "":
                    # assign session variables
                    session["currentTeacher"] = teacher.getTeacherSession()
                    session["currentUserId"] = teacher.id
                    # log in user for Flask-Login
                    # login_user(teacher)
                    # variable "numDelOfTeacher" has the number from sepcial code
                    numDelOfTeacher = teacher.getNumOfMaxStudents()
                    # assign assignments in current teacher
                    numNow = teacher.getNumOfStudents()
                    # if the teacher has same assignments as his code permits then go to teacher page old
                    if numNow == numDelOfTeacher:
                        return teacher.returnUserPageOld()
                    # else go get more delgates
                    else:
                        # assigns 'numRem' the number of delegates remainging
                        numRem = numDelOfTeacher - numNow
                        return modHelpers.renderNewTeacherPage(teacher, numRem)
            flash(
                "You have entered an incorrect password, please try again. If the problem persists, call your HOSPITALITY member for asistance.")
            return render_template("user_registration.html")
        flash(
            "You have entered an incorrect email, please try again. If the problem persists, call your HOSPITALITY member for asistance.")
        return render_template("user_registration.html")


### /user_signUp (GET POST -> templateRendered)
### user_signUp reoute to sign up a new teacher
### GET: returns the user_signUp template
### POST: checks if all fields are filled and correct and makes the new teacher
@app.route("/user_signUp", methods=["POST", "GET"])
def user_signUp():
    ### GET
    if request.method == "GET":
        return render_template("user_signUp.html")

    ### POST
    elif request.method == "POST":
        ### Validate confirmation code ###
        # checks confirmation code validity using getSpecial() if not vaild return same page with flash error
        if helpers.getSpecial(request.form["confirmationCode"]) == None:
            flash("You have entered an incorrect confirmation code.")
            flash("Please enter a valid confirmation code, if the problem persists, contact your HOSPITALITY member.")
            return render_template("user_signUp.html")

        else:
            ### Check Email Availability ###
            # checks if email is already in table
            email = Teacher.query.filter_by(email=request.form["email"]).first()

            # if email inputed is already in use return same page with flash error
            if email is not None:
                flash(
                    "The email you have entered is already in use. If you do not remember your password please contact your HOSPITALITY member.")
                return render_template("user_signUp.html")

            ### Check Passwords Match ###
            if not request.form["password"] == request.form["password_second"]:
                flash("The passwords that you have entered do not match, please try again.")
                return render_template("user_signUp.html")

            ### Adding teacher ###
            teacher = Teacher(request.form["personName"], request.form["email"],
                              pwd_context.hash(request.form["password"]), request.form["school"],
                              request.form["confirmationCode"])
            db.session.add(teacher)
            db.session.commit()
            # return template user_signUpSuccess
            return render_template("user_signUpSuccess.html")


### /user_signUpSuccess (GET POST -> templateRendered)
### user_signUpSuccess route, simple node
### GET: returns the user_signUpSuccess template
### POST: returnes the teacher to registration template
@app.route("/user_signUpSuccess", methods=["POST", "GET"])
def user_signUpSuccess():
    ### POST
    if request.method == "POST":
        return render_template("user_registration.html")

    ### GET
    else:
        return render_template("user_signUpSuccess.html")


# Helper Function
# USAGE: Will assign a country to a teacher or return a message error
def assign_helper(looking_for, type_of_committee, is_important, is_advanced, teacher):
    if looking_for != 0:
        available = modHelpers.stillAvailable(typeOfCom=type_of_committee, important=is_important, advanced=is_advanced)
        if available >= looking_for:
            modHelpers.randomCountry(looking_for, type_of_committee, is_important, teacher, is_advanced)
            return None
        elif available != 0:
            # assign the available assignments
            modHelpers.randomCountry(available, type_of_committee, is_important, teacher, is_advanced)
            return "We were only able to assign " + str(available) + " " + TypeOfCom.to_string(type_of_committee) + \
                   (' Important' if is_important == Important.YES.value else '') + \
                   (' Advanced' if is_advanced == Advanced.YES.value else '') + " assignments. The remaining " + \
                   str(looking_for - available) + " assignments are still at your disposal."
        else:
            return "There are not enough " + TypeOfCom.to_string(type_of_committee) + \
                   (' Important' if is_important == Important.YES.value else '') + \
                   (' Advanced' if is_advanced == Advanced.YES.value else '') + " assignments, there are only " + \
                   str(available) + " available. You asked for: " + str(looking_for)


# /user_newTeacherPage (POST -> templateRendered)
# user_newTeacherPage route, for the new teachers that need to select the number of assignments
# POST: let teachers select number of assignments limited to their code limit
@app.route("/user_newTeacherPage", methods=["POST"])
# @login_required
def user_newTeacherPage():
    if request.method == "POST" and not session["currentTeacher"] is None:
        # grab teacher that is signed in
        teacher = Teacher.query.get(session["currentUserId"])

        # assigns the number of delegates requested in each variable
        MSE = helpers.assignToInt(request.form["MSE"])
        MSS = helpers.assignToInt(request.form["MSS"])
        HSE = helpers.assignToInt(request.form["HSE"])
        HSS = helpers.assignToInt(request.form["HSS"])

        HSEI = helpers.assignToInt(request.form["HSEI"])
        MSEI = helpers.assignToInt(request.form["MSEI"])
        MSSI = helpers.assignToInt(request.form["MSSI"])
        HSSI = helpers.assignToInt(request.form["HSSI"])

        MSEA = helpers.assignToInt(request.form["MSEA"])
        MSSA = helpers.assignToInt(request.form["MSSA"])
        HSEA = helpers.assignToInt(request.form["HSEA"])
        HSSA = helpers.assignToInt(request.form["HSSA"])

        MSEAI = helpers.assignToInt(request.form["MSEAI"])
        MSSAI = helpers.assignToInt(request.form["MSSAI"])
        HSEAI = helpers.assignToInt(request.form["HSEAI"])
        HSSAI = helpers.assignToInt(request.form["HSSAI"])

        G6EN = helpers.assignToInt(request.form["G6EN"])

        # assings 'number' number of requested delegates plus delegates already in the teacher's table
        number = MSE + MSS + HSE + HSS + MSEI + HSEI + MSSI + HSSI + MSEA + MSSA + \
                 HSEA + HSSA + G6EN + MSEAI + MSSAI + HSEAI + HSSAI + teacher.getNumOfStudents()

        # grabs the teacher's number of students
        target = teacher.getNumOfMaxStudents()

        # goes over all the requested delegates checking there are requested of such type
        # and there are remaining in generalList
        # if true, then calls randomCountry() to assign the assignment
        if number == target:
            # list for possible error messages
            error_list = []

            # if there are not enough assignments available adds an error to the list and
            # does not add any assignments of the type

            # regular committees
            error_list.append(assign_helper(looking_for=MSE, type_of_committee=TypeOfCom.MSEN.value,
                                            is_important=Important.NO.value,
                                            is_advanced=Advanced.NO.value, teacher=teacher))
            error_list.append(assign_helper(looking_for=MSS, type_of_committee=TypeOfCom.MSSP.value,
                                            is_important=Important.NO.value,
                                            is_advanced=Advanced.NO.value, teacher=teacher))
            error_list.append(assign_helper(looking_for=HSE, type_of_committee=TypeOfCom.HSEN.value,
                                            is_important=Important.NO.value,
                                            is_advanced=Advanced.NO.value, teacher=teacher))
            error_list.append(assign_helper(looking_for=HSS, type_of_committee=TypeOfCom.HSSP.value,
                                            is_important=Important.NO.value,
                                            is_advanced=Advanced.NO.value, teacher=teacher))

            # important assignments in regular committees
            error_list.append(assign_helper(looking_for=MSEI, type_of_committee=TypeOfCom.MSEN.value,
                                            is_important=Important.YES.value,
                                            is_advanced=Advanced.NO.value, teacher=teacher))
            error_list.append(assign_helper(looking_for=MSSI, type_of_committee=TypeOfCom.MSSP.value,
                                            is_important=Important.YES.value,
                                            is_advanced=Advanced.NO.value, teacher=teacher))
            error_list.append(assign_helper(looking_for=HSEI, type_of_committee=TypeOfCom.HSEN.value,
                                            is_important=Important.YES.value,
                                            is_advanced=Advanced.NO.value, teacher=teacher))
            error_list.append(assign_helper(looking_for=HSSI, type_of_committee=TypeOfCom.HSSP.value,
                                            is_important=Important.YES.value,
                                            is_advanced=Advanced.NO.value, teacher=teacher))

            # advanced committees
            error_list.append(assign_helper(looking_for=MSEA, type_of_committee=TypeOfCom.MSEN.value,
                                            is_important=Important.NO.value,
                                            is_advanced=Advanced.YES.value, teacher=teacher))
            error_list.append(assign_helper(looking_for=MSSA, type_of_committee=TypeOfCom.MSSP.value,
                                            is_important=Important.NO.value,
                                            is_advanced=Advanced.YES.value, teacher=teacher))
            error_list.append(assign_helper(looking_for=HSEA, type_of_committee=TypeOfCom.HSEN.value,
                                            is_important=Important.NO.value,
                                            is_advanced=Advanced.YES.value, teacher=teacher))
            error_list.append(assign_helper(looking_for=HSSA, type_of_committee=TypeOfCom.HSSP.value,
                                            is_important=Important.NO.value,
                                            is_advanced=Advanced.YES.value, teacher=teacher))

            # important assignments in advanced committees
            error_list.append(assign_helper(looking_for=MSEAI, type_of_committee=TypeOfCom.MSEN.value,
                                            is_important=Important.YES.value,
                                            is_advanced=Advanced.YES.value, teacher=teacher))
            error_list.append(assign_helper(looking_for=MSSAI, type_of_committee=TypeOfCom.MSSP.value,
                                            is_important=Important.YES.value,
                                            is_advanced=Advanced.YES.value, teacher=teacher))
            error_list.append(assign_helper(looking_for=HSEAI, type_of_committee=TypeOfCom.HSEN.value,
                                            is_important=Important.YES.value,
                                            is_advanced=Advanced.YES.value, teacher=teacher))
            error_list.append(assign_helper(looking_for=HSSAI, type_of_committee=TypeOfCom.HSSP.value,
                                            is_important=Important.YES.value,
                                            is_advanced=Advanced.YES.value, teacher=teacher))

            # 6th grade assignments
            error_list.append(assign_helper(looking_for=G6EN, type_of_committee=TypeOfCom.G6EN.value,
                                            is_important=Important.NO.value,
                                            is_advanced=Advanced.NO.value, teacher=teacher))

            # check error list is not empty, then return same page with flash errors, else return user_oldTeacherPage()
            # will filter the list for any None values
            error_list = list(filter(None, error_list))
            if len(error_list) > 0:
                flash("Some assignments have been added but we have some issues:")
                for error in range(0, len(error_list)):
                    flash(error_list[error])
                num_rem = target - teacher.getNumOfStudents()
                return modHelpers.renderNewTeacherPage(session["currentTeacher"], num_rem)
            else:
                return teacher.returnUserPageOld()
        else:
            # if incorrect number of assignments, return same page with number of assignments remeaining
            num_rem = target - teacher.getNumOfStudents()
            flash(
                "You have entered an incorrect number of assignments, please try again you have {} delegates to assign.".format(
                    num_rem))
            return modHelpers.renderNewTeacherPage(session["currentTeacher"], num_rem)

    flash("An error was encountered please log in again. If the error persists call your HOSPITALITY member.")
    return render_template("user_registration.html")


### /goTo (POST -> templateRendered)
### goTo route, takes to the singUp template used after the teacher registers only has POST for button click
@app.route("/goTo", methods=["POST"])
def goTo():
    ### POST
    return render_template("user_signUp.html")


### /userSettingsPage (POST -> templateRendered)
### page where teachers can edit their info
@app.route("/userSettingsPage", methods=["POST", "GET"])
def userSettingsPage():
    if request.method == "POST" and not session["currentTeacher"] is None:
        teacher_id = request.form["submit"]
        teacher = Teacher.query.get(teacher_id)
        if request.form["password"] != "":
            teacher.changePassword(request.form["password"])
        teacher.email = request.form["email"]
        teacher.name = request.form["name"]
        teacher.school = request.form["school"]
        flash("Changes have been made successfully!")
        db.session.commit()
        return render_template("user_settingsPage.html", teacher=teacher)

    elif request.method == "GET" and not session["currentTeacher"] is None:
        teacher = Teacher.query.get(session["currentUserId"])
        return render_template("user_settingsPage.html", teacher=teacher)


### /user_oldTeacherPage (POST GET -> templateRendered)
### user page old route
### POST: name of student is updated if anything in input bar, else name stays as taken
### GET: the program returns the user_oldTeacherPage()
@app.route("/user_oldTeacherPage", methods=["POST", "GET"])
# @login_required
def user_oldTeacherPage():
    ### POST
    if request.method == "POST" and not session["currentTeacher"] is None:
        # grab teacher that is logged in
        teacher = Teacher.query.get(session["currentUserId"])

        # gets all assginments from table of the current teacher in session
        delegates = teacher.delegates
        for delegate in delegates:
            # asigns y the assignment ID in the table that corresponds to the ID of the input bar
            nameID = "N_" + str(delegate.id)
            # uses the nameID of the deleagte to get name in html page input bar
            delName = request.form[nameID]
            # checks if the input bar has a valid name input or not
            if delName == "" or delName == " ":
                # name is put to blank if the delegate name is blank only
                delegate.name = " "
            else:
                # name is updated to the input string from the bar in teacher's table
                delegate.name = delName
            # use the id to get grade drop down
            gradeID = "G_" + str(delegate.id)
            delGrade = request.form[gradeID]
            if delGrade != "":
                delegate.grade = delGrade

        db.session.commit()
        # return the user page old with returnUserPageOld()
        flash("The names have been changed as requested.")
        return teacher.returnUserPageOld()

    ### GET
    elif request.method == "GET" and not session["currentTeacher"] is None:
        teacher = Teacher.query.get(session["currentUserId"])
        return teacher.returnUserPageOld()


### /userDownload (POST -> templateRendered)
### return printable html file with all the teacher's info
### POST: render user_printAssignments.html with teacher's info
@app.route("/userDownload", methods=["POST"])
# @login_required
def userDownload():
    ### POST
    if request.method == "POST" and not session["currentTeacher"] is None:
        # grab teacher logged in
        teacher = Teacher.query.get(session["currentUserId"])
        # grabs the school name of teacher
        school = teacher.school
        # grabs all delegates of the teacher
        delegates = teacher.delegates
        # return the html file with the data
        return render_template("user_printAssignments.html", school=school, delegates=delegates)


### /logOut (POST -> templateRendred)
### similiar to signOut but different unknown use
### POST: delete all session info and flashes, return user_registration.html
@app.route("/logOut", methods=["POST"])
##@login_required
def logOut():
    if session:
        session.clear()
        session.pop('_flashes', None)
    # logout_user()
    return render_template("user_registration.html")


###############################################################################################################################################################
###############################################################################################################################################################
#####################################################       Admin Pages     ###################################################################################
###############################################################################################################################################################
###############################################################################################################################################################


### /adminOne (POST GET -> templateRendered)
### admin console route
### POST: check the button status and act accordingly
### GET: return retrunAdminPage() for all info
@app.route("/adminOne", methods=["POST", "GET"])
def adminOne():
    ### GET
    if request.method == "GET" and session["adminIn"] == True:
        return modHelpers.returnAdminPage("", None)
    ### POST
    if request.method == "POST" and session["adminIn"] == True:
        app.jinja_env.globals.update(numOfAssignments=Committee.numOfAssignments)
        app.jinja_env.globals.update(numOfImportantAssignments=Committee.numOfImportantAssignments)
        app.jinja_env.globals.update(numOfDelegates=Committee.numOfDelegates)
        app.jinja_env.globals.update(numOfImportantDelegates=Committee.numOfImportantDelegates)
        app.jinja_env.globals.update(codeYellow=Committee.codeYellow)
        app.jinja_env.globals.update(codeRed=Committee.codeRed)

        #
        session["admingCurrentTable"] = ""
        # value tells what button was clicked
        value = request.form["Button"]

        ### General Filter Buttons ###
        if value == "MS":
            assignments = db.session.query(Assignment).join(Committee).filter(
                or_(Committee.typeOfCom == TypeOfCom.MSEN.value, Committee.typeOfCom == TypeOfCom.MSSP.value)).all()
            session["admingCurrentTable"] = " AND (typeOfCom = 'MS EN' OR typeOfCom = 'MS SP')"
            genFilter = "MS"
            return modHelpers.returnAdminPage(assignments, genFilter)
        elif value == "HS":
            assignments = db.session.query(Assignment).join(Committee).filter(
                or_(Committee.typeOfCom == TypeOfCom.HSEN.value, Committee.typeOfCom == TypeOfCom.HSSP.value)).all()
            session["admingCurrentTable"] = " AND (typeOfCom = 'HS EN' OR typeOfCom = 'HS SP')"
            genFilter = "HS"
            return modHelpers.returnAdminPage(assignments, genFilter)
        elif value == "ALL":
            session["admingCurrentTable"] = ""
            return modHelpers.returnAdminPage("", None)
        elif value == "English":
            assignments = db.session.query(Assignment).join(Committee).filter(
                or_(Committee.typeOfCom == TypeOfCom.HSEN.value, Committee.typeOfCom == TypeOfCom.MSEN.value)).all()
            session["admingCurrentTable"] = " AND (typeOfCom = 'HS EN' OR typeOfCom = 'MS EN')"
            genFilter = "English"
            return modHelpers.returnAdminPage(assignments, genFilter)
        elif value == "Spanish":
            assignments = db.session.query(Assignment).join(Committee).filter(
                or_(Committee.typeOfCom == TypeOfCom.HSSP.value, Committee.typeOfCom == TypeOfCom.MSSP.value)).all()
            session["admingCurrentTable"] = " AND (typeOfCom = 'HS SP' OR typeOfCom = 'MS SP')"
            genFilter = "Spanish"
            return modHelpers.returnAdminPage(assignments, genFilter)
        elif value == "HSEN":
            assignments = db.session.query(Assignment).join(Committee).filter(
                Committee.typeOfCom == TypeOfCom.HSEN.value).all()
            session["admingCurrentTable"] = " AND typeOfCom = 'HS EN'"
            genFilter = TypeOfCom.HSEN.value
            return modHelpers.returnAdminPage(assignments, genFilter)
        elif value == "HSSP":
            assignments = db.session.query(Assignment).join(Committee).filter(
                Committee.typeOfCom == TypeOfCom.HSSP.value).all()
            session["admingCurrentTable"] = " AND typeOfCom = 'HS SP'"
            genFilter = TypeOfCom.HSSP.value
            return modHelpers.returnAdminPage(assignments, genFilter)
        elif value == "MSEN":
            assignments = db.session.query(Assignment).join(Committee).filter(
                Committee.typeOfCom == TypeOfCom.MSEN.value).all()
            session["admingCurrentTable"] = " AND typeOfCom = 'MS EN'"
            genFilter = TypeOfCom.MSEN.value
            return modHelpers.returnAdminPage(assignments, genFilter)
        elif value == "MSSP":
            assignments = db.session.query(Assignment).join(Committee).filter(
                Committee.typeOfCom == TypeOfCom.MSSP.value).all()
            session["admingCurrentTable"] = " AND typeOfCom = 'MS SP'"
            genFilter = TypeOfCom.MSSP.value
            return modHelpers.returnAdminPage(assignments, genFilter)
        elif value == "Taken":
            assignments = Assignment.query.filter(or_(Assignment.delegate != None)).all()
            session["adminCurrentTable"] = " AND delegate_name != ''"
            genFilter = "Taken"
            return modHelpers.returnAdminPage(assignments, genFilter)
        elif value == "NotTaken":
            assignments = Assignment.query.filter(or_(Assignment.delegate == None)).all()
            session["adminCurrentTable"] = " AND delegate_name != ''"
            genFilter = "Taken"
            return modHelpers.returnAdminPage(assignments, genFilter)

        ### Table with teachers data ###
        elif value == "Teachers":
            teachers = Teacher.query.all()
            return render_template("admin_teachersTable.html", teachers=teachers)

        ### Table with all delegates ###
        elif value == "Delegates":
            delegates = Delegate.query.all()
            teachers = Teacher.query.order_by(Teacher.name.asc()).all()
            return render_template("admin_delegatesTable.html", delegates=delegates, teachers=teachers)

        ### Table with all committees ###
        elif value == "Committees":
            committees = Committee.query.order_by(Committee.name.asc()).all()
            return render_template("admin_committeeTable.html", committees=committees)

        ### Generate Code ###
        elif value == "GenerateCode":
            return render_template("admin_generateCode.html", code="")

        ### Change room info for committees ### !!! check this
        elif value == "changeRooms":
            committees = Committee.query.order_by(Committee.name.asc()).all()
            return render_template("admin_changeRooms.html", committees=committees)

        ### Add New Committee ###
        elif value == "AddNewCom":
            typeOfCom = []
            for com in TypeOfCom:
                typeOfCom.append(com)
            return render_template("admin_addNewCommittee.html", second=False, typeOfCom=typeOfCom)

        ### Add new Country to committee ###
        elif value == "AddNewCon":
            comID = int(request.form.get("toCommitteeDropDown"))
            session["addNewComitteeID"] = comID
            committee = Committee.query.get(comID)
            assignments = db.session.query(Assignment).join(Committee).filter(Committee.id == comID)
            return render_template("admin_addNewCountry.html", committee=committee, second=False,
                                   assignments=assignments)

        ### Delete info of all selected rows(assignments) ###
        elif value == "DeleteBulkInfo":
            rowIds = request.form.getlist("Selected")
            for row in rowIds:
                assignment = Assignment.query.get(int(row))
                if assignment.delegate is not None:
                    flash("The following committe/country has been stripped of delegate info: {} / {}".format(
                        assignment.committee.name, assignment.country))
                    db.session.delete(assignment.delegate)
            # commit all deletes
            db.session.commit()

        ### Delete the rows(assignments) selected ###
        elif value == "DeleteBulkRow":
            rowIds = request.form.getlist("Selected")
            for row in rowIds:
                assignment = Assignment.query.get(int(row))
                flash("The following committe/country and its delegate has been deleted: {} / {}".format(
                    assignment.committee.name, assignment.country))
                # if assignment is realted to delegate, must delete delegate first
                modHelpers.deleteAssignment(assignment)
                modHelpers.checkAutoCommitteeDelete()
            # idArange(Assignment)

        ### Search parameters ###
        elif value == "Search":
            com = request.form.get("committeeDropDown")
            if com == "None":
                isCommitteeSelected = False
            else:
                comID = int(com)
                isCommitteeSelected = True

            conName = request.form["countryField"]
            if conName != "":
                isCountrySelected = True
            else:
                isCountrySelected = False

            if request.form.get("Taken"):
                isNotTaken = True
            else:
                isNotTaken = False

            if isCommitteeSelected and isCountrySelected and isNotTaken:
                assignments = db.session.query(Assignment).join(Committee).filter(Committee.id == comID,
                                                                                  Assignment.country == conName,
                                                                                  Assignment.delegate == None, ).all()
                message = "Committee : {} , Country : {} , Not Taken".format(assignments[0].committee.name, conName)
            elif not isCommitteeSelected and isCountrySelected and isNotTaken:
                assignments = Assignment.query.filter(Assignment.country == conName, Assignment.delegate == None).all()
                message = "Country : {} , Not Taken".format(conName)
            elif isCommitteeSelected and not isCountrySelected and isNotTaken:
                assignments = db.session.query(Assignment).join(Committee).filter(Committee.id == comID,
                                                                                  Assignment.delegate == None).all()
                message = "Committee : {} , Not Taken".format(assignments[0].committee.name)
            elif isCommitteeSelected and isCountrySelected and not isNotTaken:
                assignments = db.session.query(Assignment).join(Committee).filter(Committee.id == comID,
                                                                                  Assignment.country == conName).all()
                message = "Committee : {} , Country : {}".format(assignments[0].committee.name, conName)
            elif not isCommitteeSelected and not isCountrySelected and isNotTaken:
                assignments = Assignment.query.filter(Assignment.delegate == None).all()
                message = "Not Taken"
            elif isCommitteeSelected and not isCountrySelected and not isNotTaken:
                assignments = db.session.query(Assignment).join(Committee).filter(Committee.id == comID).all()
                message = "Committee : {}".format(assignments[0].committee.name)
            elif (not isCommitteeSelected) and isCountrySelected and (not isNotTaken):
                assignments = Assignment.query.filter(Assignment.country == conName).all()
                message = "Country : {}".format(conName)
            else:
                assignments = Assignment.query.all()
            return modHelpers.returnAdminPage(assignments, message)

        ### Single row buttons ###
        # single row buttons only care about the first three characters of button value to decide
        listValue = value[0:3]
        # Delete Information
        if (listValue == "DI_"):
            deleteInfo = value[3:]
            assignment = Assignment.query.get(int(deleteInfo))
            if assignment.delegate is not None:
                db.session.delete(assignment.delegate)
            db.session.commit()
            flash("The following committe/country has been stripped of delegate info: {} / {}".format(
                assignment.committee.name, assignment.country))

        # Edite Row
        elif (listValue == "Ed_"):
            edit = value[3:]
            assignment = Assignment.query.filter(Assignment.id == int(edit)).first()
            return render_template("admin_editAssignment.html", assignment=assignment)

        # Delete complete row
        elif (listValue == "DR_"):
            deleteRow = value[3:]
            assignment = Assignment.query.get(int(deleteRow))
            flash("The following committe/country has been deleted: {} / {}".format(assignment.committee.name,
                                                                                    assignment.country))
            modHelpers.deleteAssignment(assignment)
            # idArange("generalList")
            modHelpers.checkAutoCommitteeDelete()

        return modHelpers.returnAdminPage("", None)


### goes with top function
### /admin_editAssignment (POST -> templateRendered)
### path to admin_editAssignment, will edit the assignment information, button on main admin page
### POST: edit the assignment information as specified
@app.route("/admin_editAssignment", methods=["POST"])
def admin_editAssignment():
    ### POST
    if request.method == "POST" and session["adminIn"] == True:
        # get values from webpage
        con = request.form["country"]
        idx = int(request.form["Button"])

        # grab assignment to deal with
        assignment = Assignment.query.get(idx)

        assignment.country = con

        # use .get() because value might be None or not there
        if request.form.get("Important") == "on":
            assignment.important = Important.YES.value
            flash("The following has changed: {} = {} , {} = {}.".format(assignment.country, con, assignment.important,
                                                                         Important.YES.value))

        else:
            flash("The following has changed: {} = {} , {} = {} .".format(assignment.country, con, assignment.important,
                                                                          Important.NO.value))

        db.session.commit()
        return modHelpers.returnAdminPage("", None)


### /admin_generateCode (POST GET -> templateRendered)
### code generator route admin_generateCode
### POST: math to generate code for teachers
### GET: return admin_generateCode.html
@app.route("/admin_generateCode", methods=["GET", "POST"])
def admin_generateCode():
    ### GET
    if request.method == "GET" and session["adminIn"] == True:
        return render_template("admin_generateCode.html", code="")
    ### POST
    if request.method == "POST" and session["adminIn"] == True:
        totalnum = (int)(request.form["numOfDel"])
        if not totalnum == 0:
            firstnum = int(totalnum % 10)
            secondnum = int(totalnum / 10)
            genfirst = math.ceil((firstnum + 10) * 3)
            gensecond = math.ceil((secondnum + 10) * 3)
            return render_template("admin_generateCode.html", code=(
                    str(gensecond) + "".join(random.choice(string.ascii_uppercase) for x in range(4)) + str(
                genfirst) + "".join(random.choice(string.ascii_uppercase) for x in range(2))))
        return render_template("admin_generateCode.html", code="")


### /admin_addNewCommittee (POST -> templateRendered) !!! might need to add options for room, GET SHOULD USE ENUM stuff
### add new committee, path to admin_addNewCommittee
### POST: two parts, first is committee creation, second is assignment creations
@app.route("/admin_addNewCommittee", methods=["POST"])
def admin_addNewCommittee():
    ### POST
    if request.method == "POST" and session["adminIn"] == True:
        value = request.form["Button"]

        ### Create committee ###
        if value == "create":
            typeCom = request.form.get("typeOfCom")
            com = request.form["committee"]
            advanced = request.form.get("advanced")
            if advanced != None:
                committee = Committee(com, typeCom, "", "Yes")
            else:
                committee = Committee(com, typeCom, "", "No")
            db.session.add(committee)
            db.session.commit()
            session["committeeInSessionID"] = committee.id
            x = int(request.form["number"])
            session["numberOfAssignments"] = x

            return render_template("admin_addNewCommittee.html", second=True, numberOfAssignments=x,
                                   committee=committee.name, typeOfCom=committee.typeOfCom)

        ### Create assignments ###
        if value == "populate":
            committeeID = int(session["committeeInSessionID"])
            committee = Committee.query.get(committeeID)
            committeeAmount = committee.numOfAssignments()
            for num in range(int(session["numberOfAssignments"])):
                country = request.form.get(str(num))
                important = request.form.get("I" + str(num))
                if important != None:
                    db.session.add(Assignment(committee.id, country, committeeAmount + num + 1, Important.YES.value))
                else:
                    db.session.add(Assignment(committee.id, country, committeeAmount + num + 1, Important.NO.value))
            db.session.commit()
            # idArange(Assignment)
            return modHelpers.returnAdminPage("", None)
    return modHelpers.returnAdminPage("", None)


### /admin_addNewCountry (POST -> templateRendered)
### path to admin_addNewCountry, add new assignments to existing committee
### POST: two stages, first gets info from committee, second creates the assignments
@app.route("/admin_addNewCountry", methods=["POST"])
def admin_addNewCountry():
    ### POST
    if request.method == "POST" and session["adminIn"] == True:
        value = request.form["Button"]

        ### Get info from committee ###
        if value == "create":
            numOfCountries = int(request.form["numOfCon"])
            session["numOfCountries"] = numOfCountries
            committee = Committee.query.get(int(session["addNewComitteeID"]))
            assignments = db.session.query(Assignment).join(Committee).filter(Committee.id == committee.id)
            return render_template("admin_addNewCountry.html", second=True, numOfAssignments=numOfCountries,
                                   committee=committee, assigments=assignments)

        ### Create assignments ###
        if value == "populate":
            committeeID = int(session["addNewComitteeID"])
            committee = Committee.query.get(committeeID)
            committeeAmount = committee.numOfAssignments()
            for num in range(session["numOfCountries"]):
                country = request.form.get(str(num))
                important = request.form.get("I" + str(num))
                if important != None:
                    db.session.add(Assignment(committee.id, country, committeeAmount + num + 1, Important.YES.value))
                else:
                    db.session.add(Assignment(committee.id, country, committeeAmount + num + 1, Important.NO.value))
            db.session.commit()
            # idArange("generalList")
            return modHelpers.returnAdminPage("", None)
    return modHelpers.returnAdminPage("", None)


### /admin_teachersTable (POST -> templateRendered)
### path to admin_teachersTable, buttons in the teacher information table with all the teachers, edit or delete teacher info
### POST: two types, delete teacher and edit teacher info
@app.route("/admin_teachersTable", methods=["POST"])
def admin_teachersTable():
    ### POST
    if request.method == "POST" and session["adminIn"] == True:
        value = request.form["Button"]
        listValue = value[0:3]

        ### Delete teacher row(teacher) ###
        if (listValue == "DE_"):
            deleteInfo = value[3:]
            teacher = Teacher.query.get(int(deleteInfo))
            delegates = Delegate.query.filter(Delegate.teacher_id == teacher.id).all()
            for delegate in delegates:
                db.session.delete(delegate)
            db.session.delete(teacher)

            flash(
                "The table of {} from school {} has been deleted, her info wiped and all her assignments destroyed.".format(
                    teacher.name, teacher.school))
            db.session.commit()
            teachers = Teacher.query.all()
            return render_template("admin_teachersTable.html", teachers=teachers)

        ### Edit teacher row(teacher) ###
        elif (listValue == "ED_"):
            edit = value[3:]
            teacher = Teacher.query.filter(Teacher.id == int(edit)).first()
            return render_template("admin_teachersTableEdit.html", teacher=teacher)
        # return the adminUser.html with all the teachers tables
        teachers = Teacher.query.all()
        return render_template("admin_teachersTable.html", teachers=teachers)


### goes together with top function /admin_teachersTable
### /admin_teachersTableEdit (POST -> templateRendered)
### path to edirRowUser
### POST: edit a teacher information !!!
@app.route("/admin_teachersTableEdit", methods=["POST"])
def admin_teachersTableEdit():
    ### POST
    if request.method == "POST" and session["adminIn"] == True:
        teacherID = request.form["Button"]
        if teacherID[0:2] == "NP":
            teacher = Teacher.query.get(teacherID[3:])
            teacher.changePassword(request.form["password"])
            flash("The password has been changed succesfully to {}.".format(request.form["password"]))
        else:
            teacher = Teacher.query.get(teacherID)
            teacher.email = request.form["email"]
            teacher.confirmationCode = request.form["ConfCode"]
            teacher.school = request.form["school"]
            flash(
                "The following has changed: {} = {} , {} = {} , {} = {} .".format(teacher.email, request.form["email"],
                                                                                  teacher.school,
                                                                                  request.form["school"],
                                                                                  teacher.confirmationCode,
                                                                                  request.form["ConfCode"]))

        db.session.commit()
        teachers = Teacher.query.all()
        return render_template("admin_teachersTable.html", teachers=teachers)


### /admin_specialFunctions (POST GET -> templateRendered)
### route to /admin_specialFunctions,
### POST: code for the special functions
### GET: reutrn returnAdminSpecialFUnctions()
### !!! implement flash info and improve functions
@app.route("/admin_specialFunctions", methods=["GET", "POST"])
def admin_specialFunctions():
    ### GET
    if request.method == "GET" and session["adminIn"] == True:
        return modHelpers.returnAdminSpecialFunctions()
    ### POST
    elif request.method == "POST" and session["adminIn"] == True:
        # button value to determin function to call
        value = request.form["Button"]

        ### Delete all the information ###
        if value == "DeleteAll":
            Delegate.query.delete()
            Teacher.query.delete()
            Assignment.query.delete()
            Committee.query.delete()

        ### Delete all the info in assignment(countries, committies delegate data) ###
        elif value == "DeleteAllCountryInfo":
            Delegate.query.delete()
            Assignment.query.delete()
            Committee.query.delete()

        ### Delete all teachers and delegate info in assignment ###
        elif value == "DeleteAllUserTables":
            Delegate.query.delete()
            Teacher.query.delete()

        ### Delete all delegate info in assignment ###
        elif value == "DeleteAllDelegateInfo":
            Delegate.query.delete()

        ### Delete an entire committee ###
        elif value == "DeleteEntireCommittee":
            committeeID = int(request.form.get("committeeDropDown"))
            committee = Committee.query.get(committeeID)
            modHelpers.deleteAssignments(committee.assignments)
            db.session.delete(committee)
        db.session.commit()
        return modHelpers.returnAdminSpecialFunctions()


### /admin_editDelegate (POST -> templateRendered)
### path to admin_editDelegate, edit teacher information in users table
### POST: edit the teacher information as specified in users table !!!
@app.route("/admin_editDelegate", methods=["POST"])
def admin_editDelegate():
    if request.method == "POST" and session["adminIn"] == True:
        com = request.form["committee"]
        con = request.form["country"]
        name = request.form["delegateName"]
        school = request.form["delegateSchool"]
        idx = request.form["Button"]
        password = request.form["password"]
        delegate = Delegate.query.get(idx)

        if password == "Jpgc231099.":
            flash("The following has changed: {} = {} , {} = {} , {} = {} , {} = {} .".format(
                delegate.assignment.committee.name, com, delegate.assignment.country, con, delegate.name, name,
                delegate.teacher.school, school))
            delegate.assignment.committee.name = com
            delegate.assignment.country = con
            delegate.name = name
            delegate.teacher.school = school
            db.session.commit()
        else:
            flash("The changes were not succesful, wrong password")
        return render_template("admin_editDelegate.html", delegate=delegate)


@app.route("/admin_takeMeToDelegate", methods=["POST"])
def admin_takeMeToDelegate():
    if request.method == "POST" and session["adminIn"] == True:
        idx = request.form["editDelegate"]
        delegate = Delegate.query.get(int(idx))
        return render_template("admin_editDelegate.html", delegate=delegate)


### /admin_delegatesTables (POST -> templateRendered)
### path to admin_delegatesTables
### POST: !!!
@app.route("/admin_delegatesTables", methods=["POST"])
def admin_delegatesTables():
    if request.method == "POST" and session["adminIn"] == True:
        value = request.form["Button"]
        if value == "Search":
            teacherSchoolID = request.form["schoolDropDown"]
            delegateName = request.form["delegateName"]

            if teacherSchoolID == "None" and delegateName.strip() != "":
                delegates = Delegate.query.filter(Delegate.name.contains(delegateName)).all()
                flash("Searching for delegate with name {}".format(delegateName))
            elif teacherSchoolID != "None" and delegateName.strip() == "":
                delegates = db.session.query(Delegate).join(Teacher).filter(Teacher.id == teacherSchoolID).all()
                schoolName = db.session.query(Teacher).filter(Teacher.id == teacherSchoolID).first().school
                flash("Searching for delegate with school {}".format(schoolName))
            elif teacherSchoolID != "None" and delegateName.strip() != "":
                delegates = db.session.query(Delegate).join(Teacher).filter(Teacher.id == teacherSchoolID,
                                                                            Delegate.name.contains(delegateName))
                schoolName = db.session.query(Teacher).filter(Teacher.id == teacherSchoolID).first().school
                flash("Searching for delegate with name {} in school {}".format(delegateName, schoolName))
            else:
                delegates = Delegate.query.all()
            teachers = Teacher.query.order_by(Teacher.name.asc()).all()
            return render_template("admin_delegatesTable.html", delegates=delegates, teachers=teachers)

        listValue = value[0:3]
        if (listValue == "ED_"):
            edit = value[3:]
            delegate = Delegate.query.filter(Delegate.id == int(edit)).first()
            return render_template("admin_editDelegate.html", delegate=delegate)
        elif listValue == "DE_":
            delete = int(value[3:])
            db.session.delete(Delegate.query.get(delete))
            db.session.commit()
        delegates = Delegate.query.all()
        teachers = Teacher.query.order_by(Teacher.name.asc()).all()
        return render_template("admin_delegatesTable.html", delegates=delegates, teachers=teachers)


### /admin_committeeTable (POST -> templateRendered)
### path to admin_committeeTable
### POST: !!!
@app.route("/admin_committeeTable", methods=["POST"])
def admin_committeeTable():
    if request.method == "POST" and session["adminIn"] == True:
        value = request.form["Button"]
        listValue = value[0:3]
        if (listValue == "ED_"):
            edit = value[3:]
            committee = Committee.query.filter(Committee.id == int(edit)).first()
            return render_template("admin_editCommittee.html", committee=committee)
        elif listValue == "DE_":
            delete = int(value[3:])
            committee = Committee.query.get(delete)
            modHelpers.deleteAssignments(committee.assignments)
            db.session.delete(committee)
            db.session.commit()
        committees = Committee.query.all()
        return render_template("admin_committeeTable.html", committees=committees)


### /admin_editCommittee (POST -> templateRendered)
### path to admin_editCommittee, edit teacher information in users table
### POST: edit the teacher information as specified in users table !!!
@app.route("/admin_editCommittee", methods=["POST"])
def admin_editCommittee():
    if request.method == "POST" and session["adminIn"] == True:
        name = request.form["committee"]
        typeOfCom = request.form["typeOfCom"]
        room = request.form["room"]
        idx = request.form["Button"]
        committee = Committee.query.get(idx)

        if request.form.get("advanced"):
            committee.advanced = "Yes"
        else:
            flash("The following has changed: {} = {} , {} = {} , {} = {} , {} = {} .".format(committee.name, name,
                                                                                              committee.typeOfCom,
                                                                                              typeOfCom, committee.room,
                                                                                              room, committee.advanced,
                                                                                              "No"))
            committee.advanced = "No"

        committee.name = name
        committee.typeOfCom = typeOfCom
        committee.room = room

        db.session.commit()
        return render_template("admin_editCommittee.html", committee=committee)


@app.route("/admin_takeMeToCommittee", methods=["POST"])
def admin_takeMeToCommittee():
    if request.method == "POST" and session["adminIn"] == True:
        idx = request.form["editCommittee"]
        committee = Committee.query.get(int(idx))
        return render_template("admin_editCommittee.html", committee=committee)


### /admin_manualRegister (POST GET -> templateRendered)
### path to admin_manualRegister, button in admin page
### POST: two part, first is get teacher, committee, and room info, second is add assignment to teacher table
### GET: return admin_manualRegister.html with teachers and committees
@app.route("/admin_manualRegister", methods=["GET", "POST"])
def admin_manualRegister():
    ### GET
    if request.method == "GET" and session["adminIn"] == True:
        teachers = Teacher.query.all()
        committees = Committee.query.all()
        return render_template("admin_manualRegister.html", teachers=teachers, committees=committees, second=False)
    ### POST
    elif request.method == "POST" and session["adminIn"] == True:
        value = request.form["Button"]
        if value == "next":
            session["addingTeacherId"] = request.form.get("toTeacher")
            teacherID = session["addingTeacherId"]
            committeeID = int(request.form["committee"])
            session["manualCommitteeID"] = committeeID
            assignments = db.session.query(Assignment).join(Committee).filter(Committee.id == committeeID,
                                                                              Assignment.delegate == None).all()
            return render_template("admin_manualRegister.html", second=True, assignments=assignments,
                                   teacher=Teacher.query.get(teacherID), committee=assignments[0].committee)

        if value == "assign":
            teacherID = session["addingTeacherId"]
            comID = int(session["manualCommitteeID"])
            committee = Committee.query.get(comID)
            countryID = int(request.form.get("country"))
            teacher = Teacher.query.get(teacherID)
            if teacher.canAddDelegate():
                assignment = Assignment.query.get(countryID)
                delegate = Delegate("", assignment.id, teacher.id, "")
                flash(
                    "You have assigned {} {} {} to {} .".format(committee.name, committee.typeOfCom, assignment.country,
                                                                teacher.name))
                db.session.add(delegate)
                db.session.commit()
            else:
                flash(
                    "Unable to assign, teacher has no spots remaining, unasing another delegate or change Special Code")
                return redirect(url_for("admin_manualRegister"))

            return modHelpers.returnAdminPage("", None)


### /admin_stats (GET -> templateRendered)
### path to admin_stats, only gives information
### GET: return number of assignments available and total by type
@app.route("/admin_stats", methods=["GET"])
def admin_stats():
    ### GET
    if request.method == "GET" and session["adminIn"] == True:
        ### Assignments available ###
        # regular assignemnts
        hsenA = modHelpers.stillAvailable(TypeOfCom.HSEN.value, Important.NO.value, Advanced.NO.value)
        hsspA = modHelpers.stillAvailable(TypeOfCom.HSSP.value, Important.NO.value, Advanced.NO.value)
        msenA = modHelpers.stillAvailable(TypeOfCom.MSEN.value, Important.NO.value, Advanced.NO.value)
        msspA = modHelpers.stillAvailable(TypeOfCom.MSSP.value, Important.NO.value, Advanced.NO.value)

        # important assignemnts
        mseniA = modHelpers.stillAvailable(TypeOfCom.MSEN.value, Important.YES.value, Advanced.NO.value)
        hseniA = modHelpers.stillAvailable(TypeOfCom.HSEN.value, Important.YES.value, Advanced.NO.value)
        msspiA = modHelpers.stillAvailable(TypeOfCom.MSSP.value, Important.YES.value, Advanced.NO.value)
        hsspiA = modHelpers.stillAvailable(TypeOfCom.HSSP.value, Important.YES.value, Advanced.NO.value)

        # advanced assignemnts
        msenaA = modHelpers.stillAvailable(TypeOfCom.MSEN.value, Important.NO.value, Advanced.YES.value)
        hsenaA = modHelpers.stillAvailable(TypeOfCom.HSEN.value, Important.NO.value, Advanced.YES.value)
        msspaA = modHelpers.stillAvailable(TypeOfCom.MSSP.value, Important.NO.value, Advanced.YES.value)
        hsspaA = modHelpers.stillAvailable(TypeOfCom.HSSP.value, Important.NO.value, Advanced.YES.value)

        # advanced and important assignemnts
        msenaiA = modHelpers.stillAvailable(TypeOfCom.MSEN.value, Important.YES.value, Advanced.YES.value)
        hsenaiA = modHelpers.stillAvailable(TypeOfCom.HSEN.value, Important.YES.value, Advanced.YES.value)
        msspaiA = modHelpers.stillAvailable(TypeOfCom.MSSP.value, Important.YES.value, Advanced.YES.value)
        hsspaiA = modHelpers.stillAvailable(TypeOfCom.HSSP.value, Important.YES.value, Advanced.YES.value)

        # summation of all the available assignements
        totalA = hsenA + hsspA + msenA + msspA + mseniA + hseniA + msspiA + hsspiA + hsenaA + hsspaA + msenaA + msspaA + msenaiA + hsenaiA + msspaiA + hsspaiA

        ### Assignments total ###
        # regular assignemnts
        hsenT = modHelpers.maxAssignInGen(TypeOfCom.HSEN.value, Important.NO.value, Advanced.NO.value)
        hsspT = modHelpers.maxAssignInGen(TypeOfCom.HSSP.value, Important.NO.value, Advanced.NO.value)
        msenT = modHelpers.maxAssignInGen(TypeOfCom.MSEN.value, Important.NO.value, Advanced.NO.value)
        msspT = modHelpers.maxAssignInGen(TypeOfCom.MSSP.value, Important.NO.value, Advanced.NO.value)

        # important assignemnts
        mseniT = modHelpers.maxAssignInGen(TypeOfCom.MSEN.value, Important.YES.value, Advanced.NO.value)
        hseniT = modHelpers.maxAssignInGen(TypeOfCom.HSEN.value, Important.YES.value, Advanced.NO.value)
        hsspiT = modHelpers.maxAssignInGen(TypeOfCom.HSSP.value, Important.YES.value, Advanced.NO.value)
        msspiT = modHelpers.maxAssignInGen(TypeOfCom.MSSP.value, Important.YES.value, Advanced.NO.value)

        # advanced assignemnts
        msenaT = modHelpers.maxAssignInGen(TypeOfCom.MSEN.value, Important.NO.value, Advanced.YES.value)
        hsenaT = modHelpers.maxAssignInGen(TypeOfCom.HSEN.value, Important.NO.value, Advanced.YES.value)
        msspaT = modHelpers.maxAssignInGen(TypeOfCom.MSSP.value, Important.NO.value, Advanced.YES.value)
        hsspaT = modHelpers.maxAssignInGen(TypeOfCom.HSSP.value, Important.NO.value, Advanced.YES.value)

        # advanced and important assignemnts
        msenaiT = modHelpers.maxAssignInGen(TypeOfCom.MSEN.value, Important.YES.value, Advanced.YES.value)
        hsenaiT = modHelpers.maxAssignInGen(TypeOfCom.HSEN.value, Important.YES.value, Advanced.YES.value)
        msspaiT = modHelpers.maxAssignInGen(TypeOfCom.MSSP.value, Important.YES.value, Advanced.YES.value)
        hsspaiT = modHelpers.maxAssignInGen(TypeOfCom.HSSP.value, Important.YES.value, Advanced.YES.value)

        totalT = hsenT + hsspT + msenT + msspT + mseniT + hseniT + msspiT + hsspiT + hsenaT + hsspaT + msenaT + msspaT + msenaiT + hsenaiT + msspaiT + hsspaiT

        committees = Committee.query.all()

        # return the template with data
        return render_template("admin_stats.html", hsenA=hsenA, hsspA=hsspA, msenA=msenA, msspA=msspA, hsenT=hsenT,
                               hsspT=hsspT, msspT=msspT, msenT=msenT, totalT=totalT, totalA=totalA, mseniA=mseniA,
                               hseniA=hseniA, mseniT=mseniT,
                               hseniT=hseniT, msspiA=msspiA, hsspiA=hsspiA, msspiT=msspiT, hsspiT=hsspiT,
                               committees=committees,
                               hsenaA=hsenaA, hsspaA=hsspaA, msenaA=msenaA, msspaA=msspaA, hsenaT=hsenaT,
                               hsspaT=hsspaT, msspaT=msspaT, msenaT=msenaT, msenaiA=msenaiA, hsenaiA=hsenaiA,
                               msenaiT=msenaiT,
                               hsenaiT=hsenaiT, msspaiA=msspaiA, hsspaiA=hsspaiA, msspaiT=msspaiT, hsspaiT=hsspaiT)


### /admin_printCommittee (POST GET -> templateRendered)
### path to admin_printCommittee
### POST: admin print committee
### GET: teacher print their list of assignments
@app.route("/admin_printCommittee", methods=["POST", "GET"])
def admin_printCommittee():
    ### GET (teacher print)
    if request.method == "GET" and session["adminIn"] == True:
        lista = []
        lista = modHelpers.getComDropDownOpt()
        return render_template("admin_printCommittee.html", first=True, second=False, committees=lista)
    ### POST (admin print)
    elif request.method == "POST" and session["adminIn"] == True:
        comName = request.form.get("committeeDropDown")
        committee = Committee.query.filter(Committee.name == comName).first()
        return render_template("admin_printCommittee.html", first=False, second=True, committee=committee,
                               assignments=committee.assignments)


## /admin_changeRooms (POST -> templateRendered)
## path to admin_changeRooms
## POST: change the room info of committees in generalList and teacher tables
@app.route("/admin_changeRooms", methods=["POST"])
def admin_changeRooms():
    ### POST
    if request.method == "POST" and session["adminIn"] == True:
        committees = Committee.query.all()
        for committee in committees:
            newRoom = request.form[str(committee.id)]
            committee.room = newRoom

        db.session.commit()
        flash("Rooms have been successfully changed.")
        return render_template("admin_changeRooms.html", committees=committees)


###############################################################################################################################################################
###############################################################################################################################################################
#####################################################    ERROR HANDLERS      ##################################################################################
###############################################################################################################################################################
###############################################################################################################################################################

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template("_errorPage.html", number="404"), 404


@app.errorhandler(405)
def error405(e):
    # note that we set the 404 status explicitly
    return render_template("_errorPage.html", number="405"), 405


@app.errorhandler(403)
def error403(e):
    # note that we set the 404 status explicitly
    return render_template("_errorPage.html", number="403"), 403


@app.errorhandler(500)
def error500(e):
    # note that we set the 404 status explicitly
    return render_template("_errorPage.html", number="500"), 500


@app.errorhandler(502)
def error502(e):
    # note that we set the 404 status explicitly
    return render_template("_errorPage.html", number="502"), 502


if __name__ == "__main__":
    app.run()
    debug = True
# Made by JP Garcia

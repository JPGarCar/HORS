#!/usr/bin/python

# import multiple packeges
# for sql use
from cs50 import SQL
# flask for web service
from flask import Flask, redirect, render_template, request, url_for, session, flash, send_file
# for the random assignemnt generator
from random import *
# basic math needed
import math
# for sentry issue resolver
from raven.contrib.flask import Sentry

### imports used for the word document creation
#from docx import 5Document
#from docx.shared import Inches, RGBColor, Pt
#from docxtpl import DocxTemplate

# defines variable 'app' to the flask
app = Flask(__name__)
app.secret_key = "immunsasfm2018"
# if there is any session data on the users computer then clear it
if session:
    session.clear()
    session.pop('_flashes', None)

# assigns variable 'db' to the SQL database immuns.db
db = SQL("sqlite:///immuns.db")

# assing sentry its code to connect to account
sentry = Sentry(app, dsn='https://effbb4c86ee440eebbb9f8d2de12cd6f:e32dca8980a440e699031e80789d3a06@sentry.io/1238266')



##### no globals are used, instead the session module from flask is used, it uses cookies so that is way better.

###############################################################################################################################################################
###############################################################################################################################################################
#########################################################  Functions   ########################################################################################
###############################################################################################################################################################
###############################################################################################################################################################

# I tried to let users downoad the lists of the assignments but the options are too limited for the document, it will be better in an html page
"""
def downloadDoc(assignments, School):
    #doc = DocxTemplate("template-doc.docx")
    doc = Document()
    font = doc.styles['Normal'].font
    #font.name = 'Cinzel'
    run = doc.add_heading('IMMUNS Country Assignments', 0).add_run()
    font = run.font
    font.size = Pt(29)
    run = doc.add_paragraph("These are the country assignments for {}.".format(School["school"])).add_run()
    font = run.font
    font.size = Pt(16)
    run.add_break()
    table = doc.add_table(rows=1, cols=3)
    #table.style = 'List Table 3'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Committee'
    hdr_cells[1].text = 'Country'
    hdr_cells[2].text = 'Delegate Name'
    for assignment in assignments:
        row_cells = table.add_row().cells
        row_cells[0].text = assignment["committee"]
        row_cells[1].text = assignment["country"]
        row_cells[2].text = assignment["delegateName"]

    doc.save("assignments.doc")

    return send_file("assignments.doc", as_attachment=True, attachment_filename='assignments.doc')

"""

### idArange (String -> Void)
### string can be name of user or table
### simple method that re arranges the id's of the coutnries in a user or a table
def idArange(user):
    # grab all rows in table
    countries = db.execute("SELECT * FROM :user", user=user)
    # first id number
    x = 1
    # over all the rows, update its id to "x"
    for country in countries:
        db.execute("UPDATE :user SET id=:idx WHERE id=:firstID", user=user, idx=x, firstID=country["id"])
        x = x + 1


### getSpecial (String -> Number or None)
### String is a special code only
### produce number of possible assignemnts from inputed special code, or None if invalid special code
### usses first two and 6th and 7th char to get the Number
def getSpecial(string):
    ## gets the chars needed
    first = string[0:2]
    second = string[6:8]
    # tries to convert the chars to Integers, if not possible return None
    try:
        value = int(first)
    except ValueError:
        return None
    try:
        value = int(second)
    except ValueError:
        return None
    # simple premade arithmetic to find the number and return it
    if int(first) >= 0 and int(second) >= 0:
        finalOne = (int(first)/3)-10
        finalTwo = (int(second)/3)-10
        return (finalOne*10) + finalTwo
    return None

### maxTypeInGen (String -> Number)
### return number of assignment available of type and Importance in generalList
def maxTypeInGen(typee, Important):
    num = 0
    # grabs all assignments as specified
    assignments = db.execute("SELECT * FROM generalList WHERE typeOfCom = :typee AND delegate_name='' AND Important= :Imp ", typee=typee, Imp=Important)
    # iterates over all the assignments in the table adding one to the variable "num"
    for assignment in assignments:
        num = num + 1
    return num

### maxAssignInGen (String String -> Number)
### return number of assignments of type and importance in generalList
def maxAssignInGen(typex, importance):
    num = 0
    # grabs all assignemnts
    assignments = db.execute("SELECT * FROM generalList WHERE typeOfCom = :typez AND Important= :Imp", typez=typex, Imp=importance)
    # iterates over all the assignments in the table adding one to the variable "num"
    for assignment in assignments:
        num = num + 1
    return num

### MaxNumInUser (String -> Number)
def MaxNumInUser(user):
    num = 0
    # grabs all assignments of user
    assignments = db.execute("SELECT * FROM :users", users=user)
    # iterates over all the assignments in the table adding one to the variable num
    for assignment in assignments:
        num = num + 1
    return num

### randomCountry (Number String String -> Void)
### Randomly assigns assignments to current user's table as specified
def randomCountry(number, typeOfCom, Important):
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
        assignments = db.execute("SELECT * FROM generalList WHERE delegate_name='' AND typeOfCom = :typeOfCom AND Important= :Imp", typeOfCom=typeOfCom, Imp=Important)
        # assignment from assignemnts in index "codeID"
        assignment = assignments[codeID]
        # assignment assigned to current user and its table updated
        if not assignment["room"] == "":
            db.execute("INSERT INTO :tableName (committee, country, delegateName, room, important) VALUES(:committee, :country, :delNam, :room, :imp)",
            tableName=session["currentUser"], committee=assignment["committee"], country=assignment["country"], delNam="", room=assignment["room"], imp=assignment["Important"])
        else:
            db.execute("INSERT INTO :tableName (committee, country, delegateName, room, important) VALUES(:committee, :country, :delNam, :room, :imp)",
            tableName=session["currentUser"], committee=assignment["committee"], country=assignment["country"], delNam="", room="", imp=assignment["Important"])
        # updates the generalList
        db.execute("UPDATE generalList SET delegate_name='taken', delegate_school =:school WHERE committee=:com AND country=:con",
        school=session["currentUser"], com=assignment["committee"] ,con=assignment["country"])
        # reduces number of pedning assignments by one
        numAssign = numAssign - 1
        # increase the numer of iterations of random
        ranNum = ranNum + 1


### getInfCurUsr (Void -> userRow) !!!  This function is not used
### return row information in list of current user using session info
def getInfCurUsr():
    user = db.execute("SELECT * FROM users WHERE id=:idx", idx=session["currentUserId"])
    for use in user:
        return use


### returnUserPageOld (Void -> templateRendered)
### returns the rendered template userPageOld.html with corresponding data from current user's table
def returnUserPageOld():
    user = db.execute("SELECT * FROM :userx", userx=session["currentUser"])
    return render_template("userPageOld.html", users=user)


### returnAdminPage ( -> templateRendered)
### return the admin template
def returnAdminPage(assignments, serchParam):
    sList = getComDropDownOpt()
    # grab all assignemnts from generalList if current assignemnts is empty string
    if assignments == "":
        assignments = db.execute("SELECT * FROM generalList")
    else:
        assignments=assignments
    # return admin.html with assignemnts as rows, sList as committees for drop down and serchParam as flash message
    return render_template("admin.html", users=assignments, committees=sList, error=serchParam)


### getComDropDownOpt (Void -> (listof String))
### return list of all committie names
def getComDropDownOpt():
    sList = []
    sList.append("None")
    committees = db.execute("SELECT committee FROM generalList")
    for committee in committees:
        if not committee in sList:
            sList.append(committee)
    return sList


### returnAdminSpecialFunctions (Void -> templateRendered)
### return the special functions admin tempalate
def returnAdminSpecialFunctions():
    sList = getComDropDownOpt()
    return render_template("adminSpecialFunctions.html", committees=sList)


### stillAvailable (String String -> Number)
### return number of
def stillAvailable(typeOfCom, Important):
    # grab specified assignments available
    assignments = db.execute("SELECT * FROM generalList WHERE delegate_name = :name AND typeOfCom = :typeOfCom AND Important= :Imp", name="", typeOfCom=typeOfCom, Imp=Important)
    # count number of available assignments then return that number
    available = 0
    for assignment in assignments:
        available = available + 1
    return available

### makeUser (String String -> String)
### produces unique user id from its name and school without any special characters
def makeUser(name, school):
    return replaceSpecial(name) + replaceSpecial(school)

### replaceSpecial (String -> String)
### strips a string from special characters
def replaceSpecial(string):
    string = string.replace(" ", "")
    string = string.replace("_", "")
    string = string.replace("-", "")
    string = string.replace("'", "")
    string = string.replace(".", "")
    return string


### assginToInt (String -> Number)
### convert string to Number, if "" then 0, also gets rid of decimal value
def assignToInt(string):
    if string == "":
        return 0
    elif "." in string:
        string = string[:-2]
        return int(string)
    else:
        return int(string)


###############################################################################################################################################################
###############################################################################################################################################################
#######################################################  Routes for main Page   ###############################################################################
###############################################################################################################################################################
###############################################################################################################################################################

### / (GET POST -> templateRendered)
### main route to the sign in page,
### GET: returns the registration template
### POST: signs in a user if email and password match or sign admin
@app.route("/", methods = ["GET", "POST"])
def registration():
    ### GET
    if request.method == "GET":
        return render_template("registration.html")

    ### POST
    elif request.method == "POST":
        # restart seesion
        session["currentUser"] = None

        ### Check In Admin ###
        if request.form["signInEmail"] == "admin@gmail.com" and request.form["signInPassword"] == "adminPassword":
            session["adminIn"] = True
            return returnAdminPage("", None)

        ### Sign In User ###
        # grabs the user from table users with the inputed email and password from the input fields
        userx = db.execute("SELECT * FROM users WHERE email = :email AND password = :password",
                email=request.form["signInEmail"], password=request.form["signInPassword"])
        # loops over the user, if there is no user it will not enter the loop and return the same page with flash
        for user in userx:
            if user["personName"] != "":
                # assign session variables
                session["currentUser"] = makeUser(user["personName"], user["school"])
                session["currentUserId"] = user["id"]
                # variable "special" has the number from sepcial code
                special = getSpecial(user["confirmationCode"])
                # assign assignments in current user
                numNow = MaxNumInUser(session["currentUser"])
                # if the user has same assignments as his code permits then go to user page old
                if numNow == special:
                    return returnUserPageOld()
                # else go get more delgates
                else:
                    # assigns 'numRem' the number of delegates remainging
                    numRem = special - numNow
                    return render_template("userPageNew.html", user=user, numRem=int(numRem))
        flash("You have entered an incorrect email or password, please try again. If the problem persists, call your HOSPITALITY member for asistance.")
        return render_template("registration.html")


### /signUp (GET POST -> templateRendered)
### signUp reoute to sign up a new user
### GET: returns the signUp template
### POST: checks if all fields are filled and correct and makes the new user
@app.route("/signUp", methods = ["POST", "GET"])
def signUp():
    ### GET
    if request.method == "GET":
        return render_template("signUp.html")

    ### POST
    elif request.method == "POST":
        ### Validate confirmation code ###
        # checks confirmation code validity using getSpecial() if not vaild return same page with flash error
        if getSpecial(request.form["confirmationCode"]) == None:
            flash("You have entered an incorrect confirmation code.")
            flash("Please enter a valid confirmation code, if the problem persists, contact your HOSPITALITY member.")
            return render_template("signUp.html")

        else:
            ### Check Email Availability ###
            # grabs all the user's emails from table users and loops
            usersEmails = db.execute("SELECT email FROM users")
            userEmail = request.form["email"]
            for email in usersEmails:
                # if email inputed is already in use return same page with flash error
                if email == userEmail:
                    flash("The email you have entered is already in use. If you do not remember your password please contact your HOSPITALITY member.")
                    return render_template("signUp.html")

            ### Check Passwords Match ###
            if not request.form["password"] == request.form["password_second"]:
                flash("The passwords that you have entered do not match, please try again.")
                return render_template("signUp.html")

            ### Adding User to User table ###
            # add user to user table
            db.execute("INSERT INTO users (personName, email, school, password, confirmationCode) VALUES(:name, :email, :school, :password, :confCode)",
                    name=request.form["personName"], email=request.form["email"], school=request.form["school"], password=request.form["password"],
                    confCode=request.form["confirmationCode"])
            # creates the table for the new user
            db.execute("CREATE TABLE :tableName ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 'committee' TEXT, 'country' TEXT, 'delegateName' TEXT, 'room' TEXT, 'important' TEXT)"
                        , tableName=makeUser(request.form["personName"], request.form["school"]))
            # return template signUpSuccess
            return render_template("signUpSuccess.html")


### /signOut (POST -> templateRendered)
### signs out the user
### POST: delete all session data and return registration.html
@app.route("/signOut", methods=["POST"])
def signOut():
    if request.method == "POST" and not session["currentUser"] == None:
        if session:
            session.clear()
        return render_template("registration.html")

### /signUpSuccess (GET POST -> templateRendered)
### signUpSuccess route, simple node
### GET: returns the signUpSuccess template
### POST: returnes the user to registration template
@app.route("/signUpSuccess", methods = ["POST", "GET"])
def signUpSuccess():
    ### POST
    if request.method == "POST":
        return render_template("registration.html")

    ### GET
    else:
        return render_template("signUpSuccess.html")

### /userPageNew (POST -> templateRendered)
### userPageNew route, for the new users that need to select the number of assignments
### POST: let users select number of assignments limited to their code limit
@app.route("/userPageNew", methods = ["POST"])
def userPageNew():
    ### POST
    # check post and that session has data to be used
    if request.method == "POST" and not session["currentUser"] == None:
        # assigns the number of delegates requested in each variable
        MSE = assignToInt(request.form["MSE"])
        MSS = assignToInt(request.form["MSS"])
        HSE = assignToInt(request.form["HSE"])
        HSS = assignToInt(request.form["HSS"])
        HSEI = assignToInt(request.form["HSEI"])
        MSEI = assignToInt(request.form["MSEI"])
        MSSI = assignToInt(request.form["MSSI"])
        HSSI = assignToInt(request.form["HSSI"])
        # assings 'number' number of requested delegates plus delegates already in the user's table
        number = MSE + MSS + HSE + HSS + MSEI + HSEI + MSSI + HSSI + MaxNumInUser(session["currentUser"])
        # grabs the current user confirmationCode to check it gives same number of requested delegates
        confiCodes = db.execute("SELECT confirmationCode FROM users WHERE id = :ids", ids=session["currentUserId"])
        for confiCode in confiCodes:
            target = getSpecial(confiCode['confirmationCode'])
        # goes over all the requested delegates checking there are requested of such type and there are remeaining in generalList
        # if true, then calls randomCountry() to assign the assignment
        if  number == target:
            # list for possible error messages
            possErrors = []
            # available assigments of corresponding type
            MSEAvailable = stillAvailable("MS EN", "No")
            HSEAvailable = stillAvailable("HS EN", "No")
            MSSAvailable = stillAvailable("MS SP", "No")
            HSSAvailable = stillAvailable("HS SP", "No")
            MSEIAvailable = stillAvailable("MS EN", "Yes")
            HSEIAvailable = stillAvailable("HS EN", "Yes")
            MSSIAvailable = stillAvailable("MS SP", "Yes")
            HSSIAvailable = stillAvailable("HS SP", "Yes")
            # if there are not enough assignments available adds an error to the list and does not add any assignmetns of the type
            if MSE != 0:
                if MSEAvailable >= MSE:
                    randomCountry(MSE, "MS EN", "No")
                else:
                    possErrors.append("There are not enough Middle School English committees, there are only " + str(MSEAvailable) + " left. You asked for: " + str(MSE))
            if MSS != 0:
                if MSSAvailable >= MSS:
                    randomCountry(MSS, "MS SP", "No")
                else:
                    possErrors.append("There are not enough Middle School Spanish committees, there are only " + str(MSSAvailable) + " left. You asked for: " + str(MSS))
            if HSE != 0:
                if HSEAvailable >= HSE:
                    randomCountry(HSE, "HS EN", "No")
                else:
                    possErrors.append("There are not enough High School English committees, there are only " + str(HSEAvailable) + " left. You asked for: " + str(HSE))
            if HSS != 0:
                if HSSAvailable >= HSS:
                    randomCountry(HSS, "HS SP", "No")
                else:
                    possErrors.append("There are not enough High School Spanish committees, there are only " + str(HSSAvailable) + " left. You asked for: " + str(HSS))
            if HSEI != 0:
                if HSEIAvailable >= HSEI:
                    randomCountry(HSEI, "HS EN", "Yes")
                else:
                    possErrors.append("There are not enough High School English Important committees, there are only " + str(HSEIAvailable) + " left. You asked for: " + str(HSEI))
            if MSEI != 0:
                if MSEIAvailable >= MSEI:
                    randomCountry(MSEI, "MS EN", "Yes")
                else:
                    possErrors.append("There are not enough Middle School English Important committees, there are only " + str(MSEIAvailable) + " left. You asked for: " + str(MSEI))
            if MSSI != 0:
                if MSSIAvailable >= MSSI:
                    randomCountry(MSSI, "MS SP", "Yes")
                else:
                    possErrors.append("There are not enough Middle School Spanish Important committees, there are only " + str(MSSIAvailable) + " left. You asked for: " + str(MSSI))
            if HSSI != 0:
                if HSSIAvailable >= HSSI:
                    randomCountry(HSSI, "HS SP", "Yes")
                else:
                    possErrors.append("There are not enough High School Spanish Important committees, there are only " + str(HSSIAvailable) + " left. You asked for: " + str(HSSI))
            # check error list is not empty, then return same page with flash errors, else return userPageOld()
            if len(possErrors) > 0:
                for error in range(0,len(possErrors)):
                    flash("All the assignments have been added to your account except for:")
                    flash(possErrors[error])
                numRem = target - MaxNumInUser(session["currentUser"])
                return render_template("userPageNew.html", user = session["currentUser"], numRem = numRem)
            else:
                return returnUserPageOld()
        else:
            # if incorrect number of assignments, return same page with number of assignments remeaining
            numRem = target - MaxNumInUser(session["currentUser"])
            flash("You have entered an incorrect number of assignemnts, please try again you have {} assignments remaining.".format(numRem))
            return render_template("userPageNew.html", user = session["currentUser"], numRem = numRem)

    flash("An error was encountered please log in again. If the error persists call your HOSPITALITY member.")
    return render_template("registration.html")


### /goTo (POST -> templateRendered)
### goTo route, takes to the singUp template used after the user registers only has POST for button click
@app.route("/goTo", methods = ["POST"])
def goTo():
    ### POST
    return render_template("signUp.html")

### /userPageOld (POST GET -> templateRendered)
### user page old route
### POST: name of student is updated if anything in input bar, else name stays as taken
### GET: the program returns the userPageOld()
@app.route("/userPageOld", methods = ["POST", "GET"])
def userPageOld():

    ### POST
    if request.method == "POST" and not session["currentUser"] == None:
        # gets all assginments from table of the current user in session
        assignments = db.execute("SELECT * FROM :user", user=session["currentUser"])
        for assignment in assignments:
            # asigns y the assignment ID in the table that corresponds to the ID of the input bar
            assgnID = str(assignment["id"])
            # uses the assgnID of the deleagte to get name in html page input bar
            formAssgn = request.form[assgnID]
            # checks if the input bar has a valid name input or not
            if formAssgn == "" or formAssgn == " ":
                # name is put to 'taken' if the delegate name is blank only
                db.execute("UPDATE :user SET delegateName='' WHERE id=:idx", user=session["currentUser"], idx=assignment["id"])
            else:
                # name is updated to the input string from the bar in user's table
                db.execute("UPDATE :user SET delegateName=:name WHERE id=:idx", user=session["currentUser"], name=formAssgn,
                idx=assignment["id"])
            # update the name of the assignment in the general list of all countries
            db.execute("UPDATE generalList SET delegate_name=:name WHERE committee=:com AND country=:coun", name=formAssgn,
            com=assignment["committee"], coun=assignment["country"])
        # return the user page old with returnUserPageOld()
        flash("The names have been changed as requested.")
        return returnUserPageOld()

    ### GET
    elif request.method == "GET" and not session["currentUser"] == None:
        return returnUserPageOld()


### /userDownload (POST -> templateRendered)
### return printable html file with all the user's info
### POST: render printAssignments.html with user's info
@app.route("/userDownload", methods=["POST"])
def userDownload():
    ### POST
    if request.method == "POST" and not session["currentUser"] == None:
        # grabs the school name of user
        schools = db.execute("SELECT school FROM users WHERE id = :idx", idx=session["currentUserId"])
        school = schools[0]
        # grabs all assignments of the user
        assignments = db.execute("SELECT * FROM :table", table=session["currentUser"])
        # return the html file with the data
        return render_template("printAssignments.html", school=school["school"], users=assignments)


### /logOut (POST -> templateRendred)
### similiar to signOut but different unknown use
### POST: delete all session info and flashes, return registration.html
@app.route("/logOut", methods=["POST"])
def logOut():
    if session:
        session.clear()
        session.pop('_flashes', None)
    return render_template("registration.html")


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
        return returnAdminPage("", None)
    ### POST
    if request.method == "POST" and session["adminIn"] == True:
        #
        session["admingCurrentTable"] = ""
        # value tells what button was clicked
        value = request.form["Button"]

        ### General Filter Buttons ###
        if value == "MS":
            assignments = db.execute("SELECT * FROM generalList WHERE typeOfCom = 'MS EN' OR typeOfCom = 'MS SP'")
            session["admingCurrentTable"] = " AND (typeOfCom = 'MS EN' OR typeOfCom = 'MS SP')"
            genFilter = "MS"
            return returnAdminPage(assignments, genFilter)
        elif value == "HS":
            assignments = db.execute("SELECT * FROM generalList WHERE typeOfCom = 'HS EN' OR typeOfCom = 'HS SP'")
            session["admingCurrentTable"] = " AND (typeOfCom = 'HS EN' OR typeOfCom = 'HS SP')"
            genFilter = "HS"
            return returnAdminPage(assignments, genFilter)
        elif value == "ALL":
            session["admingCurrentTable"] = ""
            return returnAdminPage("", None)
        elif value == "English":
            assignments = db.execute("SELECT * FROM generalList WHERE typeOfCom = 'HS EN' OR typeOfCom = 'MS EN'")
            session["admingCurrentTable"] = " AND (typeOfCom = 'HS EN' OR typeOfCom = 'MS EN')"
            genFilter = "English"
            return returnAdminPage(assignments, genFilter)
        elif value == "Spanish":
            assignments = db.execute("SELECT * FROM generalList WHERE typeOfCom = 'HS SP' OR typeOfCom = 'MS SP'")
            session["admingCurrentTable"] = " AND (typeOfCom = 'HS SP' OR typeOfCom = 'MS SP')"
            genFilter = "Spanish"
            return returnAdminPage(assignments, genFilter)
        elif value == "HSEN":
            assignments = db.execute("SELECT * FROM generalList WHERE typeOfCom = 'HS EN'")
            session["admingCurrentTable"] = " AND typeOfCom = 'HS EN'"
            genFilter = "HS EN"
            return returnAdminPage(assignments, genFilter)
        elif value == "HSSP":
            assignments = db.execute("SELECT * FROM generalList WHERE typeOfCom = 'HS SP'")
            session["admingCurrentTable"] = " AND typeOfCom = 'HS SP'"
            genFilter = "HS SP"
            return returnAdminPage(assignments, genFilter)
        elif value == "MSEN":
            assignments = db.execute("SELECT * FROM generalList WHERE typeOfCom = 'MS EN'")
            session["admingCurrentTable"] = " AND typeOfCom = 'MS EN'"
            genFilter = "MS EN"
            return returnAdminPage(assignments, genFilter)
        elif value == "MSSP":
            assignments = db.execute("SELECT * FROM generalList WHERE typeOfCom = 'MS SP'")
            session["admingCurrentTable"] = " AND typeOfCom = 'MS SP'"
            genFilter = "MS SP"
            return returnAdminPage(assignments, genFilter)
        elif value == "Taken":
            assignments = db.execute("SELECT * FROM generalList WHERE delegate_name !=''")
            session["adminCurrentTable"] = " AND delegate_name != ''"
            genFilter = "Taken"
            return returnAdminPage(assignments, genFilter)

        ### Table with users data ###
        elif value == "Users":
            users = db.execute("SELECT * FROM users")
            return render_template("adminUsers.html",users=users)

        ### Table with user tables data ###
        elif value == "UsersTable":
            users = db.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
            users.pop(0)
            users.pop(0)
            users.pop(0)
            return render_template("adminUserTable.html", users=users)

        ### Generate Code ###
        elif value == "GenerateCode":
            return render_template("adminGenCode.html", code="")

        ### Change room info for committees ###
        elif value == "changeRooms":
            lista = []
            listb = []
            committees = db.execute("SELECT * FROM generalList")
            for committee in committees:
                if not committee["committee"] in lista:
                    lista.append(committee["committee"])
                    listb.append(committee)
            return render_template("adminChangeRooms.html", users=listb)

        ### Add New Committee ###
        elif value == "AddNewCom":
            return render_template("adminAddNew.html")

        ### Add new Country to committee ###
        elif value == "AddNewCon":
            com = request.form.get("toCommitteeDropDown")
            session["addNewComitteeCom"] = com
            return render_template("adminAddNewCon.html", committee=com)

        ### Delete info of all selected rows(assignments) ###
        elif value == "DeleteBulkInfo":
            rowIds = request.form.getlist("Selected")
            for row in rowIds:
                currentInfos = db.execute("SELECT * FROM generalList WHERE id=:idx", idx=int(row))
                currentInfo = currentInfos[0]
                if not currentInfo["delegate_name"] == "":
                    db.execute("DELETE FROM :table WHERE country=:con and committee=:com",
                    table=currentInfo["delegate_school"], con=currentInfo["country"], com=currentInfo["committee"])
                db.execute("UPDATE generalList SET delegate_name = '', delegate_school = '' WHERE id=:idx", idx=int(row))
                flash("The following committe/country has been stripped of delegate info: {} / {}".format(currentInfo["committee"],currentInfo["country"]))

        ### Delete the rows(assignments) selected ###
        elif value == "DeleteBulkRow":
            rowIds = request.form.getlist("Selected")
            for row in rowIds:
                currentInfos = db.execute("SELECT * FROM generalList WHERE id=idx", idx=row)
                currentInfo = currentInfos[0]
                flash("The following committe/country has been deleted: {} / {}".format(currentInfo["committee"],currentInfo["country"]))
                db.execute("DELETE FROM generalList WHERE id=:idx", idx=row)
            idArange("generalList")

        ### Search parameters ###
        elif value == "Search":
            com = request.form.get("committeeDropDown")
            comYes = False
            conYes = False
            takenYes = False
            con = request.form["countryField"]
            if com != "":
                comYes = True
            if con != "":
                conYes = True
            if request.form.get("Taken"):
                takenYes = True
            if comYes and conYes and takenYes:
                ins = "SELECT * FROM generalList WHERE committee=:com AND country=:con AND delegate_name =''" + session["admingCurrentTable"]
                users = db.execute(ins,
                com=com, con=con)
                error = "Committee : {} , Country : {} , Not Taken".format(com , con)
                return returnAdminPage(users, error)
            elif not comYes and conYes and takenYes:
                ins = "SELECT * FROM generalList WHERE country=:con AND delegate_name =''" + session["admingCurrentTable"]
                users = db.execute(ins, con=con)
                error = "Country : {} , Not Taken".format(con)
                return returnAdminPage(users, error)
            elif comYes and not conYes and takenYes:
                ins = "SELECT * FROM generalList WHERE committee=:com AND delegate_name =''" + session["admingCurrentTable"]
                users = db.execute(ins,
                com=com)
                error = "Committee : {} , Not Taken".format(com)
                return returnAdminPage(users, error)
            elif comYes and conYes and not takenYes:
                ins = "SELECT * FROM generalList WHERE committee=:com AND country=:con" + session["admingCurrentTable"]
                users = db.execute(ins,
                com=com, con=con)
                error = "Committee : {} , Country : {}".format(com , con)
                return returnAdminPage(users, error)
            elif not comYes and not conYes and takenYes:
                ins = "SELECT * FROM generalList WHERE delegate_name =''" + session["admingCurrentTable"]
                users = db.execute(ins)
                error = "Not Taken"
                return returnAdminPage(users, error)
            elif comYes and not conYes and not takenYes:
                ins = "SELECT * FROM generalList WHERE committee=:com" + session["admingCurrentTable"]
                users = db.execute(ins, com=com)
                error = "Committee : {}".format(com)
                return returnAdminPage(users, error)
            elif (not comYes) and conYes and (not takenYes):
                ins = "SELECT * FROM generalList WHERE country=:con" + session["admingCurrentTable"]
                users = db.execute(ins,con=con)
                error = "Country : {}".format(con)
                return returnAdminPage(users, error)

        ### Single row buttons ###
        # single row buttons only care about the first three characters of button value to decide
        listValue = value[0:3]
        # Delete Information
        if (listValue == "DI_"):
            deleteInfo = value[3:]
            currentInfos = db.execute("SELECT * FROM generalList WHERE id=:idx", idx=int(deleteInfo))
            currentInfo = currentInfos[0]
            if not currentInfo["delegate_name"] == "":
                db.execute("DELETE FROM :table WHERE country=:con and committee=:com",
                table=currentInfo["delegate_school"], con=currentInfo["country"], com=currentInfo["committee"])
            db.execute("UPDATE generalList SET delegate_name = '', delegate_school = '' WHERE id=:idx", idx=int(deleteInfo))
            flash("The following committe/country has been stripped of delegate info: {} / {}".format(currentInfo["committee"],currentInfo["country"]))
            return returnAdminPage("", None)
        # Edite Row
        elif (listValue == "Ed_"):
            edit = value[3:]
            row = db.execute("SELECT * FROM generalList WHERE id=:idx", idx=int(edit))
            return render_template("adminEditeRow.html", rows=row)
        # Delete complete row
        elif (listValue == "DR_"):
            deleteRow = value[3:]
            currentInfos = db.execute("SELECT * FROM generalList WHERE id=:idx", idx=int(deleteRow))
            currentInfo = currentInfos[0]
            flash("The following committe/country has been deleted: {} / {}".format(currentInfo["committee"],currentInfo["country"]))
            db.execute("DELETE FROM generalList WHERE id=:idx", idx=int(deleteRow))
            idArange("generalList")
            return returnAdminPage("", None)
        return returnAdminPage("", None)


### /codeGen (POST GET -> templateRendered)
### code generator route adminGenCode
### POST: math to generate code for teachers
### GET: return adminGenCode.html
@app.route("/codeGen", methods=["GET", "POST"])
def codeGen():
    ### GET
    if request.method == "GET" and session["adminIn"] == True:
        return render_template("adminGenCode.html", code="")
    ### POST
    if request.method == "POST" and session["adminIn"] == True:
        totalnum = (int)(request.form["numOfDel"])
        if not totalnum == 0:
            firstnum = int(totalnum % 10)
            secondnum = int(totalnum / 10)
            genfirst = math.ceil((firstnum + 10) * 3)
            gensecond = math.ceil((secondnum + 10) * 3)
            return render_template("adminGenCode.html", code=(str(gensecond) + "IMDB" + str(genfirst) + "XM"))
        return render_template("adminGenCode.html", code="")


### /adminAddNew (POST -> templateRendered)
### add new committee, path to adminAddNew
### POST: two parts, first is committee creation, second is assignment creations
@app.route("/adminAddNew", methods=["POST"])
def adminAddNew():
    ### POST
    if request.method == "POST" and session["adminIn"] == True:
        value = request.form["Button"]

        ### Create committee ###
        if value == "create":
            typeCom = request.form.get("typeOfCom")
            com = request.form["committee"]
            x = request.form["number"]
            for num in range(0,int(x)):
                db.execute("INSERT INTO generalList (committee, country, country_id, delegate_name, delegate_school, typeOfCom, room, Important) VALUES(:com, :con, :idx, :delNam, :delSch, :typeCom, :room, :imp)",
                com=com, con="", idx=num, delNam="", delSch="", typeCom=typeCom, room ="", imp="No")
            countries = db.execute("SELECT * FROM generalList WHERE committee=:com", com=com)
            return render_template("adminAddNew.html", second=True, countries=countries)

        ### Create assignments ###
        if value == "populate":
            countries = db.execute("SELECT * FROM generalList WHERE country=''")
            for country in countries:
                y = str(country["id"])
                x = request.form.get(y)
                z = "I"+ y
                if request.form.get(z) != None:
                    print("inside first if")
                    db.execute("UPDATE generalList SET country=:con, Important= :T WHERE id=:idx", con=x, idx=int(y), T="Yes")
                else:
                    print("inside else")
                    db.execute("UPDATE generalList SET country=:con WHERE id=:idx", con=x, idx=int(y))
            idArange("generalList")
            return returnAdminPage("", None)
    return returnAdminPage("", None)


### /adminAddNewCon (POST -> templateRendered)
### path to adminAddNewCon, add new assignments to existing committee
### POST: two stages, first gets info from committee, second creates the assignments
@app.route("/adminAddNewCon", methods=["POST"])
def adminAddNewCon():
    ### POST
    if request.method == "POST" and session["adminIn"] == True:
        value = request.form["Button"]

        ### Get info from committee ###
        if value == "create":
            com = session["addNewComitteeCom"]
            comList = db.execute("SELECT * FROM generalList WHERE committee=:com", com=com)
            typeOfCom = comList[0]["typeOfCom"]
            roomAvailable = comList[0]["room"]
            x = request.form["numOfCon"]
            for num in range(0,int(x)):
                if roomAvailable == "":
                    db.execute("INSERT INTO generalList (committee, country, country_id, delegate_name, delegate_school, typeOfCom, room) VALUES(:com, :con, :idx, :delNam, :delSch, :typeCom, :room)",
                    com=com, con="", idx=num, delNam="", delSch="", typeCom=typeOfCom, room="")
                else:
                    db.execute("INSERT INTO generalList (committee, country, country_id, delegate_name, delegate_school, typeOfCom, room) VALUES(:com, :con, :idx, :delNam, :delSch, :typeCom, :room)",
                    com=com, con="", idx=num, delNam="", delSch="", typeCom=typeOfCom, room=roomAvailable)
            countries = db.execute("SELECT * FROM generalList WHERE committee=:com AND country=''", com=com)
            return render_template("adminAddNewCon.html", second=True, countries=countries)

        ### Create assignments ###
        if value == "populate":
            countries = db.execute("SELECT * FROM generalList WHERE country='' AND committee=:com", com=session["addNewComitteeCom"])
            for country in countries:
                y = str(country["id"])
                x = request.form.get(y)
                if request.form.get("I"+y):
                    db.execute("UPDATE generalList SET country=:con, Important= :T WHERE id=:idx", con=x, idx=int(y), T="Yes")
                else:
                    db.execute("UPDATE generalList SET country=:con WHERE id=:idx", con=x, idx=int(y))
            idArange("generalList")
            return returnAdminPage("", None)
    return returnAdminPage("", None)


### /specialFunctions (POST GET -> templateRendered)
### route to /specialFunctions,
### POST: code for the special functions
### GET: reutrn returnAdminSpecialFUnctions()
### !!! implement flash info and improve functions
@app.route("/specialFunctions", methods=["GET", "POST"])
def specialFunctions():
    ### GET
    if request.method == "GET" and session["adminIn"] == True:
        return returnAdminSpecialFunctions()
    ### POST
    elif request.method == "POST" and session["adminIn"] == True:
        # button value to determin function to call
        value = request.form["Button"]

        ### Code to get list of all table names of program
        dbList = []
        for table in db.execute("SELECT name FROM sqlite_master WHERE type = 'table'"):
            dbList.append(table["name"])
        dbList.remove("users")
        dbList.remove("generalList")
        dbList.remove("sqlite_sequence")

        ### Delete all the information ###
        if value == "DeleteAll":
            for table in dbList:
                db.execute("DROP TABLE :table", table=table)
            db.execute("DELETE FROM generalList")
            db.execute("DELETE FROM users")

        ### Delete all the info in generalList(countries, committies delegate data) ###
        elif value == "DeleteAllCountryInfo":
            db.execute("DELETE FROM generalList")

        ### Delete all the user's tables, users in user table, and delegate info in generalList ###
        elif value == "DeleteAllUserTables":
            for table in dbList:
                db.execute("DROP TABLE :table", table=table)
            db.execute("DELETE FROM users")
            db.execute("UPDATE generalList SET delegate_name='', delegate_school=''")

        ### Delete all delegate info in generalList ###
        elif value == "DeleteAllDelegateInfo":
            db.execute("UPDATE generalList SET delegate_name='', delegate_school=''")

        ### Delete all room data from committees ###
        elif value == "WhipeAllRooms":
            db.execute("UPDATE generalList SET room =''")

        ### Delete all the committee data in generalList
        elif value == "DeleteEntireCommittee":
            com = request.form.get("committeeDropDown")
            db.execute("DELETE FROM generalList WHERE committee=:com", com=com)
        return returnAdminSpecialFunctions()


### /editRow (POST -> templateRendered)
### path to editRow
### POST: edit the assignment information as specified
@app.route("/editRow", methods=["POST"])
def editRow():
    ### POST
    if request.method == "POST" and session["adminIn"] == True:
        currentValues = db.execute("SELECT * FROM generalList WHERE id=:idx", idx=int(request.form["Button"]))
        currentValue = currentValues[0]
        # use .get() because value might be None or not there
        if request.form.get("Important") == "on":
            db.execute("UPDATE generalList SET committee=:com, country=:con, delegate_name=:delName, delegate_school=:delSchool, Important=:imp WHERE id=:idx"
            ,com=request.form["committee"], con=request.form["country"], delName=request.form["delegateName"], delSchool=request.form["delegateSchool"], idx=int(request.form["Button"]), imp="Yes")
            flash("The following has changed: {} = {} , {} = {} , {} = {} , {} = {} , {} = {} .".format(currentValue["committee"],request.form["committee"],currentValue["country"],request.form["country"],currentValue["delegate_name"],
            request.form["delegateName"],currentValue["delegate_school"],request.form["delegateSchool"], currentValue["Important"], "Yes"))
        else:
            db.execute("UPDATE generalList SET committee=:com, country=:con, delegate_name=:delName, delegate_school=:delSchool, Important=:imp WHERE id=:idx"
            ,com=request.form["committee"], con=request.form["country"], delName=request.form["delegateName"], delSchool=request.form["delegateSchool"], idx=int(request.form["Button"]), imp="No")
            flash("The following has changed: {} = {} , {} = {} , {} = {} , {} = {} , {} = {} .".format(currentValue["committee"],request.form["committee"],currentValue["country"],request.form["country"],currentValue["delegate_name"],
            request.form["delegateName"],currentValue["delegate_school"],request.form["delegateSchool"], currentValue["Important"], "No"))
        if not currentValue["delegate_name"] == "":
            db.execute("UPDATE :table SET committee=:com, country=:con, delegateName=:dn WHERE committee=:committee AND country=:country",
            table=currentValue["delegate_school"], com=request.form["committee"], con=request.form["country"], dn =request.form["delegateName"], committee=currentValue["committee"], country=currentValue["country"])
        return returnAdminPage("", None)


### /editRowUser (POST -> templateRendered)
### path to edirRowUser
### POST: edit a user information !!!
@app.route("/editRowUser", methods=["POST"])
def editRowUser():
    ### POST
    if request.method == "POST" and session["adminIn"] == True:
        currentValues = db.execute("SELECT * FROM users WHERE id=:idx", idx=request.form["Button"])
        currentValue = currentValues[0]
        db.execute("UPDATE users SET email=:email, password=:passw, confirmationCode=:cc WHERE id=:idx",
        email=request.form["email"], passw=request.form["password"], cc=request.form["ConfCode"], idx=request.form["Button"])
        users = db.execute("SELECT * FROM users")
        flash("The following has changed: {} = {} , {} = {} , {} = {} .".format(currentValue["email"],request.form["email"],currentValue["password"],request.form["password"],currentValue["confirmationCode"],request.form["ConfCode"]))
        return render_template("adminUsers.html",users=users)


### /editRowUserFromUserTable (POST -> templateRendered)
### path to editRowUserFromUserTable, edit user information in users table
### POST: edit the user information as specified in users table !!!
@app.route("/editRowUserFromUserTable", methods=["POST"])
def editRowUserFRomUserTable():
    if request.method == "POST" and session["adminIn"] == True:
        currentValues = db.execute("SELECT * FROM :table WHERE id=:idx",table=session["currentEditTable"], idx=request.form["Button"])
        currentValue = currentValues[0]
        db.execute("UPDATE :table SET committee=:com, country=:con, delegateName=:dn WHERE id=:idx",
        table=session["currentEditTable"], com=request.form["committee"], con=request.form["country"], dn=request.form["delegateName"], idx=request.form["Button"])
        db.execute("UPDATE generalList SET delegate_name=:dn WHERE committee=:com AND country=:con",
        dn=request.form["delegateName"], com=request.form["committee"], con=request.form["country"])
        row = db.execute("SELECT * FROM :name", name=session["currentEditTable"])
        flash("The following has changed: {} = {} , {} = {} , {} = {} .".format(currentValue["committee"],request.form["committee"],currentValue["country"],request.form["country"],currentValue["delegateName"],request.form["delegateName"]))
        return render_template("adminEditeRowUserTable.html", users=row)


### /editRowUserTable (POST -> templateRendered)
### path to editRowUserTable
### POST: !!!
@app.route("/editRowUserTable", methods=["POST"])
def editRowUserTable():
    if request.method == "POST" and session["adminIn"] == True:
        value = request.form["Button"]
        listValue = value[0:3]
        if (listValue == "DE_"):
            deleteInfo = value[3:]
            curentDels = db.execute("SELECT * FROM :table WHERE id=:idx", table=session["currentEditTable"], idx=int(deleteInfo))
            curentDel = curentDels[0]
            db.execute("UPDATE generalList SET delegate_name='', delegate_school='' WHERE committee=:com AND country=:con",
            com=curentDel["committee"], con=curentDel["country"])
            db.execute("DELETE FROM :table WHERE id=:idx", table=session["currentEditTable"], idx=int(deleteInfo))

            users = db.execute("SELECT * FROM :table", table=session["currentEditTable"])
            flash("The following committee/country has been deleted from the teacher and stripped of delegate information: {} / {} .".format(curentDel["committee"],curentDel["country"]))
            return render_template("adminEditeRowUserTable.html",users=users)
        elif (listValue == "ED_"):
            edit = value[3:]
            row = db.execute("SELECT * FROM :table WHERE id=:idx", table=session["currentEditTable"], idx=int(edit))
            return render_template("adminEditeRowUserFromUserTable.html", rows=row)

        row = db.execute("SELECT * FROM :name", name=session["currentEditTable"])
        return render_template("adminEditeRowUserTable.html", users=row)


### /adminUsers (POST -> templateRendered)
### path to adminUsers, buttons in the teacher information table with all the teachers
### POST: two types, delete teacher and edit teacher info
@app.route("/adminUsers", methods=["POST"])
def adminUsers():
    ### POST
    if request.method == "POST" and session["adminIn"] == True:
        value = request.form["Button"]
        listValue = value[0:3]

        ### Delete teacher row(teacher) ###
        if (listValue == "DE_"):
            deleteInfo = value[3:]
            curentUsers = db.execute("SELECT * from users WHERE id=:idx", idx=int(deleteInfo))
            currentUser = curentUsers[0]
            tableName = makeUser(currentUser["personName"], currentUser["school"])
            currentValues = db.execute("SELECT * FROM :table", table=tableName)
            for assignment in currentValues:
                db.execute("UPDATE generalList SET delegate_name='', delegate_school='' WHERE committee=:com AND country=:con",
                com=assignment["committee"], con=assignment["country"])
            db.execute("DROP TABLE :table", table=tableName)
            db.execute("DELETE FROM users WHERE id=:idx", idx=int(deleteInfo))
            users = db.execute("SELECT * FROM users")
            flash("The table of {} from school {} has been deleted, her info wiped and all her assignments destroyed.".format(currentUser["personName"], currentUser["school"]))
            return render_template("adminUsers.html",users=users)

        ### Edit teacher row(teacher) ###
        elif (listValue == "ED_"):
            edit = value[3:]
            row = db.execute("SELECT * FROM users WHERE id=:idx", idx=int(edit))
            return render_template("adminEditeRowUser.html", rows=row)
        # return the adminUser.html with all the teachers tables
        users = db.execute("SELECT * FROM users")
        return render_template("adminUsers.html",users=users)


### /adminUserTables (POST -> templateRendered)
### path to adminUserTables
### POST: !!!
@app.route("/adminUserTables", methods=["POST"])
def adminUserTables():
    if request.method == "POST" and session["adminIn"] == True:
        value = request.form["Button"]
        listValue = value[0:3]
        if (listValue == "ED_"):
            print("entered if good")
            edit = value[3:]
            print("before session")
            session["currentEditTable"] = edit
            print("before db call")
            row = db.execute("SELECT * FROM :name", name=edit)
            return render_template("adminEditeRowUserTable.html", users=row)

        users = db.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        users.pop(0)
        users.pop(0)
        users.pop(0)
        return render_template("adminUserTable.html", users=users)


### /manualRegister (POST GET -> templateRendered)
### path to manualRegister, button in admin page
### POST: two part, first is get teacher, committee, and room info, second is add assignment to teacher table
### GET: return adminManualRegister.html with teachers and committees
@app.route("/manualRegister", methods=["GET", "POST"])
def manualRegister():
    ### GET
    if request.method == "GET" and session["adminIn"] == True:
        users = db.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        users.pop(0)
        users.pop(0)
        users.pop(0)
        lista = []
        committees = db.execute("SELECT committee FROM generalList WHERE delegate_name=''")
        for committee in committees:
            if not committee in lista:
                lista.append(committee)
        return render_template("adminManualRegister.html", teachers=users, committees=lista)
    ### POST
    elif request.method == "POST" and session["adminIn"] == True:
        value = request.form["Button"]
        if value == "next":
            session["addingTeacher"] = request.form.get("toTeacher")
            session["manualCommittee"] = request.form["committee"]
            committees = db.execute("SELECT * FROM generalList WHERE committee=:com AND delegate_name=''", com=session["manualCommittee"])
            session["manualAddingRoom"] = committees[0]["room"]
            return render_template("adminManualRegister.html", second=True, countries=committees, teachers=[{'name':session["addingTeacher"]}], committees=[{'committee':session["manualCommittee"]}])

        if value == "assign":
            db.execute("UPDATE generalList SET delegate_name = 'taken', delegate_school = :school WHERE committee=:com AND country = :con",
            school=session["addingTeacher"], com=session["manualCommittee"], con=request.form.get("country"))
            if session["manualAddingRoom"] == "":
                db.execute("INSERT INTO :tableName (committee, country, delegateName, room) VALUES(:committee, :country, :delNam, :room)",
                tableName=session["addingTeacher"], committee=session["manualCommittee"], country=request.form.get("country"), delNam="", room="")
            else:
                db.execute("INSERT INTO :tableName (committee, country, delegateName, room) VALUES(:committee, :country, :delNam, :room)",
                tableName=session["addingTeacher"], committee=session["manualCommittee"], country=request.form.get("country"), delNam="", room=session["manualAddingRoom"])
            flash("You have assigned {} {} to {} .".format(session["manualCommittee"],request.form.get("country"),session["addingTeacher"]))
            return returnAdminPage("", None)


### /adminStats (GET -> templateRendered)
### path to adminStats, only gives information
### GET: return number of assignments available and total by type
@app.route("/adminStats", methods=["GET"])
def adminStats():
    ### GET
    if request.method == "GET" and session["adminIn"] == True:

        ### Assignments available ###
        hsenA = maxTypeInGen("HS EN", "No")
        hsspA = maxTypeInGen("HS SP", "No")
        msenA = maxTypeInGen("MS EN", "No")
        msspA = maxTypeInGen("MS SP", "No")
        mseniA = maxTypeInGen("MS EN", "Yes")
        hseniA = maxTypeInGen("HS EN", "Yes")
        msspiA = maxTypeInGen("MS SP", "Yes")
        hsspiA = maxTypeInGen("HS SP", "Yes")
        totalA = hsenA + hsspA + msenA + msspA + mseniA + hseniA + msspiA + hsspiA

        ### Assignments total ###
        hsenT = maxAssignInGen("HS EN", "No")
        hsspT = maxAssignInGen("HS SP", "No")
        msenT = maxAssignInGen("MS EN", "No")
        msspT = maxAssignInGen("MS SP", "No")
        mseniT = maxAssignInGen("MS EN", "Yes")
        hseniT = maxAssignInGen("HS EN", "Yes")
        hsspiT = maxAssignInGen("HS SP", "Yes")
        msspiT = maxAssignInGen("MS SP", "Yes")
        totalT = hsenT + hsspT + msenT + msspT + mseniT + hseniT + msspiT + hsspiT
        # return the template with data
        return render_template("adminStats.html", hsenA=hsenA,hsspA=hsspA,msenA=msenA,msspA=msspA,hsenT=hsenT,
        hsspT=hsspT,msspT=msspT,msenT=msenT,totalT=totalT, totalA=totalA, mseniA=mseniA, hseniA=hseniA, mseniT=mseniT,
        hseniT=hseniT, msspiA=msspiA, hsspiA=hsspiA, msspiT=msspiT, hsspiT=hsspiT)


### /printCommittee (POST GET -> templateRendered)
### path to printCommittee
### POST: admin print committee
### GET: teacher print their list of assignments
@app.route("/printCommittee", methods=["POST", "GET"])
def printCommittee():
    ### GET (teacher print)
    if request.method == "GET" and session["adminIn"] == True:
        lista = []
        committees = db.execute("SELECT committee FROM generalList WHERE delegate_name=''")
        for committee in committees:
            if not committee in lista:
                lista.append(committee)
        return render_template("printCommittee.html", first=True, second=False, committees=lista)
    ### POST (admin print)
    elif request.method == "POST" and session["adminIn"] == True:
        countries = db.execute("SELECT * FROM generalList WHERE committee=:com", com=request.form.get("committeeDropDown"))
        return render_template("printCommittee.html", first=False, second=True, committee=request.form.get("committeeDropDown"), users=countries, room=countries[0]["room"])


### /changeRooms (POST -> templateRendered)
### path to changeRooms
### POST: change the room info of committees in generalList and teacher tables
@app.route("/changeRooms", methods=["POST"])
def changeRooms():
    ### POST
    if request.method == "POST" and session["adminIn"] == True:
        # get all the committees
        lista = []
        committees = db.execute("SELECT committee FROM generalList")
        for committee in committees:
            if not committee in lista:
                lista.append(committee)

        listRooms = []
        for committee in lista:
            b = [committee["committee"] , request.form[committee["committee"]]]
            listRooms.append(b)
            db.execute("UPDATE generalList SET room=:room WHERE committee=:com", room=request.form[committee["committee"]], com=committee["committee"])
        users = db.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        users.pop(0)
        users.pop(0)
        users.pop(0)
        for user in users:
            for com in listRooms:
                db.execute("UPDATE :table SET room=:room WHERE committee=:com",table=user["name"], room=com[1], com=com[0])
        lista = []
        listb = []
        committees = db.execute("SELECT * FROM generalList")
        for committee in committees:
            if not committee["committee"] in lista:
                lista.append(committee["committee"])
                listb.append(committee)
        flash("Rooms have been successfully changed.")
        return render_template("adminChangeRooms.html", users=listb)



###############################################################################################################################################################
###############################################################################################################################################################
#####################################################    ERROR HANDLERS      ##################################################################################
###############################################################################################################################################################
###############################################################################################################################################################

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template("errorPage.html", number="404"), 404

@app.errorhandler(405)
def error405(e):
    # note that we set the 404 status explicitly
    return render_template("errorPage.html", number="405"), 405

@app.errorhandler(403)
def error403(e):
    # note that we set the 404 status explicitly
    return render_template("errorPage.html", number="403"), 403

@app.errorhandler(500)
def error500(e):
    # note that we set the 404 status explicitly
    return render_template("errorPage.html", number="500"), 500

@app.errorhandler(502)
def error502(e):
    # note that we set the 404 status explicitly
    return render_template("errorPage.html", number="502"), 502



if __name__ == "__main__":
	app.run()
	debug=True
    # Made by JP Garcia
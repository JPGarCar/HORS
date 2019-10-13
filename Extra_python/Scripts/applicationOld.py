#!/usr/bin/python

# import multiple packeges
from cs50 import SQL
from flask import Flask, redirect, render_template, request, url_for, session, flash, send_file
from random import *
import math
from raven.contrib.flask import Sentry

### imports used for the word document creation
#from docx import Document
#from docx.shared import Inches, RGBColor, Pt
#from docxtpl import DocxTemplate

# defines variable 'app' to the flask
app = Flask(__name__)
app.secret_key = "immunsasfm2018"
if session:
    session.clear()
    session.pop('_flashes', None)

# assigns variable 'db' to the SQL database immuns.db
db = SQL("sqlite:///immuns.db")

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


## simple method that re arranges the id's of the coutnries in a user or a table
def idArange(user):
    countries = db.execute("SELECT * FROM :user", user=user)
    x = 1
    for country in countries:
        db.execute("UPDATE :user SET id=:idx WHERE id=:firstID", user=user, idx=x, firstID=country["id"])
        x = x + 1


### method that gets the number from the inputed special code, gets the first two chars of the string and the char 6 and 7 to use,
### these must be numbers then do simple arithmatic to find the number
def getSpecial(string):
    ## gets the chars
    first = string[0:2]
    second = string[6:8]
    # tries to convert the chars to ints, if not possible then the special code is wrong and return None
    try:
        value = int(first)
    except ValueError:
        return None
    try:
        value = int(second)
    except ValueError:
        return None
    # simple arithmetic to find the number
    if int(first) >= 0 and int(second) >= 0:
        finalOne = (int(first)/3)-10
        finalTwo = (int(second)/3)-10
        return (finalOne*10) + finalTwo
    return None

### Gets the number of countries in a specific user table
def maxNumInDBUser(user):
    x = 0
    # grabs the entire table of the user
    spots = db.execute("SELECT * FROM generalList WHERE typeOfCom = :user AND delegate_name='' ", user=user)
    # iterates over all the countries in the table adding one to the variable x
    for spot in spots:
        x = x + 1
    # returns the number of countries in the table
    return x

def maxNumInDBUserTotal(user):
    x = 0
    # grabs the entire table of the user
    spots = db.execute("SELECT * FROM generalList WHERE typeOfCom = :user", user=user)
    # iterates over all the countries in the table adding one to the variable x
    for spot in spots:
        x = x + 1
    # returns the number of countries in the table
    return x


def maxNumInDBUserUser(user):
    x = 0
    # grabs the entire table of the user
    spots = db.execute("SELECT * FROM :users", users=user)
    # iterates over all the countries in the table adding one to the variable x
    for spot in spots:
        x = x + 1
    # returns the number of countries in the table
    return x

### Randomly assigns a country or a number of countries to current user's table from the database specified, HSEN, HSSo, MSEN, MSSP
def randomCountry(number, typeOfCom):
    # iterates until all the assignments pending are assigned
    x = 1
    while number > 0:
        # grabs the number of countries on the table
        maxNumInDBNow = maxNumInDBUser(typeOfCom)
        # assigns a random number
        for i in range(0,x):
            codeID = randint(1, maxNumInDBNow)
        # grabs all the countries of that type of committee and puts it as a list in stem
        stem = db.execute("SELECT * FROM generalList WHERE delegate_name='' AND typeOfCom = :typeOfCom", typeOfCom=typeOfCom)
        # stoop becomes the country from the list stem in the index of codeID
        stoop = stem[codeID]
        # it is assigned to the current user and information is updated in the general table and the specific country table
        if not stoop["room"] == "":
            db.execute("INSERT INTO :tableName (committee, country, delegateName, room) VALUES(:committee, :country, :delNam, :room)",
            tableName=session["currentUser"], committee=stoop["committee"], country=stoop["country"], delNam="", room=stoop["room"])
        else:
            db.execute("INSERT INTO :tableName (committee, country, delegateName, room) VALUES(:committee, :country, :delNam, :room)",
            tableName=session["currentUser"], committee=stoop["committee"], country=stoop["country"], delNam="", room="")

        #updates the general list
        db.execute("UPDATE generalList SET delegate_name='taken', delegate_school =:school WHERE committee=:com AND country=:con",
        school=session["currentUser"], com=stoop["committee"] ,con=stoop["country"])
        # reduces the number of pedning assignments by one
        number = number - 1
        x = x + 1

### Gets the information of the current user like the email, password etc.
def getDicCurUser():
    using = db.execute("SELECT * FROM users WHERE id=:idx", idx=session["currentUserId"])
    for use in using:
        return use

### returns the template userPageOld.html with the corresponding data from the current user's table
def returnUserPageOld():
    users = db.execute("SELECT * FROM :user", user=session["currentUser"])
    return render_template("userPageOld.html", users=users)

### return the admin template
def returnAdminPage(user, error):
    lista = []
    lista.append("None")
    committees = db.execute("SELECT committee FROM generalList")
    for committee in committees:
        if not committee in lista:
            lista.append(committee)
    if user == "":
        users = db.execute("SELECT * FROM generalList")
    else:
        users=user
    return render_template("admin.html", users=users, committees=lista, error=error)

### return the admin template
def returnAdminSpecialFunctions():
    lista = []
    lista.append("None")
    committees = db.execute("SELECT committee FROM generalList")
    for committee in committees:
        if not committee in lista:
            lista.append(committee)
    return render_template("adminSpecialFunctions.html", committees=lista)

### checks if there are still countries available to assign in a specific table
def stillAvailable(typeOfCom):
    count = 0
    stoop = db.execute("SELECT * FROM generalList WHERE delegate_name = :name AND typeOfCom = :typeOfCom", name="", typeOfCom=typeOfCom)
    if stoop == None:
        return False
    else:
        return True
    # for step in stoop:
    #     count = count + 1
    # if count > 0:
    #     return True
    # else:
    #     return False

### produces a unique user id from its name and school without any special characters
def makeUser(name, school):
    return replaceSpecial(name) + replaceSpecial(school)

### strips a string from special characters
def replaceSpecial(string):
    string = string.replace(" ", "")
    string = string.replace("_", "")
    string = string.replace("-", "")
    string = string.replace("'", "")
    string = string.replace(".", "")
    return string

###############################################################################################################################################################
###############################################################################################################################################################
#######################################################  Routes for main Page   ###############################################################################
###############################################################################################################################################################
###############################################################################################################################################################


### main route to the sign in page, when GET returns the registration template, when POST signs in a user
@app.route("/", methods = ["GET", "POST"])
def registration():
    ### GET
    if request.method == "GET":
        return render_template("registration.html")

    ### POST
    elif request.method == "POST":
        session["currentUser"] = None
        # check if the info is the admin console info
        if request.form["signInEmail"] == "admin@gmail.com" and request.form["signInPassword"] == "adminPassword":
            session["adminIn"] = True
            return returnAdminPage("", None)

        # grabs the user from table users with the inputed email and password from the input fields
        rows = db.execute("SELECT * FROM users WHERE email = :email AND password = :password",
                email=request.form["signInEmail"], password=request.form["signInPassword"])
        # loops over the user, if there is no user it will not enter the loop and return the same page
        for user in rows:
            if user["personName"] != "":
                # assigns the global variable 'currentUser'  to the users name + _ + the school
                session["currentUser"] = makeUser(user["personName"], user["school"])
                session["currentUserId"] = user["id"]
                # variable "special" has the number from sepcial code
                special = getSpecial(user["confirmationCode"])
                # assigns 'numRem' the number of delegates remainging by subtracting the max delegates with current delgates in the table
                numNow = maxNumInDBUserUser(session["currentUser"])
                # if there are delegates in the table equal to the max then go to user page old
                if numNow == special:
                    return returnUserPageOld()
                # else then go to get more delgates
                else:
                    numRem = special - numNow
                    return render_template("userPageNew.html", user=user, numRem=int(numRem))
        flash("You have entered an incorrect email or password, please try again. If the problem persists, call your HOSPITALITY member for asistance.")
        return render_template("registration.html")


### signUp reoute, when GET returns the signUp template, when POST checks if all fields are filled and correct in the sign up template
@app.route("/signUp", methods = ["POST", "GET"])
def signUp():
    ### GET
    if request.method == "GET":
        return render_template("signUp.html")

    ### POST
    elif request.method == "POST":
        # checks if the confirmation code is a valid code using getSpecial() if not vaild then return the same page
        if getSpecial(request.form["confirmationCode"]) == None:
            flash("You have entered an incorrect confirmation code.")
            flash("Please enter a valid confirmation code, if the problem persists, contact your HOSPITALITY member.")
            return render_template("signUp.html")
        # if true, continue checking the email not to be repeted
        else:
            # grabs all the users from table users and loops
            maybe = db.execute("SELECT email FROM users")
            email = request.form["email"]
            for may in maybe:
                # checks to see if the email inputed is already in use, if true then return signUpEmail template showing the user error
                if may == email:
                    flash("The email you have entered is already in use. If you do not remember your password please contact your HOSPITALITY member.")
                    return render_template("signUp.html")

            if not request.form["password"] == request.form["password_second"]:
                print("password dont match")
                flash("The passwords that you have entered do not match, please try again.")
                return render_template("signUp.html")
            # if not true we continue to adding the new user to the user table
            db.execute("INSERT INTO users (personName, email, school, password, confirmationCode) VALUES(:name, :email, :school, :password, :confCode)",
                    name=request.form["personName"], email=request.form["email"], school=request.form["school"], password=request.form["password"],
                    confCode=request.form["confirmationCode"])
            # creates the table for the new user
            db.execute("CREATE TABLE :tableName ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 'committee' TEXT, 'country' TEXT, 'delegateName' TEXT, 'room' TEXT)"
                        , tableName=makeUser(request.form["personName"], request.form["school"]))
            # return template signUpSuccess
            return render_template("signUpSuccess.html")


@app.route("/signOut", methods=["POST"])
def signOut():
    if request.method == "POST" and not session["currentUser"] == None:
        if session:
            session.clear()
        return render_template("registration.html")

### signUpSuccess route, when POST returnes the user to registration template, when GET retunrs the signUpSuccess template
@app.route("/signUpSuccess", methods = ["POST", "GET"])
def signUpSuccess():
    ### GET
    if request.method == "POST":
        return render_template("registration.html")

    ### POST
    else:
        return render_template("signUpSuccess.html")



### userPageNew route, for the new users that need to select the number of delegates for each section only has POST
@app.route("/userPageNew", methods = ["POST"])
def userPageNew():
    ### POST
    if request.method == "POST" and not session["currentUser"] == None:
        # assigns the number of delegates requested in each variable
        if request.form["MSE"] == "":
            MSE = 0
        else :
            MSE = int(request.form["MSE"])
        if request.form["MSS"] == "":
            MSS = 0
        else :
            MSS = int(request.form["MSS"])
        if request.form["HSE"] == "":
            HSE = 0
        else :
            HSE = int(request.form["HSE"])
        if request.form["HSS"] == "":
            HSS = 0
        else :
            HSS = int(request.form["HSS"])
        # assings to 'number' the number of requested delegates plus hom many delegates are already in the user table
        number = MSE + MSS + HSE + HSS + maxNumInDBUserUser(session["currentUser"])
        # grabs the current user table and checkes to see if the confirmation code gives the same number of requested delegates
        rows = db.execute("SELECT confirmationCode FROM users WHERE id = :ids", ids=session["currentUserId"])
        for row in rows:
            target = getSpecial(row['confirmationCode'])
        # if true, goes over all the requested delegates checkes if there are still missing of such type and that there are remeaining
        # if true, then calls randomCountry() to assign the country
        if  number <= target:
            if MSE != 0 and stillAvailable("MS EN"):
                randomCountry(MSE, "MS EN")
            if MSS != 0 and stillAvailable("MS SP"):
                randomCountry(MSS, "MS SP")
            if HSE != 0 and stillAvailable("HS EN"):
                randomCountry(HSE, "HS EN")
            if HSS != 0 and stillAvailable("HS SP"):
                randomCountry(HSS, "HS SP")
            # checks to see if the the max num of delegates has been reached, if true returnUserPageOld()
            if number == target:
                return returnUserPageOld()
            # if not true, then return the same page with the number of assignments remeaining
        num = target - maxNumInDBUserUser(session["currentUser"])
        flash("You have entered an incorrect number of assignemnts, please try again you have {} assignments remaining.".format(num))
        return render_template("userPageNew.html", user = session["currentUser"], numRem = num)

    flash("An error was encountered please log in again. If the error persists call your HOSPITALITY member.")
    return render_template("registration.html")



### goTo route, takes to the singUp template used after the user registers only has POST for button click
@app.route("/goTo", methods = ["POST"])
def goTo():
    ### GET
    return render_template("signUp.html")


### user page old route, when POST the name of the student is updated if there is anything in the input bar, if there is nothing the
### name stays as taken if the request is GET the program returns the userPageOld()
@app.route("/userPageOld", methods = ["POST", "GET"])
def userPageOld():
    ### POST
    if request.method == "POST" and not session["currentUser"] == None:
        # gets all the delegates from the table of the currentUser
        delegates = db.execute("SELECT * FROM :user", user=session["currentUser"])
        for delegate in delegates:
            # asigns y the delegate ID in the table that corresponds to the ID of the input bar
            y = str(delegate["id"])
            # uses the corresponding ID of the deleagte to get the info from the input bar
            x = request.form[y]
            # checks if the input bar has a valid name input or not
            if x == "" or x == " ":
                # name is put to 'taken'
                db.execute("UPDATE :user SET delegateName='' WHERE id=:idx", user=session["currentUser"], idx=delegate["id"])
            else:
                # name is updated to the input string from the bar
                db.execute("UPDATE :user SET delegateName=:name WHERE id=:idx", user=session["currentUser"], name=x, idx=delegate["id"])
            # update the name of the delegate in the general list of all countries
            db.execute("UPDATE generalList SET delegate_name=:name WHERE committee=:com AND country=:coun", name=x, com=delegate["committee"],
            coun=delegate["country"])
        # return the user page old with returnUserPageOld()
        flash("The names have been changed as requested.")
        return returnUserPageOld()

    ### GET
    elif request.method == "GET" and not session["currentUser"] == None:
        return returnUserPageOld()


@app.route("/userDownload", methods=["POST"])
def userDownload():
    if request.method == "POST" and not session["currentUser"] == None:
        schools = db.execute("SELECT school FROM users WHERE id = :idx", idx=session["currentUserId"])
        school = schools[0]
        assignments = db.execute("SELECT * FROM :table", table=session["currentUser"])
        return render_template("printAssignments.html", school=school["school"], users=assignments)

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


### admin console route
@app.route("/adminOne", methods=["POST", "GET"])
def adminOne():

    if request.method == "GET" and session["adminIn"] == True:
        return returnAdminPage("", None)

    if request.method == "POST" and session["adminIn"] == True:

        session["admingCurrentTable"] = ""
        value = request.form["Button"]
        if value == "MS":
            users = db.execute("SELECT * FROM generalList WHERE typeOfCom = 'MS EN' OR typeOfCom = 'MS SP'")
            session["admingCurrentTable"] = " AND (typeOfCom = 'MS EN' OR typeOfCom = 'MS SP')"
            error = "MS"
            return returnAdminPage(users, error)
        elif value == "HS":
            users = db.execute("SELECT * FROM generalList WHERE typeOfCom = 'HS EN' OR typeOfCom = 'HS SP'")
            session["admingCurrentTable"] = " AND (typeOfCom = 'HS EN' OR typeOfCom = 'HS SP')"
            error = "HS"
            return returnAdminPage(users, error)
        elif value == "ALL":
            session["admingCurrentTable"] = ""
            return returnAdminPage("", None)
        elif value == "English":
            users = db.execute("SELECT * FROM generalList WHERE typeOfCom = 'HS EN' OR typeOfCom = 'MS EN'")
            session["admingCurrentTable"] = " AND (typeOfCom = 'HS EN' OR typeOfCom = 'MS EN')"
            error = "English"
            return returnAdminPage(users, error)
        elif value == "Spanish":
            users = db.execute("SELECT * FROM generalList WHERE typeOfCom = 'HS SP' OR typeOfCom = 'MS SP'")
            session["admingCurrentTable"] = " AND (typeOfCom = 'HS SP' OR typeOfCom = 'MS SP')"
            error = "Spanish"
            return returnAdminPage(users, error)
        elif value == "HSEN":
            users = db.execute("SELECT * FROM generalList WHERE typeOfCom = 'HS EN'")
            session["admingCurrentTable"] = " AND typeOfCom = 'HS EN'"
            error = "HS EN"
            return returnAdminPage(users, error)
        elif value == "HSSP":
            users = db.execute("SELECT * FROM generalList WHERE typeOfCom = 'HS SP'")
            session["admingCurrentTable"] = " AND typeOfCom = 'HS SP'"
            error = "HS SP"
            return returnAdminPage(users, error)
        elif value == "MSEN":
            users = db.execute("SELECT * FROM generalList WHERE typeOfCom = 'MS EN'")
            session["admingCurrentTable"] = " AND typeOfCom = 'MS EN'"
            error = "MS EN"
            return returnAdminPage(users, error)
        elif value == "MSSP":
            users = db.execute("SELECT * FROM generalList WHERE typeOfCom = 'MS SP'")
            session["admingCurrentTable"] = " AND typeOfCom = 'MS SP'"
            error = "MS SP"
            return returnAdminPage(users, error)
        elif value == "Users":
            users = db.execute("SELECT * FROM users")
            return render_template("adminUsers.html",users=users)
        elif value == "UsersTable":
            users = db.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
            users.pop(0)
            users.pop(0)
            users.pop(0)
            return render_template("adminUserTable.html", users=users)
        elif value == "GenerateCode":
            return render_template("adminGenCode.html", code="")
        elif value == "changeRooms":
            lista = []
            listb = []
            committees = db.execute("SELECT * FROM generalList")
            for committee in committees:
                if not committee["committee"] in lista:
                    lista.append(committee["committee"])
                    listb.append(committee)
            return render_template("adminChangeRooms.html", users=listb)
        elif value == "AddNewCom":
            return render_template("adminAddNew.html")
        elif value == "AddNewCon":
            com = request.form.get("toCommitteeDropDown")
            session["addNewComitteeCom"] = com
            return render_template("adminAddNewCon.html", committee=com)
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
        elif value == "DeleteBulkRow":
            rowIds = request.form.getlist("Selected")
            for row in rowIds:
                currentInfos = db.execute("SELECT * FROM generalList WHERE id=idx", idx=row)
                currentInfo = currentInfos[0]
                flash("The following committe/country has been deleted: {} / {}".format(currentInfo["committee"],currentInfo["country"]))
                db.execute("DELETE FROM generalList WHERE id=:idx", idx=row)
            idArange("generalList")
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
        listValue = value[0:3]
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
        elif (listValue == "Ed_"):
            edit = value[3:]
            row = db.execute("SELECT * FROM generalList WHERE id=:idx", idx=int(edit))
            return render_template("adminEditeRow.html", rows=row)
        elif (listValue == "DR_"):
            deleteRow = value[3:]
            currentInfos = db.execute("SELECT * FROM generalList WHERE id=:idx", idx=int(deleteRow))
            currentInfo = currentInfos[0]
            flash("The following committe/country has been deleted: {} / {}".format(currentInfo["committee"],currentInfo["country"]))
            db.execute("DELETE FROM generalList WHERE id=:idx", idx=int(deleteRow))
            idArange("generalList")
            return returnAdminPage("", None)

        return returnAdminPage("", None)

### code generator route adminGenCode
@app.route("/codeGen", methods=["GET", "POST"])
def codeGen():
    if request.method == "GET" and session["adminIn"] == True:
        return render_template("adminGenCode.html", code="")

    if request.method == "POST" and session["adminIn"] == True:
        totalnum = (int)(request.form["numOfDel"])
        if not totalnum == 0:
            firstnum = int(totalnum % 10)
            secondnum = int(totalnum / 10)
            genfirst = math.ceil((firstnum + 10) * 3)
            gensecond = math.ceil((secondnum + 10) * 3)
            return render_template("adminGenCode.html", code=(str(gensecond) + "IMDB" + str(genfirst) + "XM"))
        return render_template("adminGenCode.html", code="")

### add new committee, path to adminAddNew
@app.route("/adminAddNew", methods=["POST"])
def adminAddNew():
    if request.method == "POST" and session["adminIn"] == True:
        value = request.form["Button"]
        if value == "create":
            typeCom = request.form.get("typeOfCom")
            com = request.form["committee"]
            x = request.form["number"]
            for num in range(0,int(x)):
                db.execute("INSERT INTO generalList (committee, country, country_id, delegate_name, delegate_school, typeOfCom, room) VALUES(:com, :con, :idx, :delNam, :delSch, :typeCom, :room)",
                com=com, con="", idx=num, delNam="", delSch="", typeCom=typeCom, room ="")
            countries = db.execute("SELECT * FROM generalList WHERE committee=:com", com=com)
            return render_template("adminAddNew.html", second=True, countries=countries)

        if value == "populate":
            countries = db.execute("SELECT * FROM generalList WHERE country=''")
            for country in countries:
                y = str(country["id"])
                x = request.form.get(y)
                db.execute("UPDATE generalList SET country=:con WHERE id=:idx", con=x, idx=int(y))

            return returnAdminPage("", None)

    return returnAdminPage("", None)

### add new countries to existing committee, path to adminAddNewCon
@app.route("/adminAddNewCon", methods=["POST"])
def adminAddNewCon():
    if request.method == "POST" and session["adminIn"] == True:
        value = request.form["Button"]
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

        if value == "populate":
            countries = db.execute("SELECT * FROM generalList WHERE country='' AND committee=:com", com=session["addNewComitteeCom"])
            for country in countries:
                y = str(country["id"])
                x = request.form.get(y)
                db.execute("UPDATE generalList SET country=:con WHERE id=:idx", con=x, idx=int(y))
            return returnAdminPage("", None)

    return returnAdminPage("", None)

@app.route("/specialFunctions", methods=["GET", "POST"])
def specialFunctions():
    if request.method == "GET" and session["adminIn"] == True:
        return returnAdminSpecialFunctions()

    elif request.method == "POST" and session["adminIn"] == True:
        value = request.form["Button"]
        dbList = []
        for table in db.execute("SELECT name FROM sqlite_master WHERE type = 'table'"):
            dbList.append(table["name"])
        dbList.remove("users")
        dbList.remove("generalList")
        dbList.remove("sqlite_sequence")

        if value == "DeleteAll":
            for table in dbList:
                db.execute("DROP TABLE :table", table=table)
            db.execute("DELETE FROM generalList")
            db.execute("DELETE FROM users")

        elif value == "DeleteAllCountryInfo":
            db.execute("DELETE FROM generalList")

        elif value == "DeleteAllUserTables":
            for table in dbList:
                db.execute("DROP TABLE :table", table=table)
            db.execute("DELETE FROM users")

        elif value == "DeleteAllDelegateInfo":
            db.execute("UPDATE generalList SET delegate_name='', delegate_school=''")

        elif value == "WhipeAllRooms":
            db.execute("UPDATE generalList SET room =''")

        elif value == "DeleteEntireCommittee":
            com = request.form.get("committeeDropDown")
            db.execute("DELETE FROM generalList WHERE committee=:com", com=com)

        return returnAdminSpecialFunctions()


@app.route("/editRow", methods=["POST"])
def editRow():
    if request.method == "POST" and session["adminIn"] == True:
        currentValues = db.execute("SELECT * FROM generalList WHERE id=:idx", idx=request.form["Button"])
        currentValue = currentValues[0]
        db.execute("UPDATE generalList SET committee=:com, country=:con, delegate_name=:delName, delegate_school=:delSchool WHERE id=:idx"
        ,com=request.form["committee"], con=request.form["country"], delName=request.form["delegateName"], delSchool=request.form["delegateSchool"], idx=request.form["Button"])
        if not currentValue["delegate_name"] == "":
            db.execute("UPDATE :table SET committee=:com, country=:con, delegateName=:dn WHERE committee=:committee AND country=:country",
        table=currentValue["delegate_school"], com=request.form["committee"], con=request.form["country"], dn =request.form["delegateName"], committee=currentValue["committee"], country=currentValue["country"])
        flash("The following has changed: {} = {} , {} = {} , {} = {} , {} = {} .".format(currentValue["committee"],request.form["committee"],currentValue["country"],request.form["country"],currentValue["delegate_name"],request.form["delegateName"],currentValue["delegate_school"],request.form["delegateSchool"]))
        return returnAdminPage("", None)

@app.route("/editRowUser", methods=["POST"])
def editRowUser():
    if request.method == "POST" and session["adminIn"] == True:
        currentValues = db.execute("SELECT * FROM users WHERE id=:idx", idx=request.form["Button"])
        currentValue = currentValues[0]
        db.execute("UPDATE users SET email=:email, password=:passw, confirmationCode=:cc WHERE id=:idx",
        email=request.form["email"], passw=request.form["password"], cc=request.form["ConfCode"], idx=request.form["Button"])
        users = db.execute("SELECT * FROM users")
        flash("The following has changed: {} = {} , {} = {} , {} = {} .".format(currentValue["email"],request.form["email"],currentValue["password"],request.form["password"],currentValue["confirmationCode"],request.form["ConfCode"]))
        return render_template("adminUsers.html",users=users)


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



@app.route("/adminUsers", methods=["POST"])
def adminUsers():
    if request.method == "POST" and session["adminIn"] == True:
        value = request.form["Button"]
        listValue = value[0:3]
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
        elif (listValue == "ED_"):
            edit = value[3:]
            row = db.execute("SELECT * FROM users WHERE id=:idx", idx=int(edit))
            return render_template("adminEditeRowUser.html", rows=row)

        users = db.execute("SELECT * FROM users")
        return render_template("adminUsers.html",users=users)


@app.route("/adminUserTables", methods=["POST"])
def adminUserTables():
    if request.method == "POST" and session["adminIn"] == True:
        value = request.form["Button"]
        listValue = value[0:3]
        print("before the if")
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

@app.route("/manualRegister", methods=["GET", "POST"])
def manualRegister():
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

@app.route("/adminStats", methods=["GET"])
def adminStats():
    if request.method == "GET" and session["adminIn"] == True:
        hsenA = maxNumInDBUser("HS EN")
        hsspA = maxNumInDBUser("HS SP")
        msenA = maxNumInDBUser("MS EN")
        msspA = maxNumInDBUser("MS SP")
        totalA = hsenA + hsspA + msenA + msspA
        hsenT = maxNumInDBUserTotal("HS EN")
        hsspT = maxNumInDBUserTotal("HS SP")
        msenT = maxNumInDBUserTotal("MS EN")
        msspT = maxNumInDBUserTotal("MS SP")
        totalT = hsenT + hsspT + msenT + msspT
        return render_template("adminStats.html", hsenA=hsenA,hsspA=hsspA,msenA=msenA,msspA=msspA,hsenT=hsenT,hsspT=hsspT,msspT=msspT,msenT=msenT,totalT=totalT, totalA=totalA)

@app.route("/printCommittee", methods=["POST", "GET"])
def printCommittee():
    if request.method == "GET" and session["adminIn"] == True:
        lista = []
        committees = db.execute("SELECT committee FROM generalList WHERE delegate_name=''")
        for committee in committees:
            if not committee in lista:
                lista.append(committee)
        return render_template("printCommittee.html", first=True, second=False, committees=lista)

    elif request.method == "POST" and session["adminIn"] == True:
        countries = db.execute("SELECT * FROM generalList WHERE committee=:com", com=request.form.get("committeeDropDown"))
        return render_template("printCommittee.html", first=False, second=True, committee=request.form.get("committeeDropDown"), users=countries, room=countries[0]["room"])


@app.route("/changeRooms", methods=["POST"])
def changeRooms():
    if request.method == "POST" and session["adminIn"] == True:
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
    # Made by JP Garcia
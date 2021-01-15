from flask import Flask, redirect, render_template, request, url_for, session, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from app import db
from models import Teacher, Committee, Assignment, Delegate
import helpers
from typeOfCommittee import TypeOfCom
from Important import Important
from advanced import Advanced
from random import *

###############################################################################################################################################################
###############################################################################################################################################################
#########################################################  Functions   ########################################################################################
###############################################################################################################################################################
###############################################################################################################################################################



### randomCountry (Number String String Teacher -> Void)
### Randomly assigns assignments to current user's table as specified
def randomCountry(number, typeOfCom, important, teacher, advanced):
    # used to have different iterations of the random function to be more random
    ranNum = 1
    numAssign = number
    # iterates until all the assignments pending are assigned
    while numAssign > 0:
        # number of countries as specified in generalList
        maxNumInDBNow = stillAvailable(typeOfCom, important, advanced)
        # assigns a random number to "codeID", -1 because list starts at 0
        if maxNumInDBNow == 1:
            codeID = 0;
        else:
            for i in range(0,ranNum):
                codeID = randint(0, maxNumInDBNow - 1)
        # all assignments of type of committee and importance and advanced
        assignments = db.session.query(Assignment).join(Committee).filter(Committee.typeOfCom == typeOfCom, Assignment.delegate == None, Assignment.important == important, Committee.advanced == advanced).all()
        # assignment from assignemnts in index "codeID"
        assignment = assignments[codeID]
        # assignment assigned to current user and its table updated
        delegate = Delegate(" ", assignment.id, teacher.id, "")
        db.session.add(delegate)
        # reduces number of pedning assignments by one
        numAssign = numAssign - 1
        # increase the numer of iterations of random
        ranNum = ranNum + 1
    db.session.commit()



### stillAvailable (String String String -> Number)
### return number of available assignemnts of typeOfCom and imporatnce and advanced
def stillAvailable(typeOfCom, important, advanced):
    # grab count of query and return
    return db.session.query(Assignment).join(Committee).filter(Committee.typeOfCom == typeOfCom, Assignment.delegate == None, Assignment.important == important, Committee.advanced == advanced).count()

### idArange (String -> Void)
### string can be name of user or table
### simple method that re arranges the id's of the coutnries in a user or a table
# def idArange(user):
#     # grab all rows in table
#     countries = user.query.all()
#     # first id number
#     x = 1
#     # over all the rows, update its id to "x"                       !!! This might not work due to reshufle of primary key used for relationships
#     for country in countries:
#         country.id = x
#         db.session.commit()
#         x = x + 1

### maxAssignInGen (String String String -> Number)
### return number of total assignments of type and importance and advanced
def maxAssignInGen(typee, important, advanced):
    # grabs all assignemnts
    return db.session.query(Assignment).join(Committee).filter(Committee.typeOfCom == typee, Assignment.important == important, Committee.advanced == advanced).count()


### returnAdminPage ( -> templateRendered)
### return the admin template
def returnAdminPage(assignments, serchParam):
    cList = getComDropDownOpt()
    # grab all assignemnts from generalList if current assignemnts is empty string
    if assignments == "":
        assignments = Assignment.query.all()
    else:
        assignments=assignments
    # return admin.html with assignemnts as rows, sList as committees for drop down and serchParam as flash message
    return render_template("admin.html", assignments=assignments, committees=cList, error=serchParam)


### getComDropDownOpt (Void -> (listof String))
### return list of all committie names
def getComDropDownOpt():
    return Committee.query.order_by(Committee.name.asc()).all()


### returnAdminSpecialFunctions (Void -> templateRendered)
### return the special functions admin tempalate
def returnAdminSpecialFunctions():
    sList = getComDropDownOpt()
    return render_template("admin_specialFunctions.html", committees=sList)


### no return, delete all assignments given and its corresponding delegate if applicable
def deleteAssignments(assignments):
    for assignment in assignments:
        if assignment.delegate is not None:
            db.session.delete(assignment.delegate)
        db.session.delete(assignment)
    db.session.commit()
    checkAutoCommitteeDelete()

### no return, delete assignment given and its corresponding delegate if applicable
def deleteAssignment(assignment):
    if assignment.delegate is not None:
        db.session.delete(assignment.delegate)
    db.session.delete(assignment)
    db.session.commit()
    checkAutoCommitteeDelete()


### check all committees to see if it should auto delete  ### NOT BEING USED
def checkAutoCommitteeDelete():
    committees = Committee.query.all()
    for committee in committees:
        if committee.numOfAssignments() == 0 and committee.numOfImportantAssignments() == 0:
            db.session.delete(committee)
            flash("The following committee got deleted due to having no assignments: {}  {}".format(committee.name, committee.typeOfCom))
    db.session.commit()

### render the user_newTeacherPage.html
def renderNewTeacherPage(teacher, numRem):
    # regular assignments
    MSEAvailable = stillAvailable(TypeOfCom.MSEN.value, Important.NO.value, Advanced.NO.value)
    HSEAvailable = stillAvailable(TypeOfCom.HSEN.value, Important.NO.value, Advanced.NO.value)
    MSSAvailable = stillAvailable(TypeOfCom.MSSP.value, Important.NO.value, Advanced.NO.value)
    HSSAvailable = stillAvailable(TypeOfCom.HSSP.value, Important.NO.value, Advanced.NO.value)

    # important assignemnts
    MSEIAvailable = stillAvailable(TypeOfCom.MSEN.value, Important.YES.value, Advanced.NO.value)
    HSEIAvailable = stillAvailable(TypeOfCom.HSEN.value, Important.YES.value, Advanced.NO.value)
    MSSIAvailable = stillAvailable(TypeOfCom.MSSP.value, Important.YES.value, Advanced.NO.value)
    HSSIAvailable = stillAvailable(TypeOfCom.HSSP.value, Important.YES.value, Advanced.NO.value)

    # advanced assignments
    MSEAAvailable = stillAvailable(TypeOfCom.MSEN.value, Important.NO.value, Advanced.YES.value)
    MSSAAvailable = stillAvailable(TypeOfCom.MSSP.value, Important.NO.value, Advanced.YES.value)
    HSEAAvailable = stillAvailable(TypeOfCom.HSEN.value, Important.NO.value, Advanced.YES.value)
    HSSAAvailable = stillAvailable(TypeOfCom.HSSP.value, Important.NO.value, Advanced.YES.value)

    # advanced and important assignemnts
    MSEAIAvailable = stillAvailable(TypeOfCom.MSEN.value, Important.YES.value, Advanced.YES.value)
    MSSAIAvailable = stillAvailable(TypeOfCom.MSSP.value, Important.YES.value, Advanced.YES.value)
    HSEAIAvailable = stillAvailable(TypeOfCom.HSEN.value, Important.YES.value, Advanced.YES.value)
    HSSAIAvailable = stillAvailable(TypeOfCom.HSSP.value, Important.YES.value, Advanced.YES.value)

    # grade 6 assignments
    G6HSAvailable = stillAvailable(TypeOfCom.G6EN.value, Important.NO.value, Advanced.NO.value)

    availability = {"MSEA" : MSEAvailable, "HSEA" : HSEAvailable, "MSSA" : MSSAvailable, "HSSA" : HSSAvailable,
                        "MSEIA" : MSEIAvailable, "HSEIA" : HSEIAvailable, "MSSIA" : MSSIAvailable, "HSSIA" : HSSIAvailable,
                        "MSEAA" : MSEAAvailable, "MSSAA" : MSSAAvailable, "HSEAA" : HSEAAvailable, "HSSAA" : HSSAAvailable, "G6EN" : G6HSAvailable,
                        "MSEAIA" : MSEAIAvailable, "MSSAIA" : MSSAIAvailable, "HSEAIA" : HSEAIAvailable, "HSSAIA" : HSSAIAvailable
    }

    return render_template("user_newTeacherPage.html", teacher=teacher, numRem=int(numRem), availability=availability)

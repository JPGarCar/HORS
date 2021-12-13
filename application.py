#!/usr/bin/python
from __future__ import annotations
from random import choice
from string import ascii_uppercase

from flask import Flask, redirect, render_template, request, url_for, session, flash
from flask_bootstrap import Bootstrap
from flask_security import SQLAlchemyUserDatastore, Security, roles_required, login_user, login_required
from flask_security.utils import verify_password, hash_password, logout_user
from math import ceil

from forms import TypeOfCommitteeForm
from models import Teacher, Committee, Assignment, Delegate, TypeOfCommittee, db, User, Role
import helpers
from env_secrets import SECRET_KEY, SECURITY_PASSWORD_SALT

application = app = Flask(__name__)
application.secret_key = SECRET_KEY
application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
application.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///immuns.db"
application.config["SQLALCHEMY_ECHO"] = False
application.config["DEBUG"] = True
application.config["SECURITY_PASSWORD_SALT"] = SECURITY_PASSWORD_SALT

bootstrap = Bootstrap(application)
db.init_app(application)
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(application, user_datastore)

# if there is any session data on the users computer then clear it
if session:
    session.clear()
    session.pop('_flashes', None)


def return_admin_page(assignments, search_parm: str | None):
    cList = Committee.get_committee_dropdown()
    # grab all assignemnts from generalList if current assignemnts is empty string
    if assignments is None:
        assignments = Assignment.query.all()
    # return admin.html with assignemnts as rows, sList as committees for drop down and serchParam as flash message
    return render_template("admin.html", assignments=assignments, committees=cList, error=search_parm)


@application.before_first_request
def application_init():
    db.create_all()
    user_datastore.find_or_create_role(name='teacher', description='A teacher from any school')
    admin_role = user_datastore.find_or_create_role(name='admin', description='An admin taking care of the application.')
    admin = user_datastore.get_user('admin@gmail.com')
    if not admin:
        admin = user_datastore.create_user(email='admin@gmail.com', password=hash_password('adminPassword'))
    else:
        admin.password = hash_password('adminPassword')
    user_datastore.add_role_to_user(admin, admin_role)
    db.session.commit()


@application.route("/", methods=["GET", "POST"])
def home_page():
    """
    POST -> Sign in a user
    """
    if request.method == "POST":
        user = user_datastore.get_user(request.form["signInEmail"])

        if user and verify_password(request.form["signInPassword"], user.password):
            login_user(user)

            if user.has_role(user_datastore.find_role('admin')):
                session["adminIn"] = True
                return return_admin_page(None, None)

            teacher: Teacher = user.teacher

            # assign session variables
            session["currentUserId"] = teacher.id

            max_number_of_possible_students = teacher.max_number_of_students_possible()
            number_of_students = teacher.number_of_students()

            # if the teacher has same assignments as his code permits then go to teacher page old
            if number_of_students == max_number_of_possible_students:
                return redirect(url_for('user_oldTeacherPage'))
            # else go get more delegates
            else:
                return redirect(url_for('user_newTeacherPage'))

        else:
            flash(
                "You have entered an incorrect password, please try again. "
                "If the problem persists, call your HOSPITALITY member for asistance.")
            return redirect(url_for('home_page'))

    return render_template("home_page.html")


@application.route("/user_signUp", methods=["POST", "GET"])
def user_signUp():
    """
    POST -> Create a new teacher user
    """
    if request.method == "POST":
        # Validate confirmation code #
        # checks confirmation code validity using getSpecial() if not vaild return same page with flash error
        if helpers.getSpecial(request.form["confirmationCode"]) is None:
            flash("You have entered an incorrect confirmation code.")
            flash("Please enter a valid confirmation code, if the problem persists, contact your HOSPITALITY member.")
            return redirect(url_for('user_signUp'))

        else:
            email = request.form["email"]

            user = user_datastore.get_user(email)

            # if email inputted is already in use return same page with flash error
            if user is not None:
                flash(
                    "The email you have entered is already in use. If you do not remember your "
                    "password please contact your HOSPITALITY member.")
                return redirect(url_for('user_signUp'))

            # Check Passwords Match #
            if not request.form["password"] == request.form["password_second"]:
                flash("The passwords that you have entered do not match, please try again.")
                return redirect(url_for('user_signUp'))

            user = user_datastore.create_user(email=email, password=hash_password(request.form["password"]))
            user_datastore.add_role_to_user(user, user_datastore.find_role('teacher'))

            teacher = Teacher(
                name=request.form["personName"],
                school=request.form["school"],
                code=request.form["confirmationCode"],
                user=user
            )
            db.session.add(teacher)
            db.session.commit()

            return redirect(url_for('user_signUpSuccess'))

    return render_template("user_signUp.html")


@application.route("/user_signUpSuccess", methods=["GET"])
def user_signUpSuccess():
    return render_template("user_signUpSuccess.html")


def assign_helper(looking_for: int, type_of_committee: TypeOfCommittee,
                  is_important: bool, teacher: Teacher) -> str | None:
    """
    Will assign a country to a teacher or return a message error
    :param looking_for: number of assignments the teacher wants
    :param type_of_committee: the type of committee looking for
    :param is_important: if the assignments are important or not
    :param teacher: the teacher looking for the assignments
    :return: Error message or None
    """

    if looking_for != 0:
        number_of_assigned_assignments = teacher.give_random_assignments_for_type_of_committee(
            number_of_assignments_needed=looking_for,
            type_of_committee=type_of_committee, are_important=is_important
        )

        if number_of_assigned_assignments != looking_for:
            return "We were only able to assign " + str(
                number_of_assigned_assignments) + " " + type_of_committee.__str__() + \
                   (' Important' if is_important == 'Yes' else '') + " assignments. The remaining " + \
                   str(looking_for - number_of_assigned_assignments) + " assignments are still at your disposal."


@application.route("/user_newTeacherPage", methods=["POST", "GET"])
@roles_required('teacher')
def user_newTeacherPage():
    """
    POST -> Add assignments to the teacher
    """
    if request.method == "POST":
        # grab teacher that is signed in
        teacher = Teacher.query.get(session["currentUserId"])

        class CommitteeTypeResponse:
            def __init__(self, type_of_committee: TypeOfCommittee, regular_assignment_amount: int = 0,
                         important_assignment_amount: int = 0):
                self.type_of_committee = type_of_committee
                self.regular_assignment_amount = regular_assignment_amount
                self.important_assignment_amount = important_assignment_amount

            def get_total_count(self) -> int:
                return self.regular_assignment_amount + self.important_assignment_amount

        committee_type_responses = []
        all_committee_types: list[TypeOfCommittee] = TypeOfCommittee.query.all()

        for committee_type in all_committee_types:
            regular_assignments = request.form.get(str(committee_type.id), type=int, default=0)
            important_assignments = request.form.get('{}_important'.format(str(committee_type.id)), type=int,
                                                     default=0) if \
                committee_type.has_important_assignments else 0

            committee_type_responses.append(CommitteeTypeResponse(type_of_committee=committee_type,
                                                                  regular_assignment_amount=regular_assignments,
                                                                  important_assignment_amount=important_assignments))

        total_assignment_amount = sum(
            [response.get_total_count() for response in committee_type_responses]) + teacher.number_of_students()

        # grabs the teacher's number of students
        target = teacher.max_number_of_students_possible()

        # goes over all the requested delegates checking there are requested of such type
        # and there are remaining in generalList
        # if true, then calls randomCountry() to assign the assignment
        if total_assignment_amount == target:
            # list for possible error messages
            error_list = []

            for committee_type_response in committee_type_responses:
                error_list.append(
                    assign_helper(type_of_committee=committee_type_response.type_of_committee,
                                  looking_for=committee_type_response.regular_assignment_amount,
                                  teacher=teacher, is_important=False)
                )
                if committee_type_response.important_assignment_amount:
                    error_list.append(
                        assign_helper(type_of_committee=committee_type_response.type_of_committee,
                                      looking_for=committee_type_response.important_assignment_amount,
                                      teacher=teacher, is_important=True)
                    )

            # check error list is not empty, then return same page with flash errors, else return user_oldTeacherPage()
            # will filter the list for any None values
            error_list = list(filter(None, error_list))
            if len(error_list) > 0:
                flash("Some assignments have been added but we have some issues:")
                for error in range(0, len(error_list)):
                    flash(error_list[error])
                return redirect(url_for('user_newTeacherPage'))
            else:
                return redirect(url_for('user_oldTeacherPage'))
        else:
            # if incorrect number of assignments, return same page with number of assignments remaining
            num_rem = target - teacher.number_of_students()
            flash(
                "You have entered an incorrect number of assignments, please try again you have {} delegates to assign.".format(
                    num_rem))
            return redirect(url_for('user_newTeacherPage'))

    type_of_committees: list[TypeOfCommittee] = TypeOfCommittee.query.all()
    type_of_committees.sort(key=lambda x: x.__str__())
    teacher: Teacher = Teacher.query.get(int(session["currentUserId"]))
    num_remaining = teacher.max_number_of_students_possible() - teacher.number_of_students()

    return render_template("user_newTeacherPage.html", teacher=teacher, numRem=num_remaining,
                           type_of_committees=type_of_committees)


# /userSettingsPage (POST -> templateRendered)
# page where teachers can edit their info
@application.route("/userSettingsPage", methods=["POST", "GET"])
@roles_required('teacher')
def userSettingsPage():
    if request.method == "POST":
        teacher_id = request.form["submit"]
        teacher = Teacher.query.get(teacher_id)
        if request.form["password"] != "":
            teacher.user.password = hash_password(request.form["password"])
        teacher.user.email = request.form["email"]
        teacher.name = request.form["name"]
        teacher.school = request.form["school"]
        flash("Changes have been made successfully!")
        db.session.commit()
        return redirect(url_for('userSettingsPage'))

    teacher = Teacher.query.get(session["currentUserId"])
    return render_template("user_settingsPage.html", teacher=teacher)


# /user_oldTeacherPage (POST GET -> templateRendered)
# user page old route
# POST: name of student is updated if anything in input bar, else name stays as taken
# GET: the program returns the user_oldTeacherPage()
@application.route("/user_oldTeacherPage", methods=["POST", "GET"])
@roles_required('teacher')
def user_oldTeacherPage():
    # POST
    if request.method == "POST":
        # grab teacher that is logged in
        db_session = db.session
        teacher = db_session.query(Teacher).get(session["currentUserId"])
        db_session.add(teacher)

        # gets all assignments from table of the current teacher in session
        delegates = teacher.delegates
        for delegate in delegates:
            # assigns y the assignment ID in the table that corresponds to the ID of the input bar
            name_id = "N_" + str(delegate.id)
            # uses the nameID of the delegate to get name in html page input bar
            del_name = request.form.get(name_id, type=str).strip()
            # name is put to blank if the delegate name is blank only
            delegate.name = del_name if del_name else " "

            # use the id to get grade drop down
            grade_id = "G_" + str(delegate.id)
            del_grade = request.form.get(grade_id, type=str)
            if del_grade:
                delegate.grade = del_grade

        db_session.commit()

        # return the user page old with returnUserPageOld()
        flash("Your responses have been saved. If you want a copy of the final list, please click Download Assignments.")
        return redirect(url_for('user_oldTeacherPage'))

    teacher = Teacher.query.get(session["currentUserId"])
    return teacher.return_user_page_old()


# /userDownload (POST -> templateRendered)
# return printable html file with all the teacher's info
# POST: render user_printAssignments.html with teacher's info
@application.route("/userDownload", methods=["POST"])
@roles_required('teacher')
def userDownload():
    # grab teacher logged in
    teacher = Teacher.query.get(session["currentUserId"])
    # grabs the school name of teacher
    school = teacher.school
    # grabs all delegates of the teacher
    delegates = teacher.delegates
    # return the html file with the data
    return render_template("user_printAssignments.html", school=school, delegates=delegates)


# /logOut (POST -> templateRendred)
# similar to signOut but different unknown use
# POST: delete all session info and flashes, return home_page.html
@application.route("/logOut", methods=["POST", 'GET'])
@login_required
def logOut():
    if session:
        session.clear()
        session.pop('_flashes', None)
    logout_user()
    return redirect(url_for('home_page'))


###########################
###########################
#      Admin Pages     ####
###########################
###########################


# /adminOne (POST GET -> templateRendered)
# admin console route
# POST: check the button status and act accordingly
# GET: return returnAdminPage() for all info
@application.route("/adminOne", methods=["POST", "GET"])
@roles_required('admin')
def adminOne():
    # GET
    if request.method == "GET":
        return return_admin_page(None, None)
    # POST
    if request.method == "POST":
        application.jinja_env.globals.update(numOfAssignments=Committee.number_of_assignments)
        application.jinja_env.globals.update(numOfImportantAssignments=Committee.number_of_important_assignments)
        application.jinja_env.globals.update(numOfDelegates=Committee.number_of_delegates_assigned)
        application.jinja_env.globals.update(numOfImportantDelegates=Committee.number_of_important_delegates_assigned)
        application.jinja_env.globals.update(codeYellow=Committee.is_more_than_half_assignments_available)
        application.jinja_env.globals.update(codeRed=Committee.is_more_than_two_thirds_assignments_available)

        # value tells what button was clicked
        value = request.form["Button"]

        assignments = None
        gen_filter = None

        # General Filter Buttons #
        if value == "MS":
            assignments = db.session.query(Assignment).join(Committee).join(TypeOfCommittee).filter(
                TypeOfCommittee.level == TypeOfCommittee.Level.MIDDLESCHOOL).all()
            gen_filter = "Middle School"
        elif value == "HS":
            assignments = db.session.query(Assignment).join(Committee).join(TypeOfCommittee).filter(
                TypeOfCommittee.level == TypeOfCommittee.Level.HIGHSCHOOL).all()
            gen_filter = "High School"
        elif value == "ALL":
            return return_admin_page(assignments, gen_filter)
        elif value == "English":
            assignments = db.session.query(Assignment).join(Committee).join(TypeOfCommittee).filter(
                TypeOfCommittee.language == TypeOfCommittee.Language.ENGLISH).all()
            gen_filter = "English"
        elif value == "Spanish":
            assignments = db.session.query(Assignment).join(Committee).join(TypeOfCommittee).filter(
                TypeOfCommittee.language == TypeOfCommittee.Language.SPANISH).all()
            gen_filter = "Spanish"
        elif value == 'REHS':
            assignments = db.session.query(Assignment).join(Committee).join(TypeOfCommittee).filter(
                TypeOfCommittee.level == TypeOfCommittee.Level.HIGHSCHOOL, TypeOfCommittee.is_remote == True).all()
            gen_filter = "Remote High School"
        elif value == 'REMS':
            assignments = db.session.query(Assignment).join(Committee).join(TypeOfCommittee).filter(
                TypeOfCommittee.is_remote == True, TypeOfCommittee.level == TypeOfCommittee.Level.MIDDLESCHOOL).all()
            gen_filter = "Remote Middle School"
        elif value == "HSEN":
            assignments = db.session.query(Assignment).join(Committee).join(TypeOfCommittee).filter(
                TypeOfCommittee.level == TypeOfCommittee.Level.HIGHSCHOOL,
                TypeOfCommittee.language == TypeOfCommittee.Language.ENGLISH).all()
            gen_filter = "High School English"
        elif value == "HSSP":
            assignments = db.session.query(Assignment).join(Committee).join(TypeOfCommittee).filter(
                TypeOfCommittee.level == TypeOfCommittee.Level.HIGHSCHOOL,
                TypeOfCommittee.language == TypeOfCommittee.Language.SPANISH).all()
            gen_filter = "High School Spanish"
        elif value == "MSEN":
            assignments = db.session.query(Assignment).join(Committee).join(TypeOfCommittee).filter(
                TypeOfCommittee.level == TypeOfCommittee.Level.MIDDLESCHOOL,
                TypeOfCommittee.language == TypeOfCommittee.Language.ENGLISH).all()
            gen_filter = "Middle School English"
        elif value == "MSSP":
            assignments = db.session.query(Assignment).join(Committee).join(TypeOfCommittee).filter(
                TypeOfCommittee.level == TypeOfCommittee.Level.MIDDLESCHOOL,
                TypeOfCommittee.language == TypeOfCommittee.Language.SPANISH).all()
            gen_filter = "Middle School Spanish"
        elif value == "Taken":
            assignments = Assignment.query.filter(Assignment.delegate != None).all()
            gen_filter = "Taken"
        elif value == "NotTaken":
            assignments = Assignment.query.filter(Assignment.delegate == None).all()
            gen_filter = "Taken"

        if assignments and gen_filter:
            return return_admin_page(assignments, gen_filter)

        # Table with teachers data #
        elif value == "Teachers":
            teachers: list[Teacher] = Teacher.query.all()
            return render_template("admin_teachersTable.html", teachers=teachers)

        # Table with all delegates #
        elif value == "Delegates":
            delegates = Delegate.query.all()
            teachers = Teacher.query.order_by(Teacher.name.asc()).all()
            return render_template("admin_delegatesTable.html", delegates=delegates, teachers=teachers)

        # Table with all committees #
        elif value == "Committees":
            committees = Committee.query.order_by(Committee.name.asc()).all()
            return render_template("admin_committeeTable.html", committees=committees)

        # Generate Code #
        elif value == "GenerateCode":
            return render_template("admin_generateCode.html", code="")

        # Change room info for committees # !!! check this
        elif value == "changeRooms":
            committees = Committee.query.order_by(Committee.name.asc()).all()
            return render_template("admin_changeRooms.html", committees=committees)

        # Add new Country to committee #
        elif value == "AddNewCon":
            committee_id = int(request.form.get("toCommitteeDropDown"))
            session["addNewComitteeID"] = committee_id
            committee = Committee.query.get(committee_id)
            assignments = db.session.query(Assignment).join(Committee).filter(Committee.id == committee_id)
            return render_template("admin_addNewCountry.html", committee=committee, second=False,
                                   assignments=assignments)

        # Delete info of all selected rows(assignments) #
        elif value == "DeleteBulkInfo":
            row_ids = request.form.getlist("Selected")
            for row in row_ids:
                assignment = Assignment.query.get(int(row))
                if assignment.delegate is not None:
                    flash("The following committe/country has been stripped of delegate info: {} / {}".format(
                        assignment.committee.name, assignment.country))
                    db.session.delete(assignment.delegate)
            # commit all deletes
            db.session.commit()

        # Delete the rows(assignments) selected #
        elif value == "DeleteBulkRow":
            row_ids = request.form.getlist("Selected")
            for row in row_ids:
                assignment = Assignment.query.get(int(row))
                flash("The following committe/country and its delegate has been deleted: {} / {}".format(
                    assignment.committee.name, assignment.country))
                # if assignment is realted to delegate, must delete delegate first
                db.session.delete(assignment)
                db.session.commit()

        # Search parameters #
        elif value == "Search":
            com = request.form.get("committeeDropDown")
            message = ''
            if com == "None":
                is_committee_selected = False
                committee_id = None
            else:
                committee_id = int(com)
                is_committee_selected = True

            country_name = request.form["countryField"]
            if country_name != "":
                is_country_selected = True
            else:
                is_country_selected = False

            if request.form.get("Taken"):
                is_not_taken = True
            else:
                is_not_taken = False

            if is_committee_selected and is_country_selected and is_not_taken:
                assignments = db.session.query(Assignment).join(Committee).filter(Committee.id == committee_id,
                                                                                  Assignment.country == country_name,
                                                                                  Assignment.delegate is None, ).all()
                message = "Committee : {} , Country : {} , Not Taken".format(assignments[0].committee.name,
                                                                             country_name)
            elif not is_committee_selected and is_country_selected and is_not_taken:
                assignments = Assignment.query.filter(Assignment.country == country_name,
                                                      Assignment.delegate is None).all()
                message = "Country : {} , Not Taken".format(country_name)
            elif is_committee_selected and not is_country_selected and is_not_taken:
                assignments = db.session.query(Assignment).join(Committee).filter(Committee.id == committee_id,
                                                                                  Assignment.delegate is None).all()
                message = "Committee : {} , Not Taken".format(assignments[0].committee.name)
            elif is_committee_selected and is_country_selected and not is_not_taken:
                assignments = db.session.query(Assignment).join(Committee).filter(Committee.id == committee_id,
                                                                                  Assignment.country == country_name).all()
                message = "Committee : {} , Country : {}".format(assignments[0].committee.name, country_name)
            elif not is_committee_selected and not is_country_selected and is_not_taken:
                assignments = Assignment.query.filter(Assignment.delegate is None).all()
                message = "Not Taken"
            elif is_committee_selected and not is_country_selected and not is_not_taken:
                assignments = db.session.query(Assignment).join(Committee).filter(Committee.id == committee_id).all()
                message = "Committee : {}".format(assignments[0].committee.name)
            elif (not is_committee_selected) and is_country_selected and (not is_not_taken):
                assignments = Assignment.query.filter(Assignment.country == country_name).all()
                message = "Country : {}".format(country_name)
            else:
                assignments = Assignment.query.all()
            return return_admin_page(assignments, message)

        # Single row buttons #
        # single row buttons only care about the first three characters of button value to decide
        list_value = value[0:3]
        # Delete Information
        if list_value == "DI_":
            delete_info = value[3:]
            assignment = Assignment.query.get(int(delete_info))
            if assignment.delegate is not None:
                db.session.delete(assignment.delegate)
            db.session.commit()
            flash("The following committe/country has been stripped of delegate info: {} / {}".format(
                assignment.committee.name, assignment.country))

        # Edite Row
        elif list_value == "Ed_":
            edit = value[3:]
            assignment = Assignment.query.filter(Assignment.id == int(edit)).first()
            return render_template("admin_editAssignment.html", assignment=assignment)

        # Delete complete row
        elif list_value == "DR_":
            delete_row = value[3:]
            assignment = Assignment.query.get(int(delete_row))
            flash("The following committe/country has been deleted: {} / {}".format(assignment.committee.name,
                                                                                    assignment.country))
            db.session.delete(assignment)
            db.session.commit()

        return return_admin_page(None, None)


# goes with top function
# /admin_editAssignment (POST -> templateRendered)
# path to admin_editAssignment, will edit the assignment information, button on main admin page
# POST: edit the assignment information as specified
@application.route("/admin_editAssignment", methods=["POST"])
@roles_required('admin')
def admin_editAssignment():
    # POST
    if request.method == "POST":
        # get values from webpage
        con = request.form["country"]
        idx = int(request.form["Button"])

        # grab assignment to deal with
        assignment = Assignment.query.get(idx)

        assignment.country = con

        # use .get() because value might be None or not there
        if request.form.get("Important") == "on":
            assignment.important = True
            flash("The following has changed: {} = {} , {} = {}.".format(assignment.country, con, assignment.important,
                                                                         'Yes'))

        else:
            flash("The following has changed: {} = {} , {} = {} .".format(assignment.country, con, assignment.important,
                                                                          'No'))

        db.session.commit()
        return return_admin_page(None, None)


# /admin_generateCode (POST GET -> templateRendered)
# code generator route admin_generateCode
# POST: math to generate code for teachers
# GET: return admin_generateCode.html
@application.route("/admin_generateCode", methods=["GET", "POST"])
@roles_required('admin')
def admin_generateCode():
    # POST
    if request.method == "POST":
        totalnum = (int)(request.form["numOfDel"])
        if not totalnum == 0:
            firstnum = int(totalnum % 10)
            secondnum = int(totalnum / 10)
            genfirst = ceil((firstnum + 10) * 3)
            gensecond = ceil((secondnum + 10) * 3)
            return render_template("admin_generateCode.html", code=(
                    str(gensecond) + "".join(choice(ascii_uppercase) for x in range(4)) + str(
                genfirst) + "".join(choice(ascii_uppercase) for x in range(2))))
        return render_template("admin_generateCode.html", code="")
    return render_template("admin_generateCode.html", code="")


# /admin_addNewCommittee (POST -> templateRendered) !!! might need to add options for room, GET SHOULD USE ENUM stuff
# add new committee, path to admin_create_committee
# POST: two parts, first is committee creation, second is assignment creations
@application.route("/admin_addNewCommittee", methods=["POST", "GET"])
@roles_required('admin')
def admin_create_committee():
    # POST
    if request.method == "POST":
        value = request.form["Button"]

        # Create committee #
        if value == "create":
            type_of_committee_id = request.form.get("typeOfCom", type=int)

            type_of_committee_to_use: TypeOfCommittee | None = None

            db_session = db.session

            for type_of_committee in db_session.query(TypeOfCommittee).all():
                if type_of_committee.id == type_of_committee_id:
                    type_of_committee_to_use = type_of_committee

            if not type_of_committee_to_use:
                return return_admin_page(None, None)

            committee_name = request.form["committee"]
            committee = Committee(committee_name, type_of_committee_to_use, "", type_of_committee_to_use.is_advanced)

            db_session.add(committee)
            db_session.commit()
            session["committeeInSessionID"] = committee.id
            x = int(request.form["number"])
            session["numberOfAssignments"] = x

            return render_template("admin_addNewCommittee.html", second=True, numberOfAssignments=x,
                                   committee=committee.name, committee_type_name=type_of_committee_to_use.__str__(),
                                   type_of_committee=type_of_committee_to_use)

        # Create assignments #
        if value == "populate":
            committee_id = int(session["committeeInSessionID"])
            committee = Committee.query.get(committee_id)
            committee_amount = committee.number_of_assignments()
            for num in range(int(session["numberOfAssignments"])):
                country = request.form.get(str(num))
                important = request.form.get("I" + str(num), default=False, type=bool)
                db.session.add(Assignment(committee.id, country, committee_amount + num + 1, important))
            db.session.commit()
            return return_admin_page(None, None)

    type_of_committees: list[TypeOfCommittee] = TypeOfCommittee.query.all()
    type_of_committees.sort(key=lambda x: x.__str__())
    return render_template("admin_addNewCommittee.html", second=False, typeOfCom=type_of_committees)


# /admin_addNewCountry (POST -> templateRendered)
# path to admin_addNewCountry, add new assignments to existing committee
# POST: two stages, first gets info from committee, second creates the assignments
@application.route("/admin_addNewCountry", methods=["POST"])
@roles_required('admin')
def admin_addNewCountry():
    # POST
    if request.method == "POST":
        value = request.form["Button"]

        # Get info from committee #
        if value == "create":
            numOfCountries = int(request.form["numOfCon"])
            session["numOfCountries"] = numOfCountries
            committee = Committee.query.get(int(session["addNewComitteeID"]))
            assignments = db.session.query(Assignment).join(Committee).filter(Committee.id == committee.id)
            return render_template("admin_addNewCountry.html", second=True, numOfAssignments=numOfCountries,
                                   committee=committee, assigments=assignments)

        # Create assignments #
        if value == "populate":
            committeeID = int(session["addNewComitteeID"])
            committee = Committee.query.get(committeeID)
            committeeAmount = committee.number_of_assignments()
            for num in range(session["numOfCountries"]):
                country = request.form.get(str(num))
                important = request.form.get("I" + str(num))
                if important != None:
                    db.session.add(Assignment(committee.id, country, committeeAmount + num + 1, True))
                else:
                    db.session.add(Assignment(committee.id, country, committeeAmount + num + 1, False))
            db.session.commit()
            # idArange("generalList")
            return return_admin_page(None, None)
    return return_admin_page(None, None)


# /admin_teachersTable (POST -> templateRendered)
# path to admin_teachersTable, buttons in the teacher information table with all the teachers, edit or delete teacher info
# POST: two types, delete teacher and edit teacher info
@application.route("/admin_teachersTable", methods=["POST"])
@roles_required('admin')
def admin_teachersTable():
    # POST
    if request.method == "POST":
        value = request.form["Button"]
        listValue = value[0:3]

        # Delete teacher row(teacher) #
        if listValue == "DE_":
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

        # Edit teacher row(teacher) #
        elif listValue == "ED_":
            edit = value[3:]
            teacher = Teacher.query.filter(Teacher.id == int(edit)).first()
            return render_template("admin_teachersTableEdit.html", teacher=teacher)
        # return the adminUser.html with all the teachers tables
        teachers = Teacher.query.all()
        return render_template("admin_teachersTable.html", teachers=teachers)


# goes together with top function /admin_teachersTable
# /admin_teachersTableEdit (POST -> templateRendered)
# path to edirRowUser
# POST: edit a teacher information !!!
@application.route("/admin_teachersTableEdit", methods=["POST"])
@roles_required('admin')
def admin_teachersTableEdit():
    # POST
    if request.method == "POST":
        teacher_id = request.form["Button"]
        if teacher_id[0:2] == "NP":
            teacher = Teacher.query.get(teacher_id[3:])
            teacher.user.password = hash_password(request.form["password"])
            flash("The password has been changed succesfully to {}.".format(request.form["password"]))
        else:
            teacher = Teacher.query.get(teacher_id)
            teacher.user.email = request.form["email"]
            teacher.confirmation_code = request.form["ConfCode"]
            teacher.school = request.form["school"]
            flash(
                "The following has changed: {} = {} , {} = {} , {} = {} .".format(teacher.user.email, request.form["email"],
                                                                                  teacher.school,
                                                                                  request.form["school"],
                                                                                  teacher.confirmation_code,
                                                                                  request.form["ConfCode"]))

        db.session.commit()
        teachers = Teacher.query.all()
        return render_template("admin_teachersTable.html", teachers=teachers)


# /admin_specialFunctions (POST GET -> templateRendered)
# route to /admin_specialFunctions,
# POST: code for the special functions
# GET: reutrn returnAdminSpecialFUnctions()
# !!! implement flash info and improve functions
@application.route("/admin_specialFunctions", methods=["GET", "POST"])
@roles_required('admin')
def admin_specialFunctions():
    # POST
    if request.method == "POST":
        # button value to determin function to call
        value = request.form["Button"]
        db_session = db.session

        # Delete all the information #
        if value == "DeleteAll":
            db_session.query(Delegate).delete()
            db_session.query(Teacher).delete()
            db_session.query(Assignment).delete()
            db_session.query(Committee).delete()
            db_session.query(TypeOfCommittee).delete()

        # Delete all the info in assignment(countries, committies delegate data) #
        elif value == "DeleteAllCountryInfo":
            db_session.query(Delegate).delete()
            db_session.query(Assignment).delete()
            db_session.query(Committee).delete()

        # Delete all teachers and delegate info in assignment #
        elif value == "DeleteAllUserTables":
            db_session.query(Delegate).delete()
            db_session.query(Teacher).delete()

        # Delete all delegate info in assignment #
        elif value == "DeleteAllDelegateInfo":
            db_session.query(Delegate).delete()

        # Delete an entire committee #
        elif value == "DeleteEntireCommittee":
            committee = Committee.query.get(request.form.get("committeeDropDown", type=int))
            db_session.delete(committee)

        db_session.commit()
        return redirect('admin_specialFunctions')

    return render_template("admin_specialFunctions.html", committees=Committee.get_committee_dropdown())


# /admin_editDelegate (POST -> templateRendered)
# path to admin_editDelegate, edit teacher information in users table
# POST: edit the teacher information as specified in users table !!!
@application.route("/admin_editDelegate", methods=["POST"])
@roles_required('admin')
def admin_editDelegate():
    if request.method == "POST":
        com = request.form["committee"]
        con = request.form["country"]
        name = request.form["delegateName"]
        school = request.form["delegateSchool"]
        idx = request.form["Button"]
        password = request.form["password"]
        delegate = Delegate.query.get(idx)

        if password == "SuperAdminPassword":
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


@application.route("/admin_takeMeToDelegate", methods=["POST"])
@roles_required('admin')
def admin_takeMeToDelegate():
    if request.method == "POST":
        idx = request.form["editDelegate"]
        delegate = Delegate.query.get(int(idx))
        return render_template("admin_editDelegate.html", delegate=delegate)


# /admin_delegatesTables (POST -> templateRendered)
# path to admin_delegatesTables
# POST: !!!
@application.route("/admin_delegatesTables", methods=["POST"])
@roles_required('admin')
def admin_delegatesTables():
    if request.method == "POST":
        value = request.form["Button"]
        if value == "Search":
            teacher_school_id = request.form["schoolDropDown"]
            delegate_name = request.form["delegateName"]

            if teacher_school_id == "None" and delegate_name.strip() != "":
                delegates = Delegate.query.filter(Delegate.name.contains(delegate_name)).all()
                flash("Searching for delegate with name {}".format(delegate_name))
            elif teacher_school_id != "None" and delegate_name.strip() == "":
                delegates = db.session.query(Delegate).join(Teacher).filter(Teacher.id == teacher_school_id).all()
                schoolName = db.session.query(Teacher).filter(Teacher.id == teacher_school_id).first().school
                flash("Searching for delegate with school {}".format(schoolName))
            elif teacher_school_id != "None" and delegate_name.strip() != "":
                delegates = db.session.query(Delegate).join(Teacher).filter(Teacher.id == teacher_school_id,
                                                                            Delegate.name.contains(delegate_name))
                schoolName = db.session.query(Teacher).filter(Teacher.id == teacher_school_id).first().school
                flash("Searching for delegate with name {} in school {}".format(delegate_name, schoolName))
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


# /admin_committeeTable (POST -> templateRendered)
# path to admin_committeeTable
# POST: !!!
@application.route("/admin_committeeTable", methods=["POST"])
@roles_required('admin')
def admin_committeeTable():
    if request.method == "POST":
        value = request.form["Button"]
        listValue = value[0:3]
        if (listValue == "ED_"):
            edit = value[3:]
            committee = Committee.query.filter(Committee.id == int(edit)).first()
            return render_template("admin_editCommittee.html", committee=committee,
                                   types_of_committees=TypeOfCommittee.query.all())
        elif listValue == "DE_":
            delete = int(value[3:])
            committee = Committee.query.get(delete)
            db.session.delete(committee)
            db.session.commit()
        committees = Committee.query.all()
        return render_template("admin_committeeTable.html", committees=committees)


# /admin_editCommittee (POST -> templateRendered)
# path to admin_editCommittee, edit teacher information in users table
# POST: edit the teacher information as specified in users table !!!
@application.route("/admin_editCommittee", methods=["POST"])
@roles_required('admin')
def admin_editCommittee():
    if request.method == "POST":
        db_session = db.session

        name = request.form["committee"]
        type_of_committee_id = request.form.get("typeOfCom", type=int)

        room = request.form["room"]
        idx = request.form["Button"]
        committee: Committee = db_session.query(Committee).get(idx)

        # change type of committee if we have to
        if type_of_committee_id != committee.type_of_committee.id:
            committee.type_of_committee = db_session.query(TypeOfCommittee).get(type_of_committee_id)

        committee.name = name
        committee.room = room
        db_session.commit()

        flash("Committee changed successfully!")
        return render_template("admin_editCommittee.html", committee=committee,
                               types_of_committees=TypeOfCommittee.query.all())


@application.route("/admin_takeMeToCommittee", methods=["POST"])
@roles_required('admin')
def admin_takeMeToCommittee():
    if request.method == "POST":
        idx = request.form["editCommittee"]
        committee = Committee.query.get(int(idx))
        return render_template("admin_editCommittee.html", committee=committee,
                               types_of_committees=TypeOfCommittee.query.all())


# /admin_manualRegister (POST GET -> templateRendered)
# path to admin_manualRegister, button in admin page
# POST: two part, first is get teacher, committee, and room info, second is add assignment to teacher table
# GET: return admin_manualRegister.html with teachers and committees
@application.route("/admin_manualRegister", methods=["GET", "POST"])
@roles_required('admin')
def admin_manualRegister():
    if request.method == "POST":
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
            if teacher.can_add_delegates():
                assignment = Assignment.query.get(countryID)
                delegate = Delegate("", assignment.id, teacher.id, "")
                flash(
                    "You have assigned {} {} {} to {} .".format(committee.name, committee.type_of_committee,
                                                                assignment.country,
                                                                teacher.name))
                db.session.add(delegate)
                db.session.commit()
            else:
                flash(
                    "Unable to assign, teacher has no spots remaining, unasing another delegate or change Special Code")
                return redirect(url_for("admin_manualRegister"))

            return return_admin_page(None, None)

    teachers = Teacher.query.all()
    committees = Committee.query.all()
    return render_template("admin_manualRegister.html", teachers=teachers, committees=committees, second=False)


# /admin_stats (GET -> templateRendered)
# path to admin_stats, only gives information
# GET: return number of assignments available and total by type
@application.route("/admin_stats", methods=["GET"])
@roles_required('admin')
def admin_stats():
    # GET
    if request.method == "GET":
        committees: list[Committee] = Committee.query.all()
        type_of_committees: list[TypeOfCommittee] = TypeOfCommittee.query.all()

        # return the template with data
        return render_template("admin_stats.html", committees=committees, type_of_committees=type_of_committees)


# /admin_printCommittee (POST GET -> templateRendered)
# path to admin_printCommittee
# POST: admin print committee
# GET: teacher print their list of assignments
@application.route("/admin_printCommittee", methods=["POST", "GET"])
@roles_required('admin')
def admin_printCommittee():
    # POST (admin print)
    if request.method == "POST":
        comName = request.form.get("committeeDropDown")
        committee = Committee.query.filter(Committee.name == comName).first()
        return render_template("admin_printCommittee.html", first=False, second=True, committee=committee,
                               assignments=committee.assignments)

    lista = Committee.get_committee_dropdown()
    return render_template("admin_printCommittee.html", first=True, second=False, committees=lista)


# /admin_changeRooms (POST -> templateRendered)
# path to admin_changeRooms
# POST: change the room info of committees in generalList and teacher tables
@application.route("/admin_changeRooms", methods=["POST"])
@roles_required('admin')
def admin_changeRooms():
    # POST
    if request.method == "POST" :
        committees = Committee.query.all()
        for committee in committees:
            newRoom = request.form[str(committee.id)]
            committee.room = newRoom

        db.session.commit()
        flash("Rooms have been successfully changed.")
        return render_template("admin_changeRooms.html", committees=committees)


@application.route("/admin_create_type_of_committee", methods=['POST', 'GET'])
@roles_required('admin')
def admin_create_type_of_committee():
    form = TypeOfCommitteeForm(request.form)

    if request.method == 'POST' and form.validate():
        type_of_committee = TypeOfCommittee(
            level=form.level.data, language=form.language.data,
            is_remote=form.is_remote.data, is_advanced=form.is_advanced.data,
            has_important_assignments=form.has_important_assignments.data
        )

        db.session.add(type_of_committee)
        db.session.commit()
        flash('Type of committee {} added successfully!'.format(type_of_committee.__str__()))
        return redirect(url_for('admin_create_type_of_committee'))

    committee_types_list: list[TypeOfCommittee] = TypeOfCommittee.query.all()
    return render_template('admin_add_new_type_of_committee.html', form=form, committee_types_list=committee_types_list)


@application.route("/admin_delete_type_of_committee/<type_of_committee_id>", methods=['POST'])
@roles_required('admin')
def admin_delete_type_of_committee(type_of_committee_id):
    type_of_committee: TypeOfCommittee = TypeOfCommittee.query.get(type_of_committee_id)
    committee_list: list[Committee] = type_of_committee.committees
    for committee in committee_list:
        db.session.delete(committee)

    db.session.delete(type_of_committee)
    db.session.commit()

    return redirect(url_for('admin_create_type_of_committee'))


#   ERROR HANDLERS      #


@application.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template("_errorPage.html", number="404"), 404


@application.errorhandler(405)
def error405(e):
    # note that we set the 404 status explicitly
    return render_template("_errorPage.html", number="405"), 405


@application.errorhandler(403)
def error403(e):
    # note that we set the 404 status explicitly
    return render_template("_errorPage.html", number="403"), 403


@application.errorhandler(500)
def error500(e):
    # note that we set the 404 status explicitly
    return render_template("_errorPage.html", number="500"), 500


@application.errorhandler(502)
def error502(e):
    # note that we set the 404 status explicitly
    return render_template("_errorPage.html", number="502"), 502


if __name__ == "__main__":
    application.run()
# Made by JP Garcia

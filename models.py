from __future__ import annotations
import enum
from random import randint

from flask import render_template
from flask_security import UserMixin, RoleMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
from passlib.apps import custom_app_context as pwd_context

from grades import get_list_of_grades
from helpers import replaceSpecial, getSpecial

db: SQLAlchemy = SQLAlchemy()


class Assignment(db.Model):
    """
    When deleting an assignment, the delegate will also be deleted.
    """

    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.Text)
    country_id = db.Column(db.Integer)
    important = db.Column(db.Boolean)
    delegate = db.relationship('Delegate', backref='assignment', uselist=False, cascade='all, delete-orphan')
    committee_id = db.Column(db.Integer, db.ForeignKey("committee.id"), nullable=False)

    def __init__(self, committee_id, country, country_id, important: bool):
        self.country = country
        self.country_id = country_id
        self.important = important
        self.committee_id = committee_id


class TypeOfCommittee(db.Model):
    class Level(enum.Enum):
        HIGHSCHOOL = 'High School'
        MIDDLESCHOOL = 'Middle School'
        GRADESIX = 'Grade Six'

        def __str__(self):
            return self.name

        def __html__(self):
            return self.value

    class Language(enum.Enum):
        ENGLISH = 'English'
        SPANISH = 'Spanish'

        def __str__(self):
            return self.name

        def __html__(self):
            return self.value

    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(Enum(Level))
    language = db.Column(Enum(Language))
    is_advanced = db.Column(db.Boolean)
    has_important_assignments = db.Column(db.Boolean)
    is_remote = db.Column(db.Boolean)

    def __init__(self, level: Level, language: Language,
                 is_advanced: bool = False, has_important_assignments: bool = True, is_remote: bool = False):
        self.level = level
        self.language = language
        self.is_advanced = is_advanced
        self.has_important_assignments = has_important_assignments
        self.is_remote = is_remote

    def __str__(self):
        name = '{} {}'.format(self.level.value, self.language.value)
        if self.is_advanced:
            name = name + ' Advanced'
        if self.is_remote:
            name = name + ' Remote'

        return name

    def get_database_name(self):
        return '{} {}'.format(self.level.value, self.language.value)

    def get_amount_of_available_assignments(self) -> tuple[int, int | None]:
        """
        Get the amount of available assignments, regular and advanced.
        Can not use is, must use == in filters!
        :return: Tuple with the amount of assignments found without a delegate assigned
        """
        available_assignments: int = db.session.query(Assignment).join(Committee).filter(
            Committee.type_of_committee == self,
            Assignment.delegate == None,
            Assignment.important == False
        ).count()
        available_important_assignments: int = db.session.query(Assignment).join(Committee).filter(
            Committee.type_of_committee == self,
            Assignment.delegate == None,
            Assignment.important == True
        ).count() if self.has_important_assignments else None

        return available_assignments, available_important_assignments

    def get_amount_of_assignments(self) -> tuple[int, int | None]:
        regular_available = db.session.query(Assignment).join(Committee).filter(
            Committee.type_of_committee == self,
            Assignment.important == False,
            Committee.advanced == self.is_advanced).count()

        important_available = db.session.query(Assignment).join(Committee).filter(
            Committee.type_of_committee == self,
            Assignment.important == True,
            Committee.advanced == self.is_advanced).count()

        return regular_available, important_available

    def get_all_available_assignments(self, are_important: bool = False) -> list[Assignment] | None:
        """
        Must use == not is, in filter. is wont work!
        :param are_important:
        :return: list of available assignments
        """
        if are_important and not self.has_important_assignments:
            return None

        return db.session.query(Assignment).join(Committee).filter(Committee.type_of_committee == self,
                                                                   Assignment.delegate == None,
                                                                   Assignment.important == are_important,
                                                                   Committee.advanced == self.is_advanced).all()


class Delegate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    grade = db.Column(db.Text)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)

    def __init__(self, name, assignment, teacher: int, grade: str):
        self.name = name
        self.assignment_id = assignment
        self.teacher_id = teacher
        self.grade = grade


class RolesUsers(db.Model):
    __tablename__ = 'roles_users'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column('user_id', db.Integer(), db.ForeignKey('user.id'))
    role_id = db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary='roles_users', backref=db.backref('users', lazy='dynamic'))


class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    school = db.Column(db.Text)
    confirmation_code = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('teacher', uselist=False))
    delegates = db.relationship('Delegate', backref='teacher', lazy=True)

    def __init__(self, name, school, code, user):
        self.name = name
        self.school = school
        self.confirmation_code = code
        self.user = user

    def can_add_delegates(self):
        """
        :return: true if teacher has space for more delegates, else false
        """
        return self.number_of_students() < self.max_number_of_students_possible()

    def number_of_students(self) -> int:
        """
        :return: number of students the teacher has as, aka number of assignments
        """
        num = 0
        # grabs all assignments of user
        assignments = self.delegates
        # iterates over all the assignments in the table adding one to the variable num
        for assignment in assignments:
            num = num + 1
        return num

    def return_user_page_old(self):
        """
        :return: the rendered template user_oldTeacherPage.html with corresponding data from current user's table
        """
        delegates = self.delegates
        grades = get_list_of_grades()
        return render_template("user_oldTeacherPage.html", delegates=delegates, grades=grades)

    def get_teacher_session(self) -> str:
        """
        :return: unique user id from its name and school without any special characters
        """
        return replaceSpecial(self.name) + replaceSpecial(self.school)

    def max_number_of_students_possible(self) -> int:
        """
        :return: max amount of students possible based on the confirmation code
        """
        return getSpecial(self.confirmation_code)

    def amount_of_students_for_committee_type(self, committee_type: TypeOfCommittee, is_important: bool = False) -> int:
        """
        :param is_important: if looking for important assignments
        :param committee_type: the type of committee looking for
        :return: amount of students/assignments in a committee of the given type
        """
        return Delegate.query.join(Assignment).join(Committee).filter(
            Committee.type_of_committee_id == committee_type.id,
            Assignment.important == is_important,
            Delegate.teacher_id == self.id
        ).count()

    def give_random_assignments_for_type_of_committee(self, number_of_assignments_needed: int,
                                                      type_of_committee, are_important: bool) -> int:
        """
        Will assign this teacher given amount of assignments of the given committee type.
        :param number_of_assignments_needed: the amount of assignments to get this teacher
        :param type_of_committee: the type of committee looking for
        :param are_important: if the assignments are important
        :return: number of assignments assigned
        """
        number_of_assignments_assigned = 0

        # iterates until all the assignments pending are assigned
        while number_of_assignments_assigned < number_of_assignments_needed:
            # use the important or regular assignments based on what is needed
            assignments = type_of_committee.get_all_available_assignments(are_important=are_important)

            if len(assignments) == 0:
                return number_of_assignments_assigned

            code_id = 0
            if not len(assignments) == 1:
                for i in range(0, number_of_assignments_assigned):
                    code_id = randint(0, len(assignments) - 1)

            # assignment from assignments in index "code_id"
            assignment = assignments[code_id]

            # assignment assigned to current user and its table updated
            delegate = Delegate(" ", assignment.id, self.id, "")
            db.session.add(delegate)

            # reduces number of pending assignments by one
            number_of_assignments_assigned += 1
        db.session.commit()
        return number_of_assignments_assigned


class Committee(db.Model):
    """
    When a committee is deleted, all the assignments get deleted too!
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    type_of_committee_id = db.Column(db.Integer, db.ForeignKey('type_of_committee.id'))
    type_of_committee = db.relationship("TypeOfCommittee", backref='committees')
    room = db.Column(db.Text)
    advanced = db.Column(db.Boolean)
    assignments = db.relationship("Assignment", backref="committee", cascade='all, delete-orphan')

    def __init__(self, name, type_of_committee: TypeOfCommittee, room, advanced):
        self.name = name
        self.type_of_committee = type_of_committee
        self.room = room
        self.advanced = advanced

    def __str__(self):
        return '{} {}'.format(self.name, self.type_of_committee.__str__())

    def number_of_assignments(self) -> int:
        """
        :return: number of assignments in this committee
        """
        num = 0
        for assignment in self.assignments:
            if not assignment.important:
                num = num + 1
        return num

    def number_of_important_assignments(self) -> int:
        """
        :return: number of important assignments in this committee
        """
        num = 0
        for assignment in self.assignments:
            if assignment.important:
                num = num + 1
        return num

    def number_of_delegates_assigned(self):
        """
        :return: number of assignments with a delegate in this committee
        """
        num = 0
        for assignment in self.assignments:
            if not assignment.important and assignment.delegate is not None:
                num = num + 1
        return num

    def number_of_important_delegates_assigned(self):
        """
        :return: number of important assignments with a delegate in this committee
        """
        num = 0
        for assignment in self.assignments:
            if assignment.important and assignment.delegate is not None:
                num = num + 1
        return num

    def is_more_than_half_assignments_available(self, is_important):
        """
        :param is_important: true if looking for important assignments only
        :return: true if there are more assignments available than delegates in the committee by half
        """

        if is_important:
            return self.number_of_important_assignments() - self.number_of_important_delegates_assigned() >= \
                   self.number_of_important_assignments() / 2
        else:
            return self.number_of_assignments() - self.number_of_delegates_assigned() >= \
                   self.number_of_assignments() / 2

    def is_more_than_two_thirds_assignments_available(self, is_important):
        """
        :param is_important: true if looking for important assignments only
        :return: true if there are more assignments available than delegates in the committe by two thirds
        """
        if is_important:
            return self.number_of_important_assignments() - self.number_of_important_delegates_assigned() >= \
                   self.number_of_important_assignments() * 0.6
        else:
            return self.number_of_assignments() - self.number_of_delegates_assigned() >= \
                   self.number_of_assignments() * 0.6

    @staticmethod
    def get_committee_dropdown():
        return Committee.query.order_by(Committee.name.asc()).all()

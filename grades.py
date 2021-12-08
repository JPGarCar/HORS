from enum import Enum


class Grades(Enum):
    SIXTH = "6th Grade"
    SEVENTH = "7th Grade"
    EIGHTH = "8th Grade"
    NINGTH = "9th Grade"
    TENTH = "10th Grade"
    ELEVENTH = "11th Grade"
    TWELVTH = "12th Grade"


# return the list of all possible grades plus an empty string at the beginning
def get_list_of_grades():
    enum_list = list(map(lambda c: c.value, Grades))
    return enum_list

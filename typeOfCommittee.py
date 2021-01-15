from enum import Enum


# if you add a type of committee you also need update the search params and the available and random country helpers
class TypeOfCom(Enum):
    HSEN = "HS EN"
    MSEN = "MS EN"
    HSSP = "HS SP"
    MSSP = "MS SP"
    G6EN = "G6 EN"

    @staticmethod
    def to_string(typeOfCom):
        if typeOfCom == 'HS EN':
            return 'High School English'
        elif typeOfCom == 'MS EN':
            return 'Middgle School English'
        elif typeOfCom == 'HS SP':
            return 'High School Spanish'
        elif typeOfCom == 'MS SP':
            return 'Middle School Spanish'
        else:
            return '6th Grade English'

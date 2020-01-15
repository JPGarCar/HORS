from enum import Enum

# if you add a type of committee you also need update the search params and the available and random country helpers
class TypeOfCom(Enum):
    HSEN = "HS EN"
    MSEN = "MS EN"
    HSSP = "HS SP"
    MSSP = "MS SP"
    G6EN = "G6 EN"
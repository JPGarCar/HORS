from models import TypeOfCommittee

HSEN = TypeOfCommittee(level=TypeOfCommittee.Level.HIGHSCHOOL,
                       language=TypeOfCommittee.Language.ENGLISH)
MSEN = TypeOfCommittee(level=TypeOfCommittee.Level.MIDDLESCHOOL,
                       language=TypeOfCommittee.Language.ENGLISH)
HSSP = TypeOfCommittee(level=TypeOfCommittee.Level.HIGHSCHOOL,
                       language=TypeOfCommittee.Language.SPANISH)
MSSP = TypeOfCommittee(level=TypeOfCommittee.Level.MIDDLESCHOOL,
                       language=TypeOfCommittee.Language.SPANISH)
G6EN = TypeOfCommittee(level=TypeOfCommittee.Level.GRADESIX,
                       language=TypeOfCommittee.Language.ENGLISH)
RG6EN = TypeOfCommittee(level=TypeOfCommittee.Level.GRADESIX,
                        language=TypeOfCommittee.Language.ENGLISH, is_remote=True)

HSENA = TypeOfCommittee(level=TypeOfCommittee.Level.HIGHSCHOOL,
                        language=TypeOfCommittee.Language.ENGLISH, is_advanced=True)
MSENA = TypeOfCommittee(level=TypeOfCommittee.Level.MIDDLESCHOOL,
                        language=TypeOfCommittee.Language.ENGLISH, is_advanced=True)
HSSPA = TypeOfCommittee(level=TypeOfCommittee.Level.HIGHSCHOOL,
                        language=TypeOfCommittee.Language.SPANISH, is_advanced=True)
MSSPA = TypeOfCommittee(level=TypeOfCommittee.Level.MIDDLESCHOOL,
                        language=TypeOfCommittee.Language.SPANISH, is_advanced=True)

# remote committees
REHSEN = TypeOfCommittee(level=TypeOfCommittee.Level.HIGHSCHOOL,
                         language=TypeOfCommittee.Language.ENGLISH, is_remote=True, has_important_assignments=False)
REHSSP = TypeOfCommittee(level=TypeOfCommittee.Level.HIGHSCHOOL,
                         language=TypeOfCommittee.Language.SPANISH, is_remote=True, has_important_assignments=False)
REMSEN = TypeOfCommittee(level=TypeOfCommittee.Level.MIDDLESCHOOL,
                         language=TypeOfCommittee.Language.ENGLISH, is_remote=True, has_important_assignments=False)
REMSSP = TypeOfCommittee(level=TypeOfCommittee.Level.MIDDLESCHOOL,
                         language=TypeOfCommittee.Language.SPANISH, is_remote=True, has_important_assignments=False)

TypeOfCommitteeList = [
    HSEN, HSSP, MSEN, MSSP, REHSEN, REHSSP, REMSEN, REMSSP, HSENA, HSSPA, MSENA, MSSPA, G6EN, RG6EN
]

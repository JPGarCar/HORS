from teacher import *

aguilar = Teacher("Ms. Aguilar", "aguilar@gmail.com", "1234fder", "ASFM", "IDBM23DF34")
aguilar.createClassroom()
db.session.add(aguilar)
db.session.commit()
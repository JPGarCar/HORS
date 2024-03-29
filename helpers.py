# getSpecial (String -> Number or None)
# String is a special code only
# produce number of possible assignemnts from inputed special code, or None if invalid special code
# usses first two and 6th and 7th char to get the Number
def getSpecial(string):
    # gets the chars needed
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


# replaceSpecial (String -> String)
# strips a string from special characters
def replaceSpecial(string):
    string = string.replace(" ", "")
    string = string.replace("_", "")
    string = string.replace("-", "")
    string = string.replace("'", "")
    string = string.replace(".", "")
    return string
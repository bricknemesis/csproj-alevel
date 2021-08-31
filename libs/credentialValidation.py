
import re

def validate_username(user):
    if re.fullmatch(r"^(?=[a-zA-Z0-9._]{8,20}$)(?!.*[_.]{2})[^_.].*[^_.]", user):
        return True, None
    return False, "Username must be 8-20 letters long and must not contain special characters."

def validate_name(name):
    if len(name) >= 3 and len(name) <= 25:
        return True, None
    return False, "Name must be between 3 and 25 letters long."

def validate_password(pw):
    if len(pw) >= 8 and re.search(r"\d+", pw):
        return True, None
    return False, "Password must be 8 letters long and must have atleast one number in it."

def validate_telephone(number):
    if len(number) == 11 and not re.search(r"\D", number):
        return True, None
    return False, "Phone number must be properly formatted."

def validate_address(address):
    if re.search(r"\d+|\w+|\s+", address):
        return True, None
    return False, "Address must contain a house number and text"

def validate_postcode(postcode):
    if re.fullmatch(r"BT\d+\s\d\w{2}", postcode):
        return True, None
    return False, "Check your postcode and try again"

def validate_email(input):
    if re.fullmatch(r"(?:[a-z0-9!#$%&'*+\=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])", input):
        return True, None
    return False, "E-Mail must be formatted correctly."
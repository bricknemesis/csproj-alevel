
def compile(errorMessages):
    errorString = ""
    for i in range(0, len(errorMessages)):
        prefix = i > 0 and i < len(errorMessages) - 1 and ", " or ""
        suffix = i == len(errorMessages) - 2 and " and " or i == len(errorMessages) - 1 and ". Please try again." or ""
        errorString += prefix + (i == 0 and errorMessages[i][0:1].upper() + errorMessages[i][1:] or errorMessages[i]) + suffix
    return errorString
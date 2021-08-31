
#Keir Murray
#07/05/2021

#will eventually need to refactor this lib to account for other accounts in other db tables

import string
import math
import random
import libs.dbUtil as db
import libs.emailUtil as emailUtil

def getRandomVerificationCode(length = 12):
    #todo: add check to ensure code generated is nothing we've already generated

    numLetters = math.floor(length/2)
    numNumbers = length - numLetters
    alphabet = list(string.ascii_uppercase)
    numbers = [i for i in range(0, 10)]

    ranString = "EF-"
    choicePool = []
    for i in range(1, numLetters + 1):
        choicePool.append(alphabet[random.randint(0, len(alphabet) - 1)])
    
    for i in range(1, numNumbers + 1):
        choicePool.append( str(numbers[random.randint(0, len(numbers) - 1)]) )
    
    for i in range(1, len(choicePool) + 1):
        index = random.randint(0, len(choicePool) - 1)
        ran = choicePool[index]
        ranString += ran
        del choicePool[index]
    
    return ranString


class PasswordResetSession:
    def __init__(self, email):
        self.email = email
        self.updateOurRecord()
    
    def updateOurRecord(self):
        #figure out their user id from their email
        #this also means we need a facility to prevent the same email being signed up with twice
        for record in db.retrieve("customer"):
            if record[9] == self.email:
                self.record = record
                break
        if not self.record:
            print("Email has no user attached")
    
    def sendVerificationCode(self):
        email = self.record[9]
        self.verificationCode = getRandomVerificationCode()
        #add this to their database to register it as THEIR verification code, this will expire once it has been used
        db.update("customer", self.record[0], "pendingVerificationCode", self.verificationCode)
        msg = f"""
        Hello {self.record[3]},

        We have received a request to reset your password. To make sure that it's you, please input the verification code in to our system
        so that we can help you get back on your feet.

        Code: {self.verificationCode}

        Regards,
        Elite Fitness Team
        """
        emailUtil.send_email(email, "Verification Code", msg)
    
    def resetPassword(self, inputtedCode, newPassword):
        self.updateOurRecord()
        if inputtedCode == self.record[10]:
            db.update("customer", self.record[0], "password", newPassword)
            db.update("customer", self.record[0], "pendingVerificationCode", "") #dirty hack?



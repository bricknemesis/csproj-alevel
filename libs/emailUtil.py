
import smtplib

senderAddress = "elitefitnesslisburn@gmail.com"
senderPassword = "compsci1234"

def send_email(recipientAddress, subject, msg):
    try:
        server = smtplib.SMTP("smtp.gmail.com:587")
        server.ehlo()
        server.starttls()
        server.login(senderAddress, senderPassword)
        message = f"Subject: {subject} \n\n {msg}"
        server.sendmail(senderAddress, recipientAddress, message)
        server.quit()
    except Exception as e:
        print("Email not sent. Error:", e)
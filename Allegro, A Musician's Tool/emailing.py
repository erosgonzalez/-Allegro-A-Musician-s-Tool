import smtplib as sm
import csv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#Simple Mail Transfer Protocol object to send emails
class SendEmail:
    def __init__(self, user, password, recipient, plainText, HTML, subject):
        self.user = user
        self.password = password
        self.recipient = recipient
        self.message = MIMEMultipart("alternative")
        self.message["Subject"] = subject
        self.message["From"] = self.user
        self.message["To"] = self.recipient
        part1 = MIMEText(HTML, "html")
        self.message.attach(part1)

    def Send(self):
        server = sm.SMTP("smtp.gmail.com:587")
	server.ehlo()
	server.starttls()
        server.login(self.user, self.password)
        server.sendmail(self.user, self.recipient, self.message.as_string())
        server.quit()
        print "Email sent!"

import os
import smtplib
from email.mime.text import MIMEText

server = smtplib.SMTP("smtp.yandex.com", 587)
server.starttls()
server.login("griskyy@yandex.ru", "hbdqaagcxoijlzes")
msg = MIMEText("TEST MESSAGE")
msg["Subject"] = "MESSAGECLE"
msg["From"] = "griskyy@yandex.ru"
msg["To"] = "grisky@icloud.com"

server.sendmail("griskyy@yandex.ru", "grisky@icloud.com", msg.as_string())
server.quit()
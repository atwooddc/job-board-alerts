import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os

email = "me@gmail.com"
password = "pass word pass word" # see https://support.google.com/accounts/answer/185833?hl=en on how to create a Google app password
fpath = "User/filepath/to/old/positions/file.txt"
url = "https://www.ufl.nyc/careers" # webpage to parse
name = "div" # name BeautifulSoup uses to identify relevant webpage info
id = {"class": "sqs-block html-block sqs-block-html"} # id BeautifulSoup uses to identify relevant webpage info
subject = 'UFL Careers Page Update' # email subject line

def fetch_webpage(url):
    response = requests.get(url)
    return response.text

def send_email(body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = email
    msg['To'] = email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(email, password)
        server.sendmail(email,email,msg.as_string())
        server.close()
    except:
        print("failed to send mail")

# Load previous state if it exists
if os.path.exists(fpath):
    with open(fpath, 'r') as file:
        previous_roles = file.readlines()
        previous_roles = [e.strip() for e in previous_roles]
else:
    previous_roles = ''

# Fetch the current state of the webpage
site = fetch_webpage(url)
soup = BeautifulSoup(site, 'html.parser')
entries = soup.find_all(name, id)
current_roles = [str(e.text).strip() for e in entries]

# Compare the current state with the previous state
if current_roles != previous_roles:
    changes = set(current_roles) - set(previous_roles) # roles that weren't in old version
    send_email(('\n\n').join(changes)) # send email

    # Update the previous state
    with open(fpath, 'w') as file:
        file.write(('\n').join(current_roles))

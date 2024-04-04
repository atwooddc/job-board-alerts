import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import uuid

email = "me@gmail.com"
password = "pass word pass word" # see https://support.google.com/accounts/answer/185833?hl=en on how to create a Google app password
fpath = 'User/full/path/to/project/' # crontab needs file path to be explicitly defined

def fetch_webpage(url):
    response = requests.get(url)
    return response.text

def send_email(company, body):
    msg = MIMEText(body)
    msg['Subject'] = company + ' Job Board Update'
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
        
def scrape_job_board(company, url, elem, id):
    roles_file = fpath + "txt_files/" + company + '_roles.txt'
    
    # Load previous state if it exists
    if os.path.exists(roles_file):
        with open(roles_file, 'r') as file:
            previous_roles = file.readlines()
            previous_roles = [e.strip() for e in previous_roles]
    else:
        previous_roles = ''
        
    # Fetch the current state of the webpage
    site = fetch_webpage(url)
    soup = BeautifulSoup(site, 'html.parser')
    entries = soup.find_all(elem, id)
    current_roles = [str(e.text).strip() for e in entries]

    # Compare the current state with the previous state
    if current_roles != previous_roles:
        changes = set(current_roles) - set(previous_roles) # roles that weren't in old version
        send_email(company, ('\n\n').join(changes)) # send email

        # Update the previous state
        with open(fpath, 'w') as file:
            file.write(('\n').join(current_roles))
            

scrape_job_board("UFL", 'https://www.ufl.nyc/careers', "div", {"class": "sqs-block html-block sqs-block-html"}) # company site job board
scrape_job_board("AllTrails", 'https://jobs.lever.co/alltrails', "h5", {"data-qa": "posting-name"}) # lever job board
scrape_job_board("Oklo", 'https://boards.greenhouse.io/oklo', "a", {"data-mapped": "true"}) # greenhouse job board
scrape_job_board("Snow Peak", 'https://boards.greenhouse.io/snowpeak', "a", {"data-mapped": "true"}) # greenhouse job board
# ...add add'l links to non-Workday job boards

# -------------------------------------------------

# Workday job boards
# adapted from Workday-scraper by Kartik1745 on GitHub: https://github.com/Kartik1745/Workday-scraper
try:
    with open(fpath + 'job_ids_dict.pkl', 'rb') as f:
        job_ids_dict = pickle.load(f)
except FileNotFoundError:
    job_ids_dict = {}
        
options = Options()
options.add_argument('--headless=new')
driver = webdriver.Chrome(options=options)

wait = WebDriverWait(driver, 10)

company_urls = [
    'https://patagonia.wd5.myworkdayjobs.com/PWCareers',
    # ...add add'l urls
]  

for company_url in company_urls:
    if company_url not in job_ids_dict:
        job_ids_dict[company_url] = []

new_jobs = []
for company_url in company_urls:
    jobs_to_add=[]
    company = ''.join(company_url.split('//')[1].split('.')[0])
    driver.get(company_url)
    try:
        time.sleep(2)
        wait.until(EC.presence_of_element_located((By.XPATH, '//li[@class="css-1q2dra3"]')))
        
        job_elements = driver.find_elements(By.XPATH, '//li[@class="css-1q2dra3"]')
       
        for job_element in job_elements:
            job_title_element = job_element.find_element(By.XPATH, './/h3/a')
            job_title = job_title_element.text
            location_element = job_element.find_element(By.XPATH, './/dd[@class="css-129m7dg"][preceding-sibling::dt[contains(text(),"locations")]]')
            location = location_element.text
            posted_on_element = job_element.find_element(By.XPATH, './/dd[@class="css-129m7dg"][preceding-sibling::dt[contains(text(),"posted on")]]')
            posted_on = posted_on_element.text
            job_id_element = job_element.find_element(By.XPATH, './/ul[@data-automation-id="subtitle"]/li')
            job_id = job_id_element.text
            if 'today' in posted_on.lower() or 'yesterday' in posted_on.lower():
                job_href = job_title_element.get_attribute('href')
                if job_id not in job_ids_dict[company_url]:
                    job_ids_dict[company_url].append(job_id)
                    jobs_to_add.append((job_title, job_href))
                else:
                    print(f"Job ID {job_id} already in job_ids_dict")
    
    except Exception as e:
        print(f"An error occurred while processing {company_url}: {str(e)}")
        continue
    
    for job_title, job_href in jobs_to_add:
            driver.get(job_href)
            time.sleep(1)
            job_posting_element = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@data-automation-id="job-posting-details"]')))
            redis_id = str(uuid.uuid4())
            job_info = {'company': company, 'job_title': job_title, 'location': location, 'job_href': job_href}
            new_jobs.append((company, job_title, location, job_href))
            
            
if (new_jobs):
    formatted_jobs = "\n\n".join(f"{job[1]} at {str.capitalize(job[0])} in {job[2]}, learn more @ {job[3]}" for job in new_jobs)
    send_email("Workday Job Boards Update", formatted_jobs)

with open(fpath + 'job_ids_dict.pkl', 'wb') as f:
    pickle.dump(job_ids_dict, f)
        
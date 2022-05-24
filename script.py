import requests
from bs4 import BeautifulSoup
import time
import re
import pandas as pd
import numpy as np
import random
from datetime import datetime
from datetime import timedelta
import pymysql

scraped_job_titles = []
scraped_job_locations = []
scraped_company_names = []
scraped_job_salaries = []
scraped_job_ratings = []
scraped_job_dates = []
scraped_apply_urls = []
scraped_job_descriptions = []
now = datetime.now()

# prompts that allow the user to choose job title, location and job type (full time/part time)
title = input("Enter the job title you'd like to scrape:\n")
print(title)
title = title.replace(" ", "+")
location = input("Enter the location you're searching for. To search remote only jobs, reply with 'remote':\n")
print(location)
location = location.replace(" ", "+")
job_type = input("What kind of job are you looking for? You can enter 'fulltime' or 'parttime':\n")
print(job_type)

# this loops through the top 4 pages of Indeed, which returns 60 results maximum
page = 0

# For the below: 10 = 15 listings, 20 = 30 listings, etc.
while page != 10:
    url = f"https://www.indeed.com/jobs?q={title}&l={location}&sc=0kf%3Ajt({job_type})%3B&fromage=14&start={page}"
    #print(url)
    page = page + 10

        # setup
    link = requests.get(url)
    site = BeautifulSoup(link.content, "html.parser")

    # this grabs the job titles
    job_titles = site.find_all('a', attrs={'class':'jcs-JobTitle'})
    for job in job_titles:
        scraped_job_titles.append(job.getText())

    # this grabs the job locations
    job_locations = site.find_all('div', attrs={'class':'companyLocation'})
    
    for loc in job_locations:
        scraped_job_locations.append(loc.getText())

    # this grabs the company name
    company_names = site.find_all('span', attrs={'class':'companyName'})
    
    for name in company_names:
        scraped_company_names.append(name.getText())

    # this grabs the salary

    # the salary doesn't appear in the job card if it's blank, so first we check if the element exists
    jobs_divs = site.find_all('div', attrs={'class':'slider_container'})
    

    for div in jobs_divs:
        job_salaries = div.find('div', attrs={'class':'salary-snippet-container'})
        if job_salaries:
            scraped_job_salaries.append(job_salaries.getText())
        else:
            scraped_job_salaries.append('Not shown')

    # this grabs the rating, it has a similar deal as the salary
    

    for div in jobs_divs:
        job_ratings = div.find('span', attrs={'class':'ratingNumber'})
        if job_ratings:
            scraped_job_ratings.append(job_ratings.getText())
        else:
            scraped_job_ratings.append("None")


    # this grabs the job url
    view_job_url = 'https://indeed.com'
    
    job_titles = site.find_all('a', attrs={'class':'jcs-JobTitle'})
    for job in job_titles:
        scraped_apply_urls.append(view_job_url + job['href'])

    

    # this grabs how old the job posting is
    days_spans = site.find_all('span', attrs={'class':'date'})
    
    for day in days_spans:
        day_string = day.text.strip()

        if re.findall('[0-9]+', day_string):
                parsed_day = re.findall('[0-9]+', day_string)[0]
                if 'hour' in day_string:
                    job_posted_since = str(parsed_day) + now.strftime("%m/%d/%Y") # hours ago
                elif 'day' in day_string:
                    today = datetime.today()
                    day = today - timedelta(days=int(parsed_day))
                    job_posted_since = day.strftime("%m/%d/%Y")
                    #job_posted_since = str(parsed_day) + ' days ago' # days ago
                elif 'week' in day_string:
                    job_posted_since = str(parsed_day) + ' weeks ago'
                elif 'month' in day_string:
                    job_posted_since = str(parsed_day) + ' months ago'
                else:
                    job_posted_since = str(day_string)
        else:
                job_posted_since = now.strftime("%m/%d/%Y") # today


        scraped_job_dates.append(job_posted_since)

# this is for grabbing the descriptions from each individual page
# i added a cute lil countdown too

def get_descriptions():
    length = len(scraped_apply_urls)
    for i in scraped_apply_urls:
        req = requests.get(i)
        soup_req = BeautifulSoup(req.text,"html.parser")
        description = soup_req.find('div', attrs={'id':'jobDescriptionText'})
        # remove ".getText()" below if you want to keep the HTML tags
        scraped_job_descriptions.append(description.getText())
        print("Scraping descriptions...")
        length = length - 1 
        print(length)
        time.sleep(random.randint(0,3))

get_descriptions()



# here I combine all of the arrays into a single array
m = np.array([scraped_job_titles, scraped_job_salaries, scraped_job_ratings, scraped_job_locations, scraped_job_dates, scraped_company_names, scraped_apply_urls, scraped_job_descriptions])

# YES this is what I wanted! This transposes the array into "rows" instead of arranging by "columns"
data_arr = np.transpose(m)

def submit_to_db():
    connection = pymysql.connect(host="localhost", user="root", passwd="", database="jobs")
    cursor = connection.cursor()
    dbDate = now.strftime("%Y-%m-%d")
    for row in data_arr:
        insert = "INSERT INTO jobs_table(scan_date, posted_date, title, location, salary, comp_name, rating, url, description) values(%s, %s, %s, %s, %s, %s, %s, %s, %s);"
        cursor.execute(insert, (dbDate, row[4], row[0], row[1], row[3], row[5], row[2], row[6], row[7]))

# uncomment this if you want to also save the listings to a database
#print("Submitting to database...")
#submit_to_db()

# this function writes the results to a website
def write_to_html():
    print("writing to website...")
    saveDate = now.strftime("%m-%d-%Y")
    print(saveDate)
    with open("jobs-" + saveDate + ".html", "w", encoding="utf-8") as f:
        f.write("<strong>Scraped on:</strong> " + now.strftime("%m/%d/%Y") + "<br><br>")
        #print("before data_arr loop")
        # there are 7 rows (8 when desc is active)
        for row in data_arr:
            #if 'contract' in row: print("<div class='alert'>CONTRACT JOB</div>")
            num = 0
            while num != 8:
                    #print("inside while loop")
                    if num == 0:
                        f.write("<strong>Job Title:</strong> " + row[num] + "<br>")
                        num = num + 1
                    elif num == 1:
                        f.write("<strong>Salary:</strong> " + row[num] + "<br>")
                        num = num + 1
                    elif num == 2:
                        f.write("<strong>Ratings:</strong> " + row[num] + "<br>")
                        num = num + 1
                    elif num == 3:
                        f.write("<strong>Location:</strong> " + row[num] + "<br>")
                        num = num + 1
                    elif num == 4:
                        f.write("<strong>Date Posted:</strong> " + row[num] + "<br>")
                        num = num + 1
                    elif num == 5:
                        f.write("<strong>Company Name:</strong> " + row[num] + "<br>")
                        num = num + 1
                    elif num == 6:
                        f.write("<strong>Link:</strong> <a href='" + row[num] + "' target='_blank'>Link</a><br>")
                        num = num + 1
                    elif num == 7:
                        f.write("<details><summary>Description</summary>" + str(row[num]) + "</details>")
                        num = num + 1
                    else:
                        print(num)
                        num = num + 1
            f.write("<br><br>")

# uncomment this code if you'd like to write the results to a webpage
# I recommend doing this with the HTML included in the description
# print("Writing to html...")
# write_to_html()
    


# i made this into a function so it doesn't run every time
def export_to_xlsx(title):
    date = now.strftime("%m-%d-%Y")
    # this lets pandas export to an excel spreadsheet
    #with open('tech_writer-export-' + date + '.xlsx', 'x') as f:
    df = pd.DataFrame(m).T
    df.columns = ["Title", "Salary", "Rating", "Location", "Date", "Company", "URL", "Description"]
    title = title.replace("+", "-")
    df.to_excel(excel_writer = title + "_jobs-" + date + ".xlsx")

print("Saving to XLS...")
export_to_xlsx(title)
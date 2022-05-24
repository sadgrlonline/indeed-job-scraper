# Indeed Scraper

## What is this?

This is a scraper built with Python which scrapes Indeed job listings from the last 14 days. It scrapes the following information:

- Date Posted
- Job Title
- Location
- Salary
- Company Name
- Company Ratings
- Application URL
- Job Description

It then saves this information into an XLSX file with the current date.

## How does it work?

Once you run the script, the command line will prompt you for the job title, location and job type (full time or part time). Then, when the script is complete, it will save an XLSX file in the same directory with your results.

There are also functions to print the results to a webpage, or directly to a database, but they are commented out in `script.py`

You can view the XLSX in this project, which is a demo search for Nursing Jobs in Alabama.

## How to use

1. Download a `.zip` of the repository or `git clone` it.
2. Download any needed dependencies with pip (you can see these by looking at the `from` and `import` items at the top of `script.py`. They can be installed like `pip install bs4` )
3. Go into the directory and run `python3 script.py` if on Linux, or `py script.py` if on Windows.
4. Answer the prompts that appear on the command line.
5. Wait for the script to complete. The descriptions take a bit to scrape, so a countdown in the console will show you the progress.
6. That's it! Check the directory for the spreadsheet of results.

## Customization
- If you live outside of the US, you can add your country's prefix by editing `script.py` and adding the prefix to the `view_job_url` variable.
- If you want to export the data to a webpage, go to the `get_descriptions()` function and remove `.getText()` from `scraped_job_descriptions.append(description.getText())`. Then, uncomment `write_to_html()`
- If you want to submit the data to a local database, edit the `submit_to_db()` function with your database information and then uncomment `submit_to_db`.
- If you want to increase the number of results, find the first `while` loop and change the page number from 10 to 20, 30, 40, etc. Each 10 represents 15 job listings. Be sure to change it in BOTH places. Please note the more results you display, the longer the script will take to run.

import os
import sys
import requests
import subprocess
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re

def remove_special_characters(text):
    pattern = r'[^a-zA-Z0-9\s]'
    cleaned_text = re.sub(pattern, '', text)
    return cleaned_text

def get_linkedin_job_details(url):
    while True:
        try:
            response = requests.get(url, allow_redirects=True)        
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find('h1').text.strip()
            
            print(title)

            company_name = soup.find('a', class_="topcard__org-name-link").text.strip()
            print(company_name)

            location = soup.find('span', class_="topcard__flavor--bullet").text.strip()
            print(location)
            
            article_elem = soup.find('div', class_="description__text")
            description=article_elem.get_text(strip=True) if article_elem else "Job Description not found"
            print(description)

            return title, company_name, location, description
        
        except AttributeError:
            print("Attribute Error Occurred, retrying...")
            time.sleep(5)
            continue
        
        except Exception as e:
            print(f"An error occurred: {e}")
            return None, None, None, None

def write_to_file(title, company_name, location, description):
    current_year = datetime.now().strftime("%Y")
    current_month = datetime.now().strftime("%B")

    folder_path = os.path.join(current_year, current_month, "Summary")
    os.makedirs(folder_path, exist_ok=True)
    
    clean_title = remove_special_characters(title)
    clean_company_name = remove_special_characters(company_name)

    filename = f"{clean_company_name}-{clean_title}"
    file_path = os.path.join(folder_path, f"{filename}.md")

    with open(file_path, 'w') as file:
        file.write(f"# {company_name} - {title}\n\n")
        file.write(location+"\n")
        file.write(description.strip())

    print(f"Job details written to {file_path}")

    update_summary_table(filename)

def update_summary_table(job_file_name):
    current_year = datetime.now().strftime("%Y")
    current_month = datetime.now().strftime("%B")

    summary_file_path = os.path.join(current_year, current_month, "index.md")

    if not os.path.exists(summary_file_path):
        with open(summary_file_path, 'w') as summary_file:
            summary_file.write("| Summary | Date |\n")
            summary_file.write("| ------- | ---- |\n")

    current_date = datetime.now().strftime("%Y-%m-%d")

    with open(summary_file_path, 'a') as summary_file:
        summary_file.write(f"| [[{job_file_name}]] | {current_date} |\n")

    print(f"Summary table updated in {summary_file_path}")

def handler(url):
    if "workopolis" in url:
        print("Detected workopolis url, sending curl request...")
        curl_command = ["curl", "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36", "-H", "Accept-Language: en-US,en;q=0.5", "-L", url]
        curl_process = subprocess.Popen(curl_command, stdout=subprocess.PIPE)
        curl_output, _ = curl_process.communicate()
        soup = BeautifulSoup(curl_output, 'html.parser')
        print(soup.title)
    elif "linkedin" in url:
        print("Detected linkedin url, sending request...")
        title, company_name, location, description = get_linkedin_job_details(url)

        if title is not None:
            write_to_file(title, company_name, location, description)
            print("Successfully retrieved job details.")
        else:
            print("Failed to retrieve job details.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 tracker.py <url>")
        sys.exit(1)
        
    url = sys.argv[1]

    handler(url)

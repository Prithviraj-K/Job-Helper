import os
import sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_job_details(url):
    response = requests.get(url, allow_redirects=True)        
    soup = BeautifulSoup(response.text, 'html.parser')
    # Extract job title
    title = soup.find('h1').text.strip()
    print(title)

    ## Extract Company Name
    company_name = soup.find('a', class_="topcard__org-name-link").text.strip()
    print(company_name)
    
    # Extract job description
    article_elem = soup.find('div', class_="description__text")
    description=article_elem.get_text(strip=True) if article_elem else "Job Description not found"
    print(description)

    return title, company_name, description

def write_to_file(title, company_name, description):
    # Get current year and month
    current_year = datetime.now().strftime("%Y")
    current_month = datetime.now().strftime("%B")  # Use full month name

    folder_path = os.path.join(current_year, current_month, "Summary")
    os.makedirs(folder_path, exist_ok=True)

    # Construct the full file path
    filename = f"{company_name}-{title}"
    file_path = os.path.join(folder_path, f"{filename}.md")

    # Write job details to Markdown file
    with open(file_path, 'w') as file:
        file.write(f"# {company_name} - {title}\n\n")
        file.write(description.strip())

    print(f"Job details written to {file_path}")

    # Update the main summary table
    update_summary_table(filename)

def update_summary_table(job_file_name):
    # Get current year and month
    current_year = datetime.now().strftime("%Y")
    current_month = datetime.now().strftime("%B")  # Use full month name

    # Construct the full path for the main summary markdown file
    summary_file_path = os.path.join(current_year, current_month, "index.md")

    # Check if the summary file exists
    if not os.path.exists(summary_file_path):
        # If it doesn't exist, create the summary file with the header
        with open(summary_file_path, 'w') as summary_file:
            summary_file.write("| Summary | Date |\n")
            summary_file.write("| ------- | ---- |\n")

    # Get the current date
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Append a new row to the summary table
    with open(summary_file_path, 'a') as summary_file:
        summary_file.write(f"| [[{job_file_name}]] | {current_date} |\n")

    print(f"Summary table updated in {summary_file_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 tracker.py <url>")
        sys.exit(1)
        
    url = sys.argv[1]

    title, company_name, description = get_job_details(url)

    write_to_file(title, company_name, description)

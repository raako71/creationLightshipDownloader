import sys
import os
import subprocess
import webbrowser
import shutil
import re
from datetime import datetime, timedelta

def open_url(url):
    """Open a URL in the default web browser."""
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Error opening URL: {e}")

def run_script(search_string=None):
    """Run the script again."""
    python_script = os.path.realpath(__file__)  # Get the path of the current script
    subprocess.run(["python", python_script] + ([search_string] if search_string else []))

def increment_date(search_string):
    """Increment the search string date by one day."""
    try:
        search_date = datetime.strptime(search_string, "%m-%d")
        next_day = search_date + timedelta(days=1)
        return next_day.strftime("%m-%d")
    except ValueError:
        print("Invalid date format.")
        return None

if len(sys.argv) > 1:
    search_string = sys.argv[1]
else:
    # Prompt user to enter the search string if not provided as argument
    search_string = input("Enter the search string (in format MM-DD): ")

# Define the base URL for the webpage
base_url = "https://creationlightship-archive.com/radioa/"

# Define the years to search
years = [str(year) for year in range(2018, 2008, -1)]  # From 2018 to 2009

# Initialize a variable to track if the search string is found
search_found = False

# Create a directory for temporary downloads
temp_download_dir = "temp_download"
if not os.path.exists(temp_download_dir):
    os.makedirs(temp_download_dir)

# Loop through each year
for year in years:
    # Construct the URL to search for the current year
    url = base_url + year + "%20Shows"
    
    # Check if the HTML file already exists
    html_file_path = os.path.join(temp_download_dir, f"temp_{year}.html")
    if not os.path.exists(html_file_path):
        # Fetch the webpage content and store it in a temporary file
        subprocess.run(["curl", url, "-o", html_file_path, "-s"], stdout=subprocess.DEVNULL)
    
    # Read the content of the temporary HTML file into memory
    with open(html_file_path, "r", encoding="utf-8") as html_file:
        html_content = html_file.read()

    # Search for the search string in the HTML content
    if search_string in html_content:
        # If the search string is found, print success message and set flag
        print(f"Search string found in year {year}.")

        # Use regular expression to find URLs containing the search string
        found_urls = re.findall(r'"url":"(.*?)"', html_content)

        # Filter out URLs that do not contain the search string
        found_urls = [url for url in found_urls if search_string in url]

        # Print the found URLs
        print("Found URLs:")
        for found_url in found_urls:
            print(found_url)
        
        # Set flag to indicate search string is found
        search_found = True
        break  # Exit the loop once the search string is found

# Check if the search string was found in any year
if search_found:
    # Prompt user to open the found URLs
    open_response = input("Do you want to open the found URLs? (y/n): (default y) ").strip().lower() or 'y'
    if open_response == "y":
        for found_url in found_urls:
            open_url(found_url)

    # Prompt user for rerun option
    rerun_response = input("Do you want to rerun the script? Enter 'y' for yes, 'a' to increment the search date (default), or 'n' for no: ").strip().lower() or 'a'

    if rerun_response == "y":
        new_search_string = input("Enter a new search string (in format MM-DD): ").strip() or search_string
        run_script(new_search_string)
    elif rerun_response == "a":
        next_search_string = increment_date(search_string)
        if next_search_string:
            run_script(next_search_string)
    
else:
    print("Search string not found in any year.")


# Delete the temporary download directory and its contents
shutil.rmtree(temp_download_dir)

# Wait for user input before exiting
input("Press Enter to exit...")

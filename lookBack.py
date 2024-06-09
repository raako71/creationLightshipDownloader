import sys
import os
import subprocess
import webbrowser
import shutil
import re
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

def get_date_input(prompt):
    """Get a date input from the user and validate the format."""
    while True:
        date_str = input(prompt).strip()
        try:
            return datetime.strptime(date_str, "%m-%d")
        except ValueError:
            print("Invalid date format. Please enter the date in MM-DD format.")

# Create a directory for temporary downloads
temp_download_dir = "temp_download"
if not os.path.exists(temp_download_dir):
    os.makedirs(temp_download_dir)
        
def find_most_recent_file(date, start_year=2018):
    # Define the base URL for the webpage
    base_url = "https://creationlightship-archive.com/radioa/"
    
    # Initialize the current year to start the search
    print(f"year = {start_year}")
    
    search_string = date.strftime("%m-%d")
    
    # Define the years to search 
    years = [str(year) for year in range(int(start_year), 2008, -1)]  # From 2018 to 2009
    
    for year in years:
        print(f"Searching: {year}")
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

            # Use regular expression to find URLs containing the search string
            found_urls = re.findall(r'"url":"(.*?)"', html_content)

            # Filter out URLs that do not contain the search string
            found_urls = [url for url in found_urls if search_string in url]

            for found_url in found_urls:
                return found_url, year
    print("Search string not found in any year.")
    return None, None

def download_mp3(url, destination=None):
    try:
        # If no destination is provided, use the current directory
        if destination is None:
            destination = os.getcwd()
        
        # Create the destination directory if it doesn't exist
        if not os.path.exists(destination):
            os.makedirs(destination)
        
        # Encode the URL to handle special characters
        encoded_url = urllib.parse.quote(url, safe=':/')
        
        # Extract the filename from the URL
        filename = os.path.basename(url)
        
        # Construct the full path for the destination file
        file_path = os.path.join(destination, filename)

        # Download the MP3 file from the encoded URL with progress
        with urllib.request.urlopen(encoded_url) as response, open(file_path, 'wb') as out_file:
            total_size = int(response.headers.get('Content-Length'))
            downloaded_size = 0
            block_size = 8192
            while True:
                buffer = response.read(block_size)
                if not buffer:
                    break
                out_file.write(buffer)
                downloaded_size += len(buffer)
                progress = downloaded_size / total_size * 100
                print(f"\rDownloading: {progress:.2f}%", end='', flush=True)

        print(f"\nFile downloaded successfully: {file_path}")
    except Exception as e:
        print(f"\nError downloading file from URL: {e}")
        
def main():  
    
    # Capture and validate start date
    start_date = get_date_input("Enter the start date (in format MM-DD): ")

    # Capture and validate end date or proceed with single date
    while True:
        end_date_input = input("Press enter for single date, or enter end date (in format MM-DD): ").strip()
        if end_date_input == "":
            end_date = start_date
            break
        try:
            end_date = datetime.strptime(end_date_input, "%m-%d")
            if end_date >= start_date:
                break
            else:
                print("End date cannot be earlier than start date.")
        except ValueError:
            print("Invalid date format. Please enter the date in MM-DD format.")
    
    # Display selected date(s)
    if start_date == end_date:
        print(f"Date selected is {start_date.strftime('%m-%d')}")
    else:
        print(f"Dates selected are {start_date.strftime('%m-%d')} through {end_date.strftime('%m-%d')}")

    def find_and_print_most_recent_file(start_date, year=2018):
        # Find the most recent file for the start date
        url, year = find_most_recent_file(start_date, year)

        if url:
            print(f"Start date found in year {year}")
        else:
            print("No file found for the start date.")
        
        return url, year

    # Call the function initially
    url, year = find_and_print_most_recent_file(start_date)
    loop = 1
    # Prompt user for next action if start_date is the same as end_date
    if start_date == end_date:
        while loop == 1:
            user_input = input("Enter B to search back previous years for the same date, Q to quit, R to restart, or Enter to download: ").strip().lower()
            if user_input == "b":
                url, year = find_and_print_most_recent_file(start_date, year=str(int(year) - 1))
            elif user_input == "":
                download_mp3(url)
            elif user_input == "q":
                print("Exiting...")
                loop = 0
                break
            elif user_input == "r":
                main()
            else:
                print("Invalid input. Please enter B, Enter, or Q.")

    
    # Delete the temporary download directory and its contents
    shutil.rmtree(temp_download_dir)

if __name__ == "__main__":
    main()

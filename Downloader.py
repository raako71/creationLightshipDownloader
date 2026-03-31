import sys
import os
import subprocess
import webbrowser
import shutil
import re
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

def get_date_input(prompt, default_date):
    """Get a date input from the user and validate the format."""
    while True:
        date_str = input(prompt).strip()
        if not date_str:
            return default_date
        if date_str.lower() == 'b':
            return default_date - timedelta(days=1)
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
    search_string = date.strftime("%m-%d")
    
    # Define the years to search 
    years = [str(year) for year in range(int(start_year), 2008, -1)]  # From 2018 to 2009
    
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
            destination = os.path.join(os.path.expanduser("~"), "Downloads")
        
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
    except Exception as e:
        print(f"\nError downloading file from URL: {e}")

def iterate_dates_and_download(start_date, end_date):
    # Create a list to store information about each date
    date_info_list = []

    # Iterate through each date from start_date to end_date
    current_date = start_date
    while current_date <= end_date:
        # Find the most recent file for the current date
        url, year = find_most_recent_file(current_date)

        # If a URL is found, store the date, year, and URL
        if url:
            date_info_list.append((current_date.strftime("%m-%d"), year, url))
            print(f"Found {current_date.strftime('%m-%d')}-{year}")

        # Move to the next date
        current_date += timedelta(days=1)

    # Prompt the user to either quit or download the files
    user_input = input("Press Q to quit, or Enter to download: ").strip().lower()
    if user_input == "q":
        print("Exiting...")
        return

    # Download the files for each date
    for date_info in date_info_list:
        date, year, url = date_info
        print(f"Downloading file for {date}...")
        download_mp3(url)
    
    print("Download complete. Press enter to quit.")

def main():
    today = datetime.now()
    today_str = today.strftime("%m-%d")
    
    # Capture and validate start date
    start_date_prompt = f"Enter start date, MM-DD ({today_str}) (or 'b' for yesterday): "
    start_date = get_date_input(start_date_prompt, today)

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
        print(f"Date selected is {start_date.strftime('%m-%d')} ({start_date.strftime('%B %d')})")
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

    loop = 1
    # Prompt user for next action if start_date is the same as end_date
    if start_date == end_date:
        # Call the function initially
        url, year = find_and_print_most_recent_file(start_date)
        while loop == 1:
            user_input = input("Enter B to search back previous years for the same date, Q to quit, R to restart, or Enter to download: ").strip().lower()
            if user_input == "b":
                url, year = find_and_print_most_recent_file(start_date, year=str(int(year) - 1))
            elif user_input == "":
                download_mp3(url)
                print("")
            elif user_input == "q":
                print("Exiting...")
                loop = 0
                break
            elif user_input == "r":
                loop = 0
                main()
            else:
                print("Invalid input. Please enter B, Enter, or Q.")
    else:
        user_input = input("Press Q to Quit or Enter to list all files").strip().lower()
        if user_input != "q":
            iterate_dates_and_download(start_date, end_date)

    # Delete the temporary download directory and its contents
    shutil.rmtree(temp_download_dir)

if __name__ == "__main__":
    main()

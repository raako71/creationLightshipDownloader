from datetime import datetime, timedelta

def get_date_input(prompt):
    """Get a date input from the user and validate the format."""
    while True:
        date_str = input(prompt).strip()
        try:
            return datetime.strptime(date_str, "%m-%d")
        except ValueError:
            print("Invalid date format. Please enter the date in MM-DD format.")

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

    # Wait for user input before exiting
    input("Press enter to quit")

if __name__ == "__main__":
    main()

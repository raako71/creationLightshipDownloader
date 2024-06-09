import os
import eyed3
from datetime import datetime
def update_id3_tags_and_rename_files():
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Change to the script's directory
    os.chdir(script_dir)

    # Find all MP3 files in the directory
    mp3_files = [f for f in os.listdir(script_dir) if f.endswith(".mp3")]

    if not mp3_files:
        print("No MP3 files found in the directory.")
        return

    # List the files found
    print("MP3 files found:")
    for idx, filename in enumerate(mp3_files, start=1):
        print(f"{idx}. {filename}")

    # Ask user for confirmation
    proceed = input("Do you want to update ID3 tags and rename these files? (yes/no): ").strip().lower()

    if proceed != 'yes':
        print("Operation cancelled.")
        return

    # Process each file
    for filename in mp3_files:
        try:
            # Parse the date from the filename
            base_name, _ = os.path.splitext(filename)
            parts = base_name.split('_')[-1]
            file_date = datetime.strptime(parts, "%Y-%m-%d")
            new_title = file_date.strftime("%B %d %Y")

            # Load the MP3 file
            audiofile = eyed3.load(filename)

            # Check if the file has an ID3 tag; if not, initialize it
            if audiofile.tag is None:
                audiofile.initTag()

            # Update the title tag
            audiofile.tag.title = new_title

            # Save the changes
            audiofile.tag.save()

            # Rename the file by appending 'r' to the filename
            new_filename = base_name + 'r.mp3'
            os.rename(filename, new_filename)

            print(f"Updated and renamed: {filename} -> {new_filename}")
        except Exception as e:
            print(f"Failed to process {filename}: {e}")

    print("All files processed successfully. Press Enter to quit.")
    input()

if __name__ == "__main__":
    # Run the function
    update_id3_tags_and_rename_files()

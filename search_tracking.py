import pandas as pd
import os
import shutil
import subprocess
from datetime import datetime
from time import sleep
os.environ['GIT_USERNAME'] = 'daya-daya'
os.environ['GIT_PASSWORD'] = 'Anildaya@9398'


# Clone the repository
subprocess.run(["git", "clone", "https://daya-daya:Anildaya@9398@github.com/username/repo.git"], check=True)

LOG_DIR = "search_log"
DOWNLOAD_DIR = "download_folder"

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)


def log_search(search_term):
    if not search_term.strip():
        return  # Do nothing if the search_term is blank

    log_file = os.path.join(LOG_DIR, "search_log.xlsx")
    search_term = search_nlp_correction(search_term)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if os.path.exists(log_file):
        # Load existing data
        existing_df = pd.read_excel(log_file, engine='openpyxl')

        if search_term in existing_df["Search Term"].values:
            # Update existing entry
            index = existing_df[existing_df["Search Term"] == search_term].index[0]
            existing_df.at[index, "Count"] += 1
            existing_df.at[index, "Last Searched"] = current_time
        else:
            # Add new entry
            search_data = {
                "Search Term": [search_term],
                "Count": [1],
                "Last Searched": [current_time]
            }
            new_df = pd.DataFrame(search_data)
            existing_df = pd.concat([existing_df, new_df], ignore_index=True)

        # Save the updated data back to the file
        existing_df.to_excel(log_file, index=False, engine='openpyxl')
    else:
        # Create new log file with initial data
        search_data = {
            "Search Term": [search_term],
            "Count": [1],
            "Last Searched": [current_time]
        }
        log_df = pd.DataFrame(search_data)
        log_df.to_excel(log_file, index=False, engine='openpyxl')

    # Schedule the download and delete process after 24 hours
    download_and_delete_after_24_hours(log_file)


def search_nlp_correction(search_term):
    # Placeholder for NLP-based search term correction
    return search_term


def download_and_delete_after_24_hours(log_file):
    # Wait for 24 hours (86400 seconds)
    sleep(86400)

    # Create a timestamped filename for download
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    download_path = os.path.join(DOWNLOAD_DIR, f"search_log_{timestamp}.xlsx")

    # Copy the file to the download folder
    shutil.copy(log_file, download_path)
    print(f"File downloaded to {download_path}")

    # Delete the file from Git
    delete_file_from_git(log_file)


def delete_file_from_git(file_path):
    try:
        # Stage the file for removal
        subprocess.run(["git", "rm", file_path], check=True)
        print(f"Staged file for removal: {file_path}")

        # Commit the change
        commit_message = f"Deleted file: {file_path}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        print(f"Committed change with message: '{commit_message}'")

        # Push the commit
        subprocess.run(["git", "push"], check=True)
        print("Successfully pushed changes to Git.")

    except subprocess.CalledProcessError as e:
        print(f"Error during Git operations: {e}")

# Example usage
log_search("example search term")

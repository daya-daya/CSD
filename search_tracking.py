import pandas as pd
import os
from datetime import datetime
import subprocess

LOG_DIR = "search_log"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def log_search(search_term):
    # Check if the search_term is blank or contains only whitespace
    if not search_term.strip():
        return  # Do nothing if the search_term is blank

    log_file = os.path.join(LOG_DIR, "search_log.xlsx")
    search_term = search_nlp_correction(search_term)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if os.path.exists(log_file):
        # Load existing data
        existing_df = pd.read_excel(log_file, engine='openpyxl')

        # Check if search term already exists
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

    # Ensure the updated log file is tracked and pushed to GitHub
    commit_and_push_to_git(log_file)

def search_nlp_correction(search_term):
    # Placeholder for NLP-based search term correction
    return search_term

def commit_and_push_to_git(log_file):
    try:
        # Stage the updated log file
        subprocess.run(["git", "add", log_file], check=True)

        # Commit the changes with a relevant message
        subprocess.run(["git", "commit", "-m", "Update search_log.xlsx with new search term"], check=True)

        # Push the changes to the repository
        subprocess.run(["git", "push"], check=True)

    except subprocess.CalledProcessError as e:
        print(f"An error occurred during Git operations: {e}")

# Example usage
log_search("example search term")

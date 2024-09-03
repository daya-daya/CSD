import pandas as pd
import os
from datetime import datetime
import subprocess

LOG_DIR = "search_log/search_log"

# Ensure the directory exists
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
    print(f"Created directory: {LOG_DIR}")

def log_search(search_term):
    # Check if the search_term is blank or contains only whitespace
    if not search_term.strip():
        print("Search term is blank or contains only whitespace. No action taken.")
        return  # Do nothing if the search_term is blank or only whitespace

    log_file = os.path.join(LOG_DIR, "search_log.xlsx")
    search_term = search_nlp_correction(search_term)

    current_date = datetime.now().strftime('%Y-%m-%d')

    try:
        if os.path.exists(log_file):
            # Load existing data
            existing_df = pd.read_excel(log_file, engine='openpyxl')
            print(f"Loaded existing data from {log_file}")

            # Check if the search term already exists in the log
            if search_term in existing_df["Search Term"].values:
                # Update the existing entry by incrementing the count and updating the date
                index = existing_df[existing_df["Search Term"] == search_term].index[0]
                existing_df.at[index, "Count"] += 1
                existing_df.at[index, "Last Searched Date"] = current_date
                print(f"Updated existing entry for '{search_term}'")
            else:
                # Add a new entry for the search term with a count of 1 and the current date
                new_entry = pd.DataFrame({
                    "Search Term": [search_term],
                    "Count": [1],
                    "Last Searched Date": [current_date]
                })
                existing_df = pd.concat([existing_df, new_entry], ignore_index=True)
                print(f"Added new entry for '{search_term}'")

            # Save the updated data back to the log file
            existing_df.to_excel(log_file, index=False, engine='openpyxl')
            print(f"Saved updated data to {log_file}")

        else:
            # Create a new log file with the initial search term data and date
            log_df = pd.DataFrame({
                "Search Term": [search_term],
                "Count": [1],
                "Last Searched Date": [current_date]
            })
            log_df.to_excel(log_file, index=False, engine='openpyxl')
            print(f"Created new log file {log_file} with initial data")

        # Add, commit, and push changes to Git
        git_add_commit_push()

    except Exception as e:
        print(f"An error occurred: {e}")

def search_nlp_correction(search_term):
    # Placeholder for NLP-based search term correction
    # Modify this function with actual NLP logic if needed
    return search_term

def git_add_commit_push():
    try:
        # Add files to the staging area
        subprocess.run(["git", "add", "."], check=True)
        print("Staged changes for commit.")

        # Commit the changes
        commit_message = "Update search log"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        print(f"Committed changes with message: '{commit_message}'")

        # Push the changes to the remote repository
        subprocess.run(["git", "push"], check=True)
        print("Pushed changes to the remote repository.")

    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")

# Example usage:
log_search("example search term")

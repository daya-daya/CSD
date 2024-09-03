import pandas as pd
import os
from datetime import datetime

LOG_DIR = "search_log/search_log"

# Ensure the directory exists
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def log_search(search_term):
    # Check if the search_term is blank or contains only whitespace
    if not search_term.strip():
        return  # Do nothing if the search_term is blank or only whitespace

    log_file = os.path.join(LOG_DIR, "search_log.xlsx")
    search_term = search_nlp_correction(search_term)

    current_date = datetime.now().strftime('%Y-%m-%d')

    if os.path.exists(log_file):
        # Load existing data
        existing_df = pd.read_excel(log_file, engine='openpyxl')

        # Check if the search term already exists in the log
        if search_term in existing_df["Search Term"].values:
            # Update the existing entry by incrementing the count and updating the date
            index = existing_df[existing_df["Search Term"] == search_term].index[0]
            existing_df.at[index, "Count"] += 1
            existing_df.at[index, "Last Searched Date"] = current_date
        else:
            # Add a new entry for the search term with a count of 1 and the current date
            new_entry = pd.DataFrame({
                "Search Term": [search_term],
                "Count": [1],
                "Last Searched Date": [current_date]
            })
            existing_df = pd.concat([existing_df, new_entry], ignore_index=True)

        # Save the updated data back to the log file
        existing_df.to_excel(log_file, index=False, engine='openpyxl')
    else:
        # Create a new log file with the initial search term data and date
        log_df = pd.DataFrame({
            "Search Term": [search_term],
            "Count": [1],
            "Last Searched Date": [current_date]
        })
        log_df.to_excel(log_file, index=False, engine='openpyxl')

def search_nlp_correction(search_term):
    # Placeholder for NLP-based search term correction
    # Modify this function with actual NLP logic if needed
    return search_term

# Example usage:
log_search("example search term")

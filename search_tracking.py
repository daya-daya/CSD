import pandas as pd
import os
from datetime import datetime
from zipfile import BadZipFile

LOG_DIR = "search_log"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def log_search(search_term):
    if not search_term.strip():
        return  # Do nothing if the search_term is blank

    log_file = os.path.join(LOG_DIR, "search_log.xlsx")
    search_term = search_nlp_correction(search_term)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        if os.path.exists(log_file):
            # Load existing data
            existing_df = pd.read_excel(log_file, engine='openpyxl')
            print("Loaded existing data:")
            print(existing_df)

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
            print("Updated data saved to Excel.")
        else:
            # Create new log file with initial data
            search_data = {
                "Search Term": [search_term],
                "Count": [1],
                "Last Searched": [current_time]
            }
            log_df = pd.DataFrame(search_data)
            log_df.to_excel(log_file, index=False, engine='openpyxl')
            print("New log file created and saved to Excel.")
    
    except BadZipFile as e:
        print(f"Error: {e}")
        # Handle the corrupted file scenario
        # Optionally, you could delete the corrupted file and start fresh
        if os.path.exists(log_file):
            os.remove(log_file)
        # Create a new log file
        search_data = {
            "Search Term": [search_term],
            "Count": [1],
            "Last Searched": [current_time]
        }
        log_df = pd.DataFrame(search_data)
        log_df.to_excel(log_file, index=False, engine='openpyxl')
        print("New log file created after handling BadZipFile error.")

def search_nlp_correction(search_term):
    # Placeholder for NLP-based search term correction
    return search_term

# Example usage
log_search("example search term")

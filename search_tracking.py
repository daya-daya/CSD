import os
import pandas as pd
from datetime import datetime
from fuzzywuzzy import fuzz, process

# Directory for storing search logs
LOG_DIR = "search_log"
os.makedirs(LOG_DIR, exist_ok=True)
print(f"Log directory created at: {LOG_DIR}")

SEARCH_LOG_FILE = os.path.join(LOG_DIR, "search_log.xlsx")
print(f"Search log file path: {SEARCH_LOG_FILE}")

# Function to correct the search term based on previously logged terms
def search_nlp_correction(search_term, previous_searches):
    # (Unchanged code)

# Function to fetch previously searched terms from the log
def get_previous_searches():
    print("Fetching previous searches...")
    if os.path.exists(SEARCH_LOG_FILE):
        search_log = pd.read_excel(SEARCH_LOG_FILE, engine='openpyxl')
        if "Search Term" in search_log.columns:
            return search_log["Search Term"].tolist()
        else:
            print("Error: 'Search Term' column is missing.")
            return []
    else:
        print("Search log file does not exist.")
        return []

# Function to log searches, updating the existing entry or adding a new one
def log_search(search_term):
    if not search_term.strip():
        print("No search term provided. No record added.")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if os.path.exists(SEARCH_LOG_FILE):
        search_log = pd.read_excel(SEARCH_LOG_FILE, engine='openpyxl')
    else:
        search_log = pd.DataFrame(columns=["Search Term", "Timestamp", "Search Count"])

    if "Search Term" not in search_log.columns:
        print("Error: 'Search Term' column is missing.")
        return

    if search_term in search_log["Search Term"].values:
        search_log.loc[search_log["Search Term"] == search_term, "Search Count"] += 1
        search_log.loc[search_log["Search Term"] == search_term, "Timestamp"] = timestamp
    else:
        new_entry = {"Search Term": search_term, "Timestamp": timestamp, "Search Count": 1}
        search_log = pd.concat([search_log, pd.DataFrame([new_entry])], ignore_index=True)

    try:
        with pd.ExcelWriter(SEARCH_LOG_FILE, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            search_log.to_excel(writer, index=False)
    except Exception as e:
        print(f"Error saving search log: {e}")

# Example usage
if __name__ == "__main__":
    previous_searches = get_previous_searches()
    search_term = input("Enter the item to search: ").strip()
    corrected_term = search_nlp_correction(search_term, previous_searches)
    log_search(corrected_term)
    print(f"Corrected Search Term: {corrected_term}")

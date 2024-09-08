import os
import pandas as pd
from datetime import datetime
from fuzzywuzzy import fuzz, process

# Directory for storing search logs
LOG_DIR = "search_log"
os.makedirs(LOG_DIR, exist_ok=True)

SEARCH_LOG_FILE = os.path.join(LOG_DIR, "search_log.xlsx")

# Function to correct the search term based on previously logged terms
def search_nlp_correction(search_term, previous_searches):
    """
    Corrects the search term using fuzzy matching against previous search terms.

    Parameters:
        search_term (str): The user's input for the search.
        previous_searches (list): List of previously searched terms for correction.

    Returns:
        corrected_term (str): The closest matching term from previous searches, or the original term.
    """
    if previous_searches:
        corrected_term, score = process.extractOne(search_term, previous_searches, scorer=fuzz.token_sort_ratio)
        if score > 70:  # Use a threshold to accept the corrected term
            return corrected_term
    return search_term  # If no match found, return the original term

# Function to fetch previously searched terms from the log
def get_previous_searches():
    """
    Fetches the list of previously logged search terms from the search log file.

    Returns:
        list: List of previously searched terms.
    """
    if os.path.exists(SEARCH_LOG_FILE):
        # Load existing log
        search_log = pd.read_excel(SEARCH_LOG_FILE, engine='openpyxl')
        # Check if 'Search Term' column exists
        if "Search Term" in search_log.columns:
            return search_log["Search Term"].tolist()  # Return the list of previously searched terms
        else:
            print("Error: 'Search Term' column is missing in the log file.")
            return []  # Return an empty list if the column is missing
    return []  # Return an empty list if no log exists

# Function to log searches, updating the existing entry or adding a new one
def log_search(search_term):
    """
    Logs the search term and timestamp, updating the existing entry or adding a new one.

    Parameters:
        search_term (str): The search term entered by the user.

    Returns:
        None
    """
    if not search_term.strip():  # Check if search term is empty
        print("No search term provided. No record added.")
        return

    # Get the current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check if the search log file exists
    if os.path.exists(SEARCH_LOG_FILE):
        # Load existing log
        search_log = pd.read_excel(SEARCH_LOG_FILE, engine='openpyxl')
    else:
        # Create a new DataFrame if the file does not exist
        search_log = pd.DataFrame(columns=["Search Term", "Timestamp", "Search Count"])

    # Check if the 'Search Term' column exists
    if "Search Term" not in search_log.columns:
        print("Error: 'Search Term' column is missing in the DataFrame.")
        return

    # Check if the search term already exists in the log
    if search_term in search_log["Search Term"].values:
        # Update the count and timestamp for the existing term
        search_log.loc[search_log["Search Term"] == search_term, "Search Count"] += 1
        search_log.loc[search_log["Search Term"] == search_term, "Timestamp"] = timestamp
    else:
        # Add a new entry to the log
        new_entry = {"Search Term": search_term, "Timestamp": timestamp, "Search Count": 1}
        search_log = pd.concat([search_log, pd.DataFrame([new_entry])], ignore_index=True)

    # Save the updated log back to the Excel file without overwriting
    with pd.ExcelWriter(SEARCH_LOG_FILE, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
        search_log.to_excel(writer, index=False)



# Example usage
if __name__ == "__main__":
    # Fetch previous searches
    previous_searches = get_previous_searches()

    # Get the search term from the user (replace this with your search input in the app)
    search_term = input("Enter the item to search: ").strip()

    # Correct the search term based on previous searches
    corrected_term = search_nlp_correction(search_term, previous_searches)

    # Log the search
    log_search(corrected_term)

    # Print the corrected search term
    print(f"Corrected Search Term: {corrected_term}")

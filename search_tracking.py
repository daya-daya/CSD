import os
import pandas as pd
from fuzzywuzzy import fuzz, process

# Directory for storing search logs
LOG_DIR = "search_log"
os.makedirs(LOG_DIR, exist_ok=True)

SEARCH_LOG_FILE = os.path.join(LOG_DIR, "search_log.xlsx")

# Function to correct the search term based on previously logged terms
def search_nlp_correction(search_term, previous_searches):
    """
    Corrects the search term using fuzzy matching against previous search terms.
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
    Logs the search term by either updating an existing entry or adding a new one.
    """
    # Check if the file exists, if not, create it with headers
    if not os.path.isfile(SEARCH_LOG_FILE):
        print(f"{SEARCH_LOG_FILE} not found. Creating a new file.")
        # Creating a new DataFrame with headers
        df = pd.DataFrame(columns=['Search Term', 'Search Count', 'Last Searched'])
        df.to_excel(SEARCH_LOG_FILE, index=False)
    
    try:
        # Load existing log
        df = pd.read_excel(SEARCH_LOG_FILE)

        # Check if the search term already exists
        if search_term in df['Search Term'].values:
            # Update the count and the last searched date
            df.loc[df['Search Term'] == search_term, 'Search Count'] += 1
            df.loc[df['Search Term'] == search_term, 'Last Searched'] = pd.Timestamp.now()
        else:
            # Add a new entry
            new_entry = {'Search Term': search_term, 'Search Count': 1, 'Last Searched': pd.Timestamp.now()}
            df = df.append(new_entry, ignore_index=True)

        # Save the updated log back to the Excel file
        with pd.ExcelWriter(SEARCH_LOG_FILE, engine='openpyxl', mode='w') as writer:
            df.to_excel(writer, index=False)
    
    except Exception as e:
        print(f"Error while logging search: {e}")
        raise e

    return df

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

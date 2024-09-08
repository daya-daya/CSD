import os
import pandas as pd
from datetime import datetime
from fuzzywuzzy import fuzz, process

# Directory for storing search logs
directory = 'search_log'
file_path = os.path.join(directory, 'search_log.xlsx')
if not os.path.exists(directory):
    os.makedirs(directory)
 if not os.path.exists(file_path):
    # Create a new Excel file with appropriate columns
    df = pd.DataFrame(columns=['Item Searched', 'Search Count', 'Last Searched Date'])
    df.to_excel(file_path, index=False)   
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

SEARCH_LOG_FILE = 'search_log/search_log.xlsx'

def log_search(search_term):
    # Create a DataFrame with search term and timestamp
    search_data = pd.DataFrame({
        'Search Term': [search_term],
        'Timestamp': [pd.Timestamp.now()],
        'Count': [1]
    })

    # Check if the file exists, if not, create it
    if not os.path.exists(SEARCH_LOG_FILE):
        # If file does not exist, create a new Excel file with the search data
        search_data.to_excel(SEARCH_LOG_FILE, index=False)
    else:
        # If the file exists, read it and update the search count if the term already exists
        existing_data = pd.read_excel(SEARCH_LOG_FILE)

        # Check if the search term already exists
        if search_term in existing_data['Search Term'].values:
            existing_data.loc[existing_data['Search Term'] == search_term, 'Count'] += 1
            existing_data.loc[existing_data['Search Term'] == search_term, 'Timestamp'] = pd.Timestamp.now()
        else:
            # Append the new search term
            existing_data = pd.concat([existing_data, search_data], ignore_index=True)

        # Write the updated data back to the Excel file
        with pd.ExcelWriter(SEARCH_LOG_FILE, engine='openpyxl', mode='w') as writer:
            existing_data.to_excel(writer, index=False)

    return search_term

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

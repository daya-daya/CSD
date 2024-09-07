# search_log.py

import pandas as pd
import os
from datetime import datetime
from textblob import TextBlob  # Ensure textblob is installed for spelling correction

# Directory to store search logs
SEARCH_LOG_DIR = "search_log"
os.makedirs(SEARCH_LOG_DIR, exist_ok=True)

def log_search(search_term):
    # Create or update the search log Excel file
    log_file_path = os.path.join(SEARCH_LOG_DIR, "search_log.xlsx")
    
    # Load existing search log data or create an empty DataFrame
    if os.path.exists(log_file_path):
        search_log_df = pd.read_excel(log_file_path, engine='openpyxl')
    else:
        search_log_df = pd.DataFrame(columns=["Search Term", "Search Count", "Date"])
    
    # Add or update the search term record
    today_date = datetime.now().strftime("%Y-%m-%d")
    if search_term in search_log_df["Search Term"].values:
        search_log_df.loc[search_log_df["Search Term"] == search_term, "Search Count"] += 1
    else:
        new_record = pd.DataFrame({
            "Search Term": [search_term],
            "Search Count": [1],
            "Date": [today_date]
        })
        search_log_df = pd.concat([search_log_df, new_record], ignore_index=True)
    
    # Save updated log data
    search_log_df.to_excel(log_file_path, index=False, engine='openpyxl')

def search_nlp_correction(search_term):
    # Correct spelling of the search term using TextBlob
    corrected_search_term = str(TextBlob(search_term).correct())
    return corrected_search_term


import pandas as pd
import os
from datetime import datetime

# Directory to store search logs
SEARCH_LOG_DIR = "search_log"
os.makedirs(SEARCH_LOG_DIR, exist_ok=True)

def log_search(search_term):
    log_file = os.path.join(SEARCH_LOG_DIR, "search_log.xlsx")

    # Get the current date and time
    current_time = datetime.now()

    # Create a DataFrame for the new log entry
    new_log = pd.DataFrame({
        "Date": [current_time.strftime("%Y-%m-%d")],
        "Time": [current_time.strftime("%H:%M:%S")],
        "Search Term": [search_term],
        "Count": [1]
    })

    if os.path.exists(log_file):
        # If the log file exists, load it and append the new log
        existing_logs = pd.read_excel(log_file, engine='openpyxl')

        # Check if the search term already exists for the current date
        match = existing_logs[(existing_logs['Search Term'] == search_term) & (existing_logs['Date'] == current_time.strftime("%Y-%m-%d"))]

        if not match.empty:
            # If it exists, increment the count
            existing_logs.loc[match.index, 'Count'] += 1
        else:
            # Otherwise, append the new log entry
            existing_logs = pd.concat([existing_logs, new_log], ignore_index=True)

        # Save the updated log back to the file
        existing_logs.to_excel(log_file, index=False, engine='openpyxl')
    else:
        # If the log file doesn't exist, create it with the new log entry
        new_log.to_excel(log_file, index=False, engine='openpyxl')

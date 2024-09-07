import streamlit as st
import pandas as pd
import os
import subprocess
from datetime import datetime
from zipfile import BadZipFile

# Directories
LOG_DIR = "search_log"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Path to the log file
log_file = os.path.join(LOG_DIR, "search_log.xlsx")

# Function to log search terms
def log_search(search_term):
    search_term = search_nlp_correction(search_term)  # Apply any corrections if necessary
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        if os.path.exists(log_file):
            # Load existing data
            existing_df = pd.read_excel(log_file, engine='openpyxl')
        else:
            # Create new log if it doesn't exist
            existing_df = pd.DataFrame(columns=["Search Term", "Count", "Last Searched"])

        # Check if search term already exists
        if search_term in existing_df["Search Term"].values:
            # Update existing entry
            index = existing_df[existing_df["Search Term"] == search_term].index[0]
            existing_df.at[index, "Count"] += 1
            existing_df.at[index, "Last Searched"] = current_time
        else:
            # Add new search term
            new_data = {
                "Search Term": [search_term],
                "Count": [1],
                "Last Searched": [current_time]
            }
            new_df = pd.DataFrame(new_data)
            existing_df = pd.concat([existing_df, new_df], ignore_index=True)

        # Save the updated log to Excel
        existing_df.to_excel(log_file, index=False, engine='openpyxl')

        # Commit and push the updated Excel file to GitHub
        commit_and_push_to_git(log_file)

    except BadZipFile:
        # Handle corrupted Excel files
        if os.path.exists(log_file):
            os.remove(log_file)
        new_data = {
            "Search Term": [search_term],
            "Count": [1],
            "Last Searched": [current_time]
        }
        new_df = pd.DataFrame(new_data)
        new_df.to_excel(log_file, index=False, engine='openpyxl')

def search_nlp_correction(search_term):
    # NLP correction placeholder (optional)
    return search_term

def commit_and_push_to_git(file_path):
    try:
        # Add the file to the Git staging area
        subprocess.run(["git", "add", file_path], check=True)

        # Commit the file with a message
        commit_message = f"Update search log: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)

        # Push the commit to the remote repository
        subprocess.run(["git", "push"], check=True)
        st.success("Search log updated and pushed to GitHub!")

    except subprocess.CalledProcessError as e:
        st.error(f"An error occurred during Git operations: {e}")

# Streamlit App
st.title("Search Logging App")

# Search box input
search_term = st.text_input("Enter search term:")

# If a search term is entered
if st.button("Search"):
    if search_term.strip():
        log_search(search_term)
        st.success(f"Search term '{search_term}' logged successfully!")
    else:
        st.warning("Please enter a valid search term.")

# Display the search log
if os.path.exists(log_file):
    st.subheader("Search Log")
    search_log = pd.read_excel(log_file)
    st.dataframe(search_log)

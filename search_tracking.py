import pandas as pd
import os
from datetime import datetime
import streamlit as st
from textblob import TextBlob

# Define the file path
SEARCH_LOG_FILE = os.path.join("search_log", "search_log.xlsx")

# Ensure the search_log directory and file exist
def initialize_search_log():
    if not os.path.exists("search_log"):
        os.makedirs("search_log")
        print("Created search_log directory.")
    
    if not os.path.exists(SEARCH_LOG_FILE):
        try:
            # Create an empty DataFrame with the desired columns
            search_log_df = pd.DataFrame(columns=["Search Term", "Count", "Last Searched"])
            # Save the empty DataFrame as an Excel file
            search_log_df.to_excel(SEARCH_LOG_FILE, index=False)
            print(f"Created new log file at {SEARCH_LOG_FILE}")
        except Exception as e:
            print(f"Error creating log file: {e}")

# Function to log searches
def log_search(search_term):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    initialize_search_log()

    try:
        # Load the search log data
        search_log_df = pd.read_excel(SEARCH_LOG_FILE)
        
        # Check if the search term already exists
        if search_term in search_log_df["Search Term"].values:
            # Increment the count for the existing search term
            search_log_df.loc[search_log_df["Search Term"] == search_term, "Count"] += 1
            # Update the last searched timestamp
            search_log_df.loc[search_log_df["Search Term"] == search_term, "Last Searched"] = current_time
        else:
            # Add a new entry for the search term
            new_entry = {"Search Term": search_term, "Count": 1, "Last Searched": current_time}
            search_log_df = search_log_df.append(new_entry, ignore_index=True)
        
        # Save the updated search log to the Excel file
        search_log_df.to_excel(SEARCH_LOG_FILE, index=False)
        print(f"Logged search term: {search_term}")
    except Exception as e:
        print(f"Error logging search: {e}")

# Function to handle search input
def render_search_box():
    search_term = st.text_input("Search Item Description", "")
    if search_term:
        search_term = search_term.lower()
        corrected_search_term = search_nlp_correction(search_term)
        log_search(corrected_search_term)
        st.write(f"Corrected Search Term: {corrected_search_term}")

# Function for NLP-based correction
def search_nlp_correction(search_term):
    blob = TextBlob(search_term)
    return str(blob.correct())

# Streamlit main logic
def main():
    st.title("Search Application")

    option = st.selectbox("Choose an option", ("Search", "Admin Panel"))

    if option == "Search":
        render_search_box()
    elif option == "Admin Panel":
        admin_panel()

if __name__ == "__main__":
    main()

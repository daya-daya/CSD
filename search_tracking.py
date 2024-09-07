import pandas as pd
import os
from datetime import datetime
import streamlit as st

# Define the file path
SEARCH_LOG_FILE = os.path.join("search_log/", "search_log.xlsx")

# Ensure the search_log directory exists
os.makedirs("search_log", exist_ok=True)

# Function to create the Excel file if it doesn't exist
def create_log_file_if_not_exists():
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
    # Get current time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Ensure the file exists, create it if not
    create_log_file_if_not_exists()

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

# Function to allow admin to download the search log
def download_search_log():
    try:
        with open(SEARCH_LOG_FILE, "rb") as file:
            btn = st.download_button(
                label="Download Search Log",
                data=file,
                file_name="search_log.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        return btn
    except Exception as e:
        print(f"Error downloading search log: {e}")

# Function to handle search input
def render_search_box():
    search_term = st.text_input("Search Item Description", "")  # User's search input
    search_term = search_term.lower()  # Convert to lowercase for case-insensitive search
    corrected_search_term = search_nlp_correction(search_term)  # Correct the search term using NLP

    # Log the search term to the Excel sheet
    log_search(corrected_search_term)

    if search_term:
        # Perform search and display results...
        pass
    
    return search_term

# Function for admin panel (download option)
def admin_panel():
    st.header("Admin Panel")
    if os.path.exists(SEARCH_LOG_FILE):
        st.write("Download the search log:")
        download_search_log()
    else:
        st.write("No search log available yet.")

# Function for NLP-based correction
def search_nlp_correction(search_term):
    # Dummy implementation of NLP correction
    # Replace with actual NLP-based correction
    return search_term

# Streamlit main logic (example for demonstration)
def main():
    st.title("Search Application")

    option = st.selectbox("Choose an option", ("Search", "Admin Panel"))

    if option == "Search":
        render_search_box()
    elif option == "Admin Panel":
        admin_panel()

if __name__ == "__main__":
    main()

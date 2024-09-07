import os
import subprocess
import pandas as pd
from datetime import datetime
import streamlit as st

# Directory and file paths
UPLOAD_DIR = "uploaded_files"
DEMAND_DIR = "Demand_stock"
SEARCH_LOG_DIR = "search_log"
SEARCH_LOG_FILE = os.path.join(SEARCH_LOG_DIR, "search_log.csv")

# Ensure the directories and file exist
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def ensure_file_exists(file_path):
    if not os.path.isfile(file_path):
        with open(file_path, 'w') as f:
            # Create an empty file or initialize with headers
            f.write("Search Term,Count,Last Searched\n")

# Commit and push changes to GitHub
def commit_and_push_to_github(file_path):
    repo_dir = '/path/to/your/repo'  # Update this path to your local GitHub repo
    search_log_dir = os.path.dirname(file_path)
    
    # Ensure the directory and file exist
    ensure_directory_exists(search_log_dir)
    ensure_file_exists(file_path)

    # Change directory to the git repository
    os.chdir(repo_dir)

    # Add the file to staging
    subprocess.run(['git', 'add', file_path], check=True)

    # Commit the changes
    commit_message = f"Update search log {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    subprocess.run(['git', 'commit', '-m', commit_message], check=True)

    # Push the changes to the remote repository
    subprocess.run(['git', 'push'], check=True)

# Streamlit app setup
def render_search_box():
    search_term = st.text_input("Search Item Description", "")
    search_term = search_term.lower()
    corrected_search_term = search_nlp_correction(search_term)

    # Log search and commit to GitHub
    log_search(corrected_search_term)
    commit_and_push_to_github(SEARCH_LOG_FILE)

    if search_term:
        files = list_files()
        if files:
            all_data = pd.concat([process_data(load_data(os.path.join(UPLOAD_DIR, file))) for file in files if
                                  load_data(os.path.join(UPLOAD_DIR, file)) is not None], ignore_index=True)
            result_data = search_data(all_data, search_term)

            if not result_data.empty:
                styled_data = result_data.style.apply(color_banded_rows, axis=1)
                st.dataframe(styled_data, use_container_width=True, hide_index=True)
            else:
                st.write("No matching items found.")
        else:
            st.write("No files available. Please upload a file via the Admin Panel.")
    return search_term

def log_search(search_term):
    # Load existing search log data
    if os.path.isfile(SEARCH_LOG_FILE):
        search_log = pd.read_csv(SEARCH_LOG_FILE)
    else:
        search_log = pd.DataFrame(columns=["Search Term", "Count", "Last Searched"])

    # Update search log
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if search_term in search_log["Search Term"].values:
        search_log.loc[search_log["Search Term"] == search_term, "Count"] += 1
        search_log.loc[search_log["Search Term"] == search_term, "Last Searched"] = now
    else:
        new_entry = pd.DataFrame({"Search Term": [search_term], "Count": [1], "Last Searched": [now]})
        search_log = pd.concat([search_log, new_entry], ignore_index=True)

    search_log.to_csv(SEARCH_LOG_FILE, index=False)

# Sample functions to be integrated
def search_nlp_correction(search_term):
    # Placeholder for NLP correction function
    return search_term

def list_files():
    return os.listdir(UPLOAD_DIR)

def load_data(file):
    try:
        if file.endswith('.xlsx'):
            data = pd.read_excel(file, engine='openpyxl')
        elif file.endswith('.xls'):
            data = pd.read_excel(file, engine='xlrd')
        else:
            st.error(f"Unsupported file format: {file}")
            return None
    except Exception as e:
        st.error(f"Error loading file {os.path.basename(file)}: {e}")
        return None
    return data

def process_data(data):
    required_columns = ['Index No', 'Item Description', 'RRATE', 'Closing']
    if not all(col in data.columns for col in required_columns):
        st.error(f"Missing required columns in data.")
        return pd.DataFrame()  # Return empty DataFrame

    data = data[~(data[required_columns].isnull().all(axis=1) | (data[required_columns] == 0).all(axis=1))]
    data = data[required_columns]
    data = data.rename(columns={'RRATE': 'Price'})
    data.reset_index(drop=True, inplace=True)
    data.index += 1
    data.index.name = 'S.No'
    data.reset_index(inplace=True)
    data['Price'] = pd.to_numeric(data['Price'], errors='coerce')
    data['Price'] = data['Price'].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else '0.00')
    data['Available'] = data['Closing'].apply(lambda x: 'Yes' if pd.notnull(x) and x != 0 else 'No')
    data = data.drop(columns=['Closing'])
    return data

def search_data(data, search_term):
    if search_term:
        pattern = f"{search_term}"
        return data[data['Item Description'].str.contains(pattern, case=False, na=False, regex=True)]
    return data

def color_banded_rows(row):
    return [
        'background-color: #f9f5e3; color: #333333' if row.name % 2 == 0 else 'background-color: #ffffff; color: #333333'] * len(
        row)

# Streamlit UI logic (for reference, should be integrated with the rest of your app)
if st.session_state.page == "admin":
    # Admin panel code here...
    pass

elif st.session_state.page == "demand":
    # Demand form code here...
    pass

else:
    # Default view code here...
    pass

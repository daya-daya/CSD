import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime
from search_tracking import log_search, search_nlp_correction, get_previous_searches

# Define your admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Anildaya"

# Directory to store uploaded files
UPLOAD_DIR = "uploaded_files"
DEMAND_DIR = "Demand_stock"
SEARCH_LOG_DIR = "search_log"

# Ensure the directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DEMAND_DIR, exist_ok=True)
os.makedirs(SEARCH_LOG_DIR, exist_ok=True)

def download_demand_data():
    demand_files = os.listdir(DEMAND_DIR)
    if demand_files:
        for demand_file in demand_files:
            file_path = os.path.join(DEMAND_DIR, demand_file)
            with open(file_path, "rb") as f:
                st.download_button(
                    label=f"Download {demand_file}",
                    data=f,
                    file_name=demand_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"download_{demand_file}"  # Unique key for each file
                )
    else:
        st.write("No demand data available to download.")

def download_search_log():
    log_files = os.listdir(SEARCH_LOG_DIR)
    if log_files:
        for log_file in log_files:
            file_path = os.path.join(SEARCH_LOG_DIR, log_file)
            with open(file_path, "rb") as f:
                st.download_button(
                    label="Download Search Log",
                    data=f,
                    file_name="search_log.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_search_log"  # Unique key
                )
    else:
        st.write("No search log data available to download.")

def remove_extension(file_name):
    return os.path.splitext(file_name)[0]

def authenticate(username, password):
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD

def save_uploaded_file(uploaded_file):
    # Get the current date in 'DD-MM-YYYY' format
    current_date = datetime.now().strftime("%d-%m-%Y")
    new_file_name = f"CANTEEN_STOCK_SUMMARY_{current_date}.xlsx"
    file_path = os.path.join(UPLOAD_DIR, new_file_name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def delete_uploaded_file(file_name):
    file_path = os.path.join(UPLOAD_DIR, file_name)
    if os.path.exists(file_path):
        os.remove(file_path)

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

    # Check for missing required columns
    if not all(col in data.columns for col in required_columns):
        st.error("Missing required columns in data.")
        return pd.DataFrame()  # Return empty DataFrame

    # Remove rows with None or special characters in required columns
    data = data.dropna(subset=required_columns)
    data = data[~data['Index No'].apply(lambda x: re.search(r'[^\w\s]', str(x)))]
    data = data[~data['Item Description'].apply(lambda x: re.search(r'[^\w\s]', str(x)))]

    # Format 'RRATE'
    data['Price'] = data['RRATE'].apply(lambda x: f"{float(x):.2f}" if pd.notnull(x) and x != 0 else 'Soon Available')

    # Determine availability
    data['Available'] = data['Closing'].apply(lambda x: 'YES' if pd.notnull(x) and x != 0 else 'AVAILABLE SOON')

    data = data[['Index No', 'Item Description', 'Price', 'Available']]
    data.reset_index(drop=True, inplace=True)
    data.index += 1
    data.index.name = 'S.No'
    data.reset_index(inplace=True)

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

def render_demand_form():
    with st.form(key='demand_form'):
        service_no = st.text_input("Service No.")
        name = st.text_input("Name")
        product_name = st.text_input("Product Name")
        quantity = st.number_input("Quantity", min_value=1)
        mobile_no = st.text_input("Mobile No.")
        alternate_no = st.text_input("Alternate No. (optional)", "")
        address = st.text_area("Address")
        image = st.file_uploader("Image (optional)", type=['jpg', 'png', 'jpeg'], label_visibility="collapsed")

        submit_button = st.form_submit_button("Submit")

        if submit_button:
            if not (service_no, name, product_name, quantity, mobile_no, address):
                st.error("Please fill in all required fields.")
                return

            data = pd.DataFrame({
                "S/No.": [1],
                "Service No.": [service_no],
                "Name": [name],
                "Product Name": [product_name],
                "Quantity": [quantity],
                "Mobile No.": [mobile_no],
                "Alternate No.": [alternate_no],
                "Address": [address],
                "Image": [image.name if image else ""]
            })

            save_demand_data(data)

def render_search_box():
    previous_searches = get_previous_searches()
    search_term = st.text_input("Search Item Description", "")
    corrected_term = search_nlp_correction(search_term, previous_searches)
    updated_searches = log_search(corrected_term)

    if search_term:
        files = list_files()
        if files:
            all_data = pd.concat([process_data(load_data(os.path.join(UPLOAD_DIR, file))) for file in files if
                                  load_data(os.path.join(UPLOAD_DIR, file)) is not None], ignore_index=True)
            result_data = search_data(all_data, corrected_term)

            if not result_data.empty:
                styled_data = result_data.style.apply(color_banded_rows, axis=1)
                st.dataframe(styled_data, use_container_width=True, hide_index=True)
            else:
                st.write("No matching items found.")
        else:
            st.write("No files available. Please upload a file via the Admin Panel.")

    return search_term

# Main Application Logic
if st.session_state.page == "admin":
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.sidebar.header("Admin Login")
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")

        if st.sidebar.button("Login"):
            if authenticate(username, password):
                st.session_state.logged_in = True
                st.sidebar.success("Logged in successfully!")
            else:
                st.sidebar.error("Invalid username or password.")
    else:
        st.sidebar.header("Admin Panel")
        if st.button("Download Search Log"):
            download_search_log()
        if st.button("Download Demand Data"):
            download_demand_data()
        st.sidebar.subheader("Upload File")
        uploaded_file = st.sidebar.file_uploader("Upload your Excel file", type=["xlsx", "xls"])

        if uploaded_file:
            file_path = save_uploaded_file(uploaded_file)
            st.sidebar.success(f"File uploaded: {uploaded_file.name}")

        st.sidebar.subheader("Delete File")
        files = list_files()
        if files:
            file_to_delete = st.sidebar.selectbox("Select file to delete", files)

            if st.sidebar.button("Delete File"):
                delete_uploaded_file(file_to_delete)
                st.sidebar.success(f"File deleted: {file_to_delete}")
else:
    # Display data from the uploaded files directory
    files = list_files()
    if files:
        render_search_box()

        for file in files:
            st.write(f"### {remove_extension(file)}")
            data = load_data(os.path.join(UPLOAD_DIR, file))
            if data is not None:
                processed_data = process_data(data)
                styled_data = processed_data.style.apply(color_banded_rows, axis=1)
                st.dataframe(styled_data, use_container_width=True, hide_index=True)
    else:
        st.write("No files available. Please upload a file via the Admin Panel.")

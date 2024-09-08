import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime
from search_tracking import log_search, search_nlp_correction, get_previous_searches

# Define your admin credentials (for simplicity, hard-coded here)
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

    # Rename the file to 'CANTEEN_STOCK_SUMMARY_<current_date>.xlsx'
    new_file_name = f"CANTEEN_STOCK_SUMMARY_{current_date}.xlsx"
    file_path = os.path.join(UPLOAD_DIR, new_file_name)

    # Delete all existing files in the directory before saving the new one
    for file in list_files():
        delete_uploaded_file(file)

    # Save the file with the new name
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

    # Define a function to check for special characters
    def has_special_characters(value):
        if isinstance(value, str):
            return bool(re.search(r'[^\w\s]', value))
        return False

    # Remove rows with None or special characters in required columns
    data = data.dropna(subset=required_columns)  # Drop rows with NaN values in required columns
    data = data[~data['Index No'].apply(has_special_characters)]  # Drop rows with special characters in 'Index No'
    data = data[~data['Item Description'].apply(
        has_special_characters)]  # Drop rows with special characters in 'Item Description'

    # Define a function to safely convert and format 'RRATE'
    def format_price(value):
        try:
            if pd.notnull(value) and value != 0:
                return f"{float(value):.2f}"  # Convert to float and format
            else:
                return 'Soon Available'
        except ValueError:
            return 'Soon Available'

    # Apply the format function to 'RRATE'
    data['Price'] = data['RRATE'].apply(format_price)

    # Determine availability
    data['Available'] = data['Closing'].apply(lambda x: 'YES' if pd.notnull(x) and x != 0 else 'AVAILABLE SOON')

    # Select only the required columns
    data = data[['Index No', 'Item Description', 'Price', 'Available']]

    # Reset index and adjust index to start from 1
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

def save_demand_data(new_data):
    today = datetime.now()
    next_day = today + pd.DateOffset(days=1)
    date_str = next_day.strftime("%Y-%m-%d")
    file_name = f"Demand_{date_str}.xlsx"
    file_path = os.path.join(DEMAND_DIR, file_name)

    # If file exists, read existing data
    if os.path.exists(file_path):
        existing_data = pd.read_excel(file_path, engine='openpyxl')
        # Determine the next serial number
        max_serial_no = existing_data["S/No."].max()
        new_data["S/No."] = range(max_serial_no + 1, max_serial_no + 1 + len(new_data))
        combined_data = pd.concat([existing_data, new_data], ignore_index=True)
    else:
        # If file does not exist, initialize serial numbers
        new_data["S/No."] = range(1, len(new_data) + 1)
        combined_data = new_data

    # Save the updated data to the file
    combined_data.to_excel(file_path, index=False, engine='openpyxl')
    st.success(f"Demand data saved to {file_path}")

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
            if not (service_no and name and product_name and quantity and mobile_no and address):
                st.error("Please fill in all required fields.")
                return

            data = pd.DataFrame({
                "S/No.": [1],  # Adjust this if you need a proper sequence
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

# Application Logic
st.markdown("""
    <marquee behavior="scroll" direction="left" scrollamount="8" style="color:red;font-weight:bold;background-color:yellow">
        CANTEEN TIMINGS: 09:00-12:45 AND 14:00-18:00 FRIDAY HALFDAY WORKING AND MONDAY WEEKLY OFF
        &nbsp;&nbsp;&nbsp;&nbsp;
        CANTEEN TIMINGS: 09:00-12:45 AND 14:00-18:00 FRIDAY HALFDAY WORKING AND MONDAY WEEKLY OFF
    </marquee>
""", unsafe_allow_html=True)

st.markdown(f"""
    <style>
        .header-container {{
           background-image: linear-gradient(to right, #4caf50, #4caf50);
            padding: 20px;
            text-align: center;
            color: white;
            border-radius: 20px;
        }}
        .header-container h1 {{
            font-size: 30px;
        }}
    </style>
    <div class="header-container">
        <h1>Welcome to the Canteen Management System</h1>
    </div>
""", unsafe_allow_html=True)

st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a page:", ["Landing Page", "Admin", "New Registration"])

if page == "Landing Page":
    st.image("centered_image.png", use_column_width=True)
    st.markdown("## Welcome to the Canteen Management System")
    st.write("Please use the sidebar to navigate to different sections.")
    st.write("**Options**:")
    st.write("1. [Admin Page](#admin)")
    st.write("2. [New Registration](#new-registration)")
    st.markdown("---")
    download_demand_data()
    download_search_log()

elif page == "Admin":
    st.title("Admin Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if authenticate(username, password):
            st.success("Login successful!")
            uploaded_file = st.file_uploader("Upload Canteen Stock Summary", type=['xlsx', 'xls'])
            if uploaded_file:
                file_path = save_uploaded_file(uploaded_file)
                st.write(f"File uploaded successfully: {os.path.basename(file_path)}")

                # Load and process the new data
                data = load_data(file_path)
                if data is not None:
                    processed_data = process_data(data)
                    st.write("Processed Data:")
                    st.dataframe(processed_data.style.apply(color_banded_rows, axis=1))

                    # Save to demand data
                    if st.button("Save to Demand Data"):
                        save_demand_data(processed_data)

            st.write("**Search**")
            search_term = st.text_input("Search Item")
            if st.button("Search"):
                if not search_term:
                    st.warning("Please enter a search term.")
                else:
                    # Correct the search term and log the search
                    corrected_term = search_nlp_correction(search_term)
                    log_search(corrected_term)
                    
                    # Perform search on the processed data
                    searched_data = search_data(processed_data, corrected_term)
                    st.write(f"Search Results for '{corrected_term}':")
                    st.dataframe(searched_data.style.apply(color_banded_rows, axis=1))

        else:
            st.error("Invalid username or password.")

elif page == "New Registration":
    st.title("New Registration Form")
    render_demand_form()


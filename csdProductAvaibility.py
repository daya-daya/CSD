import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime
from search_tracking import log_search, search_nlp_correction, get_previous_searches

# Define your admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Anildaya"

# Directories to store files
UPLOAD_DIR = "uploaded_files"
DEMAND_DIR = "Demand_stock"
SEARCH_LOG_DIR = "search_log"

# Ensure the directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DEMAND_DIR, exist_ok=True)
os.makedirs(SEARCH_LOG_DIR, exist_ok=True)

def download_file(directory, label):
    files = os.listdir(directory)
    if files:
        for file in files:
            file_path = os.path.join(directory, file)
            with open(file_path, "rb") as f:
                st.download_button(
                    label=f"{label} {file}",
                    data=f,
                    file_name=file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"download_{file}"
                )
    else:
        st.write(f"No {label.lower()} data available to download.")

def authenticate(username, password):
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD

def save_uploaded_file(uploaded_file):
    for file in list_files(UPLOAD_DIR):
        delete_uploaded_file(file)

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

def list_files(directory):
    return os.listdir(directory)

def load_data(file):
    try:
        return pd.read_excel(file, engine='openpyxl') if file.endswith('.xlsx') else pd.read_excel(file, engine='xlrd')
    except Exception as e:
        st.error(f"Error loading file {os.path.basename(file)}: {e}")
        return None

def process_data(data):
    required_columns = ['Index No', 'Item Description', 'RRATE', 'Closing']

    if not all(col in data.columns for col in required_columns):
        st.error("Missing required columns in data.")
        return pd.DataFrame()

    def has_special_characters(value):
        return isinstance(value, str) and bool(re.search(r'[^\w\s]', value))

    data = data.dropna(subset=required_columns)
    data = data[~data['Index No'].apply(has_special_characters)]
    data = data[~data['Item Description'].apply(has_special_characters)]

    def format_price(value):
        try:
            return f"{float(value):.2f}" if pd.notnull(value) and value != 0 else 'Soon Available'
        except ValueError:
            return 'Soon Available'

    data['Price'] = data['RRATE'].apply(format_price)
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
    return ['background-color: #f9f5e3; color: #333333' if row.name % 2 == 0 else 'background-color: #ffffff; color: #333333'] * len(row)

def save_demand_data(new_data):
    today = datetime.now()
    next_day = today + pd.DateOffset(days=1)
    date_str = next_day.strftime("%Y-%m-%d")
    file_name = f"Demand_{date_str}.xlsx"
    file_path = os.path.join(DEMAND_DIR, file_name)

    if os.path.exists(file_path):
        existing_data = pd.read_excel(file_path, engine='openpyxl')
        max_serial_no = existing_data["S/No."].max()
        new_data["S/No."] = range(max_serial_no + 1, max_serial_no + 1 + len(new_data))
        combined_data = pd.concat([existing_data, new_data], ignore_index=True)
    else:
        new_data["S/No."] = range(1, len(new_data) + 1)
        combined_data = new_data

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

# Application Logic
st.markdown("""
    <marquee behavior="scroll" direction="left" scrollamount="8" style="color:red;font-weight:bold;background-color:yellow">
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
        .header-title {{
            font-size: 2.5em;
            font-family: 'Trebuchet MS', sans-serif;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .header-subtitle {{
            font-size: 1.5em;
            font-family: 'Trebuchet MS', sans-serif;
        }}
        .sidebar .sidebar-content {{
            background-color: #3a6186;
            color: white;
        }}
        .sidebar .block-container {{
            padding: 1rem;
        }}
        .stButton>button {{
            background-color: #ff5722;
            color: white;
            border-radius: 10px;
            font-weight: bold;
        }}
        .stTextInput>div>div>input {{
            border-radius: 5px;
            border: 2px solid #ff5722;
        }}
        .stDataFrame>div {{
            background-color: #ffffff;
            border: 2px solid #ff5722;
            border-radius: 10px;
            color: #333333;
        }}
        @media (prefers-color-scheme: dark) {{
            body {{
                background-color: #1a1a1a;
                color: #f5f5f5;
            }}
            .header-container {{
                color: #f5f5f5;
            }}
            .sidebar .sidebar-content {{
                background-color: #333333;
            }}
            .stButton>button {{
                background-color: #ff6f61;
                color: #f5f5f5;
            }}
            .stTextInput>div>div>input {{
                background-color: #333333;
                color: #f5f5f5;
            }}
            .stDataFrame>div {{
                background-color: #2e2e2e;
                color: #f5f5f5;
            }}
            .stDataFrame>div .dataframe-row {{
                background-color: #333333 !important;
                color: #f5f5f5 !important;
            }}
        }}
        @

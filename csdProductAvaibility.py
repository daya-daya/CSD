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

# Ensure the directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DEMAND_DIR, exist_ok=True)
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
    SEARCH_LOG_DIR = "search_log"
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
    # Delete all existing files in the directory before saving the new one
    for file in list_files():
        delete_uploaded_file(file)

    # Get the current date in 'DD-MM-YYYY' format
    current_date = datetime.now().strftime("%d-%m-%Y")

    # Rename the file to 'CANTEEN_STOCK_SUMMARY_<current_date>.xlsx'
    new_file_name = f"CANTEEN_STOCK_SUMMARY_{current_date}.xlsx"
    file_path = os.path.join(UPLOAD_DIR, new_file_name)

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
    #print(data)

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
            color: #333333; /* Ensure text color is dark gray */
        }}
        @media (prefers-color-scheme: dark) {{
            body {{
                background-color: #1a1a1a; /* Dark background color */
                color: #f5f5f5; /* Light text color for dark mode */
            }}
            .header-container {{
                color: #f5f5f5; /* Light text in header for dark mode */
            }}
            .sidebar .sidebar-content {{
                background-color: #333333; /* Dark sidebar background */
            }}
            .stButton>button {{
                background-color: #ff6f61; /* Slightly brighter button for dark mode */
                color: #f5f5f5; /* Light button text */
            }}
            .stTextInput>div>div>input {{
                background-color: #333333; /* Dark input background */
                color: #f5f5f5; /* Light input text */
            }}
            .stDataFrame>div {{
                background-color: #2e2e2e; /* Dark DataFrame background */
                color: #f5f5f5; /* Light DataFrame text */
            }}
            .stDataFrame>div .dataframe-row {{
                background-color: #333333 !important; /* Darker row background */
                color: #f5f5f5 !important; /* Light row text */
            }}
        }}
        /* Ensure visibility on small screens */
        @media only screen and (max-width: 600px) {{
            .stDataFrame>div {{
                color: #f5f5f5 !important; /* Ensure light text on mobile in dark mode */
                background-color: #2e2e2e !important; /* Darker background for visibility */
            }}
            .stDataFrame>div .dataframe-row {{
                color: #f5f5f5 !important; /* Ensure light text on mobile in dark mode */
                background-color: #333333 !important; /* Darker row background */
            }}
        }}
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="header-container">
        <div class="header-title"><b>UNIT RUN CANTEEN</b></div>
        <div class="header-subtitle"><b>THE PARACHUTE REGIMENT TRAINING CENTRE</b></div>
    </div>
""", unsafe_allow_html=True)

# Initialize session state for page navigation
if 'page' not in st.session_state:
    st.session_state.page = "home"

# Page Navigation
col1, col2 = st.columns([1, 3])
with col1:
    if st.button("Admin"):
        st.session_state.page = "admin"
with col2:
    if st.button("Demand"):
        st.session_state.page = "demand"


# Common Search Box
def render_search_box():
    # Fetch previous searches
    previous_searches = get_previous_searches()

    # Get the search term from the user
    search_term = st.text_input("Search Item Description", "")


    # Correct the search term based on previous searches
    corrected_term = search_nlp_correction(search_term, previous_searches)

    # Log the search and get updated search terms
    updated_searches = log_search(corrected_term)
    #print(updated_searches)
    if search_term:
        files = list_files() # Implement list_files to get files in UPLOAD_DIR
        #print(files)
        if files:
            all_data = pd.concat([process_data(load_data(os.path.join(UPLOAD_DIR, file))) for file in files if
                                  load_data(os.path.join(UPLOAD_DIR, file)) is not None], ignore_index=True)
            result_data = search_data(all_data, updated_searches)
            print(all_data)
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
        if st.button("Download_demand_data"):
            download_demand_data()
        st.sidebar.subheader("Upload File")
        uploaded_file = st.sidebar.file_uploader("Upload your Excel file", type=["xlsx", "xls"])

        if uploaded_file is not None:
            file_path = save_uploaded_file(uploaded_file)
            st.session_state.file_path = file_path
            st.sidebar.success(f"File uploaded: {uploaded_file.name}")

        st.sidebar.subheader("Delete File")
        files = list_files()
        if files:
            file_to_delete = st.sidebar.selectbox("Select file to delete", files)

            if st.sidebar.button("Delete File"):
                delete_uploaded_file(file_to_delete)
                st.sidebar.success(f"File deleted: {file_to_delete}")
                if 'file_path' in st.session_state and file_to_delete == os.path.basename(st.session_state.file_path):
                    st.session_state.pop('file_path', None)
        else:
            st.sidebar.write("No files to delete.")

        # Show data if a file has been uploaded
        if 'file_path' in st.session_state:
            st.write("Welcome to the CSD PRTC!")
            files = list_files()

            if files:
                render_search_box()

                for file in files:
                    st.write(f"### {remove_extension(file)}")  # Display the file name without extension
                    data = load_data(os.path.join(UPLOAD_DIR, file))
                    if data is not None:
                        processed_data = process_data(data)
                        styled_data = processed_data.style.apply(color_banded_rows, axis=1)
                        st.dataframe(styled_data, use_container_width=True, hide_index=True)

            else:
                st.write("No files available. Please upload a file via the Admin Panel.")
            processed_data = process_data(load_data(st.session_state.file_path))
            render_search_box()

elif st.session_state.page == "demand":
    render_demand_form()


else:
    # Display data from the uploaded_files directory
    files = list_files()

    if files:
        render_search_box()

        for file in files:
            st.write(f"### {remove_extension(file)}")  # Display the file name without extension
            data = load_data(os.path.join(UPLOAD_DIR, file))
            if data is not None:
                processed_data = process_data(data)
                styled_data = processed_data.style.apply(color_banded_rows, axis=1)
                st.dataframe(styled_data, use_container_width=True, hide_index=True)

    else:
        st.write("No files available. Please upload a file via the Admin Panel.")
# Include this in your Streamlit app to add a responsive footer with a "Contact Us" heading

st.markdown("""
    <style>
        /* Footer styling */
        .footer-container {
            background-color: #4caf50;
            color: white;
            padding: 20px;
            text-align: center;
            border-top: 2px solid #333333;
        }
        .footer-heading {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
            color: white; /* Highlight color */
        }
        .footer-content {
            display: flex;
            justify-content: center;
            align-items: center;
            flex-wrap: wrap;
        }
        .footer-content a {
            color: white;
            margin: 0 15px;
            text-decoration: none;
            font-size: 24px;
            transition: color 0.3s;
        }
        .footer-content a:hover {
            color: #ff5722;
        }
        /* Responsive design */
        @media (max-width: 600px) {
            .footer-heading {
                font-size: 20px;
            }
            .footer-content a {
                font-size: 20px;
                margin: 0 10px;
            }
        }
    </style>

    <div class="footer-container">
        <div class="footer-heading">Contact Us</div>
        <div class="footer-content">
            <a href="https://chat.whatsapp.com/JjZTkVRJ9cVJ0yCkvlaROx" target="_blank">
                <i class="fab fa-whatsapp"></i>
            </a>
            <a href="mailto:csd.prtc@gmail.com">
                <i class="fas fa-envelope"></i>
            </a>
        </div>
    </div>
""", unsafe_allow_html=True)
# Make sure to import Font Awesome in the header or use the existing inclusion
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">', unsafe_allow_html=True)

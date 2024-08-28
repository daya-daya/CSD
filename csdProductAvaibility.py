import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Define your admin credentials (for simplicity, hard-coded here)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Anildaya"

# Use a safe location for temporary storage (especially in cloud environments like Streamlit Cloud)
BASE_DIR = "/tmp" if os.getenv("IS_DEPLOYED") else os.getcwd()
UPLOAD_DIR = os.path.join(BASE_DIR, "uploaded_files")
DEMAND_DIR = os.path.join(BASE_DIR, "Demand_stock")

# Ensure the directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DEMAND_DIR, exist_ok=True)


def remove_extension(file_name):
    return os.path.splitext(file_name)[0]


def authenticate(username, password):
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD


def save_uploaded_file(uploaded_file):
    # Delete all existing files in the directory before saving the new one
    for file in list_files():
        delete_uploaded_file(file)

    # Now save the new uploaded file
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
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
    if not all(col in data.columns for col in required_columns):
        st.error(f"Missing required columns in data.")
        return pd.DataFrame()  # Return empty DataFrame

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


def save_demand_data(data):
    today = datetime.now()
    next_day = today + pd.DateOffset(days=1)
    date_str = next_day.strftime("%Y-%m-%d")
    file_name = f"Demand_{date_str}.xlsx"
    file_path = os.path.join(DEMAND_DIR, file_name)

    # Check if file already exists
    if os.path.exists(file_path):
        existing_data = pd.read_excel(file_path, engine='openpyxl')
        data = pd.concat([existing_data, data], ignore_index=True)

    data.to_excel(file_path, index=False, engine='openpyxl')
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
                background-color: #333333 !important; /* Darker row background for visibility */
            }}
        }}
    </style>
""", unsafe_allow_html=True)

st.sidebar.image("path/to/logo.png", use_column_width=True)
st.sidebar.title("Admin Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    if authenticate(username, password):
        st.success("Login successful!")
        st.sidebar.markdown("---")
        st.sidebar.markdown("### Upload Data File")
        uploaded_file = st.sidebar.file_uploader("Choose a file", type=['xlsx', 'xls'])

        if uploaded_file is not None:
            file_path = save_uploaded_file(uploaded_file)
            st.sidebar.markdown("File saved successfully!")

            data = load_data(file_path)
            if data is not None:
                st.dataframe(data.style.apply(color_banded_rows, axis=1))

                search_term = st.text_input("Search by Item Description", "")
                filtered_data = search_data(data, search_term)

                st.dataframe(filtered_data.style.apply(color_banded_rows, axis=1))

                if st.button("Save to Demand Stock"):
                    save_demand_data(filtered_data)

                st.markdown("---")
                st.markdown("### Demand Form")
                render_demand_form()
            else:
                st.error("Failed to load data.")
        else:
            st.warning("Please upload a data file.")
    else:
        st.error("Invalid username or password.")

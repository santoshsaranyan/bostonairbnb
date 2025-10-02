import streamlit as st
from utilities.datascraper import scrape_data
from utilities.datapreprocessor import preprocess_data
from utilities.dbloader import load_data


st.set_page_config(page_title="Boston AirBnB Data Pipeline", layout="wide", page_icon="🏠")

st.title("🏘️ Boston AirBnB Data Pipeline")

with st.sidebar:
    st.image("https://t3.ftcdn.net/jpg/05/89/24/50/360_F_589245011_2eyvpGgTRGZT3Hw4ScUj9QPwvOLp3XsQ.jpg", width=100)
    st.sidebar.title("About")
    st.markdown("""
    This application demonstrates a complete data pipeline for Boston AirBnB listings, including data scraping, preprocessing, and loading into a MySQL database. The pipeline consists of three main steps:
    1. **Data Scraping**: Fetches the latest AirBnB data from [InsideAirBnB](http://insideairbnb.com/get-the-data/) and downloads the relevant CSV files.
    2. **Data Preprocessing**: Cleans and preprocesses the downloaded data to ensure it is ready for analysis and storage.
    3. **Database Loading**: Loads the cleaned data into a MySQL database for further analysis and querying.
    """)
    
        
    st.markdown("""
    ### Instructions to Run the Application
    1. Ensure you have Python installed on your machine.
    2. Install the required libraries using pip: `pip install -r requirements.txt`
    3. Set up a MySQL database and update the connection details in the environment variables.env file.
    4. Run the Streamlit application using the command: `streamlit run BostonBnBApp.py`
    5. Click the "Run Data Pipeline" button to execute the entire data pipeline.
    """)

    st.markdown("""
    ### Note
    - Ensure that your MySQL server is running and accessible.
    - The application uses environment variables to manage sensitive information like database credentials. Make sure to set these up correctly before running the application.
    """)
    

if "step1_done" not in st.session_state:
    st.session_state.step1_done = False
if "step2_done" not in st.session_state:
    st.session_state.step2_done = False
if "step3_done" not in st.session_state:
    st.session_state.step3_done = False
    
st.header("Step-by-Step Pipeline")

# Step 1: Data Scraper
with st.expander("Step 1: Data Scraper", expanded=True):
    if st.session_state.step1_done:
        st.success("✅ Data scraping completed")
    else:
        if st.button("Run Data Scraper"):
            with st.spinner("Scraping data..."):
                scrape_data()
                st.session_state.step1_done = True
            st.success("✅ Data scraping completed")

# Step 2: Data Preprocessor
with st.expander("Step 2: Data Preprocessor", expanded=st.session_state.step1_done):
    if not st.session_state.step1_done:
        st.info("Complete Step 1 first")
    elif st.session_state.step2_done:
        st.success("✅ Data preprocessing completed")
    else:
        if st.button("Run Data Preprocessor"):
            with st.spinner("Preprocessing data..."):
                preprocess_data()
                st.session_state.step2_done = True
            st.success("✅ Data preprocessing completed")

# Step 3: DB Loader
with st.expander("Step 3: DB Loader", expanded=st.session_state.step2_done):
    if not st.session_state.step2_done:
        st.info("Complete Step 2 first")
    elif st.session_state.step3_done:
        st.success("✅ Data loading completed")
    else:
        if st.button("Run DB Loader"):
            with st.spinner("Loading data into the database..."):
                load_data()
                st.session_state.step3_done = True
            st.success("✅ Data loading completed")
    

    


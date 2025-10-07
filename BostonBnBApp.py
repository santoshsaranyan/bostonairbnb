import streamlit as st
from utilities.datascraper import scrape_data
from utilities.datapreprocessor import preprocess_data
from utilities.dbloader import load_data
import utilities.streamlithtml as htmllib
import os

st.set_page_config(page_title="Boston AirBnB Data Pipeline", layout="wide", page_icon="🏠")

st.title("🏘️ Boston AirBnB Data Pipeline")

with st.sidebar:
    st.image("https://t3.ftcdn.net/jpg/05/89/24/50/360_F_589245011_2eyvpGgTRGZT3Hw4ScUj9QPwvOLp3XsQ.jpg", width=150)
    st.sidebar.title("About")
    st.markdown("""
    This application demonstrates a complete data pipeline for Boston AirBnB listings, including data scraping, preprocessing, and loading into a MySQL database. The pipeline consists of three main steps:
    1. **Data Scraping**: Fetches the latest AirBnB data from [InsideAirBnB](http://insideairbnb.com/get-the-data/) and downloads the relevant CSV files. The data is generated quarterly by the source and is of the last 12 months.
    2. **Data Preprocessing**: Cleans and preprocesses the downloaded data to ensure it is ready for analysis and storage.
    3. **Database Loading**: Loads the cleaned data into a MySQL database for further analysis and querying.
    """)
    
    
for step in ["step1_done", "step2_done", "step3_done"]:
    if step not in st.session_state:
        st.session_state[step] = False


st.markdown(htmllib.html_2, unsafe_allow_html=True)

# Header
st.markdown("<div class='pipeline-title'>Data Pipeline</div>", unsafe_allow_html=True)
st.markdown("<div class='pipeline-sub'>Follow the steps to scrape, preprocess, and load data.</div>", unsafe_allow_html=True)

download_folder = "data/downloads"
if os.path.exists(download_folder) and len(os.listdir(download_folder)) > 0:
    st.session_state.step1_done = True
    st.info("✅ Step 1 files already exist in the folder. You can proceed to Step 2.")
    
cleaned_folder = "data/cleaned"
if os.path.exists(cleaned_folder) and len(os.listdir(cleaned_folder)) > 0:
    st.session_state.step2_done = True
    st.info("✅ Step 2 files already exist in the folder. You can proceed to Step 3.")
    
# Progress Bar
completed = sum([st.session_state.step1_done,
                 st.session_state.step2_done,
                 st.session_state.step3_done])
progress_pct = int((completed / 3) * 100)
st.markdown(
    f"<div class='progress-container'><div class='progress-bar' style='width:{progress_pct}%;'></div></div>",
    unsafe_allow_html=True,
)

# Data Scraper
with st.expander("Step 1: Data Scraper", expanded=True):
    st.write("Collect data from the source.")
    if st.session_state.step1_done:
        st.success("✅ Scrape completed")
    if st.button("Run Scraper", key="step1_btn"):
        with st.spinner("Scraping data..."):
            scrape_data()
        st.session_state.step1_done = True
        st.rerun()

# Data Preprocessor
with st.expander("Step 2: Data Preprocessor", expanded=True):
    st.write("Clean and prepare the data for loading.")
    if st.session_state.step2_done:
        st.success("✅ Preprocessing completed")
    if st.button("Run Preprocessor", key="step2_btn"):
        with st.spinner("Preprocessing data..."):
            preprocess_data()
        st.session_state.step2_done = True
        st.rerun()

# DB Loader
with st.expander("Step 3: DB Loader", expanded=True):
    st.write("Load the processed data into the database.")
    if st.session_state.step3_done:
        st.success("✅ Load completed")
    if st.button("Run Loader", key="step3_btn"):
        with st.spinner("Loading data into DB..."):
            load_data()
        st.session_state.step3_done = True
        st.rerun()
   

st.markdown(htmllib.html_1, unsafe_allow_html=True)

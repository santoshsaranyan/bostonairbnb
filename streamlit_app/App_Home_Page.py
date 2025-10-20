import streamlit as st

st.set_page_config(page_title="Boston BnB Insights App", layout="wide", page_icon="🏠")

st.title("🏘️ Welcome to the Boston BnB Insights App!")


with st.sidebar:
   st.image("https://t3.ftcdn.net/jpg/05/89/24/50/360_F_589245011_2eyvpGgTRGZT3Hw4ScUj9QPwvOLp3XsQ.jpg", width=150)
   st.divider()

   st.header("How to Use")
   st.markdown("""
   1. Verify each pipeline step in order
   2. View processed insights and analytics 
   """)
   
   st.markdown("View the source code on [GitHub](https://github.com/santoshsaranyan/bostonairbnb)")

   st.divider()

   st.caption("Data Source: [InsideAirbnb](https://insideairbnb.com)")
   st.caption("Developed by: [Santosh Saranyan](https://www.linkedin.com/in/santosh-saranyan/)")
   st.caption("App Last updated: October 2025")
    
st.markdown(" This Streamlit app demonstrates a complete end-to-end **data engineering and analytics pipeline** for Boston Airbnb listings, built using **Python**, **PostgreSQL**, and **Docker**. ")

st.info("💡 *Navigate to the various pages using the top-left section of the sidebar* ")

st.subheader("🧱 ETL Pipeline Overview")

st.markdown("""
The whole ETL process is contained within a **Docker** container, and automated to run on a monthly schedule using **GitHub Actions**.
The pipeline consists of three main steps:
1. **Data Scraping**  
   Retrieves the latest Boston Airbnb datasets directly from [InsideAirbnb](https://insideairbnb.com), which provides data for the past 12 months updated quarterly.
2. **Data Preprocessing**  
   Cleans, standardizes, and prepares the data for storage and analysis — handling missing values, formatting columns, and optimizing the dataset for database loading.
3. **Database Loading**  
   Loads the raw and processed data into a **PostgreSQL** database (hosted by **Supabase**) for efficient querying and analytics. Also refreshes the materialized views to ensure up-to-date insights.
""")

st.subheader("📊 Analysis and Visualization")

st.markdown("""
Once loaded, the data is used to generate insights and interactive visualizations on:

   - The distribution and characteristics of Airbnb listings in Boston.
   - Host performance and review trends over time.
   - Neighborhood popularity and room type distribution.
   - Amenities offered and availability trends across listings. 
""")

st.subheader("⚙️ Technology Stack")

st.markdown("""
- **Python** - Data scraping, cleaning, and analysis
- **PostgreSQL** - Database management, hosted in Supabase
- **Docker** - Containerization for the ETL pipeline, Automated using GitHub Actions
- **Streamlit** - Interactive web interface, hosted on Streamlit Cloud
""")


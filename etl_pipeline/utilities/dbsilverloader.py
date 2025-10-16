import pandas as pd
import numpy as np
from sqlalchemy import create_engine, inspect, text
import logging
from dotenv import load_dotenv
import os
import time
import textwrap

# Set the path to the .env file

# Load the environment variables from the .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',handlers=[logging.FileHandler("logs/dbsilverloader.log"),logging.StreamHandler()])

# Get database credentials from environment variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

# Check if the environment variables are set
if not USER or not PASSWORD or not DBNAME or not HOST or not PORT:
    raise ValueError("Database credentials are not set in the .env file.")


"""
This script reads data from CSV files, and inserts the data into the PostgreSQL database.
It uses SQLAlchemy for help with database operations and pandas for data manipulation.
"""

def load_silver_data() -> None:
    
    start = time.time()
    
    # Creates a connection to a PostgreSQL database.
    connectionStr = f'postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require'
    PostgreSQLEngine = create_engine(connectionStr)
    logging.info("Connected to the PostgreSQL database successfully.")
    
    # Read data from CSV files and insert it into the database.
    insert_data_to_table(PostgreSQLEngine)
    
    end = time.time()
    
    logging.info(f"Script executed in {end - start:.2f} seconds.")
    
    

def read_data(filePath: str) -> pd.DataFrame:
    """
    Reads data from a CSV file and returns it as a pandas DataFrame.
    
    Parameters:
        filePath: Path to the CSV file.
        
    Returns:
        data: pandas DataFrame containing the data.
    """
    
    try:
        data = pd.read_csv(filePath)
        return data
    
    except Exception as e:
        logging.info(f"Error reading the file: {e}")
        return pd.DataFrame() 
    
    
    
def insert_data_to_table(engine) -> None:
    """
    Reads data from CSV files and inserts it into the database.
    
    Parameters:
        engine: SQLAlchemy engine object.
        
    Returns:
        None
    """
    
    # Read data from CSV files
    logging.info("Reading data from CSV files...")
    locationsData = read_data('data/cleaned/cleaned_locations.csv')
    hostsData = read_data('data/cleaned/cleaned_hosts.csv')
    listingsData = read_data('data/cleaned/cleaned_listings.csv')
    reviewsData = read_data('data/cleaned/cleaned_reviews.csv')
    amenitiesData = read_data('data/cleaned/cleaned_amenities.csv')
    listingAmenitiesData = read_data('data/cleaned/cleaned_listing_amenities.csv')
    availabilityData = read_data('data/cleaned/cleaned_availability.csv')
    logging.info("Data read successfully.")
    
    
    # Insert data into the database tables
    logging.info("Inserting data into the database...")
    if not locationsData.empty:
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE silver.bnb_dim_locations RESTART IDENTITY CASCADE;"))
            conn.commit()
        locationsData.to_sql('bnb_dim_locations', con=engine, schema='silver', if_exists='append', index=False)
        logging.info("Locations data truncated and inserted successfully.")
        
    if not hostsData.empty:
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE silver.bnb_dim_hosts RESTART IDENTITY CASCADE;"))
            conn.commit()
        hostsData.to_sql('bnb_dim_hosts', con=engine, schema='silver', if_exists='append', index=False)
        logging.info("Hosts data truncated and inserted successfully.")
        
        
    if not listingsData.empty:
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE silver.bnb_dim_listings RESTART IDENTITY CASCADE;"))
            conn.commit()
        listingsData.to_sql('bnb_dim_listings', con=engine, schema='silver', if_exists='append', index=False)
        logging.info("Listings data truncated and inserted successfully.")
        
    if not reviewsData.empty:
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE silver.bnb_fact_reviews RESTART IDENTITY CASCADE;"))
            conn.commit()
        reviewsData.to_sql('bnb_fact_reviews', con=engine, schema='silver', if_exists='append', index=False)
        logging.info("Reviews data truncated and inserted successfully.")
        
    if not amenitiesData.empty:
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE silver.bnb_dim_amenities RESTART IDENTITY CASCADE;"))
            conn.commit()
        amenitiesData.to_sql('bnb_dim_amenities', con=engine, schema='silver', if_exists='append', index=False)
        logging.info("Amenities data truncated and inserted successfully.")
        
        
    if not availabilityData.empty:
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE silver.bnb_fact_availability RESTART IDENTITY CASCADE;"))
            conn.commit()
        availabilityData.to_sql('bnb_fact_availability', con=engine, schema='silver', if_exists='append', index=False)
        logging.info("Availability data truncated and inserted successfully.")
    
    if not listingAmenitiesData.empty:
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE silver.bnb_br_listing_amenities RESTART IDENTITY CASCADE;"))
            conn.commit()
        listingAmenitiesData.to_sql('bnb_br_listing_amenities', con=engine, schema='silver', if_exists='append', index=False)
        logging.info("Listing amenities truncated and data inserted successfully.")
        
    else:
        logging.info("No data to insert into the database.")
    

if __name__ == "__main__":
    load_silver_data() 
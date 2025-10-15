import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import logging
from dotenv import load_dotenv
import os
import time
import json

# Load the environment variables from the .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler("logs/dbbronzeloader.log"), logging.StreamHandler()])

# Get database credentials from environment variables
user = os.getenv('user')
password = os.getenv('password')
db_name = os.getenv('db_name')

# Check if the environment variables are set
if not user or not password or not db_name:
    raise ValueError("Database credentials are not set in the .env file.")


"""
This script reads raw CSV files (listings, reviews, availability), and inserts the data
into the PostgreSQL bronze tables. It uses SQLAlchemy for database operations and pandas
for data manipulation. Each row is stored as JSONB in the raw_data column with a created_at timestamp.
"""

def load_bronze_data() -> None:
    
    start = time.time()
    
    # Creates a connection to a PostgreSQL database.
    connectionStr = f'postgresql+psycopg2://{user}:{password}@postgres:5432/{db_name}'
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
        data: DataFrame containing the data.
    """
    try:
        data = pd.read_csv(filePath, compression='gzip')
        return data
    
    except Exception as e:
        logging.info(f"Error reading the file {filePath}: {e}")
        return pd.DataFrame() 
    
    
def row_to_json_safe(row):
    """
    Convert a pandas row to a JSON string safely for PostgreSQL JSONB.
    - Replaces NaN/NaT/Inf with None (→ JSON null)
    - Converts numpy types to native Python types
    """
    row_dict = row.to_dict()
    safe_dict = {}
    for k, v in row_dict.items():
        if pd.isna(v) or v in [np.inf, -np.inf]:
            safe_dict[k] = None
        elif isinstance(v, (np.integer, np.int32, np.int64)):
            safe_dict[k] = int(v)
        elif isinstance(v, (np.floating, np.float32, np.float64)):
            safe_dict[k] = float(v)
        elif isinstance(v, np.bool_):
            safe_dict[k] = bool(v)
        else:
            safe_dict[k] = v
    return json.dumps(safe_dict)


def insert_data_to_table(engine) -> None:
    """
    Loads raw CSV files into bronze tables.
    """
    
    # Read data from CSV files
    listings_df = read_data("data/downloads/listings.csv.gz")
    reviews_df = read_data("data/downloads/reviews.csv.gz")
    calendar_df = read_data("data/downloads/calendar.csv.gz")
    
    # Insert data into bronze tables
    logging.info("Inserting data into the bronze tables...")

    if not listings_df.empty:
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE bronze.bnb_raw_listings RESTART IDENTITY CASCADE;"))
            conn.commit()
        listings_prepared = listings_df.copy()
        listings_prepared["raw_data"] = listings_prepared.apply(row_to_json_safe, axis=1)
        listings_prepared = listings_prepared[["raw_data"]]
        listings_prepared.to_sql('bnb_raw_listings', con=engine, schema='bronze', if_exists='append', index=False)
        logging.info("Listings data truncated and inserted successfully.")

    if not reviews_df.empty:
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE bronze.bnb_raw_reviews RESTART IDENTITY CASCADE;"))
            conn.commit()
        reviews_prepared = reviews_df.copy()
        reviews_prepared["raw_data"] = reviews_prepared.apply(row_to_json_safe, axis=1)
        reviews_prepared = reviews_prepared[["raw_data"]]
        reviews_prepared.to_sql('bnb_raw_reviews', con=engine, schema='bronze', if_exists='append', index=False)
        logging.info("Reviews data truncated and inserted successfully.")

    if not calendar_df.empty:
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE bronze.bnb_raw_availability RESTART IDENTITY CASCADE;"))
            conn.commit()
        calendar_prepared = calendar_df.copy()
        calendar_prepared["raw_data"] = calendar_prepared.apply(row_to_json_safe, axis=1)
        calendar_prepared = calendar_prepared[["raw_data"]]
        calendar_prepared.to_sql('bnb_raw_availability', con=engine, schema='bronze', if_exists='append', index=False)
        logging.info("Availability data truncated and inserted successfully.")

    else:
        logging.info("No data to insert into bronze tables.")


if __name__ == "__main__":
    load_bronze_data()

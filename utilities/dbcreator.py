import pandas as pd
import numpy as np
from sqlalchemy import create_engine, inspect, text
import logging
from dotenv import load_dotenv
import os
import time
import textwrap

# Set the path to the .env file
env_path = os.path.join(os.path.dirname(__file__), '.env')

print(env_path)

# Load the environment variables from the .env file
load_dotenv(dotenv_path=env_path)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get database credentials from environment variables
user = os.getenv('user')
password = os.getenv('password')
db_name = os.getenv('db_name')

# Check if the environment variables are set
if not user or not password or not db_name:
    raise ValueError("Database credentials are not set in the .env file.")


"""
This script creates a MySQL database and its tables, reads data from CSV files, and inserts the data into the database.
It uses SQLAlchemy for database operations and pandas for data manipulation.
"""

def main() -> None:
    
    start = time.time()
    
    # Creates a connection to a MySQL database.
    connectionStr = f'mysql+pymysql://{user}:{password}@127.0.0.1:3306/{db_name}'
    print(connectionStr)
    mySQLEngine = create_engine(connectionStr, echo=True)
    
    # # Create the database tables.
    create_all_tables(mySQLEngine)
    
    # Read data from CSV files and insert it into the database.
    insert_data_to_table(mySQLEngine)
    
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
    
    

def create_listings_table(engine) -> None:
    """
    Creates the listings table in the database.
    
    Parameters:
        engine: SQLAlchemy engine object.
    Returns:
        None
    """
    
    # Note: MySQL does not throw an error if the table already exists during table creation with the IF NOT EXISTS clause.
    # But, we still check for its existence anyway to log what is happening and also to avoid any unforseen bugs, as this will be used as part of an automated script.
     
    tableName = "listings"
    
    if table_exists(engine, tableName):
        logging.info(f"Table '{tableName}' exists.")
        
    else:
        logging.info(f"Table '{tableName}' does not exist.")
    
        listingsSchemaQuery = textwrap.dedent(f"""
        CREATE TABLE IF NOT EXISTS {tableName} (
        listing_id INTEGER PRIMARY KEY,
        listing_cid TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        host_id INTEGER NOT NULL,
        listing_url TEXT NOT NULL,
        location_id INTEGER NOT NULL,
        neighborhood_overview TEXT,
        picture_url TEXT,
        latitude FLOAT,
        longitude FLOAT,
        property_type TEXT,
        room_type TEXT,
        accommodates INTEGER,
        bathrooms FLOAT,
        bathroom_type TEXT,
        bedrooms INTEGER,
        beds INTEGER,
        amenities TEXT,
        license TEXT,
        overall_rating FLOAT CHECK(overall_rating >= 0 AND overall_rating <= 5),
        accuracy_rating FLOAT CHECK(accuracy_rating >= 0 AND accuracy_rating <= 5),
        cleanliness_rating FLOAT CHECK(cleanliness_rating >= 0 AND cleanliness_rating <= 5),
        checkin_rating FLOAT CHECK(checkin_rating >= 0 AND checkin_rating <= 5),
        communication_rating FLOAT CHECK(communication_rating >= 0 AND communication_rating <= 5),
        location_rating FLOAT CHECK(location_rating >= 0 AND location_rating <= 5),
        value_rating FLOAT CHECK(value_rating >= 0 AND value_rating <= 5),
        number_of_reviews INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (host_id) REFERENCES hosts(host_id),
        FOREIGN KEY (location_id) REFERENCES locations(location_id)
        );
        """)
        
        with engine.connect() as connection:
            connection.execute(text(listingsSchemaQuery))
            logging.info("Listings table created successfully.")

    

def create_reviews_table(engine) -> None:
    """
    Creates the reviews table in the database.
    
    Parameters:
        engine: SQLAlchemy engine object.
    
    Returns:
        None
    """
    
    # Note: MySQL does not throw an error if the table already exists during table creation with the IF NOT EXISTS clause.
    # But, we still check for its existence anyway to log what is happening and also to avoid any unforseen bugs, as this will be used as part of an automated script.
   
    tableName = "reviews"
    
    if table_exists(engine, tableName):
        logging.info(f"Table '{tableName}' exists.")
        
    else:
        logging.info(f"Table '{tableName}' does not exist.")
    
        reviewsSchemaQuery = textwrap.dedent(f"""
        CREATE TABLE IF NOT EXISTS {tableName} (
        review_id INTEGER PRIMARY KEY,
        review_cid TEXT NOT NULL,
        listing_id INTEGER NOT NULL,
        date DATE NOT NULL,
        reviewer_id TEXT NOT NULL,
        reviewer_name TEXT NOT NULL,
        comments TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (listing_id) REFERENCES listings(listing_id)
        );
        """)
        
        with engine.connect() as connection:
            connection.execute(text(reviewsSchemaQuery))
            logging.info("Reviews table created successfully.")
            

def create_amenities_table(engine) -> None:
    """
    Creates the amenities table in the database.
    
    Parameters:
        engine: SQLAlchemy engine object.
    
    Returns:
        None
    """
    
    # Note: MySQL does not throw an error if the table already exists during table creation with the IF NOT EXISTS clause.
    # But, we still check for its existence anyway to log what is happening and also to avoid any unforseen bugs, as this will be used as part of an automated script.
   
    tableName = "amenities"
    
    if table_exists(engine, tableName):
        logging.info(f"Table '{tableName}' exists.")
        
    else:
        logging.info(f"Table '{tableName}' does not exist.")
    
        reviewsSchemaQuery = textwrap.dedent(f"""
        CREATE TABLE IF NOT EXISTS {tableName} (
        amenity_id INTEGER PRIMARY KEY,
        amenity_name TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );
        """)
        
        with engine.connect() as connection:
            connection.execute(text(reviewsSchemaQuery))
            logging.info(f"{tableName} table created successfully.")
            

def create_listing_amenities_table(engine) -> None:
    """
    Creates the listing-amenities table in the database.
    
    Parameters:
        engine: SQLAlchemy engine object.
    
    Returns:
        None
    """
    
    # Note: MySQL does not throw an error if the table already exists during table creation with the IF NOT EXISTS clause.
    # But, we still check for its existence anyway to log what is happening and also to avoid any unforseen bugs, as this will be used as part of an automated script.
   
    tableName = "listing_amenities"
    
    if table_exists(engine, tableName):
        logging.info(f"Table '{tableName}' exists.")
        
    else:
        logging.info(f"Table '{tableName}' does not exist.")
    
        reviewsSchemaQuery = textwrap.dedent(f"""
        CREATE TABLE IF NOT EXISTS {tableName} (
        listing_id INTEGER NOT NULL,
        amenity_id INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (listing_id, amenity_id),
        FOREIGN KEY (listing_id) REFERENCES listings(listing_id),
        FOREIGN KEY (amenity_id) REFERENCES amenities(amenity_id)
        );
        """)
        
        with engine.connect() as connection:
            connection.execute(text(reviewsSchemaQuery))
            logging.info(f"{tableName} table created successfully.")
    


def create_hosts_table(engine) -> None:
    """
    Creates the hosts table in the database.
    
    Parameters:
        engine: SQLAlchemy engine object.
        
    Returns:
        None
    """
    
    # Note: MySQL does not throw an error if the table already exists during table creation with the IF NOT EXISTS clause.
    # But, we still check for its existence anyway to log what is happening and also to avoid any unforseen bugs, as this will be used as part of an automated script.
  
    
    tableName = "hosts"
    
    if table_exists(engine, tableName):
        logging.info(f"Table '{tableName}' exists.")
        
    else:
        logging.info(f"Table '{tableName}' does not exist.")
        
        hostsSchemaQuery = textwrap.dedent(f"""
        CREATE TABLE IF NOT EXISTS {tableName} (
        host_id INTEGER PRIMARY KEY,
        host_cid TEXT NOT NULL,
        host_name TEXT NOT NULL,
        host_url TEXT NOT NULL,
        host_since TEXT,
        location_id INTEGER NOT NULL,
        host_about TEXT,
        host_response_time TEXT,
        host_response_rate FLOAT CHECK(host_response_rate >= 0 AND host_response_rate <= 100),
        host_acceptance_rate FLOAT CHECK(host_acceptance_rate >= 0 AND host_acceptance_rate <= 100),
        host_is_superhost BOOLEAN,
        host_thumbnail_url TEXT,
        host_picture_url TEXT,
        host_total_listings_count INTEGER DEFAULT 0,
        host_verifications TEXT,
        host_has_profile_pic BOOLEAN,
        host_identity_verified BOOLEAN,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (location_id) REFERENCES locations(location_id)
        );
        """)
        
        with engine.connect() as connection:
            connection.execute(text(hostsSchemaQuery))
            logging.info("Hosts table created successfully.")
        
    
    
def create_locations_table(engine) -> None:
    """
    Creates the locations table in the database.
    
    Parameters:
        engine: SQLAlchemy engine object.
        
    Returns:
        None
    """
    
    # Note: MySQL does not throw an error if the table already exists during table creation with the IF NOT EXISTS clause.
    # But, we still check for its existence anyway to log what is happening and also to avoid any unforseen bugs, as this will be used as part of an automated script.
    
    tableName = "locations"
    
    if table_exists(engine, tableName):
        logging.info(f"Table '{tableName}' exists.")
        
    else:
        logging.info(f"Table '{tableName}' does not exist.")
        locationsSchemaQuery = textwrap.dedent(f"""
        CREATE TABLE IF NOT EXISTS {tableName} (
        location_id INTEGER PRIMARY KEY,
        location TEXT NOT NULL,
        neighborhood TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );
        """)
        
        with engine.connect() as connection:
            connection.execute(text(locationsSchemaQuery))
            logging.info("Locations table created successfully.")
    
    

def create_availability_table(engine) -> None:
    """
    Creates the availability table in the database.
    
    Parameters:
        engine: SQLAlchemy engine object.
        
    Returns:
        None
    """ 
    
    # Note: MySQL does not throw an error if the table already exists during table creation with the IF NOT EXISTS clause.
    # But, we still check for its existence anyway to log what is happening and also to avoid any unforseen bugs, as this will be used as part of an automated script.
   
    tableName = "availability"
    
    if table_exists(engine, tableName):
        logging.info(f"Table '{tableName}' exists.")
        
    else:
        logging.info(f"Table '{tableName}' does not exist.")
    
        availabilitySchemaQuery = textwrap.dedent(f"""
        CREATE TABLE IF NOT EXISTS {tableName} (
        listing_id INTEGER NOT NULL,
        date DATE NOT NULL,
        available BOOLEAN NOT NULL,
        minimum_nights INTEGER DEFAULT 1,
        maximum_nights INTEGER DEFAULT 365,
        price FLOAT CHECK(price >= 0),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (listing_id, date),
        FOREIGN KEY (listing_id) REFERENCES listings(listing_id)
        );
        """)
        
        with engine.connect() as connection:
            connection.execute(text(availabilitySchemaQuery))
            logging.info("Availability table created successfully.")
        
        

def create_all_tables(engine) -> None:
    """
    Creates all tables in the database.
    
    Parameters:
        engine: SQLAlchemy engine object.
        
    Returns:
        None
    """
    
    logging.info("Creating all tables in the database...")
    
    # Create all tables
    create_locations_table(engine)
    create_hosts_table(engine)
    create_listings_table(engine)
    create_reviews_table(engine)
    create_availability_table(engine)
    create_amenities_table(engine)
    create_listing_amenities_table(engine)
    
    logging.info("All tables created successfully.")
    
    
    
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
    listingsData = read_data('data/cleaned_listings.csv')
    reviewsData = read_data('data/cleaned_reviews.csv')
    hostsData = read_data('data/cleaned_hosts.csv')
    locationsData = read_data('data/cleaned_locations.csv')
    availabilityData = read_data('data/cleaned_availability.csv')
    amenitiesData = read_data('data/cleaned_amenities.csv')
    listingAmenitiesData = read_data('data/cleaned_listing_amenities.csv')
    logging.info("Data read successfully.")
    
    
    # Insert data into the database tables
    logging.info("Inserting data into the database...")
    if not locationsData.empty:
        locationsData.to_sql('locations', con=engine, if_exists='append', index=False)
        logging.info("Locations data inserted successfully.")
        
    if not hostsData.empty:
        hostsData.to_sql('hosts', con=engine, if_exists='append', index=False)
        logging.info("Hosts data inserted successfully.")
        
        
    if not listingsData.empty:
        listingsData.to_sql('listings', con=engine, if_exists='append', index=False)
        logging.info("Listings data inserted successfully.")
        
    if not reviewsData.empty:
        reviewsData.to_sql('reviews', con=engine, if_exists='append', index=False)
        logging.info("Reviews data inserted successfully.")
        
    if not amenitiesData.empty:
        amenitiesData.to_sql('amenities', con=engine, if_exists='append', index=False)
        logging.info("Amenities data inserted successfully.")
        
        
    if not availabilityData.empty:
        availabilityData.to_sql('availability', con=engine, if_exists='append', index=False)
        logging.info("Availability data inserted successfully.")
    
    if not listingAmenitiesData.empty:
        listingAmenitiesData.to_sql('listing_amenities', con=engine, if_exists='append', index=False)
        logging.info("Listing amenities data inserted successfully.")
        
    else:
        logging.info("No data to insert into the database.")



def table_exists(engine, tableName: str) -> bool:
    """Checks if a table exists in the database.

    Parameters:
        engine: SQLAlchemy engine object.
        tableName: Name of the table to check.

    Returns:
        True if the table exists, False otherwise.
    """
    inspector = inspect(engine)
    return inspector.has_table(tableName)
    


if __name__ == "__main__":
    main() 
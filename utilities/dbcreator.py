import pandas as pd
import numpy as np
from sqlalchemy import create_engine, inspect



def read_data(filePath: str) -> pd.DataFrame:
    """
    Reads data from a CSV file and returns it as a pandas DataFrame.
    
    :param filePath: Path to the CSV file.
    :return: DataFrame containing the data.
    """
    try:
        data = pd.read_csv(filePath)
        return data
    except Exception as e:
        print(f"Error reading the file: {e}")
        return pd.DataFrame() 
    
    

def create_listings_table(engine) -> None:
    """
    Creates the listings table in the database.
    
    :param engine: SQLAlchemy engine object.
    """
    table_name = "listings"
    if table_exists(engine, table_name):
        print(f"Table '{table_name}' exists.")
        
    else:
        print(f"Table '{table_name}' does not exist.")
    
        listingsSchemaQuery = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            listing_id INTEGER PRIMARY KEY,
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
            FOREIGN KEY (host_id) REFERENCES hosts(host_id),
            FOREIGN KEY (location_id) REFERENCES locations(location_id)
        );
        """
        
        with engine.connect() as connection:
            connection.execute(listingsSchemaQuery)
            print("Listings table created successfully.")

    

def create_reviews_table(engine) -> None:
    """
    Creates the reviews table in the database.
    
    :param engine: SQLAlchemy engine object.
    """
    table_name = "reviews"
    if table_exists(engine, table_name):
        print(f"Table '{table_name}' exists.")
        
    else:
        print(f"Table '{table_name}' does not exist.")
    
        reviewsSchemaQuery = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            review_id INTEGER PRIMARY KEY,
            listing_id INTEGER NOT NULL,
            date DATE NOT NULL,
            reviewer_id TEXT NOT NULL,
            reviewer_name TEXT NOT NULL,
            comments TEXT,
            FOREIGN KEY (listing_id) REFERENCES listings(listing_id)
        );
        """
        
        with engine.connect() as connection:
            connection.execute(reviewsSchemaQuery)
            print("Reviews table created successfully.")
    


def create_hosts_table(engine) -> None:
    """
    Creates the hosts table in the database.
    
    :param engine: SQLAlchemy engine object.
    """
    table_name = "hosts"
    if table_exists(engine, table_name):
        print(f"Table '{table_name}' exists.")
        
    else:
        print(f"Table '{table_name}' does not exist.")
        
        hostsSchemaQuery = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            host_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            host_url TEXT NOT NULL,
            host_since TEXT,
            host_location_id TEXT,
            host_about TEXT,
            host_response_time TEXT,
            host_response_rate FLOAT CHECK(host_response_rate >= 0 AND host_response_rate <= 100),
            host_acceptance_rate FLOAT CHECK(host_acceptance_rate >= 0 AND host_acceptance_rate <= 100),
            host_is_superhost BOOLEAN,
            host_thumbnail_url TEXT,
            host_picture_url TEXT,
            host_listings_count INTEGER DEFAULT 0,
            host_verifications TEXT,
            host_has_profile_pic BOOLEAN,
            host_identity_verified BOOLEAN,
            FOREIGN KEY (host_location_id) REFERENCES locations(location_id)
        );
        """
        
        with engine.connect() as connection:
            connection.execute(hostsSchemaQuery)
            print("Hosts table created successfully.")
        
    
    
def create_locations_table(engine) -> None:
    """
    Creates the locations table in the database.
    
    :param engine: SQLAlchemy engine object.
    """
    
    table_name = "locations"
    if table_exists(engine, table_name):
        print(f"Table '{table_name}' exists.")
        
    else:
        print(f"Table '{table_name}' does not exist.")
        locationsSchemaQuery = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            location_id INTEGER PRIMARY KEY,
            location TEXT NOT NULL,
            neighborhood TEXT,
            FOREIGN KEY (listing_id) REFERENCES listings(id)
        );
        """
        
        with engine.connect() as connection:
            connection.execute(locationsSchemaQuery)
            print("Locations table created successfully.")
    
    

def create_availability_table(engine) -> None:
    """
    Creates the availability table in the database.
    
    :param engine: SQLAlchemy engine object.
    """
    
    table_name = "availability"
    if table_exists(engine, table_name):
        print(f"Table '{table_name}' exists.")
        
    else:
        print(f"Table '{table_name}' does not exist.")
    
        availabilitySchemaQuery = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            availability_id INTEGER PRIMARY KEY,
            listing_id INTEGER NOT NULL,
            date DATE NOT NULL,
            available BOOLEAN NOT NULL,
            minimum_nights INTEGER DEFAULT 1,
            maximum_nights INTEGER DEFAULT 365,
            FOREIGN KEY (listing_id) REFERENCES listings(listing_id)
        );
        """
        
        with engine.connect() as connection:
            connection.execute(availabilitySchemaQuery)
            print("Availability table created successfully.")
        
        

def create_all_tables(engine) -> None:
    """
    Creates all tables in the database.
    
    :param engine: SQLAlchemy engine object.
    """
    print("Creating all tables in the database...")
    
    # Create all tables
    create_listings_table(engine)
    create_reviews_table(engine)
    create_hosts_table(engine)
    create_locations_table(engine)
    create_availability_table(engine)
    print("All tables created successfully.")
    
    
    
def read_and_insert_date(engine) -> None:
    """
    Reads data from CSV files and inserts it into the database.
    
    :param engine: SQLAlchemy engine object.
    """
    
    # Read data from CSV files
    print("Reading data from CSV files...")
    listingsData = read_data('cleaned_listings.csv')
    reviewsData = read_data('cleaned_reviews.csv')
    hostsData = read_data('cleaned_hosts.csv')
    locationsData = read_data('cleaned_locations.csv')
    availabilityData = read_data('cleaned_availability.csv')
    print("Data read successfully.")
    
    
    # Insert data into the database tables
    print("Inserting data into the database...")
    if not listingsData.empty:
        listingsData.to_sql('listings', con=engine, if_exists='append', index=False)
        print("Listings data inserted successfully.")
    if not reviewsData.empty:
        reviewsData.to_sql('reviews', con=engine, if_exists='append', index=False)
        print("Reviews data inserted successfully.")
    if not hostsData.empty:
        hostsData.to_sql('hosts', con=engine, if_exists='append', index=False)
        print("Hosts data inserted successfully.")
    if not locationsData.empty:
        locationsData.to_sql('locations', con=engine, if_exists='append', index=False)
        print("Locations data inserted successfully.")
    if not availabilityData.empty:
        availabilityData.to_sql('availability', con=engine, if_exists='append', index=False)
        print("Availability data inserted successfully.")
    else:
        print("No data to insert into the database.")



def table_exists(engine, table_name):
    """Checks if a table exists in the database.

    Args:
        engine: SQLAlchemy engine object.
        table_name: Name of the table to check.

    Returns:
        True if the table exists, False otherwise.
    """
    inspector = inspect(engine)
    return inspector.has_table(table_name)



def main() -> None:
    
    # Creates a connection to a MySQL database.
    mySQLEngine = create_engine('mysql+pymysql://user:password@localhost/db_name', echo=True)
    
    # Create the database tables.
    create_all_tables(mySQLEngine)
    
    # Read data from CSV files and insert it into the database.
    read_and_insert_date(mySQLEngine)
    


if __name__ == "__main__":
    main() 
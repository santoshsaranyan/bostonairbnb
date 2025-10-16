import time
import logging
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

# Load the environment variables from the .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',handlers=[logging.FileHandler("logs/dbrefreshview.log"),logging.StreamHandler()])

# Get database credentials from environment variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

# Check if the environment variables are set
if not USER or not PASSWORD or not DBNAME or not HOST or not PORT:
    raise ValueError("Database credentials are not set in the .env file.")

def refresh_gold_materialized_views() -> None:
    start = time.time()
    
    # Create a connection to PostgreSQL
    connectionStr = f'postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require'
    engine = create_engine(connectionStr)
    logging.info("Connected to the PostgreSQL database successfully.")
    
    # List of materialized views to refresh
    materialized_views = [
        "gold.mv_listing_overview",
        "gold.mv_host_summary",
        "gold.mv_review_activity",
        "gold.mv_neighborhood_summary",
        "gold.mv_amenity_summary",
        "gold.mv_availability_summary",
        "gold.mv_availability_trend"
    ]
    
    # Refresh views
    with engine.begin() as conn:
        for mv in materialized_views:
            try:
                conn.execute(text(f"REFRESH MATERIALIZED VIEW {mv};"))
                logging.info(f"Refreshed materialized view: {mv}")
                
            except Exception as e:
                logging.info(f"Failed to refresh {mv}: {e}")
    
    end = time.time()
    logging.info(f"All materialized views refreshed in {end - start:.2f} seconds.")


if __name__ == "__main__":
    refresh_gold_materialized_views()

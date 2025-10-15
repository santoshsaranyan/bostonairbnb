import time
import logging
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

# Load the environment variables from the .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',handlers=[logging.FileHandler("logs/dbsilverloader.log"),logging.StreamHandler()])

# Get database credentials from environment variables
user = os.getenv('user')
password = os.getenv('password')
db_name = os.getenv('db_name')

def refresh_gold_materialized_views() -> None:
    start = time.time()
    
    # Create a connection to PostgreSQL
    connectionStr = f'postgresql+psycopg2://{user}:{password}@postgres:5432/{db_name}'
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
    
    # Refresh views one by one
    with engine.begin() as conn:  # ensures transaction safety
        for mv in materialized_views:
            conn.execute(text(f"REFRESH MATERIALIZED VIEW {mv};"))
            logging.info(f"Refreshed materialized view: {mv}")
    
    end = time.time()
    logging.info(f"All materialized views refreshed in {end - start:.2f} seconds.")


if __name__ == "__main__":
    refresh_gold_materialized_views()

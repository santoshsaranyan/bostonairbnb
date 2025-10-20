from utilities.datascraper import scrape_data
from utilities.datapreprocessor import preprocess_data
from utilities.dbbronzeloader import load_bronze_data
from utilities.dbsilverloader import load_silver_data
from utilities.dbgoldrefresh import refresh_gold_materialized_views
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',handlers=[logging.FileHandler("logs/etlpipeline.log"),logging.StreamHandler()])

""" 
This script runs the complete ETL pipeline by executing each step in sequence:
1. Data Webscraping
2. Data Preprocessing & Transformation
3. Loading Bronze Data to PostgreSQL
4. Loading Silver Data to PostgreSQL
5. Refreshing Gold Materialized Views in PostgreSQL
"""

def run_with_retry(taskfunction, retries=1, delay=5):
    """
    Runs a function with retry logic.
    Retries the function with delay in seconds between attempts.
    
    Parameters:
        taskfunction: The function to run.
        retries: Number of retries on failure.
        delay: Delay in seconds between retries.
        
    Returns:
        None
    """
    for attempt in range(1, retries + 2):  # +1 for the initial attempt
        try:
            taskfunction()
            return 
        except Exception as e:
            if attempt <= retries:
                logging.info(f"Failed: {taskfunction.__name__} failed on attempt {attempt}")
                logging.info(f"Retry: Retrying in {delay} seconds")
                logging.info(f"Error: {e}")
                time.sleep(delay)
            else:
                logging.info(f"Failed: {taskfunction.__name__} failed after {retries + 1} attempts")
                logging.info(f"Error: {e}")
                raise

def run_etl_pipeline() -> None:
    """
    Runs the complete ETL pipeline by executing each step in sequence.
    Each step is retried once with a few seconds of delay on failure.
    
    Parameters:
        None
    
    Returns:
        None
    """
    logging.info("Starting: ETL Pipeline")

    tasks = [
        ("datascraper", scrape_data),
        ("datapreprocessor", preprocess_data),
        ("dbbronzeloader", load_bronze_data),
        ("dbsilverloader", load_silver_data),
        ("dbgoldrefresh", refresh_gold_materialized_views),
    ]

    for taskname, taskfunction in tasks:
        logging.info(f"Running Task: {taskname}")
        run_with_retry(taskfunction, retries=1, delay=10)

    logging.info("Completed: ETL Pipeline completed successfully.")
    
if __name__ == "__main__":
    run_etl_pipeline()
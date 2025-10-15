from etl_pipeline.utilities.datascraper import scrape_data
from etl_pipeline.utilities.datapreprocessor import preprocess_data
from etl_pipeline.utilities.dbsilverloader import load_silver_data
from etl_pipeline.utilities.dbbronzeloader import load_bronze_data
from etl_pipeline.utilities.dbgoldrefresh import refresh_gold_materialized_views
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',handlers=[logging.FileHandler("logs/pipelinerunner.log"),logging.StreamHandler()])

""" This script orchestrates the entire ETL pipeline by calling individual modules in sequence."""

def run_pipeline():
    
    start = time.time()
    logging.info("Starting ETL Pipeline...")
    
    logging.info("Step 1: Scraping Data")
    scrape_data()
    
    logging.info("Step 2: Preprocessing Data")
    preprocess_data()
    
    logging.info("Step 3: Loading Bronze Data")
    load_bronze_data()
    
    logging.info("Step 4: Loading Silver Data")
    load_silver_data()
    
    logging.info("Step 5: Refreshing Gold Materialized Views")
    refresh_gold_materialized_views()
    
    end = time.time()
    logging.info(f"ETL Pipeline completed in {end - start:.2f} seconds.")
    
if __name__ == "__main__":
    run_pipeline()
    
    
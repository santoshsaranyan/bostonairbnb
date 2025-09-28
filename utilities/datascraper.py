import httpx
from bs4 import BeautifulSoup
from io import BytesIO
import urllib.request
import os
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    
    # Define the URL to scrape
    url = "https://insideairbnb.com/get-the-data/"
    fetch_html(url)
    
    
def fetch_html(url: str, max_retries: int = 3, backoff_factor: float = 1.0) -> None:
    """
    Fetches the HTML content of a given URL.
    
    Args:
        url (str): The URL to fetch.
        
    Returns:
        None
    """
    for attempt in range(1, max_retries + 1):
        try:
            # Get the HTML content from the URL
            response = httpx.get(url)
            # Note: For production code, I generally add a user-agent header and proxy settings to avoid being blocked.
            
            if response.status_code == 200 and response.content:
                # Parse the HTML content
                html_source = response.text
                logging.info("Request was successful.")
                soup = BeautifulSoup(html_source, 'lxml')
                soup = BeautifulSoup(soup.prettify(), 'lxml')
                
                try:
                    boston = soup.find('table',class_='data table table-hover table-striped boston')
                    table_rows = boston.find('tbody').find_all('tr')
                    
                    for row in table_rows:
                        try:
                            link_item = row.find('a', href=True)
                            link = link_item['href']
                            if '/data/' in link:
                                download_file(link)
                                
                        except Exception as e:
                            logging.info(f"Error extracting link: {e}")
                        
                except Exception as e:
                    logging.info(f"Error parsing HTML: {e}")
                        
        except Exception as e:
            logging.info(f"Error fetching the URL: {e}")
        
        # Backoff before next retry
        if attempt < max_retries:
            # Delay with exponential backoff
            delay = backoff_factor * (2 ** (attempt - 1))
            logging.info(f"Retrying in {delay:.1f} seconds...")
            time.sleep(delay)
        else:
            logging.error("Max retries exceeded. Failed to fetch URL.")
        
        
def download_file(link: str) -> None:
    """
    Downloads a file from the given URL.
    
    Args:
        link (str): The URL of the file to download.
    """
    
    # Create destination folder if it doesn't exist
    save_folder = '../data/downloads'
    os.makedirs(save_folder, exist_ok=True)

    filename = os.path.join(save_folder, link.split('/')[-1])
    
    # Download the file
    try:
        urllib.request.urlretrieve(link, filename)
        logging.info(f"File downloaded and saved to: {filename}")
        
    except Exception as e:
        logging.info(f"Error downloading file: {e}")

    
if __name__ == "__main__":
    main()
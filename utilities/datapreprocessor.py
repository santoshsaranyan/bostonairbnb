import pandas as pd
import numpy as np
import re
import time
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import csv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

"""
This script reads data from gzipped CSV files, and preprocesses them to clean and transform the data into suitable formats to insert into database tables.
The cleaned data is then saved as CSV files.
"""

def main():
    
    start = time.time()
    
    logging.info("Starting data preprocessing...")
    listingsDF, hostsDF, locationsDF, amenityDF, listingAmenitiesDF, listingsCIDMap = preprocess_listings_data()
    reviewsDF = preprocess_reviews_data(listingsCIDMap)
    calendar_df = preprocess_calendar_data(listingsCIDMap)
    
    logging.info("Data processing completed. Saving cleaned data to CSV files...")
    
    save_data(listingsDF, 'data/cleaned_listings.csv')
    save_data(hostsDF, 'data/cleaned_hosts.csv')
    save_data(locationsDF, 'data/cleaned_locations.csv')
    save_data(amenityDF, 'data/cleaned_amenities.csv')
    save_data(listingAmenitiesDF, 'data/cleaned_listing_amenities.csv')
    save_data(reviewsDF, 'data/cleaned_reviews.csv')
    save_data(calendar_df, 'data/cleaned_availability.csv')
    
    logging.info("Cleaned data saved.")
    
    end = time.time()
    
    logging.info(f"Script executed in {end - start:.2f} seconds.")
    


def read_data(filePath: str) -> pd.DataFrame:
    """
    Reads data from a compressed (gzip) CSV file and returns it as a pandas DataFrame.
    
    Parameters:
        filePath: Path to the CSV file.
        
    Returns:
        data: pandas DataFrame containing the data.
    """
    
    try:
        data = pd.read_csv(filePath, compression='gzip')
        return data
    
    except Exception as e:
        logging.info(f"Error reading the file: {e}")
        return pd.DataFrame() 
    
    
    
def save_data(data: pd.DataFrame, filePath: str):
    """
    Saves a pandas DataFrame to a CSV file.
    
    Parameters:
        data: pandas DataFrame to be saved.
        filePath: Path where the CSV file will be saved.
        
    Returns:
        None
    """
    
    try:
        data.to_csv(filePath, index=False)
        logging.info(f"Data saved to {filePath}")
        
    except Exception as e:
        logging.info(f"Error saving the file: {e}")
        
    

def clean_and_split_amenities(text):
    """ 
    Cleans and splits the amenities text into a list of individual amenities.
    Parameters:
        text: A string containing the amenities, in a list-like format.
    Returns:
        A list of individual amenities. If the input is empty or invalid, returns a list with a single element 'no amenities listed'.
    """
    
    if not isinstance(text, str) or not text.strip():
        return ['no amenities listed']
    
    text = text.lower()
    
    text = re.sub(r'[\[\]"]', '', text)  # Remove brackets and quotes  
                
    text = re.sub(r'[^\w\s,]', '', text) # Remove punctuation like &?! etc.           
            
    text = re.sub(r'\band\b', ',', text) # Replace 'and' with comma 
    
    text = re.sub(r'\s*,\s*', ', ', text) # Normalize comma spacing      
            
    text = re.sub(r'\s+', ' ', text).strip() # Normalize whitespace               

    if text == '':
        return ['no amenities listed']
    
    return [a.strip() for a in text.split(',') if a.strip()]


    
def match_amenity_to_category_tfidf(amenityToVector, amenityStr, categoryVectors, categoryLabels):
    """ 
    Matches an amenity string to its corresponding category using TF-IDF vectorization and cosine similarity.
    
    Parameters:
        amenityToVector: A dictionary mapping amenities to their TF-IDF vectors.
        amenityStr: A string representing the amenity to be matched.
        categoryVectors: A matrix of TF-IDF vectors for each category.
        categoryLabels: A list of category labels corresponding to the vectors in categoryVectors.
    
    Returns:
        A list of category labels that match the amenity string based on cosine similarity. If no matches are found, returns a list with a single element 'Miscellaneous'.
    """
    
    v = amenityToVector.get(amenityStr)
    
    if v is None or v.nnz == 0:
        return ['Miscellaneous']
    sims = cosine_similarity(v, categoryVectors)[0]
    matches = [categoryLabels[i] for i, score in enumerate(sims) if score > 0.2] 
    return matches if matches else ['Miscellaneous']


def preprocess_listings_data():
    """
    Reads the listings data from a compressed CSV file, processes it to clean and transform the data into a suitable format to insert into the database's listings, hosts, locations, amenities, and listing_amenities tables.
    
    Parameters:
        None
        
    Returns:
        listingsDF: DataFrame containing cleaned listings data.
        hostsDF: DataFrame containing cleaned hosts data.
        locationsDF: DataFrame containing cleaned locations data.
        amenityDF: DataFrame containing cleaned amenities data.
        listingAmenitiesDF: DataFrame containing cleaned listing-amenities mapping data.
        listingsCIDMap: Dictionary mapping listing_cid to listing_id.
    """

    # Load listings data
    listingsData = load_listings_data("data/listings.csv.gz")

    # Clean listings table
    listingsDF = process_listings(listingsData)

    # Process amenities
    amenityDF, listingAmenitiesDF = process_amenities(listingsDF)

    # Process hosts and locations
    hostsDF, locationsDF, listingsDF, listingsCIDMap = process_hosts_and_locations(listingsData, listingsDF)

    return listingsDF, hostsDF, locationsDF, amenityDF, listingAmenitiesDF, listingsCIDMap



def load_listings_data():
    """
    Reads the listings data from a compressed CSV file and returns it as a pandas DataFrame.
    
    Parameters:
        None
        
    Returns:
        listingsData: DataFrame containing the listings data.
    """
    
    logging.info("Processing listings data...")
    
    listingsData = read_data('data/listings.csv.gz')
    
    listingsData = listingsData.reset_index().rename(columns={'index': 'listing_id'})
    listingsData['listing_id'] = listingsData['listing_id'] + 1000 
    listingsData['listing_id'] = listingsData['listing_id'].astype(int)
    listingsData['id'] = listingsData['id'].astype(str)
    
    return listingsData


def process_listings(listingsData):
    """
    Processes the listings data to clean and transform it into a suitable format to insert into the database's listings table.
    
    Parameters:
        listingsData: DataFrame containing the raw listings data.
    Returns:
        listingsDF: DataFrame containing cleaned listings data.
    """
    # Selecting and renaming columns
    logging.info("Selecting and renaming columns...")
    listingsColumns = ["listing_id", "id","name", "description", "host_id", "listing_url", "neighbourhood_cleansed","neighborhood_overview",
        "picture_url", "latitude", "longitude", "property_type", "room_type", "accommodates",
        "bathrooms","bathrooms_text", "bedrooms", "beds", "amenities", "license", 'review_scores_rating', 'review_scores_accuracy',
        'review_scores_cleanliness', 'review_scores_checkin',
        'review_scores_communication', 'review_scores_location',
        'review_scores_value','number_of_reviews']


    listingsDF = listingsData[listingsColumns].copy()
    listingsDF.rename(columns={'id':'listing_cid','review_scores_rating': 'overall_rating','review_scores_accuracy': 'accuracy_rating',
        'review_scores_cleanliness': 'cleanliness_rating', 'review_scores_checkin': 'checkin_rating',
        'review_scores_communication': 'communication_rating', 'review_scores_location': 'location_rating',
        'review_scores_value': 'value_rating'}, inplace=True)

    # Filling in missing values
    listingsDF['description'] = listingsDF['description'].fillna('No description given')
    listingsDF['neighborhood_overview'] = listingsDF['neighborhood_overview'].fillna('No neighborhood overview given')
    listingsDF['license'] = listingsDF['license'].fillna('No license information')

    listingsDF['bathrooms'] = np.where(listingsDF['bathrooms'].isnull(), listingsDF['bathrooms_text'].str.extract(r'(\d+\.?\d*)').astype(float), listingsDF['bathrooms'])

    listingsDF['bathrooms'] = listingsDF['bathrooms'].fillna(0) 
    listingsDF['bedrooms'] = listingsDF['bedrooms'].fillna(1)  
    listingsDF['beds'] = listingsDF['beds'].fillna(1)

    listingsDF['bathroom_type'] = np.where(listingsDF['bathrooms_text'].str.contains('shared', case=False, na=False), 'shared', 'private')
    listingsDF.drop(columns=['bathrooms_text'], inplace=True)

    logging.info("Cleaning, splitting and categorizing amenities...")
    listingsDF['amenities'] = listingsDF['amenities'].apply(clean_and_split_amenities)
    
    return listingsDF


def process_amenities(listingsDF):
    """ 
    Processes the amenities data from the listings DataFrame to create amenities and listing_amenities DataFrames.
    
    Parameters:
        listingsDF: DataFrame containing the listings data with amenities.
        
    Returns:
        amenityDF: DataFrame containing cleaned amenities data.
        listingAmenitiesDF: DataFrame containing cleaned listing-amenities mapping data.
    """
    
    logging.info("Categorizing amenities...")
    # Creating a mapping of amenities to categories using TF-IDF vectorization and cosine similarity
    amenityCategoryMap = {
        'TV': ['hdtv', 'tv', 'screen', 'television', 'smart tv', 'flat screen', 'oled', 'led'],
        'Streaming': ['netflix', 'amazon prime', 'fire tv', 'apple tv', 'roku', 'hulu', 'disney', 'hbo', 'streaming service', 'streaming'],
        'Kitchen': ['oven', 'stove', 'refrigerator', 'kitchen', 'cooktop'],
        'Air Conditioning': ['air conditioning', 'ac', 'central air', 'split type ductless'],
        'Heating': ['heating', 'heater'],
        'View': ['beach view', 'lake view', 'mountain view', 'city skyline view', 'garden view', 'view'],
        'Parking': ['parking', 'garage', 'driveway', 'carport'],
        'Internet': ['wifi', 'ethernet', 'internet'],
        'Toiletries': ['soap', 'shampoo', 'conditioner', 'body wash', 'toiletries'],
        'Kitchen Appliances': ['dishwasher', 'kettle', 'coffee maker', 'microwave', 'toaster'],
        'Other Appliances': ['iron','hair dryer'],
        'Essentials': ['towels', 'linens', 'toilet paper', 'paper towels', 'kitchen essentials'],
        'Safety Equipemnt': ['smoke alarm', 'carbon monoxide alarm', 'fire extinguisher', 'first aid kit'],
        'Bedding': ['sheets', 'pillows', 'blankets', 'comforter', 'bedding'],
        'Dining': ['dining table', 'dining area', 'bar stools', 'kitchen island', 'cutlery', 'dishes', 'glassware', 'silverware', 'pots and pans'],
        'Laundry': ['washer', 'dryer', 'laundromat', 'laundry'],
        'Gym': ['gym', 'exercise equipment', 'weights', 'treadmill'],
        'Entertainment': ['board games', 'arcade', 'pool table', 'ping pong', 'dvd player', 'game console'],
        'Pool': ['pool', 'lap pool', 'indoor pool', 'outdoor pool','hot tub'],
        'Fireplace': ['fireplace'],
        'Baby Friendly': ['crib', 'high chair', 'baby monitor', 'booster seat', 'changing table', 'baby friendly'],
        'Pet Friendly': ['pets allowed', 'pet friendly', 'cat(s)', 'dog(s)', 'pet(s)'],
        'Smoking': ['smoking allowed', 'smoking'],
        'Security': ['security system', 'doorman', 'safe', 'lockbox', 'keypad'],
        'Outdoor Space': ['balcony', 'terrace', 'patio', 'garden', 'deck', 'outdoor furniture', 'outdoor space'],
        'Accessibility': ['wheelchair accessible', 'elevator', 'step-free access', 'grab bars'],
        'Miscellaneous': ['miscellaneous', 'other', 'various amenities'],
        'No Amenities': ['no amenities listed']
    }


    categoryTexts = [' '.join(keywords) for keywords in amenityCategoryMap.values()]
    categoryLabels = list(amenityCategoryMap.keys())

    logging.info("Extracting unique amenities...")
    uniqueAmenities = set()
    for amenities_list in listingsDF['amenities']:
        uniqueAmenities.update(amenities_list)
    uniqueAmenities = list(uniqueAmenities)


    logging.info("Fitting TF-IDF vectorizer...")
    vectorizer = TfidfVectorizer().fit(categoryTexts + uniqueAmenities)

    # Encode categories and amenities
    categoryVectors = vectorizer.transform(categoryTexts)
    amenityVectors = vectorizer.transform(uniqueAmenities)

    # Map amenity to vector
    amenityToVector = dict(zip(uniqueAmenities, amenityVectors))


    logging.info("Matching amenities to categories...")
    listingsDF['amenity_categories'] = listingsDF['amenities'].apply(lambda amenities: list(set(cat for amenity in amenities for cat in match_amenity_to_category_tfidf(amenityToVector, amenity, categoryVectors, categoryLabels))))


    uniqueAmenityCategories = list(amenityCategoryMap.keys())

    amenityDF = pd.DataFrame({
        'amenity_id': range(1, len(uniqueAmenityCategories) + 1),
        'amenity_name': uniqueAmenityCategories
    })

    amenityToId = dict(zip(amenityDF['amenity_name'], amenityDF['amenity_id']))

    logging.info("Creating listing amenities mapping...")
    listingAmenities = [(listing_id, amenityToId[amenity]) for listing_id, amenities in zip(listingsDF['listing_id'], listingsDF['amenity_categories']) for amenity in amenities]

    listingAmenitiesDF = pd.DataFrame(listingAmenities, columns=['listing_id', 'amenity_id'])
    
    return amenityDF, listingAmenitiesDF


def process_locations(listingsData, listingsDF):
    """
    Processes the locations data from the listings DataFrame to create locations DataFrame and a mapping of neighborhood-location to location_id.
    
    Parameters:
        listingsData: DataFrame containing the raw listings data.
        listingsDF: DataFrame containing the cleaned listings data.
    
    Returns:
        locationsDF: DataFrame containing cleaned locations data.
        locationsNeighborhoodMap: Dictionary mapping neighborhood-location to location_id.
    """
    # Fill missing neighborhood/location
    listingsDF['neighbourhood_cleansed'] = listingsDF['neighbourhood_cleansed'].fillna('Not Specified')
    listingsDF['location'] = 'Boston, MA'

    hostsSubset = listingsData[['host_neighbourhood', 'host_location']].copy()
    hostsSubset['host_neighbourhood'] = np.where(
        (hostsSubset['host_location'].isna()) & (hostsSubset['host_neighbourhood'].isna()),
        'Unknown',
        hostsSubset['host_neighbourhood']
    )
    hostsSubset['host_neighbourhood'] = hostsSubset['host_neighbourhood'].fillna('Not Specified')
    hostsSubset['host_location'] = np.where(
        (hostsSubset['host_location'].isna()) & (hostsSubset['host_neighbourhood'] == 'Unknown'),
        'Unknown',
        hostsSubset['host_location']
    )
    hostsSubset['host_location'] = hostsSubset['host_location'].fillna('Boston, MA')

    # Build location table
    locationsDF = hostsSubset.drop_duplicates().reset_index(drop=True).rename(
        columns={'host_neighbourhood': 'neighbourhood', 'host_location': 'location'}
    )
    listingsLocationDF = listingsDF[['neighbourhood_cleansed', 'location']].drop_duplicates().reset_index(drop=True)
    listingsLocationDF = listingsLocationDF.rename(columns={'neighbourhood_cleansed': 'neighbourhood', 'location': 'location'})

    locationsDF = pd.concat([locationsDF, listingsLocationDF], ignore_index=True).drop_duplicates().reset_index(drop=True)
    locationsDF = locationsDF.reset_index().rename(columns={'index': 'location_id'})
    locationsDF['location_id'] = locationsDF['location_id'] + 1
    locationsDF.rename(columns={'neighbourhood': 'neighborhood'}, inplace=True)

    # Build mapping
    locationsNeighborhoodMap = dict(zip(
        locationsDF['neighborhood'] + ', ' + locationsDF['location'],
        locationsDF['location_id']
    ))

    return locationsDF, locationsNeighborhoodMap


def process_hosts(listingsData, locationsNeighborhoodMap):
    """
    Processes the hosts data from the listings DataFrame to create hosts DataFrame.
    
    Parameters:
        listingsData: DataFrame containing the raw listings data.
        locationsNeighborhoodMap: Dictionary mapping neighborhood-location to location_id.
    
    Returns:
        hostsDF: DataFrame containing cleaned hosts data.
    """
    
    hostsColumns = [
        'host_id', 'host_name', 'host_url','host_since', 'host_location','host_about',
        'host_response_time','host_response_rate', 'host_acceptance_rate', 'host_is_superhost',
        'host_thumbnail_url','host_picture_url','host_neighbourhood', 'host_total_listings_count',
        'host_has_profile_pic', 'host_identity_verified','host_verifications'
    ]
    hostsDF = listingsData[hostsColumns].copy()
    
    hostsDF['host_neighbourhood'] = np.where((hostsDF['host_location'].isna())&(hostsDF['host_neighbourhood'].isna()), 'Unknown', hostsDF['host_neighbourhood'])
    hostsDF['host_neighbourhood'] = hostsDF['host_neighbourhood'].fillna('Not Specified')

    hostsDF['host_location'] = np.where((hostsDF['host_location'].isna()) & (hostsDF['host_neighbourhood'] == 'Unknown'), 'Unknown', hostsDF['host_location'])
    hostsDF['host_location'] = hostsDF['host_location'].fillna('Boston, MA')

    # Map to location_id
    hostsDF['location_id'] = hostsDF.apply(
        lambda row: locationsNeighborhoodMap[row['host_neighbourhood'] + ', ' + row['host_location']],
        axis=1
    )
    hostsDF.drop(columns=['host_neighbourhood', 'host_location'], inplace=True)

    # Clean host fields
    hostsDF['host_about'] = hostsDF['host_about'].astype(str).replace({r'\r\n': ' ', r'\r': ' ', r'\n': ' '}, regex=True).str.strip()
    hostsDF['host_about'] = hostsDF['host_about'].apply(lambda x: x.encode('utf-8', 'ignore').decode('utf-8') if isinstance(x, str) else x)

    hostsDF['host_name'] = hostsDF['host_name'].fillna('Unknown Host')
    hostsDF['host_is_superhost'] = hostsDF['host_is_superhost'].apply(lambda x: x == 't')
    hostsDF['host_has_profile_pic'] = hostsDF['host_has_profile_pic'].apply(lambda x: x == 't')
    hostsDF['host_identity_verified'] = hostsDF['host_identity_verified'].apply(lambda x: x == 't')
    hostsDF['host_response_rate'] = hostsDF['host_response_rate'].str.replace('%', '').astype(float)
    hostsDF['host_acceptance_rate'] = hostsDF['host_acceptance_rate'].str.replace('%', '').astype(float)

    # Re-index hosts
    hostsDF['host_id'] = pd.to_numeric(hostsDF['host_id'], errors='coerce')
    hostsDF.dropna(subset=['host_id'], inplace=True)
    hostsDF['host_id'] = hostsDF['host_id'].astype(int)
    hostsDF['host_cid'] = hostsDF['host_id'].astype(str)
    hostsDF.drop(columns=['host_id'], inplace=True)

    hostsDF.drop_duplicates(inplace=True)
    hostsDF = hostsDF.reset_index(drop=True).reset_index().rename(columns={'index': 'host_id'})
    hostsDF['host_id'] = hostsDF['host_id'] + 1000
    hostsDF['host_id'] = hostsDF['host_id'].astype(int)

    hostsDF = hostsDF[[
        'host_id', 'host_cid', 'host_name', 'host_url', 'host_since', 'location_id', 'host_about',
        'host_response_time', 'host_response_rate', 'host_acceptance_rate',
        'host_is_superhost', 'host_thumbnail_url', 'host_picture_url',
        'host_total_listings_count', 'host_verifications', 'host_has_profile_pic',
        'host_identity_verified'
    ]]
    
    hostsDF.drop_duplicates(inplace=True)

    return hostsDF


def final_process_listings(listingsDF, hostsDF, locationsNeighborhoodMap):
    """ 
    Final processing of listings DataFrame to clean and transform it into a suitable format to insert into the database's listings table.
    
    Parameters:
        listingsDF: DataFrame containing the cleaned listings data.
        hostsDF: DataFrame containing the cleaned hosts data.
        locationsNeighborhoodMap: Dictionary mapping neighborhood-location to location_id.
    
    Returns:
        listingsDF: DataFrame containing cleaned listings data.
    """
    logging.info("Final processing of listings data...")
    listingsDF['neighbourhood_cleansed'] = listingsDF['neighbourhood_cleansed'].fillna('Not Specified')
    listingsDF['location'] = 'Boston, MA'
    
    # Map listings to locations
    listingsDF['location_id'] = listingsDF.apply(
        lambda row: locationsNeighborhoodMap[row['neighbourhood_cleansed'] + ', ' + row['location']],
        axis=1
    )
    listingsDF.drop(columns=['neighbourhood_cleansed', 'location'], inplace=True)

    # Map host IDs
    listingsDF['host_cid'] = listingsDF['host_id']
    hostcidMap = dict(zip(hostsDF['host_cid'], hostsDF['host_id']))
    listingsDF['host_cid'] = listingsDF['host_cid'].astype(str)
    listingsDF['host_id'] = listingsDF['host_cid'].map(hostcidMap).astype(int)

    # Clean listing fields
    listingsDF['description'] = listingsDF['description'].astype(str).replace({r'\r\n': ' ', r'\r': ' ', r'\n': ' '}, regex=True).str.strip()
    listingsDF['description'] = listingsDF['description'].apply(lambda x: x.encode('utf-8', 'ignore').decode('utf-8') if isinstance(x, str) else x)

    listingsDF['amenities'] = listingsDF['amenities'].apply(lambda x: ','.join(map(str, x)))

    listingsDF['listing_id'] = pd.to_numeric(listingsDF['listing_id'], errors='coerce')
    listingsDF.dropna(subset=['listing_id'], inplace=True)
    listingsDF['listing_id'] = listingsDF['listing_id'].astype(int)

    listingsDF.drop_duplicates(inplace=True)
    listingsDF = listingsDF.drop_duplicates(subset=['listing_id'], keep='first')

    # Select final schema
    listingsDF = listingsDF[[
        'listing_id', 'listing_cid', 'name', 'description', 'host_id', 'listing_url',
        'location_id', 'neighborhood_overview', 'picture_url',
        'latitude', 'longitude', 'property_type', 'room_type', 'accommodates',
        'bathrooms', 'bedrooms', 'bathroom_type', 'beds', 'amenities', 'license',
        'overall_rating', 'accuracy_rating', 'cleanliness_rating',
        'checkin_rating', 'communication_rating', 'location_rating',
        'value_rating', 'number_of_reviews'
    ]]

    return listingsDF



def process_hosts_and_locations(listingsData, listingsDF):
    """
    Processes the hosts and locations data from the listings DataFrame to create hosts and locations DataFrames. Also finalizes the listings DataFrame.
    
    Parameters:
        listingsData: DataFrame containing the raw listings data.
        listingsDF: DataFrame containing the cleaned listings data.
    
    Returns:
        hostsDF: DataFrame containing cleaned hosts data.
        locationsDF: DataFrame containing cleaned locations data.
        listingsDF: DataFrame containing cleaned listings data.
        listingsCIDMap: Dictionary mapping listing_cid to listing_id.
    """
    logging.info("Processing hosts and locations data from listings data...")

    # Process locations
    locationsDF, locationsNeighborhoodMap = process_locations(listingsData, listingsDF)

    # Process hosts
    hostsDF = process_hosts(listingsData, locationsNeighborhoodMap)

    # Process listings
    listingsDF = final_process_listings(listingsDF, hostsDF, locationsNeighborhoodMap)

    # Create CID-ID map
    listingsCIDMap = dict(zip(listingsDF['listing_cid'], listingsDF['listing_id']))

    return listingsDF, hostsDF, locationsDF, listingsCIDMap




def preprocess_reviews_data(listingsCIDMap):
    """
    Reads the reviews data from a compressed CSV file, processes it to clean and transform the data into a suitable format to insert into the database's reviews table.
    The dataframe is saved as a CSV file.
    
    Parameters:
        None
        
    Returns:
        reviewsDF: DataFrame containing cleaned reviews data.
    """

    logging.info("Processing reviews data...")
    reviewsData = read_data('data/reviews.csv.gz')

    reviewsData.rename(columns={'id':'review_cid', 'listing_id':'listing_cid'}, inplace=True)
    
    reviewsData['listing_cid'] = reviewsData['listing_cid'].astype(str)
    
    reviewsData['listing_cid'] = reviewsData['listing_cid'].replace('.0', '')
    
    reviewsData['review_cid'] = reviewsData['review_cid'].astype(str)
    
    reviewsData['reviewer_id'] = reviewsData['reviewer_id'].astype(str)

    reviewsData['reviewer_name'] = reviewsData['reviewer_name'].fillna('Unknown Reviewer')
    
    reviewsData['listing_id'] = reviewsData['listing_cid'].map(listingsCIDMap)
    
    
    # Fixing the comments colummn
    
    reviewsData['comments'] = reviewsData['comments'].fillna('No comments provided')
    
    reviewsData['comments'] = reviewsData['comments'].astype(str)
    
    reviewsData['comments'] = reviewsData['comments'].replace({r'\r\n': ' ', r'\r': ' ', r'\n': ' '}, regex=True)
    
    reviewsData['comments'] = reviewsData['comments'].str.strip()
    
    reviewsData['comments'] = reviewsData['comments'].apply(lambda x: x.encode('utf-8', 'ignore').decode('utf-8') if isinstance(x, str) else x)
    

    reviewsDF = reviewsData[['review_cid', 'listing_id', 'date', 'reviewer_id', 'reviewer_name', 'comments']]
    
    reviewsDF =reviewsDF.dropna(subset=['listing_id'])
    
    reviewsDF = reviewsDF.drop_duplicates()
    
    reviewsDF = reviewsDF.reset_index(drop=True).reset_index().rename(columns={'index': 'review_id'})
    
    reviewsDF['review_id'] = reviewsDF['review_id'] + 1000
    
    reviewsDF['review_id'] = reviewsDF['review_id'].astype(int)
    
    reviewsDF['listing_id'] = reviewsDF['listing_id'].astype(int)


    return reviewsDF
    
    
    
def preprocess_calendar_data(listingsCIDMap):
    """
    Reads the calendar data from a compressed CSV file, processes it to clean and transform the data into a suitable format to insert into the database's availability table.
    The dataframe is saved as a CSV file.
    
    Parameters:
        None
        
    Returns:
        calendarData: DataFrame containing cleaned calendar (availability) data.
    """
    logging.info("Processing calendar data...")
    calendarData = read_data('data/calendar.csv.gz')
    
    calendarData.rename(columns={'listing_id':'listing_cid'}, inplace=True)
    
    calendarData['listing_cid'] = calendarData['listing_cid'].astype(str)
    
    calendarData['listing_id'] = calendarData['listing_cid'].map(listingsCIDMap)
    
    calendarData['listing_id'] = calendarData['listing_id'].astype(int)
    
    calendarData.dropna(subset=['listing_id'], inplace=True)

    calendarData.drop(columns=['adjusted_price','listing_cid'], inplace=True)
    
    calendarData['available'] = calendarData['available'].apply(lambda x: True if x == 't' else False)

    calendarData['price'] = calendarData['price'].replace('[\$,]', '', regex=True).astype(float) # Removes dollar sign
    
    calendarData.dropna(subset=['date', 'listing_id'], inplace=True)
    
    return calendarData



if __name__ == "__main__":
    main() 





import pandas as pd
import numpy as np
import re
import time
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    
    start = time.time()
    
    logging.info("Starting data preprocessing...")
    listingsDF, hostsDF, locationsDF, amenityDF, listingAmenitiesDF = preprocess_listings_data()
    reviewsDF = preprocess_reviews_data()
    calendar_df = preprocess_calendar_data()
    
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
    Reads the listings data from a compressed CSV file, processes it to clean and transform the data into five different dataframes which are the listings, hosts, locations, amenities, and listing_amenities dataframes.
    These dataframes are then saved as CSV files.
    
    Parameters:
        None
        
    Returns:
        listingsDF: DataFrame containing cleaned listings data.
        hostsDF: DataFrame containing cleaned hosts data.
        locationsDF: DataFrame containing cleaned locations data.
        amenityDF: DataFrame containing unique amenities and their IDs.
        listingAmenitiesDF: DataFrame containing the mapping of listings to their amenities.
    """
    
    logging.info("Processing listings data...")
    
    listingsData = read_data('data/listings.csv.gz')
    
    listingsData = listingsData.reset_index().rename(columns={'index': 'listing_id'})
    listingsData['listing_id'] = listingsData['listing_id'] + 1000 
    listingsData['listing_id'] = listingsData['listing_id'].astype(int)
    
    # Selecting and renaming columns
    logging.info("Selecting and renaming columns...")
    listingsColumns = ["listing_id", "name", "description", "host_id", "listing_url", "neighbourhood_cleansed","neighborhood_overview",
        "picture_url", "latitude", "longitude", "property_type", "room_type", "accommodates",
        "bathrooms","bathrooms_text", "bedrooms", "beds", "amenities", "license", 'review_scores_rating', 'review_scores_accuracy',
        'review_scores_cleanliness', 'review_scores_checkin',
        'review_scores_communication', 'review_scores_location',
        'review_scores_value','number_of_reviews']


    listingsDF = listingsData[listingsColumns].copy()
    listingsDF.rename(columns={'review_scores_rating': 'overall_rating','review_scores_accuracy': 'accuracy_rating',
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


    logging.info("Processing hosts and locations data from listings data...")
    hostsColumns = ['host_id', 'host_name', 'host_url','host_since', 'host_location','host_about', 'host_response_time',
                    'host_response_rate', 'host_acceptance_rate', 'host_is_superhost','host_thumbnail_url','host_picture_url',
                    'host_neighbourhood', 'host_total_listings_count', 'host_has_profile_pic', 'host_identity_verified','host_verifications']

    hostsDF = listingsData[hostsColumns].copy()

    # Filling in missing values for location related columns
    hostsDF['host_neighbourhood'] = np.where((hostsDF['host_location'].isna())&(hostsDF['host_neighbourhood'].isna()), 'Unknown', hostsDF['host_neighbourhood'])
    hostsDF['host_neighbourhood'] = hostsDF['host_neighbourhood'].fillna('Not Specified')

    hostsDF['host_location'] = np.where((hostsDF['host_location'].isna()) & (hostsDF['host_neighbourhood'] == 'Unknown'), 'Unknown', hostsDF['host_location'])
    hostsDF['host_location'] = hostsDF['host_location'].fillna('Boston, MA')
    
    listingsDF['neighbourhood_cleansed'] = listingsDF['neighbourhood_cleansed'].fillna('Not Specified')
    listingsDF['location'] = 'Boston, MA'
    


    # Creating a DataFrame for locations
    locationsDF = hostsDF[['host_neighbourhood','host_location']].drop_duplicates().reset_index(drop=True).rename(columns={'host_neighbourhood': 'neighbourhood', 'host_location': 'location'})

    listingsLocationDF = listingsDF[['neighbourhood_cleansed', 'location']].drop_duplicates().reset_index(drop=True).rename(columns={'neighbourhood_cleansed': 'neighbourhood', 'location': 'location'})

    locationsDF = pd.concat([locationsDF, listingsLocationDF], ignore_index=True).drop_duplicates().reset_index(drop=True).reset_index().rename(columns={'index': 'location_id'})
    locationsDF['location_id'] = locationsDF['location_id'] + 1
    
    
    # Mapping hosts data with locations
    logging.info("Mapping hosts and listings data with locations...")
    locationsNeighborhoodMap = dict(zip(locationsDF['neighbourhood']+', '+ locationsDF['location'], locationsDF['location_id']))

    hostsDF['location_id'] = hostsDF.apply(lambda row: locationsNeighborhoodMap[row['host_neighbourhood'] + ', ' + row['host_location']], axis=1)

    hostsDF.drop(columns=['host_neighbourhood', 'host_location'], inplace=True)
    
    hostsDF = hostsDF[['host_id', 'host_name', 'host_url', 'host_since', 'location_id', 'host_about',
        'host_response_time', 'host_response_rate', 'host_acceptance_rate',
        'host_is_superhost', 'host_thumbnail_url', 'host_picture_url',
        'host_total_listings_count', 'host_verifications', 'host_has_profile_pic',
        'host_identity_verified']]

    hostsDF['host_name'] = hostsDF['host_name'].fillna('Unknown Host')

    hostsDF['host_is_superhost'] = hostsDF['host_is_superhost'].apply(lambda x: True if x == 't' else False)
    hostsDF['host_has_profile_pic'] = hostsDF['host_has_profile_pic'].apply(lambda x: True if x == 't' else False)
    hostsDF['host_identity_verified'] = hostsDF['host_identity_verified'].apply(lambda x: True if x == 't' else False)
    hostsDF['host_response_rate'] = hostsDF['host_response_rate'].str.replace('%', '').astype(float)
    hostsDF['host_acceptance_rate'] = hostsDF['host_acceptance_rate'].str.replace('%', '').astype(float)
    hostsDF.drop_duplicates(inplace=True)
    
    hostsDF['host_id'] = pd.to_numeric(hostsDF['host_id'], errors='coerce')
    hostsDF.dropna(subset=['host_id'], inplace=True)
    hostsDF['host_id'] = hostsDF['host_id'].astype(int)
    

    # Mapping listings data with locations
    logging.info("Mapping listings data with locations...")
    listingsDF['location_id'] = listingsDF.apply(lambda row: locationsNeighborhoodMap[row['neighbourhood_cleansed'] + ', ' + row['location']], axis=1)

    listingsDF.drop(columns=['neighbourhood_cleansed', 'location'], inplace=True)

    listingsDF = listingsDF[['listing_id', 'name', 'description', 'host_id', 'listing_url',
        'location_id', 'neighborhood_overview', 'picture_url',
        'latitude', 'longitude', 'property_type', 'room_type', 'accommodates',
        'bathrooms', 'bedrooms', 'bathroom_type', 'beds', 'amenities', 'license',
        'overall_rating', 'accuracy_rating', 'cleanliness_rating',
        'checkin_rating', 'communication_rating', 'location_rating',
        'value_rating', 'number_of_reviews']]
    
    listingsDF['amenities'] = listingsDF['amenities'].apply(lambda x: ','.join(map(str, x)))
    
    listingsDF['host_id'] = pd.to_numeric(listingsDF['host_id'], errors='coerce')
    listingsDF.dropna(subset=['host_id'], inplace=True)
    listingsDF['host_id'] = listingsDF['host_id'].astype(int)
    
    listingsDF['listing_id'] = pd.to_numeric(listingsDF['listing_id'], errors='coerce')
    listingsDF.dropna(subset=['listing_id'], inplace=True)
    listingsDF['listing_id'] = listingsDF['listing_id'].astype(int)
    
    listingsDF.drop_duplicates(inplace=True)
    listingsDF = listingsDF.drop_duplicates(subset=['listing_id'], keep='first')
    
    locationsDF.rename(columns={'neighbourhood': 'neighborhood'}, inplace=True)

    
    return listingsDF, hostsDF, locationsDF, amenityDF, listingAmenitiesDF




def preprocess_reviews_data():
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

    reviewsData.rename(columns={'id':'review_id'}, inplace=True)

    reviewsData['reviewer_name'] = reviewsData['reviewer_name'].fillna('Unknown Reviewer')

    reviewsDF = reviewsData[['review_id', 'listing_id', 'date', 'reviewer_id', 'reviewer_name', 'comments']]

    reviewsDF['comments'] = reviewsDF['comments'].fillna('No comments provided')

    return reviewsDF
    
    
    
def preprocess_calendar_data():
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

    calendarData.drop(columns=['adjusted_price'], inplace=True)
    calendarData['available'] = calendarData['available'].apply(lambda x: True if x == 't' else False)

    calendarData['price'] = calendarData['price'].replace('[\$,]', '', regex=True).astype(float) # Remove dollar sign

    calendarData.to_csv('data/cleaned_availability.csv', index=False)
    
    logging.info("Calendar data saved to cleaned_availability.csv")
    
    return calendarData



if __name__ == "__main__":
    main() 





-- DB: PostgreSQL

-- Silver Schema
CREATE SCHEMA IF NOT EXISTS silver;

-- Silver Tables

-- Locations
CREATE TABLE IF NOT EXISTS silver.bnb_dim_locations (
    location_id SERIAL PRIMARY KEY,
    location TEXT NOT NULL,
    neighborhood TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_bnb_dim_locations_name ON silver.bnb_dim_locations(location);
CREATE INDEX IF NOT EXISTS idx_bnb_dim_locations_neighborhood ON silver.bnb_dim_locations(neighborhood);

-- Hosts
CREATE TABLE IF NOT EXISTS silver.bnb_dim_hosts (
    host_id SERIAL PRIMARY KEY,
    host_cid TEXT UNIQUE NOT NULL,
    host_name TEXT NOT NULL,
    host_url TEXT NOT NULL,
    host_since TEXT,
    location_id INT NOT NULL REFERENCES silver.bnb_dim_locations(location_id),
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_bnb_dim_hosts_location_id ON silver.bnb_dim_hosts(location_id);

-- Listings
CREATE TABLE IF NOT EXISTS silver.bnb_dim_listings (
    listing_id SERIAL PRIMARY KEY,
    listing_cid TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    host_id INT NOT NULL REFERENCES silver.bnb_dim_hosts(host_id),
    listing_url TEXT NOT NULL,
    location_id INT NOT NULL REFERENCES silver.bnb_dim_locations(location_id),
    neighborhood_overview TEXT,
    picture_url TEXT,
    latitude FLOAT,
    longitude FLOAT,
    property_type TEXT,
    room_type TEXT,
    accommodates INT,
    bathrooms FLOAT,
    bathroom_type TEXT,
    bedrooms INT,
    beds INT,
    amenities TEXT,
    license TEXT,
    overall_rating FLOAT CHECK(overall_rating >= 0 AND overall_rating <= 5),
    accuracy_rating FLOAT CHECK(accuracy_rating >= 0 AND accuracy_rating <= 5),
    cleanliness_rating FLOAT CHECK(cleanliness_rating >= 0 AND cleanliness_rating <= 5),
    checkin_rating FLOAT CHECK(checkin_rating >= 0 AND checkin_rating <= 5),
    communication_rating FLOAT CHECK(communication_rating >= 0 AND communication_rating <= 5),
    location_rating FLOAT CHECK(location_rating >= 0 AND location_rating <= 5),
    value_rating FLOAT CHECK(value_rating >= 0 AND value_rating <= 5),
    number_of_reviews INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_bnb_dim_listings_host_id ON silver.bnb_dim_listings(host_id);
CREATE INDEX IF NOT EXISTS idx_bnb_dim_listings_location_id ON silver.bnb_dim_listings(location_id);
CREATE INDEX IF NOT EXISTS idx_bnb_dim_listings_lat_long ON silver.bnb_dim_listings(latitude, longitude);

-- Reviews
CREATE TABLE IF NOT EXISTS silver.bnb_fact_reviews (
    review_id SERIAL PRIMARY KEY,
    review_cid TEXT UNIQUE NOT NULL,
    listing_id INT NOT NULL REFERENCES silver.bnb_dim_listings(listing_id),
    date DATE NOT NULL,
    reviewer_id TEXT NOT NULL,
    reviewer_name TEXT NOT NULL,
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_bnb_fact_reviews_listing_id ON silver.bnb_fact_reviews(listing_id);
CREATE INDEX IF NOT EXISTS idx_bnb_fact_reviews_date ON silver.bnb_fact_reviews(date);

-- Amenities
CREATE TABLE IF NOT EXISTS silver.bnb_dim_amenities (
    amenity_id SERIAL PRIMARY KEY,
    amenity_name TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_bnb_dim_amenities_name ON silver.bnb_dim_amenities(amenity_name);

-- Listing Amenities
CREATE TABLE IF NOT EXISTS silver.bnb_br_listing_amenities (
    listing_id INT NOT NULL REFERENCES silver.bnb_dim_listings(listing_id),
    amenity_id INT NOT NULL REFERENCES silver.bnb_dim_amenities(amenity_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (listing_id, amenity_id)
);

-- Availability
CREATE TABLE IF NOT EXISTS silver.bnb_fact_availability (
    listing_id INT NOT NULL REFERENCES silver.bnb_dim_listings(listing_id),
    date DATE NOT NULL,
    available BOOLEAN NOT NULL,
    minimum_nights INT DEFAULT 1,
    maximum_nights INT DEFAULT 365,
    price FLOAT CHECK(price >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (listing_id, date)
);

CREATE INDEX IF NOT EXISTS idx_bnb_fact_availability_listing_id ON silver.bnb_fact_availability(listing_id);
CREATE INDEX IF NOT EXISTS idx_bnb_fact_availability_date ON silver.bnb_fact_availability(date);


-- Gold Schema
CREATE SCHEMA IF NOT EXISTS gold;

-- Gold Views
CREATE OR REPLACE VIEW gold.vw_listing_overview AS
SELECT 
	l.listing_id, 
	l.name as "Listing Name",
	l.picture_url as "Picture",
	CASE 
        WHEN LENGTH(l.description) > 400 THEN LEFT(l.description, 200) || '...'
        ELSE l.description
    END AS "Description",
	h.host_name as "Host Name",
	lc.neighborhood as "Neighborhood", 
	l.latitude,
	l.longitude,
	CASE 
        WHEN LENGTH(l.neighborhood_overview) > 400 THEN LEFT(l.neighborhood_overview, 200) || '...'
        ELSE l.neighborhood_overview
    END AS "Neighborhood Overview",
	l.room_type as "Room Type", 
	l.amenities as "Amenities", 
	l.overall_rating as "Rating", 
	l.number_of_reviews as "Reviews"
FROM silver.bnb_dim_listings as l
LEFT JOIN silver.bnb_dim_hosts as h
ON l.host_id = h.host_id
LEFT JOIN silver.bnb_dim_locations as lc
ON l.location_id = lc.location_id;
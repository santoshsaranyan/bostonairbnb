-- DataBase Type: PostgreSQL
-- Hosted in: localhost:5432

----------------------------------------------------------------------------------

-- Bronze Schema
CREATE SCHEMA IF NOT EXISTS bronze;

-- Bronze Tables

-- Listings Raw Data
CREATE TABLE IF NOT EXISTS bronze.bnb_raw_listings (
    raw_listings_id SERIAL PRIMARY KEY,
    raw_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reviews Raw Data
CREATE TABLE IF NOT EXISTS bronze.bnb_raw_reviews (
    raw_reviews_id SERIAL PRIMARY KEY,
    raw_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Availability Raw Data
CREATE TABLE IF NOT EXISTS bronze.bnb_raw_availability (
    raw_availability_id SERIAL PRIMARY KEY,
    raw_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

----------------------------------------------------------------------------------

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
    host_since DATE,
    location_id INT NOT NULL REFERENCES silver.bnb_dim_locations(location_id),
    host_about TEXT,
    host_response_time TEXT,
    host_response_rate NUMERIC(5,2) CHECK(host_response_rate >= 0 AND host_response_rate <= 100),
    host_acceptance_rate NUMERIC(5,2) CHECK(host_acceptance_rate >= 0 AND host_acceptance_rate <= 100),
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
    bathrooms NUMERIC(3,1),
    bathroom_type TEXT,
    bedrooms INT,
    beds INT,
    amenities TEXT,
    license TEXT,
    overall_rating NUMERIC(2,1) CHECK(overall_rating >= 0 AND overall_rating <= 5),
    accuracy_rating NUMERIC(2,1) CHECK(accuracy_rating >= 0 AND accuracy_rating <= 5),
    cleanliness_rating NUMERIC(2,1) CHECK(cleanliness_rating >= 0 AND cleanliness_rating <= 5),
    checkin_rating NUMERIC(2,1) CHECK(checkin_rating >= 0 AND checkin_rating <= 5),
    communication_rating NUMERIC(2,1) CHECK(communication_rating >= 0 AND communication_rating <= 5),
    location_rating NUMERIC(2,1) CHECK(location_rating >= 0 AND location_rating <= 5),
    value_rating NUMERIC(2,1) CHECK(value_rating >= 0 AND value_rating <= 5),
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
    price NUMERIC(10,2) CHECK(price >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (listing_id, date)
);

CREATE INDEX IF NOT EXISTS idx_bnb_fact_availability_listing_id ON silver.bnb_fact_availability(listing_id);
CREATE INDEX IF NOT EXISTS idx_bnb_fact_availability_date ON silver.bnb_fact_availability(date);

----------------------------------------------------------------------------------

-- Gold Schema
CREATE SCHEMA IF NOT EXISTS gold;

-- Gold Views

-- Listing Overview View
CREATE MATERIALIZED VIEW gold.mv_listing_overview AS
SELECT 
	l.listing_id, 
	l.name AS "Listing Name",
	l.picture_url AS "Picture",
	CASE 
        WHEN LENGTH(l.description) > 400 THEN LEFT(l.description, 200) || '...'
        ELSE l.description
    END AS "Description",
	h.host_name AS "Host Name",
	lc.neighborhood AS "Neighborhood", 
	l.latitude,
	l.longitude,
	CASE 
        WHEN LENGTH(l.neighborhood_overview) > 400 THEN LEFT(l.neighborhood_overview, 200) || '...'
        ELSE l.neighborhood_overview
    END AS "Neighborhood Overview",
	l.room_type AS "Room Type", 
	l.amenities AS "Amenities", 
	l.overall_rating AS "Rating", 
	l.number_of_reviews AS "Reviews"
FROM silver.bnb_dim_listings AS l
LEFT JOIN silver.bnb_dim_hosts AS h
ON l.host_id = h.host_id
LEFT JOIN silver.bnb_dim_locations AS lc
ON l.location_id = lc.location_id;

-- Host Summary View
CREATE MATERIALIZED VIEW gold.mv_host_summary AS
SELECT 
	h.host_id,
	h.host_name AS "Host Name",
	h.host_since AS "Host Since",
	h.host_total_listings_count AS "Host Listings Count",
	h.host_is_superhost AS "Superhost Status",
	h.host_response_rate AS "Host Response Rate",
	h.host_acceptance_rate AS "Host Acceptance Rate",
	ROUND(lh.overall_rating,1) AS "Overall Rating",
	lh.number_of_reviews AS "Number of Reviews"
FROM silver.bnb_dim_hosts AS h
LEFT JOIN (
	SELECT 
		l.host_id,
		AVG(l.overall_rating) AS overall_rating,
		SUM(l.number_of_reviews) AS number_of_reviews
	FROM silver.bnb_dim_listings AS l
	GROUP BY host_id
	) AS lh
ON h.host_id = lh.host_id;

-- Review Activity Summary View
CREATE MATERIALIZED VIEW gold.mv_review_activity AS
WITH review_counts AS (
    SELECT
        TO_CHAR(r.date, 'YYYY-MM') AS review_month,
        l.listing_id,
        lc.neighborhood,
        l.host_id
    FROM silver.bnb_fact_reviews r
    JOIN silver.bnb_dim_listings l ON r.listing_id = l.listing_id
    JOIN silver.bnb_dim_locations lc ON l.location_id = lc.location_id
),
neighborhood_top AS (
	SELECT
		review_month,
		neighborhood,
		ROW_NUMBER() OVER (PARTITION BY review_month ORDER BY COUNT(*) DESC) AS ranknum
	FROM review_counts
	GROUP BY review_month, neighborhood
),
host_top AS (
	SELECT
		review_month,
		host_id,
		ROW_NUMBER() OVER (PARTITION BY review_month ORDER BY COUNT(*) DESC) AS ranknum
	FROM review_counts
	GROUP BY review_month, host_id
),
monthly_summary AS (
    SELECT
        review_month,
        COUNT(*) AS total_reviews,
        COUNT(DISTINCT listing_id) AS distinct_listings_reviewed
    FROM review_counts
    GROUP BY review_month
)
SELECT 
	ms.review_month AS "Review Month",
	nt.neighborhood AS "Most Reviewed Neighborhood",
	h.host_name AS "Most Reviewed Host",
	ms.total_reviews AS "Reviews",
	ms.distinct_listings_reviewed AS "Unique Listings"
FROM monthly_summary AS ms
LEFT JOIN neighborhood_top AS nt
ON ms.review_month = nt.review_month and nt.ranknum = 1
LEFT JOIN host_top AS ht
ON ms.review_month = ht.review_month and ht.ranknum = 1
LEFT JOIN silver.bnb_dim_hosts AS h
ON ht.host_id = h.host_id
ORDER BY "Review Month";

-- Neighborhood Summary View
CREATE MATERIALIZED VIEW gold.mv_neighborhood_summary AS
WITH neighborhood_counts AS (
	SELECT
		lc.neighborhood,
		l.listing_id,
		l.overall_rating,
		l.number_of_reviews,
		l.accommodates,
		l.room_type
	FROM silver.bnb_dim_listings AS l
	LEFT JOIN silver.bnb_dim_locations AS lc
	ON l.location_id = lc.location_id
),
top_room_type AS (
	SELECT
		neighborhood,
		room_type,
		ROW_NUMBER() OVER (PARTITION BY neighborhood ORDER BY COUNT(*) DESC) AS rownum
	FROM neighborhood_counts
	GROUP BY neighborhood, room_type
),
neighborhood_summary AS (
	SELECT
		neighborhood,
		SUM(number_of_reviews) AS total_reviews,
		COUNT(listing_id) AS total_listings,
		ROUND(AVG(overall_rating),1) AS overall_rating,
		ROUND(AVG(accommodates),0) AS average_accommodates
	FROM neighborhood_counts
	GROUP BY neighborhood
)
SELECT
	ns.neighborhood AS "Neighborhood",
	ns.total_reviews AS "Total Reviews",
	ns.total_listings AS "Total Listings",
	ns.overall_rating AS "Average Overall Rating",
	ns.average_accommodates AS "Average Accommodates",
	tr.room_type AS "Most Common Room Type"
FROM neighborhood_summary AS ns
LEFT JOIN top_room_type AS tr
ON ns.neighborhood = tr.neighborhood and tr.rownum = 1;

-- Amenity Summary View
CREATE MATERIALIZED VIEW gold.mv_amenity_summary AS
WITH amenity_counts AS (
	SELECT
		la.amenity_id,
		l.listing_id,
		l.overall_rating
	FROM silver.bnb_dim_listings AS l
	LEFT JOIN silver.bnb_br_listing_amenities AS la
	ON l.listing_id = la.listing_id
),
amenity_summary AS (
	SELECT
		amenity_id,
		COUNT(listing_id) AS listing_count,
		ROUND(AVG(overall_rating),1) AS average_rating
	FROM amenity_counts
	GROUP BY amenity_id
),
total_listings_sum AS (
	SELECT
		COUNT(*) AS total_listings
	FROM silver.bnb_dim_listings
)
SELECT
	am.amenity_name AS "Amenity",
	ams.listing_count AS "Listings Count",
	ams.average_rating AS "Average Rating for Listings",
	ROUND((ams.listing_count::numeric / tl.total_listings)*100,1) AS "Percent of Total Listings"
FROM amenity_summary AS ams
CROSS JOIN total_listings_sum AS tl
LEFT JOIN silver.bnb_dim_amenities AS am
ON ams.amenity_id = am.amenity_id;

-- Availability Summary View
CREATE MATERIALIZED VIEW gold.mv_availability_summary AS
SELECT
    a.listing_id,
    l.name AS "Listing Name",
    lc.neighborhood AS "Neighborhood",
    COUNT(a.date) AS "Total Days Tracked",
    SUM(CASE WHEN a.available = true THEN 1 ELSE 0 END) AS "Available Days",
    SUM(CASE WHEN a.available = false THEN 1 ELSE 0 END) AS "Unavailable Days",
    ROUND(SUM(CASE WHEN a.available = true THEN 1 ELSE 0 END)::numeric / COUNT(a.date) * 100, 1) AS "Availability Rate",
    ROUND(AVG(a.minimum_nights), 2) AS "Min Nights Avg",
    ROUND(AVG(a.maximum_nights), 2) AS "Max Nights Avg"
FROM silver.bnb_fact_availability AS a
LEFT JOIN silver.bnb_dim_listings AS l
  ON a.listing_id = l.listing_id
LEFT JOIN silver.bnb_dim_locations AS lc
  ON l.location_id = lc.location_id
GROUP BY a.listing_id, l.name, lc.neighborhood
ORDER BY a.listing_id;

-- Availability Trend View
CREATE MATERIALIZED VIEW gold.mv_availability_trend AS
SELECT
    TO_CHAR(a.date,'YYYY-MM') AS "Month",
    lc.neighborhood AS "Neighborhood",
    ROUND(AVG(CASE WHEN a.available = true THEN 1.0 ELSE 0 END) * 100, 1) AS "Avg Availability Rate"
FROM silver.bnb_fact_availability AS a
LEFT JOIN silver.bnb_dim_listings AS l
  ON a.listing_id = l.listing_id
LEFT JOIN silver.bnb_dim_locations AS lc
  ON l.location_id = lc.location_id
GROUP BY "Month", lc.neighborhood
ORDER BY "Month", lc.neighborhood;

-- Indexes for Gold Views

-- Listing Overview View Index
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_listing_overview_listing_id ON gold.mv_listing_overview(listing_id);
CREATE INDEX IF NOT EXISTS idx_mv_listing_overview_neighborhood ON gold.mv_listing_overview("Neighborhood");
CREATE INDEX IF NOT EXISTS idx_mv_listing_overview_host_name ON gold.mv_listing_overview("Host Name");

-- Host Summary View Index
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_host_summary_host_id ON gold.mv_host_summary(host_id);
CREATE INDEX IF NOT EXISTS idx_mv_host_summary_overall_rating ON gold.mv_host_summary("Overall Rating");

-- Review Activity Summary View Index
CREATE INDEX IF NOT EXISTS idx_mv_review_activity_month ON gold.mv_review_activity("Review Month");
CREATE INDEX IF NOT EXISTS idx_mv_review_activity_neighborhood ON gold.mv_review_activity("Most Reviewed Neighborhood");
CREATE INDEX IF NOT EXISTS idx_mv_review_activity_host ON gold.mv_review_activity("Most Reviewed Host");

-- Neighborhood Summary View Index
CREATE INDEX IF NOT EXISTS idx_mv_neighborhood_summary_neighborhood ON gold.mv_neighborhood_summary("Neighborhood");
CREATE INDEX IF NOT EXISTS idx_mv_neighborhood_summary_avg_rating ON gold.mv_neighborhood_summary("Average Overall Rating");

-- Amenity Summary View Index
CREATE INDEX IF NOT EXISTS idx_mv_amenity_summary_amenity ON gold.mv_amenity_summary("Amenity");

-- Availability Summary View Index
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_availability_summary_listing_id ON gold.mv_availability_summary(listing_id);
CREATE INDEX IF NOT EXISTS idx_mv_availability_summary_neighborhood ON gold.mv_availability_summary("Neighborhood");

-- Availability Trend View Index
CREATE INDEX IF NOT EXISTS idx_mv_availability_trend_month ON gold.mv_availability_trend("Month");
CREATE INDEX IF NOT EXISTS idx_mv_availability_trend_neighborhood ON gold.mv_availability_trend("Neighborhood");

-- DataBase Type: PostgreSQL
-- Hosted in: Supabase

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
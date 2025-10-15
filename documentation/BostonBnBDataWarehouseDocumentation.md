# Boston BnB Data Warehouse — Documentation

**Database Type:** PostgreSQL  
**Host:** `Supabase`  
**Schemas:** `bronze`, `silver`, `gold`

---

## Bronze Schema
**Purpose:**  
Stores raw, unprocessed JSON data directly from the source files for reproducibility and traceability.

### Table: `bronze.bnb_raw_listings`
| Column | Type | Description |
|--------|------|-------------|
| `raw_listings_id` | SERIAL (PK) | Unique identifier for each raw listings entry. |
| `raw_data` | JSONB | Full JSON payload containing raw listing details. |
| `created_at` | TIMESTAMP | Timestamp when the record was inserted. |

---

### Table: `bronze.bnb_raw_reviews`
| Column | Type | Description |
|--------|------|-------------|
| `raw_reviews_id` | SERIAL (PK) | Unique identifier for each raw review entry. |
| `raw_data` | JSONB | Full JSON payload containing raw review data. |
| `created_at` | TIMESTAMP | Timestamp when the record was inserted. |

---

### Table: `bronze.bnb_raw_availability`
| Column | Type | Description |
|--------|------|-------------|
| `raw_availability_id` | SERIAL (PK) | Unique identifier for each raw availability entry. |
| `raw_data` | JSONB | Full JSON payload containing raw availability data. |
| `created_at` | TIMESTAMP | Timestamp when the record was inserted. |

---

## Silver Schema
**Purpose:**  
Cleansed, structured, and relational data derived from bronze. Forms the **core star schema** (dimensions and facts).

---

### Table: `silver.bnb_dim_locations`
| Column | Type | Description |
|--------|------|-------------|
| `location_id` | SERIAL (PK) | Unique ID for the location. |
| `location` | TEXT | Name of the city or area. |
| `neighborhood` | TEXT | Sub-region or neighborhood within the location. |
| `created_at` | TIMESTAMP | Record creation timestamp. |

**Indexes:**
- `idx_bnb_dim_locations_name` — for location lookup  
- `idx_bnb_dim_locations_neighborhood` — for neighborhood-based queries

---

### Table: `silver.bnb_dim_hosts`
| Column | Type | Description |
|--------|------|-------------|
| `host_id` | SERIAL (PK) | Unique host ID. |
| `host_cid` | TEXT | Source system’s host identifier. |
| `host_name` | TEXT | Name of the host. |
| `host_url` | TEXT | Host’s public listing URL. |
| `host_since` | DATE | Date when the host joined the platform. |
| `location_id` | INT (FK) | Reference to `bnb_dim_locations`. |
| `host_about` | TEXT | Description provided by the host. |
| `host_response_time` | TEXT | Average response time (e.g., “within an hour”). |
| `host_response_rate` | NUMERIC(5,2) | % of responses sent by host. |
| `host_acceptance_rate` | NUMERIC(5,2) | % of booking requests accepted. |
| `host_is_superhost` | BOOLEAN | Whether the host is a Superhost. |
| `host_thumbnail_url` | TEXT | Thumbnail image URL. |
| `host_picture_url` | TEXT | Full-size profile picture URL. |
| `host_total_listings_count` | INT | Number of listings managed by host. |
| `host_verifications` | TEXT | Comma-separated list of host verifications. |
| `host_has_profile_pic` | BOOLEAN | Whether profile picture exists. |
| `host_identity_verified` | BOOLEAN | Identity verified flag. |
| `created_at` | TIMESTAMP | Record creation timestamp. |

**Indexes:**
- `idx_bnb_dim_hosts_location_id` — joins with location

---

### Table: `silver.bnb_dim_listings`
| Column | Type | Description |
|--------|------|-------------|
| `listing_id` | SERIAL (PK) | Unique listing ID. |
| `listing_cid` | TEXT | Source system’s listing identifier. |
| `name` | TEXT | Name/title of the listing. |
| `description` | TEXT | Full description text. |
| `host_id` | INT (FK) | Reference to `bnb_dim_hosts`. |
| `listing_url` | TEXT | URL to the listing page. |
| `location_id` | INT (FK) | Reference to `bnb_dim_locations`. |
| `neighborhood_overview` | TEXT | Description of the neighborhood. |
| `picture_url` | TEXT | Listing’s main photo URL. |
| `latitude` / `longitude` | FLOAT | Coordinates for map visualization. |
| `property_type` | TEXT | Type of property (Apartment, House, etc.). |
| `room_type` | TEXT | Type of room (Private, Shared, Entire Home, etc.). |
| `accommodates` | INT | Max number of guests. |
| `bathrooms` | NUMERIC(3,1) | Number of bathrooms. |
| `bathroom_type` | TEXT | Type of bathroom (Private, Shared, etc.). |
| `bedrooms` | INT | Number of bedrooms. |
| `beds` | INT | Number of beds. |
| `amenities` | TEXT | Comma-separated amenities list. |
| `license` | TEXT | License information (if any). |
| `overall_rating` to `value_rating` | NUMERIC(2,1) | Review-based ratings (0–5). |
| `number_of_reviews` | INT | Count of reviews received. |
| `created_at` | TIMESTAMP | Record creation timestamp. |

**Indexes:**
- Host ID, Location ID, (Latitude, Longitude)

---

### Table: `silver.bnb_fact_reviews`
| Column | Type | Description |
|--------|------|-------------|
| `review_id` | SERIAL (PK) | Unique review ID. |
| `review_cid` | TEXT | Source review identifier. |
| `listing_id` | INT (FK) | Linked listing. |
| `date` | DATE | Review date. |
| `reviewer_id` | TEXT | Reviewer’s ID. |
| `reviewer_name` | TEXT | Reviewer’s name. |
| `comments` | TEXT | Review text. |
| `created_at` | TIMESTAMP | Record creation timestamp. |

**Indexes:**
- By listing and date for time-based review analysis.

---

### Table: `silver.bnb_dim_amenities`
| Column | Type | Description |
|--------|------|-------------|
| `amenity_id` | SERIAL (PK) | Unique amenity ID. |
| `amenity_name` | TEXT | Name of the amenity (e.g., Wi-Fi). |
| `created_at` | TIMESTAMP | Record creation timestamp. |

---

### Table: `silver.bnb_br_listing_amenities`
| Column | Type | Description |
|--------|------|-------------|
| `listing_id` | INT (FK) | Reference to listing. |
| `amenity_id` | INT (FK) | Reference to amenity. |
| `created_at` | TIMESTAMP | Record creation timestamp. |

**Primary Key:** `(listing_id, amenity_id)`  
**Purpose:** Bridge table for many-to-many relationship between listings and amenities.

---

### Table: `silver.bnb_fact_availability`
| Column | Type | Description |
|--------|------|-------------|
| `listing_id` | INT (FK) | Reference to listing. |
| `date` | DATE | Calendar date of record. |
| `available` | BOOLEAN | Availability status. |
| `minimum_nights` | INT | Minimum nights allowed. |
| `maximum_nights` | INT | Maximum nights allowed. |
| `price` | NUMERIC(10,2) | Price per night. |
| `created_at` | TIMESTAMP | Record creation timestamp. |

**Primary Key:** `(listing_id, date)`  
**Indexes:** By listing and date for time series queries.

---

## Gold Schema
**Purpose:**  
Aggregated and denormalized **materialized views** optimized for analytics and visualization dashboard queries.

---

### View: `gold.mv_listing_overview`
| Column | Type | Description |
|---------|------|-------------|
| `listing_id`| INTEGER | Unique identifier of the listing |
| `Listing Name` | TEXT | Name of the property |
| `Picture` | TEXT | URL of listing image |
| `Description` | TEXT | Shortened listing description (max 200 chars + ellipsis) |
| `Host Name` | TEXT | Name of the host |
| `Neighborhood` | TEXT | Neighborhood where listing is located |
| `latitude` | NUMERIC | Latitude coordinate |
| `longitude` | NUMERIC | Longitude coordinate |
| `Neighborhood Overview` | TEXT | Shortened overview of the neighborhood |
| `Room Type` | TEXT | Type of accommodation (e.g., Entire home, Private room) |
| `Amenities` | TEXT | Comma-separated list of amenities |
| `Rating` | NUMERIC | Overall rating of the listing |
| `Reviews` | INTEGER | Total number of reviews |

---

### View: `gold.mv_host_summary`
| Column | Type | Description |
|---------|------|-------------|
| `host_id` | INTEGER | Unique identifier for the host |
| `Host Name` | TEXT | Name of the host |
| `Host Since` | DATE | Date when the host joined |
| `Host Listings Count` | INTEGER | Number of active listings |
| `Superhost Status` | BOOLEAN | Indicates if host is a Superhost |
| `Host Response Rate` | NUMERIC | Percentage of inquiries responded to |
| `Host Acceptance Rate` | NUMERIC | Percentage of bookings accepted |
| `Overall Rating` | NUMERIC | Average listing rating for host |
| `Number of Reviews` | INTEGER | Total number of reviews across listings |

---

### View: `gold.mv_review_activity`
| Column | Type | Description |
|---------|------|-------------|
| `Review Month`| TEXT | Month of review activity (YYYY-MM) |
| `Most Reviewed Neighborhood` | TEXT | Neighborhood with the highest review count in that month |
| `Most Reviewed Host` | TEXT | Host receiving the most reviews in that month |
| `Reviews` | INTEGER | Total number of reviews |
| `Unique Listings` | INTEGER | Number of distinct listings reviewed that month |

---

### View: `gold.mv_neighborhood_summary`
| Column | Type | Description |
|---------|------|-------------|
| `Neighborhood` | TEXT | Neighborhood name |
| `Total Reviews` | INTEGER | Sum of all reviews in the neighborhood |
| `Total Listings` | INTEGER | Total number of listings |
| `Average Overall Rating` | NUMERIC | Mean overall rating of listings |
| `Average Accommodates` | NUMERIC | Average number of guests accommodated |
| `Most Common Room Type` | TEXT | Most frequent room type in the neighborhood |

---

### View: `gold.mv_amenity_summary`
| Column | Type | Description |
|---------|------|-------------|
| `Amenity` | TEXT | Name of the amenity |
| `Listings Count` | INTEGER | Number of listings offering this amenity |
| `Average Rating for Listings` | NUMERIC | Average rating for listings with this amenity |
| `Percent of Total Listings` | NUMERIC | Percentage of listings that include this amenity |

---

### View: `gold.mv_availability_summary`
| Column | Type | Description |
|---------|------|-------------|
| `listing_id` | INTEGER | Unique listing identifier |
| `Listing Name` | TEXT | Name of the listing |
| `Neighborhood` | TEXT | Neighborhood where listing is located |
| `Total Days Tracked` | INTEGER | Number of days recorded for the listing |
| `Available Days` | INTEGER | Number of days available |
| `Unavailable Days` | INTEGER | Number of days unavailable/booked |
| `Availability Rate` | NUMERIC | Percentage of available days |
| `Min Nights Avg` | NUMERIC | Average minimum nights required |
| `Max Nights Avg` | NUMERIC | Average maximum nights allowed |

---

### View: `gold.mv_availability_trend`
| Column | Type | Description |
|---------|------|-------------|
| `Month` | TEXT | Month of record (YYYY-MM) |
| `Neighborhood` | TEXT | Neighborhood name |
| `Avg Availability Rate` | NUMERIC | Average availability percentage across listings |

---


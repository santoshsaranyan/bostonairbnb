# Boston BnB Insights App
This project, consisting of a Streamlit app, demonstrates a complete end-to-end **data engineering and analytics pipeline** for Boston Airbnb listings, built using **Python**, **PostgreSQL**, and **Docker**. The AirBnB data is stored in a PostgreSQL database which is modelled after a small-scale data warehouse.

You can find the link to the app, hosted on streamlit cloud, here: [Boston BnB App](https://bostonairbnb-dataengineeringproject.streamlit.app)

> **Note:** The link might not work on Safari. If you encounter issues, try opening it in another browser.  
> If the webpage displays “The App has gone to sleep,” click the **“Yes, get it back up”** button to restart it.

### Data Architecture Overview

![Data Architecture](https://github.com/santoshsaranyan/bostonairbnb/blob/main/streamlit_app/images/DataArchitecture.png)

Refer to the `documentations` folder for more details about the Data Architecture.

> **Note:** Some design choices in this project were made intentionally for learning purposes.  
> For example, although the source Airbnb datasets were provided as structured gzipped CSV files, the raw data in the Bronze layer is stored in PostgreSQL using JSONB columns to demonstrate handling of semi-structured data within Postgres.  
> In a production-grade setup, these raw files would typically reside in an object store (such as Amazon S3, Azure Blob Storage/Data Lake Storage) or be ingested as staging tables, with the Bronze layer referencing those files directly before transformation into the Silver and Gold layers.


### ETL Pipeline Overview
The whole ETL process is contained within a Docker container, and automated to run on a monthly schedule using GitHub Actions. The pipeline consists of three main steps:

1. Data Scraping
Retrieves the latest Boston Airbnb datasets directly from InsideAirbnb, which provides data for the past 12 months updated quarterly.
2. Data Preprocessing
Cleans, standardizes, and prepares the data for storage and analysis — handling missing values, formatting columns, and optimizing the dataset for database loading.
3. Database Loading
Loads the raw and processed data into a PostgreSQL database (hosted by Supabase) for efficient querying and analytics. Also refreshes the materialized views to ensure up-to-date insights.

### Analysis and Visualization
Once loaded, the data is used to generate insights and interactive visualizations on:

- The distribution and characteristics of Airbnb listings in Boston.
- Host performance and review trends over time.
- Neighborhood popularity and room type distribution.
- Amenities offered and availability trends across listings.

### Technology Stack
Python - Data scraping, cleaning, and analysis

PostgreSQL - Database management, hosted in Supabase

Docker - Containerization for the ETL pipeline, Automated using GitHub Actions

Streamlit - Interactive web interface, hosted on Streamlit Cloud

### Instructions to run the code Locally:
- Switch to Branch feature-local_run and clone the repository/download the code
- Install Docker Desktop (https://www.docker.com/products/docker-desktop/)
- (Optional) Install Python (https://www.python.org/downloads/release/python-31011/). Only if you want to run the scripts outside Docker.
- Create a `.env` file with the required credentials to connect to the database. The `.env` file must have the Username, Password and Database Name. Example of the `.env` file:
```
user=exampleairbnbuser
password=examplepassword123
db_name=airbnbdatabase
```
- Open Command Prompt or Terminal (Or a prefered code editor)
- In the terminal run the following command: `docker-compose up -d --build`. This will build the docker images and start the containers. `-d` makes it run in detached mode. If you want to have the logs stream to your terminal run: `docker-compose up --build` instead.
- Open http://localhost:8501 in your browser to view the streamlit app.
- To close the containers run: `docker-compose down`. If you want to also remove the volumes (resets the database) run: `docker-compose down -v`. 
- For subsequent runs you can just run: `docker-compose up` to not have to rebuild the images each time if you haven't changed anything.


### Source for the Dataset
https://insideairbnb.com


### Code Author
Santosh Saranyan

https://www.linkedin.com/in/santosh-saranyan/

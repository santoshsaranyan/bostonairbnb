import streamlit as st
import utilities.streamlithtml as htmllib
import os
import pandas as pd
import pydeck as pdk
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

user = os.getenv('user')
password = os.getenv('password')
db_name = os.getenv('db_name')

with st.sidebar:
    st.image("https://t3.ftcdn.net/jpg/05/89/24/50/360_F_589245011_2eyvpGgTRGZT3Hw4ScUj9QPwvOLp3XsQ.jpg", width=150)
    st.divider()
    st.sidebar.title("About")
    st.markdown("""
    The data is used to generate insights and interactive visualizations on:
    - Listing prices and availability across neighborhoods  
    - Host activity and response behavior  
    - Seasonal and spatial trends within the Boston short-term rental market
    """)

st.markdown(htmllib.html_2, unsafe_allow_html=True)
    
st.title("📊 Analytics and Visualization") 

st.info("⚠️ Work in Progress...")

st.info("💡 *Run the Date Pipeline First* ")

tab1, tab2, tab3 = st.tabs(["Overview", "Visualizations", "Insights"])
with tab1:
    # Load listings
    engine = create_engine(f"postgresql+psycopg2://{user}:{password}@postgres:5432/{db_name}")

    listings = pd.read_sql("SELECT * FROM gold.vw_listing_overview", con=engine)

    # Filter by nieghborhood
    location_options = listings['Neighborhood'].unique()
    selected_locations = st.multiselect("Filter by Neighborhood", location_options)
    if not selected_locations:
        selected_locations = location_options

    filtered_listings = listings[listings['Neighborhood'].isin(selected_locations)].reset_index(drop=True)
    filtered_listings_map = filtered_listings[['Listing Name', 'Neighborhood', 'latitude', 'longitude', 'Room Type', 'Reviews', 'Rating', 'Description']]
    filtered_listings_map = filtered_listings_map.dropna(subset=['latitude', 'longitude'])
    
    filtered_listings_table = filtered_listings[['Picture', 'Listing Name', 'Description', 'Host Name', 'Neighborhood', 'Neighborhood Overview','Room Type','Amenities', 'Reviews', 'Rating']]
    
    tab11, tab12 = st.tabs(["Map View", "Table View"])
    with tab11:
        st.subheader("Map View of Listings")
        st.markdown("This map visualizes Airbnb listings in Boston. Hover over the points to see details about each listing.")
        
        # Truncate text for display
        def truncate(text, length=80):
            if pd.isna(text):
                return "N/A"
            return (text[:length] + "...") if len(text) > length else text

        filtered_listings_map["tooltip_description"] = filtered_listings_map["Description"].apply(truncate)
        
        filtered_listings_map.rename(columns={"Listing Name":'name',"Room Type": "room_type", "Neighborhood":'neighborhood', "Reviews":'reviews', "Rating":'rating'}, inplace=True)

        # Scatterplot layer to visualize listings
        scatter_layer = pdk.Layer(
            "ScatterplotLayer",
            data=filtered_listings_map,
            get_position='[longitude, latitude]',
            get_fill_color='[255, 140, 0, 200]',    
            get_radius=40,              
            radius_min_pixels=2,
            radius_max_pixels=15,
            pickable=True,
            auto_highlight=True,
            highlight_color=[180, 90, 0, 255]       
        )
        
        st.markdown(htmllib.html_3, unsafe_allow_html=True)

        
        # Tooltip that shows listing details on hover
        tooltip = {
            "html": """
            <div class="deck-tooltip">
                <b>{name}</b><br/>
                <b>Neighborhood:</b> {neighborhood}<br/>
                <b>Description:</b> {tooltip_description}<br/>
                <b>Room:</b> {room_type}<br/>
                <b>Reviews:</b> {reviews} reviews | <b>Rating:</b> {rating}
            </div>
            """,
            "style": {"fontSize": "12px", "color": "black"}  # optional
        }

        # Map view state
        view_state = pdk.ViewState(
            latitude=filtered_listings_map['latitude'].mean(),
            longitude=filtered_listings_map['longitude'].mean(),
            zoom=12
        )

        # Map
        r = pdk.Deck(
            layers=[scatter_layer],
            initial_view_state=view_state,
            map_style=None,  
            tooltip=tooltip
        )

        st.pydeck_chart(r)
        
    with tab12:
        st.subheader("Table View of Listings")
        st.markdown("This table provides detailed information about Airbnb listings in Boston.")
        st.dataframe(
            filtered_listings_table,
            width='content',
            column_config={
                "Picture": st.column_config.ImageColumn(
                    "Picture", width=50
                )
            }
        )

    


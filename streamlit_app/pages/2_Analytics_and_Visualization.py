import streamlit as st
import os
import pandas as pd
import pydeck as pdk
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import altair as alt

load_dotenv()

# Get database credentials from environment variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

# Check if the environment variables are set
if not USER or not PASSWORD or not DBNAME or not HOST or not PORT:
    raise ValueError("Database credentials are not set in the .env file.")

engine = create_engine(f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require")

with st.sidebar:
    st.image("https://t3.ftcdn.net/jpg/05/89/24/50/360_F_589245011_2eyvpGgTRGZT3Hw4ScUj9QPwvOLp3XsQ.jpg", width=150)
    st.divider()
    st.sidebar.title("About")
    st.markdown("""
    The data is used to generate insights and interactive visualizations on:
    - The distribution and characteristics of Airbnb listings in Boston.
    - Host performance and review trends over time.
    - Neighborhood popularity and room type distribution.
    - Amenities offered and availability trends across listings.
    """)
    st.divider()
    st.caption("Data Source: [InsideAirbnb](https://insideairbnb.com)")
    st.caption("Developed by: [Santosh Saranyan](https://www.linkedin.com/in/santosh-saranyan/)")
    st.caption("App Last updated: October 2025")

    
@st.cache_data(ttl=600)
def load_data(view_name):
    with engine.connect() as conn:
        return pd.read_sql(text(f"SELECT * FROM gold.{view_name}"), conn)

    
st.title("📊 Analytics and Visualization")
st.markdown("Explore insights from the Boston Airbnb data")

tab1, tab2, tab3, tab4 = st.tabs(["Listing Overview", "Hosts and Reviews", "Neighborhood Insights", "Amenities and Availability"])
with tab1:

    listings = load_data("mv_listing_overview")

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
        
        def truncate(text, length=80):
            if pd.isna(text):
                return "N/A"
            return (text[:length] + "...") if len(text) > length else text

        filtered_listings_map["tooltip_description"] = filtered_listings_map["Description"].apply(truncate)
        
        filtered_listings_map.rename(columns={"Listing Name":'name',"Room Type": "room_type", "Neighborhood":'neighborhood', "Reviews":'reviews', "Rating":'rating'}, inplace=True)

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
        
        st.markdown("""
        <style>
        .deck-tooltip {
            max-width: 300px !important;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
            font-size: 13px !important;
            line-height: 1.5 !important;
            background: white !important;
            color: black !important;
            border-radius: 8px !important;
        }

        .deck-tooltip b {
            font-size: 14px;
        }
        </style>
        """, unsafe_allow_html=True)


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

        view_state = pdk.ViewState(
            latitude=filtered_listings_map['latitude'].mean(),
            longitude=filtered_listings_map['longitude'].mean(),
            zoom=12
        )

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
        
with tab2:
    st.subheader("Hosts and Reviews")
    hosts = load_data("mv_host_summary")
    reviews = load_data("mv_review_activity")
    
    tab21, tab22 = st.tabs(["Hosts Overview", "Reviews Over Time"])
    with tab21:
        st.markdown("This section provides insights into Airbnb hosts in Boston, including their ratings, number of listings, and review counts.")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Hosts", len(hosts))
        with col2:
            st.metric("Average Host Rating", round(hosts["Overall Rating"].mean(), 2))
        with col3:
            superhost_ratio = hosts["Superhost Status"].mean() * 100
            st.metric("Superhost %", f"{superhost_ratio:.1f}%")

        hosts['Host Display'] = hosts['Host Name'] + " (" + hosts['Host ID'].astype(str) + ")"
        top_hosts = hosts.nlargest(15, 'Number of Reviews')
        bar = alt.Chart(top_hosts).mark_bar().encode(
            x=alt.X('Number of Reviews:Q'),
            y=alt.Y('Host Display:N', sort='-x', title='Host'),
            color=alt.Color('Overall Rating:Q', scale=alt.Scale(scheme='greens')),
            tooltip=['Host Name', 'Host ID', 'Number of Reviews', 'Overall Rating', 'Host Listings Count']
        ).properties(title="Top 15 Hosts by Total Reviews")
        st.altair_chart(bar, use_container_width=True)
        
        hosts = hosts.sort_values(by=["Number of Reviews","Overall Rating"], ascending=False).reset_index(drop=True)
        st.subheader("Hosts Data Table")
        st.dataframe(hosts)
        
    with tab22:
        st.markdown("This section visualizes review trends over time, highlighting the most reviewed neighborhoods and hosts.")

        st.subheader("Review Trends Over Time")
        line_chart = alt.Chart(reviews).encode(
            x="Review Month:T",
            y="Reviews:Q",
            tooltip=["Most Reviewed Neighborhood", "Most Reviewed Host"]
        )

        line = line_chart.mark_line(color='lightblue', strokeWidth=3)
        points = line_chart.mark_point(color='darkblue', filled=True, size=40)

        st.altair_chart(line + points, use_container_width=True)
        
with tab3:
    neigh = load_data("mv_neighborhood_summary")
    neigh["Reviews per Listing"] = neigh["Total Reviews"] / neigh["Total Listings"]
    st.subheader("Neighborhood Insights")
    total_listings = neigh["Total Listings"].sum()
    total_reviews = neigh["Total Reviews"].sum()
    avg_rating = round(neigh["Average Overall Rating"].mean(), 2)
    avg_accommodates = round(neigh["Average Accommodates"].mean(), 1)

    tab31, tab32, tab33 = st.tabs(["Neighborhood Overview", "Neighborhood Popularity", "Room Type Distribution"])

    with tab31:
        st.markdown("This section provides an overview of Airbnb listings across different neighborhoods in Boston, including key metrics and visualizations.")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Listings", f"{total_listings:,}")
        col2.metric("Total Reviews", f"{total_reviews:,}")
        col3.metric("Average Rating", avg_rating)
        col4.metric("Avg Accommodates", avg_accommodates)
        
        st.subheader("Neighborhood Data Table")
        st.dataframe(neigh.reset_index(drop=True))
        
    with tab32:
        st.markdown("This section analyzes neighborhood popularity based on reviews per listing and highlights the top neighborhoods.")
        scatter_ratio = alt.Chart(neigh).mark_circle(size=150).encode(
            x=alt.X("Total Listings:Q", title="Total Listings"),
            y=alt.Y("Reviews per Listing:Q", title="Reviews per Listing"),
            color=alt.Color("Average Overall Rating:Q", scale=alt.Scale(scheme="greens"), title="Avg Rating"),
            tooltip=["Neighborhood", "Total Listings", "Total Reviews", "Reviews per Listing", "Average Overall Rating"]
        ).properties(
            title="Neighborhood Popularity: Reviews per Listing vs Total Listings",
            width=700,
            height=500
        ).interactive()
        st.altair_chart(scatter_ratio, use_container_width=True)
        
        neigh_sorted = neigh.sort_values(by="Reviews per Listing", ascending=False).head(15)
        bar_rank = alt.Chart(neigh_sorted).mark_bar().encode(
            x=alt.X("Reviews per Listing:Q", title="Reviews per Listing"),
            y=alt.Y("Neighborhood:N", sort='-x', title="Neighborhood"),
            color=alt.Color("Average Overall Rating:Q", scale=alt.Scale(scheme="greens"), title="Avg Rating"),
            tooltip=["Neighborhood", "Total Listings", "Total Reviews", "Reviews per Listing", "Average Overall Rating"]
        ).properties(
            title="Top 15 Neighborhoods by Reviews per Listing",
            width=700,
            height=500
        )
        st.altair_chart(bar_rank, use_container_width=True)

    with tab33:
        st.markdown("This section visualizes the distribution of room types across different neighborhoods in Boston.")
        room_type_dist = alt.Chart(neigh).mark_bar().encode(
            x=alt.X("Neighborhood:N", title="Neighborhood"),
            y=alt.Y("Total Listings:Q", title="Number of Listings"),
            color=alt.Color("Most Common Room Type:N", legend=alt.Legend(title="Room Type")),
            tooltip=["Neighborhood", "Most Common Room Type", "Total Listings"]
        ).properties(
            title="Room Type Distribution by Neighborhood",
            width=700,
            height=400
        )
        st.altair_chart(room_type_dist, use_container_width=True)
        
        
with tab4:
    st.subheader("Amenities & Availability")
    
    st.markdown("This section explores the popularity and ratings of amenities offered in Airbnb listings, as well as availability trends across neighborhoods in Boston.")

    amenities = load_data("mv_amenity_summary")
    avail = load_data("mv_availability_summary")
    trend = load_data("mv_availability_trend")

    tab41, tab42 = st.tabs(["Availability Trends","Amenities Overview"])
    
    with tab41:
        st.markdown("This section analyzes the availability of Airbnb listings across different neighborhoods in Boston, highlighting trends and patterns over time.")
        neighborhoods = trend["Neighborhood"].unique().tolist()
        selected_neigh = st.multiselect("Select Neighborhood(s)", neighborhoods, default=neighborhoods)
        filtered_trend = trend[trend["Neighborhood"].isin(selected_neigh)]

        line = alt.Chart(filtered_trend).mark_line(point=True).encode(
            x="Month:T",
            y="Avg Availability Rate:Q",
            color="Neighborhood:N",
            tooltip=["Neighborhood", "Avg Availability Rate"]
        ).properties(
            title="Monthly Average Availability Rate by Neighborhood",
            width=700,
            height=400
        )
        st.altair_chart(line, use_container_width=True)
        
        st.subheader("Availability Summary Table")
        st.dataframe(avail[["Listing Name", "Neighborhood", "Availability Rate", "Available Days", "Unavailable Days"]])

    with tab42:
        st.markdown("This section provides insights into the amenities offered in Airbnb listings, including their popularity and average ratings.")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Amenities", len(amenities))
        col2.metric("Avg Listings per Amenity", round(amenities["Listings Count"].mean(), 1))
        col3.metric("Avg Rating Across Amenities", round(amenities["Average Rating for Listings"].mean(), 2))
        
        top_amenities = amenities.nlargest(15, "Percent of Total Listings")

        bar = alt.Chart(top_amenities).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
            x="Percent of Total Listings:Q",
            y=alt.Y("Amenity:N", sort="-x"),
            color=alt.Color("Percent of Total Listings:Q", scale=alt.Scale(scheme='greens'), legend=alt.Legend(title="Percent of Listings")),
            tooltip=["Amenity", "Listings Count", "Average Rating for Listings", "Percent of Total Listings"]
        ).properties(
            title="Top 15 Amenities by Percent of Listings",
            width=700,
            height=400
        )

        st.altair_chart(bar, use_container_width=True)

    
    
    
    


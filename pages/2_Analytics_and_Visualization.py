import streamlit as st
import utilities.streamlithtml as htmllib
import os
import pandas as pd
import pydeck as pdk
import json


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

st.write("Work in Progress...")

tab1, tab2, tab3 = st.tabs(["Overview", "Visualizations", "Insights"])
with tab1:
    # Load listings
    listings = pd.read_csv("data/cleaned/cleaned_listings.csv")

    # Filter by location_id
    location_options = listings['location_id'].unique()
    selected_locations = st.multiselect("Filter by location_id:", location_options)
    if not selected_locations:
        selected_locations = location_options

    filtered_listings = listings[listings['location_id'].isin(selected_locations)].reset_index(drop=True)

    # Truncate text for display
    def truncate(text, length=80):
        if pd.isna(text):
            return "N/A"
        return (text[:length] + "...") if len(text) > length else text

    filtered_listings["tooltip_description"] = filtered_listings["description"].apply(truncate)
    filtered_listings["tooltip_neighborhood"] = filtered_listings["neighborhood_overview"].apply(truncate)

    # Scatterplot layer to visualize listings
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=filtered_listings,
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


    # Tooltip that shows listing details on hover
    tooltip = {
        "html": """
        <div class="deck-tooltip">
            <b>{name}</b><br/>
            <b>Neighborhood:</b> {tooltip_neighborhood}<br/>
            <b>Description:</b> {tooltip_description}<br/>
            <b>Room:</b> {room_type}<br/>
            <b>Reviews:</b> {number_of_reviews} reviews | <b>Rating:</b> {overall_rating}
        </div>
        """,
        "style": {"fontSize": "12px", "color": "black"}  # optional
    }

    # Map view state
    view_state = pdk.ViewState(
        latitude=filtered_listings['latitude'].mean(),
        longitude=filtered_listings['longitude'].mean(),
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


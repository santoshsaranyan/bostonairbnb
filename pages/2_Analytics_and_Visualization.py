import streamlit as st
import utilities.streamlithtml as htmllib
import os


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
    
st.title("📊 Analysis and Visualization") 

st.markdown("<div class='pipeline-sub'><b>Work in Progress</b></div>", unsafe_allow_html=True)

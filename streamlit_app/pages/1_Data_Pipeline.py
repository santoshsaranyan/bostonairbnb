import streamlit as st
import utilities.streamlithtml as htmllib
from utilities.db_utils import check_table_exists, check_table_has_data

# Sidebar
with st.sidebar:
    st.image(
        "https://t3.ftcdn.net/jpg/05/89/24/50/360_F_589245011_2eyvpGgTRGZT3Hw4ScUj9QPwvOLp3XsQ.jpg",
        width=150,
    )
    st.divider()
    st.sidebar.title("About")
    st.markdown("""
    This page verifies that all tables and materialized views for the pipeline
    exist in the PostgreSQL database and contain data.
    """)

# Initialize session state for each step
for step in ["step1_done", "step2_done", "step3_done"]:
    if step not in st.session_state:
        st.session_state[step] = False

# Render HTML header
st.markdown(htmllib.html_2, unsafe_allow_html=True)

# Header
st.title("🧱 Data Pipeline Verification")
st.markdown("Verify that the pipeline tables/views exist and contain data.")

# Function to check tables/views for a given step
def check_step(items, schema, step_key):
    all_ok = True
    for item in items:
        exists = check_table_exists(item, schema)
        has_data = check_table_has_data(item, schema) if exists else False
        if exists and has_data:
            st.success(f"✅ {schema.capitalize()} '{item}' exists and contains data")
        elif exists:
            st.warning(f"⚠️ {schema.capitalize()} '{item}' exists but is empty")
            all_ok = False
        else:
            st.error(f"❌ {schema.capitalize()} '{item}' does not exist")
            all_ok = False
    st.session_state[step_key] = all_ok

# Step 1: Bronze Tables
with st.expander("Step 1: Bronze Tables", expanded=True):
    bronze_tables = ["bnb_raw_listings", "bnb_raw_reviews", "bnb_raw_availability"] 
    if st.session_state.step1_done:
        check_step(bronze_tables, "bronze", "step1_done")
    if st.button("Check Bronze Tables", key="step1_btn"):
        check_step(bronze_tables, "bronze", "step1_done")
        st.rerun()

# Step 2: Silver Tables / Views
with st.expander("Step 2: Silver Tables", expanded=True):
    silver_tables = ["bnb_dim_listings", "bnb_dim_hosts", "bnb_fact_reviews","bnb_fact_availability","bnb_dim_locations","bnb_dim_amenities","bnb_br_listing_amenities"]  
    if st.session_state.step2_done:
        check_step(silver_tables, "silver", "step2_done")
    if st.button("Check Silver Tables/Views", key="step2_btn"):
        check_step(silver_tables, "silver", "step2_done")
        st.rerun()

# Step 3: Gold Materialized Views
with st.expander("Step 3: Gold Materialized Views", expanded=True):
    gold_views = ["mv_listing_overview", "mv_host_summary", "mv_review_activity","mv_neighborhood_summary","mv_amenity_summary","mv_availability_summary","mv_availability_trend"] 
    if st.session_state.step3_done:
        check_step(gold_views, "gold", "step3_done")
    if st.button("Check Gold Materialized Views", key="step3_btn"):
        check_step(gold_views, "gold", "step3_done")
        st.rerun()

# Progress Bar
completed = sum([
    st.session_state.step1_done,
    st.session_state.step2_done,
    st.session_state.step3_done
])
progress_pct = int((completed / 3) * 100)
st.markdown(
    f"<div class='progress-container'><div class='progress-bar' style='width:{progress_pct}%;'></div></div>",
    unsafe_allow_html=True,
)

# Render HTML footer
st.markdown(htmllib.html_1, unsafe_allow_html=True)

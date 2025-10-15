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

# Step 1: Bronze Tables
with st.expander("Step 1: Bronze Tables", expanded=True):
    bronze_tables = ["listings", "reviews"]  # Replace with actual bronze table names
    all_ok = True
    for table in bronze_tables:
        exists = check_table_exists(table, "bronze")
        has_data = check_table_has_data(table, "bronze") if exists else False
        if exists and has_data:
            st.success(f"✅ Bronze table '{table}' exists and contains data")
        elif exists:
            st.warning(f"⚠️ Bronze table '{table}' exists but is empty")
            all_ok = False
        else:
            st.error(f"❌ Bronze table '{table}' does not exist")
            all_ok = False
    st.session_state.step1_done = all_ok

# Step 2: Silver Tables / Views
with st.expander("Step 2: Silver Tables", expanded=True):
    silver_tables = ["listings_summary", "reviews_summary"]  # Replace with actual silver tables/views
    all_ok = True
    for table in silver_tables:
        exists = check_table_exists(table, "silver")
        has_data = check_table_has_data(table, "silver") if exists else False
        if exists and has_data:
            st.success(f"✅ Silver table/view '{table}' exists and contains data")
        elif exists:
            st.warning(f"⚠️ Silver table/view '{table}' exists but is empty")
            all_ok = False
        else:
            st.error(f"❌ Silver table/view '{table}' does not exist")
            all_ok = False
    st.session_state.step2_done = all_ok

# Step 3: Gold Materialized Views
with st.expander("Step 3: Gold Materialized Views", expanded=True):
    gold_views = ["mv_listing_overview", "mv_neighborhood_summary"]  # Replace with actual gold views
    all_ok = True
    for view in gold_views:
        exists = check_table_exists(view, "gold")
        has_data = check_table_has_data(view, "gold") if exists else False
        if exists and has_data:
            st.success(f"✅ Gold materialized view '{view}' exists and contains data")
        elif exists:
            st.warning(f"⚠️ Gold materialized view '{view}' exists but is empty")
            all_ok = False
        else:
            st.error(f"❌ Gold materialized view '{view}' does not exist")
            all_ok = False
    st.session_state.step3_done = all_ok

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

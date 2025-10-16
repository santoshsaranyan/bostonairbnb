import os
import streamlit as st
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import time

load_dotenv()
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

if not USER or not PASSWORD or not DBNAME or not HOST or not PORT:
    raise ValueError("Database credentials are not set in the .env file.")

engine = create_engine(f'postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require')

def check_table_exists(name: str, schema: str) -> bool:
    query = text("""
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables WHERE table_schema = :schema AND table_name = :name
    ) OR EXISTS (
        SELECT 1 FROM information_schema.views WHERE table_schema = :schema AND table_name = :name
    ) OR EXISTS (
        SELECT 1 FROM pg_matviews WHERE schemaname = :schema AND matviewname = :name
    )
    """)

    with engine.connect() as conn:
        return bool(conn.execute(query, {"schema": schema, "name": name}).scalar())

def check_table_has_data(name: str, schema: str) -> bool:
    query = text(f"SELECT 1 FROM {schema}.{name} LIMIT 1")
    with engine.connect() as conn:
        return conn.execute(query).first() is not None

for step in ["bronze", "silver", "gold"]:
    if f"{step}_results" not in st.session_state:
        st.session_state[f"{step}_results"] = []

with st.sidebar:
    st.image(
        "https://t3.ftcdn.net/jpg/05/89/24/50/360_F_589245011_2eyvpGgTRGZT3Hw4ScUj9QPwvOLp3XsQ.jpg",
        width=150,
    )
    st.divider()
    st.title("About")
    st.markdown("""
        This page verifies that all tables and materialized views for the pipeline
        exist in the PostgreSQL database and contain data.
    """)
    st.divider()
    st.caption("Data Source: [InsideAirbnb](https://insideairbnb.com)")
    st.caption("Developed by: [Santosh Saranyan](https://www.linkedin.com/in/santosh-saranyan/)")
    st.caption("App Last updated: October 2025")

st.title("🧱 Data Pipeline Verification")
st.markdown("Verify that the pipeline tables/views exist and contain data.")

bronze_tables = ["bnb_raw_listings", "bnb_raw_reviews", "bnb_raw_availability"]
silver_tables = [
    "bnb_dim_listings", "bnb_dim_hosts", "bnb_fact_reviews",
    "bnb_fact_availability", "bnb_dim_locations","bnb_dim_amenities",
    "bnb_br_listing_amenities"
]
gold_views = [
    "mv_listing_overview","mv_host_summary","mv_review_activity",
    "mv_neighborhood_summary","mv_amenity_summary","mv_availability_summary",
    "mv_availability_trend"
]

def render_step(name, items):
    exp = st.expander(f"{name.capitalize()} Check", expanded=True)
    with exp:
        progress_bar = st.progress(0)

        if st.button(f"Check {name.capitalize()}", key=f"btn_{name}"):
            results = []
            total = len(items)
            for i, item in enumerate(items):
                exists = check_table_exists(item, name)
                has_data = check_table_has_data(item, name) if exists else False

                if exists and has_data:
                    results.append(("success", f"{name.capitalize()} '{item}' exists and contains data"))
                elif exists:
                    results.append(("warning", f"{name.capitalize()} '{item}' exists but is empty"))
                else:
                    results.append(("error", f"{name.capitalize()} '{item}' does not exist"))

                
                progress_bar.progress((i + 1) / total)
                time.sleep(0.05)

            st.session_state[f"{name}_results"] = results

        for status, msg in st.session_state[f"{name}_results"]:
            if status == "success": st.success(f"✅ {msg}")
            elif status == "warning": st.warning(f"⚠️ {msg}")
            else: st.error(f"❌ {msg}")

render_step("bronze", bronze_tables)
render_step("silver", silver_tables)
render_step("gold", gold_views)

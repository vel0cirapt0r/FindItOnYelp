import streamlit as st
import httpx
import pandas as pd

API_BASE_URL = "http://localhost:8000/api"

def search_businesses(term, location, sort_by, limit, max_results):
    """Fetch businesses from the FastAPI backend using httpx."""
    params = {
        "term": term,
        "location": location,
        "sort_by": sort_by,
        "limit": limit,
        "max_results": max_results
    }
    try:
        with httpx.Client() as client:
            response = client.get(f"{API_BASE_URL}/search", params=params)
            response.raise_for_status()
            return response.json()["businesses"]
    except httpx.HTTPStatusError as e:
        st.error(f"API error: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        st.error(f"Request error: {e}")
    return []

def export_to_csv(term, location, sort_by, max_results):
    """Trigger CSV export from the backend using httpx."""
    params = {
        "term": term,
        "location": location,
        "sort_by": sort_by,
        "max_results": max_results
    }
    try:
        with httpx.Client() as client:
            response = client.get(f"{API_BASE_URL}/export", params=params)
            response.raise_for_status()
            return response.json()["file"]
    except httpx.HTTPStatusError as e:
        st.error(f"API error: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        st.error(f"Request error: {e}")
    return None

st.title("FindItOnYelp")

term = st.text_input("Search Term", "pizza")
location = st.text_input("Location", "New York")
sort_by = st.selectbox("Sort By", ["best_match", "rating", "review_count", "distance"])
limit = st.slider("Limit", 1, 50, 10)
max_results = st.slider("Max Results", 1, 1000, 50)

if st.button("Search"):
    businesses = search_businesses(term, location, sort_by, limit, max_results)
    if businesses:
        df = pd.DataFrame(businesses)
        st.dataframe(df)
    else:
        st.warning("No results found.")

if st.button("Export to CSV"):
    file_path = export_to_csv(term, location, sort_by, max_results)
    if file_path:
        st.success(f"CSV exported successfully: {file_path}")

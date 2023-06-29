import pandas as pd
import streamlit as st
from utils import database

st.title('Fetch Transcripts')

@st.cache_data
def get_metadata():
    metadata = database.fetch_metadata_from_db()
    return metadata

metadata = get_metadata()

# select the unique companies for user to filter
company_name = st.selectbox(label='Company', options=list(
    metadata['name'].sort_values().unique()))

year = st.selectbox(label='Year', options=list(
    metadata[metadata['name']==company_name]['year'].sort_values().unique()))

quarter = st.selectbox(label='Quarter', options=list(
    metadata[(metadata['name']==company_name) & (metadata['year']==year)]['quarter'].sort_values().unique()))

# quarter = st.selectbox(label='Quarter', options=[1,2,3,4])

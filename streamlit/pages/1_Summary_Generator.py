import pandas as pd
import streamlit as st
from utils import database, summarization, generic

st.title('Generate Summary')

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

month = st.selectbox(label='Month', options=list(
    metadata[(metadata['name']==company_name) & (metadata['year']==year)]['month'].sort_values().unique()))
file_urls = list(
    metadata[(metadata['name']==company_name) & (metadata['year']==year) & (metadata['month']==month)]['gurl'].sort_values().unique())

file_names = [generic.get_filename_from_gurl(file) for file in file_urls if '.txt' in file]

file_name = st.selectbox(label='File', options=file_names)

openai_api_key = st.text_input('OpenAI API Key', type='password')
metrics = st.checkbox("Display answer metrics")

if st.button("Generate Summary"):
    if not openai_api_key or not file_name or not year or not month or not company_name:
        st.write("Please fill out all the above details")
    # summary = summarization.summarize_docs(openai_api_key, file_name)
    with st.spinner(text="In progress..."):
        summary = summarization.summarize_docs(openai_api_key, file_name)
    if metrics:
        st.write(summary)
    else:
        st.write(summary["choices"][0]["text"])

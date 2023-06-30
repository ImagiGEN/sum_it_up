import pandas as pd
import streamlit as st
from utils import database, generic, pinecone_utils

st.title('Pinecone Answers')

@st.cache_data
def get_metadata():
    metadata = database.fetch_metadata_from_db()
    return metadata

if 'context' not in st.session_state:
	st.session_state.context = False


st.session_state.answer = None

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

if st.button("Upload file"):
    st.session_state.context = False
    with st.spinner(text="Setting context..."):
        pinecone_utils.store_embeddings_pinecone(file_name, openai_api_key)
    st.session_state.context = True

if st.session_state.context:
    question = st.text_input('Ask questions here')
    metrics = st.checkbox("Display answer metrics")
    
    if st.button("Send"):
        with st.spinner(text="Responding..."):
            st.session_state.answer = pinecone_utils.get_answer(question, openai_api_key)

if st.session_state.answer:    
    if metrics:
        st.write(st.session_state.answer)
    else:
        st.write(st.session_state.answer[0]["answer"])

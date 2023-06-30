import openai
from utils import generic
import os
import pinecone
import os, tempfile
import streamlit as st, pinecone
from langchain.llms.openai import OpenAI
from langchain.vectorstores.pinecone import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains.summarize import load_summarize_chain
from langchain.document_loaders import TextLoader

index_name = "extractive-question-answering"
environment = os.environ.get("PINECONE_ENV", "asia-southeast1-gcp-free")
pinecone_api_key = os.environ.get("PINECONE_API_KEY")
openai_model_name = 'text-embedding-ada-002'

def create_index():
    # check if the extractive-question-answering index exists
    if index_name not in pinecone.list_indexes():
        # create the index if it does not exist
        pinecone.create_index(
            index_name,
            dimension=1536,
            metric="cosine"
        )

def init_pinecone():
    # connect to pinecone environment
    pinecone.init(
        api_key=pinecone_api_key,
        environment=environment
    )
    create_index()

def set_openai_key(openai_api_key):
    openai.api_key = openai_api_key

def get_index():
    # connect to extractive-question-answering index we created
    index = pinecone.Index(index_name)
    return index

def summarize_docs(openaikey, file_name):
    openai.api_key = openaikey
    fetched_file = generic.fetch_file_from_gcs(file_name).decode()
    promptstr="Summarize the document:" + fetched_file
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=promptstr,
        temperature=0,
        max_tokens=64,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
        )
    return response

def generate_summary(openai_api_key, file_name):
    try:
        # Save uploaded file temporarily to disk, load and split the file into pages, delete temp file
        words = generic.fetch_file_from_gcs(file_name)
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(words)

        loader = TextLoader(tmp_file.name)
        pages = loader.load_and_split()
        os.remove(tmp_file.name)
        
        init_pinecone()
        # Create embeddings for the pages and insert into Pinecone vector database
        embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        vectordb = Pinecone.from_documents(pages, embeddings, index_name=index_name)

        # Initialize the OpenAI module, load and run the summarize chain
        llm = OpenAI(temperature=0, openai_api_key=openai_api_key)
        chain = load_summarize_chain(llm, chain_type="stuff")
        search = vectordb.similarity_search(" ")
        summary = chain.run(input_documents=search, question="Write a concise summary within 200 words.")
        return summary
    except Exception as e:
        return f"An error occurred: {e}"
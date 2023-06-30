import openai
from utils import generic
import os
import pinecone
import os, tempfile
from langchain.llms.openai import OpenAI
from langchain.vectorstores.pinecone import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
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

def get_answer(file_name, openai_api_key, question):
    set_openai_key(openai_api_key)
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

        retriever = vectordb.as_retriever()
        # Initialize the OpenAI module, load and run the summarize chain
        llm = OpenAI(temperature=0, openai_api_key=openai_api_key)
        qa = RetrievalQA.from_chain_type(llm, chain_type="stuff", retriever=retriever)
        response = qa.run(question)
        return response
    except Exception as e:
        return f"An error occurred: {e}"

from tqdm import tqdm
import pinecone
from sentence_transformers import SentenceTransformer
from utils import generic
from transformers import pipeline
from pprint import pprint
import os
import openai
from dotenv import load_dotenv

load_dotenv()

model_name = "deepset/electra-base-squad2"

index_name = "extractive-question-answering"
openai_model = "text-embedding-ada-002"
environment = os.environ.get("PINECONE_ENV", "asia-southeast1-gcp-free")
pinecone_api_key = os.environ.get("PINECONE_API_KEY")

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

# gets context passages from the pinecone index
def get_context(question, top_k):
    index = get_index()
    # generate embeddings for the question
    xq = openai.Embedding.create(
        input=question, 
        engine=openai_model)['data'][0]['embedding']
    # search pinecone index for context passage with the answer
    xc = index.query(xq, top_k=top_k, include_metadata=True)
    c = [x["metadata"]["text"] for x in xc["matches"]]
    return c


# extracts answer from the context passage
def extract_answer(question, context):
    # load the reader model into a question-answering pipeline
    reader = pipeline(tokenizer=model_name, model=model_name, task="question-answering")
    results = []
    for c in context:
        # feed the reader the question and contexts to extract answers
        answer = reader(question=question, context=c)
        # add the context to answer dict for printing both together
        answer["text"] = c
        results.append(answer)
    # sort the result based on the score from reader model
    sorted_result = sorted(results, key=lambda x: x["score"], reverse=True)
    return sorted_result

def get_answer(question, openai_api_key, top_n = 1):
    init_pinecone()
    set_openai_key(openai_api_key)
    context = get_context(question, top_n)
    return extract_answer(question, context)


def store_embeddings_pinecone(file_name, openai_api_key):
    set_openai_key(openai_api_key)
    words = generic.fetch_file_from_gcs(file_name).decode()
    chunks = []
    current_chunk = []

    company = (file_name.split('/')[0]).split('_')[1]
    year = (file_name.split('/')[0]).split('_')[0][:4]
    
    for word in words:
        current_chunk.append(word)
        if len(current_chunk) >= 500:
            chunks.append(''.join(current_chunk))
            current_chunk = []
    if current_chunk:
        chunks.append(''.join(current_chunk))
    batch_size = 128

    for i in tqdm(range(0, len(chunks), batch_size)):
        # Find end of batch
        i_end = min(i + batch_size, len(chunks))
        # Create IDs batch
        ids = [f"{company}-{year}-chunk-{j}" for j in range(i, i_end)]
                
        # Compute OpenAI embeddings for chunk
        response = openai.Embedding.create(
                    input=chunks[i:i_end],
                    model=openai_model
                )
        embeds = [record['embedding'] for record in response['data']]
        meta = [{'text': line} for line in chunks[i:i_end]]

        # Create records list for upsert
        records = zip(ids, embeds, meta)
        # Upsert to Pinecone
        try:
            init_pinecone()
            index = get_index()
            index.upsert(vectors=records)
            print(f"Upserted batch {i} to {i_end} successfully")
        except Exception as e:
            print(f"Error while upserting batch {i} to {i_end}: {e}")
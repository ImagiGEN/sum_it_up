import openai
from utils import generic


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

import os
import google.cloud.storage as gcs
from dotenv import load_dotenv

load_dotenv()

gcs_bucket_name = os.environ.get('GCS_BUCKET_NAME', 'damg7245-summer23-team2')
gcs_project_id = os.environ.get('GCS_PROJECT_ID', 'damg7245-assignment2')


storage_client = gcs.Client(project=gcs_project_id)
bucket = storage_client.bucket(gcs_bucket_name)

def fetch_file_from_gcs(file_name):

    # Specify the file path in the bucket
    blob = bucket.blob(file_name)

    # Download the file contents
    file_contents = blob.download_as_text()

    # Process the file contents as needed
    # print(f"Contents of '{file_name}':")
    # print(file_contents.encode('utf-8'))
    return file_contents.encode('utf-8')

def get_filename_from_gurl(gurl):
    return "/".join(gurl.split("/")[-2:])

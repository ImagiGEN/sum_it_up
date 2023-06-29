import os
import google.cloud.storage as gcs
from airflow import DAG
import requests
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
from airflow.utils.dates import days_ago
from datetime import timedelta
from airflow.models.baseoperator import chain
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, Date, insert, text
from google.cloud.sql.connector import Connector
import pg8000
import pandas as pd
from dotenv import load_dotenv
import uuid

load_dotenv()

owner = os.environ.get('REPO_OWNER', 'BigDataIA-Summer2023-Team2')
repo = os.environ.get('REPO_NAME', 'MAEC-A-Multimodal-Aligned-Earnings-Conference-Call-Dataset-for-Financial-Risk-Prediction')
directory_path = os.environ.get('DATASET_DIR', 'MAEC_Dataset')
token = os.environ.get('GITHUB_AUTH_TOKEN', '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')
gcs_bucket_name = os.environ.get('GCS_BUCKET_NAME', 'damg7245-summer23-team2')
gcs_project_id = os.environ.get('GCS_PROJECT_ID', 'damg7245-assignment2')


storage_client = gcs.Client(project=gcs_project_id)
bucket = storage_client.bucket(gcs_bucket_name)

default_args = {
    'owner': 'Damg-team2',
    'start_date': datetime(2023, 6, 19),
}


dag = DAG(
    dag_id="github_to_gcs_to_postgres",
    # Run daily midnight to fetch metadata from github
    schedule="0 0 * * *",   # https://crontab.guru/
    start_date=days_ago(0),
    catchup=False,
    dagrun_timeout=timedelta(minutes=60),
    tags=["assignment2", "damg7245", "github_to_gcs_to_postgres"],
)
metadata_raw = []
url = 'https://raw.githubusercontent.com/plotly/dash-stock-tickers-demo-app/master/tickers.csv'
tickers_df = pd.read_csv(url)

def initialize_bucket():
    try:
        bucket.reload()
        print(f'Bucket {gcs_bucket_name} exists.')
    except:
        print(f'Bucket {gcs_bucket_name} does not exist.')
        bucket.storage_class = "STANDARD"
        storage_client.create_bucket(bucket, location="us-east1")

def get_directory_contents(owner, repo, directory_path, token):
    bucket.reload()
    
    headers = {'Authorization': f'token {token}'}
    api_url = f'https://api.github.com/repos/{owner}/{repo}/contents/{directory_path}'
    response = requests.get(api_url, headers=headers)
    data = response.json()
    contents = []
    for item in data:
        print(contents)
        if item is None:
            continue
        if item.get('type') is None:
            continue
        if item['type'] == 'file':
            contents.append(item['download_url'])
        elif item['type'] == 'dir':
            contents += get_directory_contents(owner, repo, item['path'], token)

    headers = {'Authorization': f'token {token}'}
    for c in contents:
        api_url = c
        response1 = requests.get(api_url, headers=headers)
        folder=api_url.split('/')[-2]
        filename=api_url.split('/')[-1]
        if response1.status_code != 200:
            continue
        file_content=response1.content
        blob = bucket.blob(folder+'/'+filename)
        blob.upload_from_string(file_content)
        print(f'Uploaded to Google Cloud Storage')
    return contents


def list_top_folders_and_files(bucket_name, prefix='', limit=10):
    blobs = bucket.list_blobs(prefix=prefix)
    folders = set()
    files = []
    data = []
    for blob in blobs:
        name = blob.name
        if name.endswith('/'):
            folder_name = name.split('/')[0]
            if folder_name:
                folders.add(folder_name)
        else:
            files.append(name)

        if len(folders) + len(files) >= limit:
            break

    for folder in folders.copy():
        if len(folders) + len(files) >= limit:
            break
        subfolders, subfiles = list_top_folders_and_files(bucket_name, prefix=folder, limit=limit - (len(folders) + len(files)))
        folders.update(subfolders)
        files.extend(subfiles)

    for f in files:
        id = 0
        date_string = f.split('/')[0].split('_')[0]
        date = datetime.strptime(date_string, '%Y%m%d')
        year = date.year
        month = date.month
        day = date.day
        quarter = (month - 1) // 3 + 1
        ticker = f.split('/')[0].split('_')[1]

        csymbol = ticker
        filtered_df = tickers_df[tickers_df['Symbol'] == csymbol]

        if not filtered_df.empty:
            company_name = filtered_df['Company'].iloc[0]
            print(f"Company Name: {company_name}")
        else:
            print("No matching symbol found.")

        stored_url = f"https://storage.cloud.google.com/{bucket_name}/{f}"
        print(f"Stored URL: {stored_url}")
        datatuple= {"'id':"+str(id)+", 'name':"+str(company_name)+", 'date':"+str(date)+", 'quarter':"+str(quarter)+", 'month':"+str(month)+", 'day':"+str(day)+", 'year':"+str(year)+", 'ticker':"+str(csymbol)+", 'gurl':"+str(stored_url)}
        
        data_list = [id, company_name, date, quarter, month, day, year, ticker, stored_url]
        metadata_raw.append(data_list)

        data.append(datatuple)
        id += 1
    return metadata_raw

def store_metadata_cloudsql(ti):
    metadata_raw = ti.xcom_pull(key="return_value", task_ids='fetch_data')
    metadata = pd.DataFrame(metadata_raw, columns=['id','name', 'date', 'quarter', 'month', 'day', 'year', 'ticker', 'gurl'])
    print(metadata)

    connector = Connector()

    # build connection for db using Python Connector
    def getconn():
        conn = connector.connect(
            instance_connection_string=os.environ['INSTANCE_CONNECTION_NAME'],
            driver="pg8000",
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASS'],
            db=os.environ['DB_NAME'],
        )
        return conn

    pool = create_engine("postgresql+pg8000://", creator = getconn)

    with pool.connect() as conn:
        current_time = conn.execute(text("SELECT NOW()")).fetchone()
        print(f"Time: {str(current_time[0])}")


    with pool.connect() as conn:
        metadata.to_sql(name='metadata', con=conn, index=False, if_exists='replace')
        print("Done")    

with dag:
    initialize_bucket = PythonOperator(
        task_id='initialize_bucket',
        python_callable=initialize_bucket,
    )
    # fetch_and_push_task = PythonOperator(
    #     task_id='fetch_and_push_to_gcs',
    #     python_callable=get_directory_contents,
    #     op_args=[owner,repo,directory_path,token]
    # )
    fetch_data_task = PythonOperator(
        task_id='fetch_data',
        python_callable=list_top_folders_and_files,
        op_args=[gcs_bucket_name, '', 10]
    )
    store_metadata_cloudsql_task = PythonOperator(
        task_id='store_metadata_cloudsql',
        python_callable=store_metadata_cloudsql,
    )
    # chain(initialize_bucket, fetch_and_push_task, fetch_data_task)
    chain(initialize_bucket, fetch_data_task, store_metadata_cloudsql_task)

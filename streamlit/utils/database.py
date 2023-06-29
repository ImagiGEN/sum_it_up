import os
import pandas as pd
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv
from google.cloud.sql.connector import Connector

load_dotenv()

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

pool = sqlalchemy.create_engine("postgresql+pg8000://", creator=getconn)


def db_connection_test():
    with pool.connect() as conn:
        current_time = conn.execute(text("SELECT NOW()")).fetchone()
        print(f"Time: {str(current_time[0])}")

def fetch_metadata_from_db():
    with pool.connect() as conn:
        df = pd.read_sql_table("metadata", con=conn)
        print(df.head())
        return df

# print(f"-----Testing connection to Cloud SQL instance-----")
# db_connection_test()

# print(f"-----Loading data to Cloud SQL instance-----")
# load_data_to_db()

# print("-----Get data from Cloud SQL instance-----")
# fetch_data_from_db()
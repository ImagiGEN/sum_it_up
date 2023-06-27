# diagram.py
from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB
from diagrams.onprem.client import Users
from diagrams.gcp.database import SQL
from diagrams.onprem.workflow import Airflow
from diagrams.programming.framework import Fastapi
from diagrams.custom import Custom



with Diagram("Architecture", show=False):
    streamlit = Custom("UI", "./myresources/streamlit.jpg")
    pinecone = Custom("LLM", "./myresources/pinecone.jpg")
    langchain = Custom("LLM", "./myresources/langchain.jpg")
    user  = Users("Investment Analysts") 
    database = SQL("Database")
    dag = Airflow("Store data DAG")
    
    user >> streamlit
    dag >> database
    streamlit << database
    streamlit >> [dag, pinecone, langchain]
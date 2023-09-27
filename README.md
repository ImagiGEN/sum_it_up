# TranscriptQuery Pro
The primary objective of this assignment is to create a system that incorporates vector similarity search, traditional filtering, and hybrid search features. The application will serve as a valuable tool for financial analysts, enabling them to efficiently search for relevant information within earnings call transcripts.

## Project Resources
* [CodeLab Docs](https://codelabs-preview.appspot.com/?file_id=11EID9lPIXXklNVIuZB30y1d4Qw0QY8KpgyXMu73FQss#0)

### Link to the Live Applications
* Streamlit Application : http://35.231.98.240:8090/

## Project Flow 

The application will serve as a valuable tool for financial analysts, enabling them to efficiently search for relevant information within earnings call transcripts.
To accomplish this goal, we will use a combination of tools and technologies. Clous SQL will be utilized as the data storage solution, ensuring seamless and efficient data management. Airflow, a robust data retrieval and processing platform, will facilitate the retrieval and transformation of earnings call transcript data. Streamlit, a user-friendly framework, will be employed to develop an intuitive front-end application. To enhance data accessibility and scalability, relevant metadata will be extracted from the data source and stored in a PostgresSQL database.
We aim to deliver a high-quality, user-friendly application that empowers financial analysts at Intelligence Co to unlock the full potential of earnings call transcripts in their research and decision-making processes.

## Project Tree 

```
.
├── CaseStudy.ipynb
├── Makefile
├── README.md
├── airflow
│   ├── Dockerfile
│   ├── dags
│   │   └── fetch_transcript.py
│   └── requirements.txt
├── diagrams
│   ├── architecture.png
│   ├── architecture.py
│   └── myresources
│       ├── langchain.jpg
│       ├── pinecone.jpg
│       └── streamlit.jpg
├── docker-compose-local.yml
└── streamlit
    ├── Dockerfile
    ├── Home.py
    ├── pages
    │   ├── 1_Summary_Generator.py
    │   ├── 2_Contextual_QnA.py
    │   ├── 3_Langchain_Summary_Generator.py
    │   └── 4_Langchain_QnA.py
    ├── requirements.txt
    └── utils
        ├── __init__.py
        ├── database.py
        ├── generic.py
        ├── langchain.py
        ├── pinecone_utils.py
        └── summarization.py
```

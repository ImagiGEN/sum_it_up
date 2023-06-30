FROM python:3.9.13
# Pull the base docker image of python with tag 3.9.13

WORKDIR /app
# Change the working dir inside the container - cd /app

COPY Home.py requirements.txt ./
COPY pages ./pages
COPY utils ./utils
# COPY .streamlit ./.streamlit
# Copy source code and dependency

COPY gcs_key.json /

RUN pip install -r requirements.txt
RUN pip install --upgrade google-cloud-storage
# Install the dependency

### Container Env same as local at this point
EXPOSE 8090

CMD ["streamlit", "run", "Home.py", "--server.port", "8090"]
FROM python:3.10.6-buster

COPY requirements_prod.txt /requirements_prod.txt

RUN pip install --upgrade pip
RUN pip install -r requirements_prod.txt

COPY api /api
COPY setup.py /setup.py

# GCP project for Safety Map Project
ENV GCP_PROJECT=wagon-bootcamp-385417
ENV GCP_REGION=us-west1

# Cloud Storage
ENV BUCKET_NAME=safety-map-model

# BigQuery
ENV BQ_REGION=US
ENV BQ_DATASET=Safetymap
ENV TABLE_ID=historical_data
ENV BQ_DATASET_PREDICTION=predictions

ENV PREFECT_LOG_LEVEL=WARNING

# API on Gcloud Run
ENV GCR_IMAGE=safety-map-api

# Docker
ENV DOCKER_IMAGE_NAME="safety-map-api"
ENV GCR_REGION=us-west2
ENV GCR_MULTI_REGION="us.gcr.io"

ENV GOOGLE_APPLICATION_CREDENTIALS=credentials/wagon-bootcamp-385417-bfee5f083d98.json

RUN pip install .

COPY credentials/wagon-bootcamp-385417-bfee5f083d98.json credentials/wagon-bootcamp-385417-bfee5f083d98.json

CMD uvicorn api.fastapi.fast:app --host 0.0.0.0 --port $PORT

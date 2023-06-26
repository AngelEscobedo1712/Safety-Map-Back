import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.registry import load_model
from google.cloud import bigquery
import os

# from taxifare.ml_logic.preprocessor import preprocess_features

app = FastAPI()

# Create a BigQuery client
client = bigquery.Client()

# Allowing all middleware is optional, but good practice for dev purposes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
# Define BigQuery project ID, dataset ID, and table ID
project_id = os.getenv("GCP_PROJECT")
dataset_id = os.getenv("BQ_DATASET")
table_id_predictions = os.getenv("BQ_DATASET_PREDICTION")


@app.get("/predict")
def predict(year_month: str = None, category: str = None):
    # Construct the WHERE clause based on the query parameters

    query = f"""
        SELECT Neighborhood, year_month, {category}
        FROM {project_id}.{dataset_id}.{table_id_predictions}
        WHERE year_month = '{year_month}' ORDER BY year_month
    """

    # Run the query
    query_job = client.query(query)
    dataframe = query_job.to_dataframe()

    # Convert the result to a list of dictionaries
    result = dataframe.to_dict(orient='records')

    # Return the result as JSON
    return {"data": result}

















@app.get("/")
def root():
    return {
    'greeting': "Hello, it's working"
    }

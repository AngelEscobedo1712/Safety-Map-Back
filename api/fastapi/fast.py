from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import bigquery
from google.cloud import storage
import pandas as pd

import os
from typing import List
import json

app = FastAPI()

# Allowing all middleware is optional, but good practice for dev purposes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Create a BigQuery client
client_gbq = bigquery.Client()
client_storage = storage.Client()

# Define BigQuery project ID, dataset ID, and table ID
project_id = os.getenv("GCP_PROJECT")
dataset_id = os.getenv("BQ_DATASET")
table_id = os.getenv("TABLE_ID")
table_id_predictions = os.getenv("TABLE_ID_PREDICTIONS")
bucket_name = os.getenv("BUCKET_NAME")



@app.get("/neighborhoods")
def get_neighborhoods():
    # Prepare the query to retrieve distinct neighborhoods
    query = f"SELECT DISTINCT alcaldia_colonia FROM `{project_id}.{dataset_id}.coords_neighborhoods`"

    # Execute the query and fetch the results
    query_job = client_gbq.query(query)
    rows = query_job.result()

    # Extract the column values into a Python list
    neighborhoods = [row["alcaldia_colonia"] for row in rows]

    return {"neighborhoods": neighborhoods}


@app.post("/get_historical_data")
async def get_historical_data(
    neighborhoods: List[str] = None,
    years: List[int] = None,
    months: List[str] = None,
    categories: List[str] = None,
):
    # Construct the WHERE clause based on the query parameters
    where_clauses = []

    if neighborhoods:
        neighborhood_clause = " OR ".join([
            f"Neighborhood = '{neighborhood}'"
            for neighborhood in neighborhoods
        ])
        where_clauses.append(f"({neighborhood_clause})")

    if years and "ALL" not in years:
        year_clause = " OR ".join([f"Year = {year}" for year in years])
        where_clauses.append(f"({year_clause})")

    if months and "ALL" not in months:
        month_clause = " OR ".join([f"Month = '{month}'" for month in months])
        where_clauses.append(f"({month_clause})")

    if categories and "ALL" not in categories:
        category_clause = " OR ".join(
            [f"Category = '{category}'" for category in categories])
        where_clauses.append(f"({category_clause})")

    # Prepare the query
    if where_clauses:
        where_clause = " AND ".join(where_clauses)
    else:
        where_clause = "1 = 1"  # Condition to select all values

    query = f"""
        SELECT Latitude, Longitude, Category, Month
        FROM `{project_id}.{dataset_id}.{table_id}`
        WHERE {where_clause}
    """

    # Run the query
    query_job = client_gbq.query(query)
    dataframe = query_job.to_dataframe()

    # Convert the result to a list of dictionaries
    result = dataframe.to_dict(orient='records')

    # Return the result as JSON
    return {"data": result}



@app.get("/predict")
def predict(year_month: str = None, category: str = None):

    query = f"""
        SELECT Neighborhood, year_month, {category}
        FROM {project_id}.{dataset_id}.{table_id_predictions}
        WHERE year_month = '{year_month}' ORDER BY year_month
    """

    # Run the query
    query_job = client_gbq.query(query)
    dataframe = query_job.to_dataframe()

    # Convert the result to a list of dictionaries
    result = dataframe.to_dict(orient='records')

    # Return the result as JSON
    return {"data": result}


@app.get("/coordinates")
def get_coordinates():
    # Prepare the query to retrieve distinct neighborhoods
    query = f"""SELECT *
            FROM {project_id}.{dataset_id}.coords_neighborhoods
    """
    # Execute the query and fetch the results

    query_job = client_gbq.query(query)


    # make dataframe from the query
    dataframe_coords = query_job.to_dataframe()
    dataframe_coords.rename(columns={"alcaldia_colonia": "Neighborhood"},inplace=True)

    # Convert the result to a list of dictionaries
    result = dataframe_coords.to_dict(orient='records')

    # Return the result as JSON
    return {"data": result}



@app.get("/get_crimes")
def get_crimes(year_month: str = None, category: str = None):
    # Prepare the query to retrieve the predictions with polygons
    query = f"""SELECT Neighborhood, code, {category}
                FROM {project_id}.{dataset_id}.predictions_polygons_merged
                WHERE year_month = '{year_month}' ORDER BY year_month"""

    query_job = client_gbq.query(query)

    df_pred_pol = query_job.to_dataframe()

    # Convert the result to a list of dictionaries
    result = df_pred_pol.to_dict(orient='records')

    # Return the result as JSON
    return {"data": result}


@app.get("/download_polygons")
def download_polygons():
    colonias_geo = 'georef-mexico-colonia.geojson'

    bucket = client_storage.get_bucket(bucket_name)
    blob_geo = bucket.blob(colonias_geo)

    blob_geo.download_to_filename('local_geo.json')

    with open('local_geo.json', 'r') as file:
        geojson_content = json.load(file)

    return geojson_content


@app.post("/get_plot_historical_data")
def get_plot_historical_data(
    neighborhoods: List[str] = None,
    years: List[int] = None,
    categories: List[str] = None,
):
    where_clauses = []

    if neighborhoods:
        neighborhood_clause = " OR ".join([
            f"Neighborhood = '{neighborhood}'"
            for neighborhood in neighborhoods
        ])
        where_clauses.append(f"({neighborhood_clause})")

    if years and "ALL" not in years:
        year_clause = " OR ".join([f"Year = {year}" for year in years])
        where_clauses.append(f"({year_clause})")

    if categories and "ALL" not in categories:
        category_clause = " OR ".join(
            [f"Category = '{category}'" for category in categories])
        where_clauses.append(f"({category_clause})")

    # Prepare the query
    if where_clauses:
        where_clause = " AND ".join(where_clauses)
    else:
        where_clause = "1 = 1"  # Condition to select all values

    query = f"""SELECT Year, Month, Category, Neighborhood,
                COUNT(*) AS TotalCrimes
                FROM `{project_id}.{dataset_id}.{table_id}`
                WHERE {where_clause}
                GROUP BY Year, Month, Category, Neighborhood
                ORDER BY Year, Month
                """


    # Run the query
    query_job = client_gbq.query(query)
    dataframe = query_job.to_dataframe()

    # Convert the result to a list of dictionaries
    result = dataframe.to_dict(orient='records')

    # Return the result as JSON
    return {"data": result}



@app.get("/get_plot_prediction_data")
def get_plot_prediction_data():

    query = f"""
            SELECT year_month,
            SUM(fraud) AS total_fraud,
            SUM(threats) AS total_threats,
            SUM(burglary) AS total_burglary,
            SUM(homicide) AS total_homicide,
            SUM(sexual_crime) AS total_sexual_crime,
            SUM(property_damage) AS total_property_damage,
            SUM(domestic_violence) AS total_domestic_violence,
            SUM(danger_of_well_being) AS total_danger_of_well_being,
            SUM(robbery_with_violence) AS total_robbery_with_violence,
            SUM(robbery_without_violence) AS total_robbery_without_violence,
            SUM(score) AS total_score
            FROM {project_id}.{dataset_id}.{table_id_predictions}
            WHERE year_month > '2023-06-01'
            GROUP BY year_month
            ORDER BY year_month;
        """

    # Run the query
    query_job = client_gbq.query(query)
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

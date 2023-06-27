from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import bigquery
import os
from typing import List

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
client = bigquery.Client()

# Define BigQuery project ID, dataset ID, and table ID
project_id = os.getenv("GCP_PROJECT")
dataset_id = os.getenv("BQ_DATASET")
table_id = os.getenv("TABLE_ID")

@app.get("/neighborhoods")
def get_neighborhoods():
    # Prepare the query to retrieve distinct neighborhoods
    query = f"SELECT DISTINCT alcaldia_colonia FROM `{project_id}.{dataset_id}.coords_neighborhoods`"

    # Execute the query and fetch the results
    query_job = client.query(query)
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
        neighborhood_clause = " OR ".join([f"Neighborhood = '{neighborhood}'" for neighborhood in neighborhoods])
        where_clauses.append(f"({neighborhood_clause})")

    if years and "ALL" not in years:
        year_clause = " OR ".join([f"Year = {year}" for year in years])
        where_clauses.append(f"({year_clause})")

    if months and "ALL" not in months:
        month_clause = " OR ".join([f"Month = '{month}'" for month in months])
        where_clauses.append(f"({month_clause})")

    if categories and "ALL" not in categories:
        category_clause = " OR ".join([f"Category = '{category}'" for category in categories])
        where_clauses.append(f"({category_clause})")

    # Prepare the query
    if where_clauses:
        where_clause = " AND ".join(where_clauses)
    else:
        where_clause = "1 = 1"  # Condition to select all values

    query = f"""
        SELECT Latitude, Longitude
        FROM `{project_id}.{dataset_id}.{table_id}`
        WHERE {where_clause}
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

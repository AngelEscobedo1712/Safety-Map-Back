from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import bigquery
import os

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
table_id_predictions = os.getenv("BQ_DATASET_PREDICTION")


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



@app.get("/get_historical_data")
async def get_historical_data(neighborhood: str = None, year: int = None, month: str = None, category: str = None):
    # Construct the WHERE clause based on the query parameters
    where_clauses = []
    if neighborhood:
        where_clauses.append(f"Neighborhood = '{neighborhood}'")
    if year:
        where_clauses.append(f"Year = {year}")
    if month:
        where_clauses.append(f"Month = '{month}'")
    if category:
        where_clauses.append(f"Category = '{category}'")

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

  
  
@app.get("/predict")
def predict(year_month: str = None, category: str = None):

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
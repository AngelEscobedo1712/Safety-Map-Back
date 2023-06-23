import os
import numpy as np
from dotenv import load_dotenv
load_dotenv()


## VARIABLES
GCP_PROJECT = os.environ.get("GCP_PROJECT")
GCP_REGION = os.environ.get("GCP_REGION")
BUCKET_NAME = os.environ.get("BUCKET_NAME")
BQ_DATASET= os.environ.get("BQ_DATASET")
BQ_DATASET_PREDICTION= os.environ.get("BQ_DATASET_PREDICTION")

## CONSTANTS
LOCAL_REGISTRY_PATH =  os.path.join(os.path.expanduser('~'), ".lewagon", "mlops", "training_outputs")

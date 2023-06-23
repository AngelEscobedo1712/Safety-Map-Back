import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.registry import load_model
# from taxifare.ml_logic.preprocessor import preprocess_features


app = FastAPI()

# Allowing all middleware is optional, but good practice for dev purposes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.state.model = load_model()
model = app.state.model

# http://127.0.0.1:8000/predict?pickup_datetime=2012-10-06 12:10:20&pickup_longitude=40.7614327&pickup_latitude=-73.9798156&dropoff_longitude=40.6513111&dropoff_latitude=-73.8803331&passenger_count=2
@app.get("/predict")
def predict(
        # Replace by inputs for prediction
        neighbourhood: str,  # Name of neighbourhood
        crime_types: list,    # List of crime types to predict
        # etc.
    ):
    """
    Make predictions
    """
    X_pred = pd.DataFrame(locals(),index=[0])

    model = app.state.model
    assert model is not None


    X_pred_processed = X_pred #replace by: preprocess_features(X_pred)
    pred_output = model.predict(X_pred_processed)

    return dict(predictions=float(pred_output)) # replace by what model should return


@app.get("/")
def root():
    return {
    'greeting': "Hello, it's working"
    }

import numpy as np
import pandas as pd
import json

from registry import load_model, load_data_to_bq
from model import get_X_y_strides
from model import INPUT_LENGTH, OUTPUT_LENGTH, SEQUENCE_STRIDE
from params import GCP_PROJECT, BQ_DATASET, BQ_DATASET_PREDICTION


def make_the_dataframe(predictions, nom_delitos_colonias):
# Date Series for the prediction dataframe
    start_date = '2023-01-01'
    num_periods = 12
    date_range = pd.date_range(start=start_date, periods=num_periods, freq='MS')
    date_series = pd.Series(range(num_periods), index=date_range)

    # Empty list to save the list of dataframes
   # Empty list to save the list of dataframes
    p1 = []
    nom_delitos = nom_delitos_colonias["delitos"]
    nom_colonias = nom_delitos_colonias["colonias"]

    for year_month in range(predictions.shape[1]):
        p1.append(pd.DataFrame(predictions[:, year_month, :], columns =nom_delitos, index = nom_colonias).assign(year_month= date_series.index[year_month].date()))

    new_prediction = pd.concat(p1)
    prediction_dataframe = new_prediction.set_index("year_month",append=True)\
        .round(0).astype(int).reset_index()\
        .rename(columns=lambda x: x.replace(" ", "_").replace("-","_"))\
        .rename(columns={"level_0": "Neighborhood"})

    return prediction_dataframe

if __name__ == "__main__":
    # Let us get the predictions!
    model = load_model()
    fold_test = pd.read_pickle("raw_data/fold_test.pkl")

    with open ("raw_data/tempfiles/nom_delitos_colonias.json", "r") as jsonfile:
        nom_delitos_colonias = json.load(jsonfile)

    # Running the Test function for X and y, and save it as csv
    X_test, y_test = get_X_y_strides(fold_test, INPUT_LENGTH, OUTPUT_LENGTH, SEQUENCE_STRIDE)

    predictions = model.predict(X_test)

    prediction_dataframe = make_the_dataframe(predictions, nom_delitos_colonias)
    prediction_dataframe.to_csv("raw_data/dataframe_score.csv")
    # Adding a "score" column
    prediction_dataframe = prediction_dataframe.assign(score=lambda x:
                                    x.burglary*7 +
                                    x.danger_of_well_being*6 +
                                    x.domestic_violence*2 +
                                    x.fraud*1 +
                                    x.homicide*10 +
                                    x.property_damage*5 +
                                    x.robbery_with_violence*8 +
                                    x.robbery_without_violence*4 +
                                    x.sexual_crime*9 +
                                    x.threats*3
                                    )


    load_data_to_bq(prediction_dataframe,
                    GCP_PROJECT,
                    BQ_DATASET,
                    BQ_DATASET_PREDICTION,
                    truncate= True
    )
    print("We are Ready!, try with these predictions")

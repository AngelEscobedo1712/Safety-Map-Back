import numpy as np
import pandas as pd

from pathlib import Path
import json
# from colorama import Fore, Style

from registry import save_model

from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
import numpy as np

from typing import Tuple
from registry import load_data_to_bq

pd.set_option('display.max_columns', 500)

#TensorFlow
from tensorflow.keras import models
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential
from tensorflow.keras import optimizers, metrics
from tensorflow.keras.regularizers import L1L2
from tensorflow.keras.callbacks import EarlyStopping

url = "https://storage.googleapis.com/safety-map-model/preprocessed_data.csv"

def get_data(url):
  df = pd.read_csv(url)
  df.drop(columns = "Neighborhood_ID", inplace = True)
  pre_data = df.set_index(["year_month","Neighborhood"]).unstack("Neighborhood")
  return df,pre_data

############
INPUT_LENGTH = 1 * 12 # records every 1 month x 12 months per year = 12 months
TRAIN_TEST_RATIO = 0.70 #70% of the data is going to be for training
############

def train_test_split(fold:pd.DataFrame,
                     train_test_ratio: float,
                     input_length: int) -> Tuple[pd.DataFrame]:
    """From a fold dataframe, take a train dataframe and test dataframe based on
    the split ratio.
    - df_train should contain all the timesteps until round(train_test_ratio * len(fold))
    - df_test should contain all the timesteps needed to create all (X_test, y_test) tuples

    Args:
        fold (pd.DataFrame): A fold of timesteps
        train_test_ratio (float): The ratio between train and test 0-1
        input_length (int): How long each X_i will be

    Returns:
        Tuple[pd.DataFrame]: A tuple of two dataframes (fold_train, fold_test)
    """
    fold_train = fold[0:round(len(fold)*train_test_ratio)]
    fold_test = fold[(round(len(fold)*train_test_ratio - input_length)):]
    return fold_train,fold_test

##########################
SEQUENCE_STRIDE = 1
OUTPUT_LENGTH = 12
TARGET = ['burglary', 'danger of well-being',
       'domestic violence', 'fraud', 'homicide', 'property damage',
       'robbery with violence', 'robbery without violence', 'sexual crime',
       'threats']
##########################

def get_X_y_strides(fold: pd.DataFrame, input_length: int, output_length: int,
    sequence_stride: int) -> Tuple[np.array]:
    """slides through a `fold` Time Series (2D array) to create sequences of equal
        * `input_length` for X,
        * `output_length` for y,
    using a temporal gap `sequence_stride` between each sequence

    Args:
        fold (pd.DataFrame): One single fold dataframe
        input_length (int): Length of each X_i
        output_length (int): Length of each y_i
        sequence_stride (int): How many timesteps to take before taking the next X_i

    Returns:
        Tuple[np.array]: A tuple of numpy arrays (X, y)
    """
    for i in range(0, len(fold), sequence_stride):
        # Exits the loop as soon as the last fold index would exceed the last index
        if (i + input_length + output_length) >= len(fold):
            break
        X_i_transformed = fold.iloc[i:i + input_length, :]
        y_i_transformed = fold.iloc[i + input_length:i + input_length + output_length, :][TARGET]

        fold_train_list = X_i_transformed.stack("Neighborhood").groupby(["Neighborhood", "year_month"])\
                            .apply(lambda x: x.values.tolist()[0])\
                            .groupby("Neighborhood").apply(lambda x: x.values.tolist())\
                            .tolist()

        fold_test_list = y_i_transformed.stack("Neighborhood").groupby(["Neighborhood", "year_month"])\
                            .apply(lambda x: x.values.tolist()[0])\
                            .groupby("Neighborhood").apply(lambda x: x.values.tolist())\
                            .tolist()

    return (np.array(fold_train_list), np.array(fold_test_list))

def init_model(X_train, y_train):
    model = Sequential()

    # –– Model
    model.add(layers.Masking(mask_value=-1, input_shape=(12,10)))
    model.add(layers.LSTM(units=40, activation='tanh', return_sequences =True))
    model.add(layers.Dense(50, activation='relu'))
    model.add(layers.Dropout(rate=0.2))  # The rate is the percentage of neurons that are "killed"
    model.add(layers.Dense(10, activation='relu'))

    # –– Compilation
    model.compile(loss='mse',
                  optimizer='adam',
                 metrics = ["mae"])

    return model


if __name__== "__main__":
    #Get Fold_train  and Fold_test
    (df, pre_data) = get_data(url)
    nom_delitos = df.columns[2:].tolist()
    nom_colonias = df.Neighborhood.unique().tolist()

    nom_delitos_colonias = {"delitos": nom_delitos, "colonias" : nom_colonias}
    with open("raw_data/tempfiles/nom_delitos_colonias.json", "w") as jsonfile:
        json.dump(nom_delitos_colonias, jsonfile)

    (fold_train, fold_test) = train_test_split(pre_data, TRAIN_TEST_RATIO, INPUT_LENGTH)
    fold_test.to_pickle("raw_data/fold_test.pkl")

    # Running the Train function for X and y
    X_train, y_train = get_X_y_strides(fold_train, INPUT_LENGTH, OUTPUT_LENGTH, SEQUENCE_STRIDE)
    # Running the Test functeion for X and y
    X_test, y_test = get_X_y_strides(fold_test, INPUT_LENGTH, OUTPUT_LENGTH, SEQUENCE_STRIDE)

    #initiate model
    model = init_model(X_train, y_train)

    # Early Stopping with patience 10
    es = EarlyStopping(patience=10)

    # Fiting Model
    model.fit(X_train, y_train,
            epochs=200,
            batch_size=32,
            verbose=1,
            callbacks = [es],
            validation_split=0.2)

    print("Yaaay! Your Model Seems to Work!")

    #saving the model to the cloud
    save_model(model)

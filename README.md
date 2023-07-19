
#¡Welcome to Your Safety Map!

Have you ever been afraid where are you walking at?

We know that security is the top thing we have to consider at the time of visiting a New City, of even a New Neighborhood.

That´s why we made this Wonderful App for you.

Let me tell U how it Works...

  1. We have 3 main pages, the Landing page, the Historical and the Forecasting, the last one is about to be developed, still in progress.
  2. For the Historical part you can search for 10 different types of crimes that have been registered since 2019 in every Neighborhood, mapped for you ;).
  3. For the Forecasting part you can look for the type of crime you want to know how is going to be up to the next 6 months, all displayed in a beautiful heat-map of the México City 

## Safety-Map-Back
Repository for the Back End of Safety Map project

### Instructions

  - Create a virtual environment for the Safety-Map-Back running the next line in the Terminal:
  pyenv virtualenv Safety-Map-Back

  - Then change to the virtual environment with the next line in the Terminal:
  pyenv local Safety-Map-Back

  - For you to install the necessary packages run the next line in the Terminal:
  pip install -r requirements_prod.txt

  - Before testing it it works, you have to to copy the credentials folder with the GCP Keys, and the .env file in the root folder

  - Then you can test is it can run, running the next line in the Terminal:
  make run_api

## Data used in the project from "Víctimas en carpetas de investigación FGJ" of the Ciudad de México

URL = https://datos.cdmx.gob.mx/dataset/victimas-en-carpetas-de-investigacion-fgj#:~:text=Descargar-,V%C3%ADctimas%20en%20Carpetas%20de%20Investigaci%C3%B3n%20(completa),-CSV


## GCP Project Safety-Map
URL = https://console.cloud.google.com/welcome/new?project=wagon-bootcamp-385417

### Cleaned data (NOT PROCESSED) stored in a public available GCP bucket
URL = https://storage.googleapis.com/safety-map-model/clean_data.csv

### Dictionary with neighborhoods and corresponding IDs, stored in a public available GCP bucket
URL = https://storage.googleapis.com/safetymap/colonia_id_dict.json

### Preprocessed data, stored in a public available GCP bucket
URL = https://storage.googleapis.com/safety-map-model/preprocessed_data.csv

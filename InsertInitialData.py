"""
    Insert the initial data of the mnaufacturers and the models in the Mongo DB
"""
from MongoDBOperations import MongoDBOperations
import Configurations

import pandas as pd

class InsertInitialData(MongoDBOperations):
    def __init__(self):
        MongoDBOperations.__init__(self)
        self._one_shift_data = "initial_data/oneshift_car_models.csv"
        self._sgcarmart_data = "initial_data/sgcarmart_car_models.csv"

    def _get_manufacturers_models_from_files(self, file_locations):
        if file_locations:
            manufacturers = set()
            models = set()
            for file_location in file_locations: 
                df = pd.read_csv(file_location)
               
                for _, row in df.iterrows():
                    if row["manufacturer"] and row["model"]:
                        manufacturers.add(str(row["manufacturer"]))
                        models.add(str(row["model"]))

            return list(manufacturers), list(models)

    def insert_manufacturers_models(self):
        manufacturers, models = self._get_manufacturers_models_from_files([self._one_shift_data, self._sgcarmart_data])
        manufacturers_list = [ {"name": manufacturer_name} for manufacturer_name in manufacturers ]
        models_list = [ {"name": model_name} for model_name in models ]
        self._insert_multiple_collection(manufacturers_list, Configurations.MANUFACTURERS_COLLECTION_NAME)
        self._insert_multiple_collection(models_list, Configurations.MODELS_COLLECTION_NAME)


if __name__ == "__main__":
    insert_initial_data = InsertInitialData()
    insert_initial_data.insert_manufacturers_models()
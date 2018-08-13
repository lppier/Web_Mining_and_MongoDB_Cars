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
            # Dictionary of sets
            manufacturer_models_dict = {}
            model_manufacture_dict = {}
            for file_location in file_locations: 
                df = pd.read_csv(file_location)
               
                for _, row in df.iterrows():
                    manufacturer = str(row["manufacturer"])
                    model = str(row["model"])
                    if manufacturer and model:  
                    
                        if manufacturer_models_dict.get(manufacturer):
                            manufacturer_models_dict[manufacturer].add(model)
                        else:
                            manufacturer_models_dict[manufacturer] = {model}

                        if model_manufacture_dict.get(model) is None:
                            model_manufacture_dict[model] = manufacturer



            return manufacturer_models_dict, model_manufacture_dict

    def insert_manufacturers_models(self):
        manufacturers, models = self._get_manufacturers_models_from_files([self._one_shift_data, self._sgcarmart_data])
        manufacturers_list = [ { "name": manufacturer_name, "models": list(manufacturers[manufacturer_name]) } for manufacturer_name in manufacturers ]
        models_list = [ { "name": model_name, "manufacturer": models[model_name] } for model_name in models ]
        self._insert_multiple_collection(manufacturers_list, Configurations.MANUFACTURERS_COLLECTION_NAME)
        self._insert_multiple_collection(models_list, Configurations.MODELS_COLLECTION_NAME)


if __name__ == "__main__":
    insert_initial_data = InsertInitialData()
    insert_initial_data.insert_manufacturers_models()
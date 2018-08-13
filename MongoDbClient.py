"""Contains samples to show how to use the API defined in MongoDBOperations class."""

from MongoDBOperations import MongoDBOperations


class MongoDbClient:
    def _get_sample_car_records(self):
        return [{
            "url": "https://docs.mongodb.com/manual/tutorial/insert-documents/",
            "model": "Camri",
            "manufacturer": "Toyota",
            "mileage": "45"
        },
            {
                "url": "https://www.tutorialspoint.com/How-to-insert-a-Python-object-in-Mongodb",
                "model": "Civic",
                "manufacturer": "Honda",
                "mileage": "51"
            }
        ]

    def _get_sample_car_record(self):
        return {
            "url": "https://stackoverflow.com/questions/10292368/insert-python-object-in-mongodb",
            "model": "Model S",
            "manufacturer": "Tesla",
            "mileage": "NA"
        }

    def insert_many_records_sample(self):
        mongo_db_operations = MongoDBOperations()
        car_documents = self._get_sample_car_records()
        mongo_db_operations.insert_multiple_listings(car_documents)

    def insert_single_record_sample(self):
        mongo_db_operations = MongoDBOperations()
        car_document = self._get_sample_car_record()
        mongo_db_operations.insert_single_listing(car_document)

    def get_manufacturers_models(self):
        mongo_db_operations = MongoDBOperations()
        print(mongo_db_operations._manufacturers)
        print(mongo_db_operations._models)


if __name__ == "__main__":
    mongodbclient = MongoDbClient()
    #mongodbclient.insert_many_records_sample()
    #mongodbclient.insert_single_record_sample()
    mongodbclient.get_manufacturers_models()

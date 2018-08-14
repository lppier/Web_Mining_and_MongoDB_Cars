"""Contains samples to show how to use the API defined in MongoDBOperations class."""

from MongoDBOperations import MongoDBOperations


class MongoDbClient:
    def _get_sample_car_records(self):
        return [{
            "url": "https://docs.mongodb.com/manual/tutorial/insert-documents/",
            "title": "Toyota Camry 2.5 (A)",
            "mileage": "45"
        },
            {
                "url": "https://www.tutorialspoint.com/How-to-insert-a-Python-object-in-Mongodb",
                "title": "Honda Civic 1.6 VTi (A) (New 5-yr COE)",
                "mileage": "51"
            }
        ]

    def insert_many_records_sample(self):
        mongo_db_operations = MongoDBOperations()
        car_documents = self._get_sample_car_records()
        mongo_db_operations.insert_multiple_listings(car_documents)


    def get_manufacturers_models(self):
        mongo_db_operations = MongoDBOperations()
        print(mongo_db_operations._manufacturers)
        print(mongo_db_operations._models)


if __name__ == "__main__":
    mongodbclient = MongoDbClient()
    mongodbclient.insert_many_records_sample()
#    mongodbclient.get_manufacturers_models()

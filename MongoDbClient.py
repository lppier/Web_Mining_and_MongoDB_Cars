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

    def _get_samples_for_aggregation(self):
        return [
        {
            "manufacturer": "Toyota",
            "url": "https://www.tutorialspoint.com/How-to-insert-a-Python-object-in-Mongodb",
            "title": "Toyota Camry 2.5 (A)",
            "mileage": "45",
            "price": "100006.76"
        },
        {
            "manufacturer": "Honda",
            "url": "https://www.tutorialspoint.com/How-to-insert-a-Python-object-in-Mongodb",
            "title": "Honda Civic 1.6 VTi (A) (New 5-yr COE)",
            "mileage": "51",
            "price": "100000"
        },
         {
            "manufacturer": "Toyota",
            "url": "https://www.tutorialspoint.com/How-to-insert-a-Python-object-in-Mongodb",
            "title": "Toyota Camry 4.5 (A)",
            "mileage": "45",
            "price": "64522.75"
        },
        {
            "manufacturer": "Honda",
            "url": "https://www.tutorialspoint.com/How-to-insert-a-Python-object-in-Mongodb",
            "title": "Honda Civic 5.6 VTi (A) (New 5-yr COE)",
            "mileage": "45",
            "price": "9385.98"
        },
        {
            "manufacturer": "Honda",
            "url": "https://www.tutorialspoint.com/How-to-insert-a-Python-object-in-Mongodb",
            "title": "Honda City 1.6 VTi (A) (New 5-yr COE)",
            "mileage": "45",
            "price": "9832.98"
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

    def test_aggregation_manufacturers(self):
        mongo_db_operations = MongoDBOperations()
        car_documents = self._get_samples_for_aggregation()
        mongo_db_operations._insert_aggregates_manufacturer(car_documents)


if __name__ == "__main__":
    mongodbclient = MongoDbClient()
    # mongodbclient.insert_many_records_sample()
#    mongodbclient.get_manufacturers_models()
    mongodbclient.test_aggregation_manufacturers()

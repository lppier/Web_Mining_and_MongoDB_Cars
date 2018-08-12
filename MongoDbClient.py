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

    def insert_many_records_sample(self):
        mongo_db_operations = MongoDBOperations()
        car_documents = self._get_sample_car_records()
        mongo_db_operations.insert_multiple(car_documents)

if __name__ == "__main__":
    mongodbclient = MongoDbClient()
    mongodbclient.insert_many_records_sample()


"""Contains samples to show how to use the API defined in MongoDBOperations class."""

from MongoDBOperations import MongoDBOperations
import Configurations

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

    def _get_manufacturer_samples_for_aggregation(self):
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

    def _get_model_samples_for_aggregation(self):
        return [
        {
            "manufacturer": "BMW",
            "url": "https://www.tutorialspoint.com/How-to-insert-a-Python-object-in-Mongodb",
            "title": "BMW 116",
            "model": "116",
            "mileage": "45",
            "price": "1000.76"
        },
        {
            "manufacturer": "BMW",
            "url": "https://www.tutorialspoint.com/How-to-insert-a-Python-object-in-Mongodb",
            "title": "BMW 116",
            "model": "116",
            "mileage": "80",
            "price": "1200.88"
        },
        {
            "manufacturer": "BMW",
            "url": "https://www.tutorialspoint.com/How-to-insert-a-Python-object-in-Mongodb",
            "title": "BMW 120i",
            "model": "120i",
            "mileage": "45",
            "price": "2000"
        },
        {
            "manufacturer": "Honda",
            "url": "https://www.tutorialspoint.com/How-to-insert-a-Python-object-in-Mongodb",
            "title": "Honda Jade",
            "model": "Jade",
            "mileage": "45",
            "price": "500"
        },
      {
            "manufacturer": "Honda",
            "url": "https://www.tutorialspoint.com/How-to-insert-a-Python-object-in-Mongodb",
            "title": "Honda Jade",
            "model": "Jade",
            "mileage": "45",
            "price": "1200.50"
        }
        ]

    def _get_samples_with_date_for_aggregation(self):
        return [
        {
            "manufacturer": "Audi",
            "url": "https://www.tutorialspoint.com/How-to-insert-a-Python-object-in-Mongodb",
            "title": "Audi S8",
            "model": "S8",
            "mileage": "45",
            "price": "1000.76",
            "date_posted": "2016-11-12"
        },
        {
            "manufacturer": "Audi",
            "url": "https://www.tutorialspoint.com/How-to-insert-a-Python-object-in-Mongodb",
            "title": "Audi S8",
            "model": "S8",
            "mileage": "80",
            "price": "1200.88",
            "date_posted": "2017-10-17"
        },
        {
            "manufacturer": "Audi",
            "url": "https://www.tutorialspoint.com/How-to-insert-a-Python-object-in-Mongodb",
            "title": "Audi TTRS",
            "model": "TTRS",
            "mileage": "45",
            "price": "2000",
            "date_posted": "2018-01-19"
        },
        {
            "manufacturer": "Ford",
            "url": "https://www.tutorialspoint.com/How-to-insert-a-Python-object-in-Mongodb",
            "title": "Ford Galaxy",
            "model": "Galaxy",
            "mileage": "45",
            "price": "500",
            "date_posted": "2018-03-03"
        },
        {
            "manufacturer": "Ford",
            "url": "https://www.tutorialspoint.com/How-to-insert-a-Python-object-in-Mongodb",
            "title": "Ford Galaxy",
            "model": "Galaxy",
            "mileage": "45",
            "price": "1200.50",
            "date_posted": "2018-04-06"
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
        car_documents = self._get_manufacturer_samples_for_aggregation()
        mongo_db_operations._insert_aggregates_to_collection(car_documents, Configurations.MANUFACTURERS_COLLECTION_NAME, "manufacturer")

    def test_aggregation_models(self):
        mongo_db_operations = MongoDBOperations()
        car_documents = self._get_model_samples_for_aggregation()
        mongo_db_operations._insert_aggregates_to_collection(car_documents, Configurations.MODELS_COLLECTION_NAME, "model")

    def test_aggregation_combined(self):
        mongo_db_operations = MongoDBOperations()
        car_documents = self._get_samples_with_date_for_aggregation()
        mongo_db_operations._insert_aggregates_to_collection(car_documents, Configurations.MANUFACTURERS_COLLECTION_NAME, "manufacturer")
        mongo_db_operations._insert_aggregates_to_collection(car_documents, Configurations.MODELS_COLLECTION_NAME, "model")


if __name__ == "__main__":
    mongodbclient = MongoDbClient()
    # mongodbclient.insert_many_records_sample()
#    mongodbclient.get_manufacturers_models()
    # mongodbclient.test_aggregation_manufacturers()
    # mongodbclient.test_aggregation_models()
    mongodbclient.test_aggregation_combined()

from pymongo import MongoClient

import Configurations

class MongoDBOperations:
    def __init__(self):
        self._mongo_client = MongoClient(Configurations.MONGO_DB_HOST, int(Configurations.MONGO_DB_PORT))
        print("Successfully connected to Mongo DB host: {0} and port: {1}".format(Configurations.MONGO_DB_HOST, str(Configurations.MONGO_DB_PORT)))
        self._collection = self._create_db_and_collection_if_not_exist()

    def _create_db_and_collection_if_not_exist(self):
        
        database_name = Configurations.DATABASE_NAME
        collection_name = Configurations.COLLECTION_NAME
    
        database = self._mongo_client[database_name]        
        collection = database[collection_name]
    
        return collection

    def insert_multiple(self, car_details_list):
        """Inserts multiple car details into the Mongo DB. It can be used to insert only one item also.

        Args:
            car_details_list (list): The details of the cars as a list of dictionary.

        Raises:
            Exception if there is an error during the insertion

        """
        if car_details_list and len(car_details_list) > 0:
            self._collection.insert_many(car_details_list)
            print("Inserted {0} documents in the collection".format(str(len(car_details_list))))
            return True
        else:
            print("No car detail to insert...")
            return False

    def insert_single(self, car_details):
        """Inserts single car details into the Mongo DB.

        Args:
            car_details: The details of the cars as a dictionary.

        Raises:
            Exception if there is an error during the insertion

        """
        if car_details is not None:
            self._collection.insert_one(car_details)
            print("Inserted 1 document in the collection.")
            return True
        else:
            print("No car detail to insert...")
            return False


        




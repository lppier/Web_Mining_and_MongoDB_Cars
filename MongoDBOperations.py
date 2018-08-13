"""Contains code to interact with Mongo DB"""

from pymongo import MongoClient

import Configurations

class MongoDBOperations:
    def __init__(self):
        self._mongo_client = MongoClient(Configurations.MONGO_DB_HOST, int(Configurations.MONGO_DB_PORT))
        print("Successfully connected to Mongo DB host: {0} and port: {1}".format(Configurations.MONGO_DB_HOST, str(Configurations.MONGO_DB_PORT)))
        self._create_db_and_collections_if_not_exist()
        self._get_all_manufacturers()
        self._get_all_models()

    def _create_db_and_collections_if_not_exist(self):
        
        database_name = Configurations.DATABASE_NAME
        listings_collection_name = Configurations.LISTINGS_COLLECTION_NAME
        manufacturers_collection_name = Configurations.MANUFACTURERS_COLLECTION_NAME
        models_collection_name = Configurations.MODELS_COLLECTION_NAME
    
        database = self._mongo_client[database_name]        
        self._listings_collection = database[listings_collection_name]
        self._manufacturers_collection = database[manufacturers_collection_name]
        self._models_collection = database[models_collection_name]
    

    def insert_multiple_listings(self, listing_details_list):
        """Inserts multiple car details into the Mongo DB. It can be used to insert only one item also.

        Args:
            listing_details_list (list): The details of the listings as a list of dictionary.

        Raises:
            Exception if there is an error during the insertion

        """
        if listing_details_list and len(listing_details_list) > 0:
            self._listings_collection.insert_many(listing_details_list)
            print("Inserted {0} documents in the collection".format(str(len(listing_details_list))))
            return True
        else:
            print("No listing detail to insert...")
            return False

    def insert_single_listing(self, list_details):
        """Inserts single list details into the Mongo DB.

        Args:
            list_details: The details of the listing as a dictionary.

        Raises:
            Exception if there is an error during the insertion

        """
        if list_details is not None:
            self._listings_collection.insert_one(list_details)
            print("Inserted 1 document in the collection.")
            return True
        else:
            print("No listing detail to insert...")
            return False

    def _get_all_manufacturers(self):
        """
            Get all manufacturers in the database.
        """
        manufacturers = self._manufacturers_collection.find()
        self._manufacturers = [manufacturer["name"] for manufacturer in manufacturers]

    def _get_all_models(self):
        """
            Get all models in the database.
        """
        models = self._models_collection.find()
        self._models = [model["name"] for model in models]



        




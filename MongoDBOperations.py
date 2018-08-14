"""Contains code to interact with Mongo DB"""

from pymongo import MongoClient
from Utility import Utility
import Configurations
import pymongo


class MongoDBOperations:
    def __init__(self):
        self._utility = Utility()
        self._mongo_client = MongoClient(Configurations.MONGO_DB_HOST, int(Configurations.MONGO_DB_PORT))
        print("Successfully connected to Mongo DB host: {0} and port: {1}".format(Configurations.MONGO_DB_HOST,
                                                                                  str(Configurations.MONGO_DB_PORT)))
        self._create_db_and_collections_if_not_exist()
        self._create_indexes()
        self._get_all_manufacturers()
        self._get_all_models()

    def _create_indexes(self):
        self._listings_collection.create_index([('url', pymongo.TEXT)], name='search_index',
                                               default_language='english')

    def _create_db_and_collections_if_not_exist(self):

        database_name = Configurations.DATABASE_NAME
        listings_collection_name = Configurations.LISTINGS_COLLECTION_NAME
        manufacturers_collection_name = Configurations.MANUFACTURERS_COLLECTION_NAME
        models_collection_name = Configurations.MODELS_COLLECTION_NAME
        uninserted_collection_name = Configurations.UNINSERTED_COLLECTION_NAME

        self.database = self._mongo_client[database_name]
        self._listings_collection = self.database[listings_collection_name]
        self._manufacturers_collection = self.database[manufacturers_collection_name]
        self._models_collection = self.database[models_collection_name]
        self._uninserted_collection = self.database[uninserted_collection_name]

    def insert_multiple_listings(self, listing_details_list):
        """Inserts multiple car details into the Mongo DB. It can be used to insert only one item also.

        Args:
            listing_details_list (list): The details of the listings as a list of dictionary.

        Raises:
            Exception if there is an error during the insertion

        """
        if listing_details_list and len(listing_details_list) > 0:
            insert_list = []
            error_list = []

            # TODO data has to be valid now for it to be inserted, it will show error now due to verification
            for item in listing_details_list:
                #if self._utility.is_valid_entry(item):  # TODO re-enable when data is valid
                    title = item["title"]
                    manufacturer, model, descrip = self._utility.manufacturer_and_model(title, self._manufacturers,
                                                                                        self._models)
                    item["manufacturer"] = manufacturer
                    item["model"] = model
                    item["model_descrip"] = descrip
                    url_to_search = "http://url/to/search" # TODO to be replaced with item["url"]
                    urls = self._listings_collection.find({"$text": {"$search": url_to_search }})

                    if urls.count() == 0: # NOTE: this is assuming URL is unique
                        insert_list.append(item)
                # else:                         # TODO re-enable when data is valid
                #     error_list.append(item)

            if len(insert_list) > 0:
                self._listings_collection.insert_many(insert_list)
                print("Inserted {0} documents in the collection".format(str(len(insert_list))))
            else:
                print("Inserted 0 documents")

            if len(error_list) > 0:
                self._uninserted_collection.insert_many(error_list)
                print("{0} documents were not inserted due to errors".format(str(len(error_list))))
            else:
                print("All documents inserted.")

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

    def _insert_multiple_collection(self, list_of_documents, collection_name):
        """ (PROTECTED METHOD) Inserts multiple documents into the Mongo DB. Only for internal use and not external consumption!

        Args:
            list_of_documents (list): The list of documents as dictionary.
            collection_name (string): The name of the collection to insert to.

        Raises:
            Exception if there is an error during the insertion

        """
        self.database[collection_name].insert_many(list_of_documents)
        print("{0} records inserted in the {1} collection.".format(str(len(list_of_documents)), collection_name))

"""Contains code to interact with Mongo DB"""

from pymongo import MongoClient
from Utility import Utility
import datetime
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
        self._time_format = "%Y-%m-%d"

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
                try:
                    validity_check_result = self._utility.is_valid_entry(item)
                    if validity_check_result[0]:  # TODO re-enable when data is valid
                        title = item["title"]
                        manufacturer, model, descrip = self._utility.manufacturer_and_model(title, self._manufacturers,
                                                                                            self._models)
                        item["manufacturer"] = manufacturer
                        item["model"] = model
                        item["model_descrip"] = descrip
                        insert_list.append(item)

                        # TODO: @Pier please help fix the below 
                        # url_to_search = item["url"] # TODO to be replaced with item["url"]
                        #urls = self._listings_collection.find({"$text": {"$search": url_to_search }})

                        # if urls.count() == 0: # NOTE: this is assuming URL is unique
                            # insert_list.append(item)
                    else: 
                        # TODO re-enable when data is valid
                        item["error_details"] = validity_check_result[1]
                        error_list.append(item)
                except Exception as ex:
                    item["error_details"] = str(ex)
                    error_list.append(item)

            if len(insert_list) > 0:
                self._listings_collection.insert_many(insert_list)
                print("Inserted {0} documents in the collection".format(str(len(insert_list))))
            else:
                print("Inserted 0 documents")

            # code to compute and insert aggregates based on the insert_list
            self._insert_aggregates_to_collection(insert_list, Configurations.MANUFACTURERS_COLLECTION_NAME, "manufacturer")
            self._insert_aggregates_to_collection(insert_list, Configurations.MODELS_COLLECTION_NAME, "model")

            if len(error_list) > 0:
                self._uninserted_collection.insert_many(error_list)
                print("{0} documents were not inserted due to errors".format(str(len(error_list))))
            else:
                print("All documents inserted.")

            return len(insert_list), len(error_list)
        else:
            print("No listing detail to insert...")
            return 0, None
    
    def insert_crawling_error(self, listing_detail, error_text):
        if listing_detail:
            listing_detail["error_details"] = "Crawling error: " + error_text
            self._uninserted_collection.insert_many([listing_detail])

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

    def _insert_aggregates_to_collection(self, listings_insert_list, collection_name, identifier):
        """Inserts aggregates in the specified collection.

        Args:
            listings_insert_list (list): The details of the listings as a list of dictionary.
            collection_name (string): The name of the collection to insert to.
            identifier (string): The identifier for the records.

        Raises:
            Exception if there is an error during the insertion
        """
        if listings_insert_list and len(listings_insert_list) > 0:
            existing_records = self.database[collection_name].find({})
            existing_records = [document for document in existing_records]
            current_date = datetime.datetime.now().date()

            records_aggregate_values_dict = {}
            for item in listings_insert_list:
                item_price = float(item["price"])

                date_difference_days = 0
                
                if item["posted_on"]:
                    listing_date = datetime.datetime.strptime(item["posted_on"],  self._time_format).date()
                    date_difference = current_date - listing_date
                    date_difference_days = date_difference.days
            
                if records_aggregate_values_dict.get(item[identifier]):
                    # first value holds the sum of prices
                    records_aggregate_values_dict[item[identifier]][0] = records_aggregate_values_dict[item[identifier]][0] + item_price
                    
                    # second value holds the number of cars for the type
                    records_aggregate_values_dict[item[identifier]][1] = records_aggregate_values_dict[item[identifier]][1] + 1

                    # third value holds the date difference
                    records_aggregate_values_dict[item[identifier]][2] = records_aggregate_values_dict[item[identifier]][2] + date_difference_days
                else:
                    records_aggregate_values_dict[item[identifier]] = [item_price, 1, date_difference_days]
            
            documents_to_update = []
            for existing_record in existing_records:
                existing_record_name = existing_record["name"]

                # if the record name exists in the set that is currently processed
                if records_aggregate_values_dict.get(existing_record_name):
                    if existing_record.get("sum_of_prices"):
                        existing_record["sum_of_prices"] = existing_record["sum_of_prices"] + records_aggregate_values_dict[existing_record_name][0]
                    else:
                        existing_record["sum_of_prices"] =  records_aggregate_values_dict[existing_record_name][0]
                    
                    if existing_record.get("quantity"):
                        existing_record["quantity"] = existing_record["quantity"] + records_aggregate_values_dict[existing_record_name][1]
                    else:
                        existing_record["quantity"] =  records_aggregate_values_dict[existing_record_name][1]

                    if existing_record.get("total_days_posted"):
                        existing_record["total_days_posted"] = existing_record["total_days_posted"] +  records_aggregate_values_dict[existing_record_name][2]
                    else:
                        existing_record["total_days_posted"] = records_aggregate_values_dict[existing_record_name][2]

                    documents_to_update.append(existing_record)
            
            for document_to_update in documents_to_update:
                self.database[collection_name].save(document_to_update)

            print('Updates performed for collection: {0} with the identifier: {1}. Number of records: {2}'.format(collection_name, identifier, str(len(documents_to_update))))
                    




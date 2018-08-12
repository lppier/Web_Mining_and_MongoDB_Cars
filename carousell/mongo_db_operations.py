def insert_into_db(car_product):
    """ This method needs to be developed to insert the records into the database"""
    if car_product:
        for k in car_product:
            print("{0}: {1}".format(k, car_product[k]))
        
        print("")
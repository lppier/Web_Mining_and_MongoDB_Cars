from bs4 import BeautifulSoup
import requests
import re
import dateutil.parser as parser
import json


#from MongoDBOperations import MongoDBOperations

BASE_URL = "http://www.sgcarmart.com/used_cars/"
LIMIT = 20


def prepare_cars_urls():
    cars_urls = []
    i = 0
    match_pattern = "info.php\?[^\" a-z]*"
    while i < LIMIT:
        url = BASE_URL+"listing.php?BRSR="+str(i)+"&RPG=20"
        print(url)
        index_page = requests.get(url)
        soup = BeautifulSoup(index_page.content, 'html.parser')

        for link in soup.find_all('a'):
            if re.search(match_pattern, link.get('href')):
                cars_urls.append(BASE_URL+link.get('href'))
        i = i + 20
    car_urls_set = set(cars_urls)
    return car_urls_set


def string_to_isoformatdate(datestring):
    date = parser.parse(datestring)
    isodate = str(date.isoformat())[:-9]
    return isodate


def write_to_file(cars_data):
    with open('cars_data.json', 'w') as fout:
        json.dump(cars_data, fout)
    print("File with the name cars_data.json has been created successfully.")

def convert_to_float(str_value):
    try:
        return float(str_value)
    except ValueError:
        return ""

def num_there(s):
    return any(i.isdigit() for i in s)

def get_single_car_data(car_url):
    car_attributes = {}
    car_attributes_list = ['price', 'depreciation', 'reg_date', 'lifespan', 'manufactured', 'mileage', 'transmission', 'engine_cap', 'road_tax',
                           'power', 'curb_weight', 'features', 'accessories', 'description', 'coe', 'omv', 'arf', 'dereg_value',
                           'no_of_owners', 'type_of_veh', 'category', 'availability', 'depreciation']
    car_integer_attributes = ['no_of_owners', 'manufactured']
    car_float_attributes = ['price', 'coe', 'omv', 'arf']

    cars_page = requests.get(car_url)
    cars_soup = BeautifulSoup(cars_page.content, 'html.parser')

    title_soup = cars_soup.find(class_='link_redbanner')
    if title_soup:
        title = ((''.join(title_soup.findAll(text=True))).strip()).lower()
        car_attributes["title"] = title
    else:
        car_attributes["title"] = ""

    car_attributes["url"] = car_url
    print(car_url)

    image_soup = cars_soup.find("ul", {"id": "gallery"})
    images_list = image_soup.find('table')
    imagerows = images_list.findAll('img')
    for image in imagerows:
        if image['src']:
            car_attributes["image_url"] = image['src']
        else:
            car_attributes["image_url"] = "No image available"

    box = cars_soup.find(class_='box')
    cartable = box.find('table')
    rows = cartable.findAll('tr')
    for row in rows:
        data = row.findAll('td')
        if len(data) > 1:
            feature_key = ((''.join(data[0].findAll(text=True))).strip()).lower()
            feature_value = (((''.join(data[1].findAll(text=True))).strip()).lower())
            if "." in feature_key and " " in feature_key:
                feature_key = feature_key.replace(".", "")
                feature_key = feature_key.replace(" ", "_")
            if " " in feature_key:
                feature_key = feature_key.replace(" ", "_")
            if "." in feature_key:
                feature_key = feature_key.replace(".", "")
            if "$" in feature_value:
                feature_value = feature_value.replace("$", "")
            if "," in feature_value:
                if feature_key == 'category':
                    car_attributes['category'] = feature_value.split(',')
                else:
                    feature_value = feature_value.replace(",", "")
            if feature_key in car_attributes_list:
                if feature_value == '-' or feature_value == '' or feature_value == 'n.a.':
                    car_attributes[feature_key] = ""
                elif feature_key == 'lifespan':
                    car_attributes[feature_key] = string_to_isoformatdate(feature_value)
                elif feature_key == 'reg_date':
                    car_attributes[feature_key] = string_to_isoformatdate(((str(feature_value).split('('))[0]).strip())
                elif feature_key in car_integer_attributes :
                        car_attributes[feature_key] = int(feature_value)
                elif feature_key in car_float_attributes :
                    car_attributes[feature_key] = convert_to_float(feature_value)
                elif feature_key == 'engine_cap':
                    car_attributes[feature_key] = convert_to_float((feature_value.split("c"))[0].strip())
                elif feature_key == 'curb_weight' :
                    car_attributes[feature_key] = convert_to_float((feature_value.split("k"))[0].strip())
                elif feature_key == 'power':
                    car_attributes['power'] = convert_to_float((feature_value.split('(')[1].split('b')[0]).strip())
                elif feature_key == 'road_tax':
                    car_attributes['road_tax'] = convert_to_float((feature_value.split('/')[0]).strip())
                elif feature_key == 'dereg_value':
                    car_attributes['dereg_value'] = convert_to_float((feature_value.split('as')[0]).strip())
                elif feature_key == 'depreciation':
                    car_attributes['depreciation'] = convert_to_float((feature_value.split('/')[0]).strip())
                elif feature_key == 'availability' :
                    if feature_value == 'available':
                       car_attributes[feature_key] = True
                    else:
                       car_attributes[feature_key] = False

                else:
                    car_attributes[feature_key] = feature_value

    usedcar_postdate = box.find("div", {"id": "usedcar_postdate"})
    usedcar_postdate = ((''.join(usedcar_postdate.findAll(text=True))).strip()).lower()
    post_status = usedcar_postdate.split('|')

    posted_on_value = (post_status[0].split(':')[1]).strip()
    posted_on_date_value = string_to_isoformatdate(posted_on_value)
    car_attributes['posted_on'] = posted_on_date_value

    car_attributes['source'] = "sgcarmart"
    car_attributes['valid'] = True

    updated_on_value = (post_status[1].split(':')[1]).strip()
    updated_on_date_value = string_to_isoformatdate(updated_on_value)
    car_attributes['updated_on'] = updated_on_date_value

    #upfront_payment
    upfront_payment = {}
    upfront_payment_soup = cars_soup.find("div", {"id": "upfrontpayment"})
    if upfront_payment_soup:
        upfront_payment_table = upfront_payment_soup.find('table')
        paymentrows = upfront_payment_table.findAll('tr')
        payment_attribute_list = ['transfer_fee', 'down_payment', '1st_instalment', 'total_upfront_payment']
        for row in paymentrows:
            data = row.findAll('td')
            if len(data) > 1:
                payment_key = ((''.join(data[0].findAll(text=True))).strip()).lower()
                payment_value = (((''.join(data[1].findAll(text=True))).strip()).lower())
                if " " in payment_key:
                    payment_key = payment_key.replace(" ", "_")
                if "$" in payment_value:
                    payment_value = payment_value.replace("$", "")
                if "," in payment_value:
                    payment_value = payment_value.replace(",", "")

                if payment_key in payment_attribute_list:
                    if payment_key == 'transfer_fee':
                        if payment_value == '-' or payment_value == '' or payment_value == 'n.a.':
                            upfront_payment[payment_key] = ''
                        else:
                            upfront_payment['transfer_fee'] = float(payment_value)
                    if payment_key == 'down_payment':
                        if payment_value == '-' or payment_value == '' or payment_value == 'n.a.':
                            upfront_payment[payment_key] = ''
                        else:
                            upfront_payment['down_payment'] = float(payment_value.split('(')[0].strip())
                    if payment_key == '1st_instalment':
                        if payment_value == '-' or payment_value == '' or payment_value == 'n.a.':
                            upfront_payment[payment_key] = ''
                        else:
                            upfront_payment['1st_instalment'] = float(payment_value)
                    if payment_key == 'total_upfront_payment':
                        if payment_value == '-' or payment_value == '' or payment_value == 'n.a.':
                            upfront_payment[payment_key] = ''
                        else:
                            upfront_payment['total_upfront_payment'] = float(payment_value.split('(')[0].strip())
            car_attributes["upfront_payment"] = upfront_payment

    #Seller Information
    seller_info = {}
    seller_attribute_list = ['company', 'address', 'office_no', 'contact_persons', 'location', 'contact_no', 'Contact Person(s)']
    contact_persons =[]

    seller_info_soup = cars_soup.find("div", {"id": "sellerinfo"})
    if seller_info_soup:
        sellers_info_table = seller_info_soup.find('table')
        seller_info_rows = sellers_info_table.findAll('tr')
        for row in seller_info_rows:
            seller_data = row.findAll('td')
            if len(seller_data) > 1:
                seller_key = ((''.join(seller_data[0].findAll(text=True))).strip()).lower()
                seller_value = ((''.join(seller_data[1].findAll(text=True))).strip()).lower()

                if " " in seller_key or "." in seller_key:
                    seller_key = seller_key.replace(" ", "_")
                    seller_key = seller_key.replace(".", "")
                if " " in seller_key:
                    seller_key = seller_key.replace(" ", "_")
                if "." in seller_key:
                    seller_key = seller_key.replace(" ", "")

                if " " in seller_key or "(" in seller_key or ")" in seller_key:
                    seller_key = seller_key.replace(" ", "_")
                    seller_key = seller_key.replace("(", "")
                    seller_key = seller_key.replace(")", "")
                if seller_key in seller_attribute_list:
                    if seller_key == 'company':
                        if seller_value == '-' or seller_value == '' or seller_value == 'n.a.':
                            seller_value = ''
                            seller_info['company'] = seller_value
                        elif len(seller_value.split('»')) > 1:
                            seller_info['company'] = seller_value.split('»')[0]
                        else:
                            seller_info['company'] = seller_value
                    elif seller_key == 'contact_persons':
                            for data in seller_data:
                                person = ((''.join(data.findAll(text=True))).strip()).lower()
                                if not num_there(person):

                                    if person != 'contact person(s)':
                                        contact_persons.append(person)
                                else:
                                    contact_persons.append(person)
                                seller_info['contact_persons'] = contact_persons



                    else:
                        seller_info[seller_key] = seller_value
        if 'company' in seller_info:
            seller_info['type'] = 'dealer'
        else:
            seller_info['type'] = 'direct_seller'


        car_attributes['seller_information'] = seller_info
        print(car_attributes)
    return car_attributes

def get_all_cars_data():
    cars_urls = prepare_cars_urls()
    cars_data = []
    for car_url in cars_urls:
        cars_data.append(get_single_car_data(car_url))

    # print(cars_data)
    # write_to_file(cars_data)
    return cars_data

get_single_car_data('http://www.sgcarmart.com/used_cars/info.php?ID=764063&DL=1000')

#http://www.sgcarmart.com/used_cars/info.php?ID=764063&DL=1000

# #prepare_cars_urls()
# cars_data = get_all_cars_data()
# #get_single_car_data('http://www.sgcarmart.com/used_cars/info.php?ID=763736&DL=2351')
#http://www.sgcarmart.com/used_cars/info.php?ID=751428&DL=1194
# mongo_db_operations = MongoDBOperations()
# success, failures = mongo_db_operations.insert_multiple_listings(cars_data)
#
# print("Total records: " + str(len(cars_data)))
# print("Number of records successfully inserted: " + str(success))
# print("Number of records failed to insert: " + str(failures))
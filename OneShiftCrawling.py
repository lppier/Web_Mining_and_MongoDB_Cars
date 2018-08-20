from bs4 import BeautifulSoup
import dateutil.parser as parser
import requests
import json
import re
import locale
from datetime import datetime, timedelta
import time
import random
from MongoDBOperations import MongoDBOperations

BASE_URL = "http://www.oneshift.com/used_cars/listings.php"
DATA_FILE = "data/one_shift_cars_data.json"
CRAWL_PAGE_LIMIT = 20
BATCH_SIZE = 20

car_info_dict = {
    "ad posted": {"name": "posted_on", "type": "date"},
    "availabilty": {"name": "availability", "type": "boolean"},
    "arf": {"name": "arf", "type": "currency"},
    "car category": {"name": "category", "type": "string"},
    "car type": {"name": "type_of_veh", "type": "string"},
    "coe": {"name": "coe", "type": "currency"},
    "colour": {"name": "colour", "type": "string"},
    "dealer company address": {"name": "dealer_company_address", "type": "string"},
    "dealer company name": {"name": "dealer_company_name", "type": "string"},
    "dealer consultant name": {"name": "dealer_consultant_name", "type": "string"},
    "depreciation": {"name": "depreciation", "type": "currency"},
    "description": {"name": "description", "type": "string"},
    "engine cap": {"name": "engine_cap", "type": "float"},
    "manufactured": {"name": "manufactured", "type": "integer"},
    "features": {"name": "features", "type": "string"},
    "fuel type": {"name": "fuel_type", "type": "string"},
    "image_url": {"name": "image_url", "type": "string"},
    "milleage": {"name": "mileage", "type": "float"},
    "no. of owners": {"name": "no_of_owners", "type": "integer"},
    "omv": {"name": "omv", "type": "currency"},
    "reg date": {"name": "reg_date", "type": "date"},
    "renewed coe expiry date": {"name": "renewed_coe_expiry_date", "type": "date"},
    "road tax": {"name": "road_tax", "type": "currency"},
    "selling price": {"name": "price", "type": "currency"},
    "title": {"name": "title", "type": "string"},
    "transmission": {"name": "transmission", "type": "string"},
    "1st installment": {"name": "1st_installment", "type": "currency"},
    "down payment": {"name": "down_payment", "type": "currency"},
    "transfer fee": {"name": "transfer_fee", "type": "currency"},
    "total upfront payment": {"name": "total_upfront_payment", "type": "currency"},
    "url": {"name": "url", "type": "string"},
    "source": {"name": "source", "type": "string"}
}


def process_value(key, value):
    if car_info_dict[key]["type"] == "currency":
        return currency_to_float(value)
    if car_info_dict[key]["type"] == "float":
        return string_to_float(value)
    if car_info_dict[key]["type"] == "integer":
        return string_to_integer(value)
    if car_info_dict[key]["type"] == "date":
        return string_to_isoformatdate(value)
    else:
        return value


def string_to_isoformatdate(datestring):
    if datestring.find("hours ago") > -1:
        hours = int(datestring.replace(" hours ago", ""))
        isodate = (datetime.today() - timedelta(hours=hours)).isoformat()[:10]
    elif datestring.find("days ago") > -1:
        days = int(datestring.replace(" days ago", ""))
        isodate = (datetime.today() - timedelta(days=days)).isoformat()[:10]
    elif datestring.find("yesterday") > -1:
        isodate = (datetime.today() - timedelta(days=1)).isoformat()[:10]
    else:
        date = parser.parse(datestring)
        isodate = str(date.isoformat())[:-9]
    return isodate


def currency_to_float(currency_string):
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    return 0.0 if currency_string == "-" else locale.atof(currency_string.strip("$"))


def string_to_integer(string):
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    return 0 if string == "-" else locale.atoi(string)


def string_to_float(string):
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    return 0.0 if string == "-" else locale.atof(string)


def fetch_cars_links(url):
    cars_page = requests.get(url)
    cars_soup = BeautifulSoup(cars_page.content, 'html.parser')
    cars_elements = cars_soup.select("#wrapper > div.container > div:nth-of-type(4) > div > div")
    urls = []
    for car_element in cars_elements:
        car_link = car_element.select_one(
            "div.col-sm-12.col-xs-12.no-padding.mtop10.mbot10 > div.col-sm-3.col-xs-8 > a")
        if car_link is not None:
            urls.append(car_link["href"])
    return urls


def prepare_cars_urls():
    cars_urls = []
    i = 1
    while i <= CRAWL_PAGE_LIMIT:
        url = "{}?NumPerPages=&pageid={}#listings_top".format(BASE_URL, i)
        print(url)
        cars_urls += fetch_cars_links(url)
        i += 1
    return cars_urls


def fetch_all_cars_data():
    mongo_db_operations = MongoDBOperations()
    cars_urls = prepare_cars_urls()
    cars_data = []

    for car_url in cars_urls:
        time.sleep(random.randint(0, 2))
        car_data = dict()
        try:
            car_data = fetch_cars_data(car_url)
            print("Fetching car listing information from {}".format(car_url))
            cars_data.append(car_data)
        except Exception as ex:
            error_text = str(ex)
            print("An error occurred for the url: " + car_url + ". Details: " + error_text)
            listing_detail = {"url": car_url, "data": car_data}
            mongo_db_operations.insert_crawling_error(listing_detail, error_text)
        finally:
            if len(cars_data) == BATCH_SIZE:
                success, failures = mongo_db_operations.insert_multiple_listings(cars_data)

                print("Total records: " + str(len(cars_data)))
                print("Number of records successfully inserted: " + str(success))
                print("Number of records failed to insert: " + str(failures))
                time.sleep(random.randint(5, 10))
                cars_data = []

    # if any car data is still left
    if len(cars_data) > 0:
        success, failures = mongo_db_operations.insert_multiple_listings(cars_data)

        print("Total records: " + str(len(cars_data)))
        print("Number of records successfully inserted: " + str(success))
        print("Number of records failed to insert: " + str(failures))


def write_to_file(cars_data, filename=DATA_FILE):
    with open(filename, 'w') as fout:
        json.dump(cars_data, fout)
    print("File with the name {} has been created successfully.".format(filename))


def populate_missing_fields(car_info):
    car_info["manufactured"] = car_info["manufactured"] if "manufactured" in car_info else 0
    car_info["arf"] = car_info["arf"] if "arf" in car_info else 0.0
    car_info["power"] = car_info["power"] if "power" in car_info else 0.0
    car_info["curb_weight"] = car_info["curb_weight"] if "curb_weight" in car_info else 0.0
    car_info["accessories"] = car_info["accessories"] if "accessories" in car_info else ""
    car_info["dereg_value"] = car_info["dereg_value"] if "dereg_value" in car_info else 0.0
    car_info["valid"] = True
    return car_info


def fetch_cars_data(url):
    car_page = requests.get(url)
    car_soup = BeautifulSoup(car_page.content, 'html.parser')
    car_element = car_soup.select_one(
        "#wrapper > div.container > div.row.mtop10 > div.col-sm-12.col-xs-12.mtop10 > div.row > div.col-xs-12.col-sm-8 > div.tab-content")

    car_info = dict()
    car_info["title"] = car_element.select_one("div:nth-of-type(1) > div:nth-of-type(1) > h1 > a").text.strip().lower()
    car_info["url"] = url
    car_info["source"] = "oneshift"
    car_info["valid"] = True

    # car image url
    try:
        image_link = car_soup.select_one("#classified_car_photo1 > a > div.large_classified_thumbs")["style"].split()[0]
        car_info["image_url"] = re.search("http:\/\/(.*[^\)])", image_link, re.I).group()
    except TypeError as e:
        car_info["image_url"] = ""

    # specs information
    specs_elements = car_element.select("#spec-table > tbody > tr")

    for element in specs_elements:
        items = element.select("td")
        if len(items) == 2:
            key = items[0].text.strip().lower()

            # exceptions
            if key == "reg date":
                items[1].find("span").extract()
                value = items[1].text.strip()
            elif key == "engine cap":
                value = items[1].text.strip().replace(" cc", "")
            elif key == "milleage":
                value = items[1].text.strip().replace(" km", "")
            elif key == "availabilty":
                value = True if items[1].text.strip().lower() == "available" else False
            elif key == "features":
                values = []
                for val in items[1].find_all("li"):
                    values.append(val.text.strip().lower())
                value = ", ".join(values)
            else:
                value = items[1].text.strip().lower()

            car_info[car_info_dict[key]["name"]] = process_value(key, value)

    # loan information
    loan_elements_keys = car_element.select(".used-car-loan > dl > dt")
    loan_elements_values = car_element.select(".used-car-loan > dl > dd")

    i = 0
    car_info["upfront_payment"] = {}
    for element_key in loan_elements_keys:
        key = element_key.text.strip().replace(":", "").lower()

        # exceptions
        if key == "down payment":
            value = loan_elements_values[i].find("span").text.strip()
        else:
            value = loan_elements_values[i].text.strip()

        car_info["upfront_payment"][car_info_dict[key]["name"]] = process_value(key, value)
        i += 1

    # dealer information
    seller_elements = car_soup.select_one(
        "#wrapper > div.container > div.row.mtop10 > div.col-sm-12.col-xs-12.mtop10 > div.row > div.col-xs-12.col-sm-8 > div:nth-of-type(4)")

    # if this is a direct seller posting
    car_info["seller"] = {}
    if seller_elements.select_one("#seller-contact"):
        seller_contact_persons = []
        for name in seller_elements.select("#seller-contact > div.value"):
            seller_contact_persons.append(name.text.strip())
        car_info["seller"]["contact_persons"] = ", ".join(seller_contact_persons)
        car_info["seller"]["type"] = "direct_seller"
    # if this is a dealer posting
    else:
        consultant_names = []
        for name in seller_elements.select(".consultant-name"):
            consultant_names.append(name.text.strip().lower())

        car_info["seller"]["contact_persons"] = ", ".join(consultant_names)
        car_info["seller"]["dealer_name"] = seller_elements.select_one(".greylinebottom").text.strip().lower()

        dealer_address = []
        for element in seller_elements.select_one(".company-address").contents:
            if element.name == "br":
                dealer_address.append(element.text.strip().replace("\u00A0", " ").lower())
            else:
                dealer_address.append(element.strip().lower())
        car_info["seller"]["dealer_address"] = ", ".join(dealer_address)
        car_info["seller"]["type"] = "dealer"

    # populate missing fields
    return populate_missing_fields(car_info)


if __name__ == "__main__":
    # print(fetch_cars_links(BASE_URL))
    # print(json.dumps(fetch_cars_data("http://www.oneshift.com/used_cars/ads_detail.php?adid=231795"), sort_keys=True,
    #                  indent=4))
    fetch_all_cars_data()

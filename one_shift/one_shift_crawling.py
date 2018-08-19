from bs4 import BeautifulSoup
import dateutil.parser as parser
import requests
import json
import re
import locale

base_url = "http://www.oneshift.com/used_cars/listings.php"

car_info_dict = {
    "ad posted": {"name": "posted_on", "type": "date"},
    "availabilty": {"name": "availability", "type": "boolean"},
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
    "road tax": {"name": "road_tax", "type": "currency"},
    "selling price": {"name": "price", "type": "currency"},
    "title": {"name": "title", "type": "string"},
    "transmission": {"name": "transmission", "type": "string"},
    "1st installment": {"name": "1st_installment", "type": "currency"},
    "down payment": {"name": "down_payment", "type": "currency"},
    "transfer fee": {"name": "transfer_fee", "type": "currency"},
    "total upfront payment": {"name": "total_upfront_payment", "type": "currency"},
    "url": {"name": "url", "type": "string"}
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
    date = parser.parse(datestring)
    isodate = str(date.isoformat())[:-9]
    return isodate


def currency_to_float(currency_string):
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    return locale.atof(currency_string.strip("$"))


def string_to_integer(string):
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    return locale.atoi(string)


def string_to_float(string):
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    return locale.atof(string)


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


def populate_missing_fields(car_info):
    car_info["manufactured"] = 0
    car_info["arf"] = 0.0
    car_info["power"] = 0.0
    car_info["curb_weight"] = 0.0
    car_info["accessories"] = ""
    car_info["dereg_value"] = 0.0
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

    # car image url
    image_link = car_soup.select_one("#classified_car_photo1 > a > div.large_classified_thumbs")["style"].split()[0]
    car_info["image_url"] = re.search("http:\/\/(.*)\.jpg", image_link, re.I).group()

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
                value = True if items[1].text.strip() == "available" else False
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
    dealer_elements = car_soup.select_one(
        "#wrapper > div.container > div.row.mtop10 > div.col-sm-12.col-xs-12.mtop10 > div.row > div.col-xs-12.col-sm-8 > div:nth-of-type(4)")

    car_info["dealer_consultant_name"] = dealer_elements.select_one(".consultant-name").text.strip().lower()
    car_info["dealer_company_name"] = dealer_elements.select_one(".greylinebottom").text.strip().lower()

    dealer_address = []
    for element in dealer_elements.select_one(".company-address").contents:
        if element.name == "br":
            dealer_address.append(element.text.strip().replace("\u00A0", " ").lower())
        else:
            dealer_address.append(element.strip().lower())
    car_info["dealer_company_address"] = ", ".join(dealer_address)

    # populate missing fields
    return populate_missing_fields(car_info)


# print(fetch_cars_links(base_url))

print(json.dumps(fetch_cars_data("http://www.oneshift.com/used_cars/ads_detail.php?adid=241819"), sort_keys=True,
                 indent=4))

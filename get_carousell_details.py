from bs4 import BeautifulSoup
import requests
import re
import urllib.request
import os

### declare constants
SITEMAP_URL = "https://sg.carousell.com/sitemap.xml"
CARS_PATTERN = "cars"
###

def get_urls(base_url, level1, level2, match_pattern = None):
    r = requests.get(base_url)
    xml = r.text

    soup = BeautifulSoup(xml, "lxml")
    level1_tags = soup.find_all(level1)

    required_urls = []
    for level1_tag in level1_tags:
        level2_value = level1_tag.findNext(level2).text
        
        # only consider those URLs that have a specific pattern in the text - if provided
        if match_pattern:
            if re.search(match_pattern, level2_value):
                required_urls.append(level2_value)
        else:
            required_urls.append(level2_value)

    return required_urls

def get_and_insert_car_product_details(car_product_url, insert_into_db):
    """
        Gets the details of the car products and insert in the data base. This method can be run in parallel
    """
    try:
        car_product_details = {}
        r = requests.get(car_product_url, timeout=1)
        html_soup = BeautifulSoup(r.content, "html.parser")
        
        car_product_details["url"] = car_product_url
        
        # Get the image URL
        main_item_image = html_soup.find("img", {"class": "pdt-thumbnail-image.is-active.lazy-image"})
        car_product_details["image_url"] = main_item_image.attr["data-layzr"]
        # main_item_image = html_soup.select_one("")

        insert_into_db(car_product_details)

    except Exception as e:
        print("An error occurred: " + str(e))

def insert_into_db(car_product):
    """ This method needs to be developed to insert the records into the database"""
    if car_product:
        for k in car_product:
            print("{0}: {1}".format(k, car_product[k]))


car_urls = get_urls(SITEMAP_URL, "sitemap", "loc", CARS_PATTERN)
print("Obtained the URL for car products...")
if car_urls and len(car_urls) > 0:
    for car_url in car_urls:
        car_product_urls = get_urls(car_url, "url", "loc")
        print("Obtained the URL of the car products")
        for car_product_url in car_product_urls:
            get_and_insert_car_product_details(car_product_url, insert_into_db)
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


car_urls = get_urls(SITEMAP_URL, "sitemap", "loc", CARS_PATTERN)
if car_urls and len(car_urls) > 0:
    for car_url in car_urls:
        car_products = get_urls(car_url, "url", "loc")

    for car_product in car_products:
        print(car_product)
from bs4 import BeautifulSoup
import requests
import re
import urllib.request
import os

import mongo_db_operations

### declare constants
SITEMAP_URL = "https://sg.carousell.com/sitemap.xml"
CARS_PATTERN = "cars"
USE_TEST_URLs = False
## Put None for no limit and get all values
LIMIT = 10
###

def get_urls(base_url, level1, level2, match_pattern = None):
    """Get the urls from the XML file which are contained inside level1 -> level2 and which match the pattern provided"""
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
        Sample: https://sg.carousell.com/p/suzuki-swift-sport-1-6-manual-178707673/
    """
    try:
        car_product_details = {}
        r = requests.get(car_product_url, timeout=3)
        html_soup = BeautifulSoup(r.content, "html.parser")
        
        car_product_details["url"] = car_product_url
        
        # Get the title
        title_p = html_soup.select("p.ef-b.ef-e")
        if title_p and len(title_p) > 0:
            car_product_details["title"] = title_p[0].text

        # Get the image URL
        main_item_image = html_soup.select("img.pdt-thumbnail-image.is-active.lazy-image")
        # print(main_item_image)
        if main_item_image and len(main_item_image) > 0:
            car_product_details["image_url"] = main_item_image[0]["data-layzr"]
        
        # Get the other details of the car
        detail_divs = html_soup.select("div.ef-_a > div")
        # print(detail_divs)
        if detail_divs and len(detail_divs) > 0:
            for detail_div in detail_divs:
                label_label = detail_div.select("label.ef-c")
                value_p = detail_div.select("p.ef-b.ef-d")
                label_text = ""
                value_text = ""
                if label_label and len(label_label) > 0:
                    label_text = label_label[0].text
                if value_p and len(value_p) > 0:
                    value_text = value_p[0].text
                
                if label_text:
                    car_product_details[label_text] = value_text

        

        insert_into_db(car_product_details)

    except Exception as e:
        print("An error occurred: " + str(e))

def get_test_urls():
    """Get test URLs to test the scraping part"""
    return ["https://sg.carousell.com/p/suzuki-swift-sport-1-6-manual-178707673/"]

def main():
    car_product_urls = []
    if USE_TEST_URLs:
        car_product_urls = get_test_urls()
    else:
        car_urls = get_urls(SITEMAP_URL, "sitemap", "loc", CARS_PATTERN)
        if car_urls and len(car_urls) > 0:
            for car_url in car_urls:
                car_product_urls.extend(get_urls(car_url, "url", "loc"))

    print("Obtained the URL for car products...")
    if car_product_urls and len(car_product_urls) > 0:
        count = 0
        for car_product_url in car_product_urls:
            get_and_insert_car_product_details(car_product_url, mongo_db_operations.insert_into_db)
            count += 1
            if LIMIT and count == LIMIT:
                break

if __name__ == "__main__":
    main()
            
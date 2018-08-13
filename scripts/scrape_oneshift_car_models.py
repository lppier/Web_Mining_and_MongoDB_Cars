from bs4 import BeautifulSoup
import urllib.parse
import requests
import csv

url = "http://www.oneshift.com/used_cars/listings.php"

html_doc = requests.get(url)

soup = BeautifulSoup(html_doc.text, 'html.parser')

manufacturers = []
manufacturer_elements = soup.select("#menuwrapper > div.col-sm-3.no-padding > div:nth-of-type(1) > div.col-xs-6.col-sm-12.center.no-padding > ul > li > ul")

for element in manufacturer_elements:
    for child in element:
        if child.name == "li":
            manufacturer = dict()
            manufacturer["name"] = child.find("a").text
            manufacturer["link"] = "http://www.oneshift.com/used_cars/listings.php?make=" + \
                                   urllib.parse.quote_plus(child.find("a").text)
            manufacturers.append(manufacturer)

manufacturers.pop(0)

models = []

with open('../data/oneshift_car_models.csv', 'w') as myfile:
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    wr.writerow(["manufacturer", "model"])

    for manufacturer in manufacturers:
        print("Scraping", manufacturer["name"], "models")
        html_doc = requests.get(manufacturer["link"])
        soup = BeautifulSoup(html_doc.text, 'html.parser')

        model_elements = soup.select("#menuwrapper > div.col-sm-3.no-padding > div:nth-of-type(2) > div.col-xs-6.col-sm-12.center.no-padding > ul > li > ul")

        for element in model_elements:
            wr.writerow([manufacturer["name"], element.text])

print("Done scraping")

from bs4 import BeautifulSoup
import requests
import csv

url = "http://www.sgcarmart.com/used_cars/listing.php"

html_doc = requests.get(url)

soup = BeautifulSoup(html_doc.text, 'html.parser')

manufacturers = []
manufacturer_elements = soup.find(id="make_attach_menu_child")

for element in manufacturer_elements:
    manufacturer = dict()
    manufacturer["name"] = element.text
    manufacturer["link"] = "http://www.sgcarmart.com/used_cars/" + element["href"]
    manufacturers.append(manufacturer)

manufacturers.pop(0)

models = []

with open('../data/sgcarmart_car_models.csv', 'w') as myfile:
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    wr.writerow(["manufacturer", "model"])

    for manufacturer in manufacturers:
        print("Scraping", manufacturer["name"], "models")

        html_doc = requests.get(manufacturer["link"])
        soup = BeautifulSoup(html_doc.text, 'html.parser')

        model_elements = soup.find(id="model_attach_menu_child")

        for element in model_elements:
            if element.text != "All Models":
                wr.writerow([manufacturer["name"], element.text])

print("Done scraping")

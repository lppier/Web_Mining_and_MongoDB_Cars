from bs4 import BeautifulSoup
import requests
import json

base_url = "http://www.oneshift.com/used_cars/listings.php"


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


def fetch_cars_data(url):
    car_page = requests.get(url)
    car_soup = BeautifulSoup(car_page.content, 'html.parser')
    car_element = car_soup.select_one(
        "#wrapper > div.container > div.row.mtop10 > div.col-sm-12.col-xs-12.mtop10 > div.row > div.col-xs-12.col-sm-8 > div.tab-content")

    car_info = dict()
    car_info["title"] = car_element.select_one("div:nth-of-type(1) > div:nth-of-type(1) > h1 > a").text.strip()

    elements = car_element.select("#spec-table > tbody > tr")

    for element in elements:
        items = element.select("td")
        if len(items) == 2:
            key = items[0].text.strip()

            # exceptions
            if key == "Reg Date":
                items[1].find("span").extract()
                value = items[1].text.strip()
            elif key == "Features":
                values = []
                for val in items[1].find_all("li"):
                    values.append(val.text.strip())
                value = ", ".join(values)
            else:
                value = items[1].text.strip()

            # if currency
            

            car_info[key] = value

    return car_info


# print(fetch_cars_links(base_url))

print(json.dumps(fetch_cars_data("http://www.oneshift.com/used_cars/ads_detail.php?adid=241819"), sort_keys=True,
                 indent=4))

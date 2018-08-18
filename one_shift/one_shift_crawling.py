from bs4 import BeautifulSoup
import requests
import json

base_url = "http://www.oneshift.com/used_cars/listings.php"


def currency_to_float(currency_string):
    from re import sub
    return float(sub(r'[^\d.]', '', currency_string))


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

    # specs information
    specs_elements = car_element.select("#spec-table > tbody > tr")

    for element in specs_elements:
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
            if value.find("$") != -1:
                value = currency_to_float(value)

            car_info[key] = value

    # loan information
    loan_elements_keys = car_element.select(".used-car-loan > dl > dt")
    loan_elements_values = car_element.select(".used-car-loan > dl > dd")

    i = 0
    for element_key in loan_elements_keys:
        key = element_key.text.strip().replace(":", "")

        # exceptions
        if key == "Down Payment":
            value = loan_elements_values[i].find("span").text.strip()
        else:
            value = loan_elements_values[i].text.strip()

        car_info[key] = currency_to_float(value)
        i += 1

    # dealer information
    dealer_elements = car_soup.select_one(
        "#wrapper > div.container > div.row.mtop10 > div.col-sm-12.col-xs-12.mtop10 > div.row > div.col-xs-12.col-sm-8 > div:nth-of-type(4)")

    car_info["Dealer Consultant Name"] = dealer_elements.select_one(".consultant-name").text.strip()
    car_info["Dealer Company Name"] = dealer_elements.select_one(".greylinebottom").text.strip()

    dealer_address = []
    for element in dealer_elements.select_one(".company-address").contents:
        if element.name == "br":
            dealer_address.append(element.text.strip().replace("\u00A0", " "))
        else:
            dealer_address.append(element.strip())
    car_info["Dealer Company Address"] = ", ".join(dealer_address)

    return car_info


# print(fetch_cars_links(base_url))

print(json.dumps(fetch_cars_data("http://www.oneshift.com/used_cars/ads_detail.php?adid=241819"), sort_keys=True,
                 indent=4))

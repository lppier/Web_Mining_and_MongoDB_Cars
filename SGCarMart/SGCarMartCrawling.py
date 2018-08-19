from bs4 import BeautifulSoup
import requests
import re
import dateutil.parser as parser
import json

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
                if feature_value == '-':
                    car_attributes[feature_key] = ""
                elif feature_key == 'lifespan':
                    car_attributes[feature_key] = string_to_isoformatdate(feature_value)
                elif feature_key == 'reg_date':
                    car_attributes[feature_key] = string_to_isoformatdate(((str(feature_value).split('('))[0]).strip())
                elif feature_key in car_integer_attributes :
                        car_attributes[feature_key] = int(feature_value)
                elif feature_key in car_float_attributes :
                    car_attributes[feature_key] = float(feature_value)
                elif feature_key == 'engine_cap':
                    car_attributes[feature_key] = float((feature_value.split("c"))[0].strip())
                elif feature_key == 'curb_weight' :
                    car_attributes[feature_key] = float((feature_value.split("k"))[0].strip())
                elif feature_key == 'power':
                    car_attributes['power'] = float((feature_value.split('(')[1].split('b')[0]).strip())
                elif feature_key == 'road_tax':
                    car_attributes['road_tax'] = float((feature_value.split('/')[0]).strip())
                elif feature_key == 'dereg_value':
                    car_attributes['dereg_value'] = float((feature_value.split('as')[0]).strip())
                elif feature_key == 'depreciation':
                    car_attributes['depreciation'] = float((feature_value.split('/')[0]).strip())
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
        #print(car_attributes)
    return car_attributes

def get_all_cars_data():
    cars_urls = prepare_cars_urls()
    cars_data = []
    for car_url in cars_urls:
        cars_data.append(get_single_car_data(car_url))

    print(cars_data)
    write_to_file(cars_data)
    return cars_data

#prepare_cars_urls()
get_all_cars_data()
#get_single_car_data('http://www.sgcarmart.com/used_cars/info.php?ID=763736&DL=2351')
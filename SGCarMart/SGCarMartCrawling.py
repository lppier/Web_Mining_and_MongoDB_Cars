from bs4 import BeautifulSoup
import requests
import re

base_url = "http://www.sgcarmart.com/used_cars/"

def prepare_cars_urls():
    cars_urls = set()
    match_pattern = "info.php\?[^\" a-z]*"
    index_page = requests.get(base_url+"listing.php")
    soup = BeautifulSoup(index_page.content, 'html.parser')

    for link in soup.find_all('a'):
        if re.search(match_pattern,link.get('href')):
            cars_urls.add(base_url+link.get('href'))
    return cars_urls

def fetch_cars_data():
    #cars_urls = prepare_cars_urls()
    car_attributes ={}
    cars_urls = "http://www.sgcarmart.com/used_cars/info.php?ID=757542&DL=2356"
    #for url in cars_urls:
    cars_page = requests.get(cars_urls)
    cars_soup = BeautifulSoup(cars_page.content, 'html.parser')
    box = cars_soup.find(class_ ='box')
    cartable = box.find('table')
    rows = cartable.findAll('tr')
    #if str(rows[0]).count('strong') == 4:

    print(len(rows))





fetch_cars_data()
#get_all_links()
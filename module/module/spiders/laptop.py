import scrapy
from bs4 import BeautifulSoup
from module.SeleniumRequest import SeleniumRequest
from selenium.webdriver.support import expected_conditions
from selenium import webdriver
from selenium.webdriver.common.by import By
from module.items import LaptopItem

class LaptopSpider(scrapy.Spider):
    name = 'laptop'
    allowed_domains = ['ek.ua']
    BASE_URL = 'https://ek.ua/ua'
    start_urls = ['https://ek.ua/ua/list/298/']

    def start_requests(self):
        for url in self.start_urls:
            yield SeleniumRequest(
                url=url,
                callback=self.parse,
                wait_time=10,
                wait_until=expected_conditions.element_to_be_clickable(
                    (By.CSS_SELECTOR,
                     ".conf-name")
                ),
            )


    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        last_page = int(soup.find(class_="list-pager").find(class_="ib page-num").find_all('a')[-1].getText())
        for i in range(0, last_page):
            yield SeleniumRequest(
                url=f"{self.start_urls[0]}/{i}/",
                callback=self.parse_laptop,
                wait_time=10,
                wait_until=expected_conditions.element_to_be_clickable(
                    (By.CSS_SELECTOR,
                     ".conf-name")
                ),
            )
    def parse_laptop(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        laptop_list = soup.find(id="list_form1").find_all('div')


        for laptop in laptop_list:
            try:
                img_url = laptop.find(class_="list-img h").find('img').get('src')
                model = laptop.find(class_="model-conf-title").find(class_="u").getText()
                price = laptop.find(class_="model-price-range").find_all('span')
                start_price = int(price[0].getText().replace('\xa0',''))
                end_price = int(price[1].getText().replace('\xa0',''))
                conf = []
                conf_html = laptop.find(class_="conf-table").find_all(class_='conf-tr')
                for conf1 in conf_html:
                    conf.append(conf1.find('u').getText())
            except AttributeError:
                continue
            yield LaptopItem(
                model=model,
                start_price=start_price,
                end_price=end_price,
                img_url=img_url,
                image_urls=[img_url],
                configurations=conf
            )
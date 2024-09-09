from time import sleep
import urllib.parse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
# from selenium.webdriver.chrome.service import Service
from webdriver_manager.firefox import GeckoDriverManager
# from webdriver_manager.chrome import ChromeDriverManager

BASE_SLEEP = 3
SMARTPHONE = 'Смартфон'
FEATURES = 'features'
BASE_URL = 'https://www.ozon.ru/category/telefony-i-smart-chasy-15501/?sorting=rating&type=49659' # noqa E501


class SelPhoneParser():
    load_sleep = 4

    def __init__(self):
        service = Service(
            executable_path=GeckoDriverManager().install()
        )
        self.driver = webdriver.Firefox(service=service)

    def quit(self):
        self.driver.quit()

    def open_page(self, url, reload=True):
        self.driver.get(url)
        self.driver.maximize_window()
        sleep(self.load_sleep)
        if reload:
            self.driver.refresh()
            sleep(self.load_sleep)

    def scroll_down(self):
        SCROLL_CMD = 'window.scrollTo(0, document.body.scrollHeight);'
        GET_HEIGHT_CMD = 'return document.body.scrollHeight'

        page_height = self.driver.execute_script(GET_HEIGHT_CMD)
        while True:
            self.driver.execute_script(SCROLL_CMD)
            sleep(self.load_sleep)
            new_height = self.driver.execute_script(GET_HEIGHT_CMD)
            if new_height == page_height:
                break
            page_height = new_height

    def get_products_urls(self):
        products = self.driver.find_elements(
            By.CSS_SELECTOR,
            'div.widget-search-result-container div.o2j_23'
        )
        urls = []
        for product in products:
            product_type = product.find_element(
                By.CSS_SELECTOR, 'span.tsBody400Small font')
            if product_type.text == SMARTPHONE:
                url = product.find_element(
                    By.CSS_SELECTOR, 'a.tile-hover-target')
                url = urllib.parse.urljoin(
                    url.get_attribute('href'), FEATURES)
                urls.append(url)
        return urls

    def get_next_page_url(self):
        return self.driver.find_element(
            By.CSS_SELECTOR,
            'a.e3q.b2113-a0.b2113-b6.b2113-b1'
        ).get_attribute('href')

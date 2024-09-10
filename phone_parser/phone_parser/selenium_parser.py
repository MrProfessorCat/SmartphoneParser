import urllib.parse
from time import sleep
from typing import Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

from phone_parser.css_selectors import (NEXT_BUTTON, PRODUCT_TYPE, PRODUCT_URL,
                                        PRODUCTS_BLOCKS)

SMARTPHONE = 'Смартфон'
FEATURES = 'features'
BASE_URL = 'https://www.ozon.ru/category/telefony-i-smart-chasy-15501/?sorting=rating&type=49659' # noqa E501


class SelPhoneParser():
    # sleep delay in seconds
    load_sleep = 4

    def __init__(self):
        service = Service(
            executable_path=GeckoDriverManager().install()
        )
        self.driver = webdriver.Firefox(service=service)

    def quit(self) -> None:
        """Closing driver"""
        self.driver.quit()

    def open_page(self, url: str, reload: bool = True) -> None:
        """Load page with passed url.
        The page is blocked on first visit. Restart required.
        """
        self.driver.get(url)
        self.driver.maximize_window()
        if reload:
            sleep(self.load_sleep)
            self.driver.refresh()
        wait = WebDriverWait(self.driver, timeout=self.load_sleep)
        wait.until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, PRODUCTS_BLOCKS)
            )
        )

    def scroll_down(self) -> bool:
        """Scrolling page down
        Returns True if the bottom of page is reached,
        otherwise returns False
        """
        SCROLL_CMD = 'window.scrollTo(0, document.body.scrollHeight);'
        GET_HEIGHT_CMD = 'return document.body.scrollHeight'

        page_height = self.driver.execute_script(GET_HEIGHT_CMD)
        self.driver.execute_script(SCROLL_CMD)
        sleep(self.load_sleep)
        new_height = self.driver.execute_script(GET_HEIGHT_CMD)
        return True if new_height == page_height else False

    def get_products_urls(self) -> list[str]:
        """Gathering links to smartphone features
        form loaded page
        """
        products = self.driver.find_elements(
            By.CSS_SELECTOR, PRODUCTS_BLOCKS
        )
        urls = []
        for product in products:
            product_type = product.find_element(By.CSS_SELECTOR, PRODUCT_TYPE)
            if product_type.text == SMARTPHONE:
                url = product.find_element(By.CSS_SELECTOR, PRODUCT_URL)
                url = urllib.parse.urljoin(url.get_attribute('href'), FEATURES)
                urls.append(url)
        return urls

    def get_next_page_url(self) -> Optional[str]:
        """Returns link to the next page"""
        return self.driver.find_element(
            By.CSS_SELECTOR, NEXT_BUTTON
        ).get_attribute('href')

    def get_phones_urls(self, amount: int) -> list[str]:
        """Gathering <amount> links to phones features
        """
        phones_urls = []
        while len(phones_urls) < amount:
            reached_page_bottom = self.scroll_down()
            phones_urls.extend(self.get_products_urls())
            phones_urls = list(set(phones_urls))
            if reached_page_bottom:
                next_page_url = self.get_next_page_url()
                self.open_page(next_page_url, reload=False)
        return phones_urls[:amount]

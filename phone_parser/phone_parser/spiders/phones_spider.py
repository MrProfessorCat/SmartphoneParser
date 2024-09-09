import logging

import scrapy
import urllib.parse

from phone_parser.items import PhoneParserItem
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager


OZON_BASE_URL = 'https://www.ozon.ru'
FEATURES = 'features'

MAX_PHONES_TO_PARSE = 100

SMARTPHONE = 'Смартфон'
MAIN_CHARACTERISTICS = 'Основные'
OPERATING_SYSTEM = 'Операционная система'
VERSION = 'Версия'
NO_VERSION = '(версия не указана)'


# def preload_proxies():
#     data = requests.get(PROXIES_URL)
#     if data.status_code == HTTPStatus.OK:
#         proxies = data.json().get('data')
#         proxies.sort(key=lambda i: i.get('speed'))


class PhonesSpider(scrapy.Spider):
    name = 'phones_spider'
    start_urls = ['https://www.ozon.ru/category/telefony-i-smart-chasy-15501/?sorting=rating&type=49659',] # noqa E501
    phones_num = 0

    def parse(self, response):
        products = response.css(
            'div.widget-search-result-container div.o2j_23'
        )
        for product in products:
            if self.phones_num == MAX_PHONES_TO_PARSE:
                return
            product_type = product.css(
                'span.tsBody400Small font::text').get()
            if product_type == SMARTPHONE:
                url = product.css('a.tile-hover-target::attr(href)').get()
                # following to the page with current phone characteristics
                url = urllib.parse.urljoin(url, FEATURES)
                logging.info(f'{self.phones_num + 1} on parsing -> {url}')
                yield response.follow(
                    url, callback=self.parse_phone,
                    meta={'phone_num': self.phones_num + 1}
                )
                self.phones_num += 1

        next_page = response.css(
            'a.e3q.b2113-a0.b2113-b6.b2113-b1::attr(href)').get()
        if next_page:
            yield response.follow(
                urllib.parse.urljoin(OZON_BASE_URL, next_page),
                callback=self.parse
            )

    def start_requests(self):
        service = Service(executable_path=GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service)
        driver.get('https://www.ozon.ru/category/telefony-i-smart-chasy-15501/?sorting=rating&type=49659') # noqa E501

    def parse_phone(self, response):
        """Parsing page with phone information"""
        # getting phone name
        phone_num = response.meta.get('phone_num')
        phone_name = response.css('a.qm1_27::text').get()
        if not phone_name:
            logging.error(f'{phone_num} failed getting name')
        else:
            phone_name = phone_name.strip().replace('\n', '')
            logging.info(f'{phone_num} got name -> {phone_name}')

        # getting block with characteristics
        characteristics = response.css('div.rk4_27')

        if not characteristics:
            logging.error(
                f'{phone_num} failed getting characteristics section'
            )
        else:
            logging.info(f'{phone_num} got characteristics section')

        # getting all blocks in characteristics block
        blocks = characteristics.css('div.ku6_27')
        if not blocks:
            logging.error(
                f'{phone_num} failed getting characteristics blocks'
            )
        else:
            logging.info(f'{phone_num} got characteristics blocks')

        # searching for block "Основные"
        for block in blocks:
            block_title = block.css('div.uk6_27::text').get()
            if block_title == MAIN_CHARACTERISTICS:
                logging.info(f'{phone_num} main block found')
                break

        # getting all characteristics from block "Основные"
        main_characteristics = block.css('dl.u9k_27')
        if not main_characteristics:
            logging.error(
                (
                    f'{phone_num} failed getting all characteristics '
                    'from main block'
                )
            )
        else:
            logging.info(f'{phone_num} got characteristics from main block')

        # searching for characteristic with name "Операционная система"
        for characteristic in main_characteristics:
            character_name = characteristic.css('span.k9u_27::text').get()
            if character_name == OPERATING_SYSTEM:
                logging.info(f'{phone_num} got OS section')
                operating_system = characteristic.css(
                    'dd.ku9_27::text, a::text').get()
                if not operating_system:
                    logging.error(f'{phone_num} failed getting OS name')
                else:
                    logging.info(
                        f'{phone_num} got OS name -> {operating_system}'
                    )
                break

        # after getting operating system name iterating over
        # main characteristic searching for "Версия {OS_name}"
        for characteristic in main_characteristics:
            character_name = characteristic.css('span.k9u_27::text').get()
            if character_name == f'{VERSION} {operating_system}':
                logging.info(f'{phone_num} got OS version section')
                os_version = characteristic.css(
                    'dd.ku9_27::text, a::text').get()
                if not os_version:
                    logging.error(f'{phone_num} failed getting OS version')
                else:
                    logging.info(f'{phone_num} got OS version -> {os_version}')
                yield PhoneParserItem(
                    {
                        'phone_num': phone_num,
                        'phone_name': phone_name,
                        'url': response.url,
                        'phone_os': os_version
                    }
                )
                break

        # some pages do not contain OS version, but only OS type.
        # In such cases there will be record "<os_type> (версия не указана)"
        else:
            yield PhoneParserItem(
                {
                    'phone_num': phone_num,
                    'phone_name': phone_name,
                    'url': response.url,
                    'phone_os': f'{operating_system} {NO_VERSION}'
                }
            )

import logging
import urllib.parse

import scrapy
from phone_parser.css_selectors import (CHARACTER_NAME, CHARACTER_TITLE,
                                        CHARACTERISTICS_BLOCKS,
                                        MAIN_CHARECTERS, NEXT_BUTTON, OS,
                                        OS_VERSION, PHONE_NAME, PRODUCT_TYPE,
                                        PRODUCT_URL, PRODUCTS_BLOCKS)
from phone_parser.items import PhoneParserItem
from phone_parser.selenium_parser import SelPhoneParser

OZON_BASE_URL = 'https://www.ozon.ru'
START_URL = 'https://www.ozon.ru/category/telefony-i-smart-chasy-15501/?sorting=rating&type=49659' # noqa E501
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
    start_urls = [START_URL,]
    phones_num = 0

    def parse(self, response):
        products = response.css(PRODUCTS_BLOCKS)
        for product in products:
            if self.phones_num == MAX_PHONES_TO_PARSE:
                return
            product_type = product.css(PRODUCT_TYPE).get()
            if product_type == SMARTPHONE:
                url = product.css(PRODUCT_URL).get()
                # following to the page with current phone characteristics
                url = urllib.parse.urljoin(url, FEATURES)
                logging.info(f'{self.phones_num + 1} on parsing -> {url}')
                yield response.follow(
                    url, callback=self.parse_phone,
                    meta={'phone_num': self.phones_num + 1}
                )
                self.phones_num += 1

        next_page = response.css(NEXT_BUTTON).get()
        if next_page:
            yield response.follow(
                urllib.parse.urljoin(OZON_BASE_URL, next_page),
                callback=self.parse
            )

    def parse_phone(self, response):
        """Parsing page with phone information"""
        # getting phone name
        phone_num = response.meta.get('phone_num')
        phone_name = response.css(PHONE_NAME).get()
        if not phone_name:
            logging.error(f'{phone_num} failed getting name')
        else:
            phone_name = phone_name.strip().replace('\n', '')
            logging.info(f'{phone_num} got name -> {phone_name}')

        # getting all blocks in characteristics block
        characteristics_blocks = response.css(CHARACTERISTICS_BLOCKS)
        if not characteristics_blocks:
            logging.error(
                f'{phone_num} failed getting characteristics blocks'
            )
        else:
            logging.info(f'{phone_num} got characteristics blocks')

        # searching for block "Основные"
        for block in characteristics_blocks:
            block_title = block.css(CHARACTER_TITLE).get()
            if block_title == MAIN_CHARACTERISTICS:
                logging.info(f'{phone_num} main block found')
                break

        # getting all characteristics from block "Основные"
        main_characteristics = block.css(MAIN_CHARECTERS)
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
            character_name = characteristic.css(CHARACTER_NAME).get()
            if character_name == OPERATING_SYSTEM:
                logging.info(f'{phone_num} got OS section')
                operating_system = characteristic.css(OS).get()
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
            character_name = characteristic.css(CHARACTER_NAME).get()
            if character_name == f'{VERSION} {operating_system}':
                logging.info(f'{phone_num} got OS version section')
                os_version = characteristic.css(OS_VERSION).get()
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


class SelPhoneSpider(PhonesSpider):
    name = 'sel_phones_spider'

    def start_requests(self):
        sel_parser = SelPhoneParser()
        sel_parser.open_page(START_URL)
        phones_urls = sel_parser.get_phones_urls(MAX_PHONES_TO_PARSE)
        sel_parser.quit()

        logging.info(f'Captured {len(phones_urls)} phones urls')

        for phone_num, url in enumerate(phones_urls, start=1):
            yield scrapy.Request(
                url, callback=self.parse_phone,
                meta={'phone_num': phone_num}
            )

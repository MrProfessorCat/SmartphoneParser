import logging
import requests
from http import HTTPStatus

import scrapy
import urllib

from phone_parser.items import PhoneParserItem

PROXIES_URL = 'https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc' # noqa E501

OZON_BASE_URL = 'https://www.ozon.ru'

MAX_PHONES_TO_PARSE = 100

SMARTPHONE = 'Смартфон'
MAIN_CHARACTERISTICS = 'Основные'
OPERATING_SYSTEM = 'Операционная система'
VERSION = 'Версия'
NO_VERSION = '(версия не указана)'


def preload_proxies():
    data = requests.get(PROXIES_URL)
    if data.status_code == HTTPStatus.OK:
        proxies = data.json().get('data')
        proxies.sort(key=lambda i: i.get('speed'))


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
            url = product.css('a.tile-hover-target::attr(href)').get()
            if product_type == SMARTPHONE:
                logging.info(f'{self.phones_num + 1} on parsing -> {url}')
                yield response.follow(
                    url, callback=self.parse_phone,
                    meta={'phone_num': self.phones_num + 1}
                )
                self.phones_num += 1

        next_page = response.css(
            'a.e3q.b2113-a0.b2113-b6.b2113-b1::attr(href)').get()
        if next_page is not None:
            yield response.follow(
                urllib.parse.urljoin(OZON_BASE_URL, next_page),
                callback=self.parse
            )

    def parse_phone(self, response):
        # no version https://www.ozon.ru/product/samsung-smartfon-galaxy-s23-5g-global-8-512-gb-rozovyy-870152865/?__rr=1 # noqa E501
        # not parsed https://www.ozon.ru/product/poco-smartfon-poco-x6-5g-rostest-eac-12-256-gb-siniy-1388605639/ # noqa E501
        """Parsing page with phone information"""
        # getting phone name
        phone_num = response.meta.get('phone_num')
        phone_name = response.css('h1.m8p_27::text').get()
        if not phone_name:
            logging.error(f'{phone_num} failed getting name')
        logging.info(f'{phone_num} got name -> {phone_name}')
        # getting block with characteristics
        characteristics = response.css('div#section-characteristics')
        if not characteristics:
            logging.error(
                f'{phone_num} failed getting characteristics section'
            )
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
        logging.info(f'{phone_num} got characteristics from main block')
        # searching for characteristic with name "Операционная система"
        for characteristic in main_characteristics:
            character_name = characteristic.css('span.k9u_27::text').get()
            if character_name == OPERATING_SYSTEM:
                logging.info(f'{phone_num} got OS section')
                operating_system = characteristic.css('a::text').get()
                if not operating_system:
                    logging.error(f'{phone_num} failed getting OS name')
                logging.info(f'{phone_num} got OS name')
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
                logging.info(f'{phone_num} got OS version -> {os_version}')
                yield PhoneParserItem(
                    {
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
                    'phone_name': phone_name,
                    'url': response.url,
                    'phone_os': f'{operating_system} {NO_VERSION}'
                }
            )

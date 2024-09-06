import scrapy
import urllib

from phone_parser.items import PhoneParserItem

BASE_URL = 'https://www.ozon.ru'

MAX_PHONES_TO_PARSE = 30

SMARTPHONE = 'Смартфон'
MAIN_CHARACTERISTICS = 'Основные'
OPERATING_SYSTEM = 'Операционная система'


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
                yield response.follow(url, callback=self.parse_phone)
                self.phones_num += 1

        next_page = response.css(
            'a.e3q.b2113-a0.b2113-b6.b2113-b1::attr(href)').get()
        if next_page is not None:
            yield response.follow(
                urllib.parse.urljoin(BASE_URL, next_page),
                callback=self.parse
            )

    def parse_phone(self, response):
        """Parsing page with phone information"""
        # getting block with characteristics
        characteristics = response.css('div#section-characteristics')
        # getting all blocks in characteristics block
        blocks = characteristics.css('div.ku6_27')
        main_block = None
        # searching for block "Основные"
        for block in blocks:
            block_title = block.css('div.uk6_27::text').get()
            if block_title == MAIN_CHARACTERISTICS:
                main_block = block
                break
        if main_block:
            # getting all characteristics from block "Основные"
            main_characteristics = main_block.css('dl.u9k_27')
            # searching for characteristic with name "Операционная система"
            for characteristic in main_characteristics:
                character_name = characteristic.css('span.k9u_27::text').get()
                if character_name == OPERATING_SYSTEM:
                    operating_system = characteristic.css('a::text').get()
                    if operating_system:
                        yield PhoneParserItem({'phone_os': operating_system})
                    else:
                        with open('errors_1.txt', 'a') as erfile:
                            erfile.write(response.url + '\n')
                    break

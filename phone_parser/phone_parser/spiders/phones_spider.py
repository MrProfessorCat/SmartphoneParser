from typing import Iterable
import scrapy


class PhonesSpider(scrapy.Spider):
    name = 'phones_spider'

    def start_requests(self) -> Iterable[scrapy.Request]:
        url = 'https://www.ozon.ru/category/telefony-i-smart-chasy-15501/?sorting=rating' # noqa E501
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for product in response.css('div.widget-search-result-container div'):
            print(product)
            yield {
                'product_type': product.css(
                    'span.tsBody400Small font::text').get(),
                'url': product.css('a.l6j_23::attr(href)').get(),
            }

        # next_page = response.css(
        #     'a.e3q.b2113-a0.b2113-b6.b2113-b1::attr(href)').get()
        # if next_page is not None:
        #     yield response.follow(next_page, callback=self.parse)

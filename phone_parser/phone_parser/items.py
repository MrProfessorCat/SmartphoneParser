# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PhoneParserItem(scrapy.Item):
    phone_name = scrapy.Field()
    url = scrapy.Field()
    phone_os = scrapy.Field()

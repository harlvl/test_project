# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TestItem(scrapy.Item):
    url = scrapy.Field()
    img_urls = scrapy.Field()
    brand = scrapy.Field()
    model = scrapy.Field()
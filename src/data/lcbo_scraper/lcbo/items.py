# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class ListingItem(scrapy.Item):
    name = scrapy.Field()
    price = scrapy.Field()
    prod_url = scrapy.Field()

class ProductItem(scrapy.Item):
    sku = scrapy.Field()
    category = scrapy.Field()
    description = scrapy.Field()
    prod_url = scrapy.Field()
    details = scrapy.Field()

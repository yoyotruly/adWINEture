# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class ProductItem(scrapy.Item):
    wine_id = scrapy.Field()
    name = scrapy.Field()
    seo_name = scrapy.Field()
    type = scrapy.Field()
    region = scrapy.Field()
    country = scrapy.Field()
    winery = scrapy.Field()
    flavor = scrapy.Field()
    structure = scrapy.Field()
    style = scrapy.Field()
    body = scrapy.Field()
    acidity = scrapy.Field()
    ratings_ave = scrapy.Field()
    year = scrapy.Field()
    price = scrapy.Field()


class ReviewItem(scrapy.Item):
    user_id = scrapy.Field()
    rating = scrapy.Field()
    note = scrapy.Field()
    language = scrapy.Field()
    created_at = scrapy.Field()
    wine_id = scrapy.Field()
    year = scrapy.Field()

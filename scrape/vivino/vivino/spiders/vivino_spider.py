import json
import math
import pandas as pd
import scrapy
from scrapy.crawler import CrawlerProcess


class VivinoSpider(scrapy.Spider):
    '''
    add docstring
    '''

    name = 'vivino_spider'

    def __init__(self):
        self.prod_url = 'https://www.vivino.com/api/explore/explore?country_code=CA&currency_code=CAD&min_rating=1&order_by=&order=desc&page={}&price_range_max=500&price_range_min=0&wine_type_ids[]=1&wine_type_ids[]=2&wine_type_ids[]=3&wine_type_ids[]=4'
        self.review_url = 'https://www.vivino.com/api/wines/{}/reviews?year={}&page=%s'
        self.prod_page_num = 1
        self.prod_page_last = None
        self.review_page_num = 1

    def start_requests(self):
        url = self.prod_url.format(self.prod_page_num)
        yield scrapy.Request(url=url, callback=self.parse_product)

    def parse_product(self, response):
        '''
        add docstring
        '''

        data = json.loads(response.body).get('explore_vintage')
        products = data.get('records')

        for product in products:
            print({
                'ratings_ave': products.get('vintage').get('statistics').get('ratings_average'),
                'wine_id': product.get('wine').get('id'),
                'name': product.get('wine').get('name'),
                'seo_name': product.get('wine').get('seo_name'),
                'wine_type': product.get('wine').get('type_id'),
                'region': product.get('wine').get('region'),
                'winery': product.get('wine').get('winery').get('name'),
                'taste': product.get('wine').get('taste'),
                'style': product.get('wine').get('style'),
                'year': product.get('year'),
                'price': product.get('price').get('amount')
            })

        if self.prod_page_num == 1:
            self.prod_page_last = math.ceil(data['records_matched']/25)

        if self.prod_page_num < self.prod_page_last:
            self.prod_page_num += 1
            prod_url_next = self.prod_url.format(self.prod_page_num)
            yield scrapy.Request(url=prod_url_next,
                                 callback=self.parse_product)

        for wine_id, year in wine_id, year:
            review_url = self.review_url.format(wine_id, year) % self.review_page_num
            yield scrapy.Request(url=review_url,
                                 callback=self.parse_review)

    def parse_review(self, response):
        '''
        add docstring
        '''
        reviews = json.loads(response.body).get('reviews')

        for review in reviews:
            print({
                'user_id': review.get('id'),
                'rating': review.get('rating'),
                'note': review.get('note'),
                'language': review.get('language'),
                'created_at': review.get('created_at'),
                'wine_id': review.get('vintage').get('wine').get('id'),
                'year': review.get('vintage').get('year')
            })

        while not reviews:
            self.review_page_num += 1
            review_url_next = self.review_url.format(wine_id, year) % self.review_page_num
            yield scrapy.Request(url=review_url_next,
                                 callback=self.parse_review)


if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(VivinoSpider)
    process.start()

    pd.DataFrame().to_csv('vivino_product.csv', index=False)
    pd.DataFrame().to_csv('vivino_review.csv', index=False)

import json
import math
import re
import scrapy
from scrapy.crawler import CrawlerProcess
from vivino.items import ProductItem, ReviewItem


class VivinoSpider(scrapy.Spider):
    '''
    A web crawler that scrapes vivino.com for red, white, rose and sparkling
    wine information and their corresponding user reviews.
    '''
    name = 'vivino_spider'

    def __init__(self):
        self.prod_url = 'https://www.vivino.com/api/explore/explore?country_code=CA&currency_code=CAD&min_rating=1&order_by=&order=desc&page={}&price_range_max=499&price_range_min=0&wine_type_ids[]=1&wine_type_ids[]=2&wine_type_ids[]=3&wine_type_ids[]=4'
        self.review_url = 'https://www.vivino.com/api/wines/{}/reviews?year={}&page={}'
        self.prod_page_last = 10

    def start_requests(self):
        url = self.prod_url.format(1)
        yield scrapy.Request(url=url, callback=self.parse_product)

    def parse_product(self, response):
        '''
        Extract information about each one and store result in ProductItem.
        Yield scrapy request following individual product url and send response
        to parse_review.
        '''
        data = json.loads(response.body).get('explore_vintage')
        records = data.get('records')

        # extract product information and store result in scrapy item
        for record in records:
            product = ProductItem()
            year = record.get('vintage').get('year')
            wine = record.get('vintage').get('wine')
            wine_id = wine.get('id')

            try:
                product['wine_id'] = wine_id
                product['name'] = wine.get('name')
                product['seo_name'] = wine.get('seo_name')
                product['wine_type'] = wine.get('type_id')
                product['region'] = wine.get('region').get('name')
                product['country'] = wine.get('region').get('country').get('name')
                product['winery'] = wine.get('winery').get('name')
                product['flavor'] = wine.get('taste').get('flavor')
                product['structure'] = wine.get('taste').get('structure')
                product['style'] = wine.get('style').get('name')
                product['body'] = wine.get('style').get('body')
                product['acidity'] = wine.get('style').get('acidity')
                product['ratings_ave'] = record.get('vintage').get('statistics').get('ratings_average')
                product['year'] = year
                product['price'] = record.get('price').get('amount')
            except (AttributeError, KeyError):
                pass

            yield product

            # follow product page url and send response to parse_review
            if year == 'N.V.':
                review_url = self.review_url.format(wine_id, 'null', 1)
            else:
                review_url = self.review_url.format(wine_id, year, 1)
            yield scrapy.Request(url=review_url, callback=self.parse_review)


        # find total number of records matched and calculate max page number
        # (vivino.com uses infinite scrolling, therefore no pagination)
        page_num = int(re.search(r'&page=(.+?)&', response.url).group(1))
        if  page_num == 1:
            records_matched = int(data['records_matched'])
            self.prod_page_last = math.ceil(records_matched / 25)

        # keep following link until reach last page
        if page_num < self.prod_page_last:
            prod_url_next = self.prod_url.format(page_num + 1)
            yield scrapy.Request(url=prod_url_next, callback=self.parse_product)


    def parse_review(self, response):
        '''
        Extract user reviews for each wine and store results in ReviewItem.
        Keep scraping while page content is not empty.
        '''
        reviews = json.loads(response.body).get('reviews')

        for rev in reviews:
            review = ReviewItem()
            review['wine_id'] = rev.get('vintage').get('wine').get('id')
            review['year'] = rev.get('vintage').get('year')
            review['user_id'] = rev.get('id')
            review['rating'] = rev.get('rating')
            review['note'] = rev.get('note')
            review['language'] = rev.get('language')
            review['created_at'] = rev.get('created_at')
            yield review

        if reviews:
            wine_id = re.search(r'wines\/(.+)\/', response.url).group(1)
            year = re.search(r'year=(.+)&', response.url).group(1)
            page_num = int(re.search(r'&page=(\d+)', response.url).group(1))
            review_url_next = self.review_url.format(wine_id, year, page_num + 1)
            yield scrapy.Request(url=review_url_next,
                                 callback=self.parse_review)


if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(VivinoSpider)
    process.start()

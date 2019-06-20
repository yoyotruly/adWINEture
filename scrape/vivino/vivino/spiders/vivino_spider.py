import json
import math
import scrapy
from scrapy.crawler import CrawlerProcess


class VivinoSpider(scrapy.Spider):
    name = 'vivino_spider'
    prod_url = 'https://www.vivino.com/api/explore/explore?country_code=CA&currency_code=CAD&min_rating=1&order_by=&order=desc&page={}&price_range_max=500&price_range_min=0&wine_type_ids[]=1&wine_type_ids[]=2&wine_type_ids[]=3&wine_type_ids[]=4'
    start_urls = [prod_url.format(1)]

    def parse(self, response):
        data = json.loads(response.body)
        max_records = data['explore_vintage']['records_matched']
        records = data['explore_vintage']['records']

        ratings_count =  records['vintage']['statistics']['ratings_count']
        ratings_average = records['vintage']['statistics']['ratings_average']
        wine_id = records['wine']['id']
        wine_name = records['wine']['name']
        wine_seo_name = records['wine']['seo_name']
        wine_type = records['wine']['type_id']
        region = records['wine']['region']['']
        winery = records['wine']['winery']['name']
        taste = records['wine']['taste']
        style = records['wine']['style']
        year = records['year']
        price = records['price']['amount']


        if max_records:
            next_page = data['page'] + 1
            yield scrapy.Request(url=self.prod_url.format(next_page), callback=self.parse)

        for record in records:
            review_url = 'https://www.vivino.com/api/wines/{}/reviews?year={}&page={}'
            yield scrapy.Request(url=review_url.format(wine_id, year, 1),
                                 callback=self.parse_review)

        def parse_review(self, response):
            data = json.loads(response.body)
            max_page = math.ceil(ratings_count/3)
            if page_num <= max_page:
                yield scrapy.Request(url=response.url.format())





if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(VivinoSpider)
    process.start()

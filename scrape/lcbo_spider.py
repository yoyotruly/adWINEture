import re
import numpy as np
import pandas as pd
import scrapy
from scrapy.crawler import CrawlerProcess

listing = {
    'name': [],
    'price': [],
    'prod_url': []
}

product = {
    'url': [],
    'sku': [],
    'category': [],
    'description': [],
    'attributes': [],
    'values': []
}

class LCBOSpider(scrapy.Spider):
    '''
    add docstring
    '''

    name = 'lcbo_spider'

    def __init__(self):
        self.last_page = None

    def start_requests(self):
        urls = [
            'https://www.lcbo.com/webapp/wcs/stores/servlet/en/lcbo/wine-14/red-wine-14001',
            'https://www.lcbo.com/webapp/wcs/stores/servlet/en/lcbo/wine-14/white-wine-14002',
            'https://www.lcbo.com/webapp/wcs/stores/servlet/en/lcbo/wine-14/ros%C3%A9-wine-14003',
            'https://www.lcbo.com/webapp/wcs/stores/servlet/en/lcbo/wine-14/champagne-14004',
            'https://www.lcbo.com/webapp/wcs/stores/servlet/en/lcbo/wine-14/sparkling-wine-14005'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_listing)

    def parse_listing(self, response):
        '''
        add docstrings
        '''

        names = response.css('.product_name a::text').extract()
        prices = response.css('#content .price::text').extract()
        prod_urls = response.css('.product_name a::attr(href)').extract()

        for name in names:
            listing['name'].append(name)

        for price in prices:
            try:
                listing['price'].append(float(re.sub(r'[$|,]', '', price.strip())))
            except ValueError:
                listing['price'].append(np.nan)

        for prod_url in prod_urls:
            if prod_url:
                listing['prod_url'].append(prod_url)
                yield response.follow(url=prod_url, callback=self.parse_product)
            else:
                listing['prod_url'].append(np.nan)

        page_num = int(response.css('#content > div.right.col-md-9.col-xs-12.col-sm-9 > div.productListingWidget > div.header_bar.topFieldBar > div.controls.pagination_present > div.paging_controls > div > div > div > div > a::text').extract_first())

        if page_num == 1:
            last_page_num = int(response.css('.ellipsis+ .hoverover::text').extract_first())
            self.last_page = last_page_num

        if page_num <= self.last_page:
            next_page_url = response.css('#WC_SearchBasedNavigationResults_pagination_link_right_categoryResults::attr(href)').extract_first()
            yield response.follow(url=next_page_url,
                                  callback=self.parse_listing)

    @staticmethod
    def parse_product(response):
        '''
        add docstrings
        '''

        css_extract_first = {
            'sku': '#prodSku span+ span::text',
            'category': '.headingNickname::text',
            'description': '#contentWrapper .hidden-xs::text',
        }
        for key, value in css_extract_first.items():
            product[key].append(response.css(value).extract_first())

        css_extract = {
            'attributes': '.product-details-list b::text',
            'values': '.product-details-list span::text',
        }
        for key, value in css_extract.items():
            product[key].append(response.css(value).extract())

        product['url'].append(response.url)


if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(LCBOSpider)
    process.start()

    pd.DataFrame(listing).to_csv('../data/raw/lcbo_listing.csv', index=False)
    pd.DataFrame(product).to_csv('../data/raw/lcbo_product.csv', index=False)

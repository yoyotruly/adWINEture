"""
This module contains a scrapy spider, which crawls LCBO website's wine section
and stores product scraping results in two csv files.
"""

import re
import numpy as np
import pandas as pd
import scrapy
from scrapy.crawler import CrawlerProcess

LIST = {
    'Name': [],
    'Price': [],
    'Product URL': []
}

PRODUCT = {
    'Product URL': [],
    'SKU': [],
    'Category': [],
    'Description': []
#     'Bottle Size': [],
#     'Alcohol/Vol': [],
#     'Made In': [],
#     'By': [],
#     'Sugar Content': [],
#     'Sweetness Descriptor': [],
#     'Style': [],
#     'Varietal': []
}

class LCBOSpider(scrapy.Spider):
    name = 'lcbo_spider'

    def start_requests(self):
        url = 'https://www.lcbo.com/webapp/wcs/stores/servlet/en/lcbo/wine-14'
        yield scrapy.Request(url=url, callback=self.parse_list)

    def parse_list(self, response):
        names = response.css('.product_name a::text').extract()
        prices = response.css('#content .price::text').extract()
        prod_urls = response.css('.product_name a::attr(href)').extract()

        for name in names:
            LIST['Name'].append(name)

        for price in prices:
            try:
                LIST['Price'].append(float(re.sub(r'[$|,]', '', price.strip())))
            except ValueError:
                LIST['Price'].append(np.nan)

        for prod_url in prod_urls:
            if prod_url:
                LIST['Product URL'].append(prod_url)
                yield response.follow(url=prod_url, callback=self.parse_product)
            else:
                LIST['Product URL'].append(np.nan)

        current_page = int(response.css('#content > div.right.col-md-9.col-xs-12.col-sm-9 > div.productListingWidget > div.header_bar.topFieldBar > div.controls.pagination_present > div.paging_controls > div > div > div > div > a::text').extract_first())
        if current_page <= 831:
            next_page_url = response.css('#WC_SearchBasedNavigationResults_pagination_link_right_categoryResults::attr(href)').extract_first()
            yield response.follow(url=next_page_url, callback=self.parse_list)

    @classmethod
    def parse_product(cls, response):
        sku = response.css('#prodSku span+ span::text').extract_first()
        category = response.css('.headingNickname::text').extract_first()
        description = response.css('#contentWrapper .hidden-xs::text').extract_first()
        # prod_keys = response.css('.product-details-list b::text').extract()
        # prod_values = response.css('.product-details-list span::text').extract()

        PRODUCT['Product URL'].append(response.url)
        if sku:
            PRODUCT['SKU'].append(sku.strip())
        else:
            PRODUCT['SKU'].append(np.nan)
        PRODUCT['Category'].append(category)
        PRODUCT['Description'].append(description)

        # for i in range(len(prod_keys)):
        #     RESULT[prod_keys[i][:-1]].append(prod_values[i])


process = CrawlerProcess()
process.crawl(LCBOSpider)
process.start()


pd.DataFrame(LIST).to_csv('lcbo_list.csv', index=False)
pd.DataFrame(PRODUCT).to_csv('lcbo_product.csv', index=False)

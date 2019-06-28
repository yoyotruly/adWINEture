import re
import numpy as np
import scrapy
from scrapy.crawler import CrawlerProcess
from lcbo.items import ListingItem, ProductItem


def remove_duplicates(seq):
    '''
    Remove duplicates from a sequence while preserving sequence order
    '''
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


class LCBOSpider(scrapy.Spider):
    '''
    A web crawler that crawls LCBO website's red, white, rose, champagne and sparkling wine sections
    '''
    name = 'lcbo_spider'

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
        Extract name, price and individual product url from each page and store
        them in ListingItem. Follow link to next page while page content is not
        empty. Yield scrapy request following each individual product url and
        send response for parse_product to parse.
        '''

        # extract wine name, price and url to product page
        names = response.css('.product_name a::text').extract()
        prices = response.css('#content .price::text').extract()
        prod_urls = response.css('.product_name a::attr(href)').extract()

        if names:  # if page content is not empty

            # store name, price and product url to scrapy item
            for name, price, prod_url in zip(names, prices, prod_urls):
                listing = ListingItem()
                listing['name'] = name
                try:
                    listing['price'] = float(re.sub(r'[$|,]', '', price.strip()))
                except ValueError:
                    listing['price'] = np.nan
                if prod_url:
                    listing['prod_url'] = prod_url
                    yield response.follow(url=prod_url, callback=self.parse_product)
                else:
                    listing['prod_url'] = np.nan
                yield listing

            # extract next page url and follow url to scrawl
            next_page_url = response.css('#WC_SearchBasedNavigationResults_pagination_link_right_categoryResults::attr(href)').extract_first()
            yield response.follow(url=next_page_url,
                                  callback=self.parse_listing)

    @staticmethod
    def parse_product(response):
        '''
        Extract product url, SKU#, category, description and product details
        from product page. Store results in ProductItem.
        '''
        product = ProductItem()
        product['prod_url'] = response.url

        # extract SKU#, category and description, store results to scrapy item
        css_extract_first = {
            'sku': '.brand-details span+ span::text',
            'category': '.headingNickname::text',
            'description': '#contentWrapper .hidden-xs::text',
        }

        for key, value in css_extract_first.items():
            product[key] = response.css(value).extract_first()

        # extract product details list and store results to scrapy item
        css_extract = {
            'attributes': '.product-details-list b::text',
            'values': '.product-details-list span::text',
        }

        details = {}
        for key, value in css_extract.items():
            details[key] = remove_duplicates(response.css(value).extract())
        for att, value in zip(details['attributes'], details['values']):
            details[att] = value
        del details['attributes'], details['values']
        product['details'] = details

        yield product


if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(LCBOSpider)
    process.start()

# -*- coding: utf-8 -*-
import scrapy
import json
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from scraps.items import scrapsItem


class scrapspider(scrapy.Spider):
    name = 'scrapspider'
    Q = None
    site_url = 'https://www.realcommercial.com.au/'
    base_url = "https://www.realcommercial.com.au/for-sale/?includePropertiesWithin=includesurrounding"
    dataset = {}
    isLease = False

    def start_requests(self):
        yield scrapy.Request(self.base_url)

    def parse(self, response):
        js_content = response.xpath(
            '//script[contains(text(),"REA.pageData")]')
        json_str = js_content.re_first(r'REA.pageData\s*=\s*({.*?});')
        json_data = json.loads(json_str)

        url_parts = urlparse(response.url)
        params = parse_qs(url_parts.query)
        if 'page' in params:
            page = int(params['page'][0])
        else:
            page = 1

        minPrice = 0
        if 'minPrice' in params:
            minPrice = int(params['minPrice'][0])

        maxPrice = 0
        if 'maxPrice' in params:
            maxPrice = int(params['maxPrice'][0])

        total = int(json_data['availableResults'])

        items = scrapsItem()

        if len(json_data['exactMatchListings']) == 0:
            return

        list = json_data['exactMatchListings']

        for item in list:
            id = item['id']
            if id not in self.dataset:
                yield scrapy.Request(url=self.site_url + item['pdpUrl'], callback=self.parse_detail)
                item['minPrice'] = minPrice
                item['maxPrice'] = maxPrice
                items['type'] = 1
                items['data'] = item
                self.Q.put(items)
                self.dataset[id] = item
                yield items
            else:
                try:
                    items['type'] = 3

                    if self.dataset[id]['minPrice'] < minPrice:
                        self.dataset[id]['minPrice'] = minPrice

                    if self.dataset[id]['maxPrice'] > maxPrice or self.dataset[id]['maxPrice'] == 0:
                        self.dataset[id]['maxPrice'] = maxPrice

                    items['data'] = {
                        'id': id,
                        'minPrice': self.dataset[id]['minPrice'],
                        'maxPrice': self.dataset[id]['maxPrice'],
                    }

                    # if (self.isLease == True and minPrice + 1000 <= maxPrice) or (self.isLease == False and minPrice + 5000 <= maxPrice):
                    self.Q.put(items)

                    yield items
                except Exception as e:
                    # Handle other exceptions (generic Exception class)
                    print("An error occurred")
                    print(f"Error details: {e}")

        next_page_num = page + 1
        params['page'] = next_page_num
        # Encode the modified query parameters
        next_page_query = urlencode(params, doseq=True)
        next_page_url = urlunparse((
            url_parts.scheme,
            url_parts.netloc,
            url_parts.path,
            url_parts.params,
            next_page_query,
            url_parts.fragment
        ))

        if maxPrice == 0:
            if self.isLease == True:
                maxPrice = 2000000
            else:
                maxPrice = 100000000

        if next_page_num <= 30 and page * 10 < total:
            yield scrapy.Request(url=next_page_url, callback=self.parse)
        else:
            if self.isLease == True and minPrice + 1000 > maxPrice:
                return
            if self.isLease == False and minPrice + 5000 > maxPrice:
                return
            middle = int((minPrice + maxPrice) / 2)
            params['minPrice'] = minPrice
            params['maxPrice'] = middle
            params['page'] = 1
            # Encode the modified query parameters
            modified_query = urlencode(params, doseq=True)

            # Reconstruct the modified URL
            modified_url = urlunparse((
                url_parts.scheme,
                url_parts.netloc,
                url_parts.path,
                url_parts.params,
                modified_query,
                url_parts.fragment
            ))
            yield scrapy.Request(url=modified_url, callback=self.parse)

            params['minPrice'] = middle + 1
            params['maxPrice'] = maxPrice
            modified_query = urlencode(params, doseq=True)

            # Reconstruct the modified URL
            modified_url = urlunparse((
                url_parts.scheme,
                url_parts.netloc,
                url_parts.path,
                url_parts.params,
                modified_query,
                url_parts.fragment
            ))
            yield scrapy.Request(url=modified_url, callback=self.parse)

        # elif self.jobtype == 2:

    def parse_detail(self, response):
        js_content = response.xpath(
            '//script[contains(text(),"REA.pageData")]')
        json_str = js_content.re_first(r'REA.pageData\s*=\s*({.*?});')
        json_data = json.loads(json_str)
        data = json_data['listing']

        items = scrapsItem()
        items['type'] = 2
        items['data'] = data
        self.Q.put(items)

        yield data

    def close(spider, reason):
        spider.Q.put('采集结束')

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
    priceRanged = []
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

        list = json_data['exactMatchListings']
        if params['includePropertiesWithin'][0] == 'includesurrounding':
            list += json_data['surroundingSuburbListings']

        if len(list) == 0:
            return

        for item in list:
            id = item['id']
            if id not in self.dataset:
                yield scrapy.Request(url=self.site_url + item['pdpUrl'], callback=self.parse_detail)
                item['minPrice'] = minPrice
                item['maxPrice'] = maxPrice
                items['type'] = 1
                items['data'] = item
                self.Q.put(items)
                item['rangeType'] = 0
                self.dataset[id] = item
                yield items
            else:
                try:
                    items['type'] = 3

                    item = self.dataset[id]
                    maxold = item['maxPrice']
                    minold = item['minPrice']

                    if (maxPrice > 0 and maxPrice < minold) or (maxold > 0 and maxold < minPrice):
                        item['rangeType'] = 1

                    if (item['rangeType'] == 1):
                        self.dataset[id]['minPrice'] = min(minold, minPrice)
                        if maxold == 0 or maxPrice == 0:
                            self.dataset[id]['maxPrice'] = 0
                        else:
                            self.dataset[id]['maxPrice'] = max(
                                maxold, maxPrice)
                    else:
                        self.dataset[id]['minPrice'] = max(minold, minPrice)
                        if maxold == 0 or maxPrice == 0:
                            self.dataset[id]['maxPrice'] = max(
                                maxold, maxPrice)
                        else:
                            self.dataset[id]['maxPrice'] = min(
                                maxold, maxPrice)

                    if (self.dataset[id]['minPrice'] != minold or self.dataset[id]['maxPrice'] != maxold):
                        # if (bShow):
                        # print(
                        #     f'{minold} - {maxold} -> {self.dataset[id]["minPrice"]} - {self.dataset[id]["maxPrice"]}')
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

        if next_page_num <= 30 and page * 10 < total:
            yield scrapy.Request(url=next_page_url, callback=self.parse)
        elif total > 0:
            if self.isLease == True and (maxPrice >= 2000000 or (minPrice + max(maxPrice / 100, 1000) > maxPrice and maxPrice > 0)):
                return
            if self.isLease == False and (maxPrice >= 100000000 or (minPrice + max(maxPrice / 100, 5000) > maxPrice and maxPrice > 0)):
                return

            if maxPrice == 0:
                if self.isLease == True:
                    middle = 2000000
                else:
                    middle = 100000000
            else:
                middle = int((minPrice + maxPrice) / 2)

            if (minPrice >= middle):
                return

            params['minPrice'] = minPrice
            params['maxPrice'] = middle - 1
            # params['includePropertiesWithin'] = 'excludesurrounding'
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
            # print(f'new scrap {params["minPrice"]} - {params["maxPrice"]}')

            params['minPrice'] = middle
            params['maxPrice'] = maxPrice
            # params['includePropertiesWithin'] = 'excludesurrounding'
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
            # print(f'new scrap {params["minPrice"]} - {params["maxPrice"]}')

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

    def close(self, reason):
        items = scrapsItem()
        items['type'] = 4
        self.Q.put(items)

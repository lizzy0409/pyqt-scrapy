# -*- coding: utf-8 -*-
import scrapy
import json
from urllib.parse import urlparse, parse_qs
from scraps.items import scrapsItem


class scrapspider(scrapy.Spider):
    name = 'scraps'
    allowed_domains = ['scraps.toscrape.com']
    Q = None
    base_url = "https://www.realcommercial.com.au/for-sale/?includePropertiesWithin=includesurrounding"

    def start_requests(self):
        # self.Q.put('开始采集')
        for page_num in range(1, 51):
            url = self.base_url + f"&page={page_num}"
            yield scrapy.Request(url)

    def parse(self, response):
        js_content = response.xpath('//script[contains(text(),"REA.pageData")]')
        json_str = js_content.re_first(r'REA.pageData\s*=\s*({.*?});')
        json_data = json.loads(json_str)

        url_parts = urlparse(response.url)
        params = parse_qs(url_parts.query)
        if 'page' in params:
            page = int(params['page'][0])
        else:
            page = 1

        total = int(json_data['availableResults'])

        items = scrapsItem()

        for item in json_data['exactMatchListings']:
            items['id'] = item['id']
            items['title'] = item['title']
            items['agency_company'] = item['agencies'][0]['name']
            items['url'] = item['pdpUrl']
            items['street'] = item['address']['streetAddress']
            items['suburb'] = item['address']['suburbAddress']
            items['price'] = item['details']['price']
            items['area'] = item['attributes']['area']
            items['property'] = ", ".join(item['attributes']['propertyTypes'])
            self.Q.put(items)
            yield items

        next_page_num = page + 1
        next_page_url = self.base_url + f'&page={next_page_num}'

        if next_page_num < 50 and page * 10 < total:
            yield scrapy.Request(url=next_page_url, callback=self.parse)

    def close(spider, reason):
        spider.Q.put('采集结束')

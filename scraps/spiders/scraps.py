# -*- coding: utf-8 -*-
import scrapy
import json
from urllib.parse import urlparse, parse_qs
from scraps.items import scrapsItem


class scrapspider(scrapy.Spider):
    name = 'scrapspider'
    Q = None
    site_url = 'https://www.realcommercial.com.au/'
    base_url = "https://www.realcommercial.com.au/for-sale/?includePropertiesWithin=includesurrounding"

    def start_requests(self):
        # self.Q.put('开始采集')
        for page_num in range(1, 2):
            url = self.base_url + f"&page={page_num}"
            yield scrapy.Request(url)

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

        total = int(json_data['availableResults'])

        items = scrapsItem()
        items['type'] = 1

        for item in json_data['exactMatchListings']:
            items['data'] = item
            # yield scrapy.Request(url=self.site_url + item['pdpUrl'], callback=self.parse_detail)
            self.Q.put(items)
            yield items

        next_page_num = page + 1
        next_page_url = self.base_url + f'&page={next_page_num}'

        if next_page_num <= 50 and page * 10 < total:
            yield scrapy.Request(url=next_page_url, callback=self.parse)

    def parse_detail(self, response):
        js_content = response.xpath(
            '//script[contains(text(),"REA.pageData")]')
        json_str = js_content.re_first(r'REA.pageData\s*=\s*({.*?});')
        json_data = json.loads(json_str)

        yield json_data

    def close(spider, reason):
        spider.Q.put('采集结束')

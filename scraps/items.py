# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class scrapsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    title = scrapy.Field()
    agency_company = scrapy.Field()
    url = scrapy.Field()
    street = scrapy.Field()
    suburb = scrapy.Field()
    price = scrapy.Field()
    area = scrapy.Field()
    property = scrapy.Field()
    # pass

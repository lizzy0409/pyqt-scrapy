# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json


class scrapsPipeline(object):
    def process_item(self, item, spider):
        return item


class ChanelPipeline(object):
    def __init__(self, location):
        self.file = open(location, 'a', encoding='utf-8')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            location=crawler.settings.get('SAVE_CONTENT'),
        )

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        # print('数据保存至本地成功')
        # spider.Q.put('数据保存至本地成功')
        return item

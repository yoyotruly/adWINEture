# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import time
from scrapy.exporters import CsvItemExporter

class VivinoPipeline(object):

    CSVPath = '../../data/raw/vivino_'
    DownloadDate = time.strftime('%Y%m%d')
    SaveTypes = ['product', 'review']

    def __init__(self):
        self.files = dict([(name, open('{}{}_{}.csv'.format(self.CSVPath, name, self.DownloadDate), 'w+b')) for name in self.SaveTypes])
        self.exporters = dict([(name, CsvItemExporter(self.files[name])) for name in self.SaveTypes])

    def spider_opened(self, spider):
        for exp in self.exporters.values():
            exp.start_exporting()

    def spider_closed(self, spider):
        for exp in self.exporters.values():
            exp.finish_exporting()
        for fil in self.files.values():
            fil.close()

    def process_item(self, item, spider):
        item_name = type(item).__name__.replace('Item', '').lower()
        if item_name in set(self.SaveTypes):
            self.exporters[item_name].export_item(item)
        return item

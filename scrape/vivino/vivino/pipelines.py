# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exporters import CsvItemExporter

class VivinoPipeline(object):

    CSVPath = '../../data/raw/vivino_'
    SaveTypes = ['product', 'review']

    def __init__(self):
        self.files = dict([(name, open(self.CSVPath + name + '.csv', 'w+b')) for name in self.SaveTypes])
        self.exporters = dict([(name, CsvItemExporter(self.files[name])) for name in self.SaveTypes])

    def spider_opened(self, spider):
        for exporter in self.exporters.values():
            exporter.start_exporting()

    def spider_closed(self, spider):
        for exporter in self.exporters.values():
            exporter.finish_exporting()
        for file in self.files.values():
            file.close()

    def process_item(self, item, spider):
        item_name = type(item).__name__.replace('Item', '').lower()
        if item_name in set(self.SaveTypes):
            self.exporters[item_name].export_item(item)
        return item

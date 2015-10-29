# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

#Items will contain BASE data from XMLs
class BaseDataItems(scrapy.Item):
    creator = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    language = scrapy.Field()
    date = scrapy.Field()
    classcode = scrapy.Field()
    autoclasscode = scrapy.Field()
    collname = scrapy.Field()
    identifier = scrapy.Field()
    relation = scrapy.Field()
    link = scrapy.Field()
    typenorm = scrapy.Field()
    contributor = scrapy.Field()
    year = scrapy.Field()
    datestamp = scrapy.Field()
    doctype = scrapy.Field()
    pdf_url = scrapy.Field()

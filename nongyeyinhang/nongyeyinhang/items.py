# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NongyeyinhangItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    publish_date = scrapy.Field()
    scrapy_link = scrapy.Field();
    goto_link = scrapy.Field();
    scrapy_id = scrapy.Field();
    created_time = scrapy.Field()
    pass

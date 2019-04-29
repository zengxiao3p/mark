# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BiaoshuItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title=scrapy.Field()
    win_bid_money=scrapy.Field()
    bid_publish_date=scrapy.Field()
    create_date=scrapy.Field()
    snapshort_html=scrapy.Field()
    goto_link=scrapy.Field()
    announcemen_type=scrapy.Field()
    budget=scrapy.Field()
    tenderee=scrapy.Field()
    win_bid_tenderee=scrapy.Field()
    original_link=scrapy.Field()
    bid_start_date=scrapy.Field()

    #source name
    source_name=scrapy.Field()
    #bankname
    bank_name=scrapy.Field()
    #省份
    province=scrapy.Field()
    #关键字
    key_word=scrapy.Field()

    pass

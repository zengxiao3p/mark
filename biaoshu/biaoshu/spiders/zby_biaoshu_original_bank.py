# -*- coding: utf-8 -*-

from biaoshu.items import BiaoshuItem
from biaoshu.settings import COOKIES_FILE_PATH
import scrapy
import json
import urllib.parse
class ToScrapeCSSSpider(scrapy.Spider):
    def __init__(self, weixinName=None, *args, **kwargs):
        self.cookies_file_path=COOKIES_FILE_PATH
        super(ToScrapeCSSSpider, self).__init__(*args, **kwargs)

    name = "zby_biaoshu_original_bank"
    allowed_domains = ['data.wxb.com','www.jianyu360.com','zhongbiaoyi.com']
    custom_settings = {
        'ITEM_PIPELINES': {'biaoshu.pipelines.BiaoshuPipeline': 301}
    }
    def get_browser_cookies(self):
        cookies = {}
        with open(self.cookies_file_path, 'r') as f:
            temp=f.read()
            if temp !='':
                listCookie = json.loads(temp)
                # cookies格式转换
                for Cookie in listCookie:
                    name = Cookie.get('name')
                    value = Cookie.get('value')
                    cookies[name] = value
        return  cookies
    #银行+关键字
    def start_requests(self):
        title_cycle = ['IT', '信息', '数据', '风控', '规划', '智慧银行']

        tempStore = [
            ['中国银行'],
            ['工商银行'],
            ['农业银行'],
            ['建设银行'],
            ['交通银行'],
            ['民生银行'],
            ['广发银行'],
            ['广州银行'],
            ['招商银行'],
            ['平安银行'],
            ['浦发银行'],
            ['邮储银行'],
            ['农商行']
        ]
        for i in tempStore:
            everyUrl = 'https://www.zhongbiaoyi.com/vip/search.php'
            for j in title_cycle:
                yield scrapy.Request(url=everyUrl, callback=self.parse, cookies=self.get_browser_cookies(),
                                     meta={'bank_name': i[0], 'title': j, 'retry_times':
                                         True, 'detail_innerHtml': False}, dont_filter=True)

    def parse(self, response):
        itemlist  = response.request.meta['itemlist']
        if (len(response.request.meta['itemlist'])>0):
            for item in itemlist:
               baioshuItem = BiaoshuItem()
               iteml=list(item.keys())
               for key in iteml:
                   baioshuItem[key] =item[key]
               baioshuItem['source_name']=response.request.meta['bank_name']+'_'+response.request.meta['title']
               baioshuItem['bank_name'] =response.request.meta['bank_name']
               baioshuItem['key_word']=response.request.meta['bank_name']+'_'+response.request.meta['title']

               baioshuItem['win_bid_money']=None
               baioshuItem['goto_link']=None
               baioshuItem['budget']=None
               baioshuItem['tenderee']=None
               baioshuItem['win_bid_tenderee']=None
               baioshuItem['bid_start_date']=None
               yield baioshuItem


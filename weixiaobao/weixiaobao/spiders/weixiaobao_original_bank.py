# -*- coding: utf-8 -*-

from weixiaobao.items import WeixiaobaoItem
from weixiaobao.settings import COOKIES_FILE_PATH
import scrapy
import json
class ToScrapeCSSSpider(scrapy.Spider):
    def __init__(self, weixinName=None, *args, **kwargs):
        self.cookies_file_path=COOKIES_FILE_PATH
        super(ToScrapeCSSSpider, self).__init__(*args, **kwargs)

    name = "weixiaobao_original_bank"
    allowed_domains = ['data.wxb.com']
    custom_settings = {
        'ITEM_PIPELINES': {'weixiaobao.pipelines.WeixiaobaoPipeline': 301}
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
    #银行+公众代码
    def start_requests(self):
        tempStore = [
            ['农商银行', '清远农商银行Qing金融'],
            ['农商银行', 'qingbankcn'],
            ['招商银行', 'cmbchina-95555'],
            ['平安银行', 'pingan_bank'],
            ['中信银行', 'CITICBANKCHINA'],
            ['光大银行', 'cebbank_95595'],
            ['浦发银行', 'WE95528'],
            ['民生银行', 'cmbcwxbank'],
            ['广州银行', 'BANK-OF-GUANGZHOU'],
            ['华夏银行', 'hxwxgzzh'],
            ['北京银行', 'WX95526'],
            ['交通银行', 'Bank-95559'],
            ['中国银行', 'bankofchina2016'],
            ['工商银行', 'icbcqy'],
            ['中国建设银行', 'CCB_elutong']
                     ]
        for i in tempStore:
            everyUrl = 'https://data.wxb.com/searchResult?kw={source_name}&page=1'

            yield scrapy.Request(url=everyUrl.format(source_name=i[1]), callback=self.parse,cookies=self.get_browser_cookies(),
                             meta={'theme_name':i[0],'source_name': i[1], 'retry_times': True}, dont_filter=True)


    def parse(self, response):
        for showcss in response.css('tbody>tr'):
            every = showcss.css('td:first-child>div.near-article-title>a')
            item = WeixiaobaoItem()
            item['goto_link'] =   every.css('::attr("href")').extract_first()
            item['title'] = every.css('::text').extract_first().strip()
            item['publish_date'] = showcss.css('td')[1].css('::text').extract_first()
            item['scrapy_link'] = response.meta['wxsgGzhDetailUrl']
            item['theme_name'] = response.meta['theme_name']
            item['source_name'] = response.meta['source_name']
            yield item


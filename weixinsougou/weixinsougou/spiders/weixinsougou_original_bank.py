# -*- coding: utf-8 -*-

from weixinsougou.items import WeixinsougouItem
from weixinsougou.settings import COOKIES_FILE_PATH
import scrapy
import json
class ToScrapeCSSSpider(scrapy.Spider):
    def __init__(self, weixinName=None, *args, **kwargs):
        self.cookies_file_path=COOKIES_FILE_PATH
        super(ToScrapeCSSSpider, self).__init__(*args, **kwargs)

    name = "wxsg_original_bank"
    allowed_domains = ['weixin.sogou.com']
    custom_settings = {
        'ITEM_PIPELINES': {'weixinsougou.pipelines.WeixinsougouPipeline': 301}
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

    def start_requests(self):
        tempStore = [['农商银行', '清远农商银行Qing金融'], ['广发银行', '广发银行清远分行'], ['中国银行', '中国银行'], ['农业银行', '中国农业银行广东清远分行']]
        for i in tempStore:
            everyUrl = 'https://weixin.sogou.com/weixin?query={source_name}&_sug_type_=&s_from=input&_sug_=n&type=1&page=1&ie=utf8'
            yield scrapy.Request(url=everyUrl.format(source_name=i[1]), callback=self.parse,cookies=self.get_browser_cookies(),
                             meta={'theme_name':i[0],'source_name': i[1], 'retry_times': True}, dont_filter=True,headers=[])


    def parse(self, response):
        for showcss in response.css('div.weui_msg_card_list>div.weui_msg_card'):
            item = WeixinsougouItem()
            item['goto_link'] = 'http://mp.weixin.qq.com' + showcss.css('div.weui_msg_card_bd>div>div.weui_media_bd>h4::attr("hrefs")').extract_first();
            item['title'] = showcss.css('div.weui_msg_card_bd>div>div.weui_media_bd>h4::text').extract_first().strip()
            item['publish_date'] = showcss.css('div.weui_msg_card_hd::text').extract_first().replace('年', '-').replace('月', '-') \
                .replace('日', '')
            item['scrapy_link'] = response.meta['wxsgGzhDetailUrl']
            item['theme_name'] = response.meta['theme_name']
            item['source_name'] = response.meta['source_name']
            yield item


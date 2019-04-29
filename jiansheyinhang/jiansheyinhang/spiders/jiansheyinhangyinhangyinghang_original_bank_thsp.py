# -*- coding: utf-8 -*-
import scrapy

from jiansheyinhang.items import JiansheyinhangItem

scrapy_link = 'http://creditcard.ccb.com/webtran/get_crd_info.gsp?table_type=2&card_province=1020&card_city=196&startNum=1&endNum=10'

domain = "creditcard.ccb.com"

import json
import math


class ToScrapeCSSSpider(scrapy.Spider):
    def __init__(self):
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'Cookie': 'usid=fnFeAPaifI4Nyp08; IPLOC=CN4401; SUV=00650FC577216661593EA9278FFA6462; CXID=0872E4A4B5DAAC714C65FAFCB269D53F; SNUID=3ECA73C2757122A81EF12DFA7555397A; ad=Oyllllllll2BDXLJlllllVoxNtclllllNhV6$lllll9lllllxCxlw@@@@@@@@@@@; SUID=616621773765860A593EB4B100044187; ABTEST=7|1510564866|v1;weixinIndexVisited=1 ',
        }

    name = "jsyh_original_bank_thsp"
    allowed_domains = [domain]
    start_urls = [
        scrapy_link,
    ]
    custom_settings = {
        'ITEM_PIPELINES': {'jiansheyinhang.pipelines.JiansheyinhangThspPipeline': 301}
    }

    def parse(self, response):
        # 求取共几页
        try:
            obj = json.loads(response.text.strip())
            everyPageNum = 10
            totalNum = int(obj.get('totalNum'))
            shang = math.floor(totalNum / everyPageNum)
            mu = 0
            if (totalNum % everyPageNum > 0):
                mu = 1
            pagesize = shang + mu
            currentpage = math.floor(int(response._url.strip().split('&endNum=')[1]) / everyPageNum)
            currentpage = int(currentpage);
            startNum = 1 + ((currentpage - 1) * 10)
            endNum = currentpage * 10
            for showcss in obj.get('obj'):
                item = JiansheyinhangItem()
                item['title'] = showcss['biz_cmsg']
                item['goto_link']='http://creditcard.ccb.com/cn/creditcard/favorable/'+showcss['biz_id']+".html"
                item['scrapy_link'] = "http://creditcard.ccb.com/webtran/get_crd_info.gsp?table_type=2&card_province=1020&card_city=196&startNum="+str(startNum)+"&endNum="+str(endNum)

                yield item

            if currentpage < pagesize:
                nextpage = int(currentpage) + 1
                nextStartNum = 1 + ((nextpage - 1) * 10)
                nextEndNum = nextpage * 10
                next_page_url = "http://creditcard.ccb.com/webtran/get_crd_info.gsp?table_type=2&card_province=1020&card_city=196&startNum="+str(nextStartNum)+"&endNum="+str(nextEndNum)
                request = scrapy.Request(response.urljoin(next_page_url))
                request.meta['item'] = item
                yield request
        except IOError as e:
            print('error', e)

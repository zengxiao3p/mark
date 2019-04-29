# -*- coding: utf-8 -*-
import scrapy

from guangfayinhang.items import GuangfayinhangItem

scrapy_link = 'http://www.cgbchina.com.cn/Channel/12218744'

domain = "cgbchina.com.cn"


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

    name = "guangfayinhang_original_bank_yhhd"
    allowed_domains=[domain]
    start_urls = [
        scrapy_link,
    ]
    custom_settings = {
        'ITEM_PIPELINES': {'guangfayinhang.pipelines.GuangfayinhangPipeline': 301}
    }

    def parse(self, response):
        #求取共几页
        try:
            for showcss in response.css('div.textContent >div.listContent>ul>li'):
                item = GuangfayinhangItem()
                item['title'] = showcss.css('li>a::text').extract_first()
                item['publish_date'] = showcss.css('li>span::text').extract_first()
                if (showcss.css('li>a::attr("href")').extract_first().startswith( 'http' )==False):
                    item['goto_link'] = "http://www.cgbchina.com.cn/" +showcss.css('li>a::attr("href")').extract_first()
                else:
                    item['goto_link'] = showcss.css('li>a::attr("href")').extract_first()
                item['scrapy_link'] = scrapy_link
                yield item
        except IOError as e:
            print('error')
# -*- coding: utf-8 -*-
import scrapy

from huaxiayinhang.items import HuaxiayinhangItem

scrapy_link = 'http://www.hxb.com.cn/jrhx/khfw/yhkx/index.shtml'

domain = "www.hxb.com.cn"


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

    name = "hxyh_original_bank_yhkx"
    allowed_domains = [domain]
    start_urls = [
        scrapy_link,
    ]
    custom_settings = {
        'ITEM_PIPELINES': {'huaxiayinhang.pipelines.HuaxiayinhangPipeline': 301}
    }

    def parse(self, response):
        # 求取共几页
        try:
            pagesize = response.css('li.pro_la::text')[0].extract().split('/')[1]
            pagesize = int(pagesize)
            for showcss in response.css('div.pro_contlist> ul>li[flag="1"]'):
                currentpage = response.css('li.pro_la::text')[0].extract().split('/')[0]
                currentpage = int(currentpage);
                item = HuaxiayinhangItem()
                item['title'] = showcss.css('a>span')[0].css('::text').extract_first()
                item['publish_date'] = showcss.css('a>span')[1].css('::text').extract_first().strip()
                if (showcss.css('a::attr("href")').extract_first().startswith('http') == False):
                    item['goto_link'] = "http://www.hxb.com.cn/" +showcss.css('a::attr("href")').extract_first()
                else:
                    item['goto_link'] = showcss.css('a::attr("href")').extract_first()
                if currentpage == 1:
                    item['scrapy_link'] = "http://www.hxb.com.cn/jrhx/khfw/yhkx/index.shtml"
                else:
                    item['scrapy_link'] = "http://www.hxb.com.cn/jrhx/khfw/yhkx/index_" + str(currentpage) + ".shtml"
                yield item

            if currentpage < pagesize:
                nextpage = int(currentpage) + 1
                next_page_url = "http://www.hxb.com.cn/jrhx/khfw/yhkx/index_" + str(nextpage) + ".shtml"
                request = scrapy.Request(response.urljoin(next_page_url))
                request.meta['item'] = item
                yield request
        except IOError as e:
            print('error', e)

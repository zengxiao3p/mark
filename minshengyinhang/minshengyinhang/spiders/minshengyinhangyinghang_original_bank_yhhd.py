# -*- coding: utf-8 -*-
import scrapy

from minshengyinhang.items import MinshengyinhangItem

scrapy_link = 'http://www.cmbc.com.cn/zdtj/yhhd/index.htm'

domain = "cmbc.com.cn"


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

    name = "msyh_original_bank_yhhd"
    allowed_domains = [domain]
    start_urls = [
        scrapy_link,
    ]
    custom_settings = {
        'ITEM_PIPELINES': {'minshengyinhang.pipelines.MinshengyinhangPipeline': 301}
    }

    def parse(self, response):
        # 求取共几页
        try:
            pagesize = response.css('input#totalPage::attr("value")').extract_first()
            pagesize = int(pagesize)
            for showcss in response.css('div.counter_mid_1>div.count_one>div.div_margin>ul>li'):
                currentpage=response.css('ul.new_page_list>li')[2].css('a::text').extract_first()
                currentpage = int(currentpage);
                item = MinshengyinhangItem()
                item['title'] = showcss.css('span.left>a::text').extract_first().strip()
                item['publish_date'] = showcss.css('span.right::text').extract_first().strip()
                if (showcss.css('span.left>a::attr("href")').extract_first().strip().startswith('http') == False):
                    item['goto_link'] = "http://www.cmbc.com.cn/" + showcss.css('span.left>a::attr("href")').extract_first().strip()
                else:
                    item['goto_link'] = showcss.css('span.left>a::attr("href")').extract_first().strip()

                item['scrapy_link'] = "http://www.cmbc.com.cn/zdtj/yhhd/index" + str(currentpage)+"htm"
                yield item

            if currentpage < pagesize:
                nextpage = int(currentpage) + 1
                next_page_url = "http://www.cmbc.com.cn/zdtj/yhhd/index" + str(nextpage)+".htm"
                request = scrapy.Request(response.urljoin(next_page_url))
                request.meta['item'] = item
                yield request
        except IOError as e:
            print('error' ,e)

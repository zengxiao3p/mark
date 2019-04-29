# -*- coding: utf-8 -*-
import scrapy

from zhongguoyinhang.items import ZhongguoyinhangItem

from scrapy_splash import SplashRequest

scrapy_link = 'http://www.boc.cn/bcservice/bi3/bi31/index.html'

domain = "www.boc.cn"


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

    name = "zgyh_original_bank_qgyh"
    allowed_domains = [domain]
    start_urls = [
        scrapy_link,
    ]
    custom_settings = {
        'ITEM_PIPELINES': {'zhongguoyinhang.pipelines.ZhongguoyinhangQgyhPipeline': 301}
    }

    def parse(self, response):
        # 求取共几页
        try:
            pagesize = response.css('div.turn_page>p>span::text').extract_first()
            pagesize = int(pagesize)
            for showcss in response.css('div.main>div.news>ul.list>li'):
                temp=response._url.split('index_')
                if(len(temp)>1):
                    currentpage=int(temp[1].split('.html')[0])+1
                else:
                    currentpage=1
                currentpage = int(currentpage);
                item = ZhongguoyinhangItem()
                item['title'] = showcss.css('a::text').extract_first()
                item['publish_date'] = showcss.css('span::text').extract_first().strip('[]').strip()
                if (showcss.css('a::attr("href")').extract_first().startswith('http') == False):
                    item['goto_link'] = "http://www.boc.cn/bcservice/bi3/bi31/" +showcss.css('a::attr("href")').extract_first()
                else:
                    item['goto_link'] = showcss.css('a::attr("href")').extract_first()
                if currentpage==1:
                    item['scrapy_link'] = "http://www.boc.cn/bcservice/bi3/bi31/index.html"
                else:
                    item['scrapy_link'] = "http://www.boc.cn/bcservice/bi3/bi31/index_"+str(currentpage-1)+".html"
                yield item

            if currentpage < pagesize:
                nextpage = int(currentpage) + 1 -1
                next_page_url = "http://www.boc.cn/bcservice/bi3/bi31/index_"+str(nextpage)+".html"
                request = scrapy.Request(response.urljoin(next_page_url))
                request.meta['item'] = item
                yield request
        except IOError as e:
            print('error' ,e)

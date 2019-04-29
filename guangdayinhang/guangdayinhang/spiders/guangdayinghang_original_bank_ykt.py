# -*- coding: utf-8 -*-
import scrapy

from guangdayinhang.items import GuangdayinhangItem

scrapy_link = 'http://www.cebbank.com/site/gryw/yhhd/ad671762-1.html'

domain = "www.cebbank.com"


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

    name = "gdyh_original_bank_yhhd"
    allowed_domains=[domain]
    start_urls = [
        scrapy_link,
    ]
    custom_settings = {
        'ITEM_PIPELINES': {'guangdayinhang.pipelines.GuangdayinhangPipeline': 301}
    }

    def parse(self, response):
        #求取共几页
        try:
            pagesize =response.css('div#ceb_fy>font::text').extract_first().strip("\n\r").strip().split('/')
            pagesize=int(pagesize[1])
            for showcss in response.css("div#main_con > div >div.module_con>ul.gg_right_ul>li"):
                currentpage = response.css('div#ceb_fy>font::text').extract_first().strip("\n\r").strip().split('/')
                currentpage=int(currentpage[0])
                currentpage = int(currentpage);
                item = GuangdayinhangItem()
                item['title'] = showcss.css('li>div.gg_nr>a::text').extract_first()
                if(showcss.css('li>span.sp2::text').extract_first()!=None):
                    item['publish_date'] = showcss.css('li>span.sp2::text').extract_first().split('至')[0].strip()
                else:
                    item['publish_date'] ='1907-01-01';
                if (showcss.css('li>div.gg_nr>a::attr("href")').extract_first().startswith( 'http' )==False):
                    item['goto_link'] = "http://www.cebbank.com" +showcss.css('li>div.gg_nr>a::attr("href")').extract_first()
                else:
                    item['goto_link'] =showcss.css('li>div.gg_nr>a::attr("href")').extract_first()
                item['scrapy_link'] = "http://www.cebbank.com/site/gryw/yhhd/ad671762-"+str(currentpage)+".html"
                yield item

            if currentpage < pagesize:
                nextpage = int(currentpage) + 1
                next_page_url ="http://www.cebbank.com/site/gryw/yhhd/ad671762-"+str(nextpage)+".html"
                request = scrapy.Request(response.urljoin(next_page_url))
                request.meta['item'] = item
                yield request
        except IOError as e:
            print('error')
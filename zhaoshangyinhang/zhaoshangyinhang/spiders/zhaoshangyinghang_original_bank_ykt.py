# -*- coding: utf-8 -*-
import scrapy

from zhaoshangyinhang.items import ZhaoshangyinhangItem

scrapy_link = 'http://www.cmbchina.com/Personal/Promotion/Default.aspx'

domain = "cmbchina.com"


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

    name = "zsyh_original_bank_ykt"
    allowed_domains=[domain]
    start_urls = [
        scrapy_link,
    ]
    custom_settings = {
        'ITEM_PIPELINES': {'zhaoshangyinhang.pipelines.Zhaoshangyinhang_YktPipeline': 302}
    }

    def parse(self, response):
        #求取共几页
        try:
            pagesize =response.css("div.container>div.pager>div.pager_left>span.nolink>span.pageText")[2].css(
                "::text").extract_first().strip("\n\r").strip()
            pagesize=int(pagesize[-1])
            for showcss in response.css("div.container> div.content>table#content_listPromotion>tr"):
                currentpage = response.css("div.container>div.pager>div.pager_left>span.nolink>span.pageText")[2].css(
                "::text").extract_first().strip("\n\r").strip()
                currentpage=int(currentpage[0])
                currentpage = int(currentpage);
                item = ZhaoshangyinhangItem()
                item['title'] = showcss.css('li>span')[0].css('a::attr("title")').extract_first()
                item['publish_date'] = showcss.css('li>span')[1].css("::text").extract_first().strip('[]')
                if (showcss.css('li>span')[0].css('a::attr("href")').extract_first().startswith( 'http' )==False):
                    item['goto_link'] = "http://www.cmbchina.com" +showcss.css('li>span')[0].css('a::attr("href")').extract_first()
                else:
                    item['goto_link'] =showcss.css('li>span')[0].css('a::attr("href")').extract_first()
                item['scrapy_link'] = scrapy_link+"?city=&PageNo="+str(currentpage)
                yield item

            if currentpage < pagesize:
                nextpage = int(currentpage) + 1
                next_page_url =scrapy_link+"?city=&PageNo="+ str(nextpage)
                request = scrapy.Request(response.urljoin(next_page_url))
                request.meta['item'] = item
                yield request
        except IOError as e:
            print('error')
# -*- coding: utf-8 -*-
import scrapy

from nongyeyinhang.items import NongyeyinhangItem

from scrapy_splash import SplashRequest

scrapy_link = 'http://www.abchina.com/cn/PersonalServices/ABCPromotion/National/default.htm'

domain = "abchina.com"


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

    name = "nyyh_original_bank_yhhd"
    allowed_domains = [domain]
    start_urls = [
        scrapy_link,
    ]
    custom_settings = {
        'ITEM_PIPELINES': {'nongyeyinhang.pipelines.NongyeyinhangYhhdPipeline': 301}
    }

    # def start_requests(self):  # 重新定义起始爬取点
    #    for url in self.start_urls:
    #       yield SplashRequest(url,self.parse, args={'timeout': 5,},)


    def parse(self, response):
        # 求取共几页
        try:
            pagesize = 12
            pagesize = int(pagesize)
            if (len(response._url.split('default_')) > 1):
                currentpage = response._url.split('default_')[1].split('.htm')[0]
                currentpage = int(currentpage) + 1
            else:
                currentpage = 1
            for showcss in response.css('div.details_rightWrapC>ul>li'):
                item = NongyeyinhangItem()
                item['title'] = showcss.css('span>a::text').extract_first()
                if (showcss.css('span>a::attr("href")').extract_first().startswith('http') == False):
                    item[
                        'goto_link'] = "http://www.abchina.com/cn/PersonalServices/ABCPromotion/National/" + showcss.css(
                        'span>a::attr("href")').extract_first()
                else:
                    item['goto_link'] = showcss.css('span>a::attr("href")').extract_first()
                if currentpage == 1:
                    item['scrapy_link'] = "http://www.abchina.com/cn/PersonalServices/ABCPromotion/National/default.htm"
                else:
                    item[
                        'scrapy_link'] = "http://www.abchina.com/cn/PersonalServices/ABCPromotion/National/default_" + str(
                        currentpage) + ".htm"
                yield item

            if currentpage < pagesize:
                nextpage = int(currentpage) + 1
                next_page_url = "http://www.abchina.com/cn/PersonalServices/ABCPromotion/National/default_" + str(
                    nextpage-1) + ".htm"
                request = scrapy.Request(response.urljoin(next_page_url))
                request.meta['item'] = item
                yield request
        except IOError as e:
            print('error', e)

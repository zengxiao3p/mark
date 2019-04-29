# -*- coding: utf-8 -*-
import scrapy

from nongshangyinhang.items import NongshangyinhangOriginalBank

scrapy_link = 'http://www.qingbank.cn/list/privilegeInfo'

domain = "http://www.qingbank.cn"


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

    name = "nsyh_original_bank_yhxx"
    allowed_domains=["www.qingbank.cn"]
    start_urls = [
        scrapy_link,
    ]
    custom_settings = {
        'ITEM_PIPELINES': {'nongshangyinhang.pipelines.NsyhOriginalBankYhxxPipeline': 300}
    }

    def parse(self, response):
        pagesize = len(response.css("select>option").extract())
        for showcss in response.css("div.content > div.list> ul>li"):
            currentpage = response.css('select>option ').css('[selected=selected]').css("::text").extract_first()
            currentpage = int(currentpage);
            item = NongshangyinhangOriginalBank()
            item['title'] = showcss.css("a::text").extract_first().strip()
            item['publish_date'] = showcss.css("span::text").extract_first();
            item['goto_link'] = domain + showcss.css('a::attr("href")').extract_first();
            item['scrapy_link'] = response.request.url
            yield item

        if currentpage < pagesize:
            nextpage = int(currentpage) + 1
            next_page_url =domain + '/list/privilegeInfo-' + nextpage
            request = scrapy.Request(response.urljoin(next_page_url))
            request.meta['item'] = item
            yield request

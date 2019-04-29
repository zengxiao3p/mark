# -*- coding: utf-8 -*-
import scrapy

from gongshangyinhang.items import GongshangyinhangItem

scrapy_link = 'http://www.icbc.com.cn/icbc/优惠活动/活动列表/全国活动列表/default.htm'

domain = "www.icbc.com.cn"


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

    name = "gsyh_original_bank_qgyh"
    allowed_domains = [domain]
    start_urls = [
        scrapy_link,
    ]
    custom_settings = {
        'ITEM_PIPELINES': {'gongshangyinhang.pipelines.GongshangyinhangQgyhPipeline': 301}
    }

    def parse(self, response):
        # 求取共几页
        try:
            temp = response.css('div.MidBox>div>table>tr>td[align="right"]>div>a::text').extract_first();
            hasNextPage=False
            if(temp=='下一页'):
                hasNextPage=True
            if (len(response._url.split('default-PageList-')) > 1):
                currentpage = response._url.split('default-PageList-')[1].split('.htm')[0]
            else:
                currentpage = 1
            currentpage = int(currentpage);
            for showcss in response.css('div.MidBox>div>table>tr>td[align="left"]>span>a'):

                item = GongshangyinhangItem()
                item['title'] = showcss.css('::text').extract_first()
                if (showcss.css('::attr("href")').extract_first().startswith('http') == False):
                    item['goto_link'] = "http://www.icbc.com.cn/" +showcss.css('::attr("href")').extract_first()
                else:
                    item['goto_link'] = showcss.css('::attr("href")').extract_first()
                if currentpage==1:
                    item['scrapy_link'] = scrapy_link
                else:
                    item['scrapy_link'] = "http://www.icbc.com.cn/icbc/优惠活动/活动列表/全国活动列表/default-PageList-"+str(currentpage)+".htm"

                yield item

            if (hasNextPage==True):
                nextpage = int(currentpage) + 1 -1
                next_page_url = "http://www.icbc.com.cn/icbc/优惠活动/活动列表/全国活动列表/default-PageList-"+str(nextpage)+".htm"
                request = scrapy.Request(response.urljoin(next_page_url))
                request.meta['item'] = item
                yield request
        except IOError as e:
            print('error' ,e)

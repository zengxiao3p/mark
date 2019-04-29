# -*- coding: utf-8 -*-
import scrapy

from pufayinhang.items import PufayinhangItem
from scrapy_splash import SplashRequest
from scrapy.selector import Selector
from scrapy.spiders import XMLFeedSpider

scrapy_link = 'https://item.jd.com/2600240.html'
domain = "htts://per.spdb.com.cn"


class ToScrapeCSSSpider(scrapy.Spider):
    def __init__(self):
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'Cookie': 'TSPD_101=08e305e14cab2800faca7f9583ccf21620727d02de25b639258ff368c8510a8f766da8760fc18b1cf7f6903ede7d4dee085645110505100088f21c8adfba68df32604c0555697ae8',
        }

    name = "pfyh_original_bank_yhhd"
    allowed_domains = [domain]
    start_urls = [
        scrapy_link,
    ]
    iterator = 'iternodes'  # you can change this; see the docs

    # 此时将开始迭代的节点设置为第一个节点 rss

    itertag = 'rss'  # change it accordingly

    custom_settings = {
        'ITEM_PIPELINES': {'pufayinhang.pipelines.Pufayinhang_YhhdPipeline': 301}
    }

    def start_requests(self):  # 重新定义起始爬取点
        for url in self.start_urls:
            yield SplashRequest(
                url,
                args={'timeout': 5, 'images': 0}
                ,
                #splash_url=url,
                #endpoint='data.xml'
            )

    def parse(self, response):
        # 求取共几页
        try:
                i = PufayinhangItem()
                selector = Selector(text=response.text)
                i['title'] = selector.xpath("/rss/channel/item/title/text()").extract()
                i['link'] = selector.xpath("/rss/channel/item/link/text()").extract()
                i['author'] = selector.xpath("/rss/channel/item/author/text()").extract()
                # i['url'] = selector.select('url').extract()
                # i['name'] = selector.select('name').extract()
                # i['description'] = selector.select('description').extract()
                # 通过 for 循环以遍历出提取出来的存在在 item 中的信息并输出
                for j in range(len(i['title'])):
                    print("第 %s 篇文章" % str(j + 1))
                    print("标题是：%s" % i['title'][j])
                    print("对应链接是：%s" % i['link'][j])
                    print("对应作者是：%s" % i['author'][j])
                    print("-" * 20)


        except IOError as e:
            print('error')

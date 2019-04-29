# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest #重新定义了请求



lua = '''  #自定义lua脚本
function main(splash)
    splash:go(splash.args.url)                                                                            
    splash:wait(3)
    return splash:html()
    end
'''


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    allowed_domains = ['quotes.toscrape.com']                                                             
    start_urls = ['http://quotes.toscrape.com/js/']

    def start_requests(self): #重新定义起始爬取点
        for url in self.start_urls:
            yield SplashRequest(url,args = {'timeout':8,'images':0})

    def parse(self, response): #页面解析函数，这里我们使用了CSS选择器
        authors = response.css('div.quote small.author::text').extract() #选中名人并返回一个列表
        quotes = response.css('div.quote span.text::text').extract() #选中名言并返回一个列表
        yield from (dict(zip(['author','quote'],item)) for item in zip(authors,quotes)) #使用zip()函数--小伙伴们自行百度菜鸟教程即可
 #构造了一个元祖再进行遍历，再次使用zip结合dict构造器做成了列表，由于yield ，所以我们使用生成器解析返回

        next_url = response.css('ul.pager li.next a::attr(href)').extract_first()
        if next_url:
            complete_url = response.urljoin(next_url)#构造了翻页的绝对url地址
            yield SplashRequest(complete_url,args = {'timeout':8,'images':0})

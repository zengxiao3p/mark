# -*- coding: utf-8 -*-

from biaoshu.items import BiaoshuItem
from biaoshu.settings import COOKIES_FILE_PATH
import scrapy
import json
import urllib.parse
class ToScrapeCSSSpider(scrapy.Spider):
    def __init__(self, weixinName=None, *args, **kwargs):
        self.cookies_file_path=COOKIES_FILE_PATH
        super(ToScrapeCSSSpider, self).__init__(*args, **kwargs)

    name = "biaoshu_original_bank"
    allowed_domains = ['data.wxb.com','www.jianyu360.com']
    custom_settings = {
        'ITEM_PIPELINES': {'biaoshu.pipelines.BiaoshuPipeline': 301}
    }
    def get_browser_cookies(self):
        cookies = {}
        with open(self.cookies_file_path, 'r') as f:
            temp=f.read()
            if temp !='':
                listCookie = json.loads(temp)
                # cookies格式转换
                for Cookie in listCookie:
                    name = Cookie.get('name')
                    value = Cookie.get('value')
                    cookies[name] = value
        return  cookies
    #银行+关键字
    def start_requests(self):
        title_cycle=['IT']

        tempStore = [
            ['农商银行'],
                     ]
        for i in tempStore:
            everyUrl = 'https://www.jianyu360.com/jylab/supsearch/index.html'
            for j in title_cycle:
                yield scrapy.Request(url=everyUrl, callback=self.parse,cookies=self.get_browser_cookies(),
                             meta={'bank_name':i[0],'title': j, 'retry_times': True,'detail_innerHtml':False}, dont_filter=True)


    def parse(self, response):
        table=response.css('div.tabContainer-2>div.lucene-table>table')[1]
        for showcss in table.css('tbody>tr'):
            baioshuItem = BiaoshuItem()
            xuhao = showcss.css('td')[0].css('div::text').extract_first()
            baioshuItem['title'] = ''.join(showcss.css('td')[1].css("div,font")[0].css("::text").extract())
            baioshuItem['announcemen_type'] =  showcss.css('td')[2].css('div::text').extract_first()
            baioshuItem['budget'] =  showcss.css('td')[3].css('div::text').extract_first()
            baioshuItem['tenderee'] =  showcss.css('td')[4].css('div::text').extract_first()
            baioshuItem['bid_start_date'] =  showcss.css('td')[5].css('div::text').extract_first()
            baioshuItem['win_bid_tenderee'] =  showcss.css('td')[6].css('div::text').extract_first()
            baioshuItem['win_bid_money'] =  showcss.css('td')[7].css('div::text').extract_first()
            baioshuItem['bid_publish_date'] =  showcss.css('td')[8].css('div::text').extract_first()
            baioshuItem['source_name'] = response.request.meta['bank_name'] + '_' + response.request.meta['title']
            baioshuItem['bank_name'] = response.request.meta['bank_name']

            #按照他们的页面跳转规则来构建跳转链接
            thisId=showcss.css('::attr("dataid")').extract_first();
            dataindustry=showcss.css('::attr("dataindustry")').extract_first();
            searchValue = response.request.meta['bank_name'] + ' ' + response.request.meta['title']
            gotoLink=''
            if dataindustry == 'undefined' or dataindustry == '':
                gotoLink =  '.html?kds=' + urllib.parse.quote(searchValue)
            else:
                gotoLink = '.html?kds=' + urllib.parse.quote(searchValue) + '&industry=' + urllib.parse.quote(dataindustry)
            gotoLink='https://www.jianyu360.com'+'/article/content/'+thisId+gotoLink

            yield scrapy.Request(url=gotoLink, callback=self.parse_html, cookies=self.get_browser_cookies(),
                                 meta={'baioshuItem': baioshuItem,'detail_innerHtml':True}, dont_filter=True)



    def parse_html(self, response):
        # 获取文章源代码。
        item = response.meta['baioshuItem']
        item['snapshort_html'] = response.css('div.com-detail').extract_first()
        item['original_link']=response.css('div.original-text>a::attr("href")').extract_first()
        item['goto_link']=response.request.url

        yield item


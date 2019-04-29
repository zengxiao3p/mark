# -*- coding: utf-8 -*-
import scrapy
import json
from zhaoshangyinhang.items import ZhaoshangyinhangItem

from scrapy_splash import SplashRequest




scrapy_link = 'http://cc.cmbchina.com/SvrAjax/PromotionChange.ashx?type=specialsale'

#scrapy_link = 'http://cc.cmbchina.com/promotion/'

domain = "http://cc.cmbchina.com"


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

    name = "zsyh_original_bank_xyk"
    allowed_domains = ["http://cc.cmbchina.com "]
    start_urls = [
        scrapy_link,
    ]
    custom_settings = {
        'ITEM_PIPELINES': {'zhaoshangyinhang.pipelines.Zhaoshangyinhang_XykPipeline': 301}
    }


    def parse(self, response):
       models=parse_js2(str(response.body.decode('utf-8')))['list']
       for dict in models:
           item = ZhaoshangyinhangItem()
           item['title'] = dict["Title"]
           item['publish_date'] = dict['Date']
           item['scrapy_link'] = "http://cc.cmbchina.com/promotion/"
           item['goto_link'] = domain+dict['LinkUrl']
           yield item




def parse_js(expr):
    """
    解析非标准JSON的Javascript字符串，等同于json.loads(JSON str)
    :param expr:非标准JSON的Javascript字符串
    :return:Python字典
    """
    import ast
    m = ast.parse(expr)
    a = m.body[0]

    def parse(node):
        if isinstance(node, ast.Expr):
            return parse(node.value)
        elif isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Dict):
            return dict(zip(map(parse, node.keys), map(parse, node.values)))
        elif isinstance(node, ast.List):
            return map(parse, node.elts)
        else:
            raise NotImplementedError(node.__class__)

    return parse(a)

#解析非json类型的类json数据
def parse_js2(expr):
    """
    解析非标准JSON的Javascript字符串，等同于json.loads(JSON str)
    :param expr:非标准JSON的Javascript字符串
    :return:Python字典
    """
    obj = eval(expr, type('Dummy', (dict,), dict(__getitem__=lambda s, n: n))())
    return obj
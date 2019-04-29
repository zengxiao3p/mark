# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
import random

import time
import scrapy
from scrapy import signals
from scrapy import log
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from scrapy.http import HtmlResponse
import logging
from biaoshu.settings import COOKIES_FILE_PATH
from biaoshu.settings import SELENIUM_CHROME_DIRVER_LOCAL_PATH
from biaoshu.settings import USER_AGENTS
from biaoshu.settings import ZBY_USERNAME
from biaoshu.settings import ZBY_PASSWORD

from biaoshu.items import BiaoshuItem
import datetime

class BiaoshuMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.
    def __init__(self, agents):
        self.agents = agents

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        #s = cls()
       # crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        #return s
        return cls(crawler.settings.getlist('USER_AGENTS'))

    def process_request(self, request, spider):
        request.headers.setdefault('User-Agent', random.choice(self.agents))


    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ProxyMiddleWare(object):
    """docstring for ProxyMiddleWare"""

    def process_request(self, request, spider):
        '''对request对象加上proxy'''
        proxy = self.get_random_proxy()
        while(proxy is None):
            proxy = self.get_random_proxy()
        if  proxy.strip().startswith('http')== False:
            request.meta['proxy'] = 'http://' + proxy
        else:
            request.meta['proxy'] = proxy


    def process_response(self, request, response, spider):
        '''对返回的response处理'''
        # 如果返回的response状态不是200，重新生成当前request对象
        if response.status != 200:
            proxy = self.get_random_proxy()
            if proxy.strip().startswith('http') == False:
                request.meta['proxy'] = 'http://' + proxy
            else:
                request.meta['proxy'] = proxy
            return request
        return response

    def get_random_proxy(self):
        '''随机从文件中读取proxy'''
        while 1:
            with open(r'./proxies.txt', 'r') as f:
                proxies = f.readlines()
            if proxies:
                break
            else:
                time.sleep(1)
        proxy = random.choice(proxies).strip()
        if proxy == "":
            pass
        else:
          return proxy


'''
    header中间件
'''
class UserAgentMiddleware(object):
    def __init__(self):
        self.User_Agent = random.choice(USER_AGENTS).strip()
        self.Referer = 'https://www.jianyu360.com/jylab/supsearch/index.html'
        self.Host = 'jianyu360.com'
        self.Connection = 'keep-alive'
        self.Accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
    def process_request(self,spider,request):
        print('[+] using headers!')
        request.headers['User-Agent'] = self.User_Agent
        request.headers['Referer'] = self.Referer
        request.headers['Host'] = self.Host
        request.headers['Connection'] = self.Connection
        request.headers['Accept'] = self.Accept
        request.headers['Upgrade-Insecure-Requests'] = 1
        request.headers['Accept-Encoding'] = 'gzip, deflate, br'
        request.headers['Accept-Language'] = 'zh-CN,zh;q=0.9'

"""
    剑鱼登录cookie保存
"""
class CodeMiddleware(object):
    def __init__(self):

        self.logger = logging.getLogger(__name__)
        self.new_cookies = {}
        self.login_url = 'https://www.jianyu360.com/'
        self.cookies_file_path = COOKIES_FILE_PATH

    def get_browser_cookies(self):
        '''
            从本地文件读取cookies，并转换成scrapy.Request的cookies格式
        '''

        with open(self.cookies_file_path,'r') as f:
            listCookie = json.loads(f.read())

        cookies = {}

        #cookies格式转换
        for Cookie in listCookie:
            name = Cookie.get('name')
            value = Cookie.get('value')
            cookies[name] = value
        return cookies

    def process_request(self,request,spider):

        '''
            检测Reques对象有没有设置cookies
            如果没有，则调用chrome进行登陆操作，并写入cookies到本地
        '''
        if not request.cookies:
            options = webdriver.ChromeOptions()
            # 设置中文
            options.add_argument('lang=zh_CN.UTF-8')
            #启用无头浏览器
            #options.add_argument('--headless')

            # 更换头部
            options.add_argument('user-agent='+random.choice(USER_AGENTS).strip())
            browser = webdriver.Chrome(executable_path=SELENIUM_CHROME_DIRVER_LOCAL_PATH,chrome_options=options)
            wait = WebDriverWait(browser,10)

            browser.get(self.login_url)
            time.sleep(5)
            #剑鱼账号登录


            jy_erweima_image = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'img#layerImg-login')))

            erweima_url = jy_erweima_image.get_attribute('src')

            browser.get(erweima_url)
            time.sleep(2)

            input('请完成登陆，然后回车～')

            listCookie = browser.get_cookies()
            self.logger.debug('[+] Chrome cookies is %s' % listCookie)

            browser.quit()

            with open(self.cookies_file_path,'w') as f:
                f.write(json.dumps(listCookie))
            #读取文件cookies.json内的cookies

            request.cookies = self.get_browser_cookies()

    def process_response(self,request,response,spider):
        '''
            重定向处理，response状态码为302
            情况一：调用Chrome访问重定向页面为验证码页面，则输入验证码，获取新cookies，并返回带有新cookies值的Request
            情况二：调用Chrome访问重定向页面为正常页面，则保存新cookies，并返回带有新cookies值的Request
            一般微信的反爬为第一次重定向页面为第二种情况，后续为情况一
        '''
        if response.status == 302:
            url = response.url
            #proxy = request.meta['proxy']
            self.logger.debug('[+] url:%s,status:%s' % (url,response.status))
            #self.logger.debug('[+] request_url is : %s' % request.url)
            '''设置代理浏览器'''
            chrome_options = webdriver.ChromeOptions()
            #chrome_options.add_argument('--proxy-server='+proxy)
            time.sleep(2)
            browser = webdriver.Chrome(chrome_options=chrome_options)
            wait = WebDriverWait(browser,15)
            time.sleep(2)
            #需要先打开页面才能设置cookeis
            browser.get('https://weixin.sogou.com')
            browser.delete_all_cookies()
            time.sleep(3)

            '''设置selenium浏览器的cookie'''
            with open(self.cookies_file_path,'r') as f:
                listCookie = json.loads(f.read())
            time.sleep(1)
            for cookie in listCookie:
                browser.add_cookie({
                    'domain':cookie['domain'],
                    'httpOnly': cookie['httpOnly'],
                    'name':cookie['name'],
                    'path':cookie['path'],
                    'secure':cookie['secure'],
                    'value':cookie['value'],
                    'expiry':cookie['expiry']
                    })

            if not browser.get(url):
                #进行页面判定，如果不是not Found页面，则进行后续操作
                try:
                    test = browser.find_element_by_xpath('//div[@id="main-message"]/h1/span').text
                except:
                    test = False
                if test:
                    self.logger.debug('[+] proxy is broken')
                    browser.quit()
                    return request

                #from scrapy.shell import inspect_response
                #inspect_response(response,spider)

                #获取验证码文本框
                self.logger.debug('[!] search input_text ....')
                try:
                    input_text = wait.until(EC.presence_of_element_located((By.ID,'seccodeInput')))
                    self.logger.debug('[√] input_text done!')
                except:
                    self.logger.debug('[!] input_text fail !')
                    input_text = None

                #判断是情况一还是情况二，如果情况一则直接返回带有新cookies值的Request
                if input_text:

                    #获取提交验证码的button
                    self.logger.debug('[!] search button....')
                    try:
                        button = wait.until(EC.element_to_be_clickable((By.ID,'submit')))
                        self.logger.debug('[√] button done!')
                    except:
                        self.logger.debug('[!] button fail!')

                    code = str(input('please input code:'))

                    input_text.clear()
                    time.sleep(3)
                    if not input_text.send_keys(code):
                    #这里停顿3秒才按button是模仿人为操作
                        time.sleep(3)
                        if not button.click():

                            time.sleep(3)

                            #设置新cookie
                            self.logger.debug('[+] Set new cookies: ')
                            new_listCookie = browser.get_cookies()

                            with open(self.cookies_file_path,'w') as f:
                                f.write(json.dumps(new_listCookie))

                            self.logger.info('[+] This is new_listCookie: %s' % new_listCookie )
                            for cookie in new_listCookie:
                                name = cookie.get('name')
                                value = cookie.get('value')
                                self.new_cookies[name] = value

                else:
                    new_listCookie = browser.get_cookies()
                    self.logger.info('[+] This is new_listCookie: %s' % new_listCookie )
                    for cookie in new_listCookie:
                        name = cookie.get('name')
                        value = cookie.get('value')
                        self.new_cookies[name] = value

                    #request.meta['retry_times'] = False

                browser.quit()
                request.cookies = self.new_cookies
                return request
                '''
                page = request.meta.get('page')
                word = request.meta.get('word')
                cookie = request.cookies
                t = request.callback
                return scrapy.Request(url=url,callback=t,cookies=cookie,meta={'page':page,'word':word,'proxy':proxy},dont_filter=True)
                '''


                #return request.replace(url = url)

        else:
            self.logger.debug('[+] 200 Continue.......')
            return response


"""
    剑鱼seleniumMiddleware
"""
class SeleniumMiddleware(object):
    def __init__(self):
        self.cookies_file_path = COOKIES_FILE_PATH

    def process_request(self, request, spider):
        #判断是否为detail_innerHtml

        if request.meta['detail_innerHtml']==False:
            options = webdriver.ChromeOptions()
            # 设置中文
            options.add_argument('lang=zh_CN.UTF-8')
            #设置无头
            #options.add_argument('--headless')
            #options.add_argument('--disable-gpu')
            #options.add_argument('--remote-debugging-port=9222')
            # 更换头部
            options.add_argument('user-agent='+request.headers['User-Agent'].decode(encoding='utf-8'))
            #options.add_argument('--proxy-server='+request.meta['proxy'])
            browser = webdriver.Chrome(
                executable_path=SELENIUM_CHROME_DIRVER_LOCAL_PATH,
                chrome_options=options)

            wait = WebDriverWait(browser, 15)
            browser.get(request.url)

            '''设置selenium浏览器的cookie'''
            with open(self.cookies_file_path, 'r') as f:
                listCookie = json.loads(f.read())
            time.sleep(1)
            browser.delete_all_cookies();
            for cookie in listCookie:
                browser.add_cookie({
                   # 'domain': cookie['domain'],
                   # 'httpOnly': cookie['httpOnly'],
                    'name': cookie['name'],
                   # 'path': cookie['path'],
                   # 'secure': cookie['secure'],
                    'value': cookie['value'],
                   # 'expiry': None if 'expiry' not in cookie else cookie['expiry']
                })
           # browser.close()
            browser.get(request.url)
            time.sleep(5)
            # 获取要查询的银行，和关键词
            title=request.meta['title']
            bank_name=request.meta['bank_name']

            #1输入标题关键词
            searcb_text = wait.until(EC.presence_of_element_located((By.ID, 'searchinput')))
            if searcb_text:
                searcb_text.send_keys(bank_name+' '+title);
            #点击招标
            zhaobiao =wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.info-content>font[data-value="招标"]')))
            zhaobiao.click()
            time.sleep(5)
            #点击中标
            zhongbiao=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.info-content>font[data-value="中标"]')))
            zhongbiao.click()
            time.sleep(5)

            #输入开始时间和结束时间
            browser.execute_script('document.getElementById("starttime").setAttribute("data-value","1483200000")')
            now = int(time.time())
            browser.execute_script('document.getElementById("endtime").setAttribute("data-value",'+str(now)+')')
            #点击表格
            biaoge  = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.right-tabBtn>button#right-table')))
            biaoge.click()
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.right-tabBtn>button#right-table'))).click()
            time.sleep(5)

            #返回页面
            true_page = browser.page_source

            res=HtmlResponse(request.url,body = true_page,encoding = 'utf-8',request = request,)
            #记录搜狗微信公众临时生成的gotoLink的地址，注意该地址是微信搜狗经常会切换的地址。

            browser.quit()
            return res

    def process_response(self, request, response, spider):
       return CodeMiddleware().process_response(request,response,spider)


"""
    中标易登录cookie保存

"""
class ZbyCodeMiddleware(object):
    def __init__(self):

        self.logger = logging.getLogger(__name__)
        self.new_cookies = {}
        self.login_url = 'https://www.zhongbiaoyi.com/vip/'
        self.cookies_file_path = COOKIES_FILE_PATH

    def get_browser_cookies(self):
        '''
            从本地文件读取cookies，并转换成scrapy.Request的cookies格式
        '''

        with open(self.cookies_file_path,'r') as f:
            listCookie = json.loads(f.read())

        cookies = {}

        #cookies格式转换
        for Cookie in listCookie:
            name = Cookie.get('name')
            value = Cookie.get('value')
            cookies[name] = value
        return cookies

    def process_request(self,request,spider):

        '''
            检测Reques对象有没有设置cookies
            如果没有，则调用chrome进行登陆操作，并写入cookies到本地
        '''
        if not request.cookies:
            options = webdriver.ChromeOptions()
            # 设置中文
            options.add_argument('lang=zh_CN.UTF-8')
            #启用无头浏览器
            #options.add_argument('--headless')

            # 更换头部
            options.add_argument('user-agent='+random.choice(USER_AGENTS).strip())
            browser = webdriver.Chrome(executable_path=SELENIUM_CHROME_DIRVER_LOCAL_PATH,chrome_options=options)
            wait = WebDriverWait(browser,10)

            browser.get(self.login_url)
            time.sleep(5)
            #中标易登录页面

            browser.find_element_by_css_selector('input[name="user"]').send_keys(ZBY_USERNAME)
            browser.find_element_by_css_selector('input[name="pass"]').send_keys(ZBY_PASSWORD)
            loginbtn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'p.center>button')))
            loginbtn.click()
            time.sleep(5)

            searchurl = 'https://www.zhongbiaoyi.com/vip/search.php'

            browser.get(searchurl)
            time.sleep(2)

            listCookie = browser.get_cookies()
            self.logger.debug('[+] Chrome cookies is %s' % listCookie)

            browser.quit()

            with open(self.cookies_file_path,'w') as f:
                f.write(json.dumps(listCookie))
            #读取文件cookies.json内的cookies

            request.cookies = self.get_browser_cookies()

    def process_response(self,request,response,spider):
        '''
            重定向处理，response状态码为302
            情况一：调用Chrome访问重定向页面为验证码页面，则输入验证码，获取新cookies，并返回带有新cookies值的Request
            情况二：调用Chrome访问重定向页面为正常页面，则保存新cookies，并返回带有新cookies值的Request
            一般微信的反爬为第一次重定向页面为第二种情况，后续为情况一
        '''
        if response.status == 302:
            url = response.url
            #proxy = request.meta['proxy']
            self.logger.debug('[+] url:%s,status:%s' % (url,response.status))
            #self.logger.debug('[+] request_url is : %s' % request.url)
            '''设置代理浏览器'''
            chrome_options = webdriver.ChromeOptions()
            #chrome_options.add_argument('--proxy-server='+proxy)
            time.sleep(2)
            browser = webdriver.Chrome(chrome_options=chrome_options)
            wait = WebDriverWait(browser,15)
            time.sleep(2)
            #需要先打开页面才能设置cookeis
            browser.get('https://weixin.sogou.com')
            browser.delete_all_cookies()
            time.sleep(3)

            '''设置selenium浏览器的cookie'''
            with open(self.cookies_file_path,'r') as f:
                listCookie = json.loads(f.read())
            time.sleep(1)
            for cookie in listCookie:
                browser.add_cookie({
                    'domain':cookie['domain'],
                    'httpOnly': cookie['httpOnly'],
                    'name':cookie['name'],
                    'path':cookie['path'],
                    'secure':cookie['secure'],
                    'value':cookie['value'],
                    'expiry':cookie['expiry']
                    })

            if not browser.get(url):
                #进行页面判定，如果不是not Found页面，则进行后续操作
                try:
                    test = browser.find_element_by_xpath('//div[@id="main-message"]/h1/span').text
                except:
                    test = False
                if test:
                    self.logger.debug('[+] proxy is broken')
                    browser.quit()
                    return request

                #from scrapy.shell import inspect_response
                #inspect_response(response,spider)

                #获取验证码文本框
                self.logger.debug('[!] search input_text ....')
                try:
                    input_text = wait.until(EC.presence_of_element_located((By.ID,'seccodeInput')))
                    self.logger.debug('[√] input_text done!')
                except:
                    self.logger.debug('[!] input_text fail !')
                    input_text = None

                #判断是情况一还是情况二，如果情况一则直接返回带有新cookies值的Request
                if input_text:

                    #获取提交验证码的button
                    self.logger.debug('[!] search button....')
                    try:
                        button = wait.until(EC.element_to_be_clickable((By.ID,'submit')))
                        self.logger.debug('[√] button done!')
                    except:
                        self.logger.debug('[!] button fail!')

                    code = str(input('please input code:'))

                    input_text.clear()
                    time.sleep(3)
                    if not input_text.send_keys(code):
                    #这里停顿3秒才按button是模仿人为操作
                        time.sleep(3)
                        if not button.click():

                            time.sleep(3)

                            #设置新cookie
                            self.logger.debug('[+] Set new cookies: ')
                            new_listCookie = browser.get_cookies()

                            with open(self.cookies_file_path,'w') as f:
                                f.write(json.dumps(new_listCookie))

                            self.logger.info('[+] This is new_listCookie: %s' % new_listCookie )
                            for cookie in new_listCookie:
                                name = cookie.get('name')
                                value = cookie.get('value')
                                self.new_cookies[name] = value

                else:
                    new_listCookie = browser.get_cookies()
                    self.logger.info('[+] This is new_listCookie: %s' % new_listCookie )
                    for cookie in new_listCookie:
                        name = cookie.get('name')
                        value = cookie.get('value')
                        self.new_cookies[name] = value

                    #request.meta['retry_times'] = False

                browser.quit()
                request.cookies = self.new_cookies
                return request
                '''
                page = request.meta.get('page')
                word = request.meta.get('word')
                cookie = request.cookies
                t = request.callback
                return scrapy.Request(url=url,callback=t,cookies=cookie,meta={'page':page,'word':word,'proxy':proxy},dont_filter=True)
                '''


                #return request.replace(url = url)

        else:
            self.logger.debug('[+] 200 Continue.......')
            return response


"""
    中标易登录SeleniumMiddleware保存
"""
class ZbySeleniumMiddleware(object):
    def __init__(self):
        self.cookies_file_path = COOKIES_FILE_PATH

    def process_request(self, request, spider):
        #判断是否为detail_innerHtml

        if request.meta['detail_innerHtml']==False:
            options = webdriver.ChromeOptions()
            # 设置中文
            options.add_argument('lang=zh_CN.UTF-8')
            #设置无头
            #options.add_argument('--headless')
            #options.add_argument('--disable-gpu')
            #options.add_argument('--remote-debugging-port=9222')
            # 更换头部
            options.add_argument('user-agent='+request.headers['User-Agent'].decode(encoding='utf-8'))
            #options.add_argument('--proxy-server='+request.meta['proxy'])
            browser = webdriver.Chrome(
                executable_path=SELENIUM_CHROME_DIRVER_LOCAL_PATH,
                chrome_options=options)

            wait = WebDriverWait(browser, 15)
            browser.get(request.url)

            '''设置selenium浏览器的cookie'''
            with open(self.cookies_file_path, 'r') as f:
                listCookie = json.loads(f.read())
            time.sleep(1)
            browser.delete_all_cookies();
            for cookie in listCookie:
                browser.add_cookie({
                    'domain': cookie['domain'],
                    'httpOnly': cookie['httpOnly'],
                    'name': cookie['name'],
                    'path': cookie['path'],
                    'secure': cookie['secure'],
                    'value': cookie['value'],
                   # 'expiry': None if 'expiry' not in cookie else cookie['expiry']
                })
           # browser.close()
            browser.get(request.url)
            time.sleep(5)
            # 获取要查询的银行，和关键词
            title=request.meta['title']
            bank_name=request.meta['bank_name']

            #点击高级搜索
            settings = wait.until(EC.presence_of_element_located((By.ID, 'btn_setting')))
            settings.click()
            time.sleep(1)
            #选择标题,公告类型
            Select(browser.find_element_by_id("sel_result")).select_by_index("1")
            Select(browser.find_element_by_id("sel_type")).select_by_index("1")

            #点击确定,关闭模态框
            #queding = wait.until(EC.alert_is_present((By.CSS_SELECTOR, 'div.modal-footer>div.row>button')))
            #queding.click()
            browser.execute_script('$("div.modal-footer>div.row>button").click()')
            #1输入标题关键词
            searcb_text = wait.until(EC.presence_of_element_located((By.ID, 'txt_search')))
            if searcb_text:
                searcb_text.send_keys(bank_name+' '+title);

            #选择100条,分别为10条、50条、100条
            Select(browser.find_element_by_css_selector("table#tbl_data>tfoot>tr>td>select")).select_by_index("3")

            time.sleep(1)
            #点击搜索
            browser.find_element_by_css_selector('div#btn_search').click()
            time.sleep(5)



            itemlist = []

            # 获取点击后的页面并静态解析
            res = HtmlResponse(request.url, body=browser.page_source, encoding='utf-8', request=request, )
            #如果为空

            if(res.css('table#tbl_data>tbody>tr>td::text').extract_first()=='未找到任何记录'):
                browser.quit()
                request.meta['itemlist'] = itemlist
                return  res

            for i,showcss in enumerate(res.css('table#tbl_data>tbody>tr')):

                item = BiaoshuItem()
                item['title'] = ''.join(showcss.css('td')[0].css('::text').extract())
                item['announcemen_type'] = showcss.css('td')[1].css('::text').extract_first().strip()
                item['province'] = showcss.css('td')[2].css('::text').extract_first()
                item['bid_publish_date'] = showcss.css('td')[3].css('::text').extract_first()

                #在这里进行模拟点击并获取内容
                detailMessage = browser.find_element_by_css_selector('table#tbl_data>tbody>tr:nth-child('+str(i+1)+')')
                detailMessage.click()
                time.sleep(2)
                detailhtml=HtmlResponse(request.url, body=browser.page_source, encoding='utf-8', request=request, )

                item['original_link'] = detailhtml.css('div.modal-mask>div.modal-wrapper>div.modal-dialog>div.modal-content>div.modal-header>p>a::attr("href")').extract_first()
                item['snapshort_html']=detailhtml.css('div.modal-mask>div.modal-wrapper>div.modal-dialog>div.modal-content>div.modal-body').extract()

                #关闭当前的模态框
                browser.execute_script('$("div.modal-footer>div.row>button").click()')

                #将item加入到数组中
                itemlist.append(item)

            request.meta['itemlist']=itemlist

            response = HtmlResponse(request.url, body=browser.page_source, encoding='utf-8', request=request, )

            # 爬取完成，关闭浏览器
            browser.quit()

            return response

    def process_response(self, request, response, spider):
       return CodeMiddleware().process_response(request,response,spider)


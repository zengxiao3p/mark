# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html




import pymysql
import datetime
from twisted.enterprise import adbapi
import scrapy
from scrapy.utils.project import get_project_settings
from biaoshu.settings import COOKIES_FILE_PATH

class MysqlInstance(scrapy.Spider):
    def __init__(self, *args, **kwargs):
        settings = get_project_settings()
        dbparams = dict(
            host=settings['MYSQL_HOST'],  # 读取settings中的配置
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            port=settings['MYSQL_PORT'],
            charset='utf8',  # 编码要加上，否则可能出现中文乱码问题
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=False,
        )
        dbpool = adbapi.ConnectionPool('pymysql', **dbparams)  # **表示将字典扩展为关键字参数,相当于host=xxx,db=yyy....
        self.dbpool = dbpool;


# 全局调用一次数据库连接池
dbpool = MysqlInstance().dbpool


class BiaoshuPipeline(object):
    def __init__(self):
        self.cookies_file_path = COOKIES_FILE_PATH


    #释放数据库连接和清空cookies
    def close_spider(self, spider):
        dbpool.close()
        with open(self.cookies_file_path, 'wb+') as f:
            f.truncate()

    # pipeline默认调用
    def process_item(self, item, spider):
        query = dbpool.runInteraction(self._conditional_insert, item)  # 调用插入的方法
        query.addErrback(self._handle_error, item, spider)  # 调用异常处理方法
        return item

    def _conditional_insert(self, tx, item):
        try:
            # 首先获取该记录是否存在，若不存在即添加，否者更新
            querysql = "select * from smartpush_scrapy_bidding_document_detail where title = %s AND bid_publish_date= %s "
            item["bid_publish_date"] = item["bid_publish_date"].strip('[]')
            tx.execute(querysql, (item['title'], item["bid_publish_date"]))
            result = tx.fetchone()

            #先把scrapyId和fromsourceId拿出来
            querysql2 = "SELECT smartpush_scrapy_id FROM(SELECT a.id AS themeid , b.fromsource_id ,b.id AS smartpush_scrapy_id FROM smartpush_scrapy_theme AS a  RIGHT JOIN smartpush_scrapy AS b ON  a.id = b.theme_id" \
                        " AND a.name= %s )AS vv LEFT JOIN smartpush_from_source AS sfs ON  vv.fromsource_id=sfs.id  " \
                        "WHERE   sfs.type =%r AND sfs.name= %s "
            tx.execute(querysql2, (item['bank_name'], int(3), item['source_name']))
            result2 = tx.fetchone()
            # insert
            if result == None:
                smartpush_scrapy_id = [int(result2['smartpush_scrapy_id'])][0]
                dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                item["bid_publish_date"] = item["bid_publish_date"].strip('[]')
                sql = "insert into smartpush_scrapy_bidding_document_detail" \
                      "(title,win_bid_money,bid_publish_date,create_date,snapshort_html" \
                      ",goto_link,announcemen_type,budget,tenderee,win_bid_tenderee,original_link,bid_start_date,key_word,province" \
                      ",scrapy_id) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                paramsInsert = (
                    item["title"], item["win_bid_money"], item['bid_publish_date'], dt, item['snapshort_html'],
                    item["goto_link"], item["announcemen_type"], item['budget'],item['tenderee'],
                    item["win_bid_tenderee"], item["original_link"], item['bid_start_date'],item['key_word'],item['province'],
                    smartpush_scrapy_id)
                tx.execute(sql, paramsInsert)

        except IOError as e:
                print('Error:', e)

    def _handle_error(self, failue, item, spider):
        print("--------------database operation exception!!-----------------")
        failue



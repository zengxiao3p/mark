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


class GuangdayinhangPipeline(object):
    # pipeline默认调用
    def process_item(self, item, spider):
        query = dbpool.runInteraction(self._conditional_insert, item)  # 调用插入的方法
        query.addErrback(self._handle_error, item, spider)  # 调用异常处理方法
        return item

    def _conditional_insert(self, tx, item):
        try:
            # 首先去重
            querysql = "select * from smartpush_scrapy_detail where title = %s AND publish_date= %s "
            item["publish_date"] = item["publish_date"].strip('[]')
            tx.execute(querysql, (item['title'], item["publish_date"]))
            result = tx.fetchone()
            # insert
            if result == None:
                # 先把scrapyId和fromsourceId拿出来
                querysql2 = "SELECT smartpush_scrapy_id FROM(SELECT a.id AS themeid , b.fromsource_id ,b.id AS smartpush_scrapy_id FROM smartpush_scrapy_theme AS a  RIGHT JOIN smartpush_scrapy AS b ON  a.id = b.theme_id" \
                            " AND a.name= %s )AS vv LEFT JOIN smartpush_from_source AS sfs ON  vv.fromsource_id=sfs.id  " \
                            "WHERE   sfs.type =%r AND sfs.name= %s "
                tx.execute(querysql2, ('光大银行',int(1), '光大银行优惠活动'))
                result2 = tx.fetchone()
                if  result2  != None:
                    smartpush_scrapy_id = [int(result2['smartpush_scrapy_id'])][0]
                    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    item["publish_date"] = item["publish_date"].strip('[]')
                    sql = "insert into smartpush_scrapy_detail(title,publish_date,scrapy_link,goto_link,scrapy_id,created_time) values(%s,%s,%s,%s,%s,%s)"
                    paramsInsert = (
                        item["title"], item["publish_date"], item['scrapy_link'], item['goto_link'], smartpush_scrapy_id,
                        dt)
                    tx.execute(sql, paramsInsert)
        except Exception as e:
            print('Error:', e)

    def _handle_error(self, failue, item, spider):
        print("--------------database operation exception!!-----------------")
        failue
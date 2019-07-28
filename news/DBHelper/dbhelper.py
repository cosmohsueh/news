import pymysql
from scrapy.utils.project import get_project_settings
from twisted.enterprise import adbapi
import time
import uuid

class DBHelper():

    def __init__(self):
        settings = get_project_settings()

        dbparams = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=False,
        )
        dbpool = adbapi.ConnectionPool('pymysql', **dbparams)

        self.dbpool = dbpool

    def connect(self):
        return self.dbpool

    def insert(self, item):
        sql = "INSERT INTO NEWS(ID, TITLE, CONTENT, CHANNEL, URL, PUBLISH_DATE, INSERT_DATE, REPORTER) " \
              "values(%s, %s, %s, %s, %s, %s, %s, %s)"
        query = self.dbpool.runInteraction(self._conditional_insert, sql, item)
        query.addErrback(self._handle_error)

        return item

    def _conditional_insert(self, tx, sql, item):
        item['id'] = str(uuid.uuid4())
        item['insert_date'] = time.strftime('%Y-%m-%d %H:%M:%S',
                                           time.localtime(time.time()))
        params = (item["id"], item["title"], item['content'], item['channel'],
                  item['url'], item['date'], item['insert_date'], item['author'])
        tx.execute(sql, params)

    def _handle_error(self, failue):
        print('--------------database operation exception!!-----------------')
        print(failue)
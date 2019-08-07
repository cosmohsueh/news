from news.DBHelper.dbhelper import DBHelper
import jieba
import json
import re

class JiebaPipeline(object):

    def __init__(self):
        self.db = DBHelper()

    def process_item(self, item, spider):
        tmp = re.sub('<[^>]*>', '', item['content'])
        tmp = re.sub('\s', '', tmp)

        seglist = jieba.cut(tmp, cut_all=False)
        hash = {}
        for i in seglist:
            if len(i) > 1:
                if i in hash:
                    hash[i] += 1
                else:
                    hash[i] = 1

        item['json'] = json.dumps(hash, ensure_ascii=False)
        self.db.insert_jieba(item)
        return item

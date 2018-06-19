# coding: utf-8
import pymongo
import sys
reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append('../')
import config
sys.path.append('./')

mongo_zydata = pymongo.MongoClient(config.MONGO_HOST, config.MONGO_PORT).zydata
mongo_conn = pymongo.MongoClient(config.MONGO_HOST, config.MONGO_PORT).test123
mongo = pymongo.MongoClient(config.MONGO_HOST, config.MONGO_PORT)

class MongoDB:
    def __init__(self, db=None, collections=None):
        """
        初始化数据库
        :param db:数据库名称 
        :param collections: 数据库的集合的名称
        """
        self.client = pymongo.MongoClient(
            config.MONGO_HOST, config.MONGO_PORT)
        if db == None:
            self.db = self.client[config.MONGO_DB]
        else:
            self.db = self.client[db]
        self.post = self.db[collections]

    def update(self, data, upsert):
        """
        更新数据库中的数据，如果upsert为Ture，那么当没有找到指定的数据时就直接插入，反之不执行插入
        :param data: 要插入的数据
        :param upsert: 判断是插入还是不插入
        :return: 
        """
        self.post.update({"ip": data}, {'$set': {'ip': data}}, upsert)

    def find(self, select):
        """
        根据传入的参数查找指定的值，注意这里的select是字典
        :param select: 指定的查找条件，这里的是字典类型的，比如{"name":"chenjiabing","age":22}
        :return: 返回的是查询的结果，同样是字典类型的
        """
        return self.post.find(select)

    def insert(self, data):
        """
        向数据库中插入指定的数据
        :param data: 要插入的数据，这里的是字典的类型比如：{"name":"chenjiabing","age":22}
        :return: 插入成功返回True,反之返回false
        """
        try:
            self.post.insert(data)
            return True
        except:
            return False

    def remove(self, select):
        """
        删除指定条件的记录
        :param select: 指定的条件，这里是字典类型的，比如{"age":22} 表示删除age=22的所有数据
        :return: 如果删除成功返回True，else返回False
        """
        try:
            self.post.remove(select)
            return True
        except:
            return False

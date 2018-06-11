# -*- coding: utf-8 -*-
# !/usr/bin/env python

import json
import redis
import sys
sys.path.append('../')
import config
sys.path.append('./')

# class RedisClient(object):
#     """
#     Reids client
#     """

#     def __init__(self, host=config.RD_HOST, port=config.RD_PORT, password=config.RD_PASSWORD, db=config.RD_DB):
#         """
#         init
#         :param host:
#         :param port:
#         :return:
#         """
#         self.__conn = redis.Redis(host=host, port=port, db=db, password=password)

#     def rpop(key, count=1):
#         if count > 1:
#             return (x for x in xrange(0,count))
#         return self.__conn.rpop(key)

#     def get(key):
#         return self.__conn.get(key)

rd = redis.Redis(host=config.RD_HOST, port=config.RD_PORT, password=config.RD_PASSWORD, db=config.RD_DB)

def rpop(key, count=1):
    if count > 1:
        return (x for x in xrange(0,count))
    return rd.rpop(key)


# rd.sadd('myset','world')
# rd.smove('myset','myset1','world')
# setNew = rd.smembers('myset1')
# print "The distination set:", setNew

# # Remove and return a random member of set ``name``, spop(self, name)
# spop = rd.spop('myset1')
# print "Get return random element:",spop, ", remaining elements:",rd.smembers('myset1')

# # Return a random member of set ``name``,  srandmember(self, name),
# # >2.6 return numbers can be self define
# srandom = rd.srandmember('myset')
# print "Return random element:",srandom 

# # Remove ``value`` from set ``name``, srem(self, name, value)
# rem = rd.srem('myset','hello')
# print "Get srem boolean:",rem 

# # sunion(self, keys, *args)
# # Return the union of sets specifiued by ``keys``
# rd.sadd('myset0','special')
# setUnion = rd.sunion(['myset','myset0','myset1'])
# print "The union of sets specified by keys:",setUnion

# # sunionstore(self, dest, keys, *args)
# # Store the union of sets specified by ``keys`` into a new
# # set named ``dest``.  Returns the number of keys in the new set.
# rd.sunionstore('setunion',['myset','myset1'])
# setUnion = rd.smembers('setunion')
# print "The union of sets store in the new set setUnion:", setUnion

# # no SSCAN

# #Empty db
# rd.flushdb()

# 批量匹配删除key
# rd.delete(*rd.keys('*yk*'))

#  rd.sismember("testkey",2)  #判断值2是否存在testkey中 return True/False
# rd.sismember("yk_video_detail_done",'http://list.youku.com/show/id_z511dd1a338e111e6bdbb.html')

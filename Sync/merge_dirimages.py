# coding=utf-8
import re
import pathlib
import sys
import os
import shutil
reload(sys)
sys.setdefaultencoding('utf8')
import json
sys.path.append('../')
import config
sys.path.append('./')
from pymongo import MongoClient
from bson.objectid import ObjectId
from DB.Vod import Vod
from DB.mysql_session import session
from PIL import Image
import Levenshtein as lst

# path = u'E:/media/baiyug/baiyug/'
merged_path = u'E:/media/image/merged/'
imagedir_path = u"E:/media/image/image"

# db
tv_db = MongoClient(config.MONGO_HOST, config.MONGO_PORT).zydata.youku_tv
test_db = MongoClient(config.MONGO_HOST, config.MONGO_PORT).zydata.test
regx = re.compile(u"ST 警视厅科学特搜班", re.IGNORECASE)

r_tets = tv_db.find({"title": regx})


def merge_image_fromdir():
    """
    merge 影视名命名文件夹的海报图片文件到mongodb，杀破狼/image01/xddddd.jpg
    merge完后删除该文件夹
    """
    origin_dirs = os.listdir(imagedir_path)
    for dir_name in origin_dirs:
        regx = re.compile(".*"+dir_name+".*", re.IGNORECASE)
        r = tv_db.find({"title": regx})
        r_cp = tv_db.find({"title": regx})
        if r:
            nlts = [lst.ratio(dir_name, mon['title'])
                    for mon in r if lst.ratio(dir_name, mon['title']) >= 0.9]
            if len(nlts) > 1:
                print("mongo > 1")
                continue
            if len(nlts) == 0:
                print("mongo none")
                continue
            # 一个电影文件下 的全部图片全路劲
            dir_names = os.listdir(imagedir_path+"/"+dir_name)
            urls = [imagedir_path+"/"+dir_name+"/"+img_dirname + "/" + "".join(os.listdir(
                imagedir_path+"/"+dir_name+"/"+img_dirname)) for img_dirname in dir_names if len(os.listdir(imagedir_path+"/"+dir_name+"/"+img_dirname)) > 0]
            for dd in r_cp:
                _width = _height = 0
                for url in urls:
                    try:
                        im = Image.open(url)
                    except Exception as e:
                        print(str(e))
                        continue
                    width, height = im.size
                    print(width, height)
                    im.close()
                    if _width == width and _height == height:
                        print("aleady saved.")
                        continue
                    _width, _height = im.size
                    print(merged_path+str(dd['_id']) + '_' +
                          str(width) + "x" + str(height) + '.jpg')
                    print(url)
                    print(dd["title"])
                    push_thumb = {
                        "url": str(dd['_id']) + '_' + str(width) + "x" + str(height) + '.jpg',
                        "width": width,
                        "height": height,
                        "title": dd["title"]
                    }
                    _id = dd['_id']
                    thumb = [x['url'] for x in dd['thumb']]
                    if str(_id) + '_' + str(width) + "x" + str(height) + '.jpg' in thumb:
                        print("已经存在该尺寸的海报")
                        continue
                    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                    print(merged_path+str(_id) + '_' +
                          str(width) + "x" + str(height) + '.jpg')
                    print({'_id': _id}, {'$push': {'thumb': push_thumb}})
                    move = shutil.move(
                        url, merged_path+str(_id) + '_' + str(width) + "x" + str(height) + '.jpg')
                    result = tv_db.update_one(
                        {'_id': _id}, {'$push': {'thumb': push_thumb}})
                    print(result.modified_count)
                    # return True
                # print(result.raw_result)

        shutil.rmtree(imagedir_path+"/"+dir_name)


if __name__ == '__main__':
    merge_image_fromdir()

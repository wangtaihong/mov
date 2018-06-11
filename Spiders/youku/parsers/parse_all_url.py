# coding:utf-8
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from lxml import etree

list_url = 'http://list.youku.com'

def parse_all_url(url,r):
    try:
        page = etree.HTML(r)
    except Exception as e:
        print(r)
        print(str(e))
        return False
    menus_el = page.xpath(u'//div[@id="filterPanel"]/div')
    temp = []
    for x in xrange(1,len(menus_el)):
        for li in menus_el[x].find('ul').findall('li'):
            if li.find("a") != None:
                temp.append({"url": "http:" + li.find("a").get("href"),"title": li.find("a").text.replace(" ", "").replace("\n", "")})
            else:
                temp.append({"url": url, "title": li.find("span").text.replace(" ", "").replace("\n", "")})
    return temp
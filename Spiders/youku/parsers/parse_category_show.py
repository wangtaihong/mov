# coding:utf-8
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from lxml import etree

def parse_category_show(r, url):
    """
    解析category_show页面
    return : types,pages
    """
    r.encode('utf-8')
    page = etree.HTML(r)
    # lis = page.xpath('//*[@id="filterPanel"]/div[3]/ul/a[not(@target)]')
    lis = page.xpath(
        u'//label[contains(text(),"类型")]/following-sibling::ul/li/a')  # 正常情况有多页的情况
    # pre = page.xpath(u'//li[@class="next" and @title="下一页"]/preceding-sibling::li/a')
    try:
        page_no = page.xpath('//ul[@class="yk-pages"]/li[last()-1]')[0].find('a').text if page.xpath('//ul[@class="yk-pages"]/li[last()-1]')[
            0].find('a') != None else page.xpath('//ul[@class="yk-pages"]/li[last()-1]')[0].find('span').text
    except Exception as e:
        # print("---------------------%s---------------------"%url)
        page_no = 1
    return {
        'types': {lis[x].text: 'http:' + lis[x].get('href') for x in xrange(1, len(lis))},
        'pages': page_no
    }


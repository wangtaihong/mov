# coding:utf-8
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import time
from lxml import etree

def parse_star_show(r, url):
    """
    解析明星主页
    return:dict
    """
    try:
        r.decode('utf-8')
        page = etree.HTML(r)
    except Exception as e:
        return False
    info_el = page.xpath('//div[@id="starInfo"]/dl/dd[@class="info"]/span')
    sub_list = {u"别名": u'alias', u"性别": u'gender', u"地区": u'area', u"出生地": u'birthplace',
                u'生日': u'birthday', u'星座': u'constellation', u"血型": u'blood', u"职业": u'occupation'}
    info_list = [re.split(u'：', x.text) for x in info_el]
    for x in xrange(0, len(info_list)):
        info_list[x][0] = re.sub(
            info_list[x][0], sub_list[info_list[x][0]], info_list[x][0])
    info_data = {x[0]: x[1] for x in info_list}
    try:
        page.xpath(
            '//div[@class="yk-content"]/div[@class="box-star"]/div[@class="box-avatar"]/img')[0].get('src')
    except Exception as e:
        print("parse_star_show:", url, str(e))
        print(u'parse_star_show youku 资源缺失', url)
        return None
    info_data['avatar'] = page.xpath(
        '//div[@class="yk-content"]/div[@class="box-star"]/div[@class="box-avatar"]/img')[0].get('src')
    info_data['name'] = page.xpath('//div[@id="starInfo"]')[0].get('data-name')
    info_data['youku_starid'] = page.xpath(
        '//div[@id="starInfo"]')[0].get('data-starid')
    # http://list.youku.com/star/show/uid_UNjMyNTI=.html?spm=a2h0j.11185381.module_basic_star.5~5~1~3~5~A#
    m = re.search(u'\/(uid_\w*\d*=*)\.html', url)
    info_data['youku_uid'] = m.group(1) if m != None else None
    info_data['createed_at'] = int(time.time()*1000)
    intro = page.xpath('//dd[@class="intro"]/span[@class="long noshow"]')
    if len(intro) > 0:
        info_data['intro'] = intro[0].text
    # 别名：未知性别：女地区：大陆出生地：中国安徽合肥血型：未知生日：01月25日星座：水瓶座职业：演员
    return info_data

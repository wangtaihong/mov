# coding:utf-8
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from lxml import etree


def parse_tv_show(r, to_detail_url):
    """
    解析播放主页
    r:网页内容
    return tvs detail list page url
    """
    try:
        page = etree.HTML(r)
    except Exception as e:
        return False
    a = page.xpath('//div[@class="tvinfo"]/h2/a')
    if len(a) > 0:
        # return "http:" + re.sub('(\.html.*)', '.html', a[0].get('href'))
        return "http:" + a[0].get('href')
    else:
        # m = re.search(u'html":"<div class=\*"tvinfo\*"><h2><a href=\*"([^\" ]+?)\*" target=\*"_blank\*"',r)
        try:
            return 'http:'+re.search(u'tvinfo.* *\n*(//list\.youku\.com/show/id_\w*\d*\.html)',r).group(1)
            # class=\"tvinfo\">\n  <h2>\n    <span class=\"bg-dubo\"></span>\n\n    <a href=\"//list.youku.com/show/id_z4b17efbfbd0c1befbfbd.html\" target=\"_blank\"
        except Exception as e:
            print(to_detail_url,r)
            return False
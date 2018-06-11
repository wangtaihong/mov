# coding:utf-8
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from lxml import etree

def parse_page_fetch(r, page_url):
    """
    解析page页面
    return :
    """
    page = etree.HTML(r)
    lis = page.xpath('//div[@class="box-series"]/ul[@class="panel"]/li')
    yk_video_detail_task = []
    yk_get_detailurl_task = []
    for li in lis:
        # actors_el = li.xpath('div[@class="yk-pack pack-film"]/ul[@class="info-list"]/li[@class="actor"]/a')
        # vip_free = li.xpath('div[@class="yk-pack pack-film"]/div[@class="p-thumb"]/div[@class="p-thumb-tagrt"]/span[@class="vip-free"]')
        href = li.xpath(
            'div[@class="yk-pack pack-film"]/div[@class="p-thumb"]/a')[0].get('href')
        href = href.replace("http:", '')
        href = 'http:' + href
        if re.match(u'http\:\/\/list\.youku\.com\/show\/', href) != None:
            # 是list.youku.com/show/页面,这个页面信息很详细
            yk_video_detail_task.append({"url": href, 'Referer': page_url})
        else:
            yk_get_detailurl_task.append({"url": href, "Referer": page_url})
        print({"url": href, 'Referer': page_url})
    return {"yk_video_detail_task":yk_video_detail_task,"yk_get_detailurl_task":yk_get_detailurl_task}

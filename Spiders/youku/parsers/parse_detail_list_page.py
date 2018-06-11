# coding:utf-8
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from lxml import etree


def url_format(url):
    """
    //v.youku.com/v_show/id_XMzA5NTA1ODg2MA==.html?s=bc2a0ca1a64b11e6b9bb
    http://v.youku.com/v_show/id_XMzA5NTA1ODg2MA==.html
    """
    url = re.sub('http:', '', url)
    return "http:" + re.sub('(\.html.*)', '.html', url)


def parse_detail(r, url):
    try:
        page = etree.HTML(r)
    except Exception as e:
        return False
    sss = re.sub(u'\\n', '', r)
    data = dict()
    stars = []
    # title_show = re.search(u'class="p-thumb"><a title="([^"]+?)" href="([^"]+?)" target=',sss)
    # v-show: v-show可能没有的
    # v_show = re.search(u'class="p-thumb"><a title="([^" href]+?)" href="([^" ]+?)" target=',sss)
    v_show = page.xpath(
        u'//div[@class="p-post"]/div[@class="yk-pack p-list"]/div[@class="p-thumb"]/a')
    if len(v_show) > 0:
        data['v_show'] = url_format(v_show[0].get("href"))
    # 海报:
    # thumb = re.search(u'^(?=.*(http\://\w+\d+\.\w+\.com/(\w*\d*)+)").*$',sss).group(1)
    thumb = page.xpath(
        u'//div[@class="p-post"]/div[@class="yk-pack p-list"]/div[@class="p-thumb"]/img')
    if len(thumb) > 0:
        data['thumb'] = [{"url": url_format(thumb[0].get(
            "src")), "title":thumb[0].get("alt"), "width":200, "height":300}]
        data['title'] = thumb[0].get("alt")
    # category:
    # category = page.xpath('//div[@class="p-base"]/ul/li[@class="p-row p-title"]')[0].find('a')
    category = page.xpath(
        '//div[@class="p-base"]/ul/li[@class="p-row p-title"]/a')
    if len(category) > 0:
        data['category'] = category[0].text
        # category_url = category.get('href')
    # 年份:可能没有
    year = page.xpath(
        '//div[@class="p-base"]/ul/li[@class="p-row p-title"]/span[@class="sub-title"]')
    if len(year) > 0:
        data['year'] = year[0].text
    # 别名:可能没有
    alias = page.xpath('//div[@class="p-base"]/ul/li[@class="p-alias"]')
    if len(alias) > 0:
        data['alias'] = alias[0].get("title")
    # 上映:可能没有
    published_at = re.search(u'>上映：</label>(\w+-\d+-\d+)*</span>', sss)
    if published_at != None:
        data['published_at'] = published_at.group(1)
    # 优酷上映：可能没有
    yk_published_at = re.search(u'>优酷上映：</label>(\w+-\d+-\d+)*</span>', sss)
    if yk_published_at != None:
        data['yk_published_at'] = yk_published_at.group(1)
    # 优酷评分：可能没有
    youku_score = page.xpath(
        '//div[@class="p-base"]/ul/li[@class="p-score"]/span[@class="star-num"]')
    if len(youku_score) > 0:
        data['youku_score'] = youku_score[0].text
    # 豆瓣评分:可能没有
    douban_score = re.search(u'<span class="db-bignum">(\d+\.\d*)</span>', sss)
    if douban_score != None:
        data['douban_score'] = douban_score.group(1)
    # 豆瓣评价数量，可能没有
    douban_cm_num = re.search(u'<span class="db-cm-num">(\d*)评价</span>', sss)
    if douban_cm_num != None:
        data['douban_cm_num'] = douban_cm_num.group(1)
    # 主演:可能没有
    actors = page.xpath('//div[@class="p-base"]/ul/li[@class="p-performer"]')
    if len(actors) > 0:
        data['actors'] = actors[0].get('title')
        data['actor_list'] = []
        for x in page.xpath('//div[@class="p-base"]/ul/li[@class="p-performer"]/a'):
            print(x)
            data['actor_list'].append({"name":x.text,"youkuid":re.search(u"//list\.youku\.com/star/show/(.*)\.html",etree.tostring(x)).group(1)})
    # 集数
    renew = page.xpath(
        '//div[@class="p-base"]/ul/li[@class="p-row p-renew"]')
    if len(renew) > 0:
        data['renew'] = renew[0].text

    # 主演连接:可能没有
    actors_a = page.xpath(
        '//div[@class="p-base"]/ul/li[@class="p-performer"]/a')
    if len(actors_a) > 1:
        for x in actors_a:
            # actor_url = url_format(x.get('href'))
            actor_name = x.text
            stars.append(url_format(x.get('href')))
            # rd.sadd(config.yk_star_task, url_format(x.get('href')))  # 明星采集队列,redis set特性去重
            # //list.youku.com/star/show/uid_UODY0MjQ=.html
    # 导演:循环出来
    # directed = page.xpath('//div[@class="p-base"]/ul/li[@class="p-performer"]')[0].getnext().findall('a')
    directed = page.xpath(
        u'//div[@class="p-base"]/ul/li[contains(text(),"导演：")]/a')
    data['director_list'] = []
    if len(directed) > 0:
        data['directors'] = ''
        for x in directed:
            # star_url = url_format(x.get("href"))
            data['directors'] = data['directors'] + '|' + x.text
            stars.append(url_format(x.get('href')))
            data['director_list'].append({"name":x.text,"youkuid":re.search(u"//list\.youku\.com/star/show/(.*)\.html",etree.tostring(x)).group(1)})
            # rd.sadd(config.yk_star_task, url_format(x.get("href")))  # 明星采集队列,redis set特性去重
    # 地区，可能没有
    area = re.search(
        u'>地区：<a href="//list\.youku\.com/category/show/([^\.html]+?)\.html" target="_blank">([^</a></li>]+?)</a>', sss)
    if area != None:
        data['area'] = area.group(2)
    # 类型:循环出来
    types = page.xpath(
        u'//div[@class="p-base"]/ul/li[contains(text(),"类型")]/a')
    if len(types) > 0:
        data['types'] = ''
        for x in types:
            data['types'] = data['types'] + ',' + x.text
    # 总播放数:可能为none
    plays_num = re.search(u'<li>总播放数：([^</li>]+?)</li>', sss)
    if plays_num != None:
        data['plays_num'] = plays_num.group(1)

    # 评论数量:可能为none
    youku_comments_num = re.search(u'<li>评论：([^</li>]+?)</li>', sss)
    if youku_comments_num:
        data['youku_comments_num'] = youku_comments_num.group(1)

    # 顶:可以空
    ding = re.search(u'<li>顶：([^</li>]+?)</li>', sss)
    if ding:
        data['ding'] = ding.group(1)

    # 简介:
    try:
        page.xpath(
            u'//div[@class="p-base"]/ul/li[@class="p-row p-intro"]/span[@class="intro-more hide"]')[0]
    except Exception as e:
        print("parse_detail_list_page:", url, str(e), r)
        #update_session(proxy)
        return False
        # sys.exit("die")
    summary = page.xpath(
        u'//div[@class="p-base"]/ul/li[@class="p-row p-intro"]/span[@class="intro-more hide"]')[0]
    if summary != None:
        data['summary'] = summary.text

    # 适合年龄，可能为空
    age = re.search(u'>适用年龄：([^</li>]+?)</li>', sss)
    if age:
        data['age'] = age.group(1)

    peiyin = page.xpath(
        u'//div[@class="p-base"]/ul/li[contains(text(),"声优：")]/a')
    if len(peiyin) > 0:
        data['peiyin'] = ''
        data['peiyin_list'] = []
        for x in peiyin:
            data['peiyin'] = data['peiyin'] + '|' + x.text
            stars.append(url_format(x.get('href')))
            # data['peiyin_list'].append({"name":x.text,"youkuid":re.search(u"show/(.*)\.html",etree.tostring(x)).group(1)})
            data['peiyin_list'].append({"name":x.text,"youkuid":re.search(u"//list\.youku\.com/star/show/(.*)\.html",etree.tostring(x)).group(1)})

    # 综艺节目有
    presenters = page.xpath(
        u'//div[@class="p-base"]/ul/li[contains(text(),"主持人：")]/a')
    if len(presenters) > 0:
        data['presenters'] = ""
        for x in presenters:
            data['presenters'] = data['presenters'] + '|' + x.text
            stars.append(url_format(x.get('href')))
            # rd.sadd(config.yk_star_task, url_format(x.get("href")))  # 明星采集队列,redis set特性去重
    return {"data": data, "stars": stars}

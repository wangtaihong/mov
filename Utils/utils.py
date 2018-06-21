# coding=utf-8
import random
import string
import time
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')


def random_str(randomlength=11, lower=False):
    """
    生成随机字符串
    """
    a = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    random.shuffle(a)
    if lower == True:
        return ''.join(a[:randomlength]).lower()
    return ''.join(a[:randomlength])


def delay(min_second=2, max_second=20):
    time.sleep(random.randrange(min_second, max_second))


def parse_regx_char(doc):
    return doc.replace(".", '\.').replace("+", "\+").replace("(", "\(").replace(")", "\)").replace("[", "\[").replace("]", '\]').replace('|', '\|').replace("?", "\?").replace("*", "\*")

def title_preprocess(doc):
    chars_replace = set([u"会员抢先看", u"未删减版",u'独享版',u'精彩看点', u"原声版", u"会员版", u"预告片", u"英语版", u"粤语版", u"TV版", u'标清', u'HD', u"高清", u'DVD版',
                     u'超清', u'影讯'])
    chars_resub = set([u"\[.*?(\])", u"\(.*?(\))", u"（.*?(）)", u"【.*?(】)", u'(国语版\w*)',
                       u'\d{2}版', u'(原声版\w*)', u'(.{2}卫视)', u'(.{2}电视台)', u'(\d{1,}-\d{1,})', u'(第.{1}集)'])
    # doc = re.sub(u'( [A-Za-z]*)',"",doc)
    ji = re.search(u'(第(.{1})季)', doc)
    bu = re.search(u'(第(.{1})部)', doc)
    if ji:
        doc = doc.replace(ji.group(1), ji.group(2))
    if bu:
        doc = doc.replace(bu.group(1), bu.group(2))
    for x in chars_replace:
        doc = doc.replace(x, "")
    for c in chars_resub:
        doc = re.sub(c, '', doc)
    '''中英文翻译的  留下中文'''
    if re.search(u'^[\u4e00-\u9fa5]', doc):
        doc = re.sub(u'( [A-Za-z]*)', '', doc)
    return doc.strip(' ').replace(' ', "")


def title_preprocess_seed(doc):
    chars_resub = set([u'(国语版\w*\d*)', u'\d{2}版',u'独享版',u'精彩看点', u'(原声版\w*\d*)', u'(TV版\w*\d*)', u'(DVD版\w*\d*)', u'(热剧\w*\d*)',u'(影讯\w*\d*)',
                   u'(粤语版\w*\d*)', u'(未删减版\w*\d*)', u'(会员抢先看\w*\d*)', u'(会员版\w*\d*)', u'(标清\w*\d*)', u'(超清\w*\d*)',
                   u'(高清\w*\d*)', u'(英语版\w*\d*)', u'(预告片\w*\d*)', u'(.{2}卫视)', u'(.{2}电视台)', u'(\d{1,}-\d{1,})',
                   u'(第.{1}集)', "-", u"(\d{5,})", u"\[.*?(\])", u"\(.*?(\))", u"（.*?(）)", u"【.*?(】)", u'HD', u'-'])
    ji = re.search(u'(第(.{1})季)', doc)
    bu = re.search(u'(第(.{1})部)', doc)
    if ji:
        doc = doc.replace(ji.group(1), ji.group(2))
    if bu:
        doc = doc.replace(bu.group(1), bu.group(2))
    for c in chars_resub:
        doc = re.sub(c, '', doc)
    '''中英文翻译的  留下中文'''
    if re.search(u'^[\u4e00-\u9fa5]', doc):
        doc = re.sub(u'( [A-Za-z]*)', '', doc)
    return doc.strip(' ').replace(' ', "")

def title_preprocess_mongosearch(doc):
    chars_resub = set([u'(国语版\w*\d*)', u'\d{2}版',u'独享版',u'精彩看点', u'(原声版\w*\d*)', u'(TV版\w*\d*)', u'(DVD版\w*\d*)', u'(热剧\w*\d*)',u'(影讯\w*\d*)',
                   u'(粤语版\w*\d*)', u'(未删减版\w*\d*)', u'(会员抢先看\w*\d*)', u'(会员版\w*\d*)', u'(标清\w*\d*)', u'(超清\w*\d*)',
                   u'(高清\w*\d*)', u'(英语版\w*\d*)', u'(预告片\w*\d*)', u'(.{2}卫视)', u'(.{2}电视台)', u'(\d{1,}-\d{1,})',
                   u'(第.{1}集)', "-", u"(\d{5,})", u"\[.*?(\])", u"\(.*?(\))", u"（.*?(）)", u"【.*?(】)", u'HD', u'-',u'(第(.{1})季)',u'(第(.{1})部)'])
    for c in chars_resub:
        doc = re.sub(c, '', doc)
    '''中英文翻译的  留下中文'''
    if re.search(u'^[\u4e00-\u9fa5]', doc):
        doc = re.sub(u'( [A-Za-z]*)', '', doc)
    return doc.strip(' ').replace(' ', "")

def area_process(area):
    if not area:
        return area
    _temp = area.split(',')
    data = []
    for x in _temp:
        if u'台湾' in x:
            data.append(u'中国台湾')
        elif u'香港' in x:
            data.append(u'中国香港')
        elif u'大陆' in x:
            data.append(u'中国')
        elif u'内地' in x:
            data.append(u'中国')
        elif u'国内' in x:
            data.append(u'中国')
        elif u'国漫' in x:
            data.append(u'中国')
        elif u'华语' in x:
            data.append(u'中国')
        elif u'日漫' in x:
            data.append(u'日本')
        elif u'不详' in x:
            pass
        else:
            data.append(x)
    return ",".join(set(data))


def language_process(language):
    _temp = language.split(',')
    for x in xrange(0, len(_temp)):
        if u'中文' in _temp[x]:
            _temp[x] = u'汉语'
        if u'国语' in _temp[x]:
            _temp[x] = u'汉语'
        if u'普通话' in _temp[x]:
            _temp[x] = u'汉语'
    return ",".join(set(_temp))


def process_actor(doc):
    chars = [u' / ', u' | ', u'|', u'/', u'，',
             u'不详', u'未知', u'...', u'其他', u'佚名']
    for x in chars:
        doc = doc.replace(x, '')
    return doc.strip(',').strip(' ').strip(',')


def parse_simple(simple):
    if not simple:
        return simple
    simple = simple.strip("\n").strip(" ").strip("\n").strip("\t").strip("\r")
    return simple.strip("\n").strip(" ").strip("\n").strip("\t").strip("\r")


def mictime_to_ymd(mtime):
    # 到微秒  mtime
    return time.strftime('%Y-%m-%d', time.localtime(mtime/1000))

def search_preprocess(doc):
    chars_resub = set([u'(国语版\w*\d*)',u'独享版',u'精彩看点', u'\d{2}版',u'(@[\u4e00-\u9fa5]*)',u'(@.* )', u'(原声版\w*\d*)', u'(TV版\w*\d*)', u'(DVD版\w*\d*)', 
                   u'(粤语版\w*\d*)', u'(未删减版\w*\d*)', u'(会员抢先看\w*\d*)', u'(会员版\w*\d*)', u'(标清\w*\d*)', u'(超清\w*\d*)',
                   u'(高清\w*\d*)', u'(英语版\w*\d*)', u'(预告片\w*\d*)', u'(.{2}卫视)', u'(.{2}电视台)', u'(\d{1,}-\d{1,})',
                   u'(热剧\w*\d*)',u'(影讯\w*\d*)',
                   u'(第.{1,}集)', "-", u"(\d{5,})", u"\[.*?(\])", u"\(.*?(\))", u"（.*?(）)", u"【.*?(】)", u'HD', u'-',u'NEW'])
    ji = re.search(u'(第(.{1})季)', doc)
    bu = re.search(u'(第(.{1})部)', doc)
    if ji:
        doc = doc.replace(ji.group(1), ji.group(2))
    if bu:
        doc = doc.replace(bu.group(1), bu.group(2))
    for c in chars_resub:
        doc = re.sub(c, '', doc)
    '''中英文翻译的  留下中文'''
    if re.search(u'^[\u4e00-\u9fa5]', doc):
        doc = re.sub(u'( [A-Za-z]*)', '', doc)
    return doc.strip(' ').replace(' ', "")



def split_space(r):
    return ",".join(parse_simple(x) for x in r.split(','))

def check_title(title):
    regx_news = u'新闻|直播|演播|录播|专题|开幕|两会|联播|党委|民生|影讯|资讯|习近平|习主席|总书记|贯彻|国务院|实事|采访|高考|中考|学生|央视|卫视|电视台|记者|主播|宣传部|省委|国务院|市委|法治'
    regx_yule = u'娱闻|八卦|娱乐'
    regx_music = u'音乐|MV|演唱会|卡拉OK|伴奏|歌曲|儿歌|纯音乐'
    regx_edu = u'新东方|初中|高中|高一|高二|中学|数学|物理|教育|习题|古诗|数学|语文|方程|认读|拼音|教学|学习|舞蹈|练习|年级|化学|地理|奥数|高数|线性|曲线|圆周|乘法|除法'
    regx_pe = u'世界杯|体育|NBA|奥运|马术|国足|库里|锦标赛|冰壶|击剑'
    if  re.search(regx_news,title):
        return u'新闻'
    if re.search(regx_yule,title):
        return u'娱乐'
    if re.search(regx_edu,title):
        return u'教育'
    if re.search(regx_music,title):
        return u'音乐'
    if len(title)>=12:
        if u'财闻' in title:
            return u'财经'
        elif u'生活' in title:
            return u'生活'
        elif u'军事' in title:
            return u'军事'
        elif u'纪实' in title:
            return u'纪实'
        elif re.search(regx_pe,title):
            return u'体育'
        elif re.search(u'(\d{5,})',title):
            return u'新闻'
        else:
            return None
    else:
        return None

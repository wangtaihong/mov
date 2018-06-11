#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-01 18:48:11
# @Author  : taihong (wangtaihong1@gmail.com)
# @Link    : citybrain.top
# @Version : $Id$

def check_block(text):
    if re.search(u'userAgent\,navigator\.vendor\]\.join\("\|"\)\;window\.location\.href="(.*)"\;</script>', text):
        url = re.search(
            u'window\.location\.href="(.*)"\;</script>', text).group(1)
        # https://sec.douban.com/a?c=7fe5a9&d="+d+"&r=https%3A%2F%2Fmovie.douban.com%2Fsubject%2F27025785%2F&k=dxPw8V4vdmfvvr4HxBIdfU3GtgRmjrJt80PY0sZQQHE
        # [navigator.platform,navigator.userAgent,navigator.vendor].join("|")
        navigator = "|".join([ua["platform"], ua["user_agent"], ua['vendor']])
        url = re.sub('"\+d\+"', navigator, url)
        print("sec url:",url)
        print(douban_home_headers)
        sec = session.get(url=url, headers=douban_home_headers)
        print("----sec:", sec.text)
        return sec.text
    page = etree.HTML(text)
    captcha = page.xpath(u'//img[@alt="captcha"]')
    if len(captcha) == 0:
        return None
    original_url = page.xpath(u'//input[@name="original-url"]')
    if len(original_url) == 0:
        return None
    original_url = original_url[0].get("value")
    post_url = re.search(u'(\w*://.*\.com)', original_url).group(1)
    captcha_url = page.xpath(u'//img[@alt="captcha"]')[0].get("src")
    action = page.xpath(u'//form')[0].get("action")
    # captcha-solution
    data = {}
    data['captcha-id'] = page.xpath(u'//input[@name="captcha-id"]')[
        0].get("value")
    data['captcha-solution'] = recognize_url(captcha_url)
    data['original-url'] = original_url
    print("robbot:...",data)
    print('https://www.douban.com'+action)
    r = session.post(url='https://www.douban.com'+action, headers={
                      "Content-Type": "application/x-www-form-urlencoded", "User-Agent": ua["user_agent"]}, data=data)
    print("check block.:%s" % r.text)
    if u'你访问豆瓣的方式有点像机器人程序' in r.text:
        check_block(r.text)
    elif re.search(u'userAgent\,navigator\.vendor\]\.join\("\|"\)\;window\.location\.href="(.*)"\;</script>', r.text):
        url = re.search(
            u'window\.location\.href="(.*)"\;</script>', r.text).group(1)
        # https://sec.douban.com/a?c=7fe5a9&d="+d+"&r=https%3A%2F%2Fmovie.douban.com%2Fsubject%2F27025785%2F&k=dxPw8V4vdmfvvr4HxBIdfU3GtgRmjrJt80PY0sZQQHE
        # [navigator.platform,navigator.userAgent,navigator.vendor].join("|")
        navigator = "".join([ua["platform"], ua["user_agent"], ua['vendor']])
        url = re.sub('"\+d\+"', navigator, url)
        print("sec url:",url)
        sec = session.get(url=url, headers=douban_home_headers)
        print("----sec:", sec.text)
        return sec.text
    return r.text
